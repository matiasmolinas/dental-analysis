# Claude Science — live-run captures

Screenshots of HISTORA running **live in Claude Science** (the flagship case study, §5 of
[`../../OVERVIEW.md`](../../OVERVIEW.md)). These are UI captures of the real session — the skill import, the
engine run, the connector-resolved 3-D structures, and the reviewer agent's audit.

> **How these get here (the browser tool can't write them to disk).** Capture each view from the Claude
> Science session with a macOS region screenshot — **`⌘⇧4`**, then drag a box around the panel — and save
> the file into **this folder** with the filename below. Frame the capture to **exclude the left project
> sidebar** (start the box at the conversation/viewer panel) so no other private project names appear.
> Once the files are here, they are embedded in `OVERVIEW.md` §5.

| Filename | What to capture |
|---|---|
| `01-skill-import.png` | the session loading the HISTORA skill + the non-diagnostic guardrail (the "Loaded 2 skills" step) |
| `02-engine-run.png` | `run_case_study.py` running / the falsifiable research-line output in the chat |
| `03-node-hexamer-3d.png` | the **IL-6/IL-6Rα/gp130 hexamer (1P9M)** open in the interactive Mol\* viewer (right panel only) |
| `04-reviewer-finding.png` | the reviewer agent's finding (1P9M is 3.65 Å, not 2.4 Å) **and** Claude's self-correction |
| `05-artifacts-tray.png` | the "GENERATED" artifacts tray (case_study.json + the .cif structures) |

*Non-diagnostic throughout; molecular/population-level only. The structure images in `OVERVIEW.md` are the
same PDB entries from RCSB PDB (rcsb.org); these captures show the same structures rendered **inside Claude
Science**.*
