"""Run the periodontitis↔cognition association on real NHANES 2011-2012 (Track 2).

Downloads the 2011-2012 files, derives the analysis table, and reports the confounder-adjusted
standardized association between periodontal severity and each cognitive score, with bootstrap CIs.
Non-diagnostic, population-level, hypothesis-generating — the empirical test of what mech_neuro
predicts directionally (more periodontal severity → worse cognition, via inflammation).

Requires pandas + network. Usage:  python src/run_perio_cognition.py [--exposure perio_cal|perio_ppd]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from nhanes_neuro_loader import download_neuro_files, load_neuro_table
from perio_cognition import analyze

OUTCOMES = ["cerad_immediate", "cerad_delayed", "animal_fluency", "digit_symbol"]
CONFOUNDERS = ["age", "education", "smoking", "hba1c"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Perio↔cognition association (NHANES 2011-2012)")
    ap.add_argument("--exposure", choices=["perio_cal", "perio_ppd"], default="perio_cal")
    ap.add_argument("--dest", default=os.path.join(os.path.dirname(__file__), "..", ".nhanes_neuro"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "perio_cognition_report.json"))
    args = ap.parse_args()

    try:
        import pandas  # noqa: F401
    except ImportError:
        raise SystemExit("pandas required: pip install pandas (and network access).")

    paths = download_neuro_files(args.dest)
    records = load_neuro_table(paths)
    report = analyze(records, args.exposure, OUTCOMES, CONFOUNDERS)
    report["meta"] = {"cycle": "NHANES 2011-2012", "n_records_total": len(records),
                      "exposure": args.exposure, "files": list(paths)}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"NHANES 2011-2012 | exposure={args.exposure} | {len(records)} participants merged")
    print(f"confounders adjusted: {', '.join(CONFOUNDERS)}\n")
    for outcome, r in report["outcomes"].items():
        if "adjusted_std_coef" not in r:
            print(f"  {outcome:18s} n={r['n']}  ({r.get('note')})")
            continue
        sig = "SIG" if r["significant"] else "ns "
        print(f"  {outcome:18s} n={r['n']:5d}  crude={r['crude_std_coef']:+.3f}  "
              f"adj={r['adjusted_std_coef']:+.3f}  CI90=[{r['ci_90_adjusted']['lo']:+.3f},"
              f"{r['ci_90_adjusted']['hi']:+.3f}]  {sig}  {r['direction']}")
    print("\nNON-DIAGNOSTIC population association (not causal; inflammation mediator not in-cycle).")
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
