# EXPERIMENTAL / inconclusive result — see docs/RESEARCH_SUMMARY.md §0 and RETROSPECTIVE.md
"""Live counterfactual-sensitivity run on Claude (Phase R6 v2).

Tests whether the converged input (B = ab_eval.build_inputs) makes the model actually
*use* its factors more than the naive input (A) — a reasoning test that the substring
recall metric cannot give. For each factor (diabetes→metabolic, smoking→behavioral,
hypertension→vascular) it flips the factor present↔absent and checks the dependent axis
moves while unrelated axes stay put.

Usage:
  python src/run_counterfactual.py --cases nhanes --n 4 --model claude-sonnet-5
  python src/run_counterfactual.py --cases grounded
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ab_eval import build_inputs
from counterfactual import counterfactual_report
from record_formats import format_a_abbrev_table
from run_live_ab import _load_dotenv, load_cases, make_claude_model_fn

# The evolved instruction (mirrors the factor-grounding rule Fable added to
# prompts/evaluator.md). Tests whether factor-grounding INSTRUCTIONS raise counterfactual
# sensitivity — the gap the v2 run measured at 0.00.
FACTOR_GROUNDING = (
    "Factor-grounded / counterfactually coherent: each relational axis must cite the "
    "specific present factors that drive it; if a driving factor is absent from the "
    "record, that axis must be correspondingly weaker or omitted. Confidence must track "
    "the factors actually present, not population priors, so flipping a driving factor "
    "would move the dependent axis in the mechanistically-correct direction."
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Counterfactual sensitivity: naive vs converged")
    ap.add_argument("--cases", choices=["grounded", "nhanes"], default="grounded")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--seqns", type=int, nargs="*")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..",
                                                  "results", "counterfactual_report.json"))
    args = ap.parse_args()

    _load_dotenv()
    cases = load_cases(args.cases, args.n, args.seqns)
    eval_base = make_claude_model_fn(args.model)
    eval_evolved = make_claude_model_fn(args.model, extra_system=FACTOR_GROUNDING)

    b_input = lambda r: build_inputs(r)["B"]  # noqa: E731
    report = {
        "A_naive": counterfactual_report(cases, format_a_abbrev_table, eval_base),
        "B_converged": counterfactual_report(cases, b_input, eval_base),
        # B input, but the evaluator now carries the evolved factor-grounding rule:
        "B_evolved": counterfactual_report(cases, b_input, eval_evolved),
        "meta": {"cases": args.cases, "model": args.model, "n": len(cases)},
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    for arm in ("A_naive", "B_converged", "B_evolved"):
        r = report[arm]
        print(f"{arm}: sensitivity_rate={r['sensitivity_rate']:.2f} "
              f"mean_affected_delta={r['mean_affected_delta']:.2f} (n_flips={r['n_flips']})")
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
