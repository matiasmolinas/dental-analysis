# HISTORA — Oral-Systemic Intelligence Agent

> A **non-diagnostic** research agent that relates periodontal (gum) disease to systemic disease —
> **cardiovascular and Alzheimer's / neurodegeneration** — by (1) surfacing oral-systemic risk
> **hypotheses** from a patient's data and (2) building and running **mechanistic mathematical models**
> of the candidate pathways, **validated against public data**. It turns *"these things co-occur"* into
> *"here is a candidate mechanism, simulated, checked against real data, with honest uncertainty."*
> It never diagnoses and never imputes a patient value.
>
> **New here? Start with [`docs/VISION.md`](docs/VISION.md) (the why, for clinicians + engineers) and
> [`docs/SOLUTION.md`](docs/SOLUTION.md) (the how).**

## The problem

Periodontal disease is common, chronic, and inflammatory. A growing body of evidence links it to
**cardiovascular disease** and, more recently, **Alzheimer's / neurodegeneration** — plausibly through
**systemic inflammation**. But that evidence is split between population statistics on one side and
disconnected molecular mechanisms on the other. HISTORA bridges them: a hypothesis-generating agent
with a mechanistic-modeling backbone and an empirical-validation layer, built to occupy the honest
terrain of *plausible-but-unproven* — generating prioritized, testable, non-diagnostic hypotheses and
flagging the confounders, never overclaiming.

## The hackathon

