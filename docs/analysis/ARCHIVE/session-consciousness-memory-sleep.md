# Lens-Based Session-Consciousness, Memory, and Offline Consolidation — A Technical Analysis

> Produced 2026-07-09 with the **Fable** model. Scope: the non-diagnostic oral-systemic
> agent in this repo — Claude only, via the **inferred** (self-report) lens, never a
> measured Jacobian lens. Claims resting on self-report are flagged as such. Companion
> to [`../APPROACH.md`](../../APPROACH.md), [`../REFORMULATION.md`](../../REFORMULATION.md).

---

## 0. Verification note (Anthropic offering)

Verified against the `claude-api` skill knowledge rather than asserted from memory. What
exists today:

- **Managed Agents (CMA)** — hosted, versioned agents + per-session sandboxes, with
  **memory stores**: workspace-scoped, cross-session persistent text documents,
  FUSE-mounted into the container, with immutable **memory versions** (audit / rollback
  / redact). Real, first-party cross-session memory.
- **Memory tool** (`memory_20250818`) — a client-side tool where Claude reads/writes a
  `/memories` directory; you own the backend. Cross-session if you persist it.
- **Context editing** (`context-management-2025-06-27`) — *clears* stale tool
  results / thinking blocks (pruning, not summarizing).
- **Compaction** (`compact-2026-01-12`) — server-side *summarization* near the window.
- **Scheduled deployments** — cron-fired sessions ("every night" is expressible here).

**Could NOT verify:** any Anthropic-native "sleep" / offline-consolidation engine that
harvests past sessions, mines recurring tasks, replays them, and consolidates behind a
held-out gate. **That is not an Anthropic feature.** The harvest→mine→replay→consolidate
engine is **SkillOpt-Sleep** (Microsoft Research; shipped 2026-07-02, `skillopt-sleep`
CLI, v0.2.0). Anthropic gives the *primitives* (memory stores for state, scheduled
deployments for the trigger; the held-out gate is your own code); the consolidation loop
itself is not managed. Below, "sleep" means **offline consolidation in general
(SkillOpt-Sleep-style)**, not an Anthropic feature.

---

## 1. How the Session Working-Consciousness (SWC) actually works

The SWC is the load-bearing novelty of the reformulation ([`../REFORMULATION.md`](../../REFORMULATION.md)
§2.5, [`../APPROACH.md`](../../APPROACH.md) §6). Its mechanism is a **two-tier memory
split** across two model instances.

**Ephemeral per-call lens (Executor).** The primary model runs with the
`claude-workspace-probe` skill active and emits, per call, an **inferred lens readout**
(`schemas/lens_readout_schema.json`): a workspace table + `sweep` line naming which
bridging mediators surfaced, at what salience/stage, which required variables
registered, and which chain-of-thought steps were covered. This is **self-report
exercised as a readout channel — not a measurement**. It is discarded when the call
ends — the primary has no cross-call memory of it.

**Persistent cross-call ledger (Observer).** A *separate* instance — the Lens Observer
(recommended Opus) — never does the task. It owns `.session/working_consciousness.md`
(git-ignored; template committed), reads it as its own context every turn, and
consolidates it after every turn. The ledger is a **curated optimization state, not a
transcript** (`skills/session-working-consciousness.md`), with five compartments:

| Compartment | What it is |
|---|---|
| **Task model** | current understanding of the case + which format/variable/KB levers have been *shown* (by lens + counterfactual) to surface which mediators |
| **Consolidated beliefs** | stable lessons promoted from ≥2 turns of evidence, a counterfactual flip, or an A/B — the in-session analogue of offline consolidation |
| **Pending hypotheses** | levers still to test |
| **Active injections** | the T0 ephemeral edits currently in force (auto-revert at session end) |
| **Turn log** | per turn: deficiencies seen → edits applied (surface+tier) → outcome |

**The turn cycle** (5 steps): **read** the SWC → **append** a turn-log entry from this
turn's deficiency map (`schemas/deficiency_map_schema.json` → `swc_update`) →
**consolidate** (promote a pending hypothesis to a belief once corroborated; drop
stale/refuted ones; keep it compact) → **decide an injection** (add a missing variable,
gloss a term, attach a KB snippet, reorder, or swap in a harness-computed value —
recorded under *Active injections* with its grounding) → **verify prior injections**
(`corroboration: reread_next_turn`; if the expected readout change didn't happen, revert
or try another surface).

**Concretely, from `.session/example_case01.md`** (a committed 3-turn ledger): Perio
III/B + HTN + T2DM with hs-CRP absent.
- **Turn 1**: shared factors surface by copying; CRP/atherosclerosis/endothelial/
  bacteremia absent; `hs_crp` never registers; `axis_derivation` skipped → deficiencies
  `missing_mediator`, `missing_variable(hs_crp)`, `uncovered_cot_step` → three **T0**
  edits (inject `hs_crp=MISSING`; attach mechanistic KB bridge; make `axis_derivation`
  explicit).
- **Turn 2**: missing-data pull now fires (CRP absent→mid); corroborated by a
  **counterfactual flip**; belief consolidated.
