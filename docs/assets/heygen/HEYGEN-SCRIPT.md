# HISTORA — HeyGen / voice-over kit

An **alternative version** of the demo where your avatar (or just your voice) narrates while the slides
play. This folder has everything you need:

- **`slides/s00.png … s10.png`** — the 12 slides with **thinned captions** (short phrases + numbers only),
  so they sit *under* narration without a read-vs-listen conflict. Use these as scene backgrounds.
- **`HISTORA-demo-vo.mp4`** — the same thinned slides already assembled into a muted ~182s video (use it
  as a single background clip if HeyGen lets you overlay an avatar over a video).
- **`HISTORA-presentation.pdf`** — the deck (one slide per page) for import or screen-recording.
- The narration script is below, keyed to each slide with its duration.

> The standalone muted+captioned video (`../HISTORA-demo.mp4`) is the safe default and is submission-ready
> on its own. This kit is only if you want to add your voice/avatar.

## How to build it in HeyGen

1. New video → set canvas **16:9 (1920×1080)**.
2. Create **12 scenes**. For scene *n*, upload **`slides/sNN.png`** as the full-frame background.
3. Paste that scene's **script line** (below) as the spoken text; pick **your own voice clone** (best) or a
   voice-only track. If you use an avatar, make it a **small corner talking-head**, not full-frame — the
   slide is the evidence and should stay dominant.
4. Set each scene's **duration** to the value listed (or let HeyGen auto-time and nudge to match).
5. Export. Total ≈ **182 s** (under the 3-minute cap). Add gentle cross-dissolves between scenes if offered.

**Honesty rules (do not deviate):** never say "treats" or "prevents"; only "window into / linked to". The
Alzheimer's axis is **exploratory**. All output is **non-diagnostic / population-level**.

## Script (first-person director voice) — ~305 words, ~182 s

| Scene | Slide | Dur | Say this |
|---|---|---|---|
| 0 | `s00.png` | 11s | "The mouth is a cheap, modifiable window into the inflammation behind heart disease and diabetes. But testing that link takes a researcher weeks of chart review — and often the data was never collected." |
| 1 | `s01.png` | 10s | "So I built the tool I was missing: from a hypothesis to a research-ready cohort and a self-audited, non-diagnostic research line — in minutes, on real public data." |
| 2 | `s02.png` | 16s | "I built it with Claude Code. Under my direction it wrote the engine, the tests, and the non-diagnostic guardrail — then it operated Claude Science itself to run and check the science." |
| 2b | `s02b.png` | 14s | "This is a supervised autonomous loop. I direct; Claude Code drives Claude Science through the Chrome extension, as the scientist — and it evolves and corrects itself along the way." |
| 3 | `s03.png` | 18s | "Here it is working. A research-ready cohort in seconds — a real eligibility funnel over public NHANES data: twenty thousand nine hundred five participants down to four hundred forty-two." |
| 4 | `s04.png` | 17s | "And it tells you what the data cannot answer. A missing value is a collection flag — never imputed. Population-level ranges out, never a patient value." |
| 5 | `s05.png` | 17s | "Then the biology that makes the cohort worth building. One falsifiable research line: the IL-6R node is genetically causal for coronary disease — while circulating CRP is not." |
| 6 | `s06.png` | 17s | "It replicates across European and East-Asian cohorts. The Alzheimer's axis stays exploratory — the genetics are null, and I say so." |
| 7 | `s07.png` | 17s | "Operating its own pipeline under a reviewer agent, it audits its own work — and fixes what it flags." |
| 8 | `s08.png` | 20s | "It even caught a bug in its own flagship number. It retracted plus zero point seven zero five, corrected it to plus zero point five five three, and shipped a regression test. A tool that can only ever agree with itself is worthless." |
| 9 | `s09.png` | 13s | "Cohort, honesty, live genetics, self-correction, non-diagnostic — promise delivered." |
| 10 | `s10.png` | 12s | "It's open source, Apache-licensed. Clone it, run it — with no one from my team in the room." |

*Numbers are written out phonetically where it helps TTS land them cleanly.*
