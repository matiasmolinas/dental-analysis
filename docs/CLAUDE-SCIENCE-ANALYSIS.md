# Integrated vs. Claude Science — a hands-on comparative analysis

> For *our* problem (a non-diagnostic oral-systemic research agent), is our **integrated** harness better
> or worse than **Claude Science**? Is a **100% Claude-Science** solution possible — and what do we lose
> and gain? Grounded in a hands-on exploration of a local Claude Science (beta) instance.
> Companion to [`DATA-AND-DELIVERY.md`](DATA-AND-DELIVERY.md) and [`PITCH.md`](PITCH.md).

## 1. What Claude Science actually is (verified hands-on)

Confirmed empirically in the running app (not just the docs):
- **Extension model:** *Capabilities* = **Skills · Connectors · Specialists · Memory · Compute ·
  Network**; *Workspace* = Permissions · Credentials · Storage · Usage.
- **Skills** are added via **Chat with Claude · Write from scratch · Upload (.zip or SKILL.md) · Import
  from GitHub**. The GitHub importer accepts *"any repo that follows the **plugin-marketplace layout** —
  or any repo with `skills/` directories."* — **exactly HISTORA's repo layout.**
- **Built-in skills** seen: AlphaFold2, Boltz, Borzoi, Chai-1, DiffDock, ESM-2, ESMFold2, **Evo 2**,
  **Indication Dossier**, LigandMPNN, **Literature Review**, OpenFold3, ProteinMPNN, … (the BioNeMo set).
- **Credentials/connectors:** GitHub, **Modal** (compute), **NVIDIA API** (BioNeMo), **OpenAlex** +
  **Literature access (journals)**, AWS/GCP/Azure. 60+ scientific databases.
- **Rendering:** native scientific figures (saw UMAP scatter, dot plots), markdown reports, and an
  artifact tray per session — every artifact traced to its code.
- **Culture:** the platform's own example session ends with *"associative AUCs — should be validated in an
  independent cohort before any translational use."* — **our exact honesty ethos.**

## 2. The core question: what MUST be code vs. what Claude Science does better

Our problem has a **hard deterministic core** that cannot be a prompt:

| Must remain code (our moat) | Why |
|---|---|
| ε calibration (bisection to the ΔCRP anchor) | a numerical fixed-point; a model-in-the-loop can't reproduce it reliably |
| the ensemble UQ (Latin-hypercube sweep → envelopes + sensitivity) | reproducible ranges, not vibes |
| the Fisher–KPP tau-spread PDE on the connectome | a real solver |
| the survey-weighted OLS + cluster bootstrap + FDR | design-based inference, seed-exact |
| the MR estimator (IVW/Egger/weighted-median) | tested on synthetic ground truth |
| the benchmark + agentic metrics | pre-registered, deterministic, seed-pinned |
| the non-diagnostic guardrail | enforced *by construction*, not by a model's goodwill |

**Claude Science does not replace this core — it hosts and wraps it.** So the comparison is not
"either/or"; it is *where the deterministic engine lives, and what surrounds it.*

## 3. Three delivery modes, compared

| Dimension | **A. Integrated (plugin / CLI)** | **B. Hybrid (recommended now)** | **C. 100% Claude Science** |
|---|---|---|---|
| Determinism / reproducibility | ✅ bit-for-bit, offline | ✅ core stays code | ◑ must **pin** the core as a fixed pipeline skill |
| Guardrail by construction | ✅ in our code path | ✅ in our code path | ◑ must **re-verify** in-platform (+ reviewer agent) |
| Portability / no account | ✅ runs anywhere | ✅ CLI arm runs anywhere | ❌ beta; needs a plan/account |
| Graphics / presentation | ❌ CLI text | ✅ CLI + native figures on the Science arm | ✅✅ native figures/proteins/tracks |
| Data integration (GWAS, UniProt, PDB, journals) | ❌ custom code | ◑ some | ✅✅ connectors (OpenAlex, Literature, NVIDIA) |
| Compute (real OpenGWAS MR, big ensembles) | ❌ laptop | ◑ | ✅ Modal / HPC |
| Continuous review (citations/calcs) | our `agent_metrics` (offline) | both | ✅ the platform **reviewer agent**, native |
| Alignment signal (Anthropic/Gladstone) | ◑ | ✅ | ✅✅ demoing in Anthropic's own workbench |
| Stage risk | ✅ lowest | ✅ low (CLI fallback) | ❌ highest (beta live) |

## 4. Is a 100% Claude-Science solution possible? Yes — here is the shape

- **The `histora` harness** → a **reusable pipeline saved as a skill** (imported from our GitHub repo;
  the layout already matches). The skill *invokes our pinned, versioned code* — so the numbers stay
  deterministic; the model orchestrates, it does not regenerate the math.
- **`agents/`** (orchestrator, periodontal/cardiometabolic analysts, guardrail-verifier) → **Specialists**.
- **Data** (UniProt/PDB grounding, GWAS for MR, journals for citations) → **Connectors** (OpenAlex,
  Literature access, NVIDIA/BioNeMo).
- **`agent_metrics` (citations/hallucination/guardrail)** → the platform **reviewer agent**, continuous.
- **Compute** (real two-sample MR over OpenGWAS; larger sweeps) → **Modal / HPC**.

