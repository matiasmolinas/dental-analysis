# Demo script — the hybrid stage runbook

> The stage guion for HISTORA: a **portable CLI demo** (safe, deterministic) + a **live drop-in into
> Claude Science** (the "it lives in a real lab" moment). Target **~3 min core** (extendable to 5).
> Spoken lines are in **English** (say them verbatim); *stage directions and notes are in Spanish*.
> Companion to [`PITCH.md`](PITCH.md). Non-diagnostic throughout.

---

## 0. Pre-flight checklist (antes de subir al escenario)

- [ ] **Terminal** abierta en la raíz del repo; corré `python demo/run_demo.py` UNA vez para calentar y
      verificar (sale en <1 s, sin API key).
- [ ] **Chrome** con **Claude Science** en `http://localhost:8765/`, logueado, en un **proyecto nuevo**
      (no el "Example project", que es read-only). Dejá abierto **Customize → Skills** listo.
- [ ] **Act 4 (Claude Science) → GRABADO por default.** Solo corré el import en vivo si TODO está verde en
      el ensayo. Precondición del vivo (elegí UNA): repo `matiasmolinas/dental-analysis` **público**, *o* un
      **token de GitHub** en Claude Science → Settings → Credentials. Sin eso el import falla con
      "repository not found or private".
- [ ] **Assets estáticos en pestañas** (por si Mermaid no renderiza o Claude Science falla): el **PNG del
      diagrama** (`docs/assets/architecture.png`), el **one-page PDF** (`histora-resumen.pdf`), y
      `fig_cis_mr.png` / `fig_mr.png` de las corridas reales.
- [ ] **Grabaciones de respaldo**: (a) la corrida de `run_demo.py`, (b) el import en Claude Science
      (Customize → Skills → Import from GitHub → Preview). Por si falla la conexión en vivo.
- [ ] **Visuales de respaldo**: el one-page artifact/PDF y el diagrama de arquitectura del README, cada
      uno en una pestaña.
- [ ] Fuente de terminal grande (≥18 pt), tema claro, ventana ancha para que el brief se lea.

---

## 1. Hook — el problema y la tesis · ~20 s

*Direccción: parado, sin pantalla todavía o con el diagrama de arquitectura de fondo.*

> **Say:** "Gum disease, heart disease, diabetes, and Alzheimer's are studied in separate silos — but
> they may share one upstream driver: inflammation. HISTORA is a Claude-powered research agent that makes
> that idea **testable** — coherently, and honestly. It's a research agent, not a diagnostic tool."

---

## 2. El demo portátil — "the inflammatory-proxy walk" · ~90 s

*Dirección: cambiá a la terminal y corré el comando. Narrá mientras imprime los 5 pasos.*

```bash
python demo/run_demo.py
```

> **Say (mientras aparece cada bloque):**
> - **①** "One case goes in — as **structural bands**, not raw values. The missing lab? It's **flagged for
>   collection**, never guessed. That's the guardrail, in the math."
> - **②** "**Claude** proposes the oral–systemic hypotheses — each **citing the input fields** it used."
> - **③** "It hands them to a **mechanistic engine**: one shared inflammatory proxy forks to three axes.
>   Out comes **not a number, but a range** — with the therapy's predicted effect, and the **shakiest
>   assumption named**."
> - **④** "We check the directions in **public NHANES**, and probe causality with **genetics** — which
>   supports the heart link and, honestly, **not** the Alzheimer's one, so we flag that axis exploratory.
>   Note the panel: **validation is not the calibration**."
> - **⑤** "And it closes with a **falsifiable brief** — what would prove it wrong — plus an **agentic
>   metric card**: citations resolve, hallucination is zero, nothing is a diagnosis."

> **Say (remate):** "Three axes aren't three models — they're **one lever, three diseases, one engine.**"

---

## 3. Por qué gana — la evidencia · ~40 s

*Dirección: opcional, mostrá la tabla de headline results del README o el artifact.*

