"""Tests for the cohort builder — funnel, completeness, protocol, integrity checklist. Pure/offline.

The records below are a small IN-MEMORY UNIT-TEST FIXTURE (not a demo dataset and never shown as a finding);
they exercise the filtering + reporting logic that, in the demo, runs over the real NHANES corpus.

Run:  python tests/test_cohort.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.cohort import (build_funnel, cohort_completeness, integrity_checklist, preliminary_protocol)

# fixture: 5 synthetic records — 2 fully eligible (perio + diabetes + CRP), the rest fail a stage.
FIXTURE = [
    {"seqn": 1, "perio_cal": 3.5, "perio_ppd": 2.0, "hba1c": 7.1, "hs_crp": 4.2},   # eligible
    {"seqn": 2, "perio_cal": 4.0, "perio_ppd": 5.0, "hba1c": 6.8, "hs_crp": 2.1},   # eligible
    {"seqn": 3, "perio_cal": 3.2, "perio_ppd": 2.0, "hba1c": 7.5, "hs_crp": None},  # no CRP
    {"seqn": 4, "perio_cal": 1.0, "perio_ppd": 1.5, "hba1c": 8.0, "hs_crp": 3.0},   # no periodontitis
    {"seqn": 5, "perio_cal": 3.6, "perio_ppd": 2.0, "hba1c": 5.4, "hs_crp": 1.5},   # no diabetes
]


def test_funnel_is_cumulative_with_real_counts():
    f = build_funnel(FIXTURE)
    stages = {s["stage"]: s["n"] for s in f["funnel"]}
    assert f["funnel"][0]["n"] == 5                      # total
    assert stages["+ hs-CRP measured"] == 2              # only seqn 1 & 2 survive all stages
    assert f["cohort_n"] == 2 and sorted(f["cohort_seqns"]) == [1, 2]
    # monotonic non-increasing
    ns = [s["n"] for s in f["funnel"]]
    assert all(ns[i] >= ns[i + 1] for i in range(len(ns) - 1))


def test_completeness_flags_the_cross_sectional_gap():
    f = build_funnel(FIXTURE)
    c = cohort_completeness(f["cohort"])
    assert c["field_present_fraction"]["hs-CRP (baseline)"] == 1.0
    # the honest 'cannot answer' longitudinal fields are always reported as absent from a corpus
    assert any("repeat hs-CRP" in x for x in c["longitudinal_fields_absent_in_corpus"])
    assert "cannot be answered by this corpus" in c["verdict"]
    assert c["non_diagnostic"] is True


def test_protocol_prepares_but_does_not_conclude():
    f = build_funnel(FIXTURE)
    c = cohort_completeness(f["cohort"])
    p = preliminary_protocol("Q?", f, c)
    assert "NOT a study" in p["header"] and p["non_diagnostic"] is True
    assert p["cohort_size"] == 2 and p["limitations"]          # limitations block is non-empty
    assert any("causal" in lim.lower() for lim in p["limitations"])


def test_integrity_checklist_denies_causality_diagnosis_therapy():
    f = build_funnel(FIXTURE)
    chk = {c["label"]: c["ok"] for c in integrity_checklist(f, cohort_completeness(f["cohort"]))}
    assert chk["Enough data to define a cohort"] is True
    assert chk["Establishes causality"] is False
    assert chk["Provides a diagnosis"] is False
    assert chk["Recommends a therapy"] is False


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
