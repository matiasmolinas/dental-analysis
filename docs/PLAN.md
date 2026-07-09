# HISTORA Oral-Systemic Intelligence Agent — Project Plan

> **Living document.** Updated as we learn. Each experiment run appends findings to
> the [Progress Log](#progress-log) and, when a decision changes direction, to
> [Decisions](#decisions). Status tags: `TODO` / `IN PROGRESS` / `DONE` / `BLOCKED`.

**Last updated:** 2026-07-09
**Owner:** matias.molinas@gmail.com
**Runs on Claude only** — no open-weights proxy, no GPU, no Colab. Canonical method
is [`APPROACH.md`](APPROACH.md).
**Context:** Built with Claude: Life Sciences (Anthropic × Cerebral Valley ×
Gladstone), 2026-07-07 → 2026-07-13. See [`HACKATHON_STRATEGY.md`](HACKATHON_STRATEGY.md).
**Method:** [`APPROACH.md`](APPROACH.md) (canonical, domain-general) · reformulation
delta + R0–R6 workplan in [`REFORMULATION.md`](REFORMULATION.md) · impact analysis in
[`IMPACT.md`](IMPACT.md).
**Data:** NHANES 2009–2010 (real anchor) + Synthea (longitudinal) — see [`DATASETS.md`](DATASETS.md).

---

## 1. One-paragraph summary

We build a **non-diagnostic** research agent that relates periodontal data
(probing depths, bleeding on probing, bone loss, treatments, radiographs) to
medical / cardiovascular data (hypertension, diabetes/HbA1c, lipids, smoking,
medications, CV history) and surfaces oral-systemic risk profiles plus research
hypotheses. The differentiator is not the model but **HISTORA as the data layer**
that integrates otherwise-fragmented dental and medical records. The technical
novelty is that we explore Anthropic's **Jacobian-lens paper indirectly, through a
self-report skill (`claude-workspace-probe`) on Claude**, to see whether our input
format actually makes the oral-systemic mediating concepts representable — and we
let Claude close the optimization loop rather than prompt-engineering blind. The
signal is an **inferred lens**: self-report exercised as a readout channel — **not
a measurement, not clinical evidence**. Because it is self-report, load-bearing
claims are corroborated with an **API-observable counterfactual-sensitivity** test
(see §3c). Everything runs on Claude — no proxy, no GPU.

---

## 1b. Working hypothesis (load-bearing)

A **second Claude instance (the Lens Observer, on Opus)**, by analyzing the primary
model's **inferred-lens readout** — the self-report skill exercised as a readout
channel — given the input **data structure**, the **problem formulation**, and the
**chain of thought**, can decide which **values to complete** (as collection flags,
never imputed), which **input formats to adjust**, and which **additional knowledge
context to inject or modify**. The optimized, complete input is then **evaluated on
the most capable Claude**, and that learning becomes the fitness signal for
**autonomous evolution of the subagents and skills** (gated). Because the readout is
self-report (not a measurement), any load-bearing claim is corroborated with an
**API-observable counterfactual-sensitivity** test — flip one input factor and the
dependent axis should move while unrelated axes stay put — on Claude only.

## 2. Scientific rationale

The periodontal <-> cardiovascular association is, clinically, a chain of
**hidden mediators**: periodontal pathogens -> systemic inflammatory burden
(hs-CRP, IL-6, TNF-alpha) -> endothelial dysfunction -> atherosclerosis, plus
shared risk factors (diabetes, smoking). The paper *"Verbalizable Representations
Form a Global Workspace in Language Models"* (transformer-circuits.pub/2026/workspace)
defines the model's **J-space** as a small, evolving set of unspoken words naming
the concepts it is currently reasoning with. Our task *is* finding hidden
cross-domain mediators — so the lens is not decoration. We do not measure that
J-space directly (we have no instrument on Claude); instead we explore the idea
**indirectly**, via a self-report skill that asks Claude to name the concepts it is
reasoning with. This **inferred lens** is a readout channel, not a measurement: it
gives us a per-format view of whether, under a given input format, the model
surfaces the mediating mechanisms (inflammation, atherosclerosis, endothelial
dysfunction, bacteremia) or is merely listing oral and systemic numbers side by
side. Because it is self-report, we corroborate any load-bearing reading with a
counterfactual-sensitivity test on Claude (§3c).

**Optimization criterion:** a good input format is one that makes the *mediator*
concepts appear in the inferred-lens **surfaced-mediator set** — not just the shared
factors (diabetes, smoking), which a model can surface by mere copying.

---

## 3. Architecture

Three roles, Claude only:

| Role | Instance | Function |
|---|---|---|
| **Executor** | Claude (primary) | Runs the analysis and emits an **inferred-lens readout** via the self-report skill (`claude-workspace-probe`) — the concepts it is reasoning with |
| **Lens Observer** | Claude (Opus, separate instance) | Reads the primary's inferred-lens readout + target mediators; diagnoses deficiencies; drives bounded, gated evolution across five surfaces; curates the Session Working-Consciousness ledger and injects prompts |
| **Gate / Guardrail** | Claude + tests | Non-diagnostic invariant + held-out accuracy gate; **PROTECTED — never evolved** |

```
candidate input ─► Claude executor ─► inferred-lens readout (surfaced-mediator set)
       ▲                                        │
       │                                        ▼
   format/context/KB/agent/harness edits ◄── Lens Observer (Opus) ◄── deficiency map
       │                                        │
       │                              corroborate via counterfactual-sensitivity (Claude)
   (converged) ─► Claude evaluator ─► structured non-diagnostic output ─► accuracy on Claude
```

**Why input-structure edits generalize:** what the Observer optimizes is *structural
representability of relations* (glossing terms, co-presenting oral+systemic data,
injecting the mechanistic KB, computing deterministic relations in the harness) —
edits to the input structure that help for reasons independent of any single prompt.
The final metric is always task accuracy measured on Claude, plus the protected
non-diagnostic guardrail.

---

## 3b. Agent architecture (runtime) and skill evolution

The inferred lens is a **readout channel**, not the runtime system. In production
the work is done by a Claude orchestrator with subagents; the inferred-lens readout
and the Lens Observer form the **in-session** loop that improves the skills those
subagents run. Readout and agents are complementary, at different layers — not
competing.

### Runtime subagents (production pipeline)

| Subagent | Function | Optimizable by |
|---|---|---|
| Orchestrator (main) | Plan, route, assemble final output | SkillOpt |
| Record Normalizer | Integrate fragmented dental+medical records (HISTORA core) -> schema; flag missing fields | inferred lens (format) + SkillOpt |
| Periodontal Analyst | Staging/grading (AAP/EFP 2017), longitudinal progression | SkillOpt |
| Cardiometabolic Analyst | Non-diagnostic framing of CV risk factors | SkillOpt |
| Oral-Systemic Relational Reasoner | Core: inflammatory/metabolic/behavioral/vascular axes & mediators | **inferred lens (primary)** + SkillOpt |
| Guardrail / Verifier | Non-diagnostic, no value imputation, traceability, confidence (adversarial) | **PROTECTED — never evolved** |
| Hypothesis Generator | Research hypotheses for follow-up | SkillOpt |

In-loop: the **Claude Workspace Probe** (self-report on Claude — emits the inferred
lens), the **Lens Observer** (Opus — diagnoses deficiencies and drives evolution),
and the **SkillOpt Optimizer** (skill.md evolution).

### Skills

`oral-systemic-analysis` (core), `record-normalization`, `periodontal-staging`,
`cardiometabolic-framing`, `oral-systemic-kb` (retrievable mediator mechanisms),
`traceability-audit`, `claude-workspace-probe` (runtime-native self-report), and
`non-diagnostic-guardrail`. The guardrail is a **protected invariant**, not a
trainable skill.

## 3c. Inferred-lens Observer loop (self-report on Claude, corroborated)

Full detail in [`APPROACH.md`](APPROACH.md). One readout channel, one observer, all
on Claude:

- **Claude Workspace Probe** (`claude-workspace-probe`): uninstrumented introspective
  self-report ON CLAUDE. Fast, zero GPU, captures CoT natively, runs the loop. This
  is the **inferred lens** — a readout channel, **not a measurement**. Inspired by
  `Doriandarko/skirano-skills` j-space-lens.
- **Lens Observer** (`agents/lens-observer.md`, on Opus): a separate Claude instance
  that reads the primary's inferred-lens readout, diagnoses deficiencies, and drives
  bounded, gated evolution across five surfaces.

**The loop:** the executor emits the inferred-lens readout; the Observer screens
format/context/CoT/agent/harness edits and injects fixes. Because it is self-report,
any load-bearing reading is corroborated by an **API-observable counterfactual-sensitivity**
test — flip one input factor (smoking / diabetes / hs-CRP / hypertension); the
dependent axis should move, unrelated axes stay put — on Claude only, no external
instrument. The authoritative gate stays Claude task accuracy + the protected
guardrail.

**The unlock (speculative).** Because the indirect results look promising — and we
are *speculating*, we have no ground truth — we propose a concrete desirable API
feature: **expose the real Jacobian lens on Claude through the Anthropic API.** If
exposed, this same loop swaps the inferred signal for a measured one with **no
architectural change**.

### Skill evolution: SkillOpt gated on Claude accuracy (the T1 tier)

Adopt **SkillOpt** (Microsoft Research) as the skill-optimization framework:
skills as trainable parameters, optimized via rollout -> reflect -> edit -> gate
with bounded, auditable edits accepted only on held-out improvement. Compose:

```
inferred-lens surfaced-mediator set (cheap, pre-output, on Claude)  ─►  pre-filter candidate skill edits
        ▼
SkillOpt bounded edit loop  ─►  gate = Claude held-out accuracy + guardrail pass-rate + tests
        ▼
human approval  ─►  versioned skill (rollback available)
```

Tiers: **T0 ephemeral** edits live only in-session; **T1 promoted** edits must pass
held-out accuracy + guardrail + tests + human approval. SkillOpt optimizes skills
for the model that *runs* them — here that is Claude — so the authoritative gate
runs on Claude; the inferred lens is only a cheap pre-filter.

### Evolution guardrails (non-negotiable in a health context)

- Evolve the **skills**, never the **guardrails**. `non-diagnostic-guardrail` and
  the "no value imputation / full traceability" tests are invariants and part of
  every gate (an edit that lowers guardrail pass-rate is rejected even if it
  raises accuracy).
- Human-in-the-loop to promote any new skill version.
- Regression suite (clinical cases + compliance) runs at every gate.
- Autonomous != unsupervised: the agent may propose and pre-evaluate improvements
  on its own; promotion to production requires passing the gate.

**Lightweight alternative for the hackathon:** implement the rollout->reflect->
edit->gate loop directly on the Claude Agent SDK's native subagents + skills,
borrowing SkillOpt's *design* (bounded edits + held-out gate) without adopting its
codebase, if time is tight.

---

## 4. Key design decisions

- **Non-diagnostic, always.** Output is research hypotheses + data-completeness
  flags. **No patient-value imputation** — missing mediating data (e.g. hs-CRP)
  becomes a *collection flag*, not a guess. Encoded in `schemas/output_schema.json`
  (`non_diagnostic_disclaimer: const true`, no value-imputation field).
- **Claude only.** No open-weights proxy, no GPU, no external instrument. The lens
  is explored indirectly via the self-report skill; corroboration is the
  API-observable counterfactual-sensitivity test on Claude.
- **English-only** across all code, artifacts, prompts, and skills.
- **Bridge concepts** live in `src/bridge_concepts.py`; mediators weighted above
  shared factors.
- **Metric:** the inferred-lens **surfaced-mediator set** per format (does each
  mediator appear?), corroborated by counterfactual sensitivity; Claude task
  accuracy is authoritative.

---

## 5. Repository layout

```
dental-analysis/
  docs/
    PLAN.md                    # this document (living)
    HACKATHON_STRATEGY.md      # tracks, named user, one-week plan, demo, judging
    APPROACH.md                # canonical method (indirect inferred-lens Observer loop)
    REFORMULATION.md           # reformulation delta + R0–R6 workplan
    IMPACT.md                  # impact analysis
  src/
    bridge_concepts.py         # target mediator + shared concepts
    record_formats.py          # NHANES-grounded case, candidate formats (A–E)
    relational_signals.py      # deterministic structural signals injected into the input
    nhanes_mapping.py          # schema field -> NHANES 2009-2010 file+variable codes
    nhanes_loader.py           # download XPT + build a grounded case (pandas.read_sas)
  schemas/
    output_schema.json         # non-diagnostic structured output contract
    lens_readout_schema.json   # inferred-lens readout contract
    deficiency_map_schema.json # Lens Observer deficiency-map contract
    examples/                  # worked readout + deficiency-map examples
  prompts/
    observer.md                # Lens Observer prompt (diagnose + drive evolution)
    evaluator.md               # Claude final-analysis prompt
  agents/                      # runtime subagents + claude-workspace-probe + lens-observer
  skills/                      # 8 skills (guardrail protected) — see skills/README.md
  tests/                       # guardrail + regression + relational-signal tests
  .session/                    # Session Working-Consciousness ledger (per case)
  README.md
```

---

## 6. Candidate input formats (initial)

Five formats isolate the levers we optimize (see `src/record_formats.py`):

- **A — abbreviated table**, dental-first, no term glossing. *(baseline)*
- **B — named sections + glossed terms** (e.g. "BOP = gingival inflammation
  marker"), medical-first.
- **C — narrative prose with an explicit mechanistic KB bridge** (periodontitis
  -> systemic inflammation -> CV risk via CRP).
- **D — structured JSON** record (schema-shaped), no narrative, no KB.
- **E — JSON + KB + interpretability constraints** (reason explicitly through the
  mediators; flag missing data; no imputation; non-diagnostic).

**Hypothesis:** E >= C >= B >> A on the surfaced-mediator set; D isolates whether
structure alone (without glossing/KB) helps. If A already surfaces the mediators,
the knowledge is latent and the work is recall, not format.

---

## 7. Workplan & status

### Phase 0 — Scaffolding — `DONE`
- [x] Separate `dental-analysis` project.
- [x] Bridge concepts, record formats, relational signals (compile + load verified).
- [x] Output schema, observer/evaluator prompts, Claude skill.
- [x] This plan.
- [x] Full skill set (`skills/`): oral-systemic-analysis, record-normalization,
      periodontal-staging, cardiometabolic-framing, oral-systemic-kb,
      traceability-audit, non-diagnostic-guardrail (protected).
- [x] Full subagent set (`agents/`): orchestrator + 6 runtime specialists +
      claude-workspace-probe + lens-observer + skillopt-optimizer. Catalog READMEs.
- [x] SkillOpt cloned as sibling reference (`../SkillOpt/`).
- [x] Inferred-lens methodology: `claude-workspace-probe` skill + subagent;
      `docs/APPROACH.md`; `docs/HACKATHON_STRATEGY.md`.

### Phase 1 — Inferred-lens inner loop on Claude — `IN PROGRESS`
- [ ] Activate `claude-workspace-probe`; run the formats on synthetic cases; log the
      surfaced-mediator set per format.
- [ ] Ground cases in real data: download NHANES 2009–2010 (`src/nhanes_loader.py`),
      aggregate `OHXPER_F` per-site PPD/CAL/BOP, build grounded cases to replace the
      hand-written values in `src/record_formats.py`.
- [ ] (Optional) reproducible CRP↔periodontitis mini-analysis on 2009–2010.
- [ ] Iterate format/KB/CoT edits on Claude until mediators surface. This is the
      primary inner loop and the demo backbone.

### Phase 2 — Lens Observer loop + counterfactual corroboration — `TODO`
- [ ] The Lens Observer (Opus) reads the inferred-lens readout, returns a deficiency
      map, and injects T0 fixes across the five surfaces; re-run until all mediators
      surface. Log which edits moved which mediators in `.session/`.
- [ ] Corroborate each load-bearing reading with a counterfactual-sensitivity test on
      Claude (flip one factor; dependent axis moves, unrelated axes stay put).
- [ ] **Document the unlock:** propose exposing the real Jacobian lens on Claude via
      the Anthropic API — same loop, measured signal, no architectural change.

### Phase 3 — Evaluator + validation — `TODO`
- [ ] Claude evaluator produces structured output on converged format (real-ish cases).
- [ ] Task-accuracy A/B: Observer-converged vs naive input, measured on Claude
      (authoritative).

### Phase 4 — Autonomous skill evolution (gated) — `TODO`
- [ ] SkillOpt-style loop on 1–2 trainable skills; inferred lens as pre-filter,
      Claude accuracy + guardrail pass-rate + tests as the gate; human-in-the-loop
      promote (T1).
- [ ] Regression suite (clinical cases + compliance) at every gate.

### Phase 5 — Demo & submission — `TODO`
- [ ] End-to-end story: HISTORA data layer + inferred-lens Observer loop + Claude
      + gated evolution. Demo script in `docs/HACKATHON_STRATEGY.md`.
- [ ] Guardrail walkthrough (non-diagnostic, collection-not-imputation).
- [ ] Writeup + video; Build-track tool + the API-feature proposal (the unlock).

---

## 8. Metrics we track

- **Surfaced-mediator set** per format (primary inferred-lens signal, on Claude):
  which target mediators the self-report surfaces under each input format.
- **Counterfactual sensitivity:** flip smoking / diabetes / hs-CRP / hypertension →
  does the affected axis move coherently (and unrelated axes stay put)? The
  API-observable corroboration of a self-report reading (Claude only, no external
  instrument).
- **Claude task accuracy** (final, authoritative) and **mechanism-recall** on the
  behavioral check.

---

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Goodhart (optimizing surfaced-mediators, not clinical quality) | The surfaced set is a hypothesis-generator; Claude accuracy is the objective |
| Self-report captures only verbalizable | Task accuracy stays primary; the inferred lens is diagnostic, not the target |
| Non-diagnostic drift | Schema forbids value imputation; guardrails in skill + evaluator prompt; protected invariant, never evolved |
| Self-report confabulation (inferred lens) | Never presented as measurement; corroborated by the counterfactual-sensitivity test; Claude accuracy is authority |
| Scope creep | Build track primary; the API-feature proposal (the unlock) is a bounded, speculative add-on, not a second project |

---

## 10. Open questions

- Does the mechanistic KB (format C) actually enlarge the surfaced-mediator set, or is it redundant?
- How reliably does counterfactual sensitivity corroborate a self-report reading?
- If the real Jacobian lens were exposed on the Anthropic API, how closely would the measured signal track the inferred one?
- Best real (de-identified) case sources via HISTORA for Phase 3?

---

## Decisions

- **2026-07-07** — Use a separate `dental-analysis` project; do not modify
  `jacobian-lens` (copy walkthrough rather than move).
- **2026-07-07** — All code, artifacts, prompts, and skills in English.
- **2026-07-07** — Non-diagnostic scope is a hard constraint: collection flags,
  never patient-value imputation.
- **2026-07-07** — **Interpretability is complementary to Claude agents, not a
  substitute:** a dev-time readout channel vs. runtime production system. Adopt a
  Claude orchestrator + subagents for runtime (see §3b).
- **2026-07-07** — **Adopt SkillOpt for skill evolution, gated on Claude accuracy.**
  The inferred-lens surfaced-mediator set is a cheap pre-filter; the authoritative
  gate is Claude held-out accuracy + guardrail pass-rate + tests. Guardrails are
  protected invariants, never evolved. Lightweight fallback: replicate the loop on
  the Claude Agent SDK.
- **2026-07-08** — **Inferred-lens loop adopted.** Add a runtime-native self-report
  instrument (`claude-workspace-probe`, inspired by `Doriandarko/skirano-skills`
  j-space-lens) as the inner loop on Claude — the inferred lens, a readout channel,
  not a measurement. The skirano skill is referenced, **not vendored** (its repo has
  no license); we ship our own domain-adapted skill.
- **2026-07-08** — **Hackathon positioning:** Build track primary (named user =
  perio-cardio research clinic on HISTORA); the differentiator is the method plus a
  humble, speculative API-feature proposal to Anthropic (does not need the Gladstone
  datasets). See `docs/HACKATHON_STRATEGY.md`.
- **2026-07-08** — **Datasets: NHANES 2009–2010 as the real anchor + Synthea for
  longitudinal.** 2009–2010 uniquely pairs the full-mouth periodontal exam with CRP
  (public, de-identified, no DUA). NHANES is cross-sectional → Synthea (custom
  periodontal module) supplies per-patient progression and shareable demo data.
  Linked EDR+EHR / UK Biobank named but access-gated, not used in the event. Mapping
  in `src/nhanes_mapping.py`, loader in `src/nhanes_loader.py`, detail in
  `docs/DATASETS.md`. Enables a reproducible CRP↔periodontitis mini-analysis
  (Research-track).

- **2026-07-08** — **Reformulation adopted (see [`REFORMULATION.md`](REFORMULATION.md)).**
  Move from an offline dev-time pipeline to a live, in-session self-evolving system:
  (1) a **separate Lens Observer instance (Opus)** analyzes the executor's *inferred*
  lens readout and drives evolution; (2) the **inferred lens is the only live
  signal** — exposing the real Jacobian lens on the Anthropic API is documented as the
  "unlock"; (3) a **Session Working-Consciousness** ledger is the closed in-session
  evolutionary loop; (4) evolution targets five surfaces incl. **harness code**.
  Guardrail stays protected; edits are tiered (T0 ephemeral / T1 promoted + human
  gate). R1 artifacts landed: `agents/lens-observer.md`, `prompts/observer.md`,
  `skills/lens-deficiency-analysis.md`, `schemas/lens_readout_schema.json`,
  `schemas/deficiency_map_schema.json`.

- **2026-07-09** — **Pivot to Claude-only.** Removed the Qwen proxy, the measured
  Jacobian lens, Colab, and the dual-lens correlation experiment (deleted `colab/`,
  `agents/jlens-diagnostic.md`, `prompts/controller.md`, `src/harness.py`,
  `docs/DUAL_LENS.md`). We now explore the Jacobian-lens paper indirectly via the
  self-report skill on Claude; corroborate with counterfactual-sensitivity; and
  propose exposing the real Jacobian lens on the Anthropic API as the unlock.

---

## Progress Log

- **2026-07-07 — Phase 0 complete.** Scaffolding, schema, prompts, skills, and
  subagents created and verified (modules compile/load; schema valid JSON).
- **2026-07-08 — Inferred-lens + hackathon strategy.** Added `claude-workspace-probe`
  skill + subagent, `docs/APPROACH.md`, `docs/HACKATHON_STRATEGY.md`; structured the
  phases around the inferred-lens Observer loop and gated evolution. SkillOpt cloned
  as sibling reference.
- **2026-07-09 — Pivot to Claude-only.** Removed the Qwen proxy, the measured
  Jacobian lens, Colab, and the dual-lens correlation experiment (deleted `colab/`,
  `agents/jlens-diagnostic.md`, `prompts/controller.md`, `src/harness.py`,
  `docs/DUAL_LENS.md`). The project now explores the Jacobian-lens paper indirectly
  via the self-report skill on Claude, corroborates with counterfactual-sensitivity,
  and proposes exposing the real Jacobian lens on the Anthropic API as the unlock.
- **(next)** — Phase 1/2 results: paste the inferred-lens surfaced-mediator set per
  format and the counterfactual-sensitivity outcomes here to continue.
