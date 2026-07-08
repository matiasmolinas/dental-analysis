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

## How it works (the working hypothesis)

We read the model's "workspace" with **two complementary instruments** (see
[`docs/DUAL_LENS.md`](docs/DUAL_LENS.md)): a fast **self-report probe on Claude
itself** (`claude-workspace-probe`, runs on the real target model, no GPU) and the
**measured Jacobian lens on the Qwen proxy** (`jlens-diagnostic`, quantitative and
causal ground truth). The self-report drives the fast inner loop; the measured lens
validates it; their **correlation is a reproducible finding**. Our hypothesis is
that **Claude, by inspecting this workspace, can decide what to fix at the input** —
and that the learning drives autonomous skill evolution:

1. **Instrument** the Qwen proxy with a pre-fitted J-lens.
2. **Present a candidate** made of three things the hypothesis targets: the input
   **data structure**, the **problem formulation**, and the **chain of thought**
   (read the workspace over the generated reasoning, not only the static prompt),
   plus KB context.
3. **Claude inspects Qwen's workspace readout** to decide which **values to
   complete** (as collection flags, never imputed), which **formats to adjust**,
   and which **additional knowledge to inject or modify** at the input.
4. **Iterate** the edits until the mediating concepts are represented (low
   workspace-band rank).
5. **Evaluate on Claude** — feed the converged, complete input to the most capable
   Claude for the final structured output. This is the authoritative gate.
6. **Evolve autonomously** — use that learning as the fitness signal to evolve the
   subagents and skills (SkillOpt-style loop), gated by Claude accuracy + the
   protected non-diagnostic guardrail, with human-in-the-loop promotion.

**Load-bearing assumption:** the proxy's workspace predicts Claude's relational
reasoning. Proxy ranks are directional, not absolute — they generate and prioritize
hypotheses; Claude is the final judge (transfer validity is verified in Phase 3).

**Docs:** [`docs/PLAN.md`](docs/PLAN.md) (living workplan, status, decisions),
[`docs/DUAL_LENS.md`](docs/DUAL_LENS.md) (two-instrument methodology + correlation
experiment), [`docs/HACKATHON_STRATEGY.md`](docs/HACKATHON_STRATEGY.md) (Built with
Claude: Life Sciences — tracks, named user, one-week plan, demo, judging),
[`docs/DATASETS.md`](docs/DATASETS.md) (NHANES 2009–2010 real anchor + Synthea
longitudinal; schema mapping and access).

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
