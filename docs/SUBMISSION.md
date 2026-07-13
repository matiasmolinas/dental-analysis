# Submission — builder track ("Build Beyond the Bench")

Working sheet for the Stage-1 async submission: a **≤3-minute demo video**, this **open-source repo**, and a
**100–200 word written summary**. Judges evaluate independently, offline, on standardized criteria — the
video must self-contain the argument (on-screen captions; numbers stay on screen; end on a verifiable
repo/license card).

**The named user:** a clinical / translational researcher and their lab — the person who arrives with a
hypothesis and faces weeks of chart review before a testable cohort exists.

**The one line that keeps us in the builder track (say it in the video and the summary):**

> *"This isn't a study about IL-6 — it's the tool a researcher uses to build the study. IL-6 is just the
> payload we loaded to prove the instrument works. Tomorrow it's a different hypothesis."*

**THE PROMISE** — stated at 0:15, proven at 2:35:

> *"A working tool that takes a researcher from a hypothesis to a research-ready cohort and a self-audited,
> falsifiable, non-diagnostic research line — in minutes, on real public data, with no one from our team in
> the room."*

---

## Demo shot list — 180s exact

| Beat | Time | On screen / capture | Voiceover (self-contained) | Builder-track element |
|---|---|---|---|---|
| **0 · Problem + promise** | 0:00–0:20 (20s) | Text-only cold open: "Testing one hypothesis = **weeks** of chart review." → the promise card. | "A clinical researcher has a hypothesis. Between them and a testable cohort: weeks of chart review — and often the data isn't even there. We built the tool that fixes this. **[read THE PROMISE]**" | Names **the user**; frames a **tool**, not a finding. |
| **1 · How it was built** | 0:20–0:40 (20s) | Capture **01** (human directs → Claude updates engine, runs). Flash `tests/` passing + the Apache `LICENSE`. | "HISTORA was built with **Claude Code** — an autonomous agent under human direction: it wrote the engine, the tests, and the guardrail. Pinned, reproducible, Apache-licensed. Built to outlast the week." | **Claude Code = builder**; supervised loop; "outlast the week." |
| **2 · The copilot delivers** | 0:40–1:15 (35s) | `fig_cohort_funnel.png` (20,905→442) + integrity checklist ✓/✗ + Capture **05** (4 real NHANES participants, ranges). | "The researcher asks a question — not a patient. On real public NHANES, Claude builds the eligibility funnel: 20,905 down to 442. Then the honest part — it tells you what the data **cannot** answer: a missing datum is a collection flag, **never** imputed. Population-level ranges out, never a patient value." | Reviewer-endorsed hero; **non-diagnostic by construction**. |
| **3 · Biology, grounded live** | 1:15–1:55 (40s) | Capture **02** (research line + 1P9M hexamer in Mol\*) + Capture **06** (MR replication across ancestries). | "Why is this cohort worth building? The biology — run live in **Claude Science**. One falsifiable research line: the IL-6R node is **genetically causal** for coronary disease; circulating CRP is **not**. It replicates across European and East-Asian cohorts. The Alzheimer's axis stays **exploratory** — the genetics are null and the direct trial failed. It never says treating the mouth prevents disease." | **Claude Science = runtime + connectors**; honesty / scope discipline. |
| **4 · It audits itself (climax)** | 1:55–2:35 (40s) | Capture **04** (reviewer finding + "All findings fixed") + Capture **07** (buggy +0.705 greyed/✗ beside corrected +0.553). | "Then the part that matters most. Operating its own pipeline under a **reviewer agent**, HISTORA caught a bug **in its own flagship number** — retracted +0.705, corrected to +0.553, and shipped a **regression test**. A tool that can only ever agree with itself is worthless. This one told us its headline was wrong." | **Failure-detection + human review + reviewer agent + Claude Code wrote the fix.** |
| **5 · Promise delivered + close** | 2:35–3:00 (25s) | Promise card re-shown, each clause ✓. End card: repo URL + `Apache-2.0` + `python demo/run_cohort.py`. | "Hypothesis → cohort → self-audited research line. Minutes, real data, non-diagnostic by construction — and you can clone it and run it yourself, with no one from our team in the room. That's HISTORA." | Proves **"usable without you"**; verifiable repo. |

Sum: 20 + 20 + 35 + 40 + 40 + 25 = **180s.**

- **Open on:** the researcher's pain + the promise (never IL-6 first).
- **End on:** promise-delivered + "clone and run it" repo/license card.
- **Cut entirely** (stays in the repo, not the video): SkillOpt, the benchmark table, the Stage-3 ODE gallery, any protein deep-dive beyond the single Capture 02 shot.

Captures live in [`assets/claude-science/`](assets/claude-science/) (01, 02, 04, 05, 06, 07) and
[`assets/figures/fig_cohort_funnel.png`](assets/figures/fig_cohort_funnel.png).

---

## Written summary (100–200 words) — submission-ready (~170)

> **HISTORA — the tool a clinical researcher is missing.** Today, testing a hypothesis like *"does
> periodontal inflammation share mechanisms with cardiometabolic disease?"* means weeks of chart review
> just to assemble a cohort — and often the data you need isn't there. Built with **Claude Code**, HISTORA
> turns a fragmented public corpus (NHANES) into a research-ready cohort in seconds: it builds an
> eligibility funnel (20,905 → 442), flags every missing datum as a collection gap it **never imputes**,
> generates a falsifiable, uncertainty-quantified hypothesis grounded in genetics it runs **live** (IL-6R →
> coronary disease causal; circulating CRP null; Alzheimer's strictly exploratory), and exports a
> preliminary protocol. Everything is population-level and **non-diagnostic by construction**. Operating its
> own pipeline in **Claude Science** under a reviewer agent, HISTORA caught and fixed a bug in its own
> flagship number — retracting +0.705 for +0.553, with a regression test. It's reproducible, tested,
> Apache-licensed software a lab can run without us in the room. IL-6 is today's payload; the instrument is
> reusable.

---

## What the submission must nail (async, standardized criteria)

1. **"Working software a named user runs without you"** — unmistakable in all three surfaces: the repo runs
   deterministically offline (README quickstart + passing `tests/`), the video's end card shows the exact
   command, the summary says "run it without us in the room."
2. **The self-correction / honesty story** as the differentiator — the video's climax (Beat 4) and a
   summary sentence; the one beat no competitor can fake. See [`SELF-CORRECTION.md`](SELF-CORRECTION.md).
3. **Repo verifiability** — an async judge *will* click in: a top-level README that leads with the user +
   copilot (not IL-6), green tests, `LICENSE` + `NOTICE`, `SELF-CORRECTION.md` linked. The repo must tell
   the same story as the video within 30 seconds of scrolling.

**Biggest single risk:** a judge mis-slots this as a researcher-track "finding about IL-6." **Fix:** the
first 20 seconds of the video and the first two sentences of the summary name **the user** and **the tool**
before any biology, and land the "instrument, not the study" line above.
