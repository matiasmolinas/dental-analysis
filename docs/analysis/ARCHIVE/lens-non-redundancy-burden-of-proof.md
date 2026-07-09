# The lens is not "feature 11 of 11": non-redundancy, the burden of proof, and what our null actually licenses

> Produced 2026-07-09 with the **Fable** model. A correction to the framing in
> [`skill-vs-mechanism-optimizer-reframe.md`](skill-vs-mechanism-optimizer-reframe.md) §3
> (the "row 11 of 11" table) and a sharpening of the null-result reads in
> [`lens-ablation-result.md`](lens-ablation-result.md), [`is-the-lens-working.md`](is-the-lens-working.md),
> and [`lens-impact-gap-map.md`](lens-impact-gap-map.md). Grounded in `results/ablation_v2.json` (n=6),
> `results/counterfactual_evolved.json` (n=4), `APPROACH.md` §8, `REFORMULATION.md` §R5, and the J-lens
> paper. Engages a direct argument from the project lead. The correction cuts against our own prior
> framing; §4 marks where the argument it defends stops being a theorem.

## 0. The claim being corrected

From `skill-vs-mechanism-optimizer-reframe.md` §3: *"The workspace readout is one input parameter among
many… The lens is row 11 of 11."* That number is where a bias entered: it demotes the lens to a peer of
ten other features and imports a prior — *the lens must earn its place against the field.* The project
lead's argument is that this prior is backwards. This document accepts it, states its one limit, and
rewrites the experimental program.

## 1. The burden-of-proof reversal — stated and accepted

Let `O` = output, `I` = input, `W` = workspace readout. Premises: `W` is (1) reportable, (2) measurable,
(3) **causally mediates** higher-order reasoning (swaps change answers; ablation kills multi-step
reasoning), (4) **non-redundant with `O`** (it carries information `O` provably does not — the paper's
headline). Inference: for optimizing `I`/harness, a signal satisfying (1)–(4) is a priori at least as
valuable as `I`/`O`, and **strictly more** than `O` on the margin *because* of (4). So the correct null
is **H₀: "the lens adds optimization value,"** and a result appearing to deny it carries the **burden of
proof**.

**This reverses what the prior framing implicitly did, and the reversal is correct.** The *letter* of
the prior work respected the asymmetry (`is-the-lens-working.md` §1: we "fail to reject," which is
"weaker than establishing absence"). But the *framing* ("Zero PROVEN cells," "row 11 of 11") set the
default reading to *unproven → discount it* — treating the negative as the resting state. Given (1)–(4),
the resting state should be the opposite.

**What our numbers license, precisely.** `verdict: lens_inconclusive` (n=6): B_lens − B_blind relational
**+0.104, 90% CI [−0.042, +0.229]**; mechanism **+0.021 [−0.042, +0.083]**; others flat; counterfactual
0.00 both. Every CI straddles zero → **failure to reject H₀**, not rejection, and certainly not
acceptance of ¬H₀. The honest one-liner: **we did not show the lens has value; we also did not show it
lacks value; we showed our mechanism, on our task, failed to extract value** — with a marginal whose sign
we can't pin down. "Failed to show value" ≠ "showed no value"; the prior framing let the first slide
toward the second.

## 2. Why non-redundancy makes it privileged, not just another feature

The optimizer already has `I` and `O` for free; its job is to change `I` so `O` improves. Every feature
derivable *from* `I`/`O` (reformattings, gradings, substring recalls, missing-field flags) carries **zero
new bits**. A feature's optimization value is its **conditional information given what you already have:**
`Value ∝ I(feature ; target | I, O)`.

