"""Tests for the perio↔cognition association engine (Track 2) — pure python, no deps, no network.

Verifies the pure-python OLS recovers a known slope, confounder adjustment removes a confounded
association, the bootstrap CI brackets the point estimate, and analyze() reports direction/
significance on synthetic data with a planted (adjusted) effect.

Run:  python tests/test_perio_cognition.py
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.perio_cognition import analyze
from histora.stats import ols_exposure_coef as _ols_exposure_coef, standardize as _standardize


def _lcg(seed):
    x = seed
    while True:
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        yield x / 0x7FFFFFFF  # deterministic uniform [0,1), no stdlib random needed


def test_standardize_zero_mean_unit_sd():
    z = _standardize([1.0, 2.0, 3.0, 4.0, 5.0])
    assert abs(sum(z)) < 1e-9
    assert abs(sum(v * v for v in z) / len(z) - 1.0) < 1e-9


def test_ols_recovers_pearson_r_with_no_confounders():
    # y = 2x + noise; standardized coef ≈ Pearson r (strong positive)
    rng = _lcg(1)
    x = [next(rng) for _ in range(200)]
    y = [2 * xi + 0.1 * (next(rng) - 0.5) for xi in x]
    r = _ols_exposure_coef(y, x, [])
    assert r > 0.9


def test_confounder_adjustment_removes_spurious_association():
    # age drives BOTH perio and cognition; perio has NO direct effect on cognition.
    rng = _lcg(7)
    age = [next(rng) for _ in range(400)]
    perio = [a + 0.05 * (next(rng) - 0.5) for a in age]          # perio tracks age
    cog = [-a + 0.05 * (next(rng) - 0.5) for a in age]           # cognition falls with age, not perio
    crude = _ols_exposure_coef(cog, perio, [])
    adjusted = _ols_exposure_coef(cog, perio, [age])
    assert crude < -0.8                    # strong spurious negative association crude
    assert abs(adjusted) < 0.2             # adjustment for age dissolves it


def test_analyze_reports_planted_adjusted_effect():
    # perio has a genuine adjusted negative effect on cognition, on top of an age confounder
    rng = _lcg(3)
    recs = []
    for _ in range(300):
        age = next(rng)
        perio = 0.5 * age + next(rng)
        cog = -0.6 * perio - 0.3 * age + 0.05 * (next(rng) - 0.5)
        recs.append({"perio_cal": perio, "cerad_delayed": cog, "age": age,
                     "education": next(rng), "smoking": 1.0 if next(rng) > 0.5 else 0.0,
                     "hba1c": 5 + next(rng)})
    out = analyze(recs, "perio_cal", ["cerad_delayed"], ["age", "education", "smoking", "hba1c"])
    r = out["outcomes"]["cerad_delayed"]
    assert r["adjusted_std_coef"] < 0                      # negative: worse cognition with more perio
    assert r["direction"] == "worse_cognition_with_more_perio"
    assert r["ci_90_adjusted"]["lo"] <= r["adjusted_std_coef"] <= r["ci_90_adjusted"]["hi"]
    assert r["significant"] is True                        # CI excludes 0 with a real planted effect


def test_analyze_flags_insufficient_rows():
    recs = [{"perio_cal": 1.0, "cerad_delayed": 2.0, "age": 3.0} for _ in range(5)]
    out = analyze(recs, "perio_cal", ["cerad_delayed"], ["age"])
    assert "insufficient" in out["outcomes"]["cerad_delayed"].get("note", "")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
