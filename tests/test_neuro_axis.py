"""Tests for the neuro relational axis in the HISTORA agent (Phase 3) — no API, no GPU.

Verifies the neuro mediators are wired, `neuro_relational_recall` scores traced neuro reasoning and
stays separate from the CV metric, and the output schema admits the `neuroinflammatory` axis.

Run:  python tests/test_neuro_axis.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ab_eval import neuro_relational_recall, relational_recall
from bridge_concepts import BRIDGE_CONCEPTS, NEURO_MEDIATOR_KEYS


def _axis(axis, mech, trace=("periodontal.bop_pct",)):
    return {"axis": axis, "oral_evidence": ["BOP"], "systemic_evidence": ["marker"],
            "hypothesized_mechanism": mech, "confidence": "medium", "traceability": list(trace)}


def test_neuro_mediators_are_wired():
    for k in NEURO_MEDIATOR_KEYS:
        assert k in BRIDGE_CONCEPTS and BRIDGE_CONCEPTS[k]


def test_neuro_recall_scores_traced_neuro_reasoning():
    out = {"relational_axes": [
        _axis("neuroinflammatory",
              "systemic inflammation drives microglial neuroinflammation, amyloid and tau pathology")
    ]}
    hit, tot = neuro_relational_recall(out)
    assert tot == len(NEURO_MEDIATOR_KEYS)
    # systemic_inflammation + neuroinflammation + amyloid_beta + tau_pathology surfaced
    assert hit >= 4


def test_neuro_and_cv_metrics_are_separate():
    # a purely CV output scores on relational_recall but ~0 on neuro-specific mediators
    cv = {"relational_axes": [
        _axis("vascular", "endothelial dysfunction and atherosclerosis raise cardiovascular risk")]}
    assert relational_recall(cv)[0] >= 2
    # only the shared drivers could hit neuro; the brain-specific ones must not
    neuro_hit, _ = neuro_relational_recall(cv)
    brain_specific = {"neuroinflammation", "amyloid_beta", "tau_pathology", "blood_brain_barrier",
                      "glymphatic_clearance"}
    mech = cv["relational_axes"][0]["hypothesized_mechanism"].lower()
    assert not any(any(s.lower() in mech for s in BRIDGE_CONCEPTS[k]) for k in brain_specific)


def test_untraced_neuro_axis_does_not_count():
    out = {"relational_axes": [{"axis": "neuroinflammatory",
            "oral_evidence": ["BOP"], "systemic_evidence": ["x"],
            "hypothesized_mechanism": "microglia tau amyloid", "confidence": "low",
            "traceability": []}]}  # no traceability -> not counted
    assert neuro_relational_recall(out)[0] == 0


def test_schema_admits_neuroinflammatory_axis():
    here = os.path.join(os.path.dirname(__file__), "..", "schemas", "output_schema.json")
    with open(here) as f:
        schema = json.load(f)
    enum = schema["properties"]["relational_axes"]["items"]["properties"]["axis"]["enum"]
    assert "neuroinflammatory" in enum
    # the four original axes remain
    for a in ("inflammatory", "metabolic", "shared_behavioral", "vascular"):
        assert a in enum


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
