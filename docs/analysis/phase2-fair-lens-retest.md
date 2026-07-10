# Phase 2 — the fair lens re-test on the mechanistic task

> The honest closure of the §0 investigation (see [`../RESEARCH_SUMMARY.md`](../RESEARCH_SUMMARY.md)).
> The §0 null ("real, non-redundant signal; no demonstrated payoff") had a most-likely cause:
> the NHANES task didn't require mechanistic reasoning, so there was no headroom for reading the
> workspace to help. Phase 1 built a task that does. Phase 2 re-runs the monitor on it — with the two
> possible payoffs held apart so the answer can't be a confound.

## The three arms (why they are separate)

On a mechanistic task, two different things could beat a blind read, and conflating them would repeat
the exact mistake the project has been disciplined about:

- **`blind`** — generic "any problems?" read (control).
- **`reasoning_monitor`** — audits the *mechanistic reasoning*, **no model tool**. This is the
  **lens thesis** at reasoning depth: does reading/auditing the reasoning help when the task needs it?
- **`model_grounded`** — same audit **plus the calibrated centerpiece's numbers as an oracle**. This
  is the **harness thesis**: does having the model as a checker help?

A win for `model_grounded` but not `reasoning_monitor` would say the payoff is **the model (a tool)**,
not reading the workspace — consistent with the whole arc (the project's wins were deterministic/tool,
not the lens). A win for `reasoning_monitor` over `blind` would be the first evidence that auditing
reasoning helps once the task has mechanistic headroom.

## v1 result — directional-reversal defects (ceiling, inconclusive)

> `run_mech_monitor.py` (blatant). 5 structural cases × 5 defect classes = 25 injected, 5 controls.
> Readers = Opus; judge = Sonnet. Report: `results/mech_monitor_report.json`.

| | blind | reasoning_monitor | model_grounded |
|---|---|---|---|
| recall (n=25) | **1.00** | **1.00** | **1.00** |
| control FP (n=5) | 1.00 | 1.00 | 1.00 |

