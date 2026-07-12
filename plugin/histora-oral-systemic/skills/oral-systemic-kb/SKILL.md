---
name: oral-systemic-kb
description: Retrievable knowledge base of the biological mechanisms linking periodontal disease and cardiovascular risk (inflammatory, metabolic, behavioral, vascular pathways). Injected as context to activate the model's internal representation of mediating concepts. Reference content; used by the relational reasoner and as the KB the SkillOpt loop optimizes.
---

# Oral-Systemic Knowledge Base (mediating mechanisms)

Concise, retrievable mechanism notes that prime the mediating concepts. Inject the
relevant snippet(s) as context; keep it short (the SkillOpt loop measures whether a
snippet actually raises mediator representation vs. being redundant).

## Inflammatory axis (primary)

Periodontitis sustains a chronic gram-negative biofilm and ulcerated pocket
epithelium, allowing bacterial products and periodontal bacteremia to enter
circulation. This raises **systemic inflammatory burden** — elevated **C-reactive
protein (hs-CRP)**, IL-6, TNF-alpha — which promotes **endothelial dysfunction**,
oxidative stress, and progression of **atherosclerosis**, linking oral inflammation
to **cardiovascular risk**.

## Metabolic axis

Diabetes is bidirectional with periodontitis: hyperglycemia worsens periodontal
inflammation and tissue breakdown, and periodontal inflammation impairs glycemic
control. HbA1c is the shared metabolic marker; the inflammatory mediators above are
the common currency with cardiovascular risk.

## Behavioral (shared) axis

Smoking is an independent risk factor for both periodontitis and cardiovascular
disease, confounding and amplifying the association; it also suppresses bleeding on
probing, so severity can be under-read from BOP alone in smokers.

## Vascular axis

Endothelial dysfunction and atherosclerotic plaque are the downstream vascular
substrate; markers include impaired flow-mediated dilation and elevated
inflammatory/atherogenic profiles.

## Grounding / citable sources

Ground snippets in these rather than free-form assertion, and mirror their
non-causal language:

- **American Heart Association scientific statement** on periodontal disease and
  atherosclerotic cardiovascular disease — states the link is an **association, not
  established causation**; proposed mechanisms are bacteremia and systemic
  inflammation (CRP, IL-6, TNF-alpha). Use its framing to keep claims non-diagnostic.
- **HOMD** (Human Oral Microbiome Database) — curated oral taxa; pairs with the
  NHANES Oral Microbiome layer (see `docs/DATASETS.md`) to name specific
  periodontal pathogens in the bacteremia/microbial pathway.
- A small **PubMed/PMC** corpus (retrieved, not memorized) for case-specific
  citations behind each hypothesized mechanism (RAG). Keep retrieved evidence
  traceable so `traceability-audit` can check it.

## Usage notes

- These are **associations and hypothesized mechanisms** for research framing, not
  causal claims about an individual patient.
- Prefer the shortest snippet that names the mediators relevant to the case; let
  the SkillOpt A/B decide whether it earns its place.