- A feature that is a function of `O` contributes ≈0 new bits (the observer's actual failure mode: the
  full-state features are re-derivable, so §5's own prediction was "(3)≈(4)").
- A feature **provably not a function of `O`** — premise (4) — is the *only* kind that can contribute a
  positive, non-substitutable quantity. Privileged **by construction**, not by luck.

So the lens is not "one feature among eleven"; it is **the one feature whose defining property is
non-redundancy with the two things we already have.** `I` and `O` are the plane the optimizer already
lives on; `W` is valuable exactly to the degree it points **off** that plane.

**Mechanism, tied to the paper.** To optimize `I`/harness you need *why `O` is what it is* and *what was
considered-but-not-said* — neither recoverable from `O` by definition. The paper's non-redundant readouts
are exactly this shape: `ERROR` on a bug the model never flagged; `fake`/`fictional` on a staged scene it
played straight; intermediate steps / a dropped branch; protein function; injection detection. In each,
grading `O` **cannot** tell you what to change about `I`, and `W` can. The prior table annotated row 11
"corroborated by row 10 (the output grade), never sole driver" — but row 10 is the very thing row 11 is
non-redundant *with*; asking the output grade to vouch for the workspace runs the dependency backwards.

**Kept from the prior doc:** rows 9 (thinking trace) and 10 (output grade) *are* signals the current
observer ignores, and adding them is a real cheap win. The correction is narrow: adding them does not
*demote* the lens; it removes blindness to the *redundant* signals while leaving the *non-redundant* one
uniquely positioned.

## 3. The three legitimate *motivos* our experiment doesn't meet the burden

Each is real, bounded, and about our setup — none licenses "the lens has no value."

**(a) ACCESS — reportable ≠ measurable-on-Claude.** The prior is about the concept `W` with all four
premises; our access on Claude satisfies only (1). `APPROACH.md` §8: the live signal is inferred
self-report, "not a measurement"; the measured lens exists only on Qwen, never on Claude via API. So (2)
and (3) hold for the object the paper studied, not the proxy we read (uncorroborated, Claude-grading-
Claude). *Licenses:* discounting our particular readout's strength. *Does not license:* discounting the
concept — the weak link is the instrument, not the theory.

**(b) TASK CHOICE — re-derivable mediators collapse `W` onto `O`.** Our perio↔CV mediators (`endothelial
dysfunction`, `C-reactive protein`, axis derivation) are re-derivable by a strong blind model — which is
why A→B_blind captures the entire gain (relational **+0.292**) and B_blind→B_lens is **+0.104, CI through
0**. Re-derivability is *precisely* the condition under which a non-redundant signal **cannot show its
non-redundancy**: if `O` reconstructs `W`, then `I(W;target|I,O)≈0` *for this task*. We ran the
privileged-feature test on the one regime that neutralizes the privilege. *Licenses:* "on re-derivable
tasks the lens adds ~0." *Does not license:* any claim about the paper's regime (hidden bug / subtle
omission / non-obvious missing variable), which is untested here.

**(c) EXTRAPOLATION — monitoring ≠ external-optimization.** The paper shows `W` is causally necessary for
the *model's own* reasoning and useful for *monitoring/detection* — not that reading it helps an
*external* optimizer improve `I`. That step is a strong plausible inference, not a theorem. *Licenses:*
treating external-optimization value as a well-motivated hypothesis with the burden on the negative.
*Does not license:* asserting it as established by the paper.

Together: (a)+(b) explain why *our* experiment couldn't reject H₀ regardless of its truth; (c) explains
why H₀ isn't yet a theorem. The justified reason lands on **our setup**, not the lens.

## 4. The one place the argument over-reaches (honest)

**"Measurable" is true for the concept and for Qwen — not for Claude via API today.** The four premises
are jointly satisfied only on a *proxy* (Qwen-4B), across a **transfer gap** (different model) and a
**single-token limit** under which the measured lens is *lower*-resolution than the self-report it would
validate (our mediators are multi-token). So "reportable AND measurable" is not *jointly* true of the
signal we can read on Claude.

**"Causal in the model" ≠ "useful to an external optimizer."** External value additionally requires a
**mechanism that converts a differential in `W` into a differential in action**. Our results are the
cautionary case: a fixed-prompt actuator capped the marginal at ~0, and the one intervention that moved
reasoning (factor-grounding, −0.25 → +0.33) was found in the **output** and **bypassed the lens pipeline**.

