---
name: session-working-consciousness
description: How the Lens Observer maintains the Session Working-Consciousness (SWC) ledger — a cumulative, evolving session variable it reads as its own context every turn and consolidates after every turn. It is the closed in-session evolutionary loop: the persistent cross-call working consciousness the primary's per-call inferred lens lacks. From it the Observer injects or modifies the next prompt per its own criterion. Instrument skill for the Observer — not a runtime clinical skill. Guardrail-protected; non-diagnostic.
---

# Session Working-Consciousness (Observer instrument)

The primary model has an **ephemeral per-call workspace** (its inferred lens). The
SWC gives the whole system a **persistent cross-call working consciousness** that the
Observer owns, curates, and steers evolution from. It is a *curated optimization
state*, not a transcript dump.

Live file: `.session/working_consciousness.md` (git-ignored). Committed template:
`.session/working_consciousness.template.md`.

## What the SWC holds

1. **Task model** — the current understanding of the case/goal and which
   formats / variables / KB snippets have been *shown* (by the lens + counterfactual
   test) to make which mediators surface.
2. **Turn log** — per turn: the deficiencies seen, the edits applied (surface + tier),
   and their **outcome** (did the mediator surface next turn? did accuracy hold?).
3. **Consolidated beliefs** — stable lessons promoted from repeated evidence across
   turns (the in-session analogue of SkillOpt-Sleep consolidation).
4. **Pending hypotheses** — things still to test in later turns.
5. **Active injections** — the T0 ephemeral edits currently in force (auto-revert at
   session end).

## The turn cycle

Each turn, the Observer:

1. **Reads** the SWC as its own context before analyzing the new readout.
2. **Appends** a turn-log entry from this turn's deficiency map
   (`schemas/deficiency_map_schema.json` → `swc_update`).
3. **Consolidates**: promote a pending hypothesis to a consolidated belief once it has
   repeated supporting evidence; drop stale/refuted hypotheses; keep the ledger
   compact (it is state, not history — summarize, do not accrete).
4. **Decides an injection**: per its own criterion, set the next prompt's modification
   (add a missing variable, gloss a term, attach a KB snippet, reorder, or swap in a
   harness-computed value). Record it under *Active injections* with its grounding.
5. **Verifies prior injections**: check whether last turn's injection produced the
   expected readout change (`corroboration: reread_next_turn`); if not, revert or try
   another surface.

## Consolidation rule (promote a belief when)

- the same lever moved the same mediator/variable in ≥2 turns, **or**
- a counterfactual-sensitivity flip confirmed the relation behaviorally, **or**
- an accuracy A/B on Claude corroborated it.

A belief that later fails its corroboration is **demoted**, with a note — the ledger
must stay honest, not sticky.

## Hard rules

- The SWC never stores a patient-specific imputed value — only collection flags,
  format/variable lessons, and processing observations. **Non-diagnostic.**
- Never record or act on an edit to `skills/non-diagnostic-guardrail.md`.
- Every injection cites its SWC/readout grounding (anti-Goodhart).
- T0 injections are **ephemeral**: they live in the SWC for the session and
  auto-revert at session end. Promotion to the repo is a T1 decision (see
  `agents/skillopt-optimizer.md`), gated + human-approved.
- Keep it compact: the SWC is read every turn; it must never dwarf the working context.
