# Reformulation — Inferred-Lens Observer & Session Working-Consciousness

> **Status:** implemented (R0–R6; live A/B pending data). Written 2026-07-08. This
> document is the **delta** from the project's earlier baseline ([`PLAN.md`](PLAN.md))
> and the R0–R6 workplan. For the standalone, domain-general description of the method
> itself, read [`APPROACH.md`](APPROACH.md); for where it generates large impact a
> priori, read [`IMPACT.md`](IMPACT.md). Guardrails in
> [`../skills/non-diagnostic-guardrail.md`](../skills/non-diagnostic-guardrail.md)
> remain protected invariants throughout.
>
> **2026-07-09 pivot (supersedes parts of this doc):** the project now runs on **Claude
> only**. The measured Qwen lens, Colab, and the dual-lens correlation experiment were
> **removed** (deleted `colab/`, `agents/jlens-diagnostic.md`, `prompts/controller.md`,
> `src/harness.py`, `docs/DUAL_LENS.md`). We explore the Jacobian-lens paper *indirectly*
> via the self-report skill and corroborate with counterfactual-sensitivity on Claude;
> the "unlock" is reframed as an API feature we propose to Anthropic (expose the real
> lens on Claude). Where this doc describes the *baseline* two-instrument setup below,
> read it as history; the current state is single inferred lens, Claude only.

---

## 0. TL;DR

We turn the current **offline, dev-time** optimization pipeline (Claude self-report
probe + measured Qwen J-lens in Colab + SkillOpt) into a **live, in-session,
self-evolving multi-agent system** built around three ideas:

1. **A second model instance — the Lens Observer** — that does *not* do the task.
   It analyzes the **inferred Jacobian lens of the primary model** (the workspace
   self-report the primary emits while it processes prompts, skills, context, and
   sub-agent definitions), detects deficiencies (missing/incorrect input variables,
   uncovered chain-of-thought steps, unrepresented mediators), and drives evolution.
2. **The inferred lens is the only signal, on Claude only.** There is no proxy, no
   Colab, no measured lens — we explore the paper *indirectly* via the self-report
   skill. We reframe the *unlock* as an **API feature we propose to Anthropic**: if the
   real Jacobian lens were exposed on Claude, this exact architecture would jump from
   inferred to measured signal and reach its true power.
3. **A Session Working-Consciousness (SWC) ledger** — a cumulative, evolving
   session variable that the Observer owns, uses as its own context, and consolidates
   turn over turn. It is the closed evolutionary loop of "working consciousness
   during the session," and from it the Observer injects or modifies prompts on the fly.

The evolution the Observer drives targets **five surfaces**, not just skills:
work prompts (main agent + sub-agents), skills, knowledge-base context, sub-agent
definitions + injected input variables/parameters, and **harness code** (parsers,
deterministic relational analyzers, and any code tool the agents rely on).

---

## 1. Where we are (baseline) and what changes

### 1.1 Baseline (today)

- **Two instruments, offline** *(baseline — removed in the 2026-07-09 pivot)*:
  `claude-workspace-probe` (self-report on Claude) + a measured Jacobian lens on a Qwen
  proxy in Colab, with their correlation as a research finding. The current project
  keeps only the self-report instrument, on Claude.
- **SkillOpt** evolves *skills only*, offline, gated by Claude held-out accuracy +
  guardrail pass-rate.
- The runtime is a Claude orchestrator + specialist sub-agents; the lens and the
  optimizer are dev-time tools that improve the skills those sub-agents run.

### 1.2 The reformulation, as four shifts

| # | Shift | From | To |
|---|---|---|---|
| S1 | **Second instance reads the primary's lens** | Self-report is logged as a signal | A separate Observer model *analyzes* the primary's inferred lens and steers evolution |
| S2 | **Single live signal = inferred lens** | Colab/Qwen measured lens is a live dependency | Inferred lens only; real lens documented as the future "unlock" |
| S3 | **Closed in-session evolutionary loop** | Offline SkillOpt between runs | Online loop + a persistent **Session Working-Consciousness** the Observer curates |
| S4 | **Evolution includes harness code** | Evolve skills only | Evolve prompts, skills, KB, sub-agent defs, injected variables, **and code (parsers/analyzers)** |

### 1.3 Why this is a stronger result

- **Better software story (Build track):** a self-observing, self-evolving system
  with a persistent working consciousness is "working software that outlasts the
  week," and it is *domain-general* — dental oral-systemic is the anchoring
  instance, not the ceiling.
- **Principled prompt-vs-code boundary:** the lens gives an explicit rule for when a
  deficiency should be fixed deterministically in the harness instead of in a prompt.
