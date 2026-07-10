# HISTORA — Oral-Systemic Intelligence Agent

> A **non-diagnostic** research agent that relates periodontal (gum) disease to systemic disease —
> **cardiovascular and Alzheimer's / neurodegeneration** — by (1) surfacing oral-systemic risk
> **hypotheses** from a patient's data with Claude, and (2) building and running **mechanistic
> mathematical models** of the candidate pathways, **validated against public data**. It turns
> *"these things co-occur"* into *"here is a candidate mechanism, simulated, checked against real data,
> with honest uncertainty."* It never diagnoses and never imputes a patient value.
>
> **New here? Read [`docs/PROBLEM.md`](docs/PROBLEM.md) (the problem, for clinicians + engineers) and
> [`docs/SOLUTION.md`](docs/SOLUTION.md) (how it works).**

## The problem

Periodontal disease is common, chronic, and inflammatory. A growing body of evidence links it to
**cardiovascular disease** and, more recently, **Alzheimer's / neurodegeneration** — plausibly through
**systemic inflammation**. But that evidence is split between population statistics on one side and
disconnected molecular mechanisms on the other. HISTORA bridges them: a hypothesis-generating agent
with a mechanistic-modeling backbone and an empirical-validation layer, built to occupy the honest
terrain of *plausible-but-unproven* — generating prioritized, testable, non-diagnostic hypotheses and
flagging the confounders, never overclaiming. Full description: [`docs/PROBLEM.md`](docs/PROBLEM.md).

## The hackathon

Co-organized with **Gladstone Institutes**, a leader in neurodegeneration research (tau, APOE4,
microglia/neuroinflammation, the blood-brain barrier). HISTORA's **oral → neuro axis** — periodontitis
→ systemic inflammation → neuroinflammation → tau propagation — offers Gladstone-adjacent labs a
**novel upstream perturbation** to plug into their existing tau/microglia/BBB frameworks.

## The solution

One shared quantity — the **effective inflammatory gain** (excess IL-6) — links a periodontal
inflammatory source to systemic axes:

```
 periodontal severity ─► IL-6 ─► hepatic CRP        (calibrated to the real ~0.5 mg/L
 (structural, non-diagnostic)     turnover, t½≈19h    ΔhsCRP-after-periodontal-therapy anchor)
                                        │
                     ┌──────────────────┼───────────────────────┐
              METABOLIC             CARDIOVASCULAR             NEURO
        (insulin sensitivity)  (endothelium / atherosclerosis,  (neuroinflammation → tau-spread α →
                                wall shear stress, IL-6→CRP)     Fisher–KPP propagation on the connectome)
```

1. **Claude-powered relational agent** — given an integrated record, Claude produces structured,
   non-diagnostic oral↔CV↔neuro hypotheses (relational axes + mechanisms + full traceability + missing-
   data flags). `src/histora/agent.py`, `src/run_agent.py`.
2. **Mechanistic-modeling harness** — pure-python tools that *formulate and run* mechanistic models
   (ODEs, control theory, fluid transport), grounded in a **curated, cited model library**
   ([`docs/model-library.md`](docs/model-library.md)). The centerpiece chain is calibrated to a real
   interventional anchor and forks to the CV and neuro axes; every uncertain coupling is **flagged and
   swept as a range**. `src/histora/mech_*.py`.
3. **Empirical validation** — the **periodontitis ↔ cognition association** on real **NHANES 2011-2012**
   (n=919): **3 of 4 cognitive measures show a significant, confounder-adjusted negative association**
   with periodontal severity — the direction the mechanistic model predicts. `src/histora/perio_cognition.py`.
4. **The execution-gap capability** — the one robust way to improve the agent's inputs: **externalize a
   deterministic step the model *knows* but *drops* in situ** (missing-data flagging **0 → 1.0**). A
   pre-A/B predictor + a 3-arm A/B to scale it. `src/histora/exec_gap.py`.
5. **An honest apparatus** — scoring, counterfactual-sensitivity, and bootstrap confidence intervals
   (a claim never fires on a sub-noise delta). `src/histora/ab_eval.py`, `counterfactual.py`, `stats.py`.

Everything is a **validated capability, a validated association, or an explicitly-flagged-and-swept
hypothesis** — nothing that could not be verified or reproduced was kept.

## Run it

The mechanistic + validation code is **pure Python** (no GPU); the association runner needs
`pandas` + network for NHANES, and the Claude agent needs `anthropic` + `ANTHROPIC_API_KEY`.

```bash
python src/run_mechanistic.py       # periodontal source → IL-6/CRP → CV & neuro axes (offline)
python src/run_mech_neuro.py        # the neuro axis: neuroinflammation → tau spread (offline)
python src/run_perio_cognition.py   # the empirical validation on real NHANES 2011-2012 (needs network)
python src/run_agent.py             # the Claude-powered non-diagnostic relational agent (needs API key)
python -m pytest tests/ -q          # or run each tests/test_*.py — pure-python harness
```

## Layout

```
dental-analysis/
  src/histora/                # the package, aligned to the solution
    record_formats · bridge_concepts · relational_signals   # domain: records, mediators, signals
    agent                                                    # the Claude-powered relational analysis
    mech_ode · mech_models · mech_calibrate · mech_neuro     # the mechanistic harness
    ab_eval · counterfactual · stats                         # the honest apparatus
    perio_cognition · nhanes                                 # the empirical validation + data
    exec_gap                                                 # the execution-gap capability
  src/run_*.py                # entrypoints (mechanistic, neuro, perio-cognition, agent)
  schemas/                    # the non-diagnostic output contract
  agents/ skills/             # the Claude Code agent + skill catalog (see their README.md)
  docs/                       # PROBLEM, SOLUTION, model-library, DATASETS
  tests/                      # pure-python harness tests (no GPU)
```

## Data & guardrails

Grounded in **public, de-identified NHANES** (2009-2010 for the periodontal + cardiovascular +
inflammatory anchor; 2011-2012 for the periodontal + cognitive battery), plus a curated mechanistic
model library from the peer-reviewed literature. **Non-diagnostic throughout:** research hypotheses and
mechanistic models only; missing data is a collection flag, never an imputed value; every relational
axis cites the input fields it was derived from. Hypothesis-level couplings are flagged and reported as
ranges, and the one failed causal drug test of the periodontitis→Alzheimer hypothesis (atuzaginstat /
GAIN) is named as the standing caveat. See [`docs/DATASETS.md`](docs/DATASETS.md).
