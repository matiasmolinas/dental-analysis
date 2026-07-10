"""The CV-axis empirical anchor — periodontitis → CRP (and CV history) on real NHANES 2009-2010.

The neuro axis could only validate a perio↔cognition ASSOCIATION (the inflammatory mediator was
out-of-cycle). The 2009-2010 cycle co-measures the periodontal exam, CRP, and CV history in the SAME
participants — so this runner tests the **perio → CRP mediator edge directly**, converting the E2.6 CV
scaffold from a bare `1+γ_cv·gain` hypothesis into a data-touching result, confounder-adjusted with
bootstrap CIs. Non-diagnostic, population-level.

CRP is right-skewed, so the primary outcome is **log CRP** (ln(1+CRP)); raw CRP and CV history (a
linear-probability screen) are secondary. A POSITIVE coefficient = more periodontal severity → higher
CRP / more CV history — the mediator/risk direction the model predicts.

Requires pandas + network. Usage:  python src/run_perio_cv.py [--exposure perio_cal|perio_ppd]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.nhanes import download_files, load_cv_table
from histora.perio_cognition import analyze

OUTCOMES = ["log_hs_crp", "hs_crp", "cv_history"]
CONFOUNDERS = ["age", "education", "smoking", "bmi", "hba1c"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Perio↔CV (CRP + CV history) association, NHANES 2009-2010")
    ap.add_argument("--exposure", choices=["perio_cal", "perio_ppd"], default="perio_cal")
    ap.add_argument("--dest", default=os.path.join(os.path.dirname(__file__), "..", ".nhanes"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "perio_cv_report.json"))
    args = ap.parse_args()

    try:
        import pandas  # noqa: F401
    except ImportError:
        raise SystemExit("pandas required: pip install pandas (and network access).")

    paths = download_files(args.dest)
    records = load_cv_table(paths)
    for r in records:                       # log CRP (skewed marker) as the primary outcome
        r["log_hs_crp"] = math.log1p(r["hs_crp"]) if r.get("hs_crp") is not None else None

    report = analyze(records, args.exposure, OUTCOMES, CONFOUNDERS)
    report["meta"] = {"cycle": "NHANES 2009-2010", "n_records_total": len(records),
                      "exposure": args.exposure, "files": list(paths),
                      "note": "positive coef = more periodontal severity → higher CRP / CV history"}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"NHANES 2009-2010 | exposure={args.exposure} | {len(records)} participants merged")
    print(f"confounders adjusted: {', '.join(CONFOUNDERS)}\n")
    for outcome, r in report["outcomes"].items():
        if "adjusted_std_coef" not in r:
            print(f"  {outcome:14s} n={r['n']}  ({r.get('note')})")
            continue
        sig = "SIG" if r["significant"] else "ns "
        arrow = "↑more-perio→higher" if r["adjusted_std_coef"] > 0 else "↓"
        print(f"  {outcome:14s} n={r['n']:5d}  crude={r['crude_std_coef']:+.3f}  "
              f"adj={r['adjusted_std_coef']:+.3f}  CI90=[{r['ci_90_adjusted']['lo']:+.3f},"
              f"{r['ci_90_adjusted']['hi']:+.3f}]  {sig}  {arrow}")
    print("\nNON-DIAGNOSTIC population association (perio→CRP is the mediator the model predicts;")
    print("this is the CV-axis empirical anchor — a data-touching result, not causation).")
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