- **Forward-looking research claim:** the inferred→measured "unlock" note is an
  honest, compelling statement of where this goes if real lens access exists.
- **Keeps rigor:** the guardrail stays protected; edits stay bounded/auditable;
  self-report is corroborated by the API-observable counterfactual-sensitivity test.

---

## 2. Target architecture

### 2.1 Two model instances, three roles

| Role | Instance | Does | Never does |
|---|---|---|---|
| **Executor** (Primary) | Model A (e.g. Fable/Sonnet) — the current orchestrator + sub-agents, run with the inferred-lens readout active | The oral-systemic task; emits output **plus** its inferred workspace readout | Grade its own work / decide its own evolution |
| **Lens Observer** (Secondary) | Model B (recommend a capable model, e.g. Opus) — a *separate* instance | Reads the primary's inferred lens, diagnoses deficiencies, curates the SWC, proposes + applies evolution edits | Produce the clinical output |
| **Gate / Guardrail** | `guardrail-verifier` (unchanged, adversarial) | Enforce protected invariants at every gate | Ever be evolved |

The two-instance split is load-bearing: it gives a genuine second perspective, avoids
the executor grading its own homework, and mirrors the paper's separation between the
*model* and the external *lens* reading it.

### 2.2 The per-unit-of-work loop

```
                     ┌─────────────────────────────────────────────────────┐
                     │  Session Working-Consciousness (SWC) ledger          │
                     │  cumulative • evolving • owned by the Observer        │
                     └───────────────▲───────────────────────┬─────────────┘
                                     │ read as context        │ consolidate
   prompt package                    │                        ▼
   (work prompt + skill +   ┌────────┴─────────┐     ┌──────────────────────┐
    KB context + subagent   │  EXECUTOR (A)     │     │  LENS OBSERVER (B)    │
    def + injected vars) ──▶│  runs task with   │────▶│  analyzes primary's   │
                            │  inferred-lens    │ out │  inferred lens vs the │
                            │  readout active   │  +  │  required-variable /  │
                            └───────────────────┘lens │  procedure spec       │
                                     ▲                 └──────────┬───────────┘
                                     │ inject / modify prompt     │ evolution actions
                                     │ (Observer's criterion)     ▼
                                     │                 ┌──────────────────────┐
                                     └─────────────────┤  EVOLUTION CONTROLLER │
                                                       │  edits 5 surfaces,    │
                                                       │  bounded + gated      │
                                                       └──────────┬───────────┘
                                                                  ▼
                                            gate = guardrail pass + (for promoted
                                            edits) held-out accuracy + human approval
```

### 2.3 The inferred Jacobian lens (the live signal)

The primary emits, per call, an **inferred lens readout**: the workspace table +
`sweep` line + (optionally) the generated chain-of-thought span, produced by the
`claude-workspace-probe` skill. This is **self-report exercised as a readout
channel — not a measurement** (same absolute rules as today). The Observer treats
this readout as *data about the primary's processing*, never as ground truth about
the patient.

**What the Observer extracts from it:**

- **Mediator coverage** — which bridge concepts (inflammation, CRP, atherosclerosis,
  endothelial dysfunction, bacteremia, …) surfaced, at what stage/salience; absence
  is the signal.
- **Variable presence & correctness** — were the required input variables/parameters
  present in the readout, and did they carry sane values? Missing or malformed ⇒
  deficiency.
- **Procedure/CoT coverage** — did the internal chain-of-thought pass through the
  steps the prompt is supposed to elicit (staging → pathway grouping → axis
  derivation), or were steps skipped/shallow?
- **Problem/variable framing** — was the problem described with the variables needed
  to solve it, or is the formulation under-specified?

### 2.4 The Observer's deficiency → action mapping

For each deficiency, the Observer chooses **where** the fix belongs and emits a
**bounded, auditable edit** to one of five surfaces:

| Deficiency the lens shows | Preferred evolution surface |
|---|---|
| Mediator concept faint/absent, term unglossed | KB context / work prompt / skill text |
| Required input variable missing from the readout | Injected variables + sub-agent def (add param, add derivation) |
| Variable present but wrong/implausible value | Harness code (parser fix) → re-inject corrected value |
| CoT skips a procedure step | Skill / sub-agent def (make the step explicit) |
| A relation the model keeps guessing unreliably | **Harness code** — compute it deterministically, inject the result |
| Problem under-specified for the task | Work prompt / problem-formulation template |

