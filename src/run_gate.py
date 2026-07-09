"""Live circularity-gate experiment (Phase R6, mode 4) — Claude only.

The smallest first experiment from docs/analysis/fable-predicted-workspace-design.md §6:
one planted NON-OBVIOUS-gap case; run the blind converger (C) and Opus executor (O), then the
Fable predictor K times (P); compute the non-redundant surface P \ (O ∪ C). Empty => the
approach collapsed to circular (NO-GO on scaling). Non-empty AND it contains the planted gap =>
escaped the trap => proceed to the behavioral (counterfactual) check.

Requirements: anthropic + ANTHROPIC_API_KEY (see run_live_ab). Roles:
  executor = Opus (the workspace we care about) · blind = Opus (strong competence floor) ·
  predictor = Fable · judge = Sonnet (neutral).

Usage:  python src/run_gate.py [--k 5] [--out results/gate_report.json]
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from predicted_workspace import (
    BLIND_SYSTEM,
    COVERAGE_JUDGE_SYSTEM,
    PREDICTOR_SYSTEM,
    aggregate_predictions,
    non_redundant_surface,
)
from record_formats import RECORD, format_b_sections_glossed
from run_live_ab import _create_with_retry, _extract_json, _load_dotenv, make_claude_model_fn

# --- The planted non-obvious gap -------------------------------------------------
# A patient on amlodipine (a dihydropyridine calcium-channel blocker for hypertension) WITH
# gingival overgrowth on the perio exam. The non-obvious gap: the gingival finding may be
# amlodipine-INDUCED (a known drug side effect), a confounder of the periodontal reading — not
# purely inflammatory periodontitis. A blind analysis focused on the perio<->CV inflammatory
# bridge plausibly misses the drug-tissue interaction. (Non-obviousness is verified empirically:
# the gate checks whether the blind converger C surfaces it.)
PLANTED_CASE = copy.deepcopy(RECORD)
PLANTED_CASE["medical_cv"]["medications"] = ["amlodipine", "metformin"]  # amlodipine, not enalapril
PLANTED_CASE["periodontal"]["gingival_overgrowth"] = "moderate generalized"

PLANTED_TARGET = {
    "key": "amlodipine_gingival_overgrowth_confounder",
    "concept": "gingival overgrowth may be amlodipine (CCB) drug-induced — a confounder of the "
               "periodontal inflammation reading; medication review indicated",
}


def _make_call(client, model: str, system: str):
    def call(user: str) -> dict:
        last = None
        for _ in range(3):  # regenerate on no-text (thinking exhausted budget) or bad JSON
            resp = _create_with_retry(
                client, model=model, max_tokens=16000, system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = next((b.text for b in resp.content if getattr(b, "type", None) == "text"), None)
            if text is None:
                last = RuntimeError("no text block")
                continue
            try:
                return _extract_json(text)
            except json.JSONDecodeError as e:
                last = e
        raise last
    return call


def main() -> None:
    ap = argparse.ArgumentParser(description="Circularity-gate experiment (mode 4)")
    ap.add_argument("--k", type=int, default=5, help="predictor samples")
    ap.add_argument("--executor-model", default="claude-opus-4-8")
    ap.add_argument("--predictor-model", default="claude-fable-5")
    ap.add_argument("--blind-model", default="claude-opus-4-8")
    ap.add_argument("--judge-model", default="claude-sonnet-5")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "gate_report.json"))
    args = ap.parse_args()

    _load_dotenv()
    import anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set.")
    client = anthropic.Anthropic()

    case_input = format_b_sections_glossed(PLANTED_CASE)  # a clear, glossed presentation

    # C — blind converger's surfaced considerations (Opus, no workspace signal)
    blind = _make_call(client, args.blind_model, BLIND_SYSTEM)
    c_items = blind(case_input).get("items", [])

    # O — Opus executor's structured analysis (its output is the O item pool)
    executor = make_claude_model_fn(args.executor_model)
    output = executor(case_input)

    # P — Fable predicts Opus's workspace, K times, delta framing (given the OUTPUT)
    predictor = _make_call(client, args.predictor_model, PREDICTOR_SYSTEM)
    pred_user = (
        "SOLVER INPUT:\n" + case_input
        + "\n\nSOLVER OUTPUT (model this workspace's absent content, do NOT re-solve):\n"
        + json.dumps(output, indent=2)
    )
    runs = [predictor(pred_user) for _ in range(args.k)]
    p_items = aggregate_predictions(runs, args.k)

    # The gate: P \ (O ∪ C)
    judge = _make_call(client, args.judge_model, COVERAGE_JUDGE_SYSTEM)
    gate = non_redundant_surface(p_items, output, c_items, judge)

    # Did the planted non-obvious gap survive to the non-redundant surface?
    surface_keys = {i["key"] for i in gate["surface"]}
    planted_in_C = any(PLANTED_TARGET["key"] in (c.get("key", "") + c.get("concept", "").lower())
                       or "amlodipine" in (c.get("concept", "").lower()) for c in c_items)
    planted_in_surface = any("amlodipine" in i.get("concept", "").lower() for i in gate["surface"])

    report = {
        "meta": {"k": args.k, "executor": args.executor_model, "predictor": args.predictor_model,
                 "blind": args.blind_model, "judge": args.judge_model},
        "planted_target": PLANTED_TARGET,
        "blind_C_items": c_items,
        "predicted_P_stable": p_items,
        "gate": gate,
        "planted_gap_surfaced_by_blind": planted_in_C,   # if True -> gap was obvious, pick subtler
        "planted_gap_in_non_redundant_surface": planted_in_surface,
        "verdict": (
            "circular" if gate["circular"]
            else "escaped_trap" if planted_in_surface
            else "non_empty_but_planted_gap_not_isolated"
        ),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"blind C items: {len(c_items)} | stable P items: {len(p_items)} | "
          f"non-redundant surface P\\(O∪C): {gate['n_surface']}")
    print(f"planted gap surfaced by blind (obvious?): {planted_in_C}")
    print(f"planted gap in non-redundant surface: {planted_in_surface}")
    print("VERDICT:", report["verdict"], "| wrote:", args.out)


if __name__ == "__main__":
    main()
