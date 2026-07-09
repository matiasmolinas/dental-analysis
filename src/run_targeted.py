"""Targeted actuator on a non-obvious-gap task (Phase R6, next-step #2) — Claude only.

The behavioral test (`run_gate_behavioral`) grounded ALL surfaced gaps as one checklist and it HURT
(dilution). The design (`fable-predicted-workspace-design.md` §5, `lens-non-redundancy-burden-of-proof.md`
§5) called for a FREE / TARGETED actuator instead: keep only the gaps a judge deems mechanistically
relevant to the present factors, injected as factor-anchored considerations — and measure whether
that *selective* grounding beats both the base input and the crude append-all.

Three arms per case, scored by counterfactual sensitivity + relational_recall (guardrail a hard gate):
  base      = the input as-is
  append_all = base + every surfaced gap (the crude actuator that hurt)
  targeted   = base + only the judge-selected, mechanistically-relevant gaps (the free actuator v1)

n is a CLI flag; n>=30 is the powered target (bounded here for cost). Uses the predictor to surface
gaps per case (Opus, which does not refuse), a selector judge, and the neutral evaluator.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ab_eval import score
from counterfactual import counterfactual_report
from record_formats import format_b_sections_glossed
from run_gate import PLANTED_CASE, PREDICTOR_TOOL, PREDICTOR_SYSTEM, _make_call
from run_live_ab import _load_dotenv, load_cases, make_claude_model_fn

SELECTOR_SYSTEM = """You select which review considerations to inject into a downstream oral-systemic
analysis. KEEP only items that are mechanistically tied to the SPECIFIC factors present in this case
(e.g. a drug-tissue interaction for a drug the patient is on, a confounder of a present finding, a
mediator directly linking the oral and systemic data). DROP peripheral/administrative items (generic
missing-data checklists, risk-score bookkeeping) that would dilute the core mediating reasoning.
Return, via the tool, keep_keys = the keys of the items to keep."""

SELECTOR_TOOL = {"type": "object", "properties": {"keep_keys": {"type": "array",
    "items": {"type": "string"}}}, "required": ["keep_keys"]}


def _gaps_block(items, header):
    return ("\n\n" + header + "\n" + "\n".join("- " + i["concept"] for i in items)) if items else ""


def main() -> None:
    ap = argparse.ArgumentParser(description="Targeted actuator on a non-obvious-gap task")
    ap.add_argument("--cases", choices=["planted", "nhanes"], default="planted")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--model", default="claude-opus-4-8")           # executor / evaluator
    ap.add_argument("--predictor-model", default="claude-opus-4-8")  # surfaces gaps (no refusal)
    ap.add_argument("--judge-model", default="claude-sonnet-5")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "targeted_report.json"))
    args = ap.parse_args()

    _load_dotenv()
    import anthropic
    client = anthropic.Anthropic()
    cases = [PLANTED_CASE] if args.cases == "planted" else load_cases("nhanes", args.n, None)

    eval_fn = make_claude_model_fn(args.model)
    predictor = _make_call(client, args.predictor_model, PREDICTOR_SYSTEM,
                           "predicted_workspace", PREDICTOR_TOOL)
    selector = _make_call(client, args.judge_model, SELECTOR_SYSTEM, "selection", SELECTOR_TOOL)

    per_case = []
    for i, rec in enumerate(cases):
        base_in = format_b_sections_glossed(rec)
        out = eval_fn(base_in)
        # surface gaps for this case (delta framing, given the output)
        items = predictor("SOLVER INPUT:\n" + base_in
                          + "\n\nSOLVER OUTPUT (model absent content, do NOT re-solve):\n"
                          + json.dumps(out, indent=2)).get("items", [])
        gaps = [it for it in items if not it.get("appears_in_output")]
        keep = set(selector("CASE:\n" + base_in + "\n\nITEMS:\n"
                            + json.dumps([{"key": g["key"], "concept": g["concept"]} for g in gaps])
                            ).get("keep_keys", []))
        targeted = [g for g in gaps if g["key"] in keep]

        # each arm = the injected text suffix (empty for base); applied on top of format_b of
        # whatever record the counterfactual runner passes (flipped or not).
        suffixes = {
            "base": "",
            "append_all": _gaps_block(gaps, "Consider these:"),
            "targeted": _gaps_block(targeted, "Consider these factor-specific points:"),
        }
        row = {"case": i, "n_gaps": len(gaps), "n_targeted": len(targeted)}
        for arm, suffix in suffixes.items():
            builder = (lambda s: (lambda r: format_b_sections_glossed(r) + s))(suffix)
            cf = counterfactual_report([rec], builder, eval_fn)
            sc = score(eval_fn(builder(rec)), rec)
            row[arm] = {"cf_mean_affected_delta": cf["mean_affected_delta"],
                        "cf_sensitivity_rate": cf["sensitivity_rate"],
                        "relational_recall": sc["relational_recall"],
                        "guardrail_pass": sc["guardrail_pass"]}
        per_case.append(row)

    def agg(arm, metric):
        xs = [c[arm][metric] for c in per_case]
        return round(sum(xs) / len(xs), 3) if xs else 0.0

    aggregate = {arm: {m: agg(arm, m) for m in ("cf_mean_affected_delta", "relational_recall")}
                 for arm in ("base", "append_all", "targeted")}
    report = {"meta": {"cases": args.cases, "n": len(cases), "model": args.model},
              "per_case": per_case, "aggregate": aggregate,
              "targeted_minus_base": {
                  m: round(aggregate["targeted"][m] - aggregate["base"][m], 3)
                  for m in ("cf_mean_affected_delta", "relational_recall")}}
    report["verdict"] = ("targeted_useful"
                         if report["targeted_minus_base"]["cf_mean_affected_delta"] > 0
                         or report["targeted_minus_base"]["relational_recall"] > 0
                         else "targeted_neutral_or_negative")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    for arm in ("base", "append_all", "targeted"):
        a = aggregate[arm]
        print(f"{arm:11s} cf_delta={a['cf_mean_affected_delta']:+.2f}  rel_recall={a['relational_recall']:.2f}")
    print("targeted-base:", report["targeted_minus_base"], "| VERDICT:", report["verdict"])
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