> **Say:** "We didn't just build it — we **measured** it. On a pre-registered benchmark, the integrated
> harness beats both **separate single-disease models** and **Claude without a harness**: one shared
> parameter instead of three, **calibration error zero**, ranges and falsification where they score zero.
> The associations **survive survey-weighted, multiplicity-controlled** statistics. Every number is
> traceable — that's the agentic card. This is an agent that is **useful because it's honest.**"

---

## 4. El drop-in en Claude Science — "y vive en un lab de verdad" · ~45 s

*Dirección: **corré este acto desde GRABACIÓN por default** (el import en vivo tiene demasiadas
precondiciones frágiles para 3 minutos: Chrome + `localhost:8765` + proyecto nuevo + repo público/token).
La grabación muestra: Customize → Skills → Import from GitHub → `matiasmolinas/dental-analysis` → 8/8
skills; la sesión con el **reviewer agent en "no issues found"**; y la figura de la **cis-MR**
(`fig_cis_mr.png`). Solo hacelo en vivo si TODO está verde en el ensayo. Está **probado en vivo** —
ver [`CLAUDE-SCIENCE.md`](CLAUDE-SCIENCE.md).*

> **Say:** "And this isn't only a CLI. **Claude Science** — Anthropic's workbench for scientists —
> imports our skills **straight from GitHub** *[click Import → 8 skills]*. Reasoning skills *and* the
> deterministic pipeline. We ran it: a case → a non-diagnostic analysis the platform's **reviewer agent
> passed**; and the pipeline pulling **real genetics from OpenGWAS** — the LD-aware IL-6R probe shows
> **coronary disease is causal, β≈0.7** *[show fig_cis_mr.png]*, while circulating CRP is null. **Same
> components, no rewrite** — a Claude Code plugin today, a Claude Science skill today too."

*Nota honesta (tenela lista): las **skills de razonamiento** corren nativas; el **motor determinista** corre
como pipeline (pip-install del paquete pineado + Compute). Ambos probados en vivo. No prometas más que eso.*

---

## 4b. SkillOpt — el diferenciador (opcional, ~25 s; usalo al extender a 5 min o si te lo piden)

*Dirección: **corré este comando en la terminal** (offline, <1 s) y mostrá las dos filas del archivo —
la ADOPTED y la REJECTED. Es el beat "más allá de la competencia": Claude mejorándose a sí mismo bajo
una invariante de seguridad que es **estructuralmente imposible de evolucionar**.*

```bash
python src/run_skill_evolution.py --fresh
```

> **Say:** "One more thing — the role nobody else shows. HISTORA can **improve its own skills**. Claude
> proposes an edit *[point to ADOPTED]*; we keep it **only if** it measurably improves — the confidence
> interval excludes zero — **and** the non-diagnostic guardrail still passes on **every** case. Here's the
> proof it has teeth *[point to REJECTED]*: this sibling gained the **exact same metric**, but it touched
> the guardrail — so it's **thrown out**. Same guardrail hash on both. **Self-improvement where breaking
> the rule scores zero — by construction.**"

*Nota honesta: **una** generación, offline, con una métrica estructural ilustrativa (cobertura de
citación de campos) — el *mecanismo*, no un resultado en vivo; la corrida definitiva cablea a Claude como
mutador + `agent_metrics`, igual que la MR pasó de ilustrativa a viva. Ver [`EVOLUTION.md`](EVOLUTION.md).*

---

## 5. Cierre — por qué ahora, por qué Anthropic + Gladstone · ~25 s

> **Say:** "Why now: the science is mature, the public data is rich, and models can finally **orchestrate**
> a mechanistic pipeline instead of guessing. Why here: HISTORA touches **four of Gladstone's five
> institutes**, and hands its neuro labs a **novel upstream perturbation** — periodontal inflammation to
> tau — as a falsifiable hypothesis. It's honest by construction: **ranges, falsification, citations, and
> a hard non-diagnostic guardrail.** That's the kind of scientific agent that earns trust — and
> accelerates research **safely**. Thank you."

