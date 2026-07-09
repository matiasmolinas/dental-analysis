# Measured Qwen lens vs. our inferred self-report: contradiction, actionability, and whether to run it

> Produced 2026-07-09 with the **Fable** model. Builds on
> [`skill-vs-mechanism-optimizer-reframe.md`](skill-vs-mechanism-optimizer-reframe.md)
> (70/30 mechanism/skill) and [`lens-impact-gap-map.md`](lens-impact-gap-map.md). Grounds
> Q2/Q3 in the *actual* capability of the sibling `../jacobian-lens` code (pre-fitted
> `neuronpedia/jacobian-lens@qwen-n1000` on `Qwen/Qwen3.5-4B`, single-token ranked-vocab
> readout, GPU-only), not the idealized paper. Speculation labeled. Answers: **(1) no
> contradiction, (2) research-actionable yes / optimization-actionable probably no,
> (3) scoped-go on a tightly bounded correlation study.**

## Q1 — Contradiction verdict: NO contradiction

Our null and the paper's claims are about **different objects**, so they cannot contradict.
The paper claims: (1) the workspace **exists and is reportable** (we *assumed* this — the
premise of the inferred-lens setup); (2) it is **causal**, proven by **intervening** on
activations (swaps) — our self-report path is read-only and literally cannot run the
experiment that could contradict the causal claim; (3) it is useful for
**diagnostic/monitoring** (eval-awareness, fabrication, hidden goals, bugs) — every
demonstrated use is *detection*, not downstream task optimization.

Our finding (`lens_inconclusive`; B_lens − B_blind relational +0.104, 90% CI
[−0.042, +0.229]; counterfactual ~0) is about a **fourth thing the paper never asserts**:
*"a verbalized readout, fed to a hand-designed `readout→observer→converge` actuator,
improves downstream optimization over a strong blind converger."* The paper does not claim
this; Trinity/Conductor predict the opposite. So our null is **fully consistent** with the
paper — evidence about our **mechanism/use**. We would only *appear* to contradict it if a
reader over-generalized the paper to "reading the workspace must help any task" — a strawman
the paper never makes. Our result actually *rhymes* with the paper: the lens's value is as a
**localizer/detector**, the register the paper validated. Honest caveat: we also do not
*corroborate* the paper (no ground truth, self-report on Claude) — we are consistent with and
downstream of it, not evidence for or against its mechanistic core.

## Q2 — Would a measured Qwen lens give actionable info? Split the question.

### (i) MEASUREMENT / research question — *plausibly YES, actionable as a finding*
*"Does input FORMAT X raise the workspace-band rank of the (single-token) mediators in Qwen,
and does Claude's inferred self-report CORRELATE with those measured ranks?"*
- `JacobianLens.apply(model, prompt, layers=…, positions=[-1])` returns per-layer vocab
  logits; the **rank of a mediator's single token** (`CRP`, `inflammation`, `plaque`,
  `endothelial`, `diabetes`) in the workspace band is a real measured number; Δrank across
  format A vs converged is a clean read of "did this format make the mediator more
  representable."
- Spearman(inferred self-report surfaced-mediators, measured Qwen ranks) is a real test of
  whether our self-report channel tracks anything mechanistically measurable — a number that
  **does not exist today** (the whole `APPROACH.md` §8 "we have no ground truth" caveat). Even
  on a proxy, it converts a pure speculation into a measured data point.

### (ii) OPTIMIZATION question — *probably NO*
*"Would feeding measured Qwen ranks into our `observer→converge` actuator beat blind?"* The
binding constraint is that a **fixed-prompt `converge_fn` caps the readout's marginal value
at ~0 regardless of signal quality** — a strong blind converger already re-derives the gap. A
*measured* signal through the *same* actuator inherits the same ceiling. Better measurement,
same redundancy.

### The three constraints (bite (ii), discount (i))
1. **Transfer gap (largest).** The lens reads **Qwen-4B, not Claude.** It measures the proxy's
   workspace on prompts Claude processes — exactly the DUAL_LENS correlation the 2026-07-09
   pivot deliberately deleted. Any result's bearing on Claude is an assumption, not a
   measurement; this caps even the research win.
2. **Single-token limit — the measured lens may be BLINDER than the self-report it "validates."**
   Our load-bearing mediators are multi-token ("endothelial dysfunction," "C-reactive protein,"
   "atherosclerosis," "oxidative stress"); the lens ranks only **single tokens** and
   `bridge_concepts.py` already retreated to lossy surfaces (`CRP`, `protein`, `endothelial`,
   `plaque`). The self-report **names the multi-token concept directly**. So the instrument that
   would "validate" self-report is strictly lower-resolution than self-report on our exact targets.
