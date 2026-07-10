"""Tests for the oral-systemic mechanistic models + centerpiece + calibration (Phase 1).

Verifies the closed-form IL-6/CRP steady states match the integrated dynamics, monotonicity of the
structural source and both axis couplings, the ε calibration hits its ΔCRP anchor, the
counterfactual levers, the non-diagnostic guardrail (no numeric patient values in features), and
that the ODE core is stable. Pure python.

Run:  python tests/test_mech_models.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mech_calibrate import calibrate_epsilon, calibrated_params
from mech_models import (
    CRP_BASAL,
    IL6_BASAL,
    centerpiece,
    crp_steady,
    default_params,
    il6_steady,
    inflammatory_gain,
    cv_axis,
    neuro_axis,
    periodontal_source,
    structural_load,
)


def test_closed_form_matches_dynamics():
    p = default_params()
    res = centerpiece({"bop_band": "high", "perio_stage": "stage III", "comorbidities": []}, p)
    dyn = res["dynamics_check"]
    assert dyn["matches_closed_form"] is True
    assert dyn["stable"] is True


def test_structural_load_monotone_and_comorbid_amplifies():
    lo = structural_load({"bop_band": "low"})
    mid = structural_load({"bop_band": "moderate"})
    hi = structural_load({"bop_band": "high"})
    assert lo < mid < hi
    plain = structural_load({"bop_band": "high"})
    with_dm = structural_load({"bop_band": "high", "comorbidities": ["diabetes"]})
    assert with_dm > plain


def test_source_and_crp_increase_with_severity():
    p = default_params()
    low = centerpiece({"bop_band": "low"}, p, verify_dynamics=False)
    high = centerpiece({"bop_band": "high"}, p, verify_dynamics=False)
    assert high["steady_state"]["crp_mg_l"] > low["steady_state"]["crp_mg_l"]
    assert high["steady_state"]["il6_pg_ml"] > low["steady_state"]["il6_pg_ml"]


def test_basal_state_when_no_source():
    p = default_params()
    # zero load (unknown band defaults low but not zero); force source 0 via empty structural
    il6 = il6_steady(0.0, p)
    assert abs(il6 - IL6_BASAL) < 1e-9
    assert abs(crp_steady(il6, p) - (p["crp_max"] * IL6_BASAL / (p["EC50_il6"] + IL6_BASAL))) < 1e-9


def test_axis_couplings_monotone_in_gain():
    p = default_params()
    assert inflammatory_gain(IL6_BASAL) == 0.0
    assert cv_axis(10.0, p)["recruitment_multiplier"] > cv_axis(IL6_BASAL, p)["recruitment_multiplier"]
    assert neuro_axis(10.0, p)["relative_increase"] > 0.0
    assert neuro_axis(IL6_BASAL, p)["relative_increase"] == 0.0


def test_calibration_hits_anchor():
    cal = calibrate_epsilon(target_delta_crp=0.5)
    assert cal["reached_target"] is True
    assert abs(cal["achieved_delta_crp"] - 0.5) < 1e-2
    assert cal["epsilon"] > 0


def test_calibrated_params_therapy_counterfactual_matches_anchor():
    p = calibrated_params(target_delta_crp=0.5)
    # the reference high-BOP case therapy ΔCRP should be ~0.5
    res = centerpiece({"bop_band": "high", "perio_stage": "stage III", "comorbidities": []}, p,
                      verify_dynamics=False)
    assert abs(res["counterfactuals"]["periodontal_therapy"]["delta_crp_mg_l"] - 0.5) < 5e-2
    assert res["epsilon_calibrated"] is True


def test_il6_blockade_lever_relaxes_to_basal():
    p = calibrated_params()
    res = centerpiece({"bop_band": "high", "comorbidities": ["diabetes"]}, p, verify_dynamics=False)
    block = res["counterfactuals"]["il6_blockade"]
    assert block["crp_mg_l"] < res["steady_state"]["crp_mg_l"]  # blockade lowers CRP
    assert block["delta_crp_mg_l"] > 0


def test_non_diagnostic_features_have_no_numeric_patient_values():
    # the source must be computable from bands/flags only; passing a raw numeric field is ignored
    p = default_params()
    s_bands = periodontal_source({"bop_band": "high", "comorbidities": ["diabetes"]}, p)
    s_with_noise = periodontal_source(
        {"bop_band": "high", "comorbidities": ["diabetes"], "bop_pct": 47, "hba1c": 8.1}, p)
    assert s_bands == s_with_noise  # numeric patient values do not enter the model


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
