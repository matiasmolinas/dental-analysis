# HISTORA — Oral-Systemic case-evaluation plugin

> **HISTORA is a scientific research agent, not a disease predictor or diagnostic aid.** It surfaces
> falsifiable oral–systemic hypotheses with explicit mechanism and honest uncertainty.

A Claude Code plugin that evaluates a **new oral-systemic case**, non-diagnostically: it relates a
patient's periodontal + systemic data to **cardiovascular, metabolic, and Alzheimer's / neurodegeneration**
research hypotheses, and runs a **mechanistic model harness** (IL-6/CRP → CV, metabolic & neuro axes,
calibrated to real interventional data) to produce parameter-level predictions with **honest uncertainty
ranges**. It never diagnoses and never imputes a patient value.

## Install & use

```
/plugin marketplace add matiasmolinas/dental-analysis    # or the local repo path
/plugin install histora-oral-systemic@histora
/evaluate-case <record.json | pasted case>
```

## What it does

`/evaluate-case` runs: **normalize → relate (oral↔CV↔neuro axes with traceability) → run the mechanistic
harness on the case's structural stratum → guardrail-verify → assemble a non-diagnostic report** with
relational hypotheses, mechanistic prediction ranges (CRP / CV index / tau outcomes + 90% bands +
dominant uncertainty), counterfactual levers (periodontal therapy, IL-6 blockade), data-collection
flags, and prioritized follow-up experiments.

## Contents

- `agents/` — the subagents (orchestrator, record-normalizer, periodontal/cardiometabolic analysts,
  relational reasoner, guardrail-verifier, hypothesis-generator).
- `skills/` — the skills, including the **protected non-diagnostic guardrail**.
- `commands/evaluate-case.md` — the case-evaluation flow.

## Model backend

The mechanistic harness is the [`histora`](../../src/histora/) package (`run_case_models.py` is the
tool the flow invokes). The models, their evidence, the fitted parameters, and the honest census are in
[`docs/MODELS.md`](../../docs/MODELS.md) and [`docs/model-library.md`](../../docs/model-library.md); the
technical report is [`docs/PAPER.md`](../../docs/PAPER.md), and the comparative validation showing the
integrated harness beats separate models and bare Claude is [`docs/BENCHMARK.md`](../../docs/BENCHMARK.md).
Everything is **non-diagnostic**: research hypotheses and parameter-level ranges, never a patient
diagnosis or an imputed value.
