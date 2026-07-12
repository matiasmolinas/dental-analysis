"""Tests for the multi-cytokine inflammatory core (Stage-3, Phase A) — pure python.

Verifies the acute-vs-chronic distinction the single scalar cannot make: a resolving low-load regime,
a chronic high-load regime, a bistable window, the chronicity grading, the bounded amplifier, and the
therapy counterfactual.

Run:  python tests/test_mech_inflammation.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.mech_inflammation import (
    bistability_report,
    chronic_amplifier,
    chronicity,
    inflammation_centerpiece,
    inflammation_params,
    resolution_index,
)

MILD = {"bop_band": "low"}
SEVERE = {"bop_band": "high", "perio_stage": "stage III"}


def test_mild_resolves_severe_chronic():
    mild = inflammation_centerpiece(MILD)
    severe = inflammation_centerpiece(SEVERE)
    assert mild["regime"] == "resolving"
    assert severe["regime"] == "chronic"
    assert severe["chronicity"] > mild["chronicity"]


def test_chronicity_monotone_and_bounded():
    loads = [chronicity(x) for x in (0.0, 0.3, 0.8, 1.3, 2.0)]
    assert loads[0] == 0.0
    assert loads == sorted(loads)                 # monotone non-decreasing in load
    assert all(0.0 <= c <= 1.0 for c in loads)


def test_amplifier_bounded_and_rises_with_severity():
    a_mild = chronic_amplifier(MILD)
    a_sev = chronic_amplifier(SEVERE)
    assert a_mild == 1.0                          # resolving → no boost
    assert 1.0 < a_sev <= 1.0 + 0.4 + 1e-9        # chronic → bounded boost


def test_bistable_window_exists():
    # a small/moderate source should admit two coexisting stable states (history-dependent)
    rep = bistability_report(0.5)
    assert rep["bistable"] is True
    assert rep["low_stable"] and rep["high_stable"]
    assert rep["high_fixed_point"]["il6"] > rep["low_fixed_point"]["il6"]


def test_resolution_index_and_therapy_counterfactual():
    c = inflammation_centerpiece(SEVERE)
    # chronic state: pro-inflammatory signalling outweighs the IL-10 brake
    assert c["resolution_index"] < 1.0
    # therapy (load→0) returns the system to the resolving basin
    assert c["counterfactual_therapy"]["resolves"] is True
    assert any("non-diagnostic" in f for f in c["flags"])


def test_non_diagnostic_numeric_values_ignored():
    a = inflammation_centerpiece({"bop_band": "high", "comorbidities": ["diabetes"]})["chronicity"]
    b = inflammation_centerpiece({"bop_band": "high", "comorbidities": ["diabetes"],
                                  "bop_pct": 47, "hba1c": 8.1})["chronicity"]
    assert a == b


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
