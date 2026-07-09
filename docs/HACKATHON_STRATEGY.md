# Hackathon Strategy — Built with Claude: Life Sciences

**Event:** Built with Claude: Life Sciences (Anthropic × Cerebral Valley ×
Gladstone Institutes). Fully virtual, 2026-07-07 12:00 PM EDT → 2026-07-13 9:00 PM
EDT. Team size max 2. ~500 selected participants.

**Resources per participant:** 1 month Claude Max 20x + $200 API credits.
**Prize:** compete for $100k in Claude API/usage credits.
**Judges:** Anthropic + Gladstone Institutes.
**Tooling emphasis:** Claude Science (AI research workbench: literature, data,
code, compute) and Claude Code.

## Tracks and where we play

- **Build track** — "build beyond the bench: start from a user you can name (a
  scientist, a clinic, a biotech) and use Claude Code to create the tool they're
  missing, working software that outlasts the week." → **Our primary track.**
- **Research track** — "build from the bench: a discrete finding, a trained model,
  an analysis others can reproduce," with partnered Gladstone datasets
  (Marson/Pritchard T-cell Perturb-seq; Pollard MPRA DNA regulatory model; Krogan
  protein interaction networks). → Not our track; our differentiator is the
  **method** and a concrete **API-feature proposal** to Anthropic (below), neither
  of which requires the Gladstone datasets.

**Note on datasets:** the Gladstone datasets are for the Research track and are not
our clinical domain. The Build track explicitly lets us bring our own named user
and data, so HISTORA oral-systemic is valid without them.

## Named user (Build track requirement)

A **periodontist / oral-medicine researcher (or a perio-cardio research clinic)**
who has fragmented dental and medical records and wants to surface oral-systemic
(periodontal ↔ cardiovascular) research patterns and hypotheses — non-diagnostically
— that today require manual cross-referencing across siloed systems. HISTORA is the
data layer; our agent is the missing tool.

## The pitch (one paragraph)

HISTORA integrates fragmented dental + medical records; on top of it we build a
non-diagnostic oral-systemic research agent. What we submit is an **honest, tested
apparatus** and a **rigorous negative-with-nuance**, not a claimed win. The apparatus
is real: an inferred-lens Observer loop, five-surface evolution, a Session
Working-Consciousness ledger, and a guardrail-protected gate — Claude-only, 44 tests
green, run live on real NHANES. The finding is honest: the workspace self-report
signal is **genuinely non-redundant** with the output, but **no actuator we built
converts it into an outcome gain** over a strong blind baseline on this largely
re-derivable task. The one clean, repeated win — reliable missing-data flagging
(0.00 → 1.00, 6/6) — belongs to a **deterministic directive, not the lens**. That
honest result directly motivates the strongest *forward* ask: a concrete API feature
to Anthropic — **expose the real (measured) Jacobian lens on Claude** — so the same
loop swaps the inferred signal for a measured one with no architectural change, and
the project is the consumer already built for it.

## Why this wins with these judges

- **On-theme for Anthropic:** built on Claude Code + Claude Science, engages the
  July-2026 global-workspace/J-lens research indirectly on Claude, and closes with a
  concrete, humble API-feature proposal (expose the real Jacobian lens on Claude).
- **On-theme for Gladstone:** a rigorous method and a real clinical-research user;
  non-diagnostic and evidence-traceable.
- **Credible because it is honest:** working software (Build) — a tested apparatus,
  Claude-only, 44 tests green, run live on real NHANES — plus a **rigorous
  negative-with-nuance**: a real, non-redundant workspace signal with **no
  demonstrated payoff** over a strong blind baseline. A believable negative beats an
  overclaimed win, and it is exactly what motivates the measured-lens API ask.
- **The one clean win is named honestly:** reliable missing-data flagging (guardrail
  0.00 → 1.00, 6/6) — and it belongs to a **deterministic directive, not the lens**.
- **Responsible:** non-diagnostic guardrail as a protected invariant; the inferred
  lens is never presented as a measurement or clinical evidence.

## One-week plan (Jul 7 → Jul 13)

