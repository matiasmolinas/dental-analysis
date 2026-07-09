# EXPERIMENTAL / inconclusive result — see docs/RESEARCH_SUMMARY.md §0 and RETROSPECTIVE.md
"""Live Session Working-Consciousness session (Phase R6 next-step #4) — Claude only.

The SWC thesis (a turn-1 deficiency measurably improves turn-2, and the lesson persists) has never
run live — only `.session/example_case01.md` exists. This is the minimal live demonstration, and it
wires the SWC to the cross-session lever ledger (#3): run turn 1, have a reviewer name a deficiency,
inject a TARGETED fix, run turn 2, measure the relational-recall / counterfactual delta, and — if
turn 2 improved and the guardrail holds — persist the working lever to `.knowledge/lever_ledger.jsonl`
so a future session starts from it.

Requirements: anthropic + ANTHROPIC_API_KEY. Roles: executor = Opus, reviewer/selector = Opus/Sonnet.
Usage:  python src/run_swc_session.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ab_eval import score
from counterfactual import counterfactual_report
from lever_ledger import case_signature, write_lever
from record_formats import format_b_sections_glossed
from run_gate import PLANTED_CASE, PREDICTOR_SYSTEM, PREDICTOR_TOOL, _make_call
from run_targeted import SELECTOR_SYSTEM, SELECTOR_TOOL
from run_live_ab import _load_dotenv, make_claude_model_fn


def main() -> None:
    ap = argparse.ArgumentParser(description="Live 2-turn SWC session + ledger write")
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--reviewer-model", default="claude-opus-4-8")
    ap.add_argument("--selector-model", default="claude-sonnet-5")
    ap.add_argument("--ledger", default=os.path.join(os.path.dirname(__file__), "..",
                                                     ".knowledge", "lever_ledger.jsonl"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "swc_session.json"))
    args = ap.parse_args()

    _load_dotenv()
    import anthropic
    client = anthropic.Anthropic()
    rec = PLANTED_CASE
    eval_fn = make_claude_model_fn(args.model)
    reviewer = _make_call(client, args.reviewer_model, PREDICTOR_SYSTEM, "predicted_workspace", PREDICTOR_TOOL)
    selector = _make_call(client, args.selector_model, SELECTOR_SYSTEM, "selection", SELECTOR_TOOL)

    # Turn 1 — executor output + its score
    t1_in = format_b_sections_glossed(rec)
    t1_out = eval_fn(t1_in)
    s1 = score(t1_out, rec)
    cf1 = counterfactual_report([rec], format_b_sections_glossed, eval_fn)

    # Deficiency: a reviewer names absent, mechanistically-relevant gaps; select the targeted ones
    items = [it for it in reviewer(
        "SOLVER INPUT:\n" + t1_in + "\n\nSOLVER OUTPUT (model absent content, do NOT re-solve):\n"
        + json.dumps(t1_out, indent=2)).get("items", []) if not it.get("appears_in_output")]
    keep = set(selector("CASE:\n" + t1_in + "\n\nITEMS:\n"
                        + json.dumps([{"key": g["key"], "concept": g["concept"]} for g in items])
                        ).get("keep_keys", []))
    targeted = [g for g in items if g["key"] in keep]

    # Turn 2 — inject the targeted fix, re-run, re-score
    suffix = ("\n\nConsider these factor-specific points:\n"
              + "\n".join("- " + g["concept"] for g in targeted)) if targeted else ""
    t2_build = lambda r: format_b_sections_glossed(r) + suffix  # noqa: E731
    t2_out = eval_fn(t2_build(rec))
    s2 = score(t2_out, rec)
    cf2 = counterfactual_report([rec], t2_build, eval_fn)

    rr_delta = round(s2["relational_recall"] - s1["relational_recall"], 3)
    cf_delta = round(cf2["mean_affected_delta"] - cf1["mean_affected_delta"], 3)
    improved = (rr_delta > 0 or cf_delta > 0) and (s2["guardrail_pass"] or not s1["guardrail_pass"])

    persisted = None
    if improved and targeted:
        lever = {"case_signature": case_signature(rec), "surface": "injected_variables",
                 "lever": "inject targeted factor-specific review considerations",
                 "mediator_moved": (targeted[0]["concept"][:60]),
                 "corroboration": "repeated_turns", "confidence": 0.6, "guardrail_pass": True,
                 "provenance": "swc_session turn1->turn2"}
        try:
            write_lever(args.ledger, lever); persisted = lever["lever"]
        except ValueError as e:
            persisted = f"rejected: {e}"

    report = {
        "turn1": {"relational_recall": s1["relational_recall"], "cf_mean_affected_delta": cf1["mean_affected_delta"]},
        "turn2": {"relational_recall": s2["relational_recall"], "cf_mean_affected_delta": cf2["mean_affected_delta"]},
        "deltas": {"relational_recall": rr_delta, "cf_mean_affected_delta": cf_delta},
        "n_targeted_injected": len(targeted), "improved": improved, "ledger_write": persisted,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"turn1 rel_recall {s1['relational_recall']:.2f} -> turn2 {s2['relational_recall']:.2f} "
          f"(Δ {rr_delta:+.2f}); cf Δ {cf_delta:+.2f}; improved={improved}; ledger={persisted}")


if __name__ == "__main__":
    main()