Co-organized with **Gladstone Institutes**, a leader in neurodegeneration research (tau, APOE4,
microglia/neuroinflammation, the blood-brain barrier). HISTORA's **oral → neuro axis** — periodontitis
→ systemic inflammation → neuroinflammation → tau propagation — offers Gladstone-adjacent labs a
**novel upstream perturbation** to plug into their existing tau/microglia/BBB frameworks. The project
also explores, *indirectly*, Anthropic's global-workspace ("Jacobian lens") interpretability paper —
see the honest note under [What we explored and set aside](#what-we-explored-and-set-aside).

## The solution that works

One shared quantity — the **effective inflammatory gain** (excess IL-6) — links a periodontal
inflammatory source to three systemic axes:

```
 periodontal severity ─► IL-6 ─► hepatic CRP        (calibrated to the real ~0.5 mg/L
 (structural, non-diagnostic)     turnover, t½≈19h    ΔhsCRP-after-periodontal-therapy anchor)
                                        │
                     ┌──────────────────┼───────────────────────┐
              METABOLIC             CARDIOVASCULAR             NEURO
        (insulin sensitivity)  (endothelium / atherosclerosis,  (neuroinflammation → tau-spread α →
                                wall shear stress, IL-6→CRP)     Fisher–KPP propagation on the connectome)
```

1. **Mechanistic-modeling harness** — pure-python tools that *formulate and run* mechanistic models
   (ODEs, control theory, fluid transport, ecological dynamics), grounded in a **curated, cited model
   library** ([`docs/model-library.md`](docs/model-library.md), ~30 confidence-tiered models). The
   centerpiece chain is calibrated to a real interventional anchor and forks to the CV and neuro axes;
   every uncertain coupling is **flagged and swept as a range**, never asserted.
   `src/mech_ode.py`, `src/mech_models.py`, `src/mech_calibrate.py`, `src/mech_neuro.py`.
2. **Empirical validation** — the **periodontitis ↔ cognition association** on real **NHANES 2011-2012**
   (n=919 older adults): **3 of 4 cognitive measures show a significant, confounder-adjusted
   (age/education/smoking/HbA1c) negative association** with periodontal severity — the direction the
   mechanistic model predicts. Reproducible with pure-python stats + bootstrap CIs.
   `src/perio_cognition.py`, [`docs/analysis/perio-cognition-result.md`](docs/analysis/perio-cognition-result.md).
3. **Non-diagnostic relational agent** — generates structured oral↔CV↔neuro research hypotheses with
   full traceability and a **protected guardrail** (never a diagnosis, never an imputed value, enforced
   at write time). `src/relational_signals.py`, `src/ab_eval.py`, `schemas/output_schema.json`.
4. **An honest experimental apparatus** — A/B, ablation, counterfactual-sensitivity, all with
   bootstrap confidence intervals. The discipline that produced rigorous results (including rigorous
   negatives). `src/ablation.py`, `src/counterfactual.py`.
5. **The execution-gap capability** — the one robust way found to improve the agent's inputs:
   **externalize a deterministic structural step the model *knows* but *drops* in situ** (validated:
   missing-data flagging **0 → 1.0**). A pre-A/B predictor + a 3-arm A/B to scale it.
   `src/exec_gap.py`, [`docs/analysis/lens-recipes-and-the-execution-gap.md`](docs/analysis/lens-recipes-and-the-execution-gap.md).

## What we explored and set aside

The project rigorously investigated whether reading a model's internal **workspace** (the *Jacobian
lens*) could optimize the agent's inputs and evolve its harness. The answer is a **rigorous negative
with a precise explanation**: on tasks within a capable model's competence, the lens is redundant with
*(the output + a competent reader's own knowledge)* — so reading it adds nothing over reading the
output with a capable model. Cross-session memory/consolidation was likewise **inconclusive**. These
negatives are documented honestly and they *sharpened* the positive: the durable value — the
mechanistic models, the empirical validation, and the execution-gap capability — depends on none of
them. Full trail: [`docs/analysis/`](docs/analysis/README.md); canonical technical record:
[`docs/RESEARCH_SUMMARY.md`](docs/RESEARCH_SUMMARY.md).

## Run it

Everything in the core runs on **pure Python** (no GPU, no notebook); the mechanistic models and the
NHANES validation need only `numpy`/`pandas` at run time.

```bash
python src/run_mechanistic.py       # the centerpiece: periodontal source → IL-6/CRP → CV & neuro axes
python src/run_mech_neuro.py        # the neuro axis: neuroinflammation → tau spread (Braak-ordered)
python src/run_perio_cognition.py   # the empirical validation on real NHANES 2011-2012 (needs network)
python -m pytest tests/ -q          # or run each tests/test_*.py — pure-python harness, 120+ tests
```

## Layout

```
dental-analysis/
  src/
    mech_ode.py / mech_models.py / mech_calibrate.py / mech_neuro.py   # the mechanistic harness
    perio_cognition.py / nhanes_neuro_loader.py                        # the empirical validation
    ab_eval.py / ablation.py / counterfactual.py                       # the honest apparatus
    relational_signals.py / bridge_concepts.py / record_formats.py     # the relational signals + concepts
    exec_gap.py                                                        # the execution-gap capability
    nhanes_mapping.py / nhanes_loader.py                               # NHANES data mapping + loader
  schemas/          # non-diagnostic output contract + examples
  agents/ skills/   # the Claude Code agent + skill catalog (see their README.md)
  docs/             # VISION, SOLUTION, model-library, RESEARCH_SUMMARY, DATASETS, analysis trail
  tests/            # pure-python harness tests (no GPU)
```

## Data & guardrails

Grounded in **public, de-identified NHANES** (2009-2010 for the periodontal + cardiovascular +
inflammatory anchor; 2011-2012 for the periodontal + cognitive battery), plus a curated mechanistic
model library from the peer-reviewed literature. **Non-diagnostic throughout:** research hypotheses and
mechanistic models only; missing data is a collection flag, never an imputed value; every relational
axis cites the input fields it was derived from. Honest by design: hypothesis-level couplings are
flagged and reported as ranges, and the one failed causal drug test of the periodontitis→Alzheimer
hypothesis (atuzaginstat / GAIN) is named as the standing caveat. See [`docs/DATASETS.md`](docs/DATASETS.md).
