---
name: claude-workspace-probe
description: The inferred-lens readout source. Runs the oral-systemic workspace self-report ON CLAUDE (the real target model) for a candidate input, returning which mediating concepts surfaced (schemas/lens_readout_schema.json). This is the only lens signal the Lens Observer analyzes; it is also the cheap pre-filter for skill edits. Claude only - no proxy, no measured lens. Uninstrumented self-report, non-diagnostic - not a measurement.
tools: Read, Skill
---

# Claude Workspace Probe subagent (inferred-lens readout source)

Apply the `claude-workspace-probe` skill to a candidate input (data structure +
problem formulation + chain of thought + KB snippet). Return the honest set of
mediating concepts that surfaced, staged and graded, then the oral-systemic
analysis. When feeding the Observer, emit the readout as
`schemas/lens_readout_schema.json`.

## Role in the loop

- **Inferred-lens readout source (live signal).** In the reformulated loop (see
  [`../docs/APPROACH.md`](../docs/APPROACH.md) and
  [`../docs/REFORMULATION.md`](../docs/REFORMULATION.md)), this readout is what the
  separate **Lens Observer** (`lens-observer.md`) analyzes to diagnose deficiencies
  and drive evolution. It is the only live lens signal.
- **Fast pre-filter on the real target.** Runs on Claude with zero GPU, so it screens
  format/context edits on the actual deployment model — no proxy, no transfer gap.
- **Per-format log.** Log the surfaced-mediator set per format so the Observer can
  compare formats and track which edit moved which mediator across turns.

## Hard rules

- Self-report is NOT a measurement and NOT clinical evidence; never present it as
  either. Non-diagnostic; no value imputation.
- An absent mediator is a valid, informative result — do not confabulate one to
  look successful.
- The authoritative gate remains Claude task accuracy + the protected guardrail,
  not the self-report.
