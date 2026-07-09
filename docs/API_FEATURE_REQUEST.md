# Feature request to Anthropic: expose the Jacobian lens on Claude via the API

> Phase R6 next-step #1. A concrete, evidence-motivated ask. The one route that removes the
> access/inference layer our whole investigation is bottlenecked on. See
> [`RESEARCH_SUMMARY.md`](RESEARCH_SUMMARY.md), [`APPROACH.md`](APPROACH.md) §8,
> [`analysis/lens-non-redundancy-burden-of-proof.md`](analysis/lens-non-redundancy-burden-of-proof.md).

## The ask
A read API that returns, for a given request, the **Jacobian-lens readout of Claude's workspace** —
the ranked single-token J-space contents per layer/position, as in the paper's open implementation —
so an external system can consume the model's *measured* workspace, not a self-report of it.

Minimal shape (illustrative): given a completion, return `workspace: [{layer, position, tokens:
[{token, rank}]}]`, optionally filtered to a concept set. Even a coarse, opt-in, latency-tolerant
version would be transformative for the use below.

## Why (evidence, not hype)
Our project is a **consumer built and waiting for this signal.** We ran the loop on Claude with three
*stand-ins* for the measured lens and found, consistently:
1. The workspace signal is **real and non-redundant with the output** — an uncommitted read of it
   points *off* the output plane (clearest proof: it flags inconsistencies in the output's *own*
   reasoning, which the output cannot self-report). Vindicated at the signal level
   (`lens-non-redundancy-burden-of-proof.md`).
2. But every *stand-in* is under-powered for **optimization**: self-report is uncorroborated
   (`is-the-lens-working.md`); the measured lens on a **Qwen proxy** has a transfer gap and a
   single-token limit that makes it *blinder* than verbal self-report on multi-token mediators
   (`measured-qwen-lens-contradiction-and-colab.md`); a model *predicting* Claude's workspace is not
   circular but is not behaviorally useful through our actuators
   (`gate-behavioral-and-opus-result.md`).

The common cause is **access**: on Claude we can only *infer* the workspace, never *measure* it. A
measured readout removes the inference/rationalization/variance layer in one step — turning a
directional, uncorroborated hint into causal ground truth, and enabling the paper's
representation-swap interventions.

## The consumer seam (no architecture change needed)
The loop is already built to a lens-readout interface, so swapping inferred → measured is a
signal-source change, not a redesign:
- `schemas/lens_readout_schema.json` — the readout contract the Observer consumes today (self-report).
  A measured readout populates the same `concepts` / `sweep` fields (with real ranks instead of
  qualitative salience).
- `agents/lens-observer.md` / `prompts/observer.md` — the Observer analyzes that readout; unchanged.
- `agents/claude-workspace-probe.md` — the current (inferred) readout source; a measured-lens API
  call would be a drop-in alternative source.
- The honesty caveats (`APPROACH.md` §8) flip from "self-report, not a measurement" to "measured" —
  the only place the wording changes.

## What we'd do the day it exists
Re-run the lens-isolation ablation and the targeted-actuator experiment
(`RESEARCH_SUMMARY.md` §4 #2) with the *measured* signal in place of the inferred one, on a
non-obvious-gap task at n≥30, and report whether `marginal(measured-lens)` clears zero — the clean
test our stand-ins could not power. The apparatus is built and tested; only the signal is missing.

## Safety framing
Read-only, opt-in, non-diagnostic use. The measured readout would strengthen — not weaken — the
protected guardrail: it makes "did the model actually represent this mediator / notice this
inconsistency" checkable rather than inferred, which is exactly the monitoring use the paper
demonstrates (catching fabrication, evaluation-awareness, silent errors).
