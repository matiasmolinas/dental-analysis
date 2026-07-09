# EXPERIMENTAL / inconclusive result — see docs/RESEARCH_SUMMARY.md §0 and RETROSPECTIVE.md
"""Behavioral validation of the gate's non-redundant surface (Phase R6, mode 4, step 4).

The gate showed the predictor surfaces a NON-EMPTY non-redundant surface P\\(O∪C) (7 items). But
non-redundant != useful. This runner tests the payoff: does GROUNDING those surfaced gaps into the
executor's input measurably improve the honest metrics (counterfactual sensitivity + relational
recall + guardrail) vs the base input? If yes, the uncommitted predictor's non-redundant gaps are
behaviorally load-bearing, not just novel.

Reads the surface from a gate report (default results/gate_report_v2.json); no re-run of the gate.
Requirements: anthropic + ANTHROPIC_API_KEY. Claude only.

Usage:  python src/run_gate_behavioral.py [--gate-report results/gate_report_v2.json]
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
from run_gate import PLANTED_CASE
from run_live_ab import _load_dotenv, make_claude_model_fn


def main() -> None:
    ap = argparse.ArgumentParser(description="Behavioral validation of the gate surface")
    ap.add_argument("--gate-report", default=os.path.join(os.path.dirname(__file__), "..",
                                                          "results", "gate_report_v2.json"))
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "gate_behavioral.json"))
    args = ap.parse_args()

    _load_dotenv()
    report = json.load(open(args.gate_report))
    surface = [i.get("concept", "") for i in report["gate"]["surface"] if i.get("concept")]
    if not surface:
        raise SystemExit("gate report has an empty non-redundant surface — nothing to validate.")

    case = PLANTED_CASE
    eval_fn = make_claude_model_fn(args.model)

    gaps_block = (
        "\n\nAn external review flagged these considerations a thorough analysis should address "
        "(non-diagnostic; investigate, do not impute):\n" + "\n".join("- " + g for g in surface)
    )
    base_input = format_b_sections_glossed            # (record) -> str
    grounded_input = lambda r: format_b_sections_glossed(r) + gaps_block  # noqa: E731

    # Counterfactual sensitivity: base vs grounded (flips diabetes/smoking/hypertension).
    cf_base = counterfactual_report([case], base_input, eval_fn)
    cf_grounded = counterfactual_report([case], grounded_input, eval_fn)

    # Direct A/B on the un-flipped case: does grounding lift relational_recall / guardrail?
    s_base = score(eval_fn(base_input(case)), case)
    s_grounded = score(eval_fn(grounded_input(case)), case)

    result = {
        "meta": {"model": args.model, "n_surface_grounded": len(surface),
                 "gate_report": os.path.basename(args.gate_report)},
        "grounded_items": surface,
        "counterfactual": {
            "base": {"sensitivity_rate": cf_base["sensitivity_rate"],
                     "mean_affected_delta": cf_base["mean_affected_delta"]},
            "grounded": {"sensitivity_rate": cf_grounded["sensitivity_rate"],
                         "mean_affected_delta": cf_grounded["mean_affected_delta"]},
            "delta_mean_affected": round(cf_grounded["mean_affected_delta"]
                                         - cf_base["mean_affected_delta"], 3),
        },
        "ab_unflipped": {
            "base": {k: s_base[k] for k in ("relational_recall", "missing_data_flagged",
                                            "guardrail_pass")},
            "grounded": {k: s_grounded[k] for k in ("relational_recall", "missing_data_flagged",
                                                    "guardrail_pass")},
            "delta_relational_recall": round(s_grounded["relational_recall"]
                                             - s_base["relational_recall"], 3),
        },
    }
    # honest verdict: grounding helps iff it lifts a metric without regressing guardrail
    cf_up = result["counterfactual"]["delta_mean_affected"] > 0
    rr_up = result["ab_unflipped"]["delta_relational_recall"] > 0
    guard_ok = s_grounded["guardrail_pass"] or not s_base["guardrail_pass"]
    result["verdict"] = ("grounding_useful" if (cf_up or rr_up) and guard_ok
                         else "grounding_neutral_or_negative")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print("counterfactual mean_affected_delta: base",
          f"{cf_base['mean_affected_delta']:+.2f} -> grounded {cf_grounded['mean_affected_delta']:+.2f}",
          f"(Δ {result['counterfactual']['delta_mean_affected']:+.2f})")
    print("relational_recall: base",
          f"{s_base['relational_recall']:.2f} -> grounded {s_grounded['relational_recall']:.2f}",
          f"(Δ {result['ab_unflipped']['delta_relational_recall']:+.2f})")
    print("guardrail base/grounded:", s_base["guardrail_pass"], "/", s_grounded["guardrail_pass"])
    print("VERDICT:", result["verdict"], "| wrote:", args.out)


if __name__ == "__main__":
    main()
