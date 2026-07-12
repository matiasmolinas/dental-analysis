"""Tests for the Bergman glucose-insulin axis (Stage-3, Phase B) — pure python.

Verifies inflammation degrades insulin sensitivity S_I, the meal response raises mean glucose with
severity, HbA1c is calibrated to the ~0.35 pp therapy anchor, the β_si sweep gives a range, and the
guardrail holds.

Run:  python tests/test_mech_glucose.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.mech_calibrate import calibrated_params
from histora.mech_glucose import (
    calibrate_glucose,
    glucose_centerpiece,
    glucose_response,
    _s_i,
    glucose_params,
)

P = calibrated_params()


def test_si_degrades_with_inflammation():
    p = glucose_params(P)
    assert _s_i(0.0, p) > _s_i(1.0, p) > _s_i(3.0, p)      # S_I falls as gain rises


def test_mean_glucose_monotone_in_gain():
    g0 = glucose_response(0.0, glucose_params(P))["mean_glucose"]
    g1 = glucose_response(1.0, glucose_params(P))["mean_glucose"]
    assert g1 > g0


def test_hba1c_calibrated_to_anchor():
    cal = calibrate_glucose(p=dict(P))
    c = glucose_centerpiece({"bop_band": "high", "perio_stage": "stage III", "comorbidities": []}, dict(P))
    assert abs(c["hba1c_shift_pp"] - 0.35) < 0.02          # reference case reproduces the anchor
    assert cal["k_hba1c_glu"] > 0


def test_centerpiece_monotone_and_sweep_range():
    low = glucose_centerpiece({"bop_band": "low"}, dict(P))
    high = glucose_centerpiece({"bop_band": "high", "perio_stage": "stage IV",
                                "comorbidities": ["diabetes"]}, dict(P))
    assert high["hba1c_shift_pp"] > low["hba1c_shift_pp"]
    assert high["si_relative_drop"] > low["si_relative_drop"] >= 0
    lo, hi = high["hba1c_shift_range_over_beta"]
    assert lo < hi


def test_non_diagnostic():
    c = glucose_centerpiece({"bop_band": "high"}, dict(P))
    assert any("non-diagnostic" in f for f in c["flags"])


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
