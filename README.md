# dental-analysis — HISTORA Oral-Systemic Intelligence Agent

Interpretability-guided optimization of the input format, context, and knowledge
base for a **non-diagnostic** research agent that relates periodontal data
(probing, bleeding, bone loss, treatments, radiographs) to medical /
cardiovascular data (hypertension, diabetes, lipids, smoking, medications, CV
history) and surfaces oral-systemic risk profiles and research hypotheses.

## The problem we solve

Medical and dental records live in separate silos, and the periodontal <->
cardiovascular link runs through *hidden mediators* (inflammation, C-reactive
protein, atherosclerosis, endothelial dysfunction, bacteremia) that no single
record makes explicit. HISTORA supplies the missing data layer that integrates
oral and systemic records. The open question this project answers is:

> Given integrated oral + systemic data, **we do not know a priori the best way to
> present, formulate, and contextualize it** so that a model actually represents
> the true oral-systemic relationships — which values to complete, which input
> format to use, and which knowledge to inject.

We answer it with interpretability instead of guesswork, and turn the answer into
a self-improving, **non-diagnostic** research agent.

## How it works (the loop)

Full method in [`docs/APPROACH.md`](docs/APPROACH.md). A **second model instance — the
Lens Observer** (`agents/lens-observer.md`, Opus) reads the **inferred Jacobian lens**
of the primary model — the workspace self-report the primary emits while it processes
a prompt (`claude-workspace-probe` → `schemas/lens_readout_schema.json`) — and drives
the loop:

1. **Run** the task on the Executor with the inferred-lens readout active; emit the
   output **plus** the readout.
2. **Diagnose** — the Observer compares the readout to the spec (required mediators,
   variables, procedure steps) and returns a typed deficiency map
   (`schemas/deficiency_map_schema.json`): missing/incorrect variables, uncovered
   chain-of-thought steps, unrepresented mediators, under-specified framing.
3. **Evolve** — route each deficiency to the cheapest of five surfaces (work prompt,
   skill, KB context, sub-agent def + injected variables, **harness code**) as a
   bounded, readout-grounded edit. Values to complete become **collection flags, never
   imputed**.
4. **Consolidate + inject** — update the cumulative **Session Working-Consciousness**
   ledger and, from it, inject/modify the next prompt. Lessons compound across turns.
5. **Gate** — T0 edits are ephemeral (in-session); durable T1 edits are gated by
   Claude held-out accuracy + the protected non-diagnostic guardrail + tests + human
   approval. The final authority is task accuracy + guardrail, never the readout score.

**The measured Jacobian lens on the Qwen proxy** (`jlens-diagnostic`, quantitative and
causal) is **not** wired into the live loop: it is the reproducible *validation* path,
and the correlation between the inferred and measured signals is a research finding.
See "Inferred vs. measured Jacobian lens (and the unlock)" below.

**Epistemic status:** the inferred lens is self-report exercised as a readout channel —
directional, never a measurement and never clinical evidence; task accuracy on Claude
plus the protected guardrail are the authorities.

**Docs:** [`docs/APPROACH.md`](docs/APPROACH.md) (**the canonical, domain-general
description of the method** — inferred-lens Observer + Session Working-Consciousness),
[`docs/IMPACT.md`](docs/IMPACT.md) (where/when the approach generates large impact a
priori — predictors, archetypes, and a scoring rubric),
[`docs/REFORMULATION.md`](docs/REFORMULATION.md) (the delta from the earlier baseline +
the R0–R6 workplan), [`docs/PLAN.md`](docs/PLAN.md) (living workplan, status,
decisions), [`docs/DUAL_LENS.md`](docs/DUAL_LENS.md) (two-instrument methodology +
correlation experiment), [`docs/HACKATHON_STRATEGY.md`](docs/HACKATHON_STRATEGY.md)
(Built with Claude: Life Sciences — tracks, named user, one-week plan, demo, judging),
[`docs/DATASETS.md`](docs/DATASETS.md) (NHANES 2009–2010 real anchor + Synthea
longitudinal; schema mapping and access).

## Inferred vs. measured Jacobian lens (and the unlock)

