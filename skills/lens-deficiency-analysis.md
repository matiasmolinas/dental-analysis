---
name: lens-deficiency-analysis
description: How the Lens Observer reads the executor's inferred Jacobian-lens readout and turns it into a deficiency map plus bounded, gated evolution edits. Compares the readout (schemas/lens_readout_schema.json) against the required-variable / procedure spec, detects missing/incorrect variables, uncovered chain-of-thought steps, unrepresented mediators, and under-specified problem framing, then routes each gap to one of five evolution surfaces. Instrument skill for the offline/dev-time Observer — not a runtime clinical skill. Anti-Goodhart and guardrail-protected.
---

# Lens Deficiency Analysis (Observer instrument)

Turn the primary's inferred-lens readout into a deficiency map and bounded edits.
Self-report is a readout channel, **not a measurement**; never a claim about the
patient. Return `schemas/deficiency_map_schema.json`.

## Inputs

- The prompt package the executor ran (work prompt + skill + KB context + sub-agent
  def + injected variables).
- The readout (`schemas/lens_readout_schema.json`): `concepts`, `sweep`,
  `required_variables_seen`, `cot_steps_traversed`.
- The **spec**: required mediators, required variables, and expected procedure steps.
- The Session Working-Consciousness ledger.

## Deficiency detection (readout → `kind`)

Check each, in order. Absence is a valid, informative result — do not invent gaps.

1. **`missing_mediator`** — a required bridge concept (inflammation, CRP,
   atherosclerosis, endothelial dysfunction, bacteremia, cytokines, oxidative stress,
   CV risk) is absent from `concepts`, or present only `faint` / `late` / `low`
   confidence. *Evidence:* the concept's readout entry (or its absence).
2. **`missing_variable`** — a required input variable is `present: false` in
   `required_variables_seen`, or never appears in `sweep`. *Evidence:* the
   `required_variables_seen` entry.
3. **`wrong_value`** — a variable is present but `value_plausible: no`. *Evidence:*
   the entry + why the value is implausible. (Prefer a code fix — see routing.)
4. **`uncovered_cot_step`** — an expected step in `cot_steps_traversed` is `skipped`
   or `shallow`. *Evidence:* the step's coverage entry.
5. **`underspecified_problem`** — the readout shows the model never framed the task
   with the variables needed to solve it (mediators absent AND the problem framing
   channel is empty/generic). *Evidence:* the sweep + missing framing concepts.

For each, record `detail`, `evidence`, and `severity`
(`blocking` / `important` / `minor`).

## Routing (deficiency → surface + tier)

| Deficiency | Surface | Default tier |
|---|---|---|
| `missing_mediator` (unglossed term / missing mechanism) | `kb_context` / `work_prompt` / `skill` | T0 |
| `missing_variable` | `injected_variables` (+ `subagent_def` to derive it) | T0 |
| `wrong_value` | `harness_code` (parser fix) → re-inject corrected value | T1 (`requires_test`) |
| `uncovered_cot_step` | `skill` / `subagent_def` (make the step explicit) | T0→T1 if durable |
| relation guessed unreliably (recurring `wrong_value` / low-conf mediator) | `harness_code` (deterministic analyzer) | T1 (`requires_test`) |
| `underspecified_problem` | `work_prompt` / problem-formulation template | T0 |

Prefer the **cheapest surface that fixes the deficiency**. Escalate to `harness_code`
only when the model cannot reliably represent/derive the value in text (see
`skills/harness-evolution` for the prompt-vs-code boundary).

## Emitting edits (bounded + auditable)

Each edit: `surface`, `tier`, `edit_type` (add/delete/replace), `target` (file/field),
the concrete `change`, a `rationale` that **cites the deficiency evidence**, and
`guardrail_safe: true`. Cap edits per turn; keep each small and reversible.

## Corroboration

For load-bearing claims, set `corroboration: counterfactual_sensitivity` and describe
the flip (toggle one factor, e.g. `hs_crp` present↔MISSING; the affected axis should
move, unrelated axes should not — see `docs/DUAL_LENS.md`). Use `reread_next_turn` to
verify a T0 edit actually surfaced the mediator on the following turn.

## Hard rules

- No edit without readout evidence (anti-Goodhart).
- Never edit `skills/non-diagnostic-guardrail.md`; never impute a patient value.
- The authoritative gate is Claude accuracy + guardrail pass-rate; readout ranks are a
  cheap pre-filter, exactly as the measured J-lens was in the baseline plan.
