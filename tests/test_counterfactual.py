"""Tests for the counterfactual-sensitivity runner (Phase R6 v2) — no API, no GPU.

Verifies factor flipping, the axis-confidence readout, and that a SENSITIVE input builder
(output tracks the factor) scores higher than an INSENSITIVE one (output ignores the flip).

Run:  python tests/test_counterfactual.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from counterfactual import FACTORS, axis_conf, counterfactual_report, flip, sensitivity
from record_formats import RECORD


def _axis(axis, conf):
    return {"axis": axis, "oral_evidence": ["x"], "systemic_evidence": ["y"],
            "hypothesized_mechanism": "m", "confidence": conf, "traceability": ["f"]}


def test_flip_removes_factor():
    r = flip(RECORD, "type2_diabetes")
    assert r["shared_risk"]["type2_diabetes"] is False and "hba1c" not in r["shared_risk"]
    # original untouched
    assert RECORD["shared_risk"]["type2_diabetes"] is True


def test_axis_conf():
    out = {"relational_axes": [_axis("metabolic", "high"), _axis("vascular", "low")]}
    assert axis_conf(out, "metabolic") == 3 and axis_conf(out, "vascular") == 1
    assert axis_conf(out, "inflammatory") == 0


def test_sensitive_vs_insensitive_builder():
    # sensitive: metabolic axis strong WITH diabetes, gone WITHOUT it; others unchanged
    def sensitive_eval(inp):
        has_diabetes = '"type2_diabetes": true' in inp.lower()
        axes = [_axis("shared_behavioral", "medium")]
        if has_diabetes:
            axes.append(_axis("metabolic", "high"))
        return {"relational_axes": axes}

    def insensitive_eval(inp):  # ignores the flip entirely
        return {"relational_axes": [_axis("metabolic", "high"),
                                    _axis("shared_behavioral", "medium")]}

    import json
    build = lambda rec: json.dumps(rec)  # noqa: E731 - input carries the factor value

    s = sensitivity(RECORD, "type2_diabetes", build, sensitive_eval)
    assert s["sensitive"] is True and s["affected_delta"] == 3

    ins = sensitivity(RECORD, "type2_diabetes", build, insensitive_eval)
    assert ins["sensitive"] is False and ins["affected_delta"] == 0


def test_report_aggregates():
    import json
    build = lambda rec: json.dumps(rec)  # noqa: E731
    rep = counterfactual_report([RECORD], build, lambda inp: {"relational_axes": []},
                                factors=list(FACTORS))
    assert rep["n_flips"] == len(FACTORS) and rep["sensitivity_rate"] == 0.0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