The live loop uses the **inferred** Jacobian lens: the workspace self-report the
primary model emits while it processes a prompt (`claude-workspace-probe` →
`schemas/lens_readout_schema.json`). A **second model instance — the Lens Observer**
(`agents/lens-observer.md`, on Opus) analyzes that readout of the *primary* model,
diagnoses deficiencies (missing/incorrect input variables, uncovered chain-of-thought
steps, unrepresented mediators), and drives bounded, gated evolution of five surfaces —
work prompts, skills, KB context, sub-agent definitions + injected variables, and
**harness code**. It curates a cumulative **Session Working-Consciousness** ledger (the
closed in-session evolutionary loop) and injects/modifies prompts from it.

We deliberately do **not** wire the real Colab/Qwen Jacobian lens into the runtime; it
stays the documented, reproducible *validation* path (`agents/jlens-diagnostic.md`,
`colab/`, and the `docs/DUAL_LENS.md` correlation experiment). This is an honest limit:
the inferred lens is **self-report exercised as a readout channel — never a measurement
and never clinical evidence.**

> **The unlock.** If the frontier model's *real* Jacobian lens were exposed (e.g. via
> API), this exact architecture would swap the inferred signal for a **measured** one —
> turning directional hypotheses into causal ground truth, enabling representation
> swaps, and letting the Observer optimize against the model's true internal workspace.
> The whole loop is built to that interface; only the signal source would change. That
> is where this reaches its real power.

## Layout

```
dental-analysis/
  colab/
    histora_diagnostic.ipynb   # main GPU harness (run in Colab)
    walkthrough.ipynb          # copy of the jacobian-lens reference notebook
  src/
    bridge_concepts.py         # target mediator + shared concepts
    record_formats.py          # one synthetic record, three candidate formats
    harness.py                 # J-lens metrics: concept_ranks, capacity, sweep_layers
  schemas/
    output_schema.json         # non-diagnostic structured output contract
  prompts/
    controller.md              # Claude input-optimizer prompt
    evaluator.md               # Claude final-analysis prompt
  agents/                      # runtime subagents (orchestrator + specialists) + offline agents
  skills/                      # reusable capability docs (SkillOpt-trainable; guardrail protected)
```

See [`agents/README.md`](agents/README.md) and [`skills/README.md`](skills/README.md)
for the full subagent + skill catalog and the skill↔subagent map.

## Reference repos (siblings, not part of this repo)

- `../jacobian-lens/` — Anthropic's Jacobian-lens reference (imported by the notebook).
- `../SkillOpt/` — Microsoft Research SkillOpt: skills as trainable parameters,
  the reference for the skill-evolution loop.
- `Doriandarko/skirano-skills` (GitHub, not cloned) — Pietro Schirano's `j-space-lens`
  self-report skill that inspired `skills/claude-workspace-probe.md`. Referenced with
  attribution, **not vendored** (its repo has no license); install its plugin
  separately if you want the original.

## Run

Open `colab/histora_diagnostic.ipynb` in Colab (GPU runtime). It clones and
installs `jacobian-lens`, loads the model + pre-fitted lens, and scores the five
candidate input formats (A–E, see `src/record_formats.py`). No fitting required.
The `src/` modules are imported by the notebook; they compile and load without a
GPU (except `harness.py`, which needs `jlens`).

## Data

Cases are grounded in **NHANES 2009–2010** (public, de-identified — the cycle that
pairs the full-mouth periodontal exam with CRP), plus the **NHANES Oral Microbiome
2009–2012** mediator layer (SEQN-linked) and **Synthea** for longitudinal
progression and shareable demo records. Mapping in [`src/nhanes_mapping.py`](src/nhanes_mapping.py),
loader in [`src/nhanes_loader.py`](src/nhanes_loader.py), full detail in
[`docs/DATASETS.md`](docs/DATASETS.md).

## Guardrails

Non-diagnostic throughout. Missing mediating data becomes a **collection flag**,
never an imputed patient value. Every relational axis cites the input fields it
was derived from. NHANES-grounded / synthetic data only for methodology development.

## Note

`jacobian-lens/` (sibling folder) is the upstream reference and is left
unmodified; this project only imports from it.
