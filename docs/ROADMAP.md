# Roadmap — two objectives: the best model, and a case-evaluation plugin

> Yes to both, and they are complementary, not rival: **Objective B (a Claude plugin for evaluating new
> cases) packages and delivers Objective A (the best oral-systemic model — harness + ensemble + skills +
> subagents).** They share the same models and the same non-diagnostic guardrail. Stabilize A, ship B;
> B is testable early on whatever A currently is.

## Objective A — the best model (the research + modeling engine)

The goal: a mechanistic + relational agent whose predictions are *validated against public data* and
whose modeling harness Claude can *extend and ensemble* under the tier/guardrail discipline of
[`MODELS.md`](MODELS.md).

- **A1. Empirical anchors on complete datasets** — turn each axis from a scaffold into a data-touched
  result, confounder-adjusted with bootstrap CIs.
  - ✅ **perio ↔ cognition** (NHANES 2011-2012) — the neuro axis anchor (3/4 significant).
  - ✅ **perio → CRP + CV history** (NHANES 2009-2010) — the CV-axis anchor; CRP is co-measured with the
    periodontal exam here, so this validates the mediator the neuro cycle couldn't (`run_perio_cv.py`).
  - ⬜ **the diabetes coupling** (C4: IL-6 → insulin-sensitivity) — anchored to the HbA1c-drop-after-
    therapy meta-analysis + in-cycle NHANES 2009-2010 HbA1c.
- **A2. The ensemble scaffold** ([`MODELS.md`](MODELS.md) §6) — a **model registry** (one dict per
  sub-model with a `gain_coupling` hook + a `tier`), a **composition layer** (series / parallel-fork /
  feedback / operator-split), and an **ensemble/UQ driver** (Latin-hypercube sweeps, Sobol sensitivity,
  Bayesian model averaging, Gillespie for rare events) that outputs an **envelope over the ε/`gain`
  sweep**, never a point. This is what makes "adjust the ensemble" a real operation.
- **A3. The next axes as code** — the disciplined additions from [`MODELS.md`](MODELS.md) §5, each with a
  data path: CV inflammation-wave (A3), microglial hub (B2), the diabetes coupling (C4). Only models
  that couple to the shared `gain` **and** have a public-data anchor.
- **A4. Modeling skills + subagents** — a `modeling-technique-selector` subagent that picks a technique
  (compartmental / control / nonlinear / network / stochastic / cross-domain analogy *with its
  falsification gate*), instantiates it as a registry entry, calibrates it, and hands it to the
  ensemble; a `guardrail-verifier` pass enforces non-diagnostic framing and the analogy gates.

**"Stable" means:** every built axis has a bootstrap-CI'd anchor on public data, the ensemble reports
ranges with tier labels, and the guardrail/traceability tests stay green.

## Objective B — the case-evaluation plugin (the delivery surface)

The goal: a **Claude Code plugin** so a user can feed a *new case* (an integrated oral + systemic
record) and get non-diagnostic oral-systemic **hypotheses + mechanistic predictions with ranges**,
under the guardrail. Feasible today because `agents/` and `skills/` are already Claude Code artifacts;
what's missing is packaging + exposing the harness as tools.

- **B1. Package** — a `plugin.json` / marketplace manifest bundling the existing subagents (`agents/`),
  skills (`skills/`), and a commands entry (e.g. `/evaluate-case`). Installable like the sibling
  DreamOS/SkillOS plugins.
- **B2. Case-intake flow** — raw record → `record-normalizer` → the relational analysis on Claude
  (`histora.agent`, which already injects the deterministic W1 missing-data directive) → the mechanistic
  harness run on the case's structural stratum → `guardrail-verifier` → a non-diagnostic report
  (relational axes + mechanisms + traceability + predicted CRP/tau/CV ranges + data-collection flags).
- **B3. The harness as callable tools** — thin tool wrappers around `mech_models.centerpiece`,
  `mech_neuro.neuro_centerpiece`, the counterfactual levers, and (read-only, population-level)
  `perio_cognition` / `perio_cv` so Claude can *run the models* on a new case's stratum, not just
  describe them. Non-diagnostic guardrail enforced at the tool boundary (structural bands only; ranges;
  never a patient value).

## How they fit — one picture

```
      OBJECTIVE A (the model)                          OBJECTIVE B (the plugin)
   ┌───────────────────────────┐                    ┌────────────────────────────┐
   │ mechanistic harness       │                    │ plugin.json + /evaluate-case│
   │  + ensemble/UQ            │  ── packaged by ──► │ subagents + skills          │
   │  + public-data anchors    │                    │ + harness-as-tools          │
   │  + modeling subagents     │  ◄── new cases ──   │ (non-diagnostic, guardrailed)│
   └───────────────────────────┘   test & refine    └────────────────────────────┘
```

**Shared invariant across both:** one shared inflammatory-`gain`, every prediction a swept range with a
tier label, every imported model carrying its validation/falsification condition, and the protected
non-diagnostic guardrail — never a diagnosis, never an imputed patient value.

## Sequence (honest, cheapest-decisive-first)

1. **A1** — finish the empirical anchors (CV anchor running now; then C4 diabetes). *In progress.*
2. **A2** — build the ensemble scaffold (registry + compose + UQ). *The prerequisite for "adjust the ensemble."*
3. **B1–B3** — package the plugin around the current model (testable early), then keep it in lockstep as
   A3/A4 add axes.
4. **A3/A4** — grow axes and modeling subagents under the tier/guardrail discipline.

The plugin can be built and tested against the *current* model before the ensemble is finished — so the
two objectives proceed in parallel once A2 exists, with B always delivering the latest stable A.
