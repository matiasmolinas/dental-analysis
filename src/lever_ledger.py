# write-time guardrail is a VALIDATED invariant (W2); cross-session transfer *value* is UNTESTED — see docs/RESEARCH_SUMMARY.md §4b #3
"""Cross-session memory: the lever ledger (Phase R6, next-step #3).

The Session Working-Consciousness is per-session and amnesiac across sessions. This is the persistent
piece: a committed ledger of *which format/variable/harness lever surfaced which mediator*, keyed by a
STRUCTURAL case signature — so a new case can start from levers that worked before, instead of
relitigating them. Plus an offline CONSOLIDATION pass (SkillOpt-Sleep-style) that promotes stable
beliefs and prunes noise, behind the guardrail.

HARD non-diagnostic rule (enforced at write time): the ledger stores ONLY structural signatures and
format/variable/processing lessons — NEVER a patient-specific numeric value. `case_signature` is
bands/booleans/field-names only. See docs/analysis/session-consciousness-memory-sleep.md §2.
"""

from __future__ import annotations

import json
import os
from typing import Any

CORROBORATION = {"counterfactual_flip", "ab_on_claude", "repeated_turns"}
SURFACES = {"work_prompt", "skill", "kb_context", "injected_variables", "subagent_def", "harness_code"}


def case_signature(record: dict) -> dict:
    """A STRUCTURAL signature — bands, a comorbidity set, and which mediating data are flagged absent.
    No numeric patient values (guardrail: never store an imputable value)."""
    perio = record.get("periodontal", {})
    shared = record.get("shared_risk", {})
    med = record.get("medical_cv", {})
    bop = perio.get("bop_pct")
    stage = perio.get("diagnosis", "")
    comorbid = sorted(k for k, v in {
        "diabetes": shared.get("type2_diabetes"), "smoking": shared.get("smoking_active"),
        "hypertension": shared.get("hypertension")}.items() if v)
    absent = sorted(f for f in ("hs_crp", "il6") if med.get(f) is None and f not in perio)
    return {
        "perio_stage": stage.split(",")[0].strip() if stage else "unknown",
        "bop_band": ("high" if (bop or 0) >= 30 else "moderate" if (bop or 0) >= 10 else "low"),
        "comorbidities": comorbid,          # names only
        "absent_mediators": absent,         # field names only
    }


_ALLOWED_KEYS = {"case_signature", "surface", "lever", "mediator_moved", "corroboration",
                 "confidence", "guardrail_pass", "provenance"}


def validate_lever(rec: dict) -> None:
    """Raise if the record is malformed OR would leak a patient value / break the guardrail."""
    missing = {"case_signature", "surface", "lever", "corroboration", "guardrail_pass"} - set(rec)
    if missing:
        raise ValueError(f"lever record missing {missing}")
    if rec["surface"] not in SURFACES:
        raise ValueError(f"unknown surface {rec['surface']!r}")
    if rec["corroboration"] not in CORROBORATION:
        raise ValueError(f"unknown corroboration {rec['corroboration']!r}")
    if rec["guardrail_pass"] is not True:
        raise ValueError("guardrail_pass must be True to persist a lever")
    # No numeric patient values anywhere (the ledger stores lessons, not data).
    def _no_numbers(v, path=""):
        if isinstance(v, bool):
            return
        if isinstance(v, (int, float)):
            raise ValueError(f"numeric value at {path} — the ledger must never store patient values")
        if isinstance(v, dict):
            for k, x in v.items():
                _no_numbers(x, f"{path}.{k}")
        elif isinstance(v, list):
            for i, x in enumerate(v):
                _no_numbers(x, f"{path}[{i}]")
    _no_numbers({k: rec[k] for k in rec if k != "confidence"})  # confidence is a model float, allowed


def write_lever(path: str, rec: dict) -> None:
    """Append one validated lever record (JSONL). Rejects guardrail-failing / value-leaking records."""
    validate_lever(rec)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def read_levers(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _sig_key(sig: dict) -> tuple:
    return (sig.get("perio_stage"), sig.get("bop_band"),
            tuple(sig.get("comorbidities", [])), tuple(sig.get("absent_mediators", [])))


def suggest_levers(path: str, sig: dict) -> list[dict]:
    """Levers previously seen for a matching (or comorbidity-overlapping) case signature, ranked by
    how well the signature matches and by confidence. Memory PROPOSES; the guardrail disposes at use."""
    out = []
    for rec in read_levers(path):
        rs = rec["case_signature"]
        exact = _sig_key(rs) == _sig_key(sig)
        overlap = len(set(rs.get("comorbidities", [])) & set(sig.get("comorbidities", [])))
        if exact or overlap:
            out.append({**rec, "_match": "exact" if exact else "partial", "_overlap": overlap})
    out.sort(key=lambda r: (r["_match"] == "exact", r["_overlap"], r.get("confidence", 0)), reverse=True)
    return out


def consolidate(path: str, min_support: int = 2) -> list[dict]:
    """Offline pass: group levers by (signature, surface, lever); promote a BELIEF when it has
    >= min_support corroborated occurrences OR a counterfactual/ab corroboration. Returns the
    consolidated beliefs (stable lessons); noise (singletons w/o strong corroboration) is dropped."""
    groups: dict[tuple, list[dict]] = {}
    for rec in read_levers(path):
        key = (_sig_key(rec["case_signature"]), rec["surface"], rec["lever"])
        groups.setdefault(key, []).append(rec)
    beliefs = []
    for (sig, surface, lever), recs in groups.items():
        strong = any(r["corroboration"] in ("counterfactual_flip", "ab_on_claude") for r in recs)
        if len(recs) >= min_support or strong:
            beliefs.append({
                "case_signature": recs[0]["case_signature"], "surface": surface, "lever": lever,
                "support": len(recs), "corroboration": sorted({r["corroboration"] for r in recs}),
                "confidence": round(sum(r.get("confidence", 0.5) for r in recs) / len(recs), 3),
                "mediator_moved": sorted({r.get("mediator_moved", "") for r in recs if r.get("mediator_moved")}),
            })
    beliefs.sort(key=lambda b: (b["support"], b["confidence"]), reverse=True)
    return beliefs
