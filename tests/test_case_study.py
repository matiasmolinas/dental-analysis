"""Tests for the flagship case study — the composed research line. Pure/offline.

Locks in the honesty invariants Fable's red-lines require: the research line pulls the REAL engine numbers
(no re-derivation), it is non-diagnostic, it ships refutation conditions and a named shakiest assumption,
and the named drug (tocilizumab) is framed as a causal-node anchor — never as a treatment/prescription.

Run:  python tests/test_case_study.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "demo"))

from run_case_study import research_line
from run_demo import build_brief

CASE = json.load(open(os.path.join(os.path.dirname(__file__), "..", "demo", "case.json")))


def _line():
    return research_line(build_brief(CASE, live=False))


def test_research_line_uses_the_real_engine_numbers():
    brief = build_brief(CASE, live=False)
    line = research_line(brief)
    # the predicted ΔCRP is the engine's own therapy counterfactual, not a fresh/hardcoded number
    assert line["lever"]["predicted_delta_crp_mg_l"] == \
        brief["engine"]["counterfactuals"]["periodontal_therapy"]["delta_crp_mg_l"]
    crp = brief["engine"]["ranges_over_uncertainty"]["crp_mg_l"]
    assert line["lever"]["predicted_crp_range_mg_l"] == [crp["lo"], crp["hi"]]


def test_lever_is_non_pharmacological_periodontal_therapy():
    line = _line()
    assert "periodontal therapy" in line["lever"]["intervention"].lower()
    assert "non-pharmacolog" in line["lever"]["intervention"].lower()


def test_drug_is_a_node_anchor_never_a_treatment():
    line = _line()
    proof = line["causal_node"]["pharmacological_proof_of_node"].lower()
    assert "tocilizumab" in proof
    assert "never as a proposed treatment" in proof
    # the generated hypothesis explicitly disclaims being a therapy
    assert "not a therapy" in line["causal_node"]["the_hypothesis"].lower()


def test_ships_refutation_and_shakiest_assumption_and_is_non_diagnostic():
    line = _line()
    assert len(line["what_would_refute_it"]) >= 3
    assert line["shakiest_assumption"].strip()
    assert line["non_diagnostic"] is True
    # the nulls / exploratory tiering stay visible in the honest-scope statement
    assert "exploratory" in line["honest_scope"].lower()
    assert "≠" in line["honest_scope"] or "!=" in line["honest_scope"]  # MR != RCT; calibration != validation


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
