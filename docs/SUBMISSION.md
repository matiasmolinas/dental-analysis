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

**THE PROMISE** — stated up front, proven at the close:

> *"A working tool that takes a researcher from a hypothesis to a research-ready cohort and a self-audited,
> falsifiable, non-diagnostic research line — in minutes, on real public data, with no one from our team in
> the room."*

---

## Delivered video — [`assets/HISTORA-demo.mp4`](assets/HISTORA-demo.mp4)

**Narrated** (real avatar, small top-right corner) + voice + burned-in captions, **1920×1080, AAC audio,
~2:06 (125.9s)** — under the 3-min cap. The table below is the **storyboard** the narrated cut follows
(timings approximate — the narrated cut is tighter than the original 12-beat muted reference). The muted cut
and voice-over kit are the alternatives, in [`assets/heygen/`](assets/heygen/).

| # | ~Time | On-screen slide | Caption (verbatim) | Builder-track element |
|---|---|---|---|---|
| 0 | 0:00 (11s) | Text — **the problem · why it matters** | "The mouth is a cheap, modifiable window into the inflammation behind **heart disease and diabetes**. But testing that link means **weeks** of chart review — and often the data was never collected." | Names the pain **+ the global stakes** |
| 1 | 0:10 (10s) | Text — **the promise** | "A tool that takes a researcher from a hypothesis to a **research-ready cohort** and a self-audited, falsifiable, **non-diagnostic** research line — in minutes, on real public data, with no one from our team in the room." | Frames a **tool** |
| 2 | 0:20 (16s) | Capture **01** + chips | "Built with **Claude Code** — under my direction it wrote the engine, the tests, and the guardrail, then **operated Claude Science** to run and check the science." | **Claude Code = builder** |
| **2b** | **0:36 (14s)** | **The build-loop diagram** | "A **supervised autonomous loop**: I direct; Claude Code drives Claude Science through the **Chrome extension**, as the scientist — and it **evolves and corrects itself**." | **The dev process: Claude Code ⇄ Claude Science via Claude for Chrome; supervised loop; evolution + correction** |
| 3 | 0:50 (18s) | `fig_cohort_funnel` | "A **research-ready cohort** in seconds: the eligibility funnel, **20,905 → 442**." | Reviewer-endorsed hero |
| 4 | 1:08 (17s) | Capture **05** | "It tells you what the data **cannot** answer. A missing datum is a collection flag — **never imputed**. Population-level ranges out, never a patient value." | **Non-diagnostic by construction** |
| 5 | 1:25 (17s) | Capture **02** | "One falsifiable research line: the **IL-6R node is genetically causal** for coronary disease. Circulating CRP is **not**." | **Claude Science = runtime + connectors** |
| 6 | 1:42 (17s) | Capture **06** | "Replicates across **European** (FinnGen) and **East-Asian** (BioBank Japan) cohorts. The Alzheimer's axis stays **exploratory**." | Honesty / scope discipline |
| 7 | 1:59 (17s) | Capture **04** | "Operating its own pipeline under a **reviewer agent**, it audits its own work — and fixes what it flags." | **Correction mechanism** |
| 8 | 2:16 (20s) | Capture **07** | "It caught a bug in **its own flagship number**. Retracted **+0.705** → corrected **+0.553**. Shipped a regression test." | **Self-correction (climax)** |
| 9 | 2:36 (13s) | Checklist ✓ | "Promise delivered" — 5 clauses ticked | Proves the promise |
| 10 | 2:49 (12s) | End card | repo · `Apache-2.0` · `python demo/run_cohort.py` — "Clone it. Run it. No one from our team in the room." | **Usable without you** |

- **Open on:** the researcher's pain + the promise (never IL-6 first). **End on:** promise-delivered + the "clone and run it" repo/license card.
- **The dev-process beat (2b)** is the builder-track centerpiece — see [`HOW-IT-WAS-BUILT.md`](HOW-IT-WAS-BUILT.md).
- **Cut** (stays in the repo, not the video): the benchmark table, the Stage-3 ODE gallery, protein deep-dives beyond Capture 02. SkillOpt appears only as the "evolution" node in beat 2b.

Captures live in [`assets/claude-science/`](assets/claude-science/) (01, 02, 04, 05, 06, 07) and
[`assets/figures/fig_cohort_funnel.png`](assets/figures/fig_cohort_funnel.png).

### Voice-over / HeyGen alternative — [`assets/heygen/`](assets/heygen/)
If you'd rather narrate (your own voice — recommended — or a HeyGen avatar): a **thinned-caption** cut
([`HISTORA-demo-vo.mp4`](assets/heygen/HISTORA-demo-vo.mp4), captions reduced to key phrases + numbers so
they don't fight the narration), the **12 slides** ([`slides/`](assets/heygen/slides/)) as scene
backgrounds, a **PDF deck** ([`HISTORA-presentation.pdf`](assets/heygen/HISTORA-presentation.pdf)), and the
**per-scene narration script** ([`HEYGEN-SCRIPT.md`](assets/heygen/HEYGEN-SCRIPT.md)). Fable's ranking:
your own real voice-over > muted-captioned as-is > HeyGen voice-only > HeyGen full-frame avatar (avoid — a
talking head competes with the captures, which are the evidence).

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
   navigator (not IL-6), green tests, `LICENSE` + `NOTICE`, `SELF-CORRECTION.md` linked. The repo must tell
   the same story as the video within 30 seconds of scrolling.

**Biggest single risk:** a judge mis-slots this as a researcher-track "finding about IL-6." **Fix:** the
first 20 seconds of the video and the first two sentences of the summary name **the user** and **the tool**
before any biology, and land the "instrument, not the study" line above.
