# "Lens recipes" as Opus context — the deflationary truth, and the real buildable capability

> Fable analysis, 2026-07-10. Verdict on whether Fable-pre-generated "lens recipes" injected as
> on-demand Opus context are a new capability. Answer: **mostly W1 in a lens costume — but with one
> genuinely new, buildable target the original boundary condition never named.** Builds on
> [`validated-evolution-and-qwen-regime.md`](validated-evolution-and-qwen-regime.md),
> [`why-no-lens-payoff.md`](why-no-lens-payoff.md), and W1/F1 in [`../RETROSPECTIVE.md`](../RETROSPECTIVE.md).

## The refinement that decides everything: split K_R into *knowledge* vs *execution*

The boundary was written `I(L;Y|O,K_R)≈0`, treating `K_R` as *what the competent reader knows*. **W1
breaks that framing.** The load-bearing W1 fact: **free-form convergers handed the SAME missing-data
directive still fell to 0.00**, while the hardcoded deterministic injection went to 1.0. They *had the
content in context* and still didn't deploy it. So W1's payoff is **not** "content outside the prior."
It is content **inside** the knowledge-prior but **outside** the execution-prior. Split:

- `K_R^know` = what the model can state if asked.
- `K_R^exec` = what it *reliably deploys in situ under generation load*.

The payoff channel is the set difference **`K_R^know \ K_R^exec`** — steps the model **knows but
drops**. A deterministic recipe can externalize exactly this, and it was invisible to the original
boundary because that boundary conditioned on knowledge, not execution.

## Q1 — When a recipe pays (formal condition)

A recipe `R` for class `C` helps iff `I(R; E* | O, K_R_opus) > 0`. By content type:

| Recipe type | In `K_R^know`? | Deterministic/checkable? | `I(R;E*|O,K_R)` | Precedent |
|---|---|---|---|---|
| **R_struct** — enumerable/checkable step the model drops in situ | yes | **yes** | **> 0** (execution gap) | **W1** |
| **R_ext** — externally-validated fact the model lacks | no | n/a | **> 0** (knowledge gap) | Track-2 / eval-anchored |
| **R_sem** — semantic judgment the model both knows and applies | yes | no | **≈ 0** (screened; can hurt) | F1 append-all; all Opus-reads-Opus nulls |

Exactly **two** ways to get `> 0`, both already in the project: the **execution gap** (W1 — a
deterministic, verifiable, structural step the model can't reason past) and the **knowledge gap**
(inject externally-validated data). The "lens" is only a **source of candidate content**, never a new
mechanism. Everything semantic collapses to the screened checklist (null, and F1 shows it can hurt).

## Q2 — Is the Qwen measured lens load-bearing for recipes? **Ornamental.**

The paying recipe content (`R_struct`, `R_ext`) is not discoverable by measuring Qwen's workspace:
- **`R_struct` is population-mismatched** — a Qwen lens reveals *Qwen's* dropped steps; the recipe must
  target *Opus's* `K_R^know \ K_R^exec`. Different models drop different steps. The correct discovery
  method is **error analysis of Opus's own transcripts** (states the step on demand, omits it in situ).
- **`R_ext` comes from data**, not internals.
- The one lens-only signal (silently-considered-vs-never-considered) is **reader-specific** — Qwen's
  tells you nothing about Opus's.

Whatever a Qwen lens names, you must **A/B it on Opus anyway** — the A/B is necessary and sufficient;
the Qwen provenance is neither. So Fable-brainstorming is a fine candidate *generator*; the measured
Qwen lens **adds no content to the recipe path.** Qwen is load-bearing only for its *own* standalone
question ("does a measured lens carry signal for a weak reader") — real mechanism-closure, but **not
on the recipe critical path.**

## Q3 — The recipe A/B (and the pre-A/B predictor)

**Task class:** reuse the W1 apparatus — NHANES-style tasks with an *external/held-out* metric
(guardrail pass-rate, injected-defect recall, held-out association recovery). **Never** a model-judged
score (Opus-reads-Opus, screened).

**Three arms** (the third is the discriminator W1 demands):
- **Arm 0** — baseline, no recipe.
- **Arm 1** — recipe injected as **deterministic, enforced** context.
- **Arm 2** — the **same recipe as prose**, not enforced (the W1 control that fell to 0.00).

**Significance:** paired `ablation._bootstrap_ci`, 90% CI, **n ≥ 30**. **Adopt iff CI(Arm1 − Arm0)
excludes 0.** Read Arm 2 to classify *why*:

| Pattern | Interpretation |
|---|---|
| Arm1 > Arm2 > Arm0 | **execution-gap recipe (true W1 class)** — deterministic externalization does the work. *The genuine deliverable.* |
| Arm1 ≈ Arm2 > Arm0 | knowledge gap — the *content* helped, externalization didn't; just inject the fact. |
| Arm1 ≈ Arm2 ≈ Arm0 | **screened** (R_sem) — null; watch for F1-style harm. |

**Predictor, computable BEFORE the A/B** — classify each candidate on two axes: (1) **Known?** ask the
model to state the step blind; (2) **deterministic/checkable vs semantic?** Then:
- **known + deterministic + demonstrably dropped in situ** → **predict PAYS** (exec gap). *The
  "stated-on-demand-but-dropped-in-situ" test is the single strongest, cheapest predictor.*
- **not-known + external** → pays as content injection.
- **known + semantic** → **predict NULL** — don't spend the A/B.

One sentence: **a recipe pays iff it is a deterministic step the model omits in situ despite being able
to state it, or carries an externally-validated fact it lacks.**

## Q4 — What to build

**Not a "lens recipe library" — a library of externally-validated / deterministic-structural context
directives (W1 generalized to the execution gap).** Each admitted only if its A/B CI separates *and* it
beats the prose-handoff control (proving the *externalization*, not just the content, is load-bearing),
with candidate yield predicted in advance by the exec-gap/knowledge-gap classifier. **Fable is a fine
candidate generator; do not gate anything on the Qwen measured lens** — run Qwen purely as standalone
mechanism-closure, decoupled from this deliverable.

The genuine novelty, stated plainly: **W1 was not luck.** It is one instance of a generalizable
mechanism — *externalize a known-but-unreliably-executed structural step* — and the execution gap
`K_R^know \ K_R^exec` is a real, buildable target the boundary condition (as first written) didn't name.
That is the honest positive to build on, alongside Track-2's data-anchored knowledge gap.
