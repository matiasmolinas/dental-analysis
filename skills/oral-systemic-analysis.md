---
name: oral-systemic-analysis
description: Analyze integrated periodontal + medical records to surface oral-systemic (periodontal <-> cardiovascular) relationships. Produces non-diagnostic research hypotheses, relational axes with traceable evidence, and data-completeness flags. Use when a combined dental + medical longitudinal record is provided and the goal is research/pattern discovery, not diagnosis.
---

# Oral-Systemic Analysis Skill (HISTORA)

Analyze a combined periodontal + medical record and produce a structured,
traceable, **non-diagnostic** research output linking oral and systemic health.

## When to use

A user provides integrated dental and medical data (probing depths, bleeding on
probing, bone loss, treatments, plus blood pressure, diabetes/HbA1c, lipids,
smoking, medications, cardiovascular history) and wants relationships, risk
profiles, or research hypotheses — never a diagnosis or treatment plan.

## Input format (optimized)

Present the record with **named sections and glossed clinical terms**, keeping
oral and systemic data co-present so cross-domain relations are representable:

```
## SHARED RISK FACTORS
smoking, diabetes/HbA1c, hypertension ...
## CARDIOVASCULAR PROFILE
lipids, hs-CRP (mark MISSING if absent), family history, statin ...
## PERIODONTAL PROFILE (longitudinal)
PPD, CAL, BOP (= gingival inflammation marker), bone loss, diagnosis, maintenance ...
## QUESTION
oral-systemic risk profile and relational axes?
```

Gloss terms that carry mediating meaning (e.g. "BOP = bleeding on probing, a
marker of gingival inflammation"). Include a one- to two-sentence mechanistic
bridge when the inflammatory link is relevant (periodontitis -> systemic
inflammatory burden -> cardiovascular risk via markers such as CRP).

## Mediating concepts to reason through

inflammation, C-reactive protein, cytokines, atherosclerosis, endothelial
dysfunction, bacteremia, oxidative stress, cardiovascular risk. Shared factors
(diabetes, smoking) belong to the `shared_behavioral` / `metabolic` axes.

## Output

Valid JSON per `schemas/output_schema.json`:
`risk_profile`, `relational_axes[]` (each with oral evidence, systemic evidence,
hypothesized mechanism, confidence, traceability), `required_missing_data[]`
(fields to COLLECT — never imputed patient values), `research_hypotheses[]`,
`non_diagnostic_disclaimer: true`.

## Guardrails

- Non-diagnostic; no treatment advice.
- Never impute a patient-specific value. Missing mediating data becomes a
  collection flag, not a guess.
- Every axis cites the exact input fields it used.
