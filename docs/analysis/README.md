# Analysis trail

The reasoning record behind the project's conclusions. For the product story read
[`../VISION.md`](../VISION.md) and [`../SOLUTION.md`](../SOLUTION.md); for the consolidated technical
verdict read [`../RESEARCH_SUMMARY.md`](../RESEARCH_SUMMARY.md) §0.

## The positives (what works)

- [`perio-cognition-result.md`](perio-cognition-result.md) — **the validated empirical result**:
  periodontitis ↔ cognition on real NHANES 2011-2012, 3/4 cognitive measures significant and
  confounder-adjusted, the direction the mechanistic model predicts.
- [`lens-recipes-and-the-execution-gap.md`](lens-recipes-and-the-execution-gap.md) — **the buildable
  capability**: W1 generalized. The payoff channel is the *execution gap* (`K_R^know \ K_R^exec` — a
  step the model knows but drops in situ); a predictor + 3-arm A/B to scale it.

## The lens investigation (a rigorous negative, explained)

- [`lens-hypothesis-rationale.md`](lens-hypothesis-rationale.md) — why we believed the lens should
  help, and the one missing premise (reader competence `K_R`).
- [`why-no-lens-payoff.md`](why-no-lens-payoff.md) — **the boundary condition**: `I(L;Y|O,K_R)≈0` for a
  competent reader; the info-theoretic core, with the negative-space and session-level refinements
  (both NO — the boundary bites harder at session scale).
- [`phase2-fair-lens-retest.md`](phase2-fair-lens-retest.md) — the fair 3-arm re-test on a mechanistic
  task (blind ≈ monitor ≈ oracle): the boundary condition measured.
- [`qa-monitor-live-result.md`](qa-monitor-live-result.md) — the QA-monitor (lens-as-detector) live
  runs (v1 ceiling, v2 powered-inconclusive; signal localized).
- [`memory-value-result.md`](memory-value-result.md) — cross-session consolidation: **`memory_inconclusive`**
  (the decision gate for harness-evolution frameworks).
- [`harness-evolution-adoption.md`](harness-evolution-adoption.md) — llmunix / skillos adoption: measure
  first, adopt ideas not frameworks (all CUT).
- [`validated-evolution-and-qwen-regime.md`](validated-evolution-and-qwen-regime.md) — the validated
  (eval/data-anchored) evolution driver, and the one untested door: a **measured** lens on a **weaker**
  model (Qwen), the regime the boundary permits — mechanism-closure only, no Claude transfer.

## Historical record

- [`ARCHIVE/`](ARCHIVE/README.md) — the earlier analyses (the chronological lens trail) and the
  superseded planning/method docs (REFORMULATION, PLAN, IMPACT, APPROACH, HACKATHON_STRATEGY,
  FORWARD_PLAN, EXECUTION_PLAN), preserved verbatim for honesty.
