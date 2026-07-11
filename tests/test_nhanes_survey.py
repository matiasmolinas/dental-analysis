"""Tests for the design-adjusted NHANES analysis — pure/offline, on synthetic ground truth.

Run:  python tests/test_nhanes_survey.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.nhanes_survey import (
    analyze_weighted,
    benjamini_hochberg,
    cluster_bootstrap,
    weighted_ols_exposure_coef,
)


def test_weighted_ols_standardized_is_correlation():
    # standardized OLS returns the (weighted) correlation, so a perfect line → 1.0 regardless of slope
    x = [float(i) for i in range(50)]
    y = [0.5 * v for v in x]
    w = [1.0] * 50
    assert abs(weighted_ols_exposure_coef(y, x, [], w) - 1.0) < 1e-6
    # a negative perfect line → -1.0
    assert abs(weighted_ols_exposure_coef([-3.0 * v for v in x], x, [], w) + 1.0) < 1e-6


def test_weights_change_the_estimate():
    # re-weighting a high-leverage point measurably changes the design-adjusted coefficient
    x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    y = [1.0, 2.0, 3.0, 4.0, 5.0, 60.0]        # last point is high-leverage
    c_flat = weighted_ols_exposure_coef(y, x, [], [1.0] * 6)
    c_down = weighted_ols_exposure_coef(y, x, [], [1.0, 1.0, 1.0, 1.0, 1.0, 0.01])
    assert abs(c_down - c_flat) > 0.05          # weights matter (this is the point of survey weighting)


def test_benjamini_hochberg():
    p = {"a": 0.001, "b": 0.02, "c": 0.20, "d": 0.80}
    bh = benjamini_hochberg(p, q=0.10)
    assert bh["a"]["survives_fdr"] is True
    assert bh["d"]["survives_fdr"] is False
    # ranks assigned by ascending p
    assert bh["a"]["rank"] == 1 and bh["d"]["rank"] == 4


def test_benjamini_hochberg_handles_none():
    bh = benjamini_hochberg({"a": 0.01, "b": None}, q=0.10)
    assert bh["a"]["survives_fdr"] is True and bh["b"]["survives_fdr"] is None


def test_cluster_bootstrap_runs_and_brackets_point():
    # two strata, two PSUs each; a clean positive relationship
    rows = []
    for stra in (1, 2):
        for psu in (1, 2):
            for k in range(15):
                xv = float(k + 10 * psu)
                rows.append({"x": xv, "y": 0.4 * xv, "sdmvstra": stra, "sdmvpsu": psu})

    def stat(rs):
        return weighted_ols_exposure_coef([r["y"] for r in rs], [r["x"] for r in rs], [],
                                          [1.0] * len(rs))

    res = cluster_bootstrap(rows, stat, iters=200, seed=1)
    assert res["lo"] is not None and res["lo"] <= res["estimate"] <= res["hi"]
    assert res["estimate"] > 0.9                # standardized slope of a perfect line ≈ 1


def test_analyze_weighted_end_to_end():
    rows = []
    for stra in (1, 2, 3):
        for psu in (1, 2):
            for k in range(30):
                xv = float(k)
                rows.append({"exp": xv, "out": -0.3 * xv + 0.01 * k, "conf": float(k % 5),
                             "weight": 1.0 + (psu == 1), "sdmvstra": stra, "sdmvpsu": psu})
    rep = analyze_weighted(rows, "exp", ["out"], ["conf"])
    r = rep["outcomes"]["out"]
    assert r["weighted_std_coef"] < 0                      # negative relationship recovered
    assert "unweighted_std_coef" in r and "fdr" in r
    assert r["design_ci_90"]["lo"] is not None


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
