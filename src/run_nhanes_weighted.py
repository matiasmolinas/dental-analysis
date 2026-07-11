"""Design-adjusted NHANES analysis (WS6) — survey weights + clustering + FDR, weighted vs unweighted.

Re-runs the three validated associations with the NHANES complex-survey design (exam weights,
strata, PSU) and reports them **beside** the unweighted estimates, so any attenuation is visible, with
a joint Benjamini–Hochberg FDR across all outcomes and a CAL-vs-PPD sensitivity check.

Usage:  python src/run_nhanes_weighted.py [--exposure perio_cal|perio_ppd]   (needs pandas + cached NHANES)
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.nhanes import (download_files, download_neuro_files, load_cv_table, load_neuro_table)
from histora.nhanes_survey import analyze_weighted, benjamini_hochberg

CYCLE_2009 = {"outcomes": ["hs_crp", "cv_history", "hba1c"],
              "confounders": ["age", "education", "smoking", "bmi"]}
CYCLE_2011 = {"outcomes": ["digit_symbol", "animal_fluency", "cerad_immediate", "cerad_delayed"],
              "confounders": ["age", "education", "smoking", "hba1c"]}


def main() -> None:
    ap = argparse.ArgumentParser(description="Design-adjusted NHANES analysis (WS6)")
    ap.add_argument("--exposure", choices=["perio_cal", "perio_ppd"], default="perio_cal")
    ap.add_argument("--dest", default=os.path.join(os.path.dirname(__file__), "..", ".nhanes"))
    ap.add_argument("--dest-neuro", default=os.path.join(os.path.dirname(__file__), "..", ".nhanes_neuro"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "nhanes_weighted_report.json"))
    args = ap.parse_args()
    try:
        import pandas  # noqa: F401
    except ImportError:
        raise SystemExit("pandas required: pip install pandas (and cached/network NHANES).")

    cv_rows = load_cv_table(download_files(args.dest))
    neuro_rows = load_neuro_table(download_neuro_files(args.dest_neuro))

    r09 = analyze_weighted(cv_rows, args.exposure, CYCLE_2009["outcomes"], CYCLE_2009["confounders"])
    r11 = analyze_weighted(neuro_rows, args.exposure, CYCLE_2011["outcomes"], CYCLE_2011["confounders"])

    # joint BH-FDR across all outcomes from both cycles
    pvals = {}
    for cyc, rep in (("2009-2010", r09), ("2011-2012", r11)):
        for o, res in rep["outcomes"].items():
            if "p_value" in res:
                pvals[f"{cyc}:{o}"] = res["p_value"]
    joint_fdr = benjamini_hochberg(pvals, q=0.10)

    # CAL vs PPD sensitivity (weighted coefficient only)
    other = "perio_ppd" if args.exposure == "perio_cal" else "perio_cal"
    s09 = analyze_weighted(cv_rows, other, CYCLE_2009["outcomes"], CYCLE_2009["confounders"])
    s11 = analyze_weighted(neuro_rows, other, CYCLE_2011["outcomes"], CYCLE_2011["confounders"])

    report = {"exposure": args.exposure, "cycle_2009_2010": r09, "cycle_2011_2012": r11,
              "joint_bh_fdr": joint_fdr,
              "sensitivity_other_exposure": {"exposure": other,
                                             "cycle_2009_2010": s09, "cycle_2011_2012": s11}}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Design-adjusted NHANES analysis | exposure={args.exposure}")
    print("weighted std OLS (WTMEC2YR) + cluster bootstrap (PSU within SDMVSTRA) + joint BH-FDR\n")
    print(f"  {'outcome':26s} {'unwtd':>8s} {'wtd':>8s} {'design CI90':>20s} {'p':>8s}  FDR")
    for cyc, rep in (("2009-2010", r09), ("2011-2012", r11)):
        for o, res in rep["outcomes"].items():
            if "weighted_std_coef" not in res:
                print(f"  {cyc}:{o:16s} (n={res.get('n')}: {res.get('note')})")
                continue
            ci = res["design_ci_90"]
            fdr = joint_fdr[f"{cyc}:{o}"]["survives_fdr"]
            print(f"  {cyc}:{o:16s} {res['unweighted_std_coef']:+8.3f} {res['weighted_std_coef']:+8.3f} "
                  f"[{ci['lo']:+.3f},{ci['hi']:+.3f}]  {res['p_value']:.4f}  "
                  f"{'SURV' if fdr else 'drop'}")
    print("\nNON-DIAGNOSTIC design-adjusted population associations. wrote:", args.out)


if __name__ == "__main__":
    main()