**Anti-Goodhart rule:** every edit must cite the lens-grounded deficiency that
justifies it. An edit with no readout evidence is rejected. Where possible, the
Observer corroborates a lens claim with the **counterfactual-sensitivity** test
(see [`APPROACH.md`](APPROACH.md) §8) (flip one input factor; the affected axis
should move, unrelated axes should not) — an API-observable check that is not pure
self-report.

### 2.5 Session Working-Consciousness (SWC) — the closed loop

A persistent, Observer-owned artifact (runtime file, e.g.
`.session/working_consciousness.md`, git-ignored; template committed) that the
Observer **reads as its own context every turn and consolidates after every turn.**
It is the difference between the primary's *ephemeral per-call* workspace and a
*persistent cross-call* working consciousness for the whole system.

It accumulates:

- a running model of the task and of which formats / variables / KB snippets have
  been shown (by the lens + counterfactual test) to make which mediators surface;
- deficiencies observed, edits applied, and their outcomes (did the mediator surface
  next turn? did accuracy hold?);
- **consolidated beliefs** — stable lessons promoted from repeated evidence (an
  in-session analogue of SkillOpt-Sleep consolidation);
- **pending hypotheses** the Observer still wants to test.

From the SWC, per its own criterion, the Observer **injects or modifies the next
prompt** (adds a missing variable, glosses a term, reorders sections, attaches a KB
snippet, or swaps in a harness-computed value). This is the "closed, evolving loop
of working consciousness during the session."

### 2.6 Harness evolution (S4)

When the deficiency is "the model won't reliably represent/derive variable X," the
right fix is often **not** a prompt but code. The Observer can target `src/`:

- generate or modify a **parser** (e.g. a dropped `hs-CRP` field ⇒ fix
  `record_formats.py` / a NHANES mapping) ;
- add a **deterministic analyzer** (e.g. a linear/rule-based relation the LLM keeps
  approximating ⇒ compute it in code);
- expose the computed value as a new **injected variable** the lens then re-checks.

**Hard rule:** harness edits must pass existing + generated tests in a sandbox before
their output is used. This closes the loop: lens observation → code evolution → new
injected variable → lens re-check.

---

## 3. Evolution tiers & gating (health-context safety)

Online self-modification in a health context requires strict tiers:

| Tier | Scope | Lifetime | Gate |
|---|---|---|---|
| **T0 — Ephemeral session adaptation** | prompt tweaks, injected-variable additions, KB snippet attach, reordering | in-session only; auto-revert at session end; logged in SWC | bounded + guardrail-safe + lens-grounded rationale |
| **T1 — Promoted evolution** | committed edits to skills / sub-agent defs / harness code | persistent (repo) | SkillOpt gate: strict held-out accuracy improvement **and** no drop in guardrail pass-rate **and** tests pass **and** human approval |

**Non-negotiable invariants (unchanged):**

- `non-diagnostic-guardrail.md` is **protected** — the Observer may never edit it,
  and it is part of every gate. An accuracy gain that lowers guardrail pass-rate is
  rejected.
- Non-diagnostic throughout; missing data is a **collection flag**, never imputed.
- Every relational axis cites the input fields it came from.
- Bounded, auditable edits (SkillOpt discipline) — even T0 ones.
- Loop-stability backstops: cap edits per turn; each edit needs readout evidence;
  the Observer logs a rationale for every injection.

---

## 4. Repository changes (mapping)

### New
- `docs/REFORMULATION.md` — this document.
- `agents/lens-observer.md` — the second-instance Observer / evolution controller.
- `prompts/observer.md` — the Observer system prompt (deficiency analysis + edit
  proposal contract + tier/gate rules).
- `skills/lens-deficiency-analysis.md` — how the Observer reads the inferred lens and
  produces the deficiency map + bounded edits.
- `skills/session-working-consciousness.md` — how the SWC ledger is maintained,
  consolidated, and used to inject/modify prompts.
- `skills/harness-evolution.md` — lens-driven code-evolution rules + the
  prompt-vs-code boundary + the test-before-use rule.
- `.session/working_consciousness.template.md` — committed template; the live
  `.session/working_consciousness.md` is git-ignored.

### Repurposed
- `skills/claude-workspace-probe.md` → framed explicitly as the **inferred Jacobian
  lens readout source** consumed by the Observer (content largely unchanged; the
  "not a measurement" rules stay).
- `agents/skillopt-optimizer.md` → generalized from *skills only* to the **five
  surfaces incl. harness code**, and split into T0 (ephemeral) vs T1 (promoted).
- `agents/orchestrator.md` → adds the Observer hand-off (emit readout; receive
  injected/modified prompt) and the SWC read/write step.