---

## 6. Q&A — respuestas honestas preparadas

| Si preguntan… | Respondé (honesto, sin defensiva) |
|---|---|
| "The effect sizes are small." | "Yes — periodontitis is **one contributor among many**; that's the honest epidemiology. HISTORA is a **hypothesis generator**, not a risk score. The value is coherence + honesty, not a big number." |
| "The Alzheimer's link didn't hold." | "Correct — the **genetics don't support it causally**, and we **flag that axis exploratory**. Reporting the null *is the feature* — an agent you can trust because it tells you what it can't show." |
| "Are the MR numbers real?" | "Yes — we ran it **live over public OpenGWAS** in Claude Science: verified the study IDs against `gwasinfo`, harmonized, and ran the unit-tested estimator. The repo also ships illustrative panels for offline reproducibility, clearly labeled." |
| "Wait — is it 0.105 or 0.705?" | "Different instrument *and* method. **0.105** is the established literature direction (CRP/IL-6R with **naïve IVW**). **0.705** is our **cis IL-6R** run with **correlated (LD-aware) IVW** — the valid estimator when the instruments are in LD; naïve IVW understates it with a ~7× wider SE. And circulating CRP → CAD is **null** — the marker isn't causal, the IL-6R node is." |
| "Is this clinical-ready?" | "**No — and by design.** It's **non-diagnostic**: structural bands in, population-level ranges out, never a patient value. It's a research instrument for a lab, not a bedside tool." |
| "Why not just prompt Claude?" | "We tested that — it's the **bare-model arm**. It **hallucinates uncited numbers, gives points not ranges, and isn't calibrated**. The harness is what makes Claude honest here." |
| "What's novel for Gladstone?" | "A **parameterized, falsifiable upstream perturbation** (perio-inflammation → tau-α) they can plug into existing tau/microglia/BBB models — with the intellectual honesty, including the **failed GAIN trial**, a serious lab needs." |
| "How is the self-improvement safe?" | "The **genome is only the prose of trainable skills** — the guardrail, the citations, and the engine are outside it, so evolution literally can't reach them. Safety is a **binary gate, not a fitness term**: any guardrail failure disqualifies the edit no matter how much metric it gained. And the archive carries the **guardrail hash, identical in parent and child** — machine-checkable proof the invariant never moved. It's `EVOLUTION.md`." |

---

## 7. Fallbacks (si algo falla en vivo)

1. **El import de Claude Science falla** (repo privado / sin token) → mostrá la **grabación** del import y
   el screenshot del diálogo *"Import from GitHub: plugin-marketplace layout… or any repo with skills/
   directories"*; decí: "our repo follows exactly this layout — here it is importing." (No pierdas tiempo
   depurando en vivo.)
2. **Claude Science se cuelga** → pasá al **one-page artifact/PDF** (la historia completa en una hoja).
3. **`run_demo.py` falla** → corré la **grabación** del brief; el resultado es determinista, así que es
   idéntico.
4. **Te quedás sin tiempo** → cortá el Act 3 (Claude Science) y cerrá con el Act 5; el demo portátil +
   la evidencia (Acts 2-3) ya cuentan la historia.

---

## 8. Runbook — comandos y clicks exactos

**Terminal (Act 2):**
```bash
python demo/run_demo.py            # el brief end-to-end, offline
```
**Claude Science (Act 4):** `localhost:8765` → *(proyecto nuevo)* → **Customize** → **Skills** →
**Add skill** ▾ → **Import from GitHub** → escribir `matiasmolinas/dental-analysis` → **Preview** →
**Import** → volver a Skills y mostrar las de HISTORA activadas.

---

*Guion en inglés para la entrega; puedo generar una versión 100% en español si presentás en español.
Companion: [`PITCH.md`](PITCH.md) (la tesis) · [`DATA-AND-DELIVERY.md`](internal/DATA-AND-DELIVERY.md) (la integración).*
