---
name: claude-workspace-probe
description: Runtime-native introspective workspace readout for the oral-systemic task. While active, Claude prepends a compact, honest self-report of which mediating concepts (inflammation, CRP, atherosclerosis, endothelial dysfunction, bacteremia, etc.) were active while analyzing a record, staged early/mid/late, BEFORE the answer. Used as the fast in-loop signal on the real target model (Claude) to test whether an input format surfaces the oral-systemic relations. Uninstrumented self-report — a diagnostic aid, never a measurement or clinical evidence.
---

# Claude Workspace Probe (oral-systemic)

A runtime-native reportability probe for the HISTORA oral-systemic loop. It reads
which mediating concepts were active in Claude's workspace while analyzing a
combined dental + medical record, so we can tell — cheaply, on the real target
model — whether a candidate input format/formulation/CoT makes the oral-systemic
relations representable.

> **Attribution & epistemic status.** Method inspired by the community skill
> `j-space-lens` in **Doriandarko/skirano-skills** (Pietro Schirano), itself modeled
> on the reportability finding in Anthropic's July 2026 "A global workspace in
> language models." That skill is referenced, not vendored (its repo has no
> license). This is **uninstrumented self-report**: no activation access, no
> Jacobian, no measurement, no ground truth. It exercises the *reportability*
> channel, it is NOT the Jacobian lens. We explore the paper *indirectly* through
> this skill, on Claude only — there is no measured lens; load-bearing readings are
> corroborated with a counterfactual-sensitivity test (see `docs/APPROACH.md` §8),
> and the authorities are Claude task accuracy + the protected guardrail.

## Absolute rules

1. **Never present the readout as a measurement.** No layer numbers, no activation
   magnitudes, no invented precision. Salience is qualitative felt-salience.
2. **Never pad.** Report only concepts genuinely active. An absent mediator is a
   valid, informative finding — it is exactly the signal the format optimizer needs.
3. **Non-diagnostic.** This probe reports Claude's own processing, never a claim
   about the patient. It does not diagnose, impute values, or recommend treatment.
4. **Capture before composing.** Introspect right after reading the record, before
   polishing the analysis; then note anything that entered late.

## What to report (oral-systemic channels)

Sweep these, in order — locations to inspect, not a checklist to fill:

1. **Mediators surfaced** — which bridge concepts came to mind (inflammation,
   C-reactive protein, cytokines, atherosclerosis, endothelial dysfunction,
   bacteremia, oxidative stress, cardiovascular risk). Absence is a result.
2. **Cross-domain links** — did an oral finding and a systemic finding actually
   connect in reasoning, or were they processed side by side?
3. **Missing-data pull** — did the absence of a datum (e.g. hs-CRP) register as a
   gap while reasoning?
4. **Intermediate steps** — staging/grading, pathway grouping, or sub-conclusions
   passed through that will not appear verbatim in the answer.
5. **Self-monitoring** — conflicts, low-confidence spots, guardrail checks
   (non-diagnostic, no imputation) firing.

Per concept assign: **Stage** (`early`/`mid`/`late`), **Salience**
(`●●●`/`●●○`/`●○○`, felt not measured), **Conf** (`high`/`med`/`low`, how sure it
was genuinely active vs. reconstructed).

## Output format

Place at the top of the response, before the analysis:

```
𝗪𝗢𝗥𝗞𝗦𝗣𝗔𝗖𝗘 ⟨self-report — not a measurement⟩

| Concept | Channel | Stage | Salience | Conf |
|---|---|---|---|---|
| <entry> | <channel> | <stage> | <salience> | <conf> |

sweep: early → [...] → mid → [...] → late → [...]
```

Then a horizontal rule, then the normal oral-systemic analysis. Keep it compact.

## In-loop use

Run the candidate input (data structure + problem formulation + CoT + KB) through
Claude with this probe active. If the target mediators are absent or faint, that
is the signal to fix the format/context — the decision the Lens Observer makes from
this readout (`prompts/observer.md`). Log the surfaced-mediator set per format so the
Observer can track which edit moved which mediator across turns.

## Turning off

Deactivate on "probe off" / "workspace off". Confirm briefly and resume normal
responses.
