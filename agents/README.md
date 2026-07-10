# Subagents

> **Status.** The **runtime pipeline** below is the working, non-diagnostic HISTORA agent (see
> [`../docs/VISION.md`](../docs/VISION.md) and [`../docs/SOLUTION.md`](../docs/SOLUTION.md)). The
> **inferred-lens Observer loop** further down was a research investigation that came out a rigorous
> negative (the boundary condition — [`../docs/RESEARCH_SUMMARY.md`](../docs/RESEARCH_SUMMARY.md) §0);
> those instruments are kept as the honest record but are not the product. The protected guardrail is
> unaffected.

Subagent definitions for the HISTORA Oral-Systemic Intelligence Agent, in Claude
Code agent format (frontmatter `name` / `description` / `tools`).

## Runtime pipeline

| File | Role |
|---|---|
| `orchestrator.md` | Main agent: plans, routes, assembles the final output |
| `record-normalizer.md` | Integrates fragmented dental+medical records (HISTORA core) -> schema |
| `periodontal-analyst.md` | 2017 AAP/EFP staging & grading, progression |
| `cardiometabolic-analyst.md` | Non-diagnostic CV/metabolic pathway framing |
| `oral-systemic-relational-reasoner.md` | **Core**: relational axes & mediators (J-lens target) |
| `guardrail-verifier.md` | Adversarial guardrail + traceability gate |
| `hypothesis-generator.md` | Research hypotheses for follow-up |

Flow: normalize -> (periodontal ‖ cardiometabolic) -> relate -> hypotheses ->
verify -> assemble. The verifier can block; nothing failing the guardrail is emitted.

## Inferred-lens Observer loop (in-session / dev-time) — Claude only

| File | Role |
|---|---|
| `lens-observer.md` | **Secondary instance (Opus).** Analyzes the primary's inferred-lens readout, diagnoses deficiencies, curates the Session Working-Consciousness, drives bounded gated evolution of five surfaces + injects prompts |
| `claude-workspace-probe.md` | The inferred-lens readout source ON CLAUDE (real target, no GPU); surfaces mediators per format. Self-report, not a measurement |
| `skillopt-optimizer.md` | **T1 promotion tier.** Evolves the five surfaces (prompts/skills/KB/sub-agent defs+variables/harness code) via bounded rollout->reflect->edit->gate |

The method is archived in [`../docs/analysis/ARCHIVE/APPROACH.md`](../docs/analysis/ARCHIVE/APPROACH.md)
and the verdict in [`../docs/analysis/why-no-lens-payoff.md`](../docs/analysis/why-no-lens-payoff.md).
**Claude only** — no proxy, no measured lens; the paper was explored indirectly via the self-report
skill. Kept as the honest record of a rigorous negative; not part of the working product.

## Skill ↔ subagent map

Each runtime subagent applies one skill from [`../skills/`](../skills/):
normalizer→`record-normalization`, periodontal→`periodontal-staging`,
cardiometabolic→`cardiometabolic-framing`, relational→`oral-systemic-analysis`
(+`oral-systemic-kb`), verifier→`non-diagnostic-guardrail`+`traceability-audit`.

`non-diagnostic-guardrail` is a **protected invariant**: the optimizer never edits it.