- **Turn 3**: CRP/inflammation/endothelial/atherosclerosis mid-strong; `axis_derivation`
  covered; bacteremia still absent → carried forward as a pending hypothesis.

That is the closed loop: **readout → typed deficiency → cheapest-surface injection →
verified outcome → consolidation → next-prompt modification.**

**Current limits (honest).** The SWC is a **markdown/JSON ledger curated by an LLM**, not
a datastore with write-time schema enforcement. Its signal is **inferred self-report,
not ground truth.** There is **no persistence across sessions** — T0 injections
auto-revert at session end and consolidated beliefs die with the session unless a human
promotes an edit to T1. So the "working consciousness" is genuinely *working*
(within-session) but genuinely *amnesiac* (across sessions).

---

## 2. Does memory add value here — and which kind?

Three distinct things get conflated under "memory." Only one is present.

**(a) Within-session working memory — already the SWC.** Present; not the gap.

**(b) Cross-session long-term memory — NOT yet present.** The real gap. Every session
rediscovers, from a cold naive-format start, that "`hs_crp=MISSING` fires the
missing-data pull" or "the mechanistic KB bridge raises CRP+endothelial from absent to
mid." Those lessons are consolidated in the ledger and then thrown away at session end.
A cross-session store would let case *N+1* **start from the levers that worked on cases
1..N**.

**(c) A tool-based memory store — the Agent SDK memory tool / CMA memory store.** The
*implementation vehicle* for (b). Context-editing/compaction are orthogonal (they manage
within-session window pressure, which the SWC's "state not history" rule already targets
by hand).

**What cross-session memory buys this project.** A persisted **lever→mediator ledger**:
"for cases matching {perio stage, comorbidity set, which datum is absent}, lever X
surfaced mediator Y, corroborated by {counterfactual | A/B}, confidence Z." Across
accumulating cases + the live A/B logs (`results/ab_live_report.json`), this turns the
Observer from a per-session optimizer into one that *transfers* — the same claim the
project already makes for the method being domain-general.

