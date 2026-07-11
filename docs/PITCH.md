# HISTORA — hackathon pitch

*Built with Claude: Life Sciences · co-organized with Gladstone Institutes.*

## The objective we demonstrate to win

> **The first *safe, transparent, mechanistic* scientific research agent for oral–systemic disease.**
> Claude orchestrates a calibrated mechanistic engine to turn fragmented patient data into
> **falsifiable, uncertainty-quantified hypotheses** — validated on public data *and* genetics, provably
> more coherent, calibrated, and honest than either applying single-disease models separately or using
> Claude without a harness — with a **hard non-diagnostic guardrail**. Shown end-to-end in ~3 minutes.

It is a **research agent, not a disease predictor.** The win is not accuracy; it is *mechanism +
honesty*: uncertainty and falsifiability as product features, every number traceable, nothing diagnosed.

*The stage runbook (timed lines, clicks, fallbacks, Q&A) is [`DEMO-SCRIPT.md`](DEMO-SCRIPT.md).*

## The one memorable demo — "the inflammatory-proxy walk"

`python demo/run_demo.py` (offline, no API key) runs a fixed case through five stages:

1. **Input** — a structural case (bands only); a missing hs-CRP appears as a **collection flag**, never imputed.
2. **Claude reasons** — non-diagnostic oral↔CV↔metabolic↔neuro hypotheses, each citing its input fields.
3. **The engine computes** — one **shared inflammatory proxy** (excess IL-6) forks to three axes; CRP /
   HbA1c / tau-α come out as **90% ranges** with the therapy counterfactual and the dominant uncertainty.
4. **Validation** — the three NHANES association signs + a genetic **Mendelian-randomization** probe, in a
   panel labeled **"validation ≠ calibration."**
5. **A falsifiable brief** — ranked hypotheses, each with the observation that would refute it, plus an
   **agentic-metric card** (citation accuracy, hallucination rate, uncertainty coverage, guardrail).

**The punchline:** three axes are not three models — they are *one lever, three diseases, one engine*.
The "broad scope" becomes the argument, not a weakness.

## Why we win — the honest differentiators

| Claim | Evidence (all reproducible) |
|---|---|
| **Mechanism, not correlation** | one calibrated parameter (ε) drives all three axes; every output a range with its uncertainty named |
| **Validated on public data** | NHANES: perio→CRP, →HbA1c, →cognition — confounder-adjusted, and **survives survey-weighted + FDR** stats |
| **Genetic causal probe** | Mendelian randomization: IL-6R→coronary disease **causal**, CRP→Alzheimer's **null** — supports our own tiering |
| **Beats the alternatives** | pre-registered benchmark: vs separate models and bare Claude — 1 vs 3 params, calibration error 0.00, ranges + falsifiability 1.00 |
| **Safe agent, measured** | agentic card: citation accuracy 1.0, hallucination 0.0, coverage 1.0, non-diagnostic guardrail enforced by construction |
| **Gladstone-aligned** | touches 4 of 5 institutes; a **novel upstream perturbation** (periodontal inflammation → tau-α) for the neuro labs |

## How we deliver it (the integration decision)

**Two surfaces, one engine — a dual delivery.**

- **Now — a Claude Code plugin** (`plugin/histora-oral-systemic`): the **portable demo surface**. It runs
  anywhere, needs no special account, and drives the `/evaluate-case` flow and `demo/run_demo.py`. This is
  what a judge runs on stage.
- **Final home — Claude Science.** Claude Science
  ([workbench announcement](https://www.anthropic.com/news/claude-science-ai-workbench) ·
  [product](https://claude.com/product/claude-science)) is the lab-grade surface. **It does not use
  "plugins"** — its native extension model is **skills** (reusable pipelines) and **connectors** (to
  tools, databases, ELNs, HPC, and models), plus user-created **specialist agents** and a **reviewer
  agent**. HISTORA maps onto it directly:

  | HISTORA component | Claude Science home |
  |---|---|
  | `skills/` (staging, guardrail, oral-systemic KB) | **skills** |
  | the `histora` Python harness | a **reusable pipeline saved as a skill** |
  | `agents/` (orchestrator, analysts, guardrail-verifier) | **specialist agents** |
  | data access (UniProt/PDB, GWAS for MR, NHANES) | **connectors** |
  | our citation-accuracy + guardrail metrics | the platform's **reviewer agent** (native) |

  **Can HISTORA be "a plugin to Claude Science"?** Not by that name — Claude Science has no plugin slot.
  But **yes, it integrates cleanly** via skills + connectors + specialist agents, because Claude Code and
  Claude Science share the same primitives. The same components we ship as a Claude Code plugin *are* the
  Claude Science integration. (A grant application to bring it there is drafted in
  [`grant/`](grant/AI-for-Science-application.md).)

## The 60-second script

> *"Gum disease, heart disease, diabetes, and Alzheimer's are studied separately — but they may share one
> upstream driver: inflammation. HISTORA is a research agent that makes that idea testable. Watch: a case
> goes in as structural bands — the missing lab is flagged, never guessed. Claude proposes the oral–systemic
> hypotheses and hands them to a mechanistic engine calibrated to real treatment data. Out comes not a
> number but a range, with the therapy's predicted effect and the shakiest assumption named. We check the
> directions in public NHANES and probe causality with genetics — which supports the heart link and, honestly,
> not the Alzheimer's one, so we flag that axis as exploratory. Every number is traceable; nothing is a
> diagnosis. On a pre-registered benchmark it beats both separate models and Claude-without-a-harness on
> coherence, calibration, and honesty. It's a Claude Code plugin today, and it drops into Claude Science as
> skills and connectors tomorrow."*

---

*Evidence: [`PAPER.md`](PAPER.md) · [`BENCHMARK.md`](BENCHMARK.md). Delivery: [`DATA-AND-DELIVERY.md`](DATA-AND-DELIVERY.md).
Non-diagnostic throughout; population/parameter-level only.*
