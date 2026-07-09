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
  protein interaction networks). → **Secondary / differentiator** via our dual-lens
  correlation finding (which does NOT require the Gladstone datasets).

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
non-diagnostic oral-systemic research agent. The differentiator is method: instead
of prompt-engineering the input blind, we use **interpretability** to verify the
input actually makes the oral-systemic *mediating* concepts representable — a fast
self-report probe on Claude itself, ground-truthed by the measured Jacobian lens on
an open proxy — and we let Claude close the loop and autonomously evolve the skills
behind a validation + guardrail gate. The reproducible correlation between Claude's
self-report and the measured J-space is our Research-track finding.

## Why this wins with these judges

- **On-theme for Anthropic:** built on Claude Code + Claude Science, and uses the
  July-2026 global-workspace/J-lens research directly.
- **On-theme for Gladstone:** rigorous, reproducible methodology and a real
  clinical-research user; non-diagnostic and evidence-traceable.
- **Dual deliverable:** working software (Build) + a reproducible finding (Research).
- **Responsible:** non-diagnostic guardrail as a protected invariant; self-report
  never presented as measurement or clinical evidence.

## One-week plan (Jul 7 → Jul 13)

| Day | Focus | Deliverable |
|---|---|---|
| Tue Jul 7 | Kickoff; scaffolding (done); named user + scope lock | Repo + PLAN + strategy |
| Wed Jul 8 | Fast inner loop on Claude: `claude-workspace-probe` over 3 formats; synthetic cases | Surfaced-mediator logs per format |
| Thu Jul 9 | Measured J-lens on Qwen-4B (Colab); band calibration; ranks per format | `docs/PLAN.md` progress log with ranks |
| Fri Jul 10 | Dual-lens correlation experiment (probe vs measured) | `docs/DUAL_LENS.md` results section |
| Sat Jul 11 | Runtime agent end-to-end (orchestrator + subagents) on real-ish records; guardrail gate | Working Claude Code agent + structured outputs |
| Sun Jul 12 | SkillOpt-style skill evolution on 1–2 skills, gated; accuracy A/B (optimized vs naive) | Evolved skills + A/B numbers |
| Mon Jul 13 | Demo, writeup, submission | Video/demo + README + finding |

Scope discipline: if GPU time slips, the Claude probe alone carries the inner loop
and the demo; the measured lens becomes a post-hoc validation, not a blocker.

## Deliverables checklist

- [ ] Working Claude Code agent: raw dental+medical record → structured, traceable,
      non-diagnostic oral-systemic output (schema-valid).
- [ ] Dual-lens loop demo: watch a mediator surface when a format/KB edit is applied
      (probe on Claude), corroborated by measured J-lens ranks on Qwen.
- [ ] Correlation finding (probe vs measured) with a reproducible notebook.
- [ ] Accuracy A/B: interpretability-optimized input vs naive input, on Claude.
- [ ] Guardrail suite passing (non-diagnostic, no imputation, traceability).
- [ ] Short writeup + demo video.

## Demo script (5 minutes)

1. Show a fragmented dental+medical record and the naive input → Claude misses the
   inflammatory link; probe shows "inflammation/CRP" absent.
2. **The Observer drives the edit live.** The separate Lens Observer (Opus) reads the
   primary's inferred-lens readout, returns a deficiency map (mediators absent, hs-CRP
   missing, axis derivation skipped), and injects the T0 fixes (gloss BOP, add hs-CRP
   as MISSING, attach the mechanistic KB) from the Session Working-Consciousness
   ledger → next turn the probe surfaces the mediators. Show the ledger consolidating
   the lesson across turns (`.session/example_case01.md`).
3. Full agent emits the structured non-diagnostic output with traceable axes and a
   collection flag for hs-CRP.
4. **Harness evolution beat:** the Observer decides a deterministic relation belongs in
   code → `src/relational_signals.py` computes the structural signals, tests pass, the
   value is injected, and the readout improves. Then one gated T1 skill-evolution step
   improves accuracy without breaking the guardrail.
5. Close on the correlation finding **and the unlock**: same loop, measured lens if
   exposed (see README).

## Risks specific to the week

- **GPU/time:** mitigated by the Claude-first inner loop (no GPU).
- **Self-report faithfulness:** framed as a diagnostic aid; the measured lens and
  Claude accuracy are the authorities.
- **Scope creep:** Build track is primary; the Research finding is a bounded
  add-on, not a second project.
- **Non-diagnostic discipline:** protected guardrail + synthetic/de-identified data
  only.
