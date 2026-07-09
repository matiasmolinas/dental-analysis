# Mode-4 close: NOT circular, but NOT useful — and the plant isn't isolated by either predictor

> 2026-07-09, live Claude. Combines experiment **B** (gate re-run with an Opus predictor,
> `results/gate_report_opus.json`) and **A** (behavioral validation of the surfaced gaps,
> `results/gate_behavioral.json`). Builds on [`gate-experiment-v2-result.md`](gate-experiment-v2-result.md).
> Written directly (Fable refuses this medical-meta topic). Honest close of the mode-4
> ("predicted workspace") arc.

## B — Opus predictor: same verdict as Sonnet, plant still not isolated

| | v2 (Sonnet predictor) | **B (Opus predictor)** |
|---|---|---|
| blind C items (lean) | 8 | 10 |
| stable P clusters | 8 | 14 |
| non-redundant surface `P \ (O ∪ C)` | 7 | **9 (non-empty)** |
| planted amlodipine gap isolated? | No | **No** |
| verdict | non_empty_but_planted_gap_not_isolated | **same** |

**Both predictors** (light Sonnet and strong Opus) produce a robustly **non-empty** non-redundant
surface — so the "not circular" finding is not a one-model fluke. But **neither stably isolates the
planted amlodipine → gingival-overgrowth confounder.** Opus put it #1 in an *isolated single* run,
yet across 5 runs + clustering it never cleared the 0.6 stability bar. So the plant is **intermittent,
not robust** — this is *not* "the light model missed it"; even the strong predictor doesn't surface it
reliably. The gate therefore does **not** reliably catch a *specific* planted gap. (The 9 Opus-surface
items are still good non-obvious gaps: smoking→Grade-C, smoking-suppresses-BOP, non-HDL as the better
marker, "even hs-CRP would be confounded here", missing BMI/demographics, no formal ASCVD score.)

## A — Behavioral validation: grounding the non-redundant gaps did NOT help

Grounded the 7 v2-surface gaps into the executor input; measured base vs grounded on the planted case:

| metric | base | grounded | Δ |
|---|---|---|---|
| counterfactual `mean_affected_delta` | **+0.33** | **−0.33** | **−0.67** |
| counterfactual `sensitivity_rate` | 0.00 | 0.00 | 0.00 |
| `relational_recall` | 0.625 | 0.500 | **−0.125** |
| `guardrail_pass` | False | False | — |

**VERDICT: `grounding_neutral_or_negative`.** Injecting the non-redundant gaps **degraded** both honest
metrics: the counterfactual affected-delta flipped from the correct direction (+0.33) to the wrong one
(−0.33), and relational recall fell. Plausible mechanism: appending a 7-item checklist (ASCVD score,
BMI, non-HDL, demographics…) **dilutes** the core oral-systemic mediating reasoning and pulls the model
toward the injected checklist instead of the present factors — so the axes become *less* responsive to
the actual factors. **Non-redundant did not become useful.**

## Combined bottom line

Across A + B the mode-4 "predict Opus's workspace with another model" approach:

1. **Clears the circularity bar (robustly).** An uncommitted external predictor surfaces genuinely
   non-redundant, non-obvious content the output (O) and a lean blind (C) both miss — including a
   **meta-critique of the output's own reasoning** that O cannot self-report. Confirmed with two
   different predictors (surface 7 and 9). The v1 "circular" was a harness artifact.
2. **Fails the specific-plant test.** Neither predictor stably isolates the amlodipine plant — it is
   intermittent, so the gate cannot be trusted to catch a *particular* gap.
3. **Fails the usefulness bar (the payoff).** Grounding the non-redundant gaps does not improve the
   honest metrics and slightly hurts them. **Non-redundant ≠ useful** — the exact mechanism/usefulness
   gap the [`skill-vs-mechanism-optimizer-reframe.md`](skill-vs-mechanism-optimizer-reframe.md) and
   [`lens-non-redundancy-burden-of-proof.md`](lens-non-redundancy-burden-of-proof.md) analyses predicted.

So the "predicted workspace" is a **real, non-redundant signal** — the burden-of-proof reversal was
vindicated at the *signal* level (it is not circular; it points off the output plane) — but on this
task, **through this actuator (append-as-checklist), it does not pay off.** This is consistent with the
whole investigation: the workspace signal, in every form we tried (self-report, Qwen-idea, Fable/Opus
prediction), is interesting and non-redundant, yet has not been shown to *improve outcomes* over a
strong blind baseline through the mechanisms available to us.

## Honest caveats (why A is suggestive, not definitive)
- **n = 1** for A (one planted case × 3 counterfactual flips): the −0.67 delta is noisy; a single case
  can flip it.
- **Crude actuator.** The burden-of-proof doc §5(b) called for a **free actuator** (an edit space that
  acts *differently* on the signal), not "append the gaps as text." Append-as-checklist is the weakest
  possible grounding and plausibly the reason it hurt (dilution). A per-item, targeted grounding (each
  gap drives a specific input edit, gated behaviorally) is the untested stronger version.
- **Guardrail False in both arms** — a separate issue with this planted case's format (it doesn't carry
  the deterministic missing-data directive), not caused by grounding.

## Where this leaves it
The honest, defensible position after the full mode-4 arc: the workspace/lens signal (inferred,
predicted, or — untested — measured) is **non-redundant but not yet shown to be useful** for
optimization through our actuators, on our (largely re-derivable) task. The two open doors that could
still change the verdict, both flagged repeatedly and both unrun: (a) a **free/targeted actuator** at
**n ≥ 30** on a **non-obvious-gap** task; (b) the **measured** lens (the API feature) removing the
inference/rationalization layer entirely. Absent those, the evidence says: real signal, no payoff.
