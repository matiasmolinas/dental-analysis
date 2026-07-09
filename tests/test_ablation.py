"""Tests for the three-arm lens ablation logic (Phase R6) — no API, no network, no GPU.

Verifies spec construction and the run_ablation verdict logic (lens_adds_value /
lens_neutral) with deterministic stub functions standing in for the four Claude calls.

Run:  python tests/test_ablation.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ablation import run_ablation, spec_text
from record_formats import RECORD  # medical_cv.hs_crp is None; il6 absent -> both missing

# --- canned evaluator outputs (output_schema.json-shaped) -----------------------

def _axis(mech):
    return {
        "axis": "inflammatory",
        "oral_evidence": ["BOP 62%"],
        "systemic_evidence": ["HbA1c 8.1"],
        "hypothesized_mechanism": mech,
        "confidence": "medium",
        "traceability": ["periodontal.bop_pct", "shared_risk.hba1c"],
    }

_MECH = ("inflammation raises C-reactive protein and cytokines, driving endothelial "
         "dysfunction, atherosclerosis, bacteremia, oxidative stress and cardiovascular risk")

WEAK_A = {  # names no mediators, flags nothing, guardrail fails
    "risk_profile": "moderate",
    "relational_axes": [{**_axis("both are risk factors"), "axis": "shared_behavioral"}],
    "required_missing_data": [],
    "research_hypotheses": [],
    "non_diagnostic_disclaimer": True,
}
BLIND_OUT = {  # names mediators, flags ONLY hs_crp (1/2) -> guardrail fails
    "risk_profile": "elevated",
    "relational_axes": [_axis(_MECH)],
    "required_missing_data": [{"field": "hs_crp", "why": "inflammatory mediator", "impact": "critical"}],
    "research_hypotheses": [],
    "non_diagnostic_disclaimer": True,
}
LENS_OUT = {  # names mediators, flags BOTH hs_crp + il6 (2/2) -> guardrail passes
    "risk_profile": "elevated",
    "relational_axes": [_axis(_MECH)],
    "required_missing_data": [
        {"field": "hs_crp", "why": "inflammatory mediator", "impact": "critical"},
        {"field": "il6", "why": "cytokine mediator", "impact": "important"},
    ],
    "research_hypotheses": [],
    "non_diagnostic_disclaimer": True,
}

# stub fns: converge returns a marker; eval maps marker -> canned output
_readout = lambda naive: "READOUT"
_observer = lambda naive, readout, spec: "DEFMAP"


def _make_eval(blind_out, lens_out):
    def eval_fn(inp):
        if inp == "LENS_INPUT":
            return lens_out
        if inp == "BLIND_INPUT":
            return blind_out
        return WEAK_A  # the naive input
    return eval_fn


def _converge(record, diagnosis):
    return "LENS_INPUT" if diagnosis is not None else "BLIND_INPUT"


def test_spec_text_lists_mediators_and_missing():
    s = spec_text(RECORD)
    assert "systemic_inflammation" in s and "hs_crp" in s and "il6" in s


def test_lens_adds_value_when_it_beats_blind():
    rep = run_ablation([RECORD], _readout, _observer, _converge, _make_eval(BLIND_OUT, LENS_OUT))
    agg = rep["aggregate"]
    assert agg["B_blind"]["guardrail_pass_rate"] == 0.0     # blind flags only 1/2 -> fails
    assert agg["B_lens"]["guardrail_pass_rate"] == 1.0      # lens flags 2/2 -> passes
    assert rep["deltas"]["B_lens_minus_B_blind"]["guardrail_pass_rate"] == 1.0
    assert rep["verdict"] == "lens_adds_value"


def test_lens_neutral_when_blind_is_as_good():
    # blind and lens produce the same (good) output -> lens earns nothing
    rep = run_ablation([RECORD], _readout, _observer, _converge, _make_eval(LENS_OUT, LENS_OUT))
    assert rep["aggregate"]["B_blind"]["guardrail_pass_rate"] == 1.0
    assert rep["verdict"] == "lens_neutral"


def test_report_shape():
    rep = run_ablation([RECORD], _readout, _observer, _converge, _make_eval(BLIND_OUT, LENS_OUT))
    assert set(rep["per_case"][0]) == {"case", "A", "B_blind", "B_lens"}
    assert "B_blind_minus_A" in rep["deltas"]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
