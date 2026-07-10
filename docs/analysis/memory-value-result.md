# Cross-session memory (trace-consolidation) value — the decision gate result

> Run 2026-07-10. `run_memory_value.py --cases nhanes --n-train 4 --n-holdout 3 --min-support 1
> --fresh-ledger`. Executor = Opus, selector = Sonnet. Report: `results/memory_value_report.json`.
> This is the measurement the project **built and never ran** (the decision gate for harness
> evolution / any "dream/consolidation" framework — see [`../EXECUTION_PLAN.md`](../EXECUTION_PLAN.md)
> Track 1 and [`harness-evolution-adoption.md`](harness-evolution-adoption.md)).

## Result: `memory_inconclusive` — WARM ≈ COLD, at the weakest possible bar

| metric | WARM−COLD mean | CI90 |
|---|---|---|
| guardrail_pass_rate | 0.0 | [0.0, 0.0] |
| relational_recall | 0.0 | [−0.083, +0.083] |
| cf_mean_affected_delta | 0.0 | [−0.444, +0.444] |

`significant_gain_axes = []`, `significant_loss_axes = []`. **Cross-session consolidation did not
beat a cold start.** Per-case, WARM is mixed-to-negative, not additive:

| case | cold rr | warm rr | cold cf | warm cf |
|---|---|---|---|---|
| 0 | 0.625 | **0.500** ↓ | −0.33 | −0.33 |
| 1 | 0.625 | 0.625 | −0.33 | **+0.33** ↑ |
| 2 | 0.500 | **0.625** ↑ | 0.00 | **−0.67** ↓ |

WARM actively **hurt** on some axis in 2 of 3 cases (case 0 recall; case 2 counterfactual) — the
stale-lever dilution / append-all failure mode (F1) reappearing. Mean effect exactly 0.

## Honest caveats (they make the null weaker, not stronger — and that matters)

1. **Thinnest possible material.** Only **1 of 4** training cases produced a lever — the SWC
   turn-1→turn-2 improvement mechanism fired once (the other three did not improve, so nothing was
   written). Consolidation ran on **1 belief**. The upstream lever-generation is itself unreliable.
2. **Weakest bar.** `min_support=1` — a single un-repeated lever was promoted to a belief. This is the
   most *generous* setting for showing value, and it still returned 0. A stricter `min_support≥2`
   would have yielded **zero beliefs** (a no-op), not a stronger result.
3. **Underpowered** (n=3 holdout) — but the point estimate is exactly 0 and the pattern is
   mixed-to-negative, so more n would need to overcome a null-to-negative prior, not a positive trend.
4. **Guardrail failed in every arm** (`guardrail_pass=False`, cold and warm alike): `run_memory_value`
   uses `format_b_sections_glossed`, which does **not** carry the deterministic missing-data directive
   that `ab_eval.build_inputs`' B format does (that directive was the project's one clean win, W1). The
   consolidation pipeline runs on a weaker input than the apparatus's best format — orthogonal to the
   WARM−COLD comparison, but worth fixing before any future consolidation attempt.

## 1b applied — adopt nothing

Per the plan's gate: **`memory_inconclusive` → adopt nothing.** Concretely:

- **llmunix / skillos: all CUT stands** (plugin, python-executor, combination). Fable's transitivity
  argument now has its premise measured: a deterministic, targeted, guardrailed consolidation
  (`lever_ledger.consolidate`) yields WARM−COLD ≈ 0; a keyword-overlap LLM "dream" pass over
  self-graded traces is a **strictly noisier estimator of the same quantity**, so it cannot yield
  more. Automating this loop would automate a null.
- **No hand-extension of `lever_ledger.py`** (negative constraints / deprecation / failure tags) —
  that was gated on `memory_adds_value`, which did not fire. The ~80-line shopping list and the
  anti-overfitting-gate rubric stay in the drawer, available if a future task ever shows consolidation
  value.
- **Recorded, not retried.** This is the honest close of the harness-evolution track: on this
  re-derivable task, cross-session trace-consolidation is not demonstrated to beat a cold start — fully
  consistent with the §6 boundary condition (the value would require content a competent reader lacks;
  a re-derivable NHANES case is inside the reader's competence).

## What this does and doesn't say
- It does **not** say cross-session memory is worthless in general — only that it is **not demonstrated
  to pay** on this task, at the weakest bar, with the machinery as built.
- It **does** retire the "build/adopt a consolidation framework" question: measure-first returned null,
  so there is nothing to automate. The durable value line remains **Track 2** (the mechanistic +
  relational oral↔neuro product), which depends on neither memory nor the lens.
