"""Tests for the agentic-AI metrics + citation registry — pure/offline, on synthetic ledgers.

Run:  python tests/test_agent_metrics.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.agent_metrics import (
    Claim,
    calibration_honesty,
    citation_accuracy,
    falsifiability,
    hallucination_rate,
    metric_card,
    uncertainty_coverage,
)
from histora.citations import resolve, supports


def test_citation_registry_resolve_and_supports():
    assert resolve("delta_crp_anchor") is not None
    assert resolve("does_not_exist") is None
    assert supports("delta_crp_anchor", 0.5) is True          # matches value
    assert supports("delta_crp_anchor", 5.0) is False         # value mismatch
    assert supports("does_not_exist", 0.5) is False           # dangling key
    assert supports("protein_il6") is True                    # entity, no value asserted


def test_citation_accuracy():
    claims = [
        Claim("a", 0.5, "citation", source_key="delta_crp_anchor"),   # valid + value ok
        Claim("b", 99.0, "citation", source_key="delta_crp_anchor"),  # value mismatch → fail
        Claim("c", 1.0, "citation", source_key="ghost"),              # dangling → fail
        Claim("d", None, "engine"),                                   # not a citation → ignored
    ]
    assert citation_accuracy(claims) == round(1 / 3, 3)
    assert citation_accuracy([Claim("x", None, "engine")]) is None    # no citations at all


def test_hallucination_rate():
    claims = [
        Claim("engine num", 3.0, "engine"),                           # traceable
        Claim("cited num", 0.5, "citation", source_key="delta_crp_anchor"),  # traceable
        Claim("hypothesis num", 1.2, "hypothesis", falsification="x"),  # traceable
        Claim("made up", 7.7, "none"),                                # HALLUCINATION
        Claim("qualitative", None, "none"),                           # non-numeric → ignored
    ]
    assert hallucination_rate(claims) == round(1 / 4, 3)


def test_falsifiability():
    claims = [
        Claim("h1", None, "hypothesis", falsification="a refutation"),
        Claim("h2", None, "hypothesis", falsification=""),            # missing → fail
        Claim("not a hyp", 1.0, "engine"),
    ]
    assert falsifiability(claims) == 0.5
    assert falsifiability([Claim("e", 1.0, "engine")]) is None


def test_uncertainty_coverage():
    env = {"a": {"lo": 0.4, "hi": 0.6}, "b": {"lo": None, "hi": None}}
    anchors = {"a": 0.5, "b": 0.35}
    assert uncertainty_coverage(env, anchors) == 0.5                  # a covered, b (point) not
    assert uncertainty_coverage({"a": {"lo": None, "hi": None}}, {"a": 0.5}) == 0.0


def test_calibration_honesty():
    sens_good = {"crp_mg_l": {"epsilon": 1.0, "gamma_cv": 0.0}}
    sens_bad = {"crp_mg_l": {"epsilon": 0.1, "gamma_cv": 0.9}}
    assert calibration_honesty(sens_good) is True
    assert calibration_honesty(sens_bad) is False


def test_metric_card_shape():
    card = metric_card("H", [Claim("c", 0.5, "citation", source_key="delta_crp_anchor")],
                       envelopes={"delta_crp_mg_l": {"lo": 0.3, "hi": 0.7}},
                       anchors={"delta_crp_mg_l": 0.5}, guardrail_pass=1.0)
    assert card["citation_accuracy"] == 1.0 and card["uncertainty_coverage"] == 1.0
    assert card["guardrail_pass"] == 1.0 and card["n_numeric_claims"] == 1


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
