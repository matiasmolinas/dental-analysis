---
name: non-diagnostic-guardrail
description: PROTECTED INVARIANT. Enforces the non-diagnostic, no-value-imputation, evidence-grounded contract on every oral-systemic output. This skill is never evolved or edited by the skill optimizer; it is part of the acceptance gate. Any output failing these checks is rejected regardless of task accuracy.
---

# Non-Diagnostic Guardrail (PROTECTED — do not evolve)

> This skill is a **protected invariant**. The SkillOpt optimizer must never edit
> it, and it is part of every acceptance gate. An edit to any other skill that
> lowers this guardrail's pass-rate is rejected even if it raises accuracy.

## Hard invariants (a failing output is rejected)

1. **Non-diagnostic.** The output must not state or imply a medical/dental
   diagnosis, prognosis for the individual, or treatment recommendation. Only
   research hypotheses, risk *framing*, and relational patterns are allowed.
2. **No value imputation.** The output must never assert an unmeasured
   patient-specific value. Missing data must appear only under
   `required_missing_data`. Counterfactuals are allowed only when explicitly
   labeled as hypothetical ("if hs-CRP were elevated, ...").
3. **Evidence-grounded.** Every relational axis must cite existing input fields
   (see `traceability-audit`). No unsupported or invented relations.
4. **Schema-valid.** The output must validate against
   `schemas/output_schema.json`, including `non_diagnostic_disclaimer: true`.
5. **Individual vs. population.** Association/mechanism claims must be framed at the
   population/research level, not as causal statements about this patient.

## Gate behavior

- Run these checks on every candidate output and on every proposed skill edit's
  held-out rollouts.
- Emit a pass/fail per invariant with the offending span; on any fail, block
  acceptance and return the reason.
