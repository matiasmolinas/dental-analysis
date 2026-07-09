# HISTORA Oral-Systemic Intelligence Agent — Project Plan

> **Living document.** Updated as we learn. Each experiment run appends findings to
> the [Progress Log](#progress-log) and, when a decision changes direction, to
> [Decisions](#decisions). Status tags: `TODO` / `IN PROGRESS` / `DONE` / `BLOCKED`.

**Last updated:** 2026-07-08
**Owner:** matias.molinas@gmail.com
**Context:** Built with Claude: Life Sciences (Anthropic × Cerebral Valley ×
Gladstone), 2026-07-07 → 2026-07-13. See [`HACKATHON_STRATEGY.md`](HACKATHON_STRATEGY.md).
**Method detail:** dual-lens loop — see [`DUAL_LENS.md`](DUAL_LENS.md).
**Data:** NHANES 2009–2010 (real anchor) + Synthea (longitudinal) — see [`DATASETS.md`](DATASETS.md).

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
optimization loop — rather than prompt-engineering blind. We read that workspace
with **two complementary instruments**: a fast self-report probe on Claude itself
and the measured Jacobian lens on the proxy (see §3c and `DUAL_LENS.md`).

---

## 1b. Working hypothesis (load-bearing)

Claude, by inspecting the **internal workspace of a small proxy (Qwen)** via the
J-lens — given the input **data structure**, the **problem formulation**, and the
**chain of thought** — can decide which **values to complete** (as collection
flags, never imputed), which **input formats to adjust**, and which **additional
knowledge context to inject or modify**. The optimized, complete input is then
**evaluated on the most capable Claude**, and that learning becomes the fitness
signal for **autonomous evolution of the subagents and skills** (gated). The whole
method is valid as a Claude-improvement technique only if the proxy's workspace
**predicts Claude's** relational reasoning — verified in Phase 3.

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

Dev-time / in-loop: **Claude Workspace Probe** (self-report on Claude — fast
pre-filter), **J-lens Diagnostic** (measured readout on the Qwen proxy — ground
truth), and **SkillOpt Optimizer** (skill.md evolution).

### Skills

`oral-systemic-analysis` (core), `record-normalization`, `periodontal-staging`,
`cardiometabolic-framing`, `oral-systemic-kb` (retrievable mediator mechanisms),
`traceability-audit`, `claude-workspace-probe` (runtime-native self-report), and
`non-diagnostic-guardrail`. The guardrail is a **protected invariant**, not a
trainable skill.

## 3c. Dual-lens loop (two instruments on the workspace)

Full detail in [`DUAL_LENS.md`](DUAL_LENS.md). Two instruments read the workspace
our input optimization targets — different models, different epistemics:

- **Claude Workspace Probe** (`claude-workspace-probe`): uninstrumented introspective
  self-report ON CLAUDE (the real target). Fast, zero GPU, captures CoT natively,
  runs the inner loop and sidesteps the Qwen→Claude transfer gap for optimization.
  Inspired by `Doriandarko/skirano-skills` j-space-lens; **not a measurement**.
- **Measured Jacobian lens** (`jlens-diagnostic` on Qwen): quantitative, causal,
  reproducible ground truth on a proxy.

**Inner loop (fast):** probe on Claude screens format/context/CoT edits. **Outer
validation (rigorous):** measured lens on Qwen confirms it is not confabulation.
**Correlation experiment** between the two is a reproducible Research-track finding
(agreement → self-report predicts measured J-space; disagreement → a caveat). The
authoritative gate stays Claude task accuracy + the protected guardrail.

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
  docs/
    PLAN.md                    # this document (living)
    HACKATHON_STRATEGY.md      # tracks, named user, one-week plan, demo, judging
    DUAL_LENS.md               # two-instrument methodology + correlation experiment
  colab/
    histora_diagnostic.ipynb   # measured J-lens GPU harness (run in Colab)
    walkthrough.ipynb          # copy of the jacobian-lens reference notebook
  src/
    bridge_concepts.py         # target mediator + shared concepts
    record_formats.py          # NHANES-grounded case, three candidate formats (A/B/C)
    harness.py                 # J-lens metrics: concept_ranks, capacity, sweep_layers
    nhanes_mapping.py          # schema field -> NHANES 2009-2010 file+variable codes
    nhanes_loader.py           # download XPT + build a grounded case (pandas.read_sas)
  schemas/output_schema.json   # non-diagnostic structured output contract
  prompts/
    controller.md              # Claude input-optimizer prompt
    evaluator.md               # Claude final-analysis prompt
  agents/                      # 7 runtime subagents + claude-workspace-probe + 2 offline
  skills/                      # 8 skills (guardrail protected) — see skills/README.md
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

**Hypothesis:** E >= C >= B >> A on mediator ranks; D isolates whether structure
alone (without glossing/KB) helps. If A already activates mediators, the knowledge
is latent and the work is recall, not format.

---

## 7. Workplan & status

### Phase 0 — Scaffolding — `DONE`
- [x] Separate `dental-analysis` project; `jacobian-lens` left intact.
- [x] Bridge concepts, three record formats, harness metrics (compile + load verified).
- [x] Output schema, controller/evaluator prompts, Claude skill.
- [x] Colab diagnostic notebook (valid JSON, self-contained).
- [x] This plan.
- [x] Full skill set (`skills/`): oral-systemic-analysis, record-normalization,
      periodontal-staging, cardiometabolic-framing, oral-systemic-kb,
      traceability-audit, non-diagnostic-guardrail (protected).
- [x] Full subagent set (`agents/`): orchestrator + 6 runtime specialists +
      claude-workspace-probe + jlens-diagnostic + skillopt-optimizer. Catalog READMEs.
- [x] SkillOpt cloned as sibling reference (`../SkillOpt/`).
- [x] Dual-lens methodology: `claude-workspace-probe` skill + subagent;
      `docs/DUAL_LENS.md`; `docs/HACKATHON_STRATEGY.md`.

### Phase 1a — Fast inner loop on Claude (no GPU) — `IN PROGRESS`
- [ ] Activate `claude-workspace-probe`; run the 3 formats (A/B/C) on synthetic
      cases; log the surfaced-mediator set per format.
- [ ] Iterate format/KB/CoT edits on Claude until mediators surface (fast, no GPU).
- [ ] This is the primary inner loop and the demo backbone.

### Phase 1b — Measured proxy diagnostic (Colab, GPU) — `IN PROGRESS`
- [ ] Ground cases in real data: download NHANES 2009–2010 (`src/nhanes_loader.py`),
      aggregate `OHXPER_F` per-site PPD/CAL/BOP, build grounded cases to replace the
      hand-written values in `src/record_formats.py`.
- [ ] (Optional) reproducible CRP↔periodontitis mini-analysis on 2009–2010 (Research-track).
- [ ] Run `histora_diagnostic.ipynb` on Qwen3.5-4B (scale to 27B to revalidate).
- [ ] Calibrate the workspace band (sweep) and lock [lo, hi].
- [ ] Record mediator ranks for A/B/C + capacity numbers → Progress Log.
- [ ] Prune multi-token / unmeasurable concept surfaces; expand surface lists.
- [ ] Confirm or revise the C >= B >> A hypothesis.
- [ ] **Instrument the chain of thought:** let the proxy GENERATE a reasoning trace
      and read the J-lens over the generated span (not only the static prompt tail).

### Phase 2 — Dual-lens correlation (Research-track finding) — `TODO`
- [ ] For each format, compare Signal A (probe surfaced-mediators on Claude) vs
      Signal B (measured ranks on Qwen). Spearman on the induced orderings +
      per-mediator agreement. See `docs/DUAL_LENS.md`.
- [ ] Feed readouts to Claude via `prompts/controller.md`; apply edits; re-measure
      until all mediators hit@10. Log which edits moved which mediators.

### Phase 3 — Evaluator + transfer validation — `TODO`
- [ ] Claude evaluator produces structured output on converged format (real-ish cases).
- [ ] Task-accuracy A/B: converged vs naive format, measured on Claude (authoritative).

### Phase 4 — Autonomous skill evolution (gated) — `TODO`
- [ ] SkillOpt-style loop on 1–2 trainable skills; J-lens/probe as pre-filter,
      Claude accuracy + guardrail pass-rate as the gate; human-in-the-loop promote.
- [ ] Regression suite (clinical cases + compliance) at every gate.

### Phase 5 — Demo & submission — `TODO`
- [ ] End-to-end story: HISTORA data layer + dual-lens optimization + Claude loop
      + gated evolution. Demo script in `docs/HACKATHON_STRATEGY.md`.
- [ ] Guardrail walkthrough (non-diagnostic, collection-not-imputation).
- [ ] Writeup + video; Build-track tool + Research-track correlation finding.

---

## 8. Metrics we track

- **Mediator hit@10 count** per format (primary proxy signal).
- **Mediator rank vector** (sorted) per format.
- **Capacity:** reachable data items / measured, per format.
- **Band location** (calibrated layer range).
- **Claude task accuracy** (final, authoritative) and **mechanism-recall** on the
  behavioral transfer check.
- **Counterfactual sensitivity:** flip smoking / diabetes / hs-CRP / hypertension →
  does the affected axis move coherently (and unrelated axes stay put)? The
  API-only, output-side analogue of the J-lens swap (see `DUAL_LENS.md`).

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
| Self-report confabulation (probe) | Never presented as measurement; ground-truthed by the measured lens; Claude accuracy is authority |
| GPU/time slips in the 1-week event | Claude-first inner loop carries the demo; measured lens becomes post-hoc validation, not a blocker |
| Scope creep across two tracks | Build track primary; the correlation finding is a bounded add-on, not a second project |

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
- **2026-07-08** — **Dual-lens loop adopted.** Add a runtime-native self-report
  instrument (`claude-workspace-probe`, inspired by `Doriandarko/skirano-skills`
  j-space-lens) as the fast inner loop on Claude, with the measured Jacobian lens on
  Qwen as ground-truth validation. The two are complementary (different models,
  different epistemics); their correlation is a Research-track finding. The skirano
  skill is referenced, **not vendored** (its repo has no license); we ship our own
  domain-adapted skill. Effort re-balanced: Claude-first inner loop is primary for
  the 1-week event; the measured lens is validation, not a blocker.
- **2026-07-08** — **Hackathon positioning:** Build track primary (named user =
  perio-cardio research clinic on HISTORA); Research track secondary via the
  correlation finding (does not need the Gladstone datasets). See
  `docs/HACKATHON_STRATEGY.md`.
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
  Jacobian-lens readout and drives evolution; (2) the **inferred lens is the only live
  signal** — the real Colab/Qwen lens is demoted to the documented "unlock" (offline
  correlation only); (3) a **Session Working-Consciousness** ledger is the closed
  in-session evolutionary loop; (4) evolution targets five surfaces incl. **harness
  code**. Guardrail stays protected; edits are tiered (T0 ephemeral / T1 promoted +
  human gate). R1 artifacts landed: `agents/lens-observer.md`, `prompts/observer.md`,
  `skills/lens-deficiency-analysis.md`, `schemas/lens_readout_schema.json`,
  `schemas/deficiency_map_schema.json`.

---

## Progress Log

- **2026-07-07 — Phase 0 complete.** Scaffolding, harness, schema, prompts, skills,
  subagents, and Colab notebook created and verified (modules compile/load; notebook
  + schema valid JSON).
- **2026-07-08 — Dual-lens + hackathon strategy.** Added `claude-workspace-probe`
  skill + subagent, `docs/DUAL_LENS.md`, `docs/HACKATHON_STRATEGY.md`; restructured
  phases around the dual loop (1a fast Claude probe, 1b measured Qwen lens, 2
  correlation finding, 4 gated evolution). SkillOpt cloned as sibling reference.
- **(next)** — Phase 1a/1b results: paste (A) probe surfaced-mediators per format
  and (B) measured mediator ranks + capacity + band sweep here to continue.
