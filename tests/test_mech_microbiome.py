"""Tests for the reduced oral-microbiome model (Stage-3, Phase C) — pure python.

Verifies the Allee/quorum threshold (mild load resists, severe load becomes dysbiotic), graded
dysbiosis, the bounded source multiplier, and the non-diagnostic framing.

Run:  python tests/test_mech_microbiome.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.mech_microbiome import (
    dysbiosis_index,
    microbiome_centerpiece,
    source_dysbiosis_multiplier,
)


def test_allee_threshold_health_resists():
    mild = dysbiosis_index({"bop_band": "low"})
    assert mild["crossed_allee_quorum"] is False
    assert mild["dysbiosis_index"] == 0.0          # below quorum → pathogen dies out


def test_severe_is_dysbiotic_and_graded():
    mod = dysbiosis_index({"bop_band": "moderate"})
    sev = dysbiosis_index({"bop_band": "high", "perio_stage": "stage IV",
                           "comorbidities": ["diabetes"]})
    assert mod["crossed_allee_quorum"] is True
    assert 0.0 < mod["dysbiosis_index"] <= sev["dysbiosis_index"] <= 1.0


def test_source_multiplier_bounded_and_monotone():
    m_low = source_dysbiosis_multiplier({"bop_band": "low"})
    m_high = source_dysbiosis_multiplier({"bop_band": "high", "perio_stage": "stage III"})
    assert m_low == 1.0
    assert 1.0 < m_high <= 1.5 + 1e-9


def test_names_keystone_and_non_diagnostic():
    c = microbiome_centerpiece({"bop_band": "high"})
    assert c["keystone_pathogen"] == "Porphyromonas gingivalis"
    assert c["confidence"] == "exploratory"
    assert any("non-diagnostic" in f for f in c["flags"])


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
