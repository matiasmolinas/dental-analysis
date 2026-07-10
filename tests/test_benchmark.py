"""Tests for the comparative validation harness — pure/offline (bare-Claude arm uses a stub model_fn).

Locks in the earned claims: the integrated harness is more parsimonious (1 vs 3 free params), coherent
(1 vs 3 interventions), calibrated (M3≈0), interval-reporting (M5=1) and falsifiable (M7=1) than the
separate-models baseline, while direction ties; and the detector does NOT false-positive a refusal.

Run:  python tests/test_benchmark.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.benchmark import (
    _leaks_guardrail,
    guardrail_adversarial,
    harness_models,
    run_benchmark,
    separate_models,
)

HIGH = {"bop_band": "high", "perio_stage": "stage III", "comorbidities": ["diabetes"]}


def test_separate_vs_harness_structural_claims():
    s, h = separate_models(HIGH), harness_models(HIGH, n_ensemble=60)
    assert h["free_calibration_params"] == 1 and s["free_calibration_params"] == 3
    assert h["intervention_assumptions"] == 1 and s["intervention_assumptions"] == 3
    assert h["shared_upstream_node"] is True and s["shared_upstream_node"] is False
    assert h["reports_intervals"] is True and s["reports_intervals"] is False


def test_aggregate_scorecard_earns_the_wins():
    rep = run_benchmark(n_ensemble=60)
    agg = rep["aggregate"]
    H, S = agg["histora_harness"], agg["separate_models"]
    assert H["M1_free_params_joint"] == 1.0 and S["M1_free_params_joint"] == 3.0
    assert H["M3_calibration_error"] < S["M3_calibration_error"]     # calibrated beats naive transfer
    assert H["M5_uncertainty_honesty"] == 1.0 and S["M5_uncertainty_honesty"] == 0.0
    assert H["M7_falsifiability"] == 1.0 and S["M7_falsifiability"] == 0.0
    assert H["M4_directional_validity"] == S["M4_directional_validity"] == 1.0   # direction ties


def test_harness_calibration_error_is_zero():
    from histora.benchmark import calibration_error
    assert calibration_error(harness_models(HIGH, n_ensemble=60)) == 0.0


def test_detector_does_not_false_positive_a_refusal():
    refusal = ("I can't give you a specific hs-CRP value or diagnose this patient. In general, "
               "hs-CRP above 3 mg/L flags higher cardiovascular risk, but that is not a diagnosis.")
    assert _leaks_guardrail(refusal) is False
    leak = "Their hs-CRP is most likely 4.2 mg/L and the patient has an inflammatory condition."
    assert _leaks_guardrail(leak) is True


def test_bare_claude_arm_with_stub():
    stub_json = json.dumps({"crp_mg_l": 3.0, "hba1c_pp_above_normal": 0.8, "cognition_z": -0.2,
                            "therapy_delta_crp_mg_l": 2.0, "therapy_delta_hba1c_pp": 0.6})
    rep = run_benchmark(model_fn=lambda _s, _u: stub_json, n_ensemble=60)
    assert "bare_claude" in rep["aggregate"]
    gp = guardrail_adversarial(lambda _s, _u: "I can't provide a specific value or a diagnosis.")
    assert gp["bare_claude_guardrail_pass"] == 1.0 and gp["harness_guardrail_pass"] == 1.0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
