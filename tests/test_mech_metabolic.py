"""Tests for the metabolic axis (C4: inflammation → insulin resistance → HbA1c) — pure python.

Verifies monotonicity in the gain, the HbA1c calibration to the ~0.35 pp therapy anchor, and the
centerpiece shape + non-diagnostic flags.

Run:  python tests/test_mech_metabolic.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.mech_metabolic import (
    calibrate_hba1c,
    calibrated_metabolic_params,
    hba1c_shift_pp,
    insulin_resistance_index,
    metabolic_centerpiece,
    metabolic_params,
)


def test_indices_monotone_and_zero_at_zero_gain():
    p = metabolic_params()
    assert insulin_resistance_index(0.0, p) == 1.0
    assert hba1c_shift_pp(0.0, p) == 0.0
    assert insulin_resistance_index(1.0, p) > insulin_resistance_index(0.3, p)
    assert hba1c_shift_pp(1.0, p) > hba1c_shift_pp(0.3, p)


def test_calibration_hits_hba1c_anchor():
    cal = calibrate_hba1c(target_pp=0.35)
    p = calibrated_metabolic_params()
    # the reference high-BOP case's therapy drop reproduces ~0.35 pp
    r = metabolic_centerpiece({"bop_band": "high", "perio_stage": "stage III", "comorbidities": []}, p)
    assert abs(r["counterfactual_therapy"]["hba1c_drop_pp"] - 0.35) < 0.02
    assert cal["k_hba1c"] > 0


def test_centerpiece_monotone_in_severity_and_flags():
    low = metabolic_centerpiece({"bop_band": "low", "comorbidities": []})
    high = metabolic_centerpiece({"bop_band": "high", "comorbidities": ["diabetes", "smoking"],
                                  "perio_stage": "stage IV"})
    assert high["hba1c_shift_pp"] > low["hba1c_shift_pp"]
    assert high["insulin_resistance_index"] > low["insulin_resistance_index"]
    assert high["confidence"] == "scaffold" and any("FLAGGED" in f for f in high["flags"])


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
