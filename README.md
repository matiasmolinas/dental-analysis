# dental-analysis — HISTORA Oral-Systemic Intelligence Agent

Interpretability-guided optimization of the input format, context, and knowledge
base for a **non-diagnostic** research agent that relates periodontal data
(probing, bleeding, bone loss, treatments, radiographs) to medical /
cardiovascular data (hypertension, diabetes, lipids, smoking, medications, CV
history) and surfaces oral-systemic risk profiles and research hypotheses.

## Idea

The periodontal <-> cardiovascular link is a chain of *hidden mediators*
(inflammation, C-reactive protein, atherosclerosis, endothelial dysfunction,
bacteremia). The Jacobian lens reads exactly those unspoken bridge concepts out
of a model's internal workspace. So we:

1. Instrument a small open-weights proxy (Qwen) with a pre-fitted J-lens.
2. Measure whether each candidate input format makes the mediator concepts
   representable in the workspace band (low vocabulary rank = represented).
3. Let a capable Claude read those readouts and edit the format, context, and KB
   (the **controller**), iterating until the mediators are reached.
4. Hand the converged format to the most capable Claude (the **evaluator**) for
   the final structured output, validated by task accuracy on Claude itself.

The proxy's ranks are directional, not absolute: they generate and prioritize
format hypotheses; Claude is the final judge.

**Living plan:** see [`docs/PLAN.md`](docs/PLAN.md) for the full workplan, status,
decisions, and progress log (updated as we learn).

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

## Run

Open `colab/histora_diagnostic.ipynb` in Colab (GPU runtime). It clones and
installs `jacobian-lens`, loads the model + pre-fitted lens, and scores the three
formats. No fitting required. The `src/` modules are imported by the notebook;
they compile and load without a GPU (except `harness.py`, which needs `jlens`).

## Guardrails

Non-diagnostic throughout. Missing mediating data becomes a **collection flag**,
never an imputed patient value. Every relational axis cites the input fields it
was derived from. Synthetic data only for methodology development.

## Note

`jacobian-lens/` (sibling folder) is the upstream reference and is left
unmodified; this project only imports from it.
