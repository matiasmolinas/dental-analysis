# Does the Inferred Lens Do Causal Work? An Honest Read of the Three-Arm Ablation

> Produced 2026-07-09 with the **Fable** model. Scope: live Claude Sonnet-5 run, n=4 real
> NHANES participants, `results/ablation_report.json`. Arms (`src/ablation.py` /
> `src/run_ablation.py`): **A** = naive abbreviated table; **B_blind** = a converger
> using only general expertise; **B_lens** = the *same* converger also handed the
> inferred-lens readout + the Observer's deficiency map. The only difference between the
> B arms is the lens signal. No cheerleading. Companion to
> [`is-the-lens-working.md`](is-the-lens-working.md) and [`../REFORMULATION.md`](../REFORMULATION.md) §R5.

## 1. What the ablation actually shows about the lens

**The one honest sentence:** at n=4, B_lens beats B_blind on mechanism-recall by
**+0.094 aggregate (0.906 vs 0.813)**, wins 2 cases, **loses 1**, ties 1, and shows
**zero** difference on either guardrail-axis metric. A weak directional hint, not evidence.

Decompose the "win" (recall is 8 mediators per case):

| case | B_blind hits | B_lens hits |
|---|---|---|
| 0 | 6/8 | 8/8 |
| 1 | **7/8** | **6/8** (lens worse) |
| 2 | 6/8 | 8/8 |
| 3 | 7/8 | 7/8 (tie) |
| **total** | **26/32** | **29/32** |

The entire aggregate edge is **3 extra mediator substring-hits across 4 cases** — and one
case moved the *wrong* way. A single case flipping would erase or invert the delta. No
CIs, no repeated samples, no temperature-variance control; each cell is one generation.

**On the `lens_adds_value` label:** it is a *noisy label, not a signal*. The verdict rule
(`ablation.py`) fires on **any** strict gain on **any** axis with no aggregate regression —
so it triggers on a **sub-0.1 mean difference with no significance test**. The 2-win /
1-loss / 1-tie split is what noise around a near-zero true effect looks like. This run
does **not** establish that the inferred lens adds value over blind convergence; it fails
to *reject* that hypothesis, which is weaker.

## 2. The guardrail-axis finding — the most informative result here

Both B arms score **0.00** on `missing_data_flagged` and **0.00** on `guardrail_pass_rate`,
identical to naive A. Every case is `missing_data_raw: [0, 1]` — one mediator truly
absent, **no arm flags it**. `traceability_ok` is `true` everywhere, so the guardrail
fails solely on the unflagged missing field. This is quietly damning for the lens thesis:

- R5's hardcoded B reached **guardrail 1.0 (6/6)** — but from the deterministic
  `build_inputs` **data-completeness directive** ("add EVERY `missing_mediators` field…"),
  a string pasted verbatim. That win was **the directive, not the lens.**
- Here both convergers are *told* (soft prose in `CONVERGE_SYSTEM`) to flag absent data,
  yet their free-form prose **fails to make the evaluator populate `required_missing_data`**
  — the flag doesn't survive the prose→structured-output hand-off. Free-form convergence,
  blind *or* lens-guided, **loses the reliability the deterministic directive guaranteed.**

The value on the guardrail-critical axis lives in the **deterministic harness/directive**,
not in lens-guided prose and not in the lens. On the axis §R5 called the real lever, the
lens contributes nothing, and free-form generation is *strictly less reliable* than a
hardcoded directive. The opposite of a lens win.

## 3. Is the ablation itself fair / well-posed?

A genuine attempt at the right comparison, but three choices limit it:

**(a) Recall by substring-matching is a weak proxy.** `mechanism_recall` counts a mediator
as recovered if any surface form appears anywhere in the output — **vocabulary presence,
not reasoning**. Naming "endothelial dysfunction" scores like reasoning about it.

**(b) The convergers should have received the data-completeness directive.** The biggest
gap. R5's guardrail result rode on that directive; it was withheld from both B arms here,
so the guardrail axis collapsed to 0.00/0.00 and **the lens was never actually tested on
the axis where value was previously demonstrated.**

**(c) Converger variance, single model, n=4.** One model as executor, converger, *and*
evaluator (Claude grades Claude); one day; one sample per cell; four random participants.
A scores an identical 0.625 in **all four cases** — suspiciously flat. No noise floor to
place the +0.094 against.

**Fixes for v2:** (1) n ≥ 30 with k ≥ 3 generations/cell + CIs; (2) give **both**
convergers the deterministic directive so the lens is testable on the guardrail axis;
(3) replace substring recall with a rubric scoring *relational use* + traceability;
(4) use a **separate** evaluator model; (5) add a significance/bootstrap rule so
`lens_adds_value` can't fire on sub-noise deltas.

## 3.5 Confounds specific to this run

- **Recall ceiling.** A already sits at **0.625 (5/8)** unaided; only 3 mediators of
  headroom, and B_blind alone captures most (0.813). The lens competes for a **tiny
  residual (0.813 → 1.0)** — a metric this saturated can't show a large causal effect.
- **Metric-artifact risk is live.** Plausible mechanism for the 3-hit edge: the deficiency
  map *names* the faint mediators → the converger **injects that vocabulary** → the
  substring metric mechanically rewards its reappearance. A closed lexical loop (lens
  names term → converger echoes → output repeats → metric counts) that yields a small
  positive recall delta **with no reasoning improvement**. The lens moved *only* the
  vocabulary-sensitive metric (recall) and *not at all* the semantic guardrail metric —
  more consistent with the artifact than with real reasoning gains.

## 4. Verdict + next steps

**Bottom line for a hackathon judge.** The right experiment, run honestly — and it does
**not** demonstrate the Jacobian-lens thesis. The only pro-lens number is a **+0.094
aggregate recall edge at n=4 (2 win / 1 loss / 1 tie)** on a substring metric that
plausibly rewards the lens for merely *naming* mediators the converger echoes, with no
significance behind the label. On the axis that mattered in R5 (missing-data flagging /
non-imputation) the lens shows **exactly zero** effect, and both free-form arms *lost* the
guardrail reliability (1.0 → 0.0) the deterministic directive had provided — relocating the
demonstrated value in the **harness/directive**, not the lens. Demonstrated: a
well-structured converged input beats naive (B_blind 0.813 vs A 0.625) — the
prompt-engineering result already known from R5. **Not** demonstrated: that the inferred
lens does causal work over blind convergence. Credit the engineering; reserve judgment on
the lens.

**Prioritized next steps:**
1. **Larger n (≥30) with repeated samples per cell + CIs** — the single most important
   fix; without it the +0.094 is uninterpretable.
2. **Give both convergers the data-completeness directive** so the lens can finally be
   tested on the guardrail axis (today both arms 0.00 → structurally untestable).
3. **Better recall metric** — score relational *use* + traceability, not substring
   presence, to kill the name-echo artifact; use a separate evaluator model.
4. **Implement the counterfactual-sensitivity runner** (still prose-only) — flip a
   mediator present↔MISSING and confirm the dependent axis moves and unrelated axes don't.
   Tests *reasoning*, not vocabulary — the honest corroboration self-report needs.
5. **Frame the measured lens as the real unlock** — on this evidence the inferred
   (self-report) signal is at best a small vocabulary nudge; the thesis's payoff depends
   on measured-lens access, which should be the forward claim, not implied by this run.