**The risk, and the guardrail tie-in.** Non-diagnostic health context: the SWC **never
stores a patient-specific imputed value** — only collection flags and
format/variable/processing lessons (`skills/non-diagnostic-guardrail.md` invariant #2).
Cross-session memory *multiplies* this risk: a store that accidentally captured
"hs-CRP ≈ 4.2 for a perio-III patient" would be an imputed value replayed into every
future session — the guardrail's failure mode, now durable and cross-patient. Verified
redaction (memory versions → redact) is a mitigation, not a license.

**Recommended bounded design.**
- **File:** `.knowledge/lever_ledger.jsonl` (committed — this is *learned* state, not
  ephemeral session state).
- **Store ONLY:** `case_signature` (structural — perio stage band, comorbidity set,
  which mediator *datum is flagged absent*; **no values**), `surface` (one of the five),
  `lever`, `mediator_moved`, `corroboration` (`counterfactual_flip | ab_on_claude |
  repeated_turns≥2`), `confidence`, `guardrail_pass`, `provenance` (session id + turn).
- **Do NOT store:** any numeric/imputed patient value; anything under
  `required_missing_data` beyond the flag itself; the guardrail skill or edits to it.
- **Write gate:** only when it already passed the SWC consolidation rule *and*
  `guardrail_pass = true`. At read time, reuse still re-runs the guardrail on the
  produced output — memory proposes, the guardrail disposes.
- **Substrate:** start with a committed JSONL (transparent, diffable, matches the
  markdown-ledger ethos). Move to a CMA memory store (versioning + redact) only if the
  runtime moves onto Managed Agents.

---

## 3. Does a sleep / offline-consolidation mechanism add value?

**Mapping SkillOpt-Sleep onto this project's T0→T1 promotion** — structurally the same
discipline (the project names SkillOpt as the ancestor of its T1 tier):

| SkillOpt-Sleep stage | This project's analogue |
|---|---|
| **harvest** past sessions | collect accumulated SWC ledgers + `results/ab_live_report.json` + deficiency maps |
| **mine** recurring tasks | cluster recurring deficiencies ("IL-6 always absent in NHANES," "hs-CRP inconsistently flagged" — the R5→R6 open item) |
| **replay** offline | re-run the executor on held-back cases with candidate promoted edits (`ab_eval.run_ab`) |
| **consolidate behind a held-out gate** | the T1 gate: strict held-out accuracy gain AND no drop in guardrail pass-rate AND tests pass AND human approval |

**Would a nightly offline pass help beyond in-session T0?** Yes, along the axis the live
results say is weak. The R5 A/B found B (converged input) strictly beats A, **but on
real NHANES cases B is only 1/3 guardrail-compliant (0.33)**, so the gate correctly
refuses promotion. In-session T0 edits can't fix that — they auto-revert and never
accumulate the cross-case evidence needed to make missing-mediator flagging *reliable*.
An offline pass can: it has the whole corpus to mine the systematic failure, the budget
to replay at larger n, and the held-out gate to promote only what survives. **Nothing
new needs inventing** — the T1 gate already *is* the SkillOpt held-out gate; the offline
pass is the missing scheduler + harvester around it. Trigger via a CMA scheduled
deployment (verified primitive), not an invented Anthropic "sleep" feature.

---

## 4. KEY QUESTION — does lens-based session-consciousness help *during* sleep?

**Claim: yes — the inferred-lens readouts + deficiency history are a materially better
training signal for offline consolidation than raw transcripts + right/wrong outcomes —
conditional on corroboration.**

**Mechanism.** Consolidating over raw transcripts + outcomes gives a **scalar,
credit-assignment-blind** signal: "case 47 scored 0.6." The optimizer must *infer* which
of many things in the prompt package caused the miss — a high-variance search over five
surfaces. The SWC instead carries a **localized, typed, pre-attributed** signal: not
"wrong" but *"`missing_mediator(endothelial)` — absent under naive format — fixed by the
mechanistic KB bridge — corroborated by reread at Turn 3."* That is a labeled
(deficiency_type, surface, lever, outcome) tuple. Offline, it collapses credit
assignment: recurring `missing_variable(hs_crp)` points at an
`injected_variables`/`harness_code` fix; recurring `uncovered_cot_step(axis_derivation)`
points at a `subagent_def` fix. In ML terms, the lens turns a **sparse scalar reward**
into a **dense, factored, causal-ish gradient** over the five surfaces.

**Expected benefit.** Faster convergence and — more important here — **better-targeted,
guardrail-safe edits.** The R5 finding (B's weakness is *missing-data flagging*, not
mechanism recall, on real cases) is exactly the localization the deficiency history
hands the optimizer for free; a transcript-only pass would see "guardrail fails
sometimes" and have to rediscover it.

**Honest caveats (must not be overclaimed).**
1. **Self-report is not ground truth.** A deficiency label is the Observer's *reading* of
   the primary's *self-report* — two layers of inference. Consolidating on it risks
   **baking a confabulated lens signal into a persistent edit** — a durable Goodhart,
   worse than a transient one because it ships.
2. **The mitigation is already in the architecture.** The final authority is Claude task
   accuracy + the protected guardrail, never the readout score. Two filters neutralize a
   confabulated signal before it can consolidate: (a) **counterfactual-sensitivity**
   corroboration (an API-observable behavioral test on Claude, not self-report) — the
   SWC consolidation rule already requires it (or an A/B, or ≥2-turn repetition) before a
   belief is promoted; (b) the **held-out gate + guardrail Pareto rule** — even a
   corroborated lever must strictly improve held-out accuracy with no drop in guardrail
   pass-rate.
3. **Net (no overclaim).** The lens history makes offline consolidation *more efficient
   and better-localized*, **conditional on** counterfactual corroboration + the
   accuracy/guardrail gate. Absent corroboration it is a plausible-but-unverified hint.
   The strongest version — that a *measured* lens would make the consolidation signal
   decisive — is exactly the API feature proposed to Anthropic (§8), and stays
   speculative until such a lens exists.

---

## 5. Concrete recommendations & next steps (prioritized)

Tags: **[SWC] / [memory] / [sleep-consolidation] / [guardrail]**; **(T0)** cheap/in-session,
**(T1)** gated + human-approved.

**Build first (unblocks R5→R6):**
1. **[memory] (T1)** Add the bounded cross-session `.knowledge/lever_ledger.jsonl` (§2) —
   structural case-signatures + lever→mediator + corroboration + guardrail_pass, **no
   patient values.** Converts the per-session Observer into a transferring one and is the
   input the offline pass needs. Gate its *write* on the consolidation+guardrail rule.
2. **[sleep-consolidation] (T1)** Stand up the nightly offline pass:
   harvest(SWC + `ab_live_report.json` + deficiency maps) → mine(recurring deficiencies)
   → replay(`ab_eval.run_ab` on held-back cases) → gate(existing T1). Fire via a
   scheduled deployment — not an Anthropic "sleep" feature. *This is where the R5
   guardrail-reliability problem (B at 0.33) actually gets fixed.*
3. **[guardrail] (T0→gate)** Make deficiency-history the offline pass's primary signal,
   but the mine step consumes only *consolidated* (already-corroborated) beliefs, never
   raw pending hypotheses — the guard against consolidating a confabulated signal.

**Next:**
4. **[sleep-consolidation] (T1)** Attack the R5 open item the deficiency history surfaces
   first: IL-6 always absent / hs-CRP inconsistently flagged in NHANES → route to
   `harness_code` (extend `src/relational_signals.py` / `nhanes_mapping.py` flagging),
   test-before-use, inject, re-check; re-run A/B at larger n. The concrete path to
   lifting B's guardrail pass-rate toward 1.0.
5. **[SWC] (T0)** Adopt context-editing/compaction to automate the "keep it compact"
   rule if the ledger grows. Low priority.
6. **[memory] (T1, later)** If the runtime moves onto Managed Agents, migrate the ledger
   to a CMA memory store for versioning + redact.

**Do not build:** anything that persists numeric/imputed patient values (violates the
guardrail); any offline edit touching `skills/non-diagnostic-guardrail.md` (protected);
any consolidation promoting on readout score rather than Claude accuracy + guardrail
(anti-Goodhart).