So "100% integrated" is real and buildable. The endpoint is **HISTORA-as-a-Claude-Science-skill**.

## 5. What we LOSE going 100% Claude Science (and the mitigation)

1. **Offline / portability / no-account.** Claude Science is beta and gated by plan. *Mitigation:* keep
   the **Claude Code plugin + CLI** as the portable twin — hence the hybrid; never let the stage depend
   on the beta.
2. **Determinism, if we let the model regenerate the math.** *Mitigation:* the skill must call a **pinned,
   versioned pipeline** (our tested code), not re-derive results per session. Treat the numeric core as
   frozen; only I/O is model-mediated.
3. **The guardrail moves from "by construction" to "by policy + reviewer."** *Mitigation:* ship the
   non-diagnostic guardrail as an explicit skill/policy *and* rely on the reviewer agent; add a
   platform-side check that no patient value is ever produced.
4. **Our pytest CI (19 suites) is repo-side.** *Mitigation:* keep the repo + CI as the source of truth;
   the skill is a thin wrapper over the same tested code.
5. **Control of the exact benchmark protocol** (seeds, prompts). *Mitigation:* keep the benchmark in the
   repo; surface its results as an artifact, don't re-run it model-in-the-loop.

**Net:** we lose *portability and the purity of "by construction"* — not the engine. Everything
load-bearing survives as long as the core stays a pinned pipeline.

## 6. What we GAIN (graphics, presentation, integration)

- **Graphics** — the parts that make a science demo land, now as native figures instead of CLI text:
  - the **ensemble envelopes** → a forest / uncertainty-band plot per axis;
  - the **sensitivity ranking** → a tornado plot (ε dominates CRP; β_tau dominates neuro);
  - the **tau spread** → the Braak-ordered connectome front, animated;
  - the **MR probe** → a beta-exposure vs beta-outcome scatter with the IVW slope;
  - the **benchmark / agentic card** → grouped bars;
  - **mechanism proteins** (IL-6/IL-6R, CRP, tau, gingipain) → 3D structures via AlphaFold/PDB.
- **Integration / data** — turn our honest caveats into real results:
  - **OpenAlex + Literature access** → auto-build and *verify* `docs/CITATIONS.md` at scale (citation
    accuracy becomes continuous, not a fixed table);
  - **GWAS connectors + Modal** → replace the **illustrative MR panels with live OpenGWAS extracts** —
    our biggest single upgrade;
  - **Indication Dossier / Literature Review** skills → a translational framing a Gladstone lab reads.
- **Presentation / trust** — every figure carries its **code + environment + message history**
  (reproducible artifacts), and the **reviewer agent** flags any untraceable number live — which *is* our
  agentic-metrics story, now platform-native. Demoing in Anthropic's flagship science surface is itself an
  alignment signal.

## 7. How to improve our results *in* Claude Science (concrete next steps)

1. Import the repo skills (GitHub) + save the harness as a **pinned pipeline skill**.
2. Add a **plotting skill** that renders envelopes / sensitivity / tau-front / MR / benchmark from our
   JSON outputs (the demo already emits `brief.json`).
3. Wire **OpenGWAS via a connector + Modal** to run the **real MR** and drop the "illustrative" caveat.
4. Wire **OpenAlex/Literature** to expand + verify the citation registry; let the **reviewer agent** score it.
5. Add **AlphaFold/PDB** mechanism visuals for IL-6R / tau / gingipain.
6. Keep the **non-diagnostic guardrail** as an explicit skill + a reviewer check.

## 8. Recommendation

**Hybrid now → a Claude Science skill as the endpoint.** Our integrated harness is **not redundant** — it
is precisely the deterministic engine Claude Science should host; Claude Science is the presentation +
data + review layer we don't have. Going 100% Claude Science is worth it **for the final product**
(graphics, data, review, alignment), provided we **pin the numeric core** so reproducibility and the
guardrail survive. For the **hackathon stage**, keep the portable CLI/plugin as the safe spine and show
the Claude Science drop-in as the "where it lives" moment.

---

## Appendix — live import test (result)

With a GitHub token connected, Claude Science **read our repo and recognized the plugin-marketplace
manifest**: *"publisher name: histora · marketplace manifest · by HISTORA / dental-analysis."* So the
layout is detected — the integration path is real.

**But: 0 skills importable** — *"Not importable: histora-oral-systemic (**no skills/ dirs with
SKILL.md**)."* Our skills were flat `.md` files; Claude Science (and the current Claude Code skill spec)
require **`skills/<name>/SKILL.md`** — each skill in its own subdirectory with a file named `SKILL.md`.

**Fix applied (this PR):** the seven skills were restructured `skills/<name>.md → skills/<name>/SKILL.md`
in both the plugin and the top-level `skills/`. After pushing, re-running the GitHub Preview should show
them importable. This is the concrete, mechanical change that makes HISTORA importable into Claude Science
— and it also aligns us with the current Claude Code skill spec, so it improves both surfaces at once.

**Takeaway for the analysis:** "100% Claude Science" is not just possible in principle — the importer
*already parses our repo*; the only blocker was a skill-file layout convention, now fixed.

*Non-diagnostic throughout; population/parameter-level only.*
