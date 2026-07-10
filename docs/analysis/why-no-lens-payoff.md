# Why the lens gives "extra insight" yet never pays off — and whether two proposals change that

> Fable analysis, 2026-07-10. Reconciles the tension between the paper (the lens should give
> additional insight) and the project's null (no evolution payoff), formalizes the Phase-2 boundary
> condition information-theoretically, and gut-checks two proposed escapes. Grounded in
> [`RESEARCH_SUMMARY.md`](../RESEARCH_SUMMARY.md) §0/§6b and
> [`phase2-fair-lens-retest.md`](phase2-fair-lens-retest.md).

## 1. Reconciliation — three different "values," and exactly where the chain breaks

"Insight into the model's internal computation" silently bundles three distinct quantities. Let
`L` = lens/workspace readout, `Y` = target property (output quality), `I` = input, `O` = output,
`K_R` = the *reader's* own knowledge/competence, `E*` = the optimal edit.

- **(a) Information-theoretic non-redundancy — PROVEN, and all the paper's "extra insight" strictly
  entails.** `NR = I(L ; Y | I, O) > 0`. The workspace carries information about the computation
  beyond what `I` and `O` jointly reveal (sharpest proof: an uncommitted read flags inconsistencies
  in the output's own reasoning that the output cannot self-report). A property of *information
  existing*, conditioned only on `I, O`.
- **(b) Monitoring / readout value — DEMONSTRATED by the paper.** A decoder exists from `L` to a
  property: self-report, single-token causal steering, deception/shortcut detection. Every one lives
  where the consumer *structurally cannot get the property another way* — self-report reads a state
  no external observer sees; steering acts causally *inside* the model; deception-detection fires
  precisely when `O` is adversarially misleading (so reading `O` fails by construction).
- **(c) Actionable-optimization value — NEVER demonstrated; what the project kept testing.**
  `OV = I(L ; E* | I, O, K_R)` plus an actuator that beats a competent blind baseline.

**The chain breaks between (a)/(b) and (c), and the break is the extra conditioning term `K_R`.**
Non-redundancy conditions on `{I, O}`; optimization value conditions on `{I, O, K_R}`. The program
measured `I(L; Y | I, O) > 0` and implicitly assumed it transfers to `I(L; E* | I, O, K_R) > 0`. It
does not, because for a **frontier reader on an in-competence task, `K_R` is enormous and screens off
`L`**:

> `I(L; Y | I, O) > 0` (non-redundant with the output) **but** `I(L; Y | O, K_R) ≈ 0` (no marginal
> once a competent reader's own knowledge is in the conditioning set).

That is the **Phase-2 boundary condition, restated information-theoretically.** The lens is
non-redundant with the *output*; it is redundant with *(output + a competent reader's prior)*.
Phase-2 v2 measured it directly: Opus blind caught 0.96 of subtle defects because its own competence
adjudicates a 3–4× wrong ΔCRP or a TNF-vs-IL-6 swap; the one crack (`wrong_dominant_factor`, blind
0.8) is the single defect whose truth is an *arbitrary parameter of the constructed model, not in
`K_R`*. Value survives only where `K_R` is empty.

So both statements are true without contradiction: the paper's uses (a, b) all sit where the reader
genuinely lacks `K_R` (introspective access; internal causal access; corrupted `O`); the project's
optimization tasks sit in the opposite regime — a maximally competent reader (**forced to Opus
because Fable refuses the medical read**) on a re-derivable task inside its competence. The lens
carries extra information; that information is only *actionable* where the reader cannot otherwise
obtain it; the project systematically put the reader where it can. The Fable refusal is not
incidental — it *guarantees* the max-competent-reader regime where the marginal collapses.

## 2. The two proposals

### Proposal A — lens across a design space (config selection, not optimizer)
**Verdict: RESHAPE for a measured-lens rig only; CUT on Claude-only (expected value ≈ 0).**

Precisely: over `K` configs with ground-truth quality `Q_c`, does the lens predict the ranking? The
quantity is the *marginal over a competent output read*: `Δ_A = I(L_c ; Q_c | O_subsample_c, K_judge)`
(≡ top-1 selection accuracy or Spearman of a lens-ranker minus an output-ranker). This is the
**boundary condition at coarser granularity** — config selection is optimization aggregated over
items; comparing configs *by their outputs* keeps the same `K_R` screening. Two escapes, neither on
Claude-only: **cost-asymmetry** (lens cheaper than full eval → valid cheap early-stop — but the
Claude lens is *inferred* = another Opus call, no cheaper) and **starved baseline** (weak judge →
tautological). So A only exists folded into B's measured-lens rig; on Claude it re-runs Phase-2 with
more machinery.

### Proposal B — Qwen measurement rig, then transfer to Claude
**Verdict: RESHAPE. KEEP (i)+(ii) as scoped Qwen premise-validation; CUT (iii).**

- **(i) Validate `I(L_measured ; Q | prompt, output) > 0` on Qwen** — the single measurement the
  project lacks (every Claude result uses an *inferred* proxy). Two constraints reshape it: (1) the
  prior finding "measured single-token Qwen lens is blinder than self-report on multi-token
  mediators" forces **single-token-discriminator tasks** (else it nulls for the wrong reason —
  measurement impoverishment); (2) `Q` must be **process-correctness on shortcut/anchoring tasks
  where `O` is misleading** (else a competent judge recovers `Q` from `O` and the boundary bites even
  on Qwen). Correctly scoped, this is the paper's **monitoring** use with a *real* lens — plausibly
  positive and genuinely meaningful. Estimate via Spearman + a lightly-fit logistic probe with a
  permutation test.
- **(ii) Learn the (prompt, lens, output) → quality map on Qwen** — a cheap supervised probe; the
  estimator for (i) made explicit. Fine.
- **(iii) Replicate the component in Claude via a second model reading the scenario — CUT.** The map
  learned in (ii) is a function *of the measured lens* `f(L_measured)`; Claude exposes **no**
  `L_measured`. A "second Claude reading the scenario" can only consume `(prompt, output)` → it
  *infers* a lens = definitionally the **inferred-lens Observer**, which already returned
  `lens_inconclusive` (relational +0.104, CI [−0.042, +0.229]) and which Phase-2 showed does not beat
  blind. **Transfer is not under-powered; it is undefined** — the input variable does not exist in
  Claude. Substituting `L_inferred` for `L_measured` re-runs the refuted approach with extra steps.

## 3. Complementarity & sequencing
A and B converge on one point: A's only real escape (cost-asymmetry early discrimination) *requires a
measured lens*, which is B's rig — so there is no independent Claude-only A worth running.

1. **B(i) first** — ~1 GPU-day, Qwen shortcut tasks, single-token discriminator, `Q_process` label,
   permutation-test significance. The *only* experiment in either proposal that injects genuinely new
   information (a real measurement) rather than Opus-reads-Opus; retires the "no ground truth for the
   lens" caveat either way. (Scaffold exists: `probes/qwen_correlation_probe.py`, GPU-gated, never run.)
2. **A only in measured-lens form, on B's rig, and only if B(i) is positive.**
3. **B(iii): never** (no transfer vehicle).

Everything Opus-reads-Opus on Claude (A-on-Claude, iii) is dominated by the boundary condition and
should not consume live spend. B(i)/(ii) run on Qwen — no Claude reader, so the Fable refusal is
irrelevant there.

## 4. Honest bottom line
**Neither proposal has a realistic path to overturning "no demonstrated optimization payoff over a
strong blind baseline on Claude," and where either shows a positive, that positive is narrow or
tautological.** The boundary is structural, not an experimental gap: a frontier reader on an
in-competence task screens off the lens (`I(L;Y|O,K_R)≈0`). Green appears only by **(a) weakening/
starving the baseline reader** (the lens helps a *weak* reader — which the boundary already predicts)
or **(b) redefining quality as process-correctness on shortcut tasks where `O` is misleading**
(Proposal B(i)). Move (b) is worth doing, but a positive validates the paper's **monitoring** claim on
a *weak model with a real lens* — it does not demonstrate optimization and does not transfer to Claude.

**What would genuinely overturn the null**, and nothing short of it: (1) the **measured** Jacobian
lens on **Claude** via the API (removes the inferred under-powering *and* lets you test tasks Claude
is *not* competent at); (2) a task genuinely **outside the reader's competence** (arbitrary/computed
model-specific quantities, or adversarial shortcut outputs where `O` is corrupted); (3) a **real
per-item actuator** (targeted, not append-as-checklist which actively hurt) at **n ≥ 30** with the
CIs already in `ablation.py`. Absent measured-lens-on-Claude, every Claude experiment reduces to
Opus-reads-Opus, which the boundary resolves before a token is spent. Run **B(i)** as the one honest
measurement the project is missing; treat a positive as **monitoring-validation, not a crack in the
null.**
