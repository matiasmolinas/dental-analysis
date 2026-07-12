# SkillOpt — Claude improving Claude's tooling, under an invariant it cannot evolve

> The one Claude role HISTORA hadn't shown until now: **self-improvement.** Claude proposes an edit to one
> of its own reasoning skills; the edit is kept **only if** it measurably improves a structural metric AND
> leaves the non-diagnostic guardrail untouched — a safety invariant that is **structurally impossible to
> evolve.** The differentiator for a *builder* track isn't "safe agent" (everyone says that); it's
> *"self-improvement where breaking the rules scores zero, and here is the archive that proves it."*

## The loop (`histora.skill_evolution`, `run_skill_evolution.py`)

One gated generation:

1. **Mutate** — Claude reads the *failure traces* of an A/B on a `SkillOpt-trainable` `SKILL.md` and
   proposes a directed edit (the mutation operator; `propose_mutation`). Directed, not blind — the
   Darwin Gödel Machine lesson (Sakana, arXiv:2505.22954).
2. **Gate (hard, first)** — the candidate must pass the **non-diagnostic guardrail on every held-out
   case**. A binary gate: any failure ⇒ disqualified, *no matter how much fitness it gained*. (Correctness
   before performance — the AI CUDA Engineer lesson, arXiv:2509.14279.)
3. **A/B (3 arms)** — parent vs candidate vs a **prose-only control** of the same change, scored by a
   **structural** fitness metric with a bootstrap CI (reuses `histora.exec_gap.run_directive_ab`). Adopt
   iff the candidate beats the parent (CI excludes 0). The prose arm classifies *why*: **execution_gap**
   (deploying the edit is the win — the W1 signature) vs knowledge_gap (content helped, deployment didn't).
4. **Archive** — every generation, adopted **and rejected**, is appended to an auditable JSONL with
   lineage (parent→child hashes), the fitness Δ + CI, the verdict, and the **guardrail hash**.

## Why the safety invariant is *structural*, not goodwill

Four layers, all in the repo — this is the moat:

1. **The genome is only the prose of the `SkillOpt-trainable` skills.** The guardrail skill is tagged
   `PROTECTED — do not evolve` and is **not in the allowlist**; `histora.citations` and the mechanistic
   engine are outside the genome entirely. Evolution literally cannot reach them.
2. **The guardrail is a binary gate, not a fitness term.** `fitness = disqualified` if any case fails —
   safety is never traded for accuracy.
3. **Fitness is external/structural, never model-judged** (scored against the immutable `citations.py`),
   so the search can't reward-hack a subjective judge.
4. **The archive carries the guardrail hash, identical in parent and child** — machine-checkable proof
   that no accepted (or rejected) mutation ever touched the invariant.

## What the demo shows (one screen)

`python src/run_skill_evolution.py --fresh` produces an archive with two siblings:

| | parent→child | guardrail | pattern | fitness (base→enforced, prose) | Δ CI90 | verdict |
|---|---|---|---|---|---|---|
| **ADOPTED** | 1cc42d8d → 6cd56d03 | **1.0** | execution_gap | 0.5 → **1.0**, prose 0.5 | [0.5, 0.5] | **adopted** |
| **REJECTED** | 1cc42d8d → 90172486 | **0.0** | execution_gap | 0.5 → 1.0, prose 0.5 | [0.5, 0.5] | **rejected: guardrail<1.0** |

The rejected sibling **improves the metric exactly as much** as the adopted one — and is thrown out anyway,
because it broke the guardrail. Same `guardrail_hash` on both. That single screen *is* the thesis: maximal
(Claude self-improving), unique (the meta-role nobody else shows), and safe *by construction*.

## Honest scope

- The shipped demo uses an **illustrative structural metric** (field-citation coverage) run **offline and
  reproducible** — the *mechanism*, not a claimed live result (same discipline as the illustrative MR
  panels). A definitive run wires Claude as the mutation operator and `histora.agent_metrics` over the
  benchmark panel — exactly as the MR/cis-MR went from illustrative to **live in Claude Science**.
- **One generation, offline.** We deliberately do **not** run a multi-generation population search
  (DGM-lite): more generations = more surface for reward hacking and non-reproducibility, for marginal
  narrative gain. The line is one measured, gated, honest generation.
- Reuses the already-tested apparatus (`exec_gap`, `ab_eval`, `agent_metrics`, `citations`); adds only the
  glue (`skill_evolution`, 7 tests). Non-diagnostic throughout — the loop never produces or persists a
  patient value.

*Sakana lineage:* directed mutation from failure + auditable archive (Darwin Gödel Machine); correctness
before performance (AI CUDA Engineer); evolve the recipe not the components, and measure novelty on
behavior not text (Evolutionary Model Merge; ASAL). See [`PITCH.md`](PITCH.md) and, for the full risk
analysis, [`internal/ROADMAP-STAGE2.md`](internal/ROADMAP-STAGE2.md) §11.
