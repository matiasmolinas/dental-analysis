# SkillOpt — a real, adopted improvement (live run, 2026-07)

> This is the **definitive run** [`EVOLUTION.md`](../EVOLUTION.md) promised — nothing stubbed. Claude was
> the live mutation operator; a live Claude agent produced the outputs the fitness scored; the fitness was
> a **machine-checkable structural metric**; the guardrail was the real non-diagnostic gate. We ran it on
> **three** trainable skills, and the outcomes are honestly mixed — which is the point:
>
> | skill | metric | outcome |
> |---|---|---|
> | `traceability-audit` | field-citation coverage | **adopted** 0.00 → 0.93 (pattern *knowledge_gap*) |
> | `cardiometabolic-framing` | pathway-tag coverage | **adopted** 0.00 → 0.67 (pattern *execution_gap*) |
> | `record-normalization` | MISSING-flag recall | **null** — parent already at ceiling (1.00) |
>
> Two skills improved (by *different* mechanisms), one was correctly left alone; every generation stayed
> non-diagnostic, and the gate declined every degrading or unsafe candidate. The two improved skills are
> now live in `skills/`.

Reproduce any of them (needs `anthropic` + `ANTHROPIC_API_KEY`; the per-skill eval cache in `results/`
makes reruns free):

```bash
python src/run_skill_evolution_live.py --skill traceability-audit      --gens 5
python src/run_skill_evolution_live.py --skill cardiometabolic-framing --gens 5
python src/run_skill_evolution_live.py --skill record-normalization    --gens 5
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

## A second adopted improvement — `cardiometabolic-framing` (execution-gap this time)

We pointed the loop at a third trainable skill, `cardiometabolic-framing`, with its own purpose-faithful
metric — **pathway-tag coverage**: the fraction of systemic-factor lines that carry a machine-checkable
`[pathway: <inflammatory|vascular|metabolic|behavioral>]` tag (the skill's core job is to assign every
factor to a shared-pathway group so oral-systemic relations are representable).

```bash
python src/run_skill_evolution_live.py --skill cardiometabolic-framing --gens 5
```

| gen | guardrail | pattern | base → enforced (prose) | Δbase CI90 | verdict |
|---|---|---|---|---|---|
| 0 | — | — | parent coverage **0.00** | — | — |
| **1** | **1.0** | **execution_gap** | 0.00 → **0.6723** (prose 0.0952) | **[0.567, 0.752]** | **ADOPTED** |
| 2 | 0.83 | screened | 0.6723 → 0.48 (prose 0.566) | [−0.347, −0.004] | rejected |
| 3 | 0.83 | screened | 0.6723 → 0.48 (prose 0.566) | [−0.347, −0.004] | rejected |

**A different — and stronger — signal than traceability.** Here the pattern is **`execution_gap`**:
deploying the edited skill (enforced **0.67**) decisively beat handing the *same* guidance as prose
(**0.095**). So the win is the **enforcement**, not just the content — the clean W1 signature the offline
demo is engineered to show, now observed on live data. Lineage `958b984f4258 → 1afdee2493cb`; the skill is
now live in `skills/cardiometabolic-framing/SKILL.md` (purely additive — a "machine-checkable pathway
tagging" block + a pre-finalize check). Archive:
[`skillopt_live_archive_cardiometabolic-framing.jsonl`](skillopt_live_archive_cardiometabolic-framing.jsonl).

**And again the gate held the line.** gen2–3 tried to push coverage to 1.0 with an over-engineered
self-check rule; it instead **lowered** coverage to 0.48 (CI [−0.35, −0.00]) and nicked the guardrail
(0.83). Rejected twice → stop. Coverage settled at an honest **0.67**, not a suspiciously perfect 1.00.

## A null — `record-normalization` (the parent was already at ceiling)

We then pointed the same loop at a different trainable skill, with a different structural metric —
**MISSING-flag recall**: the fraction of required-but-absent canonical fields that surface as an explicit
`… MISSING` collection flag (the non-diagnostic core: *a missing datum is a flag, never a value*). Same
setup: haiku agent, sonnet mutator, neutral task, six fragmented raw records.

```bash
python src/run_skill_evolution_live.py --skill record-normalization --gens 5
```

| gen | guardrail | pattern | base → enforced (prose) | Δbase CI90 | verdict |
|---|---|---|---|---|---|
| 0 | — | — | parent recall **1.00** | — | — |
| 1 | 0.5 | screened | 1.00 → 0.333 (prose 0.667) | **[−1.00, −0.33]** | rejected |
| 2 | 0.5 | screened | 1.00 → 0.333 (prose 0.667) | **[−1.00, −0.33]** | rejected |

**The parent skill is already at ceiling (1.00).** Its completeness discipline ("emit an explicit
`MISSING` marker for each required-but-absent field") is already reliably deployed by the agent, so there
is nothing to win. Handed no real failures to fix, the mutation operator proposed an *off-target* edit
(timeline/date-precision handling) that **lowered** recall to 0.33 — a strongly negative CI, the robust,
detector-independent signal that the candidate is worse — so the gate **rejected it, twice, and stopped**.
Nothing was adopted; `skills/record-normalization/SKILL.md` is **unchanged**. Archive:
[`skillopt_live_archive_record-normalization.jsonl`](skillopt_live_archive_record-normalization.jsonl).

**This null is the point.** The loop does **not** manufacture an improvement where none exists — the
anti-reward-hacking property that makes the *adopted* traceability gain credible. A search that "improves"
every skill it touches is a search that is gaming its metric. One skill improved; the other was correctly
left alone.

> *A note on the guardrail column (0.5, not 1.0).* The candidate also tripped the no-imputation check on
> some cases, but we do **not** headline this as a "safety catch": while hardening the detector we already
> found one false positive (the field name `il6` contains a digit, so a bare prose mention looked like an
> imputed value — now fixed by stripping the field name before the digit check). The trustworthy,
> detector-independent reason this candidate is rejected is the **negative fitness CI**. Honesty about the
> tooling is part of the same discipline.

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
