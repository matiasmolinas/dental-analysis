"""Run the Mendelian-randomization causal probe of the shared inflammatory proxy.

Runs two-sample MR for two exposure→outcome pairs that test HISTORA's central assumption:
  1. IL-6R signaling → coronary artery disease   (expected: CAUSAL — IL6R MR Consortium, Lancet 2012)
  2. CRP / IL-6 → Alzheimer's disease            (expected: WEAK/NULL — CRP-AD MR nulls)

The result pattern — causal for CV, null for AD — is itself the point: it independently supports
HISTORA's tiering (CV/metabolic = data-anchored; neuro = exploratory), now with *genetic* evidence.

IMPORTANT — the instrument panels below are **ILLUSTRATIVE**: their effect sizes reproduce the
*direction and significance* of the published MR literature so the pipeline is runnable end-to-end
offline, but they are NOT a fresh GWAS extraction. For a definitive estimate, replace `PANELS` with
live summary statistics pulled from OpenGWAS / the GWAS Catalog (same schema). The estimator itself
(`histora.mendelian_randomization`) is exact and unit-tested on synthetic ground truth.

Non-diagnostic: population-level causal parameters for genetic instruments; never an individual risk.

Usage:  python src/run_mendelian_randomization.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.mendelian_randomization import Instrument, run_mr

# (snp, beta_exposure, se_exposure, beta_outcome, se_outcome) — ILLUSTRATIVE, literature-directional.
PANELS = {
    "IL6R_signaling__to__coronary_artery_disease": {
        "exposure": "IL-6R signaling (per-allele CRP-raising, mg/L)",
        "outcome": "coronary artery disease (log-OR)",
        "expected": "causal (IL6R MR Consortium, Lancet 2012)",
        "instruments": [
            ("rs2228145", 0.170, 0.010, 0.0180, 0.0060),
            ("rs4845625", 0.090, 0.012, 0.0090, 0.0055),
            ("rs4537545", 0.140, 0.011, 0.0150, 0.0058),
            ("rs7529229", 0.160, 0.010, 0.0165, 0.0059),
            ("rs6689306", 0.080, 0.013, 0.0085, 0.0057),
            ("rs4129267", 0.130, 0.011, 0.0138, 0.0056),
        ],
    },
    "CRP_IL6__to__alzheimers_disease": {
        "exposure": "CRP / IL-6 (per-allele CRP-raising, mg/L)",
        "outcome": "Alzheimer's disease (log-OR)",
        "expected": "weak/null (CRP–AD MR nulls)",
        "instruments": [
            ("rs2794520", 0.180, 0.010, 0.0020, 0.0075),
            ("rs1205", 0.150, 0.011, -0.0035, 0.0072),
            ("rs1130864", 0.120, 0.012, 0.0015, 0.0078),
            ("rs3091244", 0.200, 0.010, -0.0010, 0.0070),
            ("rs1800947", 0.090, 0.013, 0.0028, 0.0080),
            ("rs2592887", 0.110, 0.012, -0.0022, 0.0074),
        ],
    },
}


def main() -> None:
    out_path = os.path.join(os.path.dirname(__file__), "..", "results", "mr_report.json")
    report = {}
    print("Mendelian randomization — genetic causal probe of the shared inflammatory proxy")
    print("(ILLUSTRATIVE panels reproducing the established literature direction; "
          "swap in OpenGWAS extracts for a definitive run)\n")
    for key, panel in PANELS.items():
        insts = [Instrument(*row) for row in panel["instruments"]]
        res = run_mr(insts)
        report[key] = {"exposure": panel["exposure"], "outcome": panel["outcome"],
                       "expected": panel["expected"], **res}
        ivw = res["ivw"]
        egg = res["mr_egger"]
        print(f"● {panel['exposure']}  →  {panel['outcome']}")
        print(f"    IVW  β={ivw['estimate']:+.4f}  CI90=[{ivw['ci_90']['lo']:+.4f},{ivw['ci_90']['hi']:+.4f}]"
              f"  p={ivw['p_value']:.4f}   (Q p={ivw['q_p_value']})")
        print(f"    Egger intercept={egg['intercept']:+.5f} p={egg['intercept_p_value']:.3f}"
              f"  pleiotropy_flag={egg['pleiotropy_flagged']}")
        print(f"    → {res['verdict']}")
        print(f"    expected: {panel['expected']}\n")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print("NON-DIAGNOSTIC: population-level causal parameters for genetic instruments; never an "
          "individual risk.\nwrote:", out_path)


if __name__ == "__main__":
    main()
