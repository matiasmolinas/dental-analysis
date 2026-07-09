# Circularity-gate v2: NON-EMPTY surface — the approach is NOT circular (planted gap not isolated)

> 2026-07-09, live Claude. Second gate run, after fixing the two v1 confounds
> ([`gate-experiment-result.md`](gate-experiment-result.md)). Roles: executor = **Opus 4.8**
> (strong), predictor = **Sonnet 5** (light, ≠ executor → model diversity), blind = Sonnet 5
> (lean), judge/cluster = Sonnet 5. Written directly (Fable refuses this medical-meta topic).
> Grounded in `results/gate_report_v2.json`.

## What changed from v1
- **Semantic clustering** of predictions across the K=5 runs (was exact-key, which fragmented
  recurring items and biased toward "circular").
- **Model diversity restored:** the Sonnet predictor is a *different* model from the Opus
  executor, and it **did not refuse** (all 5 runs ran on Sonnet; no fallback).
- **Lean blind:** Sonnet, top-~8 considerations, so C (8 items) does not trivially cover the space
  (was an exhaustive 24-item Opus dump).

## Result
`VERDICT: non_empty_but_planted_gap_not_isolated`.

| quantity | v1 | **v2** |
|---|---|---|
| predictor model (used) | Opus (Fable refused) | **Sonnet** (no refusal) |
| blind C items | 24 (exhaustive) | **8 (lean)** |
| stable P clusters (absent-from-output) | 2 | **8** |
| non-redundant surface `P \ (O ∪ C)` | **0 (circular)** | **7 (non-empty)** |
| planted gap surfaced by blind? | False | False |
| planted gap isolated in surface? | False | False |

## Reading — two honest halves

### ✅ The load-bearing positive: the approach is NOT circular
The non-redundant surface is **non-empty (7 items)** — with a *different* uncommitted predictor, a
*lean* blind, and *semantic* clustering, the predictor surfaces content that is present in neither
the executor's output (O) nor a blind converger's considerations (C). **This confirms the v1
"circular" verdict was a harness artifact, not a property of the approach.** The escape condition
from `fable-predicted-workspace-design.md` §2 — `P \ (O ∪ C)` non-empty — is met.

The 7 surfaced items are genuine, non-obvious, and non-redundant. Highlights:
- **"Smoking-induced vasoconstriction may suppress BOP, masking true inflammation"** — 5/5 runs.
  A real confound: the output read 62% BOP as inflammation; the lean blind noted BOP-as-marker but
  not that smoking *suppresses* it. Genuinely off the output plane.
- **"Inconsistent confidence weighting across axes in the output"** (silent-assessment) — a
  **meta-observation about the output's own reasoning quality**. Only a reviewer that *sees the
  output* and is *not committed to it* can make this; O cannot self-report its own inconsistency.
  This is the clearest example of the "non-redundant-with-output" property the burden-of-proof doc
  argued makes the workspace signal privileged.
- Metabolic-syndrome synthesis (~3/5 criteria not formally noted), missing age/sex/BMI for CV risk
  calculators, no formal ASCVD/Framingham score computed despite the inputs, statin-absence
  pleiotropic angle. Each is absent from both O and the lean C (the judge correctly moved the one
  genuinely-overlapping item — grade-C progression rationale — to COVERED).

### ⚠️ The caveat: the specific planted gap was NOT isolated
The planted amlodipine→gingival-overgrowth confounder is **not** in the surface. It was non-obvious
to the blind (good) but the **light Sonnet predictor did not stably surface it** across the 5 runs —
whereas Opus put it as its **top item** in the earlier isolated single run. So this is a
**predictor-capability gap for that specific subtle drug-tissue plant**, not a mechanism failure.
The clean "did it catch the exact plant?" test is therefore **not passed** with the light predictor.

## What this licenses
- **Licenses:** "an uncommitted external predictor surfaces non-redundant, non-obvious gaps the
  output and a blind converger both miss" — demonstrated (7 items, several at high stability,
  including an output-quality meta-critique O cannot produce). The approach is viable and **not
  circular**.
- **Does NOT yet license:** "the gate reliably isolates a specific planted gap" — the light
  predictor missed this plant; and, crucially, **non-redundant ≠ behaviorally useful.** Per the
  design §4 and the burden-of-proof doc, the surfaced items must still be shown to *move
  counterfactual sensitivity / relational_recall* when grounded into the input. That behavioral
  step is the real payoff and is not yet run.

## Next
1. **Behavioral validation (the payoff):** ground the 7 surfaced items into the executor input and
   measure whether counterfactual sensitivity / relational_recall improve vs not — the design's
   step-4 test that turns "non-redundant" into "useful."
2. **Predictor capability vs diversity trade-off:** re-run with an **Opus predictor** to check
   whether the amlodipine plant is isolated when the predictor is strong (accepting predictor =
   executor, reduced diversity) — this separates "the light model missed it" from "the plant is
   unreachable." A stronger non-refusing predictor different from Opus would be ideal.
3. Scale to more planted cases + n≥30 before any general claim.

**Bottom line:** v2 removes the confounds and flips the headline: the mode-4 approach is **not
circular** — an uncommitted external predictor does surface non-redundant, non-obvious gaps (7),
including a meta-critique of the output's own reasoning that is non-redundant by construction. What
remains unproven is (a) reliable isolation of a *specific* planted gap with a light predictor, and
(b) that the surfaced gaps are *behaviorally useful*, not merely non-redundant.
