# QA-monitor live result (Path A, v1) — planted case

> Run 2026-07-09. `src/run_qa_eval.py --cases planted`. Executor/monitor/blind = Opus 4.8, judge =
> Sonnet 5. Report: `results/qa_monitor_report.json`. This is the first live run of the monitor path.

## Numbers

| | monitor | blind | delta | CI90 |
|---|---|---|---|---|
| recall on injected defects (n=4) | **1.00** | **1.00** | **0.00** | [0.00, 0.00] |
| control FP rate (n=1) | **1.00** | **1.00** | — | — |

Per class (each n=1): internal_contradiction, inconsistent_confidence, unsupported_claim,
silent_omission — **all 1.00 / 1.00**. Verdict: **`monitor_inconclusive`**.

## Honest read — the experiment did NOT discriminate, and here is why

This is **not** evidence the monitor helps, and **not** a fair refutation either. Two design faults,
both visible in the numbers:

1. **Ceiling effect — the injected defects are too blatant.** The blind "any problems?" read caught
   all four, so there is **zero headroom** for the off-plane monitor to beat it. The hypothesis (a
   reasoning-audit read catches defects a blind read misses) can only be tested with defects a blind
   read *plausibly misses* — subtler corruptions, not a high-confidence-with-no-evidence axis that any
   reviewer flags on sight.
2. **The control is contaminated.** FP = 1.00 for *both* arms because the single control is the
   **planted amlodipine case**, whose clean output legitimately has something to flag (the
   drug-tissue confounder / medication-review gap). A planted-confounder case is a bad "clean"
   control by construction. Genuine clean controls must be defect-free NHANES outputs.
3. **n = 1 case / 4 defects / 1 control** — statistically nothing regardless.

## What this does and doesn't change

- **§0 verdict is untouched.** No detection payoff demonstrated; the optimizer claim stays dead.
- The path is **not refuted** — it was under-powered and mis-controlled on the first pass. The
  apparatus works (injectors, monitor, blind, judge, CI all ran end-to-end on live Opus); the
  *stimulus set* was wrong.

## The fix (v2, if pursued)

- **Subtler defects:** corrupt in ways a blind skim misses — e.g. a confidence one notch too high
  (medium→high) rather than high-with-empty-evidence; an omission of a *second-order* mediator, not a
  critical one; an unsupported claim phrased plausibly. Keep the non-redundant `inconsistent_confidence`
  class but make the two axes' evidence subtly (not identically) matched.
- **Clean controls from NHANES:** run `--cases nhanes --n ≥ 8`; use each case's *uncorrupted* Opus
  output as the clean control, and inject into copies. That gives real clean controls + more injected
  items → a CI with power.
- Only then does monitor_recall − blind_recall at matched FP mean anything.

**Bottom line:** the monitor read is at least as good as blind (caught everything), but on defects this
obvious that is worthless as evidence. The v1 run proves the harness, not the hypothesis. A powered v2
with subtler defects and clean NHANES controls is the honest next step — and remains the one path that
could upgrade the headline to a *demonstrated detection* payoff.
