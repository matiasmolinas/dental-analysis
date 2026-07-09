"""Fable-predicts-Opus's-workspace: the circularity-gate primitives (Phase R6, mode 4).

Design + rationale: docs/analysis/fable-predicted-workspace-design.md. This is NOT the
self-report probe (Opus introspecting itself, privileged access); this is a DIFFERENT model
(Fable) predicting what Opus's global workspace SHOULD have contained, grounded in the J-lens
paper's precepts — external inference, no activation access, explicitly a SIMULATION, never a
measurement.

The make-or-break is circularity: if the predictor RE-SOLVES the problem its output is a
function of the input and carries zero new bits. It escapes only via the DELTA framing —
predict, conditioned on the executor's OUTPUT, only content ABSENT from that output — and only
if the non-redundant surface P \ (O ∪ C) is non-empty (P = predicted items, O = items in the
output, C = items a blind converger surfaces). This module provides the prompt contracts and
the set-logic; model calls are injected so the plumbing is testable offline.
"""

from __future__ import annotations

from typing import Any, Callable

# --------------------------------------------------------------------------- prompts

# Fable predicts Opus's workspace — the DELTA framing (must not re-solve). This is the original,
# paper-faithful prompt. It triggers a topic refusal from some models (Fable declined the medical
# meta-analysis); run_gate falls back to Opus for the prediction when the primary refuses.
PREDICTOR_SYSTEM = """You model what a competent solver's GLOBAL WORKSPACE (the J-space from
Anthropic's "A global workspace in language models") SHOULD have contained while analyzing this
oral-systemic case — the silent, non-verbalized content: things noticed but not said, considered
and dropped, intermediate steps, anomalies caught, variables whose absence should register.

CRITICAL RULES:
- You do NOT have access to the solver's activations. This is INFERENCE grounded in the paper's
  precepts, a SIMULATION — never a measurement. Do not invent layer numbers or magnitudes.
- You are GIVEN the solver's actual OUTPUT. Do NOT re-solve the case. Report ONLY workspace
  content that is ABSENT from that output — the delta between "what a competent workspace would
  hold" and "what the output actually said".
- Prefer non-obvious content: a confounder, a drug-tissue interaction, an internal inconsistency,
  a dropped mediator — the kind of thing the output silently omitted.

Return, via the tool, items = [{key: short_snake_case_id, channel: one of
[silent-assessment, considered-but-dropped, intermediate-step, error-noticed, missing-variable],
concept: short phrase (multi-token OK), salience: strong|moderate|faint, appears_in_output:
true|false}]. Set appears_in_output=true when the item is already stated in the output you were
given (then it is NOT a gap)."""

# The blind converger — surfaces gaps WITHOUT any workspace/lens signal. Its output is C: what
# re-derivable competence alone catches. Kept LEAN (top considerations only) so C does not
# trivially cover the whole space — a leaner C is a fairer test of whether the predictor adds
# something non-redundant (an exhaustive C stacks the gate toward "circular").
BLIND_SYSTEM = """You are a careful oral-systemic (periodontal + cardiovascular) research analyst.
Non-diagnostic. From the record below, list the MOST IMPORTANT considerations to investigate —
the key gaps, missing data, confounders, drug-tissue interactions, or inconsistencies. Be
selective: list your top ~8 considerations, not an exhaustive dump. Do not produce the full
analysis — only the list.

Return, via the tool, items = [{key: short_snake_case_id, concept: short phrase}]."""


# Semantic clustering of predictions across the K runs: groups synonymous items so stability is
# counted per-CONCEPT, not per-(differently-worded)-key. The exact-key shortcut fragmented
# recurring items and biased the gate toward "circular" — this fixes that.
CLUSTER_SYSTEM = """You are given a numbered list of candidate items, each produced in one of
several independent runs (its run index is shown). Group items that express the SAME underlying
consideration (synonyms/paraphrases of the same point) into clusters. Every index belongs to
exactly one cluster; a unique point forms a singleton cluster. For each cluster give a canonical
concept, its channel, and the member indices.

Return, via the tool, clusters = [{concept: canonical short phrase, channel: the dominant channel,
member_indices: [int, ...]}]."""


