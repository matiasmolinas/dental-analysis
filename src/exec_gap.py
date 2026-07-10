"""The execution-gap directive harness — W1 generalized (the honest buildable capability).

The project's one clean win (W1) was a deterministic missing-data directive that raised guardrail
pass 0→1.0 — while free-form convergers handed the SAME directive fell back to 0.00. Fable's analysis
(docs/analysis/lens-recipes-and-the-execution-gap.md) shows why: the payoff channel is the EXECUTION
GAP — content the model KNOWS (`K_R^know`) but does not reliably DEPLOY in situ (`K_R^exec`). A
deterministic, enforced directive externalizes exactly `K_R^know \ K_R^exec`; a semantic directive the
model already applies is screened (F1 shows it can hurt).

This module makes that a repeatable capability, decoupled from the lens and from Qwen:
  1. a PRE-A/B predictor — classify a candidate directive by (known? deterministic? dropped-in-situ?)
     to predict whether it pays BEFORE spending an A/B;
  2. a 3-arm A/B — base / enforced / prose-handoff — that both measures the effect (bootstrap CI) and
     classifies WHY it paid (execution gap vs knowledge gap vs screened), the prose arm being the W1
     control that isolates externalization from content.

Model-agnostic (injected callables) → testable offline; the live wiring uses the Anthropic SDK.
Non-diagnostic (the apparatus scores structural/guardrail metrics, never a patient inference).
"""

from __future__ import annotations

from typing import Any, Callable

from ablation import _bootstrap_ci


# --------------------------------------------------------------------------- pre-A/B predictor
def predict_pays(known: bool, deterministic: bool, dropped_in_situ: bool) -> str:
    """Classify a candidate directive BEFORE any A/B (Fable's predictor). The single strongest,
    cheapest signal is `dropped_in_situ` for a `known` + `deterministic` step."""
    if not known:
        return "pays_knowledge_gap"          # external content the model lacks → inject the fact
    if deterministic and dropped_in_situ:
        return "pays_execution_gap"          # W1 class: known but not deployed → enforce it
    if not deterministic:
        return "predict_null_semantic"       # R_sem: known + applied → screened (may hurt, cf. F1)
    return "predict_null_known_and_deployed"  # deterministic but already deployed → nothing to add


def stated_but_dropped(
    task: Any,
    state_fn: Callable[[], Any],
    solve_fn: Callable[[Any], Any],
    states_check: Callable[[Any], bool],
    deploys_check: Callable[[Any], bool],
) -> dict[str, bool]:
    """The 'stated-on-demand-but-dropped-in-situ' test. `state_fn()` asks the model to produce the
    step blind (→ known ∈ K_R^know); `solve_fn(task)` runs the real solve and `deploys_check` tests
    whether the step was actually deployed (→ ∈ K_R^exec). Returns the three flags + the prediction."""
    known = states_check(state_fn())
    deployed = deploys_check(solve_fn(task))
    dropped = known and not deployed
    return {"known": known, "deployed": deployed, "dropped_in_situ": dropped}


# --------------------------------------------------------------------------- the 3-arm A/B
def run_directive_ab(
    records: list[dict],
    base_build: Callable[[dict], str],
    enforced_build: Callable[[dict], str],
    prose_build: Callable[[dict], str],
    eval_fn: Callable[[str], dict],
    score_fn: Callable[[dict, dict], float],
) -> dict[str, Any]:
    """Three arms per case — base / enforced (deterministic) / prose (same directive as text) —
    scored by a single external/structural metric. Reports per-arm means, bootstrap 90% CIs on the
    two contrasts, and the pattern classification. `score_fn(output, record) -> float` must be an
    EXTERNAL/held-out or structural metric (guardrail pass 0/1, defect recall, ...) — never a
    model-judged quality score (that would be Opus-reads-Opus, screened)."""
    per_case = []
    for i, rec in enumerate(records):
        per_case.append({
            "case": i,
            "base": score_fn(eval_fn(base_build(rec)), rec),
            "enforced": score_fn(eval_fn(enforced_build(rec)), rec),
            "prose": score_fn(eval_fn(prose_build(rec)), rec),
        })

    def _mean(arm):
        return round(sum(c[arm] for c in per_case) / len(per_case), 4) if per_case else 0.0

    means = {arm: _mean(arm) for arm in ("base", "enforced", "prose")}
    ci_vs_base = _bootstrap_ci([c["enforced"] - c["base"] for c in per_case])
    ci_vs_prose = _bootstrap_ci([c["enforced"] - c["prose"] for c in per_case])

    helps = ci_vs_base["lo"] > 0                      # enforced beats base (a real effect)
    externalization_load_bearing = ci_vs_prose["lo"] > 0   # enforced beats the prose handoff
    if not helps:
        pattern = "screened"                          # R_sem / no effect (watch for harm)
    elif externalization_load_bearing:
        pattern = "execution_gap"                     # W1 class: enforcing the known step is the win
    else:
        pattern = "knowledge_gap"                     # content helped; externalization did not

    return {
        "n": len(records),
        "per_case": per_case,
        "means": means,
        "ci_90_enforced_minus_base": ci_vs_base,
        "ci_90_enforced_minus_prose": ci_vs_prose,
        "helps": helps,
        "externalization_load_bearing": externalization_load_bearing,
        "pattern": pattern,
        "verdict": ("adopt" if helps else "reject"),
        "note": "adopt iff enforced−base CI excludes 0; pattern reads WHY (exec vs knowledge vs screened)",
    }