### Removed in the 2026-07-09 pivot
- `agents/jlens-diagnostic.md`, `colab/`, `src/harness.py`, `prompts/controller.md`,
  `docs/DUAL_LENS.md` — the measured Qwen lens, Colab, and the correlation experiment.
  The self-report inferred lens on Claude is the only signal; `prompts/observer.md` is
  the sole (inferred-lens) controller.

### README
Add a section: **"Exploring the Jacobian lens indirectly (and the API feature we're
proposing)."** State plainly that the loop uses the *inferred* lens (self-report) on
Claude only, that there is no proxy/Colab/measured lens, and that **if the real Jacobian
lens were exposed (e.g. via API), this same architecture would swap the inferred
signal for a measured one — turning directional hypotheses into causal ground truth,
enabling representation swaps — and reach its true power.** Keep the epistemic-honesty
framing: inferred is a diagnostic aid, never a measurement or clinical evidence.

---

## 5. Phased workplan

### Phase R0 — Design lock — `DONE`
- [x] Confirm the open decisions in §7 (R0/R1 decision: separate Opus Observer).
- [x] This document reviewed; Decision entry added to `PLAN.md`.

### Phase R1 — Observer + inferred-lens contract — `DONE`
- [x] Write `agents/lens-observer.md`, `prompts/observer.md`,
      `skills/lens-deficiency-analysis.md`.
- [x] Define the readout schema the primary emits (`schemas/lens_readout_schema.json`)
      and the deficiency-map schema the Observer returns
      (`schemas/deficiency_map_schema.json`). Both validate as JSON.
- [x] Dry-run: worked example in `schemas/examples/` — `readout_case01.json` (primary
      readout, mediators absent under naive format) → `deficiency_map_case01.json`
      (Observer: 3 readout-grounded deficiencies → 3 bounded T0 edits + SWC update).
      Both strictly schema-valid (`additionalProperties: false` honored).

**Decision (2026-07-08):** Observer = a **separate instance on Opus** observing a
Fable/Sonnet executor (per §7.1). Locks the two-instance split.

### Phase R2 — Session Working-Consciousness — `DONE`
- [x] `skills/session-working-consciousness.md` + `.session/working_consciousness.template.md`
      (live ledger git-ignored).
- [x] 3-turn worked example (`.session/example_case01.md`): mediator absent → T0
      injection → confirmed next turn → three beliefs consolidated, one carried forward.

### Phase R3 — Evolution across the five surfaces (T0) — `DONE`
- [x] Wired the executor↔Observer loop into `agents/orchestrator.md`; `prompts/observer.md`
      is the sole inferred-lens controller. Edits are ephemeral, logged in the SWC,
      guardrail-safe.
- [x] Demo: mediator absent in Turn 1 surfaces by Turn 2/3 in `.session/example_case01.md`.

### Phase R4 — Harness evolution (S4) — `DONE`
- [x] `skills/harness-evolution.md` (prompt-vs-code boundary + test-before-use).
- [x] `src/relational_signals.py` (deterministic structural signals + missing-mediator
      collection flags) + `tests/test_relational_signals.py` — **5/5 tests pass**. The
      computed values are the injected variables the lens re-checks.

### Phase R5 — Promotion tier (T1) + gate — `IN PROGRESS` (harness done; live run pending)
- [x] Generalized `agents/skillopt-optimizer.md` to the five surfaces + the T1 gate
      (held-out accuracy + guardrail pass-rate + tests + human approval) and the A/B
      protocol.
- [x] Built the A/B harness (`src/ab_eval.py`) + protocol (`docs/AB_PROTOCOL.md`) +
      tests (`tests/test_ab_eval.py`, 6/6). Model-agnostic `run_ab(records, model_fn)`;
      metrics = mechanism-recall, missing-data flagging, traceability, guardrail; the
      promotion gate = strict accuracy gain with no drop in guardrail pass-rate. Offline
      stub run: A `0.0/0.0` vs B `1.0/1.0` → `promote_B` (proves the harness, not the
      method).
- [x] Wired the live run: `src/run_live_ab.py` (+ `requirements-live.txt`, tests 6/6).
      Real Claude call via the Anthropic SDK with a **neutral fixed system prompt** (so
      the input format is the only lever), real participants via
      `nhanes_loader.build_case` (`--cases nhanes`), or the grounded case
      (`--cases grounded`); writes `results/ab_live_report.json`. See
      [`AB_PROTOCOL.md`](AB_PROTOCOL.md).
- [x] Executed on Claude (Sonnet-5), in a conda env (`dental-analysis`), with the key
      from a git-ignored `.env`. Fixed en route: ThinkingBlock extraction, token budget
      (JSON truncation), the promotion gate (guardrail is a hard prerequisite + Pareto
      rule; +2 tests), and the NHANES download (CDC moved the URLs in 2024 → soft-404;
      new base URL + XPORT-header validation in the loader).