All five classes at 1.00/1.00/1.00; Δ vs blind = 0 (CI [0,0]) for both theses → **inconclusive, no
separation.** The v1 defects were **directional reversals** ("therapy *raises* CRP", "CRP *is* the
cause", "higher BOP *lowers* inflammation") — a competent blind read catches them on sight. Same
ceiling as Path A v1: the apparatus (3 arms + oracle + judge) ran end to end, but the stimulus had no
headroom.

### The sharpening this forces
The *discriminating* defects on a mechanistic task must be **quantitative** — same direction, wrong
**magnitude / attribution / width** — because those are precisely the errors a blind read **cannot
adjudicate without the model**, while the `model_grounded` oracle can. That is not a patch; it is the
point: quantitative mechanistic error is the stimulus that both creates headroom *and* separates the
lens thesis from the harness thesis by construction.

## v2 — subtle quantitative defects (the decisive design)

> `run_mech_monitor.py --defect-mode subtle`. Same arms/roles. Report: `results/mech_monitor_v2_report.json`.

Five quantitative mechanistic defects, each same-direction / plausible / number-wrong:
- **`magnitude_therapy`** — therapy lowers CRP (correct) but by a 3–4× wrong ΔCRP (only the oracle
  knows the number).
- **`subtle_causal_attribution`** — names TNF-α (a real cytokine) as the principal CRP driver instead
  of IL-6 (mechanism knowledge or the kernel settles it).
- **`wrong_dominant_factor`** — ranks smoking (×1.25) above diabetes (×1.40) as the dominant amplifier
  (only the amplifier values settle it).
- **`overstated_confidence_subtle`** — upgrades the flagged neuro scaffold to "moderate empirical
  support / probable quantitative link" (one notch, not a blatant "established law").
- **`narrow_range`** — a ±0.05 CRP interval vs the true ε-driven spread (only the ε sweep knows the width).

**Prediction (to be tested, not assumed):** `model_grounded` should beat `blind` on the
magnitude/width/ordering classes (it has the numbers); `reasoning_monitor` should help only where
mechanism knowledge alone suffices (causal attribution). If that pattern holds, the honest headline is
**"the payoff is the model, not reading the workspace"** — and §0 stands for the lens while the
mechanistic harness earns a demonstrated detection payoff of its own.

### v2 result (2026-07-09)

> `run_mech_monitor.py --defect-mode subtle`. 25 injected, 5 controls. Report:
> `results/mech_monitor_v2_report.json`.

| | blind | reasoning_monitor | model_grounded |
|---|---|---|---|
| recall (n=25) | **0.96** | **1.00** | **1.00** |
| control FP (n=5) | 1.00 | 1.00 | 1.00 |
| Δ vs blind | — | +0.04, CI90 **[0.0, 0.12]** | +0.04, CI90 **[0.0, 0.12]** |

Per class: `magnitude_therapy`, `subtle_causal_attribution`, `narrow_range`,
`overstated_confidence_subtle` all **1.0 / 1.0 / 1.0**; only `wrong_dominant_factor` cracked —
blind **0.8**, both others 1.0. Both verdicts: **inconclusive** (CIs touch 0, no significant
separation).

### The real finding — and it generalizes §0

Even *quantitative* subtle defects are **near-ceiling for a strong blind reader**: Opus reading the
output alone caught ~96%. It did **not** need the reasoning-audit framing or the model oracle —
because **Opus already possesses the mechanistic competence to adjudicate these claims** (a 3–4×
wrong ΔCRP, a TNF-vs-IL-6 mix-up, an overstated confidence, a too-narrow interval are all things a
capable oral-systemic reasoner flags from its own knowledge). When the reader is already competent at
the task, blind ≈ reasoning_monitor ≈ model_grounded — there is no gap for the workspace or the oracle
to fill.

**The one crack is the tell.** `wrong_dominant_factor` — smoking (×1.25) ranked above diabetes (×1.40)
— is the only defect whose ground truth is **an arbitrary parameter of OUR constructed model, not a
fact in the reader's prior knowledge.** That is exactly the class where blind dipped (0.8). It
localizes where *any* monitor/oracle advantage can live: **content not already in a capable reader's
prior** — arbitrary/computed model-specific quantities — never general mechanism facts.

This sharpens and generalizes the §0 verdict into a precise, falsifiable boundary condition:

> **The workspace / lens / model-oracle adds value only where the reader lacks the knowledge to
> adjudicate the output** — a weaker reader, or genuinely novel/arbitrary content. On any task within
> a strong model's own competence, reading its workspace (or handing it an oracle) does not beat
> simply reading its output with a capable model. That is why the whole lens-as-optimizer/detector
> program keeps returning inconclusive: the tasks live inside the model's competence.

### Verdict

- **Lens thesis (reasoning_monitor > blind):** not demonstrated. Δ+0.04, CI touches 0. Reading/auditing
  the reasoning does not beat a competent blind read on a task the reader is already good at.
- **Harness thesis (model_grounded > blind):** not demonstrated *here* — for the same reason: the
  reader didn't need the oracle for defects it already knows. The oracle's genuine advantage would only
  appear on model-specific arbitrary quantities the reader cannot know (the `wrong_dominant_factor`
  regime), which is a **tooling** result (a calculator beats a guesser on arithmetic the guesser can't
  do), not a "reading the workspace optimizes a capable model" result.
- **§0 stands**, now with a mechanism for *why*: no headroom when the reader is competent.

### Should there be a v3?
A v3 could concentrate exclusively on **model-specific arbitrary/computed quantities** (values the
reader provably cannot know without the oracle) to force `model_grounded` to separate from `blind`. It
almost certainly would — but that would confirm the near-tautology "a tool helps when it holds
information the reader lacks," a **tooling** finding, not a lens finding, and not worth more live spend.
The honest close: **Phase 2 answered the §0 question.** The lens/monitor does not beat a competent
blind reader on tasks within its competence; any advantage requires the reader to lack the knowledge,
which is the weak-reader / novel-content regime, not the "optimize a capable model by reading its
workspace" regime the program set out to demonstrate.
