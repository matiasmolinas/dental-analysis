"""Tests for the NHANES schema mapping, incl. the neuro (perio+cognition) axis — no network.

Verifies both mappings are well-formed and the neuro files list is derived correctly. Does NOT
download anything (offline).

Run:  python tests/test_nhanes_mapping.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nhanes_mapping import (
    NHANES_FILES,
    NHANES_NEURO_FILES,
    SCHEMA_TO_NHANES,
    SCHEMA_TO_NHANES_NEURO,
)


def _well_formed(mapping):
    for path, (fname, codes, note) in mapping.items():
        assert isinstance(path, str) and "." in path
        assert isinstance(fname, str) and fname
        assert isinstance(codes, tuple) and codes and all(isinstance(c, str) for c in codes)
        assert isinstance(note, str) and note


def test_cv_mapping_well_formed():
    _well_formed(SCHEMA_TO_NHANES)
    assert "OMP_2009-2012" not in NHANES_FILES     # microbiome hosted separately, excluded from XPT


def test_neuro_mapping_has_cognition_and_perio_in_same_cycle():
    _well_formed(SCHEMA_TO_NHANES_NEURO)
    # cognition battery present
    for k in ("cognition.cerad_word_learning", "cognition.cerad_delayed_recall",
              "cognition.animal_fluency", "cognition.digit_symbol"):
        assert k in SCHEMA_TO_NHANES_NEURO
    # cognition (CFQ_G) and periodontal (OHXPER_G) come from the SAME 2011-2012 cycle
    assert SCHEMA_TO_NHANES_NEURO["cognition.digit_symbol"][0] == "CFQ_G"
    assert SCHEMA_TO_NHANES_NEURO["periodontal.cal_mm_2011"][0] == "OHXPER_G"


def test_neuro_files_derived_and_no_crp():
    assert "CFQ_G" in NHANES_NEURO_FILES and "OHXPER_G" in NHANES_NEURO_FILES
    # honest caveat encoded structurally: no CRP file in the cognition cycle (discontinued after 2010)
    assert not any(f.startswith("CRP") or f.startswith("HSCRP") for f in NHANES_NEURO_FILES)
    # confounders present (age + education are the dominant perio/cognition confounders)
    assert "DEMO_G" in NHANES_NEURO_FILES


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
