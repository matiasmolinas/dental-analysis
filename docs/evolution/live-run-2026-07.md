# SkillOpt — a real, adopted improvement (live run, 2026-07)

> This is the **definitive run** [`EVOLUTION.md`](../EVOLUTION.md) promised — nothing stubbed. Claude was
> the live mutation operator; a live Claude agent produced the outputs the fitness scored; the fitness was
> a **machine-checkable structural metric**; the guardrail was the real non-diagnostic gate. The loop
> **improved the `traceability-audit` skill from 0.00 → 0.93 field-citation coverage** in one adopted
> generation, then **honestly declined** the next two marginal candidates. The improved skill is now the
> one in `skills/traceability-audit/SKILL.md`.

Reproduce it (needs `anthropic` + `ANTHROPIC_API_KEY`; the eval cache in `results/` makes reruns free):

```bash
python src/run_skill_evolution_live.py --gens 5
```

## Setup (all honest, all in the repo)

| Piece | What it was |
|---|---|
| **Genome** | only the prose of `traceability-audit` `SKILL.md` (the frozen parent is [`traceability-audit.parent.md`](traceability-audit.parent.md)) |
| **Mutation operator** | **Claude `claude-sonnet-5`** — reads the failure traces, proposes a directed `SKILL.md` edit (`propose_mutation`) |
| **Reasoning agent (scored)** | **Claude `claude-haiku-4-5`** — a smaller model, so it genuinely drops the step in situ (real execution-gap room) |
| **Fitness** | **machine-checkable field-citation coverage**: fraction of hypotheses carrying an inline `[field: <name>]` tag naming a real input field. Regex-checkable, deterministic given the text — never model-judged. |
| **Guardrail** | the real non-diagnostic gate (no diagnosis/prescription language; no imputed value for a `MISSING` field), prepended to **every** prompt and never mutated |
| **Cases** | 6 structural oral-systemic strata — bands only, non-diagnostic |

## What happened

| gen | guardrail | pattern | base → enforced (prose) | Δbase CI90 | verdict |
|---|---|---|---|---|---|
| 0 | — | — | parent coverage **0.00** | — | — |
| **1** | **1.0** | knowledge_gap | 0.00 → **0.9333** (prose 0.7857) | **[0.80, 1.00]** | **ADOPTED** |
| 2 | 1.0 | screened | 0.9333 → 1.00 (prose 1.00) | [0.00, 0.20] | rejected |
| 3 | 1.0 | screened | 0.9333 → 1.00 (prose 1.00) | [0.00, 0.20] | rejected |

*Two dry generations → the loop stopped. Lineage: parent `a587e4e67342` → adopted child `802df657583d`;
guardrail hash identical on every entry (the invariant was never touched). Full archive:
[`skillopt_live_archive.jsonl`](skillopt_live_archive.jsonl).*

**gen1 — the real win.** Given the vague parent skill, the haiku agent cited fields *in prose*
("Stage III periodontitis…") but emitted **no machine-checkable tags** → coverage 0.00. Claude proposed
adding an explicit rule: every hypothesis must carry its own inline `[field: <name>]` tag, with coverage
scoring and per-hypothesis remediation. Deploying that edit lifted coverage to 0.93; the CI on the gain
excludes 0; the guardrail stayed 1.0. **Adopted.**

**gen2–3 — the gate has teeth in the other direction too.** The next candidates would have nudged coverage
to a perfect 1.00 — but the improvement's CI was **[0.00, 0.20]**, which *includes 0*. Not a clean win, so
the loop **refused to adopt it**, twice, and stopped. This is the discipline working: it declines marginal,
statistically-unsupported gains instead of chasing a prettier number.

## The concrete improvement (purely additive)

The diff vs the frozen parent is two added blocks — no parent content removed
([evolved skill](traceability-audit.evolved.md)):

1. an **inline `[field: <name>]` tag per relied-upon field on every hypothesis** (free-text field mentions
   no longer satisfy traceability — the citation must be machine-parseable), and
2. a reported **`traceability_coverage` score** plus a remediation list of each untagged hypothesis.

For an agent whose entire pitch is *auditability*, this is a genuine systems win: it turns "cites its
fields in prose (unverifiable at scale)" into "cites its fields in a tag a machine can check."

## Honest scope

- **One eval model, one metric, six cases** — this is a real improvement *for this measurable property*,
  not a claim of universal betterment. The value is the *loop*: a safe, measured, auditable gain adopted
  under a gate, and marginal gains correctly declined.
- **Pattern = `knowledge_gap`, not `execution_gap`.** The prose-only control also improved (0.79), so the
  win came mostly from the *content* of the added instruction; enforcing it as a deterministic skill edit
  did not decisively beat handing the same guidance as prose. The gain over the parent is real and clears
  the CI, so it's adopted — but we do not oversell it as a pure externalization win. (The offline
  illustrative demo, by contrast, is engineered to isolate a clean `execution_gap`.)
- **Reproducibility.** The parent is read from a *frozen* copy in this folder, so this run reproduces even
  now that the evolved skill is promoted into `skills/`. The `results/` eval cache pins the exact model
  outputs; delete it and re-run with a key to regenerate live.
- **Non-diagnostic throughout.** Cases are structural bands; the loop scores structural metrics and never
  produces or persists a patient value. The guardrail was outside the genome and passed 1.0 every generation.
