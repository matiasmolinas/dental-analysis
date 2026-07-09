---
name: harness-evolution
description: How the Lens Observer drives evolution of the code harness (parsers, deterministic relational analyzers, any code tool the agents rely on) when the inferred lens shows a deficiency is better fixed in code than in a prompt. Defines the prompt-vs-code boundary, the test-before-use rule, and how a harness-computed value becomes an injected variable the lens then re-checks. Instrument skill for the Observer; guardrail-protected; non-diagnostic.
---

# Harness Evolution (Observer instrument)

Some deficiencies are not prompt problems — they are code problems. When the lens
shows the model cannot reliably *represent* or *derive* a required value, the right
fix is deterministic code, not more prompting. This skill defines that boundary and
the loop that closes it.

## The prompt-vs-code boundary

Fix it in **code (harness)** when:
- a required variable is **dropped or malformed** by input handling
  (`wrong_value` recurring) → fix/extend a **parser**;
- a relation is **deterministic** (a threshold, a ratio, a category, a delta over
  time) that the model keeps **approximating** (recurring low-confidence mediator or
  `wrong_value`) → compute it in a **deterministic analyzer**;
- the value must be **reproducible and auditable** for the clinical-research user.

Fix it in a **prompt / skill / KB** when:
- the concept is present but **unglossed / unmentioned** (`missing_mediator`);
- a **procedure step** is skipped (`uncovered_cot_step`);
- the **problem framing** is under-specified.

Rule of thumb: **deterministic + reproducible → code; representational + semantic →
prompt.** Never move value *imputation* into code — a missing datum stays a collection
flag; the harness may compute *structural* signals from present data only.

## The closed loop (lens → code → injected variable → lens)

1. The Observer diagnoses a code-appropriate deficiency and emits a `harness_code`
   edit (`schemas/deficiency_map_schema.json`, `requires_test: true`, tier
   `T1_promoted`).
2. Generate or modify the parser/analyzer in `src/`. Keep it pure and dependency-light
   so it loads without a GPU (like the rest of `src/`).
3. **Test before use** — write/extend a test in `tests/`; the generated + existing
   suite must pass in a sandbox before the output is trusted.
4. Expose the computed value as an **injected variable** in the prompt package.
5. Re-run the executor; the Observer **re-checks the readout** — did making the value
   explicit and correct surface the mediator / cover the step?

## Reference implementation

`src/relational_signals.py` is the worked example: a deterministic, non-diagnostic
analyzer that turns a normalized record into structural oral-systemic signal flags
(inflammatory burden band from BOP%, metabolic-load band, progression delta) and an
explicit **missing-mediator** list (e.g. `hs_crp` absent → collection flag). Its
outputs are the injected variables the lens re-checks. Tests in
`tests/test_relational_signals.py`.

## Hard rules

- **Test-before-use** for every harness edit (`requires_test: true`).
- **Non-diagnostic / no imputation**: compute structural signals from present data
  only; a missing datum is a collection flag, never a computed patient value.
- Harness edits are **T1 promoted**: gated by held-out accuracy + guardrail pass-rate
  + tests + human approval. Never touch `skills/non-diagnostic-guardrail.md`.
- Keep `src/` pure and importable without a GPU — everything in this project runs on
  Claude, with no GPU-dependent modules.
