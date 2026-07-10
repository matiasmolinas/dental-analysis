"""Tests for the cross-session lever ledger (Phase R6 #3) — no API, no GPU.

Covers the structural signature (no values leak), write-time guardrail enforcement (reject
patient values / guardrail-failing records), suggestion matching, and the offline consolidation
pass. Run:  python tests/test_lever_ledger.py
"""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lever_ledger import (
    case_signature, consolidate, read_levers, suggest_levers, validate_lever, write_lever,
)
from record_formats import RECORD


def test_case_signature_is_structural_no_values():
    sig = case_signature(RECORD)
    assert sig["bop_band"] == "high" and "diabetes" in sig["comorbidities"]
    assert "hs_crp" in sig["absent_mediators"]
    # no numeric values anywhere in the signature
    def _no_num(v):
        assert not isinstance(v, (int, float)) or isinstance(v, bool)
        if isinstance(v, dict): [ _no_num(x) for x in v.values() ]
        if isinstance(v, list): [ _no_num(x) for x in v ]
    _no_num(sig)


def _rec(**over):
    base = {"case_signature": case_signature(RECORD), "surface": "injected_variables",
            "lever": "inject hs_crp=MISSING", "mediator_moved": "c_reactive_protein",
            "corroboration": "counterfactual_flip", "confidence": 0.8, "guardrail_pass": True}
    base.update(over)
    return base


def test_validate_rejects_guardrail_fail_and_values():
    validate_lever(_rec())  # ok
    try: validate_lever(_rec(guardrail_pass=False))
    except ValueError: pass
    else: raise AssertionError("should reject guardrail_pass=False")
    # a numeric field is rejected:
    bad = _rec(); bad["case_signature"] = {**bad["case_signature"], "hs_crp_value": 4.2}
    try: validate_lever(bad)
    except ValueError: pass
    else: raise AssertionError("should reject a numeric patient value")


def test_validate_rejects_measurement_number_in_string():
    # the guardrail hole: a patient-ish number embedded in free text must be rejected
    for leak in ("vasoconstriction — true 62", "BOP 42%", "hs-CRP 7.1 mg/L", "PPD 5.5"):
        try: validate_lever(_rec(mediator_moved=leak))
        except ValueError: pass
        else: raise AssertionError(f"should reject measurement number in {leak!r}")
    # but legitimate single-digit classifiers / mediator names survive
    for ok in ("IL-6 signaling", "type 2 diabetes", "endothelial dysfunction", "omega-3 pathway"):
        validate_lever(_rec(mediator_moved=ok))


def test_write_read_suggest_and_consolidate():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "lever_ledger.jsonl")
        write_lever(path, _rec(provenance="s1"))
        write_lever(path, _rec(provenance="s2"))                       # same lever, 2 supports
        write_lever(path, _rec(surface="kb_context", lever="add CRP bridge",
                               corroboration="repeated_turns", provenance="s3"))
        assert len(read_levers(path)) == 3
        sugg = suggest_levers(path, case_signature(RECORD))
        assert sugg and sugg[0]["_match"] == "exact"
        beliefs = consolidate(path, min_support=2)
        # the injected-variables lever (2 supports + counterfactual) is a belief; the kb one
        # (1 support, repeated_turns only) is NOT promoted
        levers = {b["lever"] for b in beliefs}
        assert "inject hs_crp=MISSING" in levers and "add CRP bridge" not in levers


def test_write_rejects_bad_record():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "l.jsonl")
        try: write_lever(path, _rec(guardrail_pass=False))
        except ValueError: pass
        else: raise AssertionError("write should reject guardrail-failing record")
        assert not os.path.exists(path) or read_levers(path) == []


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn(); print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
