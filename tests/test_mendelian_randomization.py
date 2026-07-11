"""Tests for the two-sample MR engine — pure/offline, validated on SYNTHETIC ground truth.

The estimator's correctness is proven by recovering a known causal slope, a known null, and a planted
directional-pleiotropy signal — independent of the illustrative panels in the runner.

Run:  python tests/test_mendelian_randomization.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.mendelian_randomization import Instrument, ivw, mr_egger, run_mr, weighted_median


def _panel(slope, pleiotropy=0.0, n=8, noise=0.0005):
    """Synthetic instruments: beta_outcome = slope*beta_exposure + pleiotropy + tiny deterministic wiggle."""
    insts = []
    for k in range(n):
        be = 0.05 + 0.02 * k
        wiggle = noise * ((k % 3) - 1)          # deterministic, mean ~0
        bo = slope * be + pleiotropy + wiggle
        insts.append(Instrument(f"rs{k}", be, 0.010, bo, 0.006))
    return insts


def test_ivw_recovers_known_causal_slope():
    r = ivw(_panel(slope=0.10))
    assert abs(r["estimate"] - 0.10) < 0.02
    assert r["p_value"] < 0.05           # a real effect is detected


def test_ivw_null_is_not_significant():
    r = ivw(_panel(slope=0.0))
    assert abs(r["estimate"]) < 0.02
    assert r["p_value"] > 0.10           # no effect → not significant


def test_egger_intercept_detects_directional_pleiotropy():
    clean = mr_egger(_panel(slope=0.10, pleiotropy=0.0))
    dirty = mr_egger(_panel(slope=0.10, pleiotropy=0.02))   # all SNPs share an off-target effect
    assert not clean["pleiotropy_flagged"]
    assert dirty["pleiotropy_flagged"]                      # intercept flags it
    assert abs(dirty["intercept"] - 0.02) < 0.01


def test_weighted_median_agrees_on_clean_data():
    m = weighted_median(_panel(slope=0.10), n_boot=300, seed=1)
    assert abs(m["estimate"] - 0.10) < 0.03


def test_run_mr_verdict_causal_vs_null():
    causal = run_mr(_panel(slope=0.12))
    null = run_mr(_panel(slope=0.0))
    assert causal["causal_support"] is True and causal["direction"] == "risk-increasing"
    assert null["causal_support"] is False


def test_pleiotropy_blocks_causal_support():
    # a significant IVW slope but with directional pleiotropy → NOT clean causal support
    r = run_mr(_panel(slope=0.10, pleiotropy=0.02))
    assert r["mr_egger"]["pleiotropy_flagged"] is True
    assert r["causal_support"] is False


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
