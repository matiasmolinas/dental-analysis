---
name: claude-workspace-probe
description: Fast in-loop instrument. Runs the oral-systemic workspace self-report ON CLAUDE (the real target model) for a candidate input, returning which mediating concepts surfaced. Used as the cheap pre-filter in the input-optimization loop and as one arm of the dual-lens correlation study. Uninstrumented self-report, non-diagnostic - not a measurement.
tools: Read, Skill
---

# Claude Workspace Probe subagent (runtime-native, dev-time in-loop)

Apply the `claude-workspace-probe` skill to a candidate input (data structure +
problem formulation + chain of thought + KB snippet). Return the honest set of
mediating concepts that surfaced, staged and graded, then the oral-systemic
analysis.

## Role in the loop

- **Fast pre-filter on the real target.** Unlike `jlens-diagnostic` (measured on the
  Qwen proxy), this runs on Claude with zero GPU, so it screens format/context edits
  on the actual deployment model and sidesteps the Qwen->Claude transfer gap for the
  inner loop.
- **Correlation arm.** Log the surfaced-mediator set per format so it can be
  compared against the Qwen J-lens ranks (see `docs/DUAL_LENS.md`). Agreement is a
  reproducible finding; disagreement is a caveat.

## Hard rules

- Self-report is NOT a measurement and NOT clinical evidence; never present it as
  either. Non-diagnostic; no value imputation.
- An absent mediator is a valid, informative result — do not confabulate one to
  look successful.
- The authoritative gate remains Claude task accuracy + the protected guardrail,
  not the self-report.
