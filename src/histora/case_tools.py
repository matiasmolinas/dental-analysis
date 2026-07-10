"""Harness-as-a-tool — mechanistic predictions for a single case, for the case-evaluation plugin.

Given an integrated oral + systemic record, derive its STRUCTURAL stratum (bands/flags only, never a
patient value) and run the mechanistic harness on it: the calibrated centerpiece (IL-6/CRP + CV/neuro),
the counterfactual levers, and the ensemble envelope (ranges, not points). Returns a non-diagnostic
prediction block the plugin's `/evaluate-case` flow attaches to Claude's relational analysis. This is
the deterministic half of the agent — no Claude call here; the guardrail is enforced by construction
(structural stratum in, parameter-level ranges out).
"""

from __future__ import annotations

from typing import Any

from .ensemble import ensemble_report
from .mech_calibrate import calibrated_params
from .mech_models import centerpiece
from .mech_neuro import neuro_centerpiece, neuro_params
from .relational_signals import case_signature


def case_stratum(record: dict) -> dict:
    """The structural stratum the models read: perio stage, BOP band, comorbidity set (no values)."""
    sig = case_signature(record)
    return {"bop_band": sig["bop_band"], "perio_stage": sig["perio_stage"],
            "comorbidities": sig["comorbidities"]}


def case_mechanistic_predictions(record: dict, n_ensemble: int = 200) -> dict[str, Any]:
    """Run the harness on a case's structural stratum. Returns the point predictions (calibrated),
    the ensemble envelope (ranges over the swept unknowns), the counterfactual levers, and the honest
    flags. Non-diagnostic: parameter-level population predictions, never a patient inference."""
    features = case_stratum(record)
    p = neuro_params(calibrated_params())

    cp = centerpiece(features, p, verify_dynamics=True)
    nc = neuro_centerpiece(features, p)
    env = ensemble_report(features, n=n_ensemble)

    return {
        "structural_stratum": features,
        "systemic": {
            "il6_pg_ml": cp["steady_state"]["il6_pg_ml"],
            "crp_mg_l": cp["steady_state"]["crp_mg_l"],
            "crp_above_cv_risk_threshold": cp["steady_state"]["crp_above_cv_risk_threshold"],
            "inflammatory_gain_pg_ml": cp["inflammatory_gain_pg_ml"],
        },
        "cardiovascular": {"recruitment_multiplier": cp["cv_axis"]["recruitment_multiplier"],
                           "confidence": cp["cv_axis"]["confidence"]},
        "neuro": {"neuroinflammation": nc["neuroinflammation"],
                  "tau_alpha_relative_increase": nc["tau_alpha"]["relative_increase"],
                  "tau_burden_relative_increase": nc["tau_burden_horizon"]["relative_increase"],
                  "connectome_front_arrival_years": nc["connectome_front_arrival_years"],
                  "confidence": nc["confidence"]},
        "counterfactuals": {
            "periodontal_therapy": cp["counterfactuals"]["periodontal_therapy"],
            "il6_blockade": cp["counterfactuals"]["il6_blockade"],
            "tau_onset_therapy_delay_years": nc["tau_onset_years"]["therapy_delay_years"],
        },
        "ranges_over_uncertainty": env["envelope"],
        "dominant_uncertainty": {o: max(s.items(), key=lambda kv: abs(kv[1]), default=("-", 0))[0]
                                 for o, s in env["sensitivity"].items()},
        "flags": nc["flags"],
        "guardrail": "non-diagnostic: structural stratum → parameter-level ranges; never a patient value",
    }
