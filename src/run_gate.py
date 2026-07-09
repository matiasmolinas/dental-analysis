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


# Tool schemas force STRUCTURED output (the SDK returns a validated dict — no fragile text-JSON
# parsing, no truncation/quote/comma breakage). Extended thinking is disabled for these
# structured calls (it was exhausting the token budget before any output).
PREDICTOR_TOOL = {"type": "object", "properties": {"items": {"type": "array", "items": {
    "type": "object", "properties": {
        "key": {"type": "string"}, "channel": {"type": "string"}, "concept": {"type": "string"},
        "salience": {"type": "string"}, "appears_in_output": {"type": "boolean"}},
    "required": ["key", "channel", "concept", "appears_in_output"]}}}, "required": ["items"]}
BLIND_TOOL = {"type": "object", "properties": {"items": {"type": "array", "items": {
    "type": "object", "properties": {"key": {"type": "string"}, "concept": {"type": "string"}},
    "required": ["key", "concept"]}}}, "required": ["items"]}
JUDGE_TOOL = {"type": "object", "properties": {"verdicts": {"type": "array", "items": {
    "type": "object", "properties": {
        "key": {"type": "string"}, "covered": {"type": "boolean"}, "why": {"type": "string"}},
    "required": ["key", "covered"]}}}, "required": ["verdicts"]}


def _make_call(client, model: str, system: str, tool_name: str, tool_schema: dict):
    """Structured call that PRESERVES extended thinking. Forced tool_use is incompatible with
    thinking, so we keep thinking ON with a generous budget and offer the tool with tool_choice
    AUTO (compatible): the model thinks, then returns the structured result via the tool (clean,
    validated dict) or as text (parsed as fallback). max_tokens is maxed so neither thinking nor
    the output is truncated."""
    tool = {"name": tool_name, "description": f"Return the {tool_name} result.",
            "input_schema": tool_schema}
    sys_prompt = system + f"\n\nReturn your result by calling the `{tool_name}` tool."

    def _stream(**kw):
        # max_tokens=32000 exceeds the SDK's non-streaming 10-min guard -> must stream.
        import time
        import anthropic
        last = None
        for i in range(5):
            try:
                with client.messages.stream(**kw) as s:
                    return s.get_final_message()
            except (anthropic.APIConnectionError, anthropic.RateLimitError,
                    anthropic.InternalServerError) as e:
                last = e
                time.sleep(2 * (i + 1))
        raise last

    def _create(user):
        # These models (Fable 5 / Opus 4.8) run ADAPTIVE thinking by default — passing no
        # thinking param preserves the think, and the maxed max_tokens (streamed) leaves ample
        # room for both the reasoning and the tool/text output. This is what the user asked for:
        # keep thinking AND the largest possible generation.
        return _stream(model=model, max_tokens=32000, system=sys_prompt, tools=[tool],
                       messages=[{"role": "user", "content": user}])

    def call(user: str) -> dict:
        last = None
        for _ in range(4):
            resp = _create(user)
            if getattr(resp, "stop_reason", None) == "refusal":
                raise RuntimeError("model refusal")  # terminal for this model -> fall back fast
            tb = next((b for b in resp.content if getattr(b, "type", None) == "tool_use"), None)
            if tb is not None and isinstance(getattr(tb, "input", None), dict):
                return tb.input
            txt = next((b.text for b in resp.content if getattr(b, "type", None) == "text"), None)
            if txt:
                try:
                    return _extract_json(txt)
                except json.JSONDecodeError as e:
                    last = e
                    continue
            last = RuntimeError("no usable tool_use/text block in response")
        raise last
    return call


def main() -> None:
    ap = argparse.ArgumentParser(description="Circularity-gate experiment (mode 4)")
    ap.add_argument("--k", type=int, default=5, help="predictor samples")
    ap.add_argument("--executor-model", default="claude-opus-4-8")
    ap.add_argument("--predictor-model", default="claude-fable-5")
    ap.add_argument("--predictor-fallback-model", default="claude-opus-4-8",
                    help="used if the primary predictor refuses/fails for topic-safety reasons")
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
    blind = _make_call(client, args.blind_model, BLIND_SYSTEM, "blind_considerations", BLIND_TOOL)
    c_items = blind(case_input).get("items", [])

    # O — Opus executor's structured analysis (its output is the O item pool)
    executor = make_claude_model_fn(args.executor_model)
    output = executor(case_input)

    # P — the predictor models the workspace's absent content, K times, delta framing.
    # Primary = Fable; fall back to Opus if the primary refuses/fails for topic-safety reasons.
    predictor = _make_call(client, args.predictor_model, PREDICTOR_SYSTEM,
                           "predicted_workspace", PREDICTOR_TOOL)
    fallback = _make_call(client, args.predictor_fallback_model, PREDICTOR_SYSTEM,
                          "predicted_workspace", PREDICTOR_TOOL)
    pred_user = (
        "SOLVER INPUT:\n" + case_input
        + "\n\nSOLVER OUTPUT (model this workspace's absent content, do NOT re-solve):\n"
        + json.dumps(output, indent=2)
    )
    runs, models_used = [], []
    for _ in range(args.k):
        try:
            runs.append(predictor(pred_user)); models_used.append(args.predictor_model)
        except Exception:  # refusal / no usable block after retries -> Opus fallback
            runs.append(fallback(pred_user)); models_used.append(args.predictor_fallback_model)
    p_items = aggregate_predictions(runs, args.k)

    # The gate: P \ (O ∪ C)
    judge = _make_call(client, args.judge_model, COVERAGE_JUDGE_SYSTEM, "coverage_verdicts", JUDGE_TOOL)
    gate = non_redundant_surface(p_items, output, c_items, judge)

    # Did the planted non-obvious gap survive to the non-redundant surface?
    surface_keys = {i["key"] for i in gate["surface"]}
    planted_in_C = any(PLANTED_TARGET["key"] in (c.get("key", "") + c.get("concept", "").lower())
                       or "amlodipine" in (c.get("concept", "").lower()) for c in c_items)
    planted_in_surface = any("amlodipine" in i.get("concept", "").lower() for i in gate["surface"])

    report = {
        "meta": {"k": args.k, "executor": args.executor_model, "predictor": args.predictor_model,
                 "predictor_fallback": args.predictor_fallback_model,
                 "predictor_models_used": models_used, "blind": args.blind_model,
                 "judge": args.judge_model},
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
