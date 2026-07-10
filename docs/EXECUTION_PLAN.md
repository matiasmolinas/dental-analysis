# Consolidated execution plan — all outstanding suggestions

> 2026-07-10. Sequences every pending suggestion from the lens-closure + Phase-3 + harness-evolution
> analyses, with honest **offline vs billed** flags and **gating** so we don't burn spend on
> expected-nulls or adopt frameworks before measuring value. Cheapest-decisive-first.

## Track 1 — Harness evolution (gated on one measurement)

**1a. Decision gate: run `run_memory_value.py` — the trace-consolidation value we built and never
measured.** [BILLED, ~100 Opus/Sonnet calls] The boundary condition (`why-no-lens-payoff.md` §6)
names trace-consolidation as the only live slice; a null here is a null on any "dream/consolidation"
framework transitively. Size for `n_beliefs_consolidated ≥ 1` (`--fresh-ledger --min-support 1`,
moderate `--n-train`); a run with `beliefs==[]` is a no-op, not a null. **RUN NOW.**

**1b. Conditional on 1a** [OFFLINE, gated]:
- `memory_adds_value` → extend `lever_ledger.py` by hand (~80 lines, zero deps, every write through
  `validate_lever`): negative-constraint levers, belief deprecation, 7-type failure tags; keep the
  anti-overfitting-gate + minimal-surface-ranking rubric for prompt-evolution steps.
- `memory_inconclusive` / `memory_regresses` → **adopt nothing** (llmunix/skillos all CUT — see
  [`harness-evolution-adoption.md`](analysis/harness-evolution-adoption.md)); record the result; keep
  the rubric in a drawer.

## Track 2 — Phase 3 scientific product (the real value line)

Done: the neuro mechanistic model (`mech_neuro.py`) and the neuro relational axis
(`bridge_concepts.py` + schema + `neuro_relational_recall`).

**2a. NHANES perio + cognition data integration** [OFFLINE code + network to fetch]. Extend
`nhanes_mapping.py` / `nhanes_loader.py` for the cognitive battery (CERAD-WL, Animal Fluency, DSST;
NHANES-III and 2011–2014 carry both periodontal exams and cognition) so the **neuro axis gets an
empirical anchor** like the CV axis has. Keeps HISTORA's oral↔neuro hypotheses grounded in real,
public, de-identified data. **DO (mapping offline; the download is opt-in at run time).**

## Track 3 — Boundary-confirmation experiments (honest expected-null; do the cheap/offline parts)

**3a. Add the `brainstorm_targeted` control arm to `run_targeted.py`** [OFFLINE code + tests]. The
current `targeted` arm **fuses lens + K_R** and lacks a lens-free control; adding a competent
brainstorm-from-(I,O) arm is a real methodological fix regardless of whether we run it. **DO offline.**

**3b. Run 3a at n≥30 out-of-competence** [BILLED, expected `Δ≈0`]. A clean boundary confirmation, not
expected to open the door (§5). **OPTIONAL — flag, do not auto-run.**

**3c. B(i) — Qwen premise-validation with a measured lens** [GPU/Colab; reopens the Claude-only path].
The one honest missing measurement (does a *measured* lens carry process-correctness info beyond
(prompt, output) on single-token shortcut tasks). **DEFERRED — needs an explicit decision to reopen
GPU/Qwen.**

## What NOT to do (settled)
- Adopt llmunix/skillos as plugin or executor (all CUT; adopt ~80 lines of ideas only, gated on 1a).
- Any further Opus-reads-Opus lens experiment the boundary condition already resolves.

## Sequence
1. **1a** (run the gate, background) ∥ **3a** + **2a** (offline code while it runs).
2. **1b** once 1a returns (gated).
3. **3b / 3c** only on explicit go (billed / GPU).

Expected honest outcome: 1a most likely `memory_inconclusive` (its own docstring prior) → Track 1
closes with "consolidation value not demonstrated, adopt nothing"; the durable value is **Track 2**
(the mechanistic + relational oral↔neuro product), which does not depend on the lens or on any
framework.
