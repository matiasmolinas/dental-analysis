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

---

## v2 result — subtle defects + clean NHANES controls (n=8 cases, 32 injected)

> Run 2026-07-09. `src/run_qa_eval.py --cases nhanes --n 8 --defect-mode subtle`. Same roles.
> Report: `results/qa_monitor_v2_report.json`.

| | monitor | blind | delta | CI90 |
|---|---|---|---|---|
| recall on injected (n=32) | **0.59** | **0.56** | **+0.03** | **[−0.125, +0.19]** (straddles 0) |
| control FP rate (n=8) | 1.00 | 1.00 | — | — |

Per class (n=8 each): `inconsistent_confidence` 0.50 vs 0.375 (**+0.125**); `overconfidence` 0.875 vs
0.75 (**+0.125**); `unsupported_claim` 1.00 vs 1.00 (ceiling); `silent_omission` 0.00 vs 0.125.
Verdict: **`monitor_inconclusive`**.

### Honest read (v2)

1. **The global headline does NOT move §0.** +0.03, CI [−0.125,+0.19] — no demonstrated monitor
   advantage at n=32. The overall claim stays inconclusive.
2. **But the per-class pattern is directionally consistent with the theory.** The monitor beats blind
   in *exactly* the two reasoning-audit classes (overconfidence and the non-redundant
   `inconsistent_confidence`, +0.125 each), ties at ceiling on `unsupported_claim`, and neither catches
   `silent_omission`. The non-redundant class — the one the paper predicts is the workspace's strength
   — shows the largest edge. **n=8/class is underpowered**; the per-class effect is not yet significant.
3. **control FP = 1.00 for both is a metric artifact, not signal.** "FP = flagged *any* problem on the
   clean output" is saturated: real Opus clinical outputs have genuine imperfections, so both reads
   always say something. A meaningful FP needs to be **type-matched** (did the read flag a defect *of
   the injected class* on a clean control?) or a flag *count*, not binary.
4. **`silent_omission` 0.0/0.125 exposes a design fix.** Neither read can catch an omission without
   knowing *what should be present*; the monitor needs the required-mediators spec (like `spec_text`
   in `ablation.py`) to detect a dropped collection flag.

### What a decisive v3 would need
- **Type-matched FP metric** (count / class-matched), replacing the saturated binary any-flag rate.
- **Power concentrated** on the two classes where the monitor plausibly helps (drop the ceiling and
  floor classes; more cases on `inconsistent_confidence` / `overconfidence`).
- **Spec-grounded monitor** for the omission class (pass the required-mediators spec).

**Bottom line (v2):** honest inconclusive overall — no demonstrated monitor advantage — but the run
*localizes* where any advantage lives (the confidence-reasoning classes, i.e. the non-redundant
channel) and shows two of the four defect classes are the wrong test (one saturates, one needs a
spec). This is a better-characterized negative, not a payoff. §0 stands: **no demonstrated detection
advantage of the off-plane monitor over a blind read.**
