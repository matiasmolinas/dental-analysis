# Can the validated strategy evolve the harness? And the untested Qwen-everything lens regime

> Fable analysis, 2026-07-10 (jacobian-lens reference impl confirmed runnable). Answers two questions:
> (Q1) can the strategy we *validated* drive harness/context evolution; (Q2) have we ever tested the
> Jacobian lens in a regime where everything — harness, context, and a MEASURED lens — is Qwen 4B, and
> is it the one place the boundary condition permits the lens to work. Builds on
> [`why-no-lens-payoff.md`](why-no-lens-payoff.md), [`perio-cognition-result.md`](perio-cognition-result.md),
> [`memory-value-result.md`](memory-value-result.md).

## Q1 — Yes-with-scope: the validated strategy is EVAL/DATA-ANCHORED evolution

What is validated is **not** the lens or consolidation (both null) — it is the **discovery loop**:
mechanistic model → hypothesis → validation against *external held-out data* with bootstrap CIs →
non-diagnostic guardrail. It produced Track-2 (perio↔cognition, 3/4 significant adjusted) and the W1
missing-data win (0→1.0). Its validity flows from one fact: **the fitness signal comes from OUTSIDE
the model** — real NHANES coefficients the model doesn't know until it computes them. That is *content
the reader lacks* — the exact channel the boundary condition permits.

| Evolution driver | Fitness signal | Result | Why |
|---|---|---|---|
| Lens-driven | model's own workspace (inferred, Opus-reads-Opus) | null | `I(L;Y\|O,K_R)≈0` — inside competence |
| Memory/consolidation | self-graded traces re-read | `memory_inconclusive` | trace re-derivable → inside K_R |
| **Eval/data-anchored** (validated) | external held-out ground truth + real downstream metric | **Track-2 + W1 positive** | signal is content the reader lacks |

This **is** §6's "harness evolution is a corpus-analysis / eval problem by construction" — and that
coincidence is not a null, it is **the positive residual left standing after the two nulls are
removed.** The boundary condition doesn't only forbid the lens; it *points* at what remains, and what
remains already paid.

**The concrete loop:** (1) propose a change to any surface (prompt/skill/subagent-def/harness
code/context) as a hypothesis; (2) define a metric with **external/held-out ground truth or a real
downstream outcome** (recover a known association on a held-out NHANES cycle; injected-defect recall;
guardrail pass-rate; CI calibration); (3) A/B baseline vs change with `ablation._bootstrap_ci`;
(4) **adopt iff the CI separates** (why W1 was adopted and the lens/memory changes were not); (5) loop.

**Can:** evolve any surface whose effect is measurable against an external anchor (the bootstrap-CI
apparatus *is* the fitness function; W1 is the existence proof). **Cannot:** evolve toward "better
reasoning" judged by the model reading its own output (Opus-reads-Opus, screened); generate its own
fitness from introspection; run open-endedly without an eval (no anchor → no evolution). One-liner:
**the validated strategy evolves the harness wherever you can point it at ground truth, and nowhere
else — the boundary condition doing useful work, not only forbidding.**

## Q2 — The Qwen-everything measured-lens regime: never tested, and the one door the boundary permits

**(a) Have we tested it? NO.** Every lens result is Claude **Opus-reads-Opus with an INFERRED
(self-report) lens** — the maximally-competent-reader regime (forced partly by Fable's medical
refusal). `probes/qwen_correlation_probe.py` is a scaffold, GPU-gated, never run, and only a
*correlation* probe — not a Qwen-executor + measured-lens + evolution loop. The **Qwen-everything
measured-lens regime is entirely untested.**

**(b) The asymmetry is correct — with two scoping constraints.** The boundary is `I(L;Y|O,K_R)≈0`
*because K_R is enormous*. Shrink K_R (weak reader) and `I(L;Y|O,K_R)` can be > 0. So Qwen-4B is **not
"just another test" — it is the exact regime the boundary names as where the lens should pay**, and the
honest gap: our own theory predicts green in a regime we never ran. Two real constraints (scoping, not
fatal):
- **Measurement impoverishment.** The measured jlens reads *single-token vocabulary surfaces*; if Y is
  multi-token, the measured lens is *blinder than the self-report it replaces* → forces the task class
  to **single-token-decodable Y** (the README boot→"lira" example).
