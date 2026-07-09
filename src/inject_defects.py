"""Deterministic, labeled defect injection for the QA-monitor eval (Path A).

Takes a clean, guardrail-passing output dict (schemas/output_schema.json shape) and injects
ONE labeled reasoning defect, returning (corrupted_output, label). Fully deterministic (no
randomness) so the eval is reproducible. Each injector returns None when the clean output
lacks the structure it needs (skipped, not faked).

The defect classes are chosen to be REASONING defects a second-model read could catch that a
schema check cannot — especially `inconsistent_confidence`, the by-construction non-redundant
class (the exact meta-critique the circularity gate surfaced): two axes with equal evidence
carrying contradictory confidence. Label shape: {defect_type, locus, description}.
"""

from __future__ import annotations

import copy
from typing import Any


def inject_internal_contradiction(output: dict, record: dict) -> tuple[dict, dict] | None:
    """An axis asserts HIGH confidence but lists no oral_evidence supporting the oral↔systemic
    link — confidence not backed by the evidence it cites."""
    axes = output.get("relational_axes", [])
    if not axes:
        return None
    out = copy.deepcopy(output)
    ax = out["relational_axes"][0]
    ax["confidence"] = "high"
    ax["oral_evidence"] = []
    return out, {
        "defect_type": "internal_contradiction",
        "locus": f"relational_axes[0].axis={ax.get('axis')}",
        "description": (f"axis '{ax.get('axis')}' asserts high confidence but lists no "
                        "oral_evidence supporting the oral–systemic link"),
    }


def inject_inconsistent_confidence(output: dict, record: dict) -> tuple[dict, dict] | None:
    """Two axes given IDENTICAL evidence but contradictory confidence (high vs low) — the
    non-redundant-by-construction class the gate surfaced. Needs >= 2 axes."""
    axes = output.get("relational_axes", [])
    if len(axes) < 2:
        return None
    out = copy.deepcopy(output)
    a0, a1 = out["relational_axes"][0], out["relational_axes"][1]
    ev = a0.get("oral_evidence") or a1.get("oral_evidence") or ["periodontal inflammation"]
    sys_ev = a0.get("systemic_evidence") or a1.get("systemic_evidence") or ["cardiovascular marker"]
    a0["oral_evidence"], a1["oral_evidence"] = list(ev), list(ev)
    a0["systemic_evidence"], a1["systemic_evidence"] = list(sys_ev), list(sys_ev)
    a0["confidence"], a1["confidence"] = "high", "low"
    return out, {
        "defect_type": "inconsistent_confidence",
        "locus": f"relational_axes[0]={a0.get('axis')} vs [1]={a1.get('axis')}",
        "description": (f"axes '{a0.get('axis')}' and '{a1.get('axis')}' carry identical "
                        "oral/systemic evidence yet contradictory confidence (high vs low)"),
    }


def inject_unsupported_claim(output: dict, record: dict) -> tuple[dict, dict] | None:
    """The mechanism asserts a specific role/value for a mediator the output ITSELF flags as
    missing/uncollected — a claim beyond the evidence."""
    axes = output.get("relational_axes", [])
    if not axes:
        return None
    missing = [m.get("field") for m in output.get("required_missing_data", []) if m.get("field")]
    field = missing[0] if missing else "hs_crp"
    out = copy.deepcopy(output)
    ax = out["relational_axes"][0]
    ax["hypothesized_mechanism"] = (ax.get("hypothesized_mechanism", "").rstrip()
                                    + f" Elevated {field} is the driving mediator in this case.")
    return out, {
        "defect_type": "unsupported_claim",
        "locus": f"relational_axes[0].hypothesized_mechanism",
        "description": (f"mechanism asserts a specific elevated value/role for '{field}', which "
                        "the output itself lists as missing/uncollected"),
    }


def inject_silent_omission(output: dict, record: dict) -> tuple[dict, dict] | None:
    """Delete one legitimately-present required_missing_data entry — a truly-absent datum
    silently dropped from the collection flags."""
    rmd = output.get("required_missing_data", [])
    if not rmd:
        return None
    out = copy.deepcopy(output)
    dropped = out["required_missing_data"].pop(0)
    return out, {
        "defect_type": "silent_omission",
        "locus": "required_missing_data",
        "description": (f"a truly-missing datum '{dropped.get('field')}' was dropped from "
                        "required_missing_data (silently omitted from the collection flags)"),
    }


INJECTORS = {
    "internal_contradiction": inject_internal_contradiction,
    "inconsistent_confidence": inject_inconsistent_confidence,
    "unsupported_claim": inject_unsupported_claim,
    "silent_omission": inject_silent_omission,
}


def inject_all(output: dict, record: dict) -> list[dict[str, Any]]:
    """Every applicable injector applied independently to the clean output. Returns a list of
    {defect_type, corrupted_output, label}; injectors that don't apply are skipped."""
    rows = []
    for name, fn in INJECTORS.items():
        res = fn(output, record)
        if res is not None:
            corrupted, label = res
            rows.append({"defect_type": name, "corrupted_output": corrupted, "label": label})
    return rows
