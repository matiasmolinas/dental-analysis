"""Tests for SkillOpt — the gated evolutionary loop over trainable skills. Pure/offline, stubs.

Locks in the safety-critical behavior: the guardrail is a HARD gate (a fitness gain never overrides it),
adoption needs a real fitness win (CI excludes 0), the prose arm classifies execution- vs knowledge-gap,
the guardrail hash is identical parent↔child (invariant untouched), PROTECTED skills can't be evolved,
and the archive keeps both adopted AND rejected entries (auditable, no cherry-picking).

Run:  python tests/test_skill_evolution.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.skill_evolution import (
    append_archive,
    evolve_generation,
    load_archive,
    propose_mutation,
    skill_hash,
)

RECORDS = [{"id": i} for i in range(6)]
GUARDRAIL_TEXT = "PROTECTED non-diagnostic guardrail — never evolved"


def _render(skill, rec):
    return skill                                   # the skill text IS the model input, in this stub world


def _eval(inp):
    # a candidate with the integrated marker scores high; the prose control (parent + a note) does not
    return {"quality": 1.0 if "<<GOOD>>" in inp else 0.3, "safe": "<<UNSAFE>>" not in inp}


def _fitness(out, rec):
    return out["quality"]


def _guardrail(out, rec):
    return out["safe"]


def _gen(candidate, summary="cite the input fields", parent="parent skill body", archive=None):
    return evolve_generation("traceability-audit", parent, candidate, summary, RECORDS,
                             _render, _eval, _fitness, _guardrail, GUARDRAIL_TEXT, archive_path=archive)


def test_adopts_a_real_safe_improvement():
    e = _gen("candidate body <<GOOD>>")
    assert e["adopted"] is True
    assert e["guardrail_pass_rate"] == 1.0
    assert e["helps"] is True and e["pattern"] == "execution_gap"     # beats parent AND the prose control
    assert e["fitness_means"]["enforced"] > e["fitness_means"]["base"]


def test_guardrail_is_a_hard_gate_even_with_a_fitness_gain():
    # candidate improves fitness (<<GOOD>>) but breaks the guardrail (<<UNSAFE>>) → MUST be rejected
    e = _gen("candidate body <<GOOD>> <<UNSAFE>>")
    assert e["adopted"] is False
    assert e["guardrail_pass_rate"] == 0.0
    assert "guardrail" in e["reason"]


def test_rejects_when_no_fitness_gain():
    e = _gen("candidate body with no marker")            # same quality as parent → CI includes 0
    assert e["adopted"] is False and e["helps"] is False
    assert "no fitness gain" in e["reason"]


def test_guardrail_hash_identical_parent_and_child():
    e = _gen("candidate body <<GOOD>>")
    assert e["guardrail_hash"] == skill_hash(GUARDRAIL_TEXT)          # the invariant was never touched
    assert e["parent_hash"] != e["child_hash"]


def test_protected_skill_cannot_be_evolved():
    raised = False
    try:
        evolve_generation("non-diagnostic-guardrail", "p", "c <<GOOD>>", "s", RECORDS,
                          _render, _eval, _fitness, _guardrail, GUARDRAIL_TEXT)
    except ValueError:
        raised = True
    assert raised


def test_propose_mutation_parses():
    stub = json.dumps({"candidate_skill": "edited body", "change_summary": "added field-level citation"})
    m = propose_mutation("parent body", "trace: axis omitted field cite", lambda _s, _u: stub)
    assert m["candidate_skill"] == "edited body" and "citation" in m["change_summary"]


def test_archive_keeps_adopted_and_rejected(tmp="/tmp/histora_skillopt_test.jsonl"):
    if os.path.exists(tmp):
        os.remove(tmp)
    _gen("candidate body <<GOOD>>", archive=tmp)                     # adopted
    _gen("candidate body <<GOOD>> <<UNSAFE>>", archive=tmp)          # rejected (guardrail)
    arch = load_archive(tmp)
    assert len(arch) == 2
    assert any(a["adopted"] for a in arch) and any(not a["adopted"] for a in arch)
    # every entry proves the invariant hash is unchanged
    assert all(a["guardrail_hash"] == skill_hash(GUARDRAIL_TEXT) for a in arch)
    os.remove(tmp)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
