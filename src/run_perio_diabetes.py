"""The metabolic-axis empirical anchor — periodontitis → HbA1c on real NHANES 2009-2010.

The 2009-2010 cycle co-measures the periodontal exam and HbA1c in the same participants, so it tests
the perio → glycemia edge the metabolic axis predicts (more periodontal severity → higher HbA1c),
confounder-adjusted with bootstrap CIs. A POSITIVE coefficient = the direction the model predicts.
Non-diagnostic, population-level. Requires pandas + network.

Usage:  python src/run_perio_diabetes.py [--exposure perio_cal|perio_ppd]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.nhanes import download_files, load_cv_table
from histora.perio_cognition import analyze

OUTCOMES = ["hba1c"]
CONFOUNDERS = ["age", "education", "smoking", "bmi"]   # HbA1c is the outcome, not a confounder here


def main() -> None:
    ap = argparse.ArgumentParser(description="Perio↔HbA1c association, NHANES 2009-2010")
    ap.add_argument("--exposure", choices=["perio_cal", "perio_ppd"], default="perio_cal")
    ap.add_argument("--dest", default=os.path.join(os.path.dirname(__file__), "..", ".nhanes"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "perio_diabetes_report.json"))
    args = ap.parse_args()

    try:
        import pandas  # noqa: F401
    except ImportError:
        raise SystemExit("pandas required: pip install pandas (and network access).")

    paths = download_files(args.dest)
    records = load_cv_table(paths)          # already carries hba1c + the confounders
    report = analyze(records, args.exposure, OUTCOMES, CONFOUNDERS)
    report["meta"] = {"cycle": "NHANES 2009-2010", "n_records_total": len(records),
                      "exposure": args.exposure,
                      "note": "positive coef = more periodontal severity → higher HbA1c"}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"NHANES 2009-2010 | exposure={args.exposure} | {len(records)} participants merged")
    print(f"confounders adjusted: {', '.join(CONFOUNDERS)}\n")
    for outcome, r in report["outcomes"].items():
        if "adjusted_std_coef" not in r:
            print(f"  {outcome:8s} n={r['n']}  ({r.get('note')})")
            continue
        sig = "SIG" if r["significant"] else "ns "
        arrow = "↑more-perio→higher HbA1c" if r["adjusted_std_coef"] > 0 else "↓"
        print(f"  {outcome:8s} n={r['n']:5d}  crude={r['crude_std_coef']:+.3f}  "
              f"adj={r['adjusted_std_coef']:+.3f}  CI90=[{r['ci_90_adjusted']['lo']:+.3f},"
              f"{r['ci_90_adjusted']['hi']:+.3f}]  {sig}  {arrow}")
    print("\nNON-DIAGNOSTIC population association — the metabolic-axis empirical anchor.")
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
