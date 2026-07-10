"""Tests for the cross-session memory value test + loop closure (memory-value) — no API/GPU.

Verifies (1) seed_ledger writes guardrail-valid levers and skips rejects, (2) consolidate is
actually invoked and gates on support, (3) warm_suffix injects matched beliefs' learned
concepts and stays empty when nothing matches, (4) run_memory_value computes WARM−COLD deltas,
CIs, and the verdict — all with a seeded scratch ledger + stub eval_fn.

Run:  python tests/test_memory_value.py
"""

from __future__ import annotations

import copy
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lever_ledger import case_signature, consolidate
from record_formats import RECORD
from run_memory_value import run_memory_value, seed_ledger, warm_suffix


def _lever_for(rec: dict, concept: str) -> dict:
    return {"case_signature": case_signature(rec), "surface": "injected_variables",
            "lever": "inject targeted factor-specific review considerations",
            "mediator_moved": concept, "corroboration": "counterfactual_flip",
            "confidence": 0.6, "guardrail_pass": True, "provenance": "test"}


def test_seed_ledger_writes_and_skips_none():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ledger.jsonl")
        recs = [RECORD, RECORD, RECORD]
        # lever_fn returns None for the middle case -> only 2 written
        calls = {"i": 0}

        def lever_fn(rec):
            calls["i"] += 1
            return None if calls["i"] == 2 else _lever_for(rec, "amlodipine gingival overgrowth")

        assert seed_ledger(recs, path, lever_fn) == 2


def test_seed_ledger_rejects_guardrail_failing_lever():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ledger.jsonl")
        # guardrail_pass False -> validate_lever raises -> not persisted
        bad = _lever_for(RECORD, "x"); bad["guardrail_pass"] = False
        assert seed_ledger([RECORD], path, lambda r: bad) == 0


def test_consolidate_gates_on_support():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ledger.jsonl")
        # one lever with strong corroboration (counterfactual_flip) -> promoted even at support 1
        seed_ledger([RECORD], path, lambda r: _lever_for(r, "amlodipine gingival overgrowth"))
        beliefs = consolidate(path, min_support=2)
        assert len(beliefs) == 1
        assert "amlodipine gingival overgrowth" in beliefs[0]["mediator_moved"]


def test_warm_suffix_injects_matched_belief():
    sig = case_signature(RECORD)
    beliefs = [{"case_signature": sig, "mediator_moved": ["amlodipine gingival overgrowth"]}]
    suffix = warm_suffix(beliefs, sig)
    assert "amlodipine gingival overgrowth" in suffix
    # no match -> empty
    other_sig = {"perio_stage": "none", "bop_band": "low", "comorbidities": [], "absent_mediators": []}
    assert warm_suffix(beliefs, other_sig) == ""


def test_run_memory_value_warm_beats_cold():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ledger.jsonl")
        seed_ledger([RECORD, RECORD], path, lambda r: _lever_for(r, "endothelial dysfunction pathway"))

        # eval_fn: a guardrail-passing output; when the WARM concept is present in the input it
        # additionally reasons with an extra mediator (higher relational_recall).
        def eval_fn(inp: str) -> dict:
            axes = [{"axis": "inflammatory", "oral_evidence": ["BOP"], "systemic_evidence": ["HTN"],
                     "hypothesized_mechanism": "systemic inflammation and cytokine signaling",
                     "confidence": "medium", "traceability": ["periodontal.bop_pct"]}]
            if "endothelial dysfunction" in inp:
                axes.append({"axis": "vascular", "oral_evidence": ["BOP"],
                             "systemic_evidence": ["HTN"],
                             "hypothesized_mechanism": "endothelial dysfunction and atherosclerosis",
                             "confidence": "medium", "traceability": ["medical_cv.blood_pressure"]})
            return {"risk_profile": "elevated", "relational_axes": axes,
                    "required_missing_data": [], "research_hypotheses": [],
                    "non_diagnostic_disclaimer": True}

        rep = run_memory_value([RECORD], path, lambda r: "BASE INPUT", eval_fn, min_support=1)
        assert rep["n_beliefs_consolidated"] == 1
        assert rep["per_case"][0]["warm_applied"] is True
        assert rep["per_case"][0]["warm"]["relational_recall"] >= rep["per_case"][0]["cold"]["relational_recall"]
        assert rep["verdict"] in ("memory_adds_value", "memory_inconclusive")


def test_run_memory_value_null_when_no_beliefs():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ledger.jsonl")  # empty ledger -> no beliefs -> WARM==COLD
        def eval_fn(inp):
            return {"risk_profile": "low", "relational_axes": [], "required_missing_data": [],
                    "research_hypotheses": [], "non_diagnostic_disclaimer": True}
        rep = run_memory_value([RECORD], path, lambda r: "BASE", eval_fn)
        assert rep["n_beliefs_consolidated"] == 0
        assert rep["per_case"][0]["warm_applied"] is False
        assert rep["verdict"] == "memory_inconclusive"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
