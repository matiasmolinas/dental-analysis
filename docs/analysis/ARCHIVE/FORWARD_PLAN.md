# Forward Implementation Plan — dental-analysis

> Produced 2026-07-08 (Fable model, gut-checked). Planned around the settled §0 verdict —
> *"real, non-redundant signal; no demonstrated payoff as an optimizer"* — see
> [`RESEARCH_SUMMARY.md`](RESEARCH_SUMMARY.md) and [`RETROSPECTIVE.md`](RETROSPECTIVE.md).
> Each path is judged only by whether it can honestly change that sentence.
>
> **Execution status (2026-07-09):** all sensible paths implemented and offline-tested — **C** done
> (`src/lens_source.py` + `--lens-source`), **A** built (`src/qa_monitor.py`, `src/inject_defects.py`,
> `src/run_qa_eval.py`), **memory-value** built (`src/run_memory_value.py`, first caller of
> `consolidate`/`suggest_levers`), **D** made significance-aware (`src/run_targeted.py` bootstrap CI).
> 65 tests green. The three live experiments (A, memory-value, D-at-n≥30) are wired and pending a
> billed Claude run. See [`RESEARCH_SUMMARY.md` §4c](RESEARCH_SUMMARY.md).

## 1. Gut-check verdict per candidate

| Path | Verdict | Why | Honest expected value |
|---|---|---|---|
| **A. Lens as MONITOR/QA** | **KEEP (top)** | Reframes the one genuine lens-flavored positive (the gate's meta-critique of the output's own reasoning) into the paper's *demonstrated* use — detection, not optimization — cheaply falsifiable with labeled defect injection. | Best-prior new signal; the only cheap path that can produce the project's first *demonstrated payoff* (of monitoring). |
| **B. Wire autonomous evolution loop** | **DEMOTE → fold into memory-value** | A standalone orchestrator "because the loop should run" is engineering for its own sake; the only loop-closure worth building is the exact `consolidate → suggest_levers → next input` seam the memory-value test needs (called by nothing today). | Near-zero standalone; real only as substrate for the memory-value experiment. |
| **C. Measured-lens readiness adapter** | **KEEP (small)** | Converts the strongest *forward* claim ("consumer built and waiting") from prose into a one-line-swap code seam. Hours, offline. | Zero research signal; high honesty/positioning value; makes a headline claim literally true and testable. |
| **D. Targeted actuator at n≥30** | **DEMOTE (gated)** | §6 lists it as one of two verdict-changing doors that are *ours to run*, so not cut — but the prior is weak (append-all hurt; targeted mixed at n=1 with a counterfactual regression) and n≥30 live-Opus is expensive. | Moderate-low; worth running only as the powered confirmation *after* A shows the surfaced gaps are behaviorally real. |
| **memory-value** | **KEEP (small/medium)** | The actual value hypothesis under B, and the first caller of the two orphan functions. | Modest; likeliest win is guardrail/consistency reliability across cases, not recall. |
| **coordinator live training** | **CUT / DEFER** | sep-CMA-ES needs many noisy live rollouts to optimize an objective we have not shown is non-flat. | Low near-term, highest cost. Revisit only if A or D show an actuator-side payoff exists. |

## 2. Plans for each KEPT path

### A — Lens as Monitor/QA detector (labeled injection eval)

