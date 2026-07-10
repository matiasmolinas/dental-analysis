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


# --------------------------------------------------------------------------- subtle variants
# v1 (the injectors above) were BLATANT — a blind "any problems?" read caught all four (ceiling
# effect, no headroom to test the monitor). These v2 variants corrupt in ways a blind skim
# plausibly MISSES: a confidence one notch too high (not high-with-empty-evidence), a 1-notch
# (not 2-notch) confidence gap on comparable axes, a plausibly-phrased second-order claim, and
# the omission of a NON-critical datum. See docs/analysis/qa-monitor-live-result.md.

_CONF_ORDER = ["low", "medium", "high"]


def _bump(conf: str) -> str:
    i = _CONF_ORDER.index(conf) if conf in _CONF_ORDER else 1
    return _CONF_ORDER[min(i + 1, len(_CONF_ORDER) - 1)]


def _evidence_count(ax: dict) -> int:
    return len(ax.get("oral_evidence", [])) + len(ax.get("systemic_evidence", []))


def subtle_overconfidence(output: dict, record: dict) -> tuple[dict, dict] | None:
    """Raise ONE axis's confidence a single notch (low→medium / medium→high) without adding any
    evidence — a plausibility a blind skim misses. Picks the thinnest-evidence non-high axis."""
    axes = output.get("relational_axes", [])
    cand = sorted(((i, a) for i, a in enumerate(axes) if a.get("confidence") in ("low", "medium")),
                  key=lambda ia: (_evidence_count(ia[1]), ia[0]))
    if not cand:
        return None
    idx, ax = cand[0]
    out = copy.deepcopy(output)
    old = ax.get("confidence")
    out["relational_axes"][idx]["confidence"] = _bump(old)
    return out, {
        "defect_type": "subtle_overconfidence",
        "locus": f"relational_axes[{idx}].axis={ax.get('axis')}",
        "description": (f"axis '{ax.get('axis')}' confidence was raised one level "
                        f"({old}→{_bump(old)}) beyond what its (unchanged, thin) evidence supports"),
    }


def subtle_inconsistent_confidence(output: dict, record: dict) -> tuple[dict, dict] | None:
    """A 1-notch confidence gap between two axes with COMPARABLE (not identical) evidence — the
    non-redundant class, made subtle. Needs >= 2 axes whose evidence counts are within 1."""
    axes = output.get("relational_axes", [])
    if len(axes) < 2:
        return None
    # find the closest-evidence pair (subtle: comparable, not forced-identical)
    pair = min(((i, j) for i in range(len(axes)) for j in range(i + 1, len(axes))),
               key=lambda ij: abs(_evidence_count(axes[ij[0]]) - _evidence_count(axes[ij[1]])),
               default=None)
    if pair is None or abs(_evidence_count(axes[pair[0]]) - _evidence_count(axes[pair[1]])) > 1:
        return None
    i, j = pair
    out = copy.deepcopy(output)
    a_hi, a_lo = out["relational_axes"][i], out["relational_axes"][j]
    a_hi["confidence"], a_lo["confidence"] = "high", "medium"  # 1-notch gap, evidence untouched
    return out, {
        "defect_type": "subtle_inconsistent_confidence",
        "locus": f"relational_axes[{i}]={a_hi.get('axis')} vs [{j}]={a_lo.get('axis')}",
        "description": (f"axes '{a_hi.get('axis')}' and '{a_lo.get('axis')}' have comparable "
                        "evidence but were given a confidence gap (high vs medium)"),
    }


def subtle_unsupported_claim(output: dict, record: dict) -> tuple[dict, dict] | None:
    """Append a plausibly-phrased SECOND-ORDER claim to a mechanism — a mediator asserted with no
    supporting evidence/traceability, worded like routine hedged mechanistic prose."""
    axes = output.get("relational_axes", [])
    if not axes:
        return None
    out = copy.deepcopy(output)
    ax = out["relational_axes"][0]
    ax["hypothesized_mechanism"] = (ax.get("hypothesized_mechanism", "").rstrip().rstrip(".")
                                    + "; oxidative stress likely amplifies this pathway.")
    return out, {
        "defect_type": "subtle_unsupported_claim",
        "locus": "relational_axes[0].hypothesized_mechanism",
        "description": ("mechanism appends a second-order mediator (oxidative stress) asserted "
                        "without any supporting evidence or traceability"),
    }


def subtle_silent_omission(output: dict, record: dict) -> tuple[dict, dict] | None:
    """Drop a NON-critical required_missing_data entry (impact optional/important preferred) —
    a low-salience omission a blind skim overlooks. Falls back to the last entry."""
    rmd = output.get("required_missing_data", [])
    if not rmd:
        return None
    order = {"optional": 0, "important": 1, "critical": 2}
    idx = min(range(len(rmd)), key=lambda k: (order.get(rmd[k].get("impact", "important"), 1), -k))
    if rmd[idx].get("impact") == "critical" and len(rmd) == 1:
        return None  # only a critical one exists -> that's not a subtle omission
    out = copy.deepcopy(output)
    dropped = out["required_missing_data"].pop(idx)
    return out, {
        "defect_type": "subtle_silent_omission",
        "locus": "required_missing_data",
        "description": (f"a non-critical missing datum '{dropped.get('field')}' "
                        f"(impact={dropped.get('impact')}) was silently dropped from the flags"),
    }


INJECTORS = {
    "internal_contradiction": inject_internal_contradiction,
    "inconsistent_confidence": inject_inconsistent_confidence,
    "unsupported_claim": inject_unsupported_claim,
    "silent_omission": inject_silent_omission,
}

SUBTLE_INJECTORS = {
    "subtle_overconfidence": subtle_overconfidence,
    "subtle_inconsistent_confidence": subtle_inconsistent_confidence,
    "subtle_unsupported_claim": subtle_unsupported_claim,
    "subtle_silent_omission": subtle_silent_omission,
}


def inject_all(output: dict, record: dict, mode: str = "blatant") -> list[dict[str, Any]]:
    """Every applicable injector applied independently to the clean output. `mode='blatant'`
    uses the v1 set; `mode='subtle'` uses the v2 set (defects a blind read plausibly misses).
    Returns [{defect_type, corrupted_output, label}]; non-applicable injectors are skipped."""
    injectors = SUBTLE_INJECTORS if mode == "subtle" else INJECTORS
    rows = []
    for name, fn in injectors.items():
        res = fn(output, record)
        if res is not None:
            corrupted, label = res
            rows.append({"defect_type": name, "corrupted_output": corrupted, "label": label})
    return rows
