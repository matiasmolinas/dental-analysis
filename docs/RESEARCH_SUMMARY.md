# Executive Summary — the HISTORA / Jacobian-lens research arc

> 2026-07-09. Consolidates the full investigation (10 analyses in [`analysis/`](analysis/) + the
> live runs in [`REFORMULATION.md`](REFORMULATION.md) §R5–R6). Purpose: answer every hypothesis and
> strategy raised along the way, and define prioritized next steps. Claude-only throughout; the
> inferred/predicted lens is self-report/inference, never a measurement.

## 0. One-line verdict

**The workspace/lens signal is real and non-redundant — but no mechanism we built converts it into an
outcome gain over a strong blind baseline, on this (largely re-derivable) task. The bottleneck is the
actuator + the task + the access, not the signal's existence.** Two unrun doors could still flip it.

## 1. What we built

A **Claude-only** self-evolving agent: an **inferred-lens Observer** (a 2nd instance that reads the
primary's workspace self-report), a **Session Working-Consciousness** ledger, evolution across **five
surfaces** (work prompts, skills, KB, sub-agent defs + injected variables, harness code), and a
guardrail-protected T0/T1 gate. Around it: a live A/B harness, an ablation harness with bootstrap CIs,
a counterfactual-sensitivity reasoning test, a "predict-the-workspace" gate, and behavioral validation
— all runnable, 35 tests green, executed live on Claude Opus/Sonnet with real NHANES cases.

## 2. Every hypothesis / strategy you raised — answered

| # | Assumption / strategy | Test | Verdict |
|---|---|---|---|
| H1 | The Observer→evolution loop (5 surfaces + session-consciousness) yields a better result | Built + R0–R6 | **Software works & is validated as a system**; the lens's *contribution within it* is the open question (H4). |
| H2 | Claude-only; explore the paper indirectly via the skill; the **real lens = the unlock** (API feature) | Adopted | **Holds.** The honest framing is intact; the measured-lens ask is the strongest forward claim. |
| H3 | The Observer-converged input beats naive on Claude ("the approach works") | Live A/B (n=1,3,6) | **Partly.** B beats A on the guardrail-critical axis (missing-data flagging 0→1.0, 6/6) — but that win is the **deterministic directive** (prompt engineering), and **recall is not the lever** (the frontier model recovers mediators unaided). |
| H4 | The **inferred lens itself** does causal work beyond good prompt engineering | 3-arm ablation (A / B_blind / B_lens), CIs | **NOT demonstrated.** `lens_inconclusive` — the lens's marginal over *blind* convergence is not significant (relational +0.104, 90% CI [−0.042,+0.229]); the guardrail value lives in the **harness**, not model convergence; counterfactual ≈0 (name-echo confirmed). |
| H5 | Session-consciousness is valuable; memory + "sleep" (Anthropic managed agents) add value; lens-based consciousness helps during sleep | Analysis | **SWC never ran live (untested).** Cross-session memory + offline consolidation add value **in principle** (esp. guardrail reliability across cases); the **lens/deficiency history is a better offline training signal than right/wrong — conditional on corroboration.** Anthropic has memory stores/tool/context-editing/compaction/scheduled deployments but **no native "sleep"** (that's SkillOpt-Sleep). |
| H6 | Is the null the **skill** or the **mechanism**? | Diagnosis + Trinity/Conductor | **~70% mechanism / 30% skill** (the 30% gated to ~0 by the mechanism). A hand-designed actuator caps the lens near zero; a **learned coordinator over the full state** (sep-CMA-ES, *not* RL) is the reframe. |
| H7 | Do results contradict the paper? Would the **measured Qwen** lens give actionable info? Worth Colab? | Analysis | **No contradiction** (the paper claims monitoring + causal-*in-model*, not external optimization). Qwen: **research-actionable** (a correlation finding) but **not optimization**, and **blinder than self-report** on our multi-token mediators (single-token limit) + a transfer gap. **Scoped-go** on a tiny no-fitting correlation probe only. |
| H8 | The workspace is reportable + measurable + **non-redundant with the output**, so a priori it's ≥ input/output in value; the burden is on the negative | Accepted + formalized | **Right.** The lens is a **privileged non-redundant feature** (`Value ∝ I(feature; target \| I, O)`), not "one of 11". Our null = **failed-to-reject**, not evidence-of-no-value. One over-reach: "measurable" is true only on **Qwen** (not Claude via API), and "causal-in-model" needs an **actuator** to become external value. |
| H9 | Use **Fable to predict Opus's workspace** (a simulation, not real) to get actionable info + report the value of the real lens | Design → gate (v1, v2, Opus) → behavioral | **NOT circular** (robust, two predictors; surfaces genuinely non-redundant, non-obvious gaps — incl. a **meta-critique of the output's own reasoning** that O cannot self-report). **BUT** the specific plant is **not isolated** (intermittent, even for Opus) and **grounding the gaps did not help** (degraded metrics) → **non-redundant ≠ useful.** |

## 3. The through-line

1. **The signal is real and non-redundant** — H8 and H9 vindicate it at the *signal* level: an
   uncommitted read of the workspace points *off* the output plane (the clearest proof: it flags
   inconsistencies in the output's *own* reasoning, which the output cannot self-report).
2. **No mechanism we built converts it into an outcome gain** over a strong blind baseline — H3
   (the win was the deterministic directive), H4 (`lens_inconclusive`), H6 (mechanism is the
   bottleneck), H9-behavioral (grounding hurt). The recurring result: **non-redundant ≠ useful,
   through our actuators.**
3. **The guardrail-critical value is deterministic harness**, not the lens — established repeatedly.
4. **The three reasons the burden isn't paid are all about our setup**, not the signal: **access**
   (self-report/inference, not the measured lens on Claude), **task** (re-derivable mediators collapse
   the workspace onto the output), **actuator** (hand-designed/append-as-text, which the paper-grounded
   design explicitly said was too weak).

## 4. Next steps — prioritized to define the path

1. **The measured lens (the API feature) — highest ceiling, not ours to run.** It is the only route
   that removes the access/inference layer. Position the whole project as **the consumer built and
   waiting for it**, plus the evidence that its inferred/predicted stand-ins are non-redundant but
   under-powered — a rigorous, honest feature request to Anthropic.
2. **A free/targeted actuator at n≥30 on a non-obvious-gap task — the untested door most likely to
   flip the verdict.** Concretely: (a) a task where a blind strong model *provably* misses the gap
   (verified by running blind first); (b) **per-item targeted grounding** — each surfaced gap drives a
   *specific* input/harness edit, gated behaviorally — **not** append-as-checklist (which diluted and
   hurt); (c) n≥30 with the bootstrap CIs already in `ablation.py`; metric = relational_recall +
   counterfactual sensitivity. This is the honest test the design demanded and we have not run.
3. **Cross-session memory + offline consolidation** (`.knowledge/lever_ledger.jsonl` + a SkillOpt-Sleep-
   style nightly pass behind the T1 gate). This is where **guardrail reliability across cases** gets
   fixed (in-session T0 can't) and where the deficiency history is a **denser training signal** than
   right/wrong. Store only structural/format/variable lessons — **never patient values** (guardrail).
4. **Run the SWC live** — the entire session-consciousness thesis is currently untested; one real
   multi-turn session where a turn-1 deficiency measurably improves turn-2 would move it from
   design-claim to result.
5. **The scoped Qwen correlation probe** — cheap epistemic hygiene: does self-report correlate with a
   measured (proxy) workspace? Retires the project's central "no ground truth" caveat, positive or
   negative.
6. **The learned coordinator (Trinity/Conductor bet)** — the big architectural swing: a full-state
   optimizer with a **learned** state→edit map (sep-CMA-ES), the lens as one privileged feature.
   Highest ceiling, highest cost; only after 2–4 justify it.

**Recommended immediate move:** #2 (free/targeted actuator, non-obvious task, n≥30) — it is the one
experiment that can still turn "non-redundant" into "useful," it uses harness we already have, and its
result is decisive either way.

### 4b. Implementation status — all six built (2026-07-09)

| # | Step | Status | Artifact |
|---|---|---|---|
| #2 | Targeted actuator, non-obvious task | **Built + bounded live run** | `src/run_targeted.py`. Planted n=1: targeted `relational_recall` 0.62 > base/append_all 0.50 (selectivity helps), but counterfactual regressed → **mixed, n=1, needs n≥30**. |
| #3 | Cross-session memory + offline consolidation | **Built + tested (offline)** | `src/lever_ledger.py`, `schemas/lever_record_schema.json`, 4 tests. Structural-signature ledger with write-time guardrail (rejects any numeric patient value), `suggest_levers`, `consolidate`. |
| #4 | Run the SWC live | **Built + live** | `src/run_swc_session.py` — 2-turn session that persists a working lever to the ledger (wires SWC ↔ #3). |
| #5 | Scoped Qwen correlation probe | **Built (artifact; GPU-gated)** | `probes/qwen_correlation_probe.py` — pre-fitted Hub lens, single-token ranks + Δrank + Spearman. Not in the Claude-only pipeline. |
| #1 | Measured-lens API feature | **Documented + consumer seam** | `docs/API_FEATURE_REQUEST.md` — the ask + why swapping inferred→measured needs no redesign. |
| #6 | Learned coordinator (Trinity/Conductor) | **Scaffold + tested** | `src/coordinator.py` (tiny head + separable ES, not RL) + 4 tests; converges on a mock objective. Live fitness (bounded Claude rollout) is the pluggable next piece. |

**What "built" does and doesn't mean:** the *runnable* pieces (#2, #3, #4, #6) are implemented and
tested/run; the *resource-gated* pieces are delivered as artifacts — #5 needs a GPU + jlens (not the
Claude-only runtime), #1 is Anthropic's feature to expose, #6's *live* training needs many bounded
rollouts. The bounded live results (#2, #4) are single-case and directional; the powered n≥30 runs and
the measured lens remain the two verdict-changing doors (§6).

### 4c. Forward-plan execution — the sensible paths, built + offline-tested (2026-07-09)

Following the gut-checked plan in [`FORWARD_PLAN.md`](FORWARD_PLAN.md) (Fable), the paths that can
honestly move — or honestly make-true — a claim were implemented. All offline pieces are tested; the
live experiments are wired and pending a run.

| Path | Verdict | Status | Artifact |
|---|---|---|---|
| **A. Lens as MONITOR/QA** (top) | reframes the one genuine positive into the paper's *demonstrated* use (detection, not optimization) | **Built + tested (offline); live run pending** | `src/qa_monitor.py` (monitor vs blind-read + eval), `src/inject_defects.py` (deterministic labeled defects), `src/run_qa_eval.py` (live Opus), `tests/test_qa_monitor.py` (8). Headline = monitor_recall − blind_recall on injected defects, bootstrap CI, matched control FP rate. **The one path that can upgrade the §0 verdict — to a demonstrated DETECTION payoff, not optimization.** |
| **C. Measured-lens readiness adapter** | makes "consumer built and waiting" literal code | **Built + tested (offline)** | `src/lens_source.py` (`get_lens_readout(source=inferred\|measured)`, same schema), `--lens-source` wired into `run_ablation.py`, `tests/test_lens_source.py` (8). `measured` raises the documented `NotImplementedError`; the day the API ships the swap is one flag + one function body. |
| **memory-value** (folds in the useful slice of the "wire the autonomous loop" path) | the value hypothesis behind the loop; first caller of the orphan functions | **Built + tested (offline); live A/B pending** | `src/run_memory_value.py` — the **first caller of `lever_ledger.consolidate` + `suggest_levers`** (both wired to nothing before). Seed → sleep-consolidate → COLD vs WARM held-out A/B with bootstrap CI. `tests/test_memory_value.py` (6). Closes the loop as a running system + measures its value. |
| **D. Targeted actuator, powered** (demoted, gated) | can only close the ours-to-run optimization door | **Made significance-aware; powered run gated on A** | `src/run_targeted.py` now computes a bootstrap 90% CI on paired `targeted − base` deltas and only says `targeted_useful` when a CI excludes 0 with no regression (point-positive-but-CI-straddles-0 is now honestly `targeted_directional_inconclusive`). Run n≥30 only **if A shows the surfaced gaps are behaviorally real**. |
| **coordinator live training** | optimizing a possibly-flat objective is premature | **CUT / deferred** | `src/coordinator.py` scaffold unchanged; revisit only if A or D show a non-flat actuator objective. |

**What this changes about the headline:** by default, nothing — these paths do not resurrect the
optimizer claim. The only path that can upgrade §0 is **A**, and it would upgrade it to *"no
optimization payoff, but a demonstrated **detection** payoff"* — the paper's actually-demonstrated use
and the more defensible claim the evidence has pointed to all along. C and memory-value make two
existing claims literally true and testable without moving the verdict (unless memory-value surprises
positive on cross-case guardrail reliability). Sequencing: **C (done, offline) → A → memory-value → D
(if A confirms)**. Test count: **65 green** (was 44; +21).

## 5. Hackathon positioning (honest)

- **Build track:** working software — the Observer loop, five-surface evolution, the guardrail-protected
  gate, and the full experimental apparatus (A/B, ablation with CIs, counterfactual reasoning test,
  predict-the-workspace gate, behavioral validation), all Claude-only, tested, run live on real NHANES.
- **Research finding (honest, and stronger for being honest):** a **rigorous negative-with-nuance** —
  the workspace signal is *non-redundant* (proven, incl. output-reasoning meta-critique O can't
  self-report) but *not yet useful* through inferred access and hand-designed actuators; the **measured
  lens is the falsifiable next step**, and the project is the consumer built for it. This is a more
  credible submission than a claimed win, and it directly motivates the API feature.

## 6. What would change the verdict
Only two things, both flagged and both unrun: **(a)** a free/targeted actuator on a genuinely
non-obvious-gap task at n≥30 (ours to do); **(b)** the **measured** Jacobian lens on Claude via the API
(Anthropic's to expose). Absent those, the defensible statement is: **real, non-redundant signal; no
demonstrated payoff.**
