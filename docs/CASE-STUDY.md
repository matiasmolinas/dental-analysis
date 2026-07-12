# Flagship case study — a research session, end to end

> The winning artifact isn't another feature — it's **one coherent session a scientist could have lived**,
> with the honesty visible at every step. This is HISTORA's whole machine assembled into a single
> **falsifiable research line**, run from Claude Science. *Scripted like a demo, real like an experiment:*
> the path is real (skills auto-load, the pinned engine runs, the UniProt/PDB connector renders real 3-D
> structures, the MR is live over OpenGWAS), the case is chosen, and the science is **hypothesis-generation
> — never a diagnosis, never a treatment claim.**

Run the brief offline (every number from the pinned engine, nothing model-regenerated):

```bash
python demo/run_case_study.py        # → the falsifiable research line + case_study.json
```

## The case

A structural stratum, bands only: **Stage III periodontitis · high BOP · type-2 diabetes · hs-CRP MISSING**.
The missing lab is a **collection flag, never imputed** — the guardrail, in the math.

## The spine (each step executes for real)

| # | Step | What actually runs |
|---|---|---|
| ① | **Case in** | structural bands; hs-CRP MISSING → collection flag |
| ② | **Claude reasons** | non-diagnostic oral↔systemic hypotheses, each citing its input fields |
| ③ | **Engine** | one shared IL-6 proxy → CV / metabolic / neuro as **90% ranges** + the therapy counterfactual |
| ④ | **Genetics + proteins** | live cis-MR (IL-6R→CAD causal, CRP→CAD null); the UniProt/PDB connector renders the **real IL-6 / IL-6Rα / gp130 / CRP** structures in the Mol\* viewer |
| ⑤ | **The research line** | a single falsifiable intervention hypothesis, with its refutation and shakiest assumption named |
| ⑥ | **Coda** | the reviewer agent's real run + the SkillOpt archive — *Claude built, self-optimized, operates, and reviewed all of this* |

## The research line — the honest anchor

**Lever = periodontal therapy** (scaling & root planing) — **non-pharmacological**, and the exact edge the
engine is *calibrated* on (ΔhsCRP after therapy), so its predicted effect is anchored, not asserted.

**Causal node = IL-6R.** Two-sample **cis-MR** supports **IL-6R → coronary disease as causal** (LD-aware
correlated-IVW β≈+0.553, SE 0.109) while **circulating CRP → CAD is null** — the marker isn't causal, the *node* is. **Tocilizumab**
(an IL-6Rα-blocking antibody) is cited **only** as pharmacological proof that the node is druggable and
causal — **never as a proposed treatment.**

**The hypothesis HISTORA generates:** *if the IL-6R node mediates the systemic effect, then lowering the
periodontal IL-6 source (the non-pharmacological lever) should move the predicted markers in the same
direction the genetics implies* — a testable research line a lab could design a study around, not a therapy.

**It ships its own refutation:** if therapy doesn't lower hs-CRP within the predicted range, the calibration
is wrong; if an IL-6R-instrumented analysis shows no coronary effect, the node premise fails; if the marker
moves opposite to the genetic direction, the mediation hypothesis is refuted. **Shakiest assumption:** that
the population-level IL-6R causal direction transfers to the periodontal-source lever in a given stratum —
untested, and exactly the question the tool exists to *pose*.

## Honesty red-lines (structural, not bolted on)

1. **Hypothesis-generation, never efficacy.** No claim that periodontal therapy or any drug treats/prevents anything.
2. **Non-diagnostic, population/parameter-level.** Ranges out; no patient value; no individual recommendation.
3. **A named drug is a mechanistic/causal-node anchor only** — never a prescribing suggestion.
4. **MR ≠ RCT; calibration ≠ validation.** MR supports a causal *direction* of a node, not that any intervention works in patients.
5. **Effect sizes modest, stated with CI.** Periodontitis is one contributor among many — said first.
6. **The nulls stay loud:** circulating-CRP-null vs IL-6R-node-causal, and the **Alzheimer's axis stays EXPLORATORY** (the GAIN-trial failure is the standing caveat). No intervention story upgrades it.

*(The P. gingivalis / gingipain → tau microbiome line is at most a one-line secondary mention — it drags in
new science and lives on the exploratory neuro axis; it never leads.)*

## Running it live in Claude Science (the "it lives in a real lab" moment)

Proven end-to-end (see [`CLAUDE-SCIENCE.md`](CLAUDE-SCIENCE.md)). In a fresh Claude Science session:

1. **Import** `matiasmolinas/dental-analysis` → the HISTORA skill **and** the non-diagnostic guardrail load together.
2. **Run** the engine at the pinned `main`; `run_case_study.py` prints the falsifiable brief.
3. **Proteins → 3-D:** the **UniProt connector** resolves the six accessions (IL-6 `P05231`, IL-6Rα
   `P08887`, gp130 `P40189`, CRP `P02741`, TNF-α `P01375`, IL-10 `P22301`); the **PDB connector** returns and
   the **Mol\* viewer renders the real structures** for IL-6 (`1ALU`), CRP (`1GNH`), TNF-α (`1TNF`).
4. **Genetics live:** the LD-aware IL-6R cis-MR over OpenGWAS (IL-6R→CAD causal; CRP→CAD null).
5. **Reviewer agent** audits the outputs against the citation registry — and reports honestly (in our run:
   3 checks, 1 minor finding — the skill-update was handled by disclosure, since the imported skill already
   pins the latest `main`).

*Stage discipline: run the path live only if everything is green in rehearsal; otherwise the recorded
capture + this one-pager tell the same true story. Never fake an output — every step executes, or it's cut.*

## Coda — Claude at every layer (the builder-track meta-role)

The build itself is an artifact. A bioengineer + AI engineer **directs**; an autonomous agent (Claude Code)
**proposes, rewrites its own skills, investigates, self-corrects, and consults**; it then **deploys and
operates** the project through the Claude-for-Chrome plugin driving **Claude Science**; and Claude, inside
Claude Science, acts as a **qualified scientist-user** that evaluates the work, finds flaws, and proposes
features. Every claim here is evidence-linked, not narrated:

- **Builder + self-optimizer:** the SkillOpt archive — Claude improved 2 of its own skills (by different
  mechanisms) and correctly left a 3rd alone; the guardrail hash is identical parent↔child, machine-checkable
  proof the invariant never moved ([`EVOLUTION.md`](EVOLUTION.md), [`evolution/live-run-2026-07.md`](evolution/live-run-2026-07.md)).
- **Operator:** a fresh Claude Science session imported the skill, reinstalled the engine, rendered the
  figures, and drove the UniProt/PDB connectors to real 3-D structures ([`CLAUDE-SCIENCE.md`](CLAUDE-SCIENCE.md)).
- **Scientist-user:** the reviewer agent's real audit, with its one honest, minor finding — *shown, not dramatized.*

Science leads; this coda reframes the whole thing as **"and Claude built and operates all of this, too."**

*Companion: [`PITCH.md`](PITCH.md) (the thesis) · [`DEMO-SCRIPT.md`](DEMO-SCRIPT.md) (the stage runbook).
Non-diagnostic throughout; population/parameter/instrument level only.*