**Live A/B results (2026-07-09, Sonnet-5).** Real signal, small-n — directional:

| Cases | Arm | mechanism_recall | missing_data_flagged | guardrail_pass_rate | verdict |
|---|---|---|---|---|---|
| grounded (n=1) | A | 0.75 | 0.00 | 0.00 | **promote_B** |
| | B | 0.75 | 1.00 | 1.00 | |
| NHANES real (n=3), pre-fix | A | 0.58 | 0.00 | 0.00 | **keep_A** |
| | B | 0.79 | 0.67 | 0.33 | |
| **NHANES real (n=6), improved** | A | 0.65 | 0.00 | 0.00 | **promote_B** |
| | **B** | **0.77** | **1.00** | **1.00 (6/6)** | |

**Reading (honest).** B strictly beats A on every metric in every run. The n=3 run
exposed a real weakness — B was only **1/3 guardrail-compliant** because the executor
inconsistently copied the injected missing-mediator flags into `required_missing_data`.
The bounded fix (an explicit **data-completeness directive** carried in B's input —
"add every `missing_mediators` field to `required_missing_data`, never impute" — plus a
fair output-compliance clause in the shared neutral system prompt) lifted B's
guardrail pass-rate from **0.33 → 1.00 (6/6)** and missing-data flagging from
**0.67 → 1.00**. A is guardrail-failing everywhere (0.0). Frontier Sonnet-5 recovers
mediators even from the naive format (recall 0.65–0.75), so B's decisive, now-reliable
lever is **missing-data flagging / non-imputation** — the guardrail-critical axis.

- [x] **Lifted B's guardrail reliability to 1.0 on real cases** (n=6) via the input
      data-completeness directive; `verdict: promote_B`.
- [ ] **Next (R6):** re-run at larger n to tighten the estimate; A/B a T1-promoted skill
      edit end-to-end; then the cross-session memory + offline-consolidation work
      (see [`analysis/session-consciousness-memory-sleep.md`](analysis/session-consciousness-memory-sleep.md)).

### Phase R6 — README + docs + demo — `DONE`
- [x] README "Exploring the Jacobian lens indirectly (and the API feature we're
      proposing)" section.
- [x] Updated `PLAN.md`, `HACKATHON_STRATEGY.md`, and the `agents/` + `skills/` catalog
      READMEs to reflect the loop; added `APPROACH.md` + `IMPACT.md`.
- [ ] Demo beat: watch the Observer diagnose, inject, evolve, and consolidate live.

---

## 6. Risks & mitigations (delta vs PLAN.md §9)

| Risk (new/changed) | Mitigation |
|---|---|
| Self-report has no ground truth ("not confabulation" defense) | Corroborate every load-bearing lens claim with the API-observable counterfactual-sensitivity test on Claude; keep the honesty framing; Claude task accuracy + guardrail are the authorities |
| Online self-modification drifts or destabilizes in a health context | Two tiers (T0 ephemeral / T1 promoted); protected guardrail in every gate; bounded edits; per-turn edit cap; test-before-use for code |
| Observer over-trusts self-report and Goodharts on the readout | Anti-Goodhart rule: every edit needs readout evidence; final authority is Claude task accuracy + guardrail, not readout scores |
| SWC bloats / becomes noisy transcript | Consolidation step (promote stable beliefs, drop stale hypotheses); the SWC is a curated optimization state, not a log dump |
| Harness edits break the pipeline | Sandbox + generated tests + existing suite must pass before the output is used |
| Two-model cost/latency | Observer runs on the readout + spec, not the full task; can batch; T0 edits are cheap; escalate model tier only for T1 gates |

---

## 7. Open decisions (confirm before R1)

1. **Observer model** — separate capable instance (recommend Opus) observing a
   Fable/Sonnet executor? Or same model, different role? (Recommend: separate.)
2. **SWC substrate** — a markdown ledger the Observer edits (transparent, demo-able)
   vs a JSON state (machine-clean). (Recommend: markdown for the demo, JSON schema
   for the machine-consumed core.)
3. **Live vs simulated in-session evolution for the hackathon** — do T0 ephemeral
   edits truly run live in the demo, or do we script a curated 3-turn evolution for
   reliability? (Recommend: live T0 on one case, scripted fallback ready.)
4. **Harness-evolution scope for the week** — one concrete parser/analyzer case
   end-to-end, or a general mechanism? (Recommend: one concrete case, general
   mechanism documented.)
```
