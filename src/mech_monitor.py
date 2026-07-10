"""Fair lens re-test on the mechanistic task — the 3-arm eval (Phase 2).

Separates the two things that could pay off on a mechanistic-reasoning task, so the §0 question is
answered without conflation:

  blind            — a generic "any problems?" read (the control).
  reasoning_monitor — audits the MECHANISTIC REASONING (counterfactual direction, causal node,
                      monotonicity, over-claimed couplings, honored uncertainty), NO model tool.
                      This is the lens-analog thesis at reasoning depth: does reading/auditing the
                      reasoning help on a task that actually requires it?
  model_grounded    — the same audit, PLUS the calibrated centerpiece's numeric predictions as an
                      oracle. This is the mechanistic-harness thesis: does having the model as a
                      checker help?

Headline: reasoning_monitor − blind (lens thesis) and model_grounded − blind (harness thesis), each
with a bootstrap CI, on labeled mechanistic defects, at matched control false-positive rate. Keeping
the two arms distinct is the whole point — a win for model_grounded but not reasoning_monitor would
say the payoff is the MODEL (a tool), not reading the workspace, consistent with the §0 arc.

Model-agnostic core (injected callables) → tested offline; run_mech_monitor wires Opus + Sonnet.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from ablation import _bootstrap_ci
from qa_monitor import MONITOR_TOOL  # reused item schema

MECH_BLIND_SYSTEM = """You are reviewing an oral-systemic mechanistic analysis (periodontal →
systemic inflammation → cardiovascular / neuro). You are given the case and the analysis's CLAIMS.
Point out any problems you notice. Return, via the tool, items = [{key, defect_type: short label,
quote: the offending claim, severity: high|medium|low, why: one clause}]."""

MECH_MONITOR_SYSTEM = """You AUDIT THE MECHANISTIC REASONING of an oral-systemic analysis (periodontal
→ IL-6 → hepatic CRP → cardiovascular / neuro). You are given the case and the analysis's CLAIMS. Do
NOT re-derive numbers; check the REASONING for mechanism errors a careful modeler would catch:
- counterfactual DIRECTION (e.g. does removing the oral inflammatory source raise or lower CRP?),
- CAUSAL NODE (IL-6/IL-1β are causal drivers; CRP is a downstream marker — not the cause),
- MONOTONICITY (more periodontal inflammation should not lower systemic inflammation),
- OVER-CLAIMED couplings (a hypothesized/scaffold link stated as an established fitted fact),
- UNHONORED UNCERTAINTY (a definitive point value where only a range is supported).
Flag each claim that violates sound mechanism. Return, via the tool, items = [{key, defect_type,
quote, severity, why}]."""

MECH_GROUNDED_SYSTEM = MECH_MONITOR_SYSTEM + """

You are ALSO GIVEN reference predictions from a calibrated mechanistic model (steady-state IL-6/CRP,
counterfactual ΔCRP for therapy and IL-6 blockade, axis couplings with confidence flags, and the CRP
range). USE these numbers to verify each claim: a claim that contradicts the reference is a defect."""


def detect_mech(monitor_fn: Callable[[str], dict], case_text: str, answer: dict,
                reference: dict | None = None) -> list[dict]:
    """Run an arm over (case, answer[, reference]); returns flagged items."""
    user = "CASE:\n" + case_text + "\n\nANALYSIS CLAIMS:\n" + json.dumps(answer.get("claims", answer),
                                                                        indent=2)
    if reference is not None:
        user += "\n\nREFERENCE MODEL PREDICTIONS (oracle):\n" + json.dumps(reference, indent=2)
    return monitor_fn(user).get("items", [])


def evaluate_mech(
    injected: list[dict],
    controls: list[dict],
    arms: dict[str, Callable[[str, dict, dict | None], list[dict]]],
    judge_caught: Callable[[list[dict], dict], bool],
    baseline: str = "blind",
) -> dict[str, Any]:
    """3-arm eval. `injected`=[{case_text, answer, label, reference}]; `controls`=[{case_text,
    answer, reference}]. `arms`={name: detect_fn}. Reports per-arm recall on mechanistic defects,
    each arm's paired delta vs the baseline arm with a bootstrap CI, control FP per arm, by-class,
    and a verdict separating the lens thesis (reasoning_monitor) from the harness thesis
    (model_grounded)."""
    names = list(arms)
    per_item = []
    for it in injected:
        row = {"defect_type": it["label"].get("defect_type")}
        for name, fn in arms.items():
            row[name] = judge_caught(fn(it["case_text"], it["answer"], it.get("reference")), it["label"])
        per_item.append(row)

    control_rows = []
    for it in controls:
        crow = {}
        for name, fn in arms.items():
            crow[name] = len(fn(it["case_text"], it["answer"], it.get("reference"))) > 0
        control_rows.append(crow)

    def _mean(xs):
        return round(sum(xs) / len(xs), 4) if xs else 0.0

    recall = {n: _mean([int(r[n]) for r in per_item]) for n in names}
    fp = {n: _mean([int(r[n]) for r in control_rows]) for n in names}
    classes = sorted({r["defect_type"] for r in per_item})
    by_class = {c: {n: _mean([int(r[n]) for r in per_item if r["defect_type"] == c]) for n in names}
                for c in classes}

    deltas_vs_baseline = {}
    for n in names:
        if n == baseline:
            continue
        d = [int(r[n]) - int(r[baseline]) for r in per_item]
        deltas_vs_baseline[n] = {"mean": round(recall[n] - recall[baseline], 4),
                                 "ci_90": _bootstrap_ci(d)}

    def _verdict(arm):
        if arm not in deltas_vs_baseline:
            return "n/a"
        ci = deltas_vs_baseline[arm]["ci_90"]
        if ci["lo"] > 0 and fp[arm] <= max(0.34, fp[baseline] + 0.1):
            return "adds_value"
        if ci["hi"] < 0:
            return "worse_than_blind"
        return "inconclusive"

    return {
        "n_injected": len(injected),
        "n_controls": len(controls),
        "recall": recall,
        "control_fp_rate": fp,
        "by_defect_class": by_class,
        "deltas_vs_blind": deltas_vs_baseline,
        "per_item": per_item,
        "lens_thesis_reasoning_monitor": _verdict("reasoning_monitor"),
        "harness_thesis_model_grounded": _verdict("model_grounded"),
    }
