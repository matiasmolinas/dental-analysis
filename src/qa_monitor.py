"""Lens-as-MONITOR: a second-model QA read that flags reasoning defects in an output (Path A).

This reframes the one genuine lens-flavored positive from the whole arc — the gate's
meta-critique of the OUTPUT's own reasoning (content off the output plane the output can't
self-report) — into the paper's DEMONSTRATED use: detection/monitoring, not optimization. A
second model reads the executor's output (+optional trace) and flags reasoning
inconsistencies, unsupported claims, internal contradictions, silent omissions.

The experiment (run_qa_eval.py) measures whether this off-plane MONITOR read catches planted,
labeled defects a BLIND read ("does this output have any problems?") misses — headline =
monitor_recall − blind_recall on injected defects, at matched false-positive rate on clean
controls, with a bootstrap CI. A positive there is the project's first demonstrated payoff of
DETECTION (not optimization, and not the measured lens).

Model-agnostic: `detect(monitor_fn, ...)` and `evaluate(...)` take injected callables so the
plumbing is testable offline with stubs; run_qa_eval wires Opus (Fable refuses the medical
read) + a Sonnet match-judge.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from ablation import _bootstrap_ci

# --------------------------------------------------------------------------- prompts

# The MONITOR — off-plane read. It is told to look PAST what the output says and critique the
# reasoning behind it: the meta-critique channel that self-report surfaces and the output
# cannot report about itself.
MONITOR_SYSTEM = """You are a QA MONITOR for a non-diagnostic oral-systemic (periodontal +
cardiovascular) research output. You are given the case INPUT and the model's OUTPUT. Do NOT
re-solve the case and do NOT rewrite the output. Read PAST what the output says and audit the
REASONING behind it — the kind of flaw the output would not report about itself:

- reasoning_inconsistency: a confidence/claim not backed by the evidence the output itself cites
- internal_contradiction: two parts of the output that cannot both be right
- unsupported_claim: a specific assertion (a value, a driving mediator) beyond the cited evidence,
  or asserting a datum the output elsewhere flags as missing
- silent_omission: a mediating datum truly absent from the input that the output failed to flag
- inconsistent_confidence: axes with comparable evidence carrying contradictory confidence