- **Recognition-generation gap.** In Qwen-everything the actuator is also Qwen, so optimization value
  needs `I(L;E*|O,K_R_qwen)>0` **and** that Qwen can *act* on flagged content it wouldn't spontaneously
  surface — real (recognition > generation) but narrower than "weak reader → lens pays."

Net: the lens *can* work on Qwen, on **single-token-decodable, out-of-competence** tasks, via the
recognition-generation gap.

**(c) The experiment (self-contained Qwen-4B loop):**
- Executor = Qwen generates `O`; measured lens = jlens `apply` (mid-network) → single-token workspace ranks.
- **Arm 0 (lens-free K_R baseline):** Qwen reads its own `O`, brainstorms what's missing, proposes edit.
- **Arm 1 (measured lens):** `L_measured` surfaces the signal → targeted edit.
- **Prerequisite gate:** the correlation probe — is `I(L_measured;Y|O) > 0` at all? If the single-token
  lens doesn't carry Y, stop (measurement impoverishment, not boundary).
- **Quantity:** the lens-beyond-K_R marginal `I(L_measured;E*|O,K_R_qwen)` ≈ paired success delta
  **Arm 1 − Arm 0**; bootstrap 90% CI, **n ≥ 30**; positive = CI excludes 0.
- **Task class (load-bearing):** at/beyond Qwen's competence edge (blind Qwen fails) AND Y
  single-token-decodable (factual/bridge recall where the answer token is represented mid-network but
  not surfaced; or shortcut tasks where `O` is misleading but the correct token is in the workspace).
- **Expected outcome:** a plausible **narrow positive** — the one regime the theory predicts green;
  effect small; null risks = single-token lens too blind, or Qwen can't act on the flagged content.

**(d) A positive would / would NOT prove:**
- **Would:** a MEASURED (not inferred, not Opus-reads-Opus) lens carries actionable signal beyond
  `O + K_R` for a WEAK reader — the first such positive; empirically **validates the boundary
  condition** (green exactly where predicted); motivates the measured-lens-on-Claude ask *for the
  analogous regime only* (tasks Claude is not competent at, corrupted `O`).
- **Would NOT:** prove lens optimization for a **competent** model on in-competence tasks (that stays
  refuted — the win comes *from* the weakness); **transfer to Claude** (no measured lens there = B(iii);
  Claude's huge K_R shrinks the payoff regime toward zero); validate lens-driven evolution of a frontier
  harness. It validates the paper's **monitoring** claim with a real lens on a weak model.

**(e) Feasibility:** `../jacobian-lens/` is a **real runnable reference impl** (`jlens` with `apply`
*and* `fit`, API matching the probe; deps torch/transformers≥5.5/huggingface_hub, tests present). Caveat:
the probe hard-codes a pre-fitted Hub lens that may not resolve → may need `jlens.fit` (~100–1000
prompts, hours on one GPU). Colab T4 suffices for apply; ~1 GPU-day total. **Cannot run in this
(no-GPU) environment — it is a Colab job.**

## Bottom line: PARTIAL ESCAPE — a genuine door into a small room

The Qwen-everything measured-lens regime *can* validate the lens where Claude couldn't — but for a
**weak model, on single-token-decodable out-of-competence tasks**, as **monitoring / weak-model
optimization**, and it **will not transfer to Claude.** It is genuine — the only genuine door in the
whole arc — because the boundary *forbade* every Claude test for a specific reason (K_R enormous →
screens the lens), and that reason is *relaxed* for Qwen (K_R small). The boundary isn't evaded; it is
**satisfied**: Qwen-out-of-competence is definitionally the "reader lacks K_R" regime the boundary
always said was where the lens works. Every Claude test put the reader *inside* its competence; the
Qwen test is the first to put a **measured** lens with a reader **outside** its competence — same
inequality, opposite side. That is exactly why the boundary permits it when it forbade every Claude test.

**Recommendation:** DEFER as a project priority; run only the minimal scoped slice if closure is wanted
— (1) the correlation gate, then (2) the 2-arm out-of-competence optimization test at n≥30 with a
bootstrap CI. ~1 GPU-day, framed as **epistemic hygiene / boundary-validation, not a path to Claude
harness evolution.** Track-2 is the durable result and the room the project actually lives in.
