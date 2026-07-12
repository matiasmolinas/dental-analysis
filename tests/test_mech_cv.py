"""Tests for the CV atherosclerosis ODE (Stage-3, Phase B) — pure python.

Verifies the foam-cell process grows plaque, plaque burden is monotone in oral severity, the therapy
counterfactual reduces plaque, the γ_cv sweep gives a range, and the guardrail holds.

Run:  python tests/test_mech_cv.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.mech_calibrate import calibrated_params
from histora.mech_cv import cv_plaque_centerpiece, cv_params, plaque_trajectory

P = calibrated_params()


def test_plaque_accumulates_over_time():
    tr = plaque_trajectory(3.0, P)
    assert tr["foam"][-1] > tr["foam"][0]          # foam cells accumulate (plaque grows)
    assert tr["foam"][0] == 0.0


def test_plaque_monotone_in_severity():
    low = cv_plaque_centerpiece({"bop_band": "low"}, P)
    high = cv_plaque_centerpiece({"bop_band": "high", "perio_stage": "stage IV",
                                  "comorbidities": ["diabetes"]}, P)
    assert (high["plaque_burden_horizon"]["relative_increase"]
            > low["plaque_burden_horizon"]["relative_increase"] >= 0)


def test_therapy_reduces_plaque_and_sweep_range():
    c = cv_plaque_centerpiece({"bop_band": "high", "perio_stage": "stage III"}, P)
    assert c["counterfactual_therapy"]["plaque_rel_reduction"] > 0
    lo, hi = c["plaque_rel_increase_range_over_gamma"]
    assert lo < hi
    assert len(c["gamma_cv_sweep"]) == 3


def test_non_diagnostic_flags_and_numeric_ignored():
    c = cv_plaque_centerpiece({"bop_band": "high"}, P)
    assert c["confidence"] == "scaffold"
    assert any("non-diagnostic" in f for f in c["flags"])
    a = cv_plaque_centerpiece({"bop_band": "high", "comorbidities": ["diabetes"]}, P)
    b = cv_plaque_centerpiece({"bop_band": "high", "comorbidities": ["diabetes"], "bop_pct": 47}, P)
    assert a["plaque_burden_horizon"]["with_oral_inflammation"] == b["plaque_burden_horizon"]["with_oral_inflammation"]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
