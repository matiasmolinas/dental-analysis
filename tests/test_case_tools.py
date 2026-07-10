"""Tests for the harness-as-a-tool (the plugin's model backend) — pure python, no API.

Verifies case_stratum reads structural bands only (no patient values), and case_mechanistic_predictions
returns the systemic/CV/neuro blocks + ranges + counterfactuals + guardrail, monotone in severity.

Run:  python tests/test_case_tools.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.case_tools import case_mechanistic_predictions, case_stratum
from histora.record_formats import RECORD


def test_case_stratum_is_structural_only():
    s = case_stratum(RECORD)
    assert set(s) == {"bop_band", "perio_stage", "comorbidities"}
    # no numeric patient value leaks into the stratum
    def _no_num(v):
        assert not isinstance(v, (int, float)) or isinstance(v, bool)
        if isinstance(v, dict): [_no_num(x) for x in v.values()]
        if isinstance(v, list): [_no_num(x) for x in v]
    _no_num(s)


def test_predictions_shape_and_guardrail():
    r = case_mechanistic_predictions(RECORD, n_ensemble=40)
    for k in ("structural_stratum", "systemic", "cardiovascular", "neuro", "counterfactuals",
              "ranges_over_uncertainty", "dominant_uncertainty", "flags", "guardrail"):
        assert k in r
    assert r["systemic"]["crp_mg_l"] > 0
    assert "non-diagnostic" in r["guardrail"]
    assert any("atuzaginstat" in f for f in r["flags"])
    # dominant uncertainty is correctly attributed
    assert r["dominant_uncertainty"]["crp_mg_l"] == "epsilon"
    assert r["dominant_uncertainty"]["tau_burden_rel_increase"] == "beta_tau"


def test_predictions_monotone_in_severity():
    low = case_mechanistic_predictions(
        {"periodontal": {"bop_pct": 5}, "shared_risk": {}, "medical_cv": {}}, n_ensemble=40)
    high = case_mechanistic_predictions(
        {"periodontal": {"bop_pct": 45, "diagnosis": "stage IV"},
         "shared_risk": {"type2_diabetes": True, "smoking_active": True}, "medical_cv": {}},
        n_ensemble=40)
    assert high["systemic"]["crp_mg_l"] > low["systemic"]["crp_mg_l"]
    assert high["neuro"]["tau_burden_relative_increase"] > low["neuro"]["tau_burden_relative_increase"]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
