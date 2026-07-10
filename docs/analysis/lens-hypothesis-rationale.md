# Why we hypothesized the lens should improve everything — and why it didn't

> 2026-07-10. The honest record of the *motivation* behind the whole lens-driven-evolution program,
> and where the reasoning was right, where it was incomplete, and what the incompleteness cost. Read
> alongside [`why-no-lens-payoff.md`](why-no-lens-payoff.md) (the info-theoretic dissection) and
> [`../RESEARCH_SUMMARY.md`](../RESEARCH_SUMMARY.md) §0/§6b (the verdict).

## 1. The original hypothesis (stated plainly)

**If a model's internal workspace is *reportable* and *causal* (Anthropic 2026), then reading it should
let us optimize everything the model consumes** — the input, the prompt, the skills, the sub-agent
definitions, the harness — because the workspace tells us *why* the model succeeds or fails, not just
*whether* it did. The answer grades the output; the lens grades the process. Acting on the process
should beat acting on the output alone.

## 2. The four steps of reasoning that made it feel almost obvious

1. **Reportability (from the paper).** The model's verbal self-report is *read out of* its internal
   global workspace — what it says it is thinking tracks what it is actually representing. So a
   self-report probe is a real (if uninstrumented) window on the computation.
2. **Causality (from the paper).** Single-token interventions in that workspace causally steer the
   output. So the workspace is not an epiphenomenal commentary — it is load-bearing.
3. **Non-redundancy (we proved it).** The workspace carries information about the computation *beyond*
   what the input and output jointly reveal — `I(L ; Y | I, O) > 0`. The sharpest demonstration: an
   uncommitted read flags inconsistencies in the output's *own reasoning* that the output cannot
   self-report. This felt like a knock-down argument (the "burden-of-proof reversal"): *if a signal is
   reportable, causal, and non-redundant with both input and output, denying it optimization value
   should require a reason.*
4. **The actuator surfaces.** Given a diagnosis of *which* concept/variable/step was missing or weak,
   you can route a fix to the cheapest surface — prompt, skill, KB, sub-agent parameter, or harness
   code — and re-check with the lens. Five surfaces, one signal.

Steps 1–3 are **correct and remain correct.** The program was not built on a fantasy; it was built on
three true premises.

## 3. The missing premise — where the reasoning was incomplete

The argument in §2 conditions non-redundancy on `{Input, Output}`. It silently assumed that
"non-redundant with input and output" implies "actionable for a competent operator." It does not,
because **actionability conditions on one more thing: the reader's own knowledge `K_R`.**

> Non-redundancy: `I(L ; Y | I, O) > 0`. Optimization value: `I(L ; E* | I, O, K_R) > 0`.

For a **frontier reader on a task inside its competence, `K_R` is enormous and screens off `L`**:
`I(L ; Y | O, K_R) ≈ 0`. The lens is non-redundant with the *output*; it is **redundant with (output
+ a competent reader's prior).** Everything the lens surfaces about *this* problem, a competent model
reading the output already knows. The burden-of-proof reversal had a valid answer all along, and it is
one word: **competence.** (Full derivation: [`why-no-lens-payoff.md`](why-no-lens-payoff.md) §1.)

## 4. Why the paper's own uses don't contradict this

The paper's demonstrated uses all live in the *opposite* regime — where the reader genuinely lacks
`K_R`:

- **self-report** reads out a state no external observer can see (`K_R` empty by construction);
- **single-token steering** acts causally *inside* the model, where no external actuator reaches;
- **deception/shortcut detection** fires exactly when the output `O` is adversarially misleading — so
  reading `O` fails, and the lens is the only channel.

So the paper is about **monitoring/readout where the output is unavailable or corrupted**, never about
optimizing the input of a competent model. Our program quietly ported a monitoring result into an
optimization setting and inherited a null the paper never claimed to escape.

## 5. What the evidence actually showed (the honest scorecard)

- **Non-redundant: yes** (proven, and consistent with the paper).
- **Improves outcomes over a strong blind baseline: not demonstrated**, across self-report, Qwen-proxy,
  and Fable/Opus-prediction, through every actuator we built. The one clean, repeated win
  (missing-data flagging 0→1.0) was a **deterministic directive, not the lens**.
- **Phase 2 measured the mechanism:** on a mechanistic-reasoning task, a competent blind reader (Opus)
  caught 0.96 of subtle defects; the reasoning-monitor and the model-oracle added nothing significant.
  The only crack was a defect whose truth was an *arbitrary parameter not in the reader's prior* — the
  boundary made visible.

## 6. The corrected hypothesis (what we would claim now)

> Reading a model's workspace optimizes its inputs **only where the reader lacks the knowledge to
> adjudicate the output** — a weaker reader, genuinely novel/arbitrary content, or an output that is
> unavailable/corrupted. On tasks inside a capable model's competence, reading its workspace does not
> beat reading its output with a capable model.

This is not a retreat from the paper; it is the paper's own boundary, made precise for the
optimization setting. It also says exactly what *would* change the verdict — the measured lens on
Claude via the API, an **out-of-competence** task, and a real per-item actuator at n≥30 — none of which
is Opus-reads-Opus, which is why every Claude-only experiment we ran returned inconclusive.

## 7. What was genuinely built and stands (so the program was not wasted)

The lens hypothesis was the *motivation*; the *deliverables* are real and outlive it: an honest,
tested experimental apparatus (A/B with bootstrap CIs, ablation, counterfactual-sensitivity), a
guardrail-protected non-diagnostic gate, and — most importantly for what comes next — the
**mechanistic-modeling harness** (Phase 1), whose value was never the lens but scientific
hypothesis generation. Phase 3 builds on *that*, not on the lens.