**Net:** the prior is strong enough to **flip/raise the burden of proof** — H₀ "the lens adds value" is
the hypothesis to try to reject, and the prior framing under-weighted a non-redundant causal signal. It
is **not** strong enough to **discharge** it: it does not, by itself, prove external-optimization value on
Claude. It raises the burden; it does not pay it.

## 5. The corrected experimental program that would actually test the prior

The prior five-arm design **stacks the deck against the lens** (re-derivable mediators + self-report), so
its "(3)≈(4)" prediction is nearly forced *by task choice*. A fair test removes all three *motivos*:

**(a) A NON-OBVIOUS-gap task — the regime where `≠O` pays.** Replace re-derivable perio↔CV with a case
whose gap a blind strong model **cannot localize from the record**: a planted subtle omission or a
genuinely non-obvious missing variable (the paper's regime). Operational test of "non-obvious": run
B_blind first and confirm it *fails to surface the gap* (relational_recall on the planted item ≈ 0). Only
on items where the blind model is blind can a non-redundant signal demonstrate non-redundancy.

**(b) A holistic optimizer over `I`+`O`+`W`, `W` privileged.** Conductor-lite v1, but with two framing
fixes: (i) allow the optimizer's rationale to be driven **by the lens alone** when it points at something
`O` does not contain (drop the "never sole driver / corroborated by the output grade" rule — it
structurally forbids the non-redundant win); (ii) add an **actuator with degrees of freedom** (an edit
space that can act differently on a differential lens signal, not a fixed converge prompt) — else the
motivo-(c) inertia recurs.

**(c) Faithful access — pay down motivo (a).** Either/both: **corroborated self-report** (gate every
load-bearing readout on the counterfactual-sensitivity flip — trusted only when flipping the named factor
moves the dependent axis, on Claude, no external instrument); and/or the **scoped measured-Qwen
correlation probe** (Spearman on single-token surfaces — establishes the self-report is a faithful proxy,
caps at "suggestive," doesn't cross the transfer gap).

**Metric & decision rule.** Headline = `relational_recall` AND counterfactual `sensitivity_rate` + mean
affected-delta; substring `mechanism_recall` diagnostic-only; guardrail a hard gate; **n ≥ 30** with
bootstrap CIs, separate evaluator.
- **Lens marginal = (full-with-lens) − (full-without-lens), on the non-obvious task.** CI **excludes 0
  above** → burden **paid**, prior **CONFIRMED** (first genuine evidence of the lens as an external
  improver, in the regime where non-redundancy is the mechanism).
- If, on a **non-obvious task**, with a **corroborated signal** and a **free actuator**, the marginal CI
  still straddles/excludes 0 below → the *justified negative* the reversal demands: prior **REJECTED** for
  external optimization on Claude. Our current null cannot do this — it removed none of the three motivos.

**Prediction (falsifiable):** on the non-obvious task with a free actuator, marginal(lens) > 0 with CI
excluding 0 — the mirror of the prior "(3)≈(4)" prediction, which was an artifact of testing on the one
regime that hides non-redundancy.

## 6. Bottom line

The lead is right on the load-bearing point and right to reverse the burden. A reportable, causal,
**non-redundant-with-output** signal is a strong prior for optimization value; "row 11 of 11"
under-weighted it — `I` and `O` are the plane the optimizer already lives on, and the workspace is
privileged precisely to the degree it points off that plane (the paper's `ERROR`-on-a-silent-bug and
`fake`-on-a-staged-scene are the proof of non-redundancy). Our `lens_inconclusive` result licenses only
"**our mechanism, on our task, failed to extract the value**," not "the lens has little value." The three
justified reasons are all about our setup (self-report proxy, re-derivable mediators, monitoring-not-
optimization). The single over-reach: "measurable" holds for the concept and Qwen but not Claude via API,
and "causal in the model" needs an actuator to become external value — so the prior **raises** the burden
without **paying** it. The corrected program pays or refutes it honestly: a non-obvious-gap task, a joint
optimizer that lets the lens drive when it points off the output plane, a corroborated signal, and
marginal(lens) with a CI that finally clears zero.
