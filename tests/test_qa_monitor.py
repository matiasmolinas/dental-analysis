"""Tests for the QA-monitor detector + injection eval (Path A) — no API, no GPU.

Verifies (1) the deterministic injectors produce the labeled corruption, (2) detect() plumbs
the monitor payload, (3) caught() reflects the match judge, (4) evaluate() computes recall,
the paired CI, control FP rates, and the verdict — all with stubs.

Run:  python tests/test_qa_monitor.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from inject_defects import (
    inject_all,
    inject_inconsistent_confidence,
    inject_internal_contradiction,
    inject_silent_omission,
    inject_unsupported_claim,
)
from qa_monitor import caught, detect, evaluate


def _clean_output() -> dict:
    return {
        "risk_profile": "elevated",
        "relational_axes": [
            {"axis": "inflammatory", "oral_evidence": ["BOP 42%"],
             "systemic_evidence": ["hypertension"], "hypothesized_mechanism": "systemic inflammation",
             "confidence": "medium", "traceability": ["periodontal.bop_pct"]},
            {"axis": "metabolic", "oral_evidence": ["deep pockets"],
             "systemic_evidence": ["HbA1c 7.1"], "hypothesized_mechanism": "glycemic dysregulation",
             "confidence": "medium", "traceability": ["shared_risk.hba1c"]},
        ],
        "required_missing_data": [
            {"field": "hs_crp", "why": "CRP is the key inflammatory mediator", "impact": "critical"},
            {"field": "il6", "why": "cytokine mediator", "impact": "important"},
        ],
        "research_hypotheses": ["perio severity tracks CV risk"],
        "non_diagnostic_disclaimer": True,
    }


def test_internal_contradiction_injects_label():
    out, label = inject_internal_contradiction(_clean_output(), {})
    assert out["relational_axes"][0]["confidence"] == "high"
    assert out["relational_axes"][0]["oral_evidence"] == []
    assert label["defect_type"] == "internal_contradiction"


def test_inconsistent_confidence_equalizes_evidence():
    out, label = inject_inconsistent_confidence(_clean_output(), {})
    a0, a1 = out["relational_axes"][0], out["relational_axes"][1]
    assert a0["oral_evidence"] == a1["oral_evidence"]
    assert {a0["confidence"], a1["confidence"]} == {"high", "low"}
    assert label["defect_type"] == "inconsistent_confidence"


def test_unsupported_claim_names_missing_field():
    out, label = inject_unsupported_claim(_clean_output(), {})
    assert "hs_crp" in out["relational_axes"][0]["hypothesized_mechanism"]
    assert label["defect_type"] == "unsupported_claim"


def test_silent_omission_drops_a_flag():
    clean = _clean_output()
    out, label = inject_silent_omission(clean, {})
    assert len(out["required_missing_data"]) == len(clean["required_missing_data"]) - 1
    assert label["defect_type"] == "silent_omission"


def test_inject_all_skips_when_not_applicable():
    # only one axis + no missing data -> inconsistent_confidence and silent_omission skip
    thin = {"relational_axes": [{"axis": "inflammatory", "oral_evidence": ["x"],
            "systemic_evidence": ["y"], "hypothesized_mechanism": "m", "confidence": "low",
            "traceability": ["f"]}], "required_missing_data": [],
            "research_hypotheses": [], "non_diagnostic_disclaimer": True, "risk_profile": "low"}
    types = {r["defect_type"] for r in inject_all(thin, {})}
    assert "internal_contradiction" in types
    assert "inconsistent_confidence" not in types and "silent_omission" not in types


def test_detect_and_caught_plumbing():
    seen = {}

    def monitor_fn(user):
        seen["user"] = user
        return {"items": [{"key": "d1", "defect_type": "internal_contradiction", "why": "w"}]}

    dets = detect(monitor_fn, "CASE X", {"risk_profile": "low"})
    assert dets and "CASE X" in seen["user"]
    assert caught(lambda _u: {"matched": True}, dets, {"defect_type": "internal_contradiction"})
    assert not caught(lambda _u: {"matched": False}, dets, {"defect_type": "x"})
    assert not caught(lambda _u: {"matched": True}, [], {"defect_type": "x"})  # empty never matches


def test_evaluate_monitor_beats_blind():
    injected = [{"input": "i", "output": {"corrupt": True}, "label": {"defect_type": t}}
                for t in ("internal_contradiction", "inconsistent_confidence",
                          "unsupported_claim", "silent_omission")]
    controls = [{"input": "i", "output": {"clean": True}} for _ in range(4)]
    # monitor flags only corrupt outputs (no control FPs); blind catches nothing
    rep = evaluate(
        injected, controls,
        monitor_detect=lambda i, o: [{"key": "m"}] if o.get("corrupt") else [],
        blind_detect=lambda i, o: [],
        judge_caught=lambda dets, label: bool(dets) and dets[0].get("key") == "m",
    )
    assert rep["monitor_recall"] == 1.0 and rep["blind_recall"] == 0.0
    assert rep["ci_90_monitor_minus_blind"]["lo"] > 0
    assert rep["control_fp_rate"]["monitor"] == 0.0
    assert rep["verdict"] == "monitor_adds_detection_value"


def test_evaluate_inconclusive_when_tied():
    injected = [{"input": "i", "output": {}, "label": {"defect_type": "internal_contradiction"}}
                for _ in range(4)]
    controls = [{"input": "i", "output": {}}]
    rep = evaluate(
        injected, controls,
        monitor_detect=lambda i, o: [{"key": "m"}],
        blind_detect=lambda i, o: [{"key": "m"}],
        judge_caught=lambda dets, label: True,  # both always catch -> delta 0
    )
    assert rep["recall_delta_mean"] == 0.0
    assert rep["verdict"] == "monitor_inconclusive"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