3. **4B weakness.** The paper's causal claims were on frontier models; Qwen-4B's workspace may be
   weaker/shallower, so a *null* on Qwen is confounded (bad format, or 4B just doesn't represent
   the bridge). Weakens the negative more than the positive.

**Calibrated Q2 answer.** A measured Qwen lens gives **actionable research information** (first
proxy-grounded self-report↔measured correlation, per-format representability) but **not** the
*optimization* information our path lacks — the mechanism, not the signal, is the bottleneck, and
on our multi-token mediators the measured lens is *lower*-resolution than the self-report it would
check. Net: upgrades the **honesty/measurement** story, not the **optimizer**.

## Q3 — Worth a Colab + Qwen-4B experiment? SCOPED-GO (small, correlation-only)

Go **only** for Q2(i), **not** a revival of the DUAL_LENS optimization pipeline and **not** feeding
measured ranks to the actuator (gated by Q2(ii)). The pre-fitted Hub lens makes it nearly free and
it converts a documented speculation into a measured point.

**Minimal experiment (positive-EV envelope):**
- **No fitting.** Load `neuronpedia/jacobian-lens@qwen-n1000` for `Qwen/Qwen3.5-4B` via
  `JacobianLens.from_pretrained` (walkthrough.ipynb). One Colab T4 (inference-only; the expensive
  backward-pass fitting is skipped).
- **Single-token surfaces only** — the ones `bridge_concepts.py` keeps (`CRP`, `protein`,
  `inflammation`, `plaque`, `endothelial`/`vascular`, `bacteria`, `oxidative`, `cardiovascular`,
  `diabetes`, `smoking`). Explicitly **exclude** multi-token targets; apply `qwen_gloss.json.gz`
  for CJK vocab noise.
- **A handful of formats** (A naive vs converged, maybe one intermediate) on **one mid-difficulty
  case**. Not n≥30 — a measurement probe, not a powered A/B.
- **Measure:** (1) mediator workspace-band **Δrank** (converged − naive); (2) **Spearman** between
  Claude's inferred surfaced-mediators and Qwen's measured ranks.

**What each outcome licenses:**
- **Positive** (converged raises Qwen ranks AND Spearman ≫ 0): the self-report is a **faithful proxy**
  on this task — the skill/signal 30% is vindicated as *measurement*, and the `APPROACH.md` §8
  measured-lens "unlock" becomes a proxy-supported hypothesis. Vindicates the **detector**, not the
  optimizer (Q2(ii) still holds).
- **Negative** (no movement / Spearman ~0): **lean harder on behavioral corroboration** —
  `relational_recall` + counterfactual sensitivity become the sole load-bearing evidence, and the
  inferred-lens framing down-weights to "cheap, unvalidated gap-namer." A useful negative.

**Honest EV & why "scoped," not "go":** upside is **epistemic hygiene** (a first ground-truth-ish
anchor for a signal we currently caveat as ungrounded — the project's central honesty risk), **not**
an optimization gain, and the write-up must not imply otherwise. Even a clean positive is about
**Qwen-4B**, on **single-token surfaces**, from an **imperfect** lens — three proxy layers from a
claim about Claude on multi-token bridges; it can *suggest*, never *establish*, transfer. It re-opens
what the pivot closed, so frame it as a **one-shot, time-boxed measurement probe** (≈ a day of Colab
against the pre-fitted lens); if it can't stay that small, it flips to **no-go** — the mechanism-side
work (`lens-impact-gap-map.md` §5: factor-grounding, deterministic missing-data path, the five-arm
optimizer ablation) has strictly higher EV for the task and must not be displaced.

## Bottom line
No contradiction with the paper (Q1). A measured Qwen lens hands us a real *research/measurement*
result and does *not* fix the optimizer — the bottleneck is the mechanism, not the signal — and on
our multi-token mediators the measured lens is actually blinder than the self-report it would check
(Q2). Worth a **tightly scoped, no-fitting, correlation-only Colab probe** whose entire deliverable is
"does our self-report correlate with a measured workspace on a proxy": valuable as honesty/measurement,
explicitly not as optimization, and only if kept small enough not to displace the higher-EV mechanism
work (Q3).
