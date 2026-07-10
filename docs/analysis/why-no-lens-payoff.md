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

## 5. Addendum — the "negative-space probe" refinement (2026-07-10)

A follow-up proposal: keep Opus-reads-Opus but make the difference come from **the probe prompt** —
design it to surface the **run-specific alternatives the forward pass did NOT activate** (the negative
space), which the output can't show; and optimize that probe as a pure meta-task (no biology/safety →
Fable can be the optimizer, sidestepping the forced-Opus point). **Verdict: NO — the boundary
re-encountered at trajectory granularity — but it names a real, previously-unnamed residual.**

- **Q1 (absence vs enumeration).** Generic enumeration `E` = {plausible alternatives} is pure `K_R`
  (a competent model brainstorms it with no lens). The content quantity `I(L; A_missed_this_run |
  O, K_R) > 0` is real but is **non-redundancy (a) restated at trajectory level, not a new door.**
  The **actionability collapse:** the optimal edit injects the alternatives that *matter* (`M ⊆ E`,
  pure `K_R`), not the ones the run *missed*. The lens's only marginal is a **negative filter** —
  distinguishing *never-considered* (worth injecting) from *silently-considered-and-discarded* (the
  model already killed it; re-injecting dilutes, cf. F1). That residual — `I(L;
  {activated-but-absent-from-O} | O, K_R)` — is the entire door, and it is expected small.
- **Q2 (confabulation vs readout) — the strongest strike.** Self-report of **absence** is categorically
  weaker than self-report of presence; the paper's reportability-is-causal result covers *activated*
  content, and there is **no evidence introspection extends to counterfactual non-activation.** Asked
  "what did I miss," the model re-derives `E` from `K_R` and subtracts what it notices in `O` — i.e.
  returns the `K_R` baseline. **The confabulated answer IS the boundary condition,** and you can't tell
  readout from confabulation without a measured lens.
- **Q3 (validation).** Optimizing a probe "toward the real lens" needs a target Claude lacks →
  collapses to **(a) Qwen ground truth = B(i) with extra steps**, or **(b) downstream payoff =
  boundary-screened.** Paraphrase-stability tests reliability, not validity; steering-consistency *is*
  the measured lens. **No third route.**
- **Q4 (the one survivable on-Claude test).** `src/run_targeted.py`'s `targeted` arm currently
  **fuses lens + K_R** (predictor surfaces gaps, selector picks) and **lacks a lens-free control.** The
  clean test adds **`brainstorm_targeted`** (a competent model brainstorms mattering, output-absent
  alternatives with **no lens**) as a third arm vs `lens_targeted` and `append_all`. Quantity
  `Δ = quality(lens_targeted) − quality(brainstorm_targeted)`, paired, `ablation._bootstrap_ci`,
  **n ≥ 30 out-of-competence** cases (else both ceiling). **Expected: Δ ≈ 0** — brainstorm matches lens,
  boundary wins; the only regime where lens could separate (out-of-competence) is self-defeating for
  self-report (a pass that couldn't enumerate the alternatives can't self-report missing them).
- **Q5 (Fable as optimizer).** Removes forced-Opus from the *meta-loop* (legitimate), but the boundary
  `I(L;Y|O,K_R)≈0` lives at the *object* level and is indifferent to who wrote the probe. **Relocated,
  not escaped.**

**Net:** the refinement isolates the only residual where an on-Claude lens could ever be actionable —
the **silently-considered-and-discarded set** — but its target is *absence* (least readable, most
confabulation-prone), it has no non-Qwen/non-payoff validation, and the clean 3-arm test's expected
result is `brainstorm_targeted ≈ lens_targeted`. The runnable slice (add the `brainstorm_targeted`
control to `run_targeted.py`, run out-of-competence at n ≥ 30) is worth doing **as the cleanest
possible demonstration that the door is painted on the wall** — a boundary confirmation, not expected
to open. **B(i)** remains the one honest missing measurement, now also the only way to test whether
"what did I miss" self-report is a readout at all.

## 6. Addendum — the SESSION-level lens (2026-07-10). Verdict: NO — boundary bites *harder*.

A further refinement: the boundary was argued at one-shot granularity; maybe a **multi-step session**
escapes it — ask the model to make explicit its Jacobian lens *across a whole session*, review that,
and consolidate (analogous to memory-trace analysis) to evolve prompts/skills/subagent-defs/harness.

**It inverts the geometry the wrong way for the lens.** A one-shot lens is the *only* carrier of the
trajectory because `O` is just the final answer. The moment a multi-step agent externalizes its
intermediate reasoning, tool calls, and discarded branches **as transcript text**, that content moves
*into the conditioning set* `O`. You are not opening a channel to the workspace — you are transcribing
the workspace into `O` and conditioning on it. With `O_transcript = g(H_{1:T})` and `L_session =
f(H_{1:T})` reading the *same* trajectory:

> `I(L_session ; Y | O_transcript, K_R) ≤ I(L_oneshot ; Y | O_oneshot, K_R) ≈ 0` — a **strict subset**
> of the already-≈0 one-shot residual. Externalization is exactly the operation that screens the lens
> *harder*.

- **Confabulation is worse, not better.** "Make explicit your session-level lens" = the model
  re-reading `O_transcript` and reconstructing a plausible trajectory `f(O_transcript, K_R)` —
  confabulation DOF scale with horizon, and the §5 Q2 strike (no introspective access to counterfactual
  non-activation) applies with *compound* force across `T` steps.
- **The value is the externalized TRACE, not a hidden session-lens.** A harness's behavior *is* its
  transcripts: a redundant tool call, a dropped requirement, a repeated dead-end all *manifest as
  text*. So `I(M ; {O_transcript}, K_R^corpus)` is large and `I(M ; {L_session} | {O_transcript},
  K_R^corpus) ≈ 0` — harness evolution is a **corpus-analysis / eval problem by construction**.
- **The already-built machinery confirms it.** `run_swc_session.py` ran (turn1 rel_recall 0.50→0.625,
  n=1, no CI) — but its mechanism is a **reviewer reading the OUTPUT** and injecting targeted
  considerations (trace/reflection, K_R-reads-O), *never* a workspace read. `run_memory_value.py` was
  built but **never run**, and on the current 1-lever ledger (support 1 < `min_support` 2) `consolidate`
  yields 0 beliefs → WARM ≡ COLD by construction. The trace-consolidation *value* is the one thing the
  project built and never measured — and it is a **trace** thesis, not a lens thesis.

**The one honest runnable slice** is therefore not a session-lens (undefined on Claude = B(iii) at
session scale) but the **trace-consolidation value** itself: run `run_memory_value.py --cases nhanes`
with enough training cases that ≥2 corroborating levers share a `case_signature` (so `consolidate`
yields ≥1 belief), COLD vs WARM, bootstrap CI. **Both arms are externalized-trace, neither is a lens.**
Expected `memory_inconclusive`, any gain likeliest on guardrail/consistency reliability. Label a
positive **trace-consolidation value, never session-lens.**

**Guardrail hole found in passing:** the one persisted lever's `mediator_moved` carried a stray
patient-ish number (`"…vasoconstriction — true 62"`) because `lever_ledger.validate_lever._no_numbers`
rejected numeric *types* only, not digits embedded in strings. Fixed (reject standalone
measurement-like numeric tokens in strings; single-digit classifiers like "type 2" still allowed).