def cluster_predictions(
    runs: list[dict],
    k: int,
    cluster_fn: Callable[[str], dict],
    stability_min: float = 0.6,
) -> list[dict]:
    """Semantic version of aggregate_predictions: cluster synonymous items across runs (via
    cluster_fn), then keep clusters that are stable (span >= stability_min of the K runs) AND
    confidently absent from the output. stability = distinct runs the cluster spans / k."""
    flat = []  # (global_index, run_index, item)
    for run_i, run in enumerate(runs):
        for it in run.get("items", []):
            flat.append((len(flat), run_i, it))
    if not flat:
        return []
    listing = "\n".join(
        f"{gi}: [run {ri}] ({it.get('channel','')}) {it.get('concept','')}"
        for gi, ri, it in flat
    )
    clusters = cluster_fn("ITEMS:\n" + listing).get("clusters", [])
    out = []
    for cl in clusters:
        idxs = [i for i in cl.get("member_indices", []) if 0 <= i < len(flat)]
        if not idxs:
            continue
        runs_covered = {flat[i][1] for i in idxs}
        members = [flat[i][2] for i in idxs]
        stability = len(runs_covered) / k if k else 0.0
        appears_rate = (sum(bool(m.get("appears_in_output")) for m in members) / len(members))
        if stability >= stability_min and appears_rate < 0.5:
            key = (cl.get("concept", "") or members[0].get("concept", ""))[:40]
            key = "_".join(key.lower().split())
            out.append({
                "key": key, "channel": cl.get("channel", members[0].get("channel", "")),
                "concept": cl.get("concept", members[0].get("concept", "")),
                "stability": round(stability, 3), "appears_in_output_rate": round(appears_rate, 3),
                "n_members": len(members),
            })
    return out

# Coverage judge: is each predicted item already covered by the output (O) or the blind list (C)?
COVERAGE_JUDGE_SYSTEM = """You decide, for each candidate item, whether its content is ALREADY
PRESENT (semantically, not necessarily verbatim) in EITHER the executor OUTPUT or the blind
CONSIDERATIONS list provided. A candidate is "covered" if a reader of O or C would already have
that consideration. Be strict: near-synonyms count as covered; a genuinely distinct point does not.

Output ONLY a JSON object: {"verdicts": [{"key": "<candidate key>", "covered": <true|false>,
"why": "<one short clause>"}]}. Return the JSON and nothing else."""


# --------------------------------------------------------------------------- aggregation

def aggregate_predictions(runs: list[dict], k: int, stability_min: float = 0.6) -> list[dict]:
    """Cluster K predictor runs by item `key`; keep items that are (a) stable across runs and
    (b) confidently absent from the output. stability = fraction of runs the key appears in;
    the confidence proxy that privileged access would otherwise supply."""
    seen: dict[str, dict] = {}
    counts: dict[str, int] = {}
    out_flags: dict[str, list[bool]] = {}
    for run in runs:
        keys_this_run = set()
        for it in run.get("items", []):
            key = it.get("key")
            if not key or key in keys_this_run:
                continue
            keys_this_run.add(key)
            counts[key] = counts.get(key, 0) + 1
            out_flags.setdefault(key, []).append(bool(it.get("appears_in_output", False)))
            seen.setdefault(key, it)
    agg = []
    for key, cnt in counts.items():
        stability = cnt / k if k else 0.0
        appears_rate = sum(out_flags[key]) / len(out_flags[key]) if out_flags[key] else 0.0
        item = dict(seen[key])
        item["stability"] = round(stability, 3)
        item["appears_in_output_rate"] = round(appears_rate, 3)
        agg.append(item)
    # candidate signal: stable AND confidently NOT in the output
    return [i for i in agg if i["stability"] >= stability_min and i["appears_in_output_rate"] < 0.5]


# --------------------------------------------------------------------------- the gate

def non_redundant_surface(
    p_items: list[dict],
    executor_output: dict,
    c_items: list[dict],
    judge_fn: Callable[[str], dict],
) -> dict[str, Any]:
    """Compute P \\ (O ∪ C): the predicted items NOT already covered by the executor output or the
    blind considerations. `judge_fn(prompt)->dict` runs the coverage judge. Empty surface => the
    approach collapsed to circular for this case."""
    import json
    if not p_items:
        return {"surface": [], "covered": [], "circular": True, "reason": "no stable predicted items"}
    prompt = (
        "EXECUTOR OUTPUT (O):\n" + json.dumps(executor_output, indent=2)
        + "\n\nBLIND CONSIDERATIONS (C):\n" + json.dumps({"items": c_items}, indent=2)
        + "\n\nCANDIDATE ITEMS (P):\n"
        + json.dumps({"items": [{"key": i["key"], "concept": i.get("concept", "")} for i in p_items]}, indent=2)
    )
    verdicts = {v["key"]: v for v in judge_fn(prompt).get("verdicts", [])}
    surface, covered = [], []
    for it in p_items:
        v = verdicts.get(it["key"], {"covered": False, "why": "no verdict -> treated as novel"})
        (covered if v.get("covered") else surface).append({**it, "_why": v.get("why", "")})
    return {
        "surface": surface,          # P \ (O ∪ C)
        "covered": covered,          # P ∩ (O ∪ C)
        "circular": len(surface) == 0,
        "n_surface": len(surface),
        "n_predicted": len(p_items),
    }
