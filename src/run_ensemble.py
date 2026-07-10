"""Run the ensemble — predictions as ranges over the swept uncertain parameters (offline, no API/GPU).

For each structural stratum: a Latin-hypercube sweep of the flagged/uncertain parameters (ε within its
ΔCRP-anchor spread, the CV and neuro couplings over plausible bands) → an envelope (median + 90% band)
for CRP, CV index, and tau outcomes, plus which unknown dominates each. Non-diagnostic.

Usage:  python src/run_ensemble.py [--n 200]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.ensemble import ensemble_report
from histora.registry import SUBMODELS


def _strata() -> list[dict]:
    base = {"perio_stage": "stage III"}
    return [
        {"label": "low BOP", **base, "bop_band": "low", "comorbidities": []},
        {"label": "high BOP", **base, "bop_band": "high", "comorbidities": []},
        {"label": "high BOP + diabetes + smoking", "perio_stage": "stage IV", "bop_band": "high",
         "comorbidities": ["diabetes", "smoking"]},
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the oral-systemic ensemble (ranges, not points)")
    ap.add_argument("--n", type=int, default=200, help="Latin-hypercube samples")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "ensemble_report.json"))
    args = ap.parse_args()

    reports = []
    for feat in _strata():
        label = feat.pop("label")
        reports.append({"label": label, **ensemble_report(feat, n=args.n)})

    out = {"registry": SUBMODELS, "n_samples": args.n, "strata": reports}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    for r in reports:
        env = r["envelope"]
        crp, tau = env["crp_mg_l"], env["tau_burden_rel_increase"]
        print(f"\n{r['label']}  (n={r['n_samples']} LHS)")
        print(f"  CRP            median {crp['median']:.2f}  90% band [{crp['lo']:.2f}, {crp['hi']:.2f}] mg/L")
        print(f"  tau burden +%  median {tau['median']*100:.1f}%  90% band "
              f"[{tau['lo']*100:.1f}%, {tau['hi']*100:.1f}%]")
        dom_crp = max(r["sensitivity"]["crp_mg_l"].items(), key=lambda kv: abs(kv[1]), default=("-", 0))
        dom_tau = max(r["sensitivity"]["tau_burden_rel_increase"].items(),
                      key=lambda kv: abs(kv[1]), default=("-", 0))
        print(f"  dominant unknown → CRP: {dom_crp[0]} (elasticity {dom_crp[1]:+.2f}); "
              f"tau: {dom_tau[0]} ({dom_tau[1]:+.2f})")
    print("\nNon-diagnostic: parameter-level ranges for a structural stratum. wrote:", args.out)


if __name__ == "__main__":
    main()