Be precise and conservative: flag a defect only when you can point to the exact locus. A clean
output should yield an empty list. Return, via the tool, items = [{key: short_snake_case_id,
defect_type: one of the above, quote: the offending text/locus, severity: high|medium|low,
why: one clause}]."""

# The BLIND baseline — a generic problem-spotting read with NO off-plane / reasoning-audit
# framing. This is the control: whatever a plain "any problems?" read already catches is what
# the monitor must BEAT to have earned its keep.
BLIND_READ_SYSTEM = """You are reviewing a non-diagnostic oral-systemic research output. You are
given the case INPUT and the model's OUTPUT. Point out any problems you notice with the output.
Return, via the tool, items = [{key: short_snake_case_id, defect_type: short label,
quote: the offending text/locus, severity: high|medium|low, why: one clause}]."""

MONITOR_TOOL = {"type": "object", "properties": {"items": {"type": "array", "items": {
    "type": "object", "properties": {
        "key": {"type": "string"}, "defect_type": {"type": "string"},
        "quote": {"type": "string"}, "severity": {"type": "string"}, "why": {"type": "string"}},
    "required": ["key", "defect_type", "why"]}}}, "required": ["items"]}

# The match judge — did any detection semantically correspond to the ONE planted defect?
MATCH_JUDGE_SYSTEM = """You are given a GROUND-TRUTH defect that was deliberately injected into a
model output, and a list of DETECTIONS a reviewer produced. Decide whether ANY detection
correctly identifies the SAME underlying defect (same locus and same kind of problem —
paraphrase is fine, a different unrelated complaint does NOT count). Return, via the tool,
matched = true|false and matched_key = the key of the matching detection (or empty)."""

MATCH_JUDGE_TOOL = {"type": "object", "properties": {
    "matched": {"type": "boolean"}, "matched_key": {"type": "string"}},
    "required": ["matched"]}


# --------------------------------------------------------------------------- primitives

def detect(monitor_fn: Callable[[str], dict], case_input: str, output: dict) -> list[dict]:
    """Run a monitor/blind read over (input, output). `monitor_fn(user)->dict` returns the tool
    payload; we return its `items`."""
    user = ("CASE INPUT:\n" + case_input
            + "\n\nMODEL OUTPUT TO REVIEW:\n" + json.dumps(output, indent=2))
    return monitor_fn(user).get("items", [])


def caught(judge_fn: Callable[[str], dict], detections: list[dict], label: dict) -> bool:
    """Did the detections catch the labeled defect? `judge_fn(user)->dict` runs the match judge.
    Empty detections never match."""
    if not detections:
        return False
    user = ("GROUND-TRUTH INJECTED DEFECT:\n" + json.dumps(label, indent=2)
            + "\n\nDETECTIONS:\n" + json.dumps(detections, indent=2))
    return bool(judge_fn(user).get("matched", False))


# --------------------------------------------------------------------------- the eval

def evaluate(
    injected: list[dict],
    controls: list[dict],
    monitor_detect: Callable[[str, dict], list[dict]],
    blind_detect: Callable[[str, dict], list[dict]],
    judge_caught: Callable[[list[dict], dict], bool],
) -> dict[str, Any]:
    """Headline experiment. `injected` = [{input, output(corrupted), label}]; `controls` =
    [{input, output(clean)}]. Both arms run over every item; the judge decides catches on
    injected; raw flag counts on controls give the false-positive rate.

    Returns per-arm recall on injected defects, the paired monitor−blind delta with a bootstrap
    90% CI, and the control FP rate per arm. CONFIRMS value iff the delta CI excludes 0 at a low
    control FP rate; REFUTES if monitor ≈ blind or the monitor's control FP rate is high.
    """
    rows = []
    for it in injected:
        m = judge_caught(monitor_detect(it["input"], it["output"]), it["label"])
        b = judge_caught(blind_detect(it["input"], it["output"]), it["label"])
        rows.append({"defect_type": it["label"].get("defect_type"),
                     "monitor_caught": m, "blind_caught": b, "delta": int(m) - int(b)})

    control_rows = []
    for it in controls:
        m_flags = len(monitor_detect(it["input"], it["output"]))
        b_flags = len(blind_detect(it["input"], it["output"]))
        control_rows.append({"monitor_flags": m_flags, "blind_flags": b_flags,
                             "monitor_fp": m_flags > 0, "blind_fp": b_flags > 0})

    def _mean(xs):
        return round(sum(xs) / len(xs), 4) if xs else 0.0

    monitor_recall = _mean([r["monitor_caught"] for r in rows])
    blind_recall = _mean([r["blind_caught"] for r in rows])
    ci = _bootstrap_ci([r["delta"] for r in rows])

    # Per-defect-class recall (the inconsistent_confidence class is the non-redundant one).
    classes = sorted({r["defect_type"] for r in rows})
    by_class = {
        c: {"n": sum(r["defect_type"] == c for r in rows),
            "monitor_recall": _mean([r["monitor_caught"] for r in rows if r["defect_type"] == c]),
            "blind_recall": _mean([r["blind_caught"] for r in rows if r["defect_type"] == c])}
        for c in classes
    }

    monitor_fp_rate = _mean([r["monitor_fp"] for r in control_rows])
    blind_fp_rate = _mean([r["blind_fp"] for r in control_rows])

    # The monitor earns its keep iff the recall delta is significant (CI lo > 0) AND it does not
    # buy that recall with a runaway false-positive rate on clean controls.
    if ci["lo"] > 0 and monitor_fp_rate <= max(0.34, blind_fp_rate + 0.1):
        verdict = "monitor_adds_detection_value"
    elif ci["hi"] < 0:
        verdict = "blind_better"
    else:
        verdict = "monitor_inconclusive"

    return {
        "n_injected": len(injected),
        "n_controls": len(controls),
        "monitor_recall": monitor_recall,
        "blind_recall": blind_recall,
        "recall_delta_mean": round(monitor_recall - blind_recall, 4),
        "ci_90_monitor_minus_blind": ci,
        "by_defect_class": by_class,
        "control_fp_rate": {"monitor": monitor_fp_rate, "blind": blind_fp_rate},
        "per_item": rows,
        "verdict": verdict,
    }
