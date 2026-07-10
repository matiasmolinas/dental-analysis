"""Run the mechanistic centerpiece end to end (Harness 1, Phase 1) — offline, no API, no GPU.

Instantiates the calibratable pipeline (periodontal source → IL-6 → CRP → CV & neuro axes),
calibrates ε to the ΔCRP-after-therapy anchor, runs it over structural strata, sweeps the
epistemic-risk parameter (ε) to report a RANGE, and writes a report. Pure deterministic modeling:
this is the *tool* an agent would call — no model calls here.

NON-DIAGNOSTIC: features are structural bands/flags (from lever_ledger.case_signature), outputs are
parameter-level predictions and swept ranges, never a patient diagnosis or an imputed value.

Usage:  python src/run_mechanistic.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.relational_signals import case_signature
from histora.mech_calibrate import calibrated_params
from histora.mech_models import centerpiece, crp_steady, il6_steady, structural_load
from histora.record_formats import RECORD


def _features_from_record(record: dict) -> dict:
    """Structural features for the model = the case signature (bands/flags only)."""
    sig = case_signature(record)
    return {"bop_band": sig["bop_band"], "perio_stage": sig["perio_stage"],
            "comorbidities": sig["comorbidities"]}


def _strata() -> list[dict]:
    """A small structural sweep to show the model's monotone response (non-diagnostic bands)."""
    base = {"perio_stage": "stage III", "comorbidities": []}
    return [
        {"label": "low BOP", **base, "bop_band": "low"},
        {"label": "moderate BOP", **base, "bop_band": "moderate"},
        {"label": "high BOP", **base, "bop_band": "high"},
        {"label": "high BOP + diabetes", "perio_stage": "stage III", "bop_band": "high",
         "comorbidities": ["diabetes"]},
        {"label": "high BOP + diabetes + smoking", "perio_stage": "stage IV", "bop_band": "high",
         "comorbidities": ["diabetes", "smoking"]},
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the mechanistic centerpiece (offline)")
    ap.add_argument("--target-delta-crp", type=float, default=0.5,
                    help="ΔhsCRP-after-therapy calibration anchor (mg/L)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "mechanistic_report.json"))
    args = ap.parse_args()

    p = calibrated_params(target_delta_crp=args.target_delta_crp)
    cal = p["_calibration"]

    # the grounded built-in case + the structural strata
    grounded = {"label": "built-in NHANES-grounded case", **_features_from_record(RECORD)}
    cases = [grounded] + _strata()
    results = []
    for feat in cases:
        label = feat.pop("label")
        res = centerpiece(feat, p)
        results.append({"label": label, **res})

    # sweep the epistemic-risk parameter ε over its anchor spread → a RANGE of CRP for the ref case
    ref = {"bop_band": "high", "perio_stage": "stage III", "comorbidities": []}
    load = structural_load(ref)
    eps0 = p["epsilon"]
    eps_grid = [round(eps0 * f, 4) for f in (0.5, 0.75, 1.0, 1.5, 2.0)]
    eps_sweep = [{"epsilon": e,
                  "crp_mg_l": round(crp_steady(il6_steady(e * load, dict(p, epsilon=e)),
                                               dict(p, epsilon=e)), 4)}
                 for e in eps_grid]

    report = {
        "calibration": cal,
        "params_anchored": {k: p[k] for k in ("k_deg_crp", "EC50_il6", "crp_max", "mu_il6",
                                              "base_prod_il6", "epsilon", "gamma_cv", "beta_neuro",
                                              "alpha_tau")},
        "cases": results,
        "epsilon_sweep_reference_high_BOP": eps_sweep,
        "guardrail": "non-diagnostic: structural bands only; parameter-level predictions + ranges",
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"ε calibrated = {cal['epsilon']} (ΔCRP target {cal['target_delta_crp']} → "
          f"achieved {cal['achieved_delta_crp']} mg/L, reached={cal['reached_target']})")
    for r in results:
        ss = r["steady_state"]
        na = r["neuro_axis"]
        cv = r["cv_axis"]
        print(f"  {r['label']:38s} IL6={ss['il6_pg_ml']:5.2f}  CRP={ss['crp_mg_l']:5.2f} mg/L"
              f"  CV×={cv['recruitment_multiplier']:.2f}  tauα+{na['relative_increase']*100:4.1f}%"
              f"  {'[dyn ok]' if r.get('dynamics_check', {}).get('stable') else ''}")
    print("ε-sweep CRP range (high-BOP ref):",
          f"{eps_sweep[0]['crp_mg_l']}–{eps_sweep[-1]['crp_mg_l']} mg/L")
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
