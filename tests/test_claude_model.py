"""Tests for the Claude soft-model estimator — pure/offline (a stub model_fn, no network).

Verifies prompt shape, the parse+guardrail (a hypothesis MUST ship a falsification path), the member
conversion (tier `claude`, weight-capped), and that a blended coded+claude edge keeps the claude
member down-weighted and visible.

Run:  python tests/test_claude_model.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.claude_model import build_prompt, estimate_edge, parse_estimate, to_member
from histora.ensemble import blend_members
from histora.registry import CLAUDE_MEMBER_WEIGHT_CAP

EDGE = {
    "name": "oral_gut_brain",
    "description": "periodontal pathogens → gut dysbiosis → systemic LPS → neuroinflammation",
    "stratum": {"bop_band": "high", "perio_stage": "stage III", "comorbidities": ["diabetes"]},
    "gain": 0.57,
}

GOOD = json.dumps({
    "edge": "oral→gut→brain",
    "direction": "increase",
    "relative_effect_band": [1.05, 1.4],
    "point": 1.2,
    "confidence": "medium",
    "rationale": "LPS translocation is plausible but human evidence is indirect.",
    "falsification": "no rise in serum LPS-binding protein after periodontal therapy would refute it",
    "recommended_technique": "compartmental_ode",
})


def test_prompt_carries_stratum_and_gain_no_values():
    prompt = build_prompt(EDGE)
    assert "oral_gut_brain" in prompt and "stage III" in prompt and "0.57" in prompt
    # structural only — no raw patient measurements leak in
    assert "mg/dL" not in prompt and "patient" not in prompt.lower()


def test_parse_and_member_capped():
    est = parse_estimate(GOOD)
    assert est["direction"] == "increase" and est["band"] == [1.05, 1.4]
    m = to_member(est, "oral_gut_brain")
    assert m["tier"] == "claude"
    assert m["weight"] <= CLAUDE_MEMBER_WEIGHT_CAP
    assert m["falsification"]


def test_missing_falsification_rejected():
    bad = json.dumps({"direction": "increase", "point": 1.2, "confidence": "high"})
    try:
        parse_estimate(bad)
        assert False, "should reject an estimate with no falsification path"
    except ValueError:
        pass


def test_estimate_edge_offline_with_stub():
    m = estimate_edge(EDGE, model_fn=lambda _p: GOOD)
    assert m["tier"] == "claude" and m["value"] == 1.2


def test_blend_keeps_claude_downweighted():
    coded = {"value": 1.0, "weight": 1.0, "source": "coded_spine", "tier": "coded"}
    claude = estimate_edge(EDGE, model_fn=lambda _p: GOOD)
    out = blend_members([coded, claude])
    # coded member dominates; claude is present and tier-labeled
    claude_row = next(s for s in out["sources"] if s["tier"] == "claude")
    coded_row = next(s for s in out["sources"] if s["tier"] == "coded")
    assert coded_row["weight"] > claude_row["weight"]
    assert out["value"] < 1.2   # pulled toward the coded 1.0, not the claude 1.2


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
