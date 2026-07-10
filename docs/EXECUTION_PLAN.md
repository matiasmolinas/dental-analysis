# Consolidated execution plan — all outstanding suggestions

> 2026-07-10. Sequences every pending suggestion from the lens-closure + Phase-3 + harness-evolution
> analyses, with honest **offline vs billed** flags and **gating** so we don't burn spend on
> expected-nulls or adopt frameworks before measuring value. Cheapest-decisive-first.

## Track 1 — Harness evolution (gated on one measurement) — **RESOLVED: adopt nothing**

**1a. Decision gate: `run_memory_value.py` — DONE (2026-07-10).** Verdict **`memory_inconclusive`**:
WARM−COLD mean 0 on all axes, CIs straddle 0 (relational_recall [−0.083,+0.083]), WARM mixed-to-
negative per case — at the weakest bar (`min_support=1`, 1 belief from 1/4 seeded levers). Cross-
session trace-consolidation did not beat a cold start. Full analysis:
[`analysis/memory-value-result.md`](analysis/memory-value-result.md).

**1b. Applied — `memory_inconclusive` → adopt nothing.**
- **llmunix / skillos: all CUT stands.** Fable's transitivity premise is now measured — deterministic
  guardrailed consolidation yields WARM−COLD ≈ 0, so a noisier LLM "dream" pass over self-graded
  traces cannot yield more. Automating the loop would automate a null.
- **No hand-extension of `lever_ledger.py`** (that was gated on `memory_adds_value`, which did not
  fire). The ~80-line ideas list + anti-overfitting rubric stay in the drawer for a future task that
  ever shows consolidation value.
- Harness-evolution track closed honestly; durable value remains **Track 2**.

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