- **Files:** `src/qa_monitor.py` (`MONITOR_SYSTEM` reframe of `predicted_workspace.PREDICTOR_SYSTEM`: from "model the absent workspace to optimize" to "read THIS output +optional trace, flag reasoning inconsistencies / unsupported claims / internal contradictions / silent omissions"; `MONITOR_TOOL` schema; `detect()`; plus `BLIND_READ_SYSTEM` baseline — generic "any problems?" read, no off-plane framing). `src/inject_defects.py` (deterministic, offline: injects one labeled defect into a clean guardrail-passing output — internal_contradiction, inconsistent-confidence-weighting [the exact meta-critique the gate surfaced], unsupported_claim, silent_omission). `src/run_qa_eval.py` (live). `tests/test_qa_monitor.py`.
- **Roles:** monitor = **Opus**, baseline = **Opus** (same model, fairness), judge = **Sonnet** (reuse `COVERAGE_JUDGE_SYSTEM` idiom), via `run_gate._make_call` streaming/tool pattern. Fable refuses the medical read → no Fable here.
- **Metric:** `monitor_recall − blind_recall` on injected defects, bootstrap CI (`ablation._bootstrap_ci`) on per-item deltas, at matched false-positive rate on clean controls. **CONFIRMS** if the 90% CI excludes 0 — especially on the internal-contradiction / inconsistent-confidence class — at low control FP. **REFUTES** if monitor ≈ blind, or FP rate on clean controls is high.
- **Offline vs live:** injectors + `detect` + scorer are offline & tested; only `run_qa_eval.py` (Opus over real outputs) is live.
- **Framing:** validates the **monitoring** use (the paper's demonstrated one). Does NOT resurrect the optimizer claim; does NOT prove the *measured* lens would do better. A positive is the project's first demonstrated payoff *of detection*.

### C — Measured-lens readiness adapter

- **Files:** `src/lens_source.py` (`get_lens_readout(request, source="inferred") -> dict` conforming to `schemas/lens_readout_schema.json`; `inferred_lens_readout` wraps today's self-report probe; `measured_lens_readout` raises `NotImplementedError("measured lens API not yet exposed — see docs/API_FEATURE_REQUEST.md")` but returns the *same* schema shape). Edit `src/run_ablation.py`: obtain `readout_fn` via `lens_source`, add `--lens-source {inferred,measured}` (default inferred); same seam in `run_gate`/`run_swc_session` if trivial. `tests/test_lens_source.py`.
- **Roles:** inferred = executor self-report (no new role). Fully offline-testable with a stub.
- **Metric:** not an experiment — the test suite passing and the swap being literally one flag. Makes the `API_FEATURE_REQUEST.md` "consumer seam" claim real code.
- **Framing:** the day the API exists, the change is `--lens-source measured` + one function body. Zero research signal; makes "built and waiting" true and testable.

### memory-value (folds in B's useful loop-closure slice)

- **Files:** `src/run_memory_value.py` (the experiment AND the loop closure — the **first caller of `lever_ledger.consolidate` and `suggest_levers`**, both wired to nothing today). `tests/test_memory_value.py` (seeded ledger + stub `eval_fn`). No edits to `lever_ledger.py`.
- **Mechanism:** (1) Seed+sleep — over solved cases reuse `run_swc_session` logic to `write_lever`, then `consolidate(ledger, min_support=2)` (offline "sleep" promoting stable beliefs). (2) A/B on held-out case N+1 whose `case_signature` matches/comorbidity-overlaps priors: **COLD** = `format_b_sections_glossed(rec)` as-is; **WARM** = same + inject the `suggest_levers`/consolidated belief's `lever` as a factor-specific consideration (the seam feeding memory into the next input — missing today). (3) Score both with `ab_eval.score` + `counterfactual_report`. Roles: eval_fn = Opus/Sonnet; no predictor. Guardrail hard-gated at write (`validate_lever`) and use.
- **Metric:** WARM−COLD on `guardrail_pass_rate`, `relational_recall`, counterfactual `mean_affected_delta` across matched held-out cases, bootstrap CI. **CONFIRMS** if WARM > COLD, CI excludes 0 (likeliest on guardrail/consistency reliability — in-session T0 can't fix cross-case). **REFUTES** if WARM ≈ COLD (no transfer) or regresses (stale-lever dilution).
- **Framing:** "Done" = the memory loop *exists as a running system* (`consolidate` finally called; `suggest_levers` feeds the next input) AND its value is measured. The likely null ("mechanism runs but memory doesn't beat cold start on re-derivable NHANES cases") is honest and does not generalize to "memory is worthless."

### D — Targeted actuator, powered (demoted, gated)

- **Files:** reuse `src/run_targeted.py`; one edit — add `ablation._bootstrap_ci` on per-case `targeted−base` deltas in its aggregate (it reports point deltas only; matching `ablation.py`'s discipline is what prevents a false positive).
- **Roles:** 3 arms (base / append_all / targeted) over n≥30. Predictor = **Opus** (Fable refuses), selector = **Sonnet**, evaluator = **Opus**.
- **Metric:** targeted−base on `relational_recall` + counterfactual `mean_affected_delta`; pre-register n=30, require CI to exclude 0 on ≥1 metric with **no significant counterfactual regression** (the n=1 risk: rel_recall 0.62>0.50 but counterfactual regressed). **Gate: run only if A shows the surfaced-gap set is behaviorally real.**
- **Framing:** a positive credits "selective grounding of predicted-workspace gaps" — a lens-stand-in-driven actuator win, but NOT the *measured* lens and NOT beyond this task. Either result closes the ours-to-run door decisively.

## 3. Sequencing (cheapest-decisive-first)

1. **C — lens_source adapter.** Hours, offline, no API cost; makes the strongest forward claim concrete. *Runnable now.*
2. **A — QA monitor + injection eval.** Offline pieces first (injectors + scorer + tests), then a bounded live Opus run. Best-prior new signal; most likely to produce the first demonstrated payoff; gates D. *Runnable now (Opus).*
3. **memory-value.** Offline seam + tests, then a modest live A/B. Closes B's loop with a value number. *Runnable now (Opus/Sonnet), moderate cost.*
4. **D — powered targeted run.** *Resource-gated (n≥30 live Opus); run only if A confirms the gap surface is behaviorally real.*
- **coordinator — not scheduled.** Deferred until A or D show a non-flat actuator objective.

## 4. Honest one-paragraph framing

By default these paths **do not overturn** "real, non-redundant signal; no demonstrated payoff *as an optimizer*." The one path that can legitimately upgrade the headline is **A**: a positive there adds the project's first demonstrated payoff, but of **monitoring/detection** — the paper's actually-demonstrated use — changing the sentence to "no optimization payoff, but a demonstrated detection payoff," not resurrecting the optimizer claim. **C** and **memory-value** make two existing claims literally true and testable (consumer-built-and-waiting; the sleep/memory loop runs) without moving the verdict unless memory-value surprises positive on cross-case guardrail reliability. **D** can only close the ours-to-run optimization door — a modest actuator win (still not the measured lens) or a clean null. The **measured-lens API** remains the only route to the high-ceiling optimization claim and is not ours to run. Net: the honest verdict stands unless A fires, and if it does, it upgrades the *detection* story — the more defensible claim the evidence has pointed to all along.
