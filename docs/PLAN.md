# HISTORA Oral-Systemic Intelligence Agent — Project Plan

> **Living document.** Updated as we learn. Each experiment run appends findings to
> the [Progress Log](#progress-log) and, when a decision changes direction, to
> [Decisions](#decisions). Status tags: `TODO` / `IN PROGRESS` / `DONE` / `BLOCKED`.

**Last updated:** 2026-07-07
**Owner:** matias.molinas@gmail.com
**Context:** Anthropic Life Sciences Hackathon

---

## 1. One-paragraph summary

We build a **non-diagnostic** research agent that relates periodontal data
(probing depths, bleeding on probing, bone loss, treatments, radiographs) to
medical / cardiovascular data (hypertension, diabetes/HbA1c, lipids, smoking,
medications, CV history) and surfaces oral-systemic risk profiles plus research
hypotheses. The differentiator is not the model but **HISTORA as the data layer**
that integrates otherwise-fragmented dental and medical records. The technical
novelty is that we use **mechanistic interpretability (the Jacobian lens) on a
small open-weights proxy to verify that our input format actually makes the
oral-systemic mediating concepts representable**, and we let Claude close the
optimization loop — rather than prompt-engineering blind.

---

## 2. Scientific rationale

The periodontal <-> cardiovascular association is, clinically, a chain of
**hidden mediators**: periodontal pathogens -> systemic inflammatory burden
(hs-CRP, IL-6, TNF-alpha) -> endothelial dysfunction -> atherosclerosis, plus
shared risk factors (diabetes, smoking). The paper *"Verbalizable Representations
Form a Global Workspace in Language Models"* (transformer-circuits.pub/2026/workspace)
defines the model's **J-space** as a small, evolving set of unspoken words naming
the concepts it is currently reasoning with. Our task *is* finding hidden
cross-domain mediators — so the J-lens is not decoration: it directly measures
whether, under a given input format, the model internally represents the
mediating mechanisms (inflammation, atherosclerosis, endothelial dysfunction,
bacteremia) or is merely listing oral and systemic numbers side by side.

**Optimization criterion:** a good input format is one that makes the *mediator*
concepts appear as hits in the mid-network **workspace band** — early and at low
vocabulary rank — not just the shared factors (diabetes, smoking), which a model
can surface by mere copying.

---

## 3. Architecture

Three roles, two models:

| Role | Model | Function |
|---|---|---|
| **Instrumented substrate** | Qwen (open-weights) + pre-fitted J-lens | White-box sensor: forward pass -> workspace-band readout of bridge concepts |
| **Controller** | Claude (capable) | Reads readout + proxy answer + target mediators; edits format, context, KB; flags required-but-missing data |
| **Evaluator** | Claude (most capable) | Produces the final structured output on the converged format; validated by task accuracy on Claude |

```
candidate input ─► Qwen + J-lens ─► workspace readout (mediator ranks, capacity)
       ▲                                        │
       │                                        ▼
   format edits ◄──── Claude controller ◄── diagnosis: which mediator is missing & why
       │
   (converged) ─► Claude evaluator ─► structured non-diagnostic output ─► accuracy on Claude
```

**Why this transfers:** what we optimize on the proxy is *structural
representability of relations* (glossing terms, co-presenting oral+systemic data,
injecting the mechanistic KB) — these work for reasons independent of Qwen. What
does **not** transfer: absolute ranks, exact token lists, tokenizer-specific
tricks. Treat proxy results as directional/ordinal; final metric is always task
accuracy measured on Claude.

---

## 3b. Agent architecture (runtime) and skill evolution

The J-lens is a **dev-time measurement instrument**, not the runtime system. In
production the work is done by a Claude orchestrator with subagents; the J-lens
(on the Qwen proxy) and the skill optimizer are **offline** tools that improve the
skills those subagents run. J-lens and agents are complementary, at different
layers — not competing.

### Runtime subagents (production pipeline)

| Subagent | Function | Optimizable by |
|---|---|---|
| Orchestrator (main) | Plan, route, assemble final output | SkillOpt |
| Record Normalizer | Integrate fragmented dental+medical records (HISTORA core) -> schema; flag missing fields | J-lens (format) + SkillOpt |
| Periodontal Analyst | Staging/grading (AAP/EFP 2017), longitudinal progression | SkillOpt |
| Cardiometabolic Analyst | Non-diagnostic framing of CV risk factors | SkillOpt |
| Oral-Systemic Relational Reasoner | Core: inflammatory/metabolic/behavioral/vascular axes & mediators | **J-lens (primary)** + SkillOpt |
| Guardrail / Verifier | Non-diagnostic, no value imputation, traceability, confidence (adversarial) | **PROTECTED — never evolved** |
| Hypothesis Generator | Research hypotheses for follow-up | SkillOpt |

Dev-time (offline): **J-lens Diagnostic** (proxy readout / controller) and
**SkillOpt Optimizer** (skill.md evolution).

### Skills

`oral-systemic-analysis` (core), `record-normalization`, `periodontal-staging`,
`cardiometabolic-framing`, `oral-systemic-kb` (retrievable mediator mechanisms),
`traceability-audit`, and `non-diagnostic-guardrail`. The guardrail is a
**protected invariant**, not a trainable skill.

### Skill evolution: SkillOpt gated by J-lens

Adopt **SkillOpt** (Microsoft Research) as the skill-optimization framework:
skills as trainable parameters, optimized via rollout -> reflect -> edit -> gate
with bounded, auditable edits accepted only on held-out improvement. Compose:

```
J-lens mediator ranks (cheap, pre-output, on Qwen)  ─►  pre-filter candidate skill edits
        │  (valid only once proxy ranks predict Claude — Phase 3 transfer check)
        ▼
SkillOpt bounded edit loop  ─►  gate = Claude held-out accuracy + guardrail pass-rate
        ▼
human approval  ─►  versioned skill (rollback available)
```

**Dependency caveat:** SkillOpt optimizes skills for the model that *runs* them —
in runtime that is Claude, not Qwen. So the authoritative gate runs on Claude;
J-lens is only a cheap pre-filter, justified once transfer validity is shown.

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
- **Proxy model:** **start with Qwen3.5-4B** (fits a free Colab T4 16 GB / L4 24 GB;
  `apply()` is a forward pass in `no_grad`, memory ~= weights ~8 GB). Scale to
  Qwen3.6-27B (~54 GB bf16 -> A100 80 GB / H100) to revalidate key findings; 4B may
  be too weak to represent some relations -> possible false negatives. Do not
  quantize the 27B: the lens was fit in bf16 and quantization degrades the readout.
  Pre-fitted lenses on the Hub (`neuronpedia/jacobian-lens`, `qwen-n1000`) -> **no
  fitting step needed**.
- **Workspace band:** prior [0.33, 0.66] of depth, intersected with the lens's
  fitted layers; **calibrate per model** with `sweep_layers` before trusting it.
- **Bridge concepts** live in `src/bridge_concepts.py`; mediators weighted above
  shared factors.
- **Metric:** min vocabulary rank of each concept over the workspace band and the
  answer/question span; `hit@10` = rank < 10.
- **jacobian-lens repo stays unmodified**; this project only imports from it.

---

## 5. Repository layout

```
dental-analysis/
  docs/PLAN.md                 # this document (living)
  colab/
    histora_diagnostic.ipynb   # main GPU harness (run in Colab)
    walkthrough.ipynb          # copy of the jacobian-lens reference notebook
  src/
    bridge_concepts.py         # target mediator + shared concepts
    record_formats.py          # one synthetic record, three candidate formats (A/B/C)
    harness.py                 # J-lens metrics: concept_ranks, capacity, sweep_layers
  schemas/output_schema.json   # non-diagnostic structured output contract
  prompts/
    controller.md              # Claude input-optimizer prompt
    evaluator.md               # Claude final-analysis prompt
  skills/oral-systemic-analysis.md  # Claude skill: optimized format + output + guardrails
  README.md
```

---

## 6. Candidate input formats (initial)

Three formats isolate the levers we optimize (see `src/record_formats.py`):

- **A — abbreviated table**, dental-first, no term glossing. *(baseline)*
- **B — named sections + glossed terms** (e.g. "BOP = gingival inflammation
  marker"), medical-first.
- **C — narrative prose with an explicit mechanistic KB bridge** (periodontitis
  -> systemic inflammation -> CV risk via CRP).

**Hypothesis:** C >= B >> A on mediator ranks. If A already activates mediators,
the knowledge is latent and the work is recall, not format.

---

## 7. Workplan & status

### Phase 0 — Scaffolding — `DONE`
- [x] Separate `dental-analysis` project; `jacobian-lens` left intact.
- [x] Bridge concepts, three record formats, harness metrics (compile + load verified).
- [x] Output schema, controller/evaluator prompts, Claude skill.
- [x] Colab diagnostic notebook (valid JSON, self-contained).
- [x] This plan.

### Phase 1 — Proxy diagnostic (Colab, GPU) — `IN PROGRESS`
- [ ] Run `histora_diagnostic.ipynb` on Qwen3.6-27B (fallback 4B).
- [ ] Calibrate the workspace band (cell 4 sweep) and lock [lo, hi].
- [ ] Record mediator ranks for A/B/C + capacity numbers → Progress Log.
- [ ] Prune multi-token / unmeasurable concept surfaces; expand surface lists.
- [ ] Confirm or revise the C >= B >> A hypothesis.

### Phase 2 — Controller loop — `TODO`
- [ ] Feed readouts to Claude via `prompts/controller.md`.
- [ ] Apply format/KB edits; re-measure; iterate until all mediators hit@10.
- [ ] Log which edits moved which mediators (the reusable findings).

### Phase 3 — Evaluator + transfer validation — `TODO`
- [ ] Claude evaluator produces structured output on converged format (real-ish cases).
- [ ] Behavioral transfer check: does the proxy's A/B/C ranking predict Claude's
      relational reasoning quality? (list intermediate mechanisms via API).
- [ ] Task-accuracy A/B: converged vs naive format, measured on Claude.

### Phase 4 — Demo & narrative — `TODO`
- [ ] End-to-end story: HISTORA data layer + interpretability-guided optimization
      + Claude closing the loop.
- [ ] Slice-viewer visuals for the winning vs naive format.
- [ ] Guardrail walkthrough (non-diagnostic, collection-not-imputation).

---

## 8. Metrics we track

- **Mediator hit@10 count** per format (primary proxy signal).
- **Mediator rank vector** (sorted) per format.
- **Capacity:** reachable data items / measured, per format.
- **Band location** (calibrated layer range).
- **Claude task accuracy** (final, authoritative) and **mechanism-recall** on the
  behavioral transfer check.

---

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Multi-token mediators (atherosclerosis, hs-CRP, endothelial) unmeasurable | Alt single-token surfaces; else measure first token, documented as approximation |
| Band mis-located | `sweep_layers` calibration before scoring |
| Proxy too weak (no format helps) | Calibrate case difficulty to the 27B; use mid-difficulty cases |
| Goodhart (optimizing proxy ranks, not clinical quality) | Ranks are hypothesis-generators; Claude accuracy is the objective |
| J-space captures only verbalizable (<10% variance) | Task accuracy stays primary; lens is diagnostic, not target |
| Non-diagnostic drift | Schema forbids value imputation; guardrails in skill + evaluator prompt |

---

## 10. Open questions

- Exact workspace band for Qwen3.6-27B?
- Which mediators are single-token in Qwen's vocabulary?
- Does the mechanistic KB (format C) actually raise mediator ranks, or is it redundant?
- Does the proxy format ranking predict Claude's behavior (transfer validity)?
- Best real (de-identified) case sources via HISTORA for Phase 3?

---

## Decisions

- **2026-07-07** — Use a separate `dental-analysis` project; do not modify
  `jacobian-lens` (copy walkthrough rather than move).
- **2026-07-07** — All code, artifacts, prompts, and skills in English.
- **2026-07-07** — Non-diagnostic scope is a hard constraint: collection flags,
  never patient-value imputation.
- **2026-07-07** — Use pre-fitted Hub lenses (no fitting) to start; GPU via Colab.
- **2026-07-07** — **J-lens is complementary to Claude agents, not a substitute:**
  dev-time white-box instrument on a proxy vs. runtime production system. Adopt a
  Claude orchestrator + subagents for runtime (see §3b).
- **2026-07-07** — **Adopt SkillOpt for skill evolution, gated by J-lens.** J-lens
  mediator ranks are a cheap pre-filter; the authoritative gate is Claude held-out
  accuracy + guardrail pass-rate. Guardrails are protected invariants, never
  evolved. Lightweight fallback: replicate the loop on the Claude Agent SDK.
- **2026-07-07** — **Colab execution: self-contained notebook.** The notebook
  clones `jacobian-lens` and recreates the `src/` modules via `%%writefile`
  (embedded, verified identical to `src/`). No private GitHub clone / token, no
  manual upload. Google Drive mount documented as the alternative for heavy
  iteration (replace section 2 with `drive.mount` + `sys.path.append`).

---

## Progress Log

- **2026-07-07 — Phase 0 complete.** Scaffolding, harness, schema, prompts, skill,
  and Colab notebook created and verified (modules compile/load; notebook + schema
  valid JSON). Awaiting first Colab run of `histora_diagnostic.ipynb`.
- **(next)** — Phase 1 results: paste mediator ranks for A/B/C, capacity, and the
  band-calibration sweep here to continue development.
