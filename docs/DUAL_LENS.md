# Dual-Lens Methodology

Two instruments read the "workspace" that our input optimization targets. They
measure **different models** with **different epistemics**, and using both — plus
the correlation between them — is the core methodological contribution.

## The two instruments

| | **Claude workspace probe** (self-report) | **Jacobian lens** (measured) |
|---|---|---|
| Skill / agent | `claude-workspace-probe` | `jlens-diagnostic` |
| Model inspected | **Claude** (the real target) | **Qwen** (open-weights proxy) |
| Nature | Qualitative introspective self-report | Quantitative mechanistic measurement (vocab ranks) |
| Ground truth | None — can confabulate | Yes — real activations |
| Causal test | No | Yes (representation swaps) |
| Infra | Zero (runs on the API you already have) | GPU (Colab T4/L4 for 4B) |
| Captures CoT | Natively (staged early/mid/late) | Only if the harness reads the generated span |
| Reproducible | Low | High |
| Attribution | Inspired by `Doriandarko/skirano-skills` j-space-lens | `anthropics/jacobian-lens` |

Neither is "better" — they are complementary. The probe reads the deployment model
cheaply but without ground truth; the lens measures rigorously but on a proxy.

## The dual loop

```
                 candidate input (data structure + problem formulation + CoT + KB)
                        │
        ┌───────────────┴────────────────┐
        ▼                                 ▼
 Claude workspace probe            Qwen J-lens (measured)
 (fast, on the target,             (ground-truth, causal,
  no GPU) → surfaced mediators      offline) → mediator ranks
        │                                 │
        └───────────────┬────────────────┘
                        ▼
       Claude controller edits format/context/KB
       (prompts/controller.md); iterate until mediators surface
                        ▼
       Claude evaluator (authoritative gate: task accuracy + guardrail)
                        ▼
       learning → SkillOpt-style autonomous evolution of skills/subagents
```

**Inner loop (fast):** the Claude workspace probe screens format/context edits on
the real target model with no GPU, sidestepping the Qwen→Claude transfer gap for
optimization. **Outer validation (rigorous):** the measured J-lens on Qwen confirms
the self-report is not confabulation and provides a reproducible, causal signal.

## The correlation experiment (Research-track deliverable)

Run the same set of candidate formats through both instruments and test whether
they agree.

- **Setup:** N record formats × the fixed bridge-concept target set.
- **Signal A (probe):** per format, the set/rank of mediators Claude self-reports as
  active (`claude-workspace-probe`).
- **Signal B (lens):** per format, the measured workspace-band rank of each mediator
  on Qwen (`src/harness.py::concept_ranks`).
- **Metric:** rank correlation (Spearman) between the format orderings each
  instrument induces, and per-mediator agreement.
- **Interpretations:**
  - **Agreement** → Claude's uninstrumented self-report predicts the measured
    J-space on open models: a novel, reproducible finding, and it justifies using
    the cheap probe as the primary in-loop signal.
  - **Disagreement** → a caveat about trusting self-report; fall back to the
    measured lens for the load-bearing decisions. Still a finding.

This experiment is the reproducible artifact that makes a strong **Research-track**
submission, alongside the **Build-track** tool it optimizes.

## Guardrails on interpretation

- The probe is **self-report, not measurement** — never label it otherwise in
  outputs, demos, or claims.
- Both instruments optimize the *input/skills*; neither is itself the source of
  clinical accuracy. The authoritative gate is Claude task accuracy + the protected
  non-diagnostic guardrail.
- Non-diagnostic throughout: missing data is a collection flag, never imputed.
