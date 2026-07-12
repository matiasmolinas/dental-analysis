"""SkillOpt — a gated, W1-standard evolutionary loop over the *trainable* skills.

The one Claude role HISTORA didn't yet demonstrate: **Claude improving Claude's own tooling under a
safety invariant that is structurally impossible to evolve.** Claude proposes an edit to ONE trainable
`SKILL.md`; the edit is adopted ONLY IF it

  1. passes the **non-diagnostic guardrail on every held-out case** — a HARD BINARY GATE, never traded
     for accuracy (fitness = disqualified if any case fails the guardrail); and
  2. beats the parent **AND a prose-only control of the same change** on a *structural* fitness metric —
     the W1 discipline: the win must come from **deploying** the edited skill, not from merely mentioning
     the content (the prose arm isolates externalization from content).

Every generation appends to an **auditable archive** with lineage (parent→child), the fitness delta + CI,
the verdict, and the **guardrail hash** — identical in parent and child, which is the *proof* the
protected invariant was never touched.

Structural safety, not goodwill: the guardrail skill, `histora.citations`, and the mechanistic engine are
**outside the genome**; the genome is only the prose of the `SkillOpt-trainable` `SKILL.md` files. Fitness
is external/structural — never model-judged. Reuses `histora.exec_gap.run_directive_ab` (the 3-arm A/B)
and `histora.ab_eval.guardrail_pass` (the gate). Pure-python; model calls injected for offline testing.
Non-diagnostic throughout — the loop never produces or persists a patient value.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Callable, Optional

from .exec_gap import run_directive_ab

# The genome: only these skills' prose may be mutated. The guardrail is PROTECTED — never in the allowlist.
TRAINABLE = {"record-normalization", "cardiometabolic-framing", "periodontal-staging",
             "oral-systemic-kb", "traceability-audit"}
PROTECTED = {"non-diagnostic-guardrail"}


def skill_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def guardrail_gate(candidate_text: str, records: list[dict], render: Callable[[str, dict], str],
                   eval_fn: Callable[[str], dict], guardrail_fn: Callable[[dict, dict], bool]) -> float:
    """Fraction of held-out cases whose candidate-skill output passes the non-diagnostic guardrail.
    A hard gate: adoption requires 1.0 — never trades safety for fitness."""
    if not records:
        return 0.0
    ok = sum(1 for r in records if guardrail_fn(eval_fn(render(candidate_text, r)), r))
    return round(ok / len(records), 4)


MUTATION_SYSTEM = """You improve ONE oral-systemic reasoning SKILL.md for a NON-DIAGNOSTIC research agent.
You are given the current skill and concrete failure traces (where it under-performed a structural
metric). Propose a focused edit that fixes the recurring defect. HARD RULES you must not break: keep it
non-diagnostic (no diagnosis, no imputing a patient value; a missing datum is a collection flag); keep
every claim traceable to input fields; do not touch the guardrail. Output ONLY JSON:
{"candidate_skill": "<the full edited SKILL.md body>", "change_summary": "<one sentence: what you changed and why>"}"""


def propose_mutation(skill_text: str, failure_traces: str,
                     model_fn: Callable[[str, str], str]) -> dict[str, str]:
    """Claude proposes a directed edit from the failure traces (the mutation operator). `model_fn(system,
    user) -> text` (injectable for offline tests). Returns {candidate_skill, change_summary}."""
    import re
    user = f"Current SKILL.md:\n{skill_text}\n\nFailure traces (structural metric under-performed here):\n{failure_traces}"
    text = model_fn(MUTATION_SYSTEM, user).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.DOTALL)
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    obj = json.loads(m.group(0) if m else text)
    return {"candidate_skill": str(obj["candidate_skill"]), "change_summary": str(obj.get("change_summary", ""))}


def evolve_generation(
    skill_name: str,
    parent_text: str,
    candidate_text: str,
    change_summary: str,
    records: list[dict],
    render: Callable[[str, dict], str],
    eval_fn: Callable[[str], dict],
    fitness_fn: Callable[[dict, dict], float],
    guardrail_fn: Callable[[dict, dict], bool],
    guardrail_text: str,
    archive_path: Optional[str] = None,
) -> dict[str, Any]:
    """Evaluate ONE candidate edit against its parent, gate it, and archive it. `render(skill, rec)->input`
    turns a skill+case into the model input; `eval_fn(input)->output`; `fitness_fn`/`guardrail_fn` are
    STRUCTURAL (external), never model-judged. Adopt iff the guardrail passes on every case AND the
    candidate beats the parent (CI excludes 0). The prose arm classifies WHY (execution vs knowledge gap)."""
    if skill_name not in TRAINABLE:
        raise ValueError(f"{skill_name} is not in the trainable genome (PROTECTED skills never evolve)")

    # HARD GATE first — never spend the A/B verdict on something that breaks the invariant.
    gpass = guardrail_gate(candidate_text, records, render, eval_fn, guardrail_fn)

    # 3-arm A/B (reused from exec_gap): base=parent, enforced=candidate, prose=parent+change-as-prose.
    def base_build(rec):
        return render(parent_text, rec)

    def enforced_build(rec):
        return render(candidate_text, rec)

    def prose_build(rec):
        return render(parent_text + f"\n\n[Additional guidance]: {change_summary}", rec)

    ab = run_directive_ab(records, base_build, enforced_build, prose_build, eval_fn, fitness_fn)

    adopted = bool(ab["helps"]) and gpass == 1.0
    entry = {
        "skill": skill_name,
        "parent_hash": skill_hash(parent_text),
        "child_hash": skill_hash(candidate_text),
        "guardrail_hash": skill_hash(guardrail_text),   # identical parent↔child = invariant untouched
        "guardrail_pass_rate": gpass,
        "fitness_means": ab["means"],
        "ci_90_enforced_minus_base": ab["ci_90_enforced_minus_base"],
        "ci_90_enforced_minus_prose": ab["ci_90_enforced_minus_prose"],
        "pattern": ab["pattern"],           # execution_gap (W1) / knowledge_gap / screened
        "helps": ab["helps"],
        "adopted": adopted,
        "reason": ("adopted: guardrail 1.0 + fitness gain (CI excludes 0)" if adopted
                   else "rejected: guardrail<1.0" if gpass < 1.0
                   else "rejected: no fitness gain (CI includes 0)"),
        "change_summary": change_summary,
        "non_diagnostic": True,
    }
    if archive_path:
        append_archive(archive_path, entry)
    return entry


def append_archive(path: str, entry: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_archive(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]
