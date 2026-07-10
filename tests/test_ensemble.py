"""Tests for the ensemble / UQ driver (A2) — pure python, no API/GPU.

Verifies the Latin-hypercube sampler, that predict_case runs the full chain, that the envelope
brackets the nominal prediction, monotonicity of the median across severity strata, and the
sensitivity ranking. Uses a small n for speed.

Run:  python tests/test_ensemble.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.ensemble import ensemble_report, latin_hypercube, predict_case, sensitivity_ranking
from histora.ensemble import _base_params
from histora.registry import OUTPUTS, SWEPT_PARAMS


def test_latin_hypercube_covers_and_bounded():
    bounds = {"a": (0.0, 1.0), "b": (10.0, 20.0)}
    s = latin_hypercube(bounds, 50, seed=1)
    assert len(s) == 50
    assert all(0.0 <= x["a"] <= 1.0 and 10.0 <= x["b"] <= 20.0 for x in s)
    # LHS stratifies: each of the 50 a-cuts is occupied once -> good spread
    lows = sum(1 for x in s if x["a"] < 0.5)
    assert 20 <= lows <= 30            # ~half below the midpoint (stratified, not clumped)


def test_predict_case_returns_all_outputs():
    p = _base_params()
    pred = predict_case({"bop_band": "high", "comorbidities": []}, p)
    assert set(pred) == set(OUTPUTS)
    assert pred["crp_mg_l"] > 0 and pred["tau_burden_rel_increase"] >= 0


def test_envelope_brackets_nominal():
    r = ensemble_report({"bop_band": "high", "comorbidities": []}, n=60, seed=0)
    for o in OUTPUTS:
        env, nom = r["envelope"][o], r["nominal"][o]
        assert env["lo"] <= env["median"] <= env["hi"]
        # the nominal prediction lies within the swept envelope (± a rounding tolerance)
        assert env["lo"] - 1e-6 <= nom <= env["hi"] + 1e-6


def test_median_crp_monotone_in_severity():
    lo = ensemble_report({"bop_band": "low", "comorbidities": []}, n=60)["envelope"]["crp_mg_l"]["median"]
    hi = ensemble_report({"bop_band": "high", "comorbidities": ["diabetes", "smoking"],
                          "perio_stage": "stage IV"}, n=60)["envelope"]["crp_mg_l"]["median"]
    assert hi > lo


def test_sensitivity_ranking_shape_and_signs():
    r = sensitivity_ranking({"bop_band": "high", "comorbidities": []}, _base_params())
    assert set(r) == set(OUTPUTS)
    # CRP responds to ε (spillover), not to the neuro coupling beta_tau
    assert abs(r["crp_mg_l"]["epsilon"]) > abs(r["crp_mg_l"].get("beta_tau", 0.0))
    # tau burden responds to beta_tau (its coupling)
    assert r["tau_burden_rel_increase"]["beta_tau"] > 0
    assert set(SWEPT_PARAMS).issuperset(r["crp_mg_l"].keys())



def test_blend_members_caps_claude_and_shows_provenance():
    from histora.ensemble import blend_members
    # a coded member (weight 1) and a Claude soft-model member (weight 1 → capped to 0.3)
    out = blend_members([
        {"value": 1.0, "weight": 1.0, "source": "coded_cv", "tier": "flagged"},
        {"value": 5.0, "weight": 1.0, "source": "claude_estimate", "tier": "claude"},
    ])
    # capped claude weight 0.3 vs coded 1.0 → blend closer to the coded value than a naive mean (3.0)
    assert out["value"] < 3.0
    assert out["band"] == [1.0, 5.0]                         # structural-uncertainty spread visible
    claude = next(s for s in out["sources"] if s["tier"] == "claude")
    assert claude["weight"] < 0.31                            # capped and shown, never hidden
    assert blend_members([])["value"] is None


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
