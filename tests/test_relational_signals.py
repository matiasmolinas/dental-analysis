"""Tests for the deterministic relational-signals harness (harness-evolution demo).

Verifies the structural bands, the progression delta, and — the load-bearing property
for the S4 loop — that an absent mediating datum becomes a MISSING collection flag and
is never imputed. Pure-python; runs without a GPU.

Run:  python -m pytest tests/ -q   (or)   python tests/test_relational_signals.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from record_formats import RECORD  # NHANES-grounded synthetic case (hs_crp is None)
from relational_signals import (
    derived_signals,
    inflammatory_load,
    metabolic_load,
    missing_mediators,
    perio_progression,
)


def test_inflammatory_load_bands():
    assert inflammatory_load({"bop_pct": 62})["band"] == "high"      # >= 30
    assert inflammatory_load({"bop_pct": 15})["band"] == "moderate"  # >= 10
    assert inflammatory_load({"bop_pct": 4})["band"] == "low"
    assert inflammatory_load({}) is None                             # absent -> no signal


def test_metabolic_load_bands():
    assert metabolic_load({"hba1c": 8.1})["band"] == "high"      # >= 6.5
    assert metabolic_load({"hba1c": 6.0})["band"] == "moderate"  # >= 5.7
    assert metabolic_load({"hba1c": 5.2})["band"] == "low"


def test_progression_delta():
    p = perio_progression({"mean_ppd_mm": 5.2, "ppd_18m_ago_mm": 4.1})
    assert p["delta_mm"] == 1.1 and p["direction"] == "worsening"
    assert perio_progression({"mean_ppd_mm": 5.2}) is None  # no prior -> no signal


def test_missing_mediator_is_flagged_never_imputed():
    flags = missing_mediators(RECORD)  # RECORD.medical_cv.hs_crp is None
    fields = {f["field"] for f in flags}
    assert "hs_crp" in fields
    for f in flags:
        assert f["status"] == "MISSING"
        assert "value" not in f  # collection flag, never a computed patient value


def test_derived_signals_bundle_is_non_diagnostic():
    out = derived_signals(RECORD)
    assert out["non_diagnostic"] is True
    assert {s["signal"] for s in out["structural_signals"]} == {
        "bop_inflammatory_load",
        "metabolic_load",
        "ppd_progression_mm",
    }
    # every structural signal cites its source fields (traceability)
    for s in out["structural_signals"]:
        assert s["from"] and all("." in f for f in s["from"])


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