| Day | Focus | Deliverable |
|---|---|---|
| Tue Jul 7 | Kickoff; scaffolding (done); named user + scope lock | Repo + PLAN + strategy |
| Wed Jul 8 | Inferred-lens inner loop on Claude: `claude-workspace-probe` over the formats; synthetic + NHANES-grounded cases | Surfaced-mediator logs per format |
| Thu Jul 9 | Lens Observer loop (Opus) over formats; deficiency maps + T0 fixes; Session Working-Consciousness ledger | `.session/` ledger + `docs/PLAN.md` progress log |
| Fri Jul 10 | Counterfactual-sensitivity corroboration on Claude; harness evolution (`src/relational_signals.py` + tests) | Corroboration results + passing tests |
| Sat Jul 11 | Runtime agent end-to-end (orchestrator + subagents) on real-ish records; guardrail gate | Working Claude Code agent + structured outputs |
| Sun Jul 12 | SkillOpt-style skill evolution on 1–2 skills, gated (T1); accuracy A/B (Observer-converged vs naive, on Claude) | Evolved skills + A/B numbers |
| Mon Jul 13 | Demo, writeup, submission | Video/demo + README + API-feature proposal |

Scope discipline: everything runs on Claude only — no external compute — so the
inner loop and the demo never wait on anything but Claude.

## Deliverables checklist

- [ ] Working Claude Code agent: raw dental+medical record → structured, traceable,
      non-diagnostic oral-systemic output (schema-valid).
- [ ] Inferred-lens Observer loop demo: watch a mediator surface when the Lens
      Observer (Opus) diagnoses a deficiency and injects a format/KB edit on Claude.
- [ ] Counterfactual-sensitivity corroboration on Claude (flip one factor; the
      dependent axis moves, unrelated axes stay put).
- [ ] Harness evolution: `src/relational_signals.py` computes deterministic
      structural signals, injected into the input; tests pass.
- [ ] Accuracy A/B: Observer-converged input vs naive input, on Claude.
- [ ] Guardrail suite passing (non-diagnostic, no imputation, traceability).
- [ ] Short writeup + demo video + the API-feature proposal (expose the real
      Jacobian lens on Claude).

## Demo script (5 minutes)

1. Show a fragmented dental+medical record and the naive input → Claude misses the
   inflammatory link; the inferred-lens readout shows "inflammation/CRP" absent.
2. **Here is the apparatus, and here is the honest result.** Show the separate Lens
   Observer (Opus) reading the primary's inferred-lens readout, returning a deficiency
   map, and injecting T0 fixes from the Session Working-Consciousness ledger — the loop
   is real and it runs. Then state the honest outcome plainly: the workspace signal is
   **non-redundant** with the output, but the lens-driven contribution over a blind
   baseline was **not demonstrated** (`lens_inconclusive`). No claimed mediator-surfacing
   win. Show the ledger consolidating across turns (`.session/example_case01.md`).
3. Full agent emits the structured non-diagnostic output with traceable axes and a
   collection flag for hs-CRP.
4. **The one clean, deterministic win.** The **deterministic missing-data directive**
   flags absent required fields reliably — guardrail **0.00 → 1.00 (6/6)**. Name it
   honestly: this win belongs to a deterministic directive, **not the lens**. Show
   `src/relational_signals.py` computing the structural signals, tests passing (44
   green), and the value injected behind the guardrail gate.
5. **Corroboration + close on the unlock:** run the counterfactual-sensitivity check
   on Claude (flip one factor; the dependent axis moves, unrelated axes stay put) to
   show the readout is not confabulation. Close on the **API-feature proposal** — the
   honest negative-with-nuance is exactly what motivates it: we ask Anthropic to expose
   the real (measured) Jacobian lens on Claude, so the same loop swaps the inferred
   signal for a measured one with no architectural change (see README).

## Risks specific to the week

- **Self-report faithfulness:** the inferred lens is framed as a readout channel, not
  a measurement; the counterfactual-sensitivity test and Claude accuracy are the
  authorities.
- **Scope creep:** Build track is primary; the API-feature proposal is a bounded,
  speculative add-on, not a second project.
- **Non-diagnostic discipline:** protected guardrail + synthetic/de-identified data
  only.
