# V2 Honest Read: Where the Inferred Lens Has Real Impact — and the Evolution Plan

> Produced 2026-07-09 with the **Fable** model. Scope: live Claude Sonnet-5, v2 results
> (`results/ablation_v2.json` n=6 real NHANES; `results/counterfactual_report.json` n=4).
> Inferred lens = self-report only, Claude grading Claude. Companion to
> [`lens-ablation-result.md`](lens-ablation-result.md) (v1) and
> [`is-the-lens-working.md`](is-the-lens-working.md). No cheerleading — the evidence is
> mostly negative and this document says so.

## 1. Headline verdict

At n=6 the inferred lens is **`lens_inconclusive`** over blind convergence: no axis's 90%
CI excludes 0. The only directional hint is relational recall (**B_lens 0.94 vs B_blind
0.83, +0.104**) and its CI **[-0.042, +0.229] straddles 0** — mechanism recall's edge is a
negligible **+0.021 [-0.042, +0.083]**, and both guardrail axes are a flat **0.00 → 0.00 →
0.00** across A / B_blind / B_lens. The guardrail value therefore does **not** live in
model convergence at all (neither lens nor blind free-form prose reaches it); it lives only
in the **deterministic harness directive** (`ab_eval.build_inputs`), which hit guardrail
1.0 (6/6) in R5 while the free-form convergers stay at 0.0 **even with that same directive
pasted into their instruction**. Finally, counterfactual sensitivity is **0.00 for both
A_naive and B_converged** over 12 flips each, and B_converged's mean affected-delta is
**-0.33** (removing a factor sometimes moved its own axis the *wrong* way) — so mediator
"recall" is largely **not factor-grounded reasoning**; the name-echo artifact suspected in
v1 is now confirmed behaviorally.

## 2. Gap-map: MODE × SURFACE

Demonstrated impact of the *inferred* lens: PROVEN / SUGGESTIVE / NOT-SHOWN / UNTESTED.
Most cells are NOT-SHOWN or UNTESTED — the ablation tested one bundled input-convergence
(not per-surface isolation), and the Session Working-Consciousness never ran live.

| MODE ↓ / SURFACE → | Context | Knowledge / KB | Instructions (skills/sub-agents/prompts) | Harness |
|---|---|---|---|---|
| **One-shot lens readout** | **NOT-SHOWN** — B_lens vs B_blind +0.104 relational but CI straddles 0. | **NOT-SHOWN** — KB given to *both* B arms; no KB-only ablation. | **NOT-SHOWN** — counterfactual 0.00 for both; B_converged delta -0.33; not factor-grounded. | **NOT-SHOWN (for the lens)** — guardrail 0.00 across all arms; the 1.0 is the deterministic directive, produced *without* any readout. |
| **Session Working-Consciousness** | **UNTESTED** — SWC never ran live; only `.session/example_case01.md`. | **UNTESTED** — no cross-turn KB consolidation run. | **UNTESTED** — no live deficiency→edit→re-check loop measured. | **UNTESTED** — no live session drove a harness injection + verified the readout change. |

**Zero PROVEN cells.** The least-weak cell is one-shot readout × instructions as a
*detector* (§3), and even there the improvement claim is NOT-SHOWN. The entire SWC row is
UNTESTED — that mode has no live run at all.

## 3. Where the lens plausibly still helps as a DETECTOR (not an improver)

- **As an improver: NOT-SHOWN.** B_lens does not beat B_blind beyond noise on any axis.
- **As a localizer: plausibly cheap and real, but unproven-as-useful.** The readout names a
  gap — `missing_variable(hs_crp)`, `missing_mediator(endothelial)`,
  `uncovered_cot_step(axis_derivation)` — a localization the scalar score doesn't give.
  But it is worth something only if the localizer is *accurate* and *actionable by a fix
  that improves outputs*; on v2 evidence neither is established (self-report, uncorroborated;
  the one action taken did not improve outputs). A localizer pointing at a gap nobody can
  profitably fix is a dashboard, not a lever.
- **The condition to become an improver — the measured-lens unlock.** The inferred signal
  crosses from detector to improver when localization is corroborated by an API-observable
  behavioral test (counterfactual sensitivity actually moving). Today that reads 0.00, so
  there is nothing for the localizer to be right *about* yet. A *measured* Jacobian lens
  (`APPROACH.md` §8) would make the localization causal ground truth. Until then: a cheap,
  uncorroborated gap-namer, not a proven optimizer.

## 4. The real, evidence-backed gaps to evolve now (regardless of the lens)

**(a) Counterfactual ~0 → outputs not factor-grounded (INSTRUCTIONS surface).** Both formats
score 0.00 (24 flips); B_converged mean affected-delta -0.33. The reasoning discipline is
too weak — it never forces each axis to be justified by the *specific present factors* or to
weaken when a factor is absent. → edit `skills/oral-systemic-analysis.md`,
`agents/oral-systemic-relational-reasoner.md`.

**(b) Free-form convergence can't hit the guardrail → deterministic directive canonical
(HARNESS surface).** Guardrail 0.00 for every free-form arm; only the hardcoded directive in
`ab_eval.build_inputs` reached 1.0. → expose the missing-mediator flags as a first-class
deterministic bundle in `src/relational_signals.py`; make `prompts/evaluator.md` treat that
block as authoritative.

**(c) Recall overstates reasoning → prefer relational_recall + counterfactual (METRIC).**
Mechanism recall 0.94–0.96 while counterfactual 0.00 — it rewards naming, not using. →
document `relational_recall` + counterfactual `sensitivity_rate` as headline metrics;
`mechanism_recall` diagnostic-only. No code metric loosened.

## 5. Evolution plan (ordered)

Hard constraints: never edit `skills/non-diagnostic-guardrail.md`; keep all tests green;
never weaken a guardrail/metric to manufacture a win; honest reasoning-grounding /
determinism / measurement only — not lens-inflation.

| # | File | Bounded edit | Why | Tier | Verify |
|---|---|---|---|---|---|
| 1 | `agents/oral-systemic-relational-reasoner.md` | each axis mechanism must cite the *present* factor(s) driving it and state it weakens if that factor is absent (map to counterfactual.py axes) | counterfactual 0.00, B delta -0.33 | T1 | rerun `run_counterfactual.py`: sensitivity_rate > 0, mean_affected_delta ≥ 0 |
| 2 | `skills/oral-systemic-analysis.md` | "Factor-grounding" bullet: no axis on mediator vocabulary alone | same | T1 | relational_recall must not regress |
| 3 | `src/relational_signals.py` | add `required_missing_data_block(record)` — deterministic `{field,why,impact}` for absent mediators | guardrail 0.00 free-form; 1.0 only deterministic | T0/T1 | `test_relational_signals.py`; build_inputs still 1.0 |
| 4 | `prompts/evaluator.md` | the injected `required_missing_data` block is authoritative, emit unchanged | prose→structured drops the flag | T1 | directive arm stays 1.0 |
| 5 | `docs/analysis/` | mechanism_recall → diagnostic-only; relational_recall + counterfactual → headline | recall overstates | T0 | doc-only |
| 6 | `docs/analysis/` | record every SWC×surface cell UNTESTED + the minimal live test to change that | SWC never ran | T0 | doc-only |

Order rationale: 1–2 attack the one gap the behavioral test *proves* (factor-grounding),
measurable by the counterfactual runner — the prerequisite that could later turn the lens
from detector into improver. 3–4 lock the guardrail value into the deterministic path where
the evidence says it lives. 5–6 are measurement/honesty hygiene.
