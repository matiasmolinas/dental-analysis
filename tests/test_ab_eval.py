"""Tests for the A/B evaluation harness (Phase R5).

Proves the scoring + promotion logic with a deterministic stub model — a naive A output
(lists numbers, misses the mediators, imputes/omits the missing datum) vs a converged B
output (reasons through the mediators, flags hs-CRP for collection, full traceability).
No live model calls; pure-python, no GPU.

Run:  python -m pytest tests/ -q   (or)   python tests/test_ab_eval.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ab_eval import (
    build_inputs,
    guardrail_pass,
    mechanism_recall,
    missing_data_flagged,
    run_ab,
    score,
)
from record_formats import RECORD

# --- canned outputs (output_schema.json-shaped) ---------------------------------

NAIVE_A_OUTPUT = {  # side-by-side listing: no mediators, hs-CRP not flagged
    "risk_profile": "moderate",
    "relational_axes": [
        {
            "axis": "shared_behavioral",
            "oral_evidence": ["BOP 62%"],
            "systemic_evidence": ["smoker 20py"],
            "hypothesized_mechanism": "both are risk factors",
            "confidence": "low",
            "traceability": ["periodontal.bop_pct", "shared_risk.smoking_pack_years"],
        }
    ],
    "required_missing_data": [],
    "research_hypotheses": ["diabetes and smoking co-occur"],
    "non_diagnostic_disclaimer": True,
}

CONVERGED_B_OUTPUT = {  # relates via mediators; flags hs-CRP; traceable
    "risk_profile": "elevated",
    "relational_axes": [
        {
            "axis": "inflammatory",
            "oral_evidence": ["BOP 62%", "periodontitis stage III"],
            "systemic_evidence": ["HbA1c 8.1"],
            "hypothesized_mechanism": (
                "periodontal inflammation raises systemic inflammatory burden "
                "(C-reactive protein, cytokines), promoting endothelial dysfunction "
                "and atherosclerosis"
            ),
            "confidence": "medium",
            "traceability": ["periodontal.bop_pct", "shared_risk.hba1c"],
        },
        {
            "axis": "vascular",
            "oral_evidence": ["bacteremia risk from perio pockets"],
            "systemic_evidence": ["hypertension 140/90"],
            "hypothesized_mechanism": "bacteremia and oxidative stress raise cardiovascular risk",
            "confidence": "low",
            "traceability": ["periodontal.mean_ppd_mm", "shared_risk.hypertension"],
        },
    ],
    "required_missing_data": [
        {"field": "hs_crp", "why": "inflammatory mediator", "impact": "critical"},
        {"field": "il6", "why": "cytokine mediator", "impact": "important"},
    ],
    "research_hypotheses": ["oxidative stress may mediate the oral-systemic link"],
    "non_diagnostic_disclaimer": True,
}


def _stub_model(prompt: str) -> dict:
    """Return the naive output for input A, the converged output for input B."""
    inputs = build_inputs(RECORD)
    return CONVERGED_B_OUTPUT if prompt == inputs["B"] else NAIVE_A_OUTPUT


# --- tests ----------------------------------------------------------------------

def test_build_inputs_B_injects_signals_and_kb():
    inp = build_inputs(RECORD)
    assert "hs_crp" in inp["B"] and "MISSING" in inp["B"]      # missing-mediator flag
    assert "bop_inflammatory_load" in inp["B"]                 # deterministic signal
    assert "C-reactive protein" in inp["B"]                    # mechanistic KB
    assert "MISSING" not in inp["A"] and "Knowledge base" not in inp["A"]


def test_mechanism_recall_discriminates():
    assert mechanism_recall(NAIVE_A_OUTPUT)[0] == 0            # names no mediators
    assert mechanism_recall(CONVERGED_B_OUTPUT)[0] >= 5        # names most mediators


def test_missing_data_flagging():
    assert missing_data_flagged(NAIVE_A_OUTPUT, RECORD) == (0, 2)
    assert missing_data_flagged(CONVERGED_B_OUTPUT, RECORD) == (2, 2)


def test_guardrail_pass_requires_flagging_missing_mediators():
    # A omits the missing-data flags -> silently unacknowledged -> guardrail fails
    assert guardrail_pass(NAIVE_A_OUTPUT, RECORD) is False
    assert guardrail_pass(CONVERGED_B_OUTPUT, RECORD) is True


def test_run_ab_promotes_B():
    report = run_ab([RECORD], _stub_model)
    agg = report["aggregate"]
    assert agg["B"]["mechanism_recall"] > agg["A"]["mechanism_recall"]
    assert agg["B"]["guardrail_pass_rate"] == 1.0
    assert report["verdict"] == "promote_B"


def test_score_shape():
    s = score(CONVERGED_B_OUTPUT, RECORD)
    assert set(s) >= {"mechanism_recall", "missing_data_flagged", "guardrail_pass",
                      "traceability_ok"}


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
