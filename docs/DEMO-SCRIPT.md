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
      diagrama** (`docs/assets/architecture.png`) y `fig_cis_mr.png` / `fig_mr.png` de las corridas reales.
- [ ] **Grabaciones de respaldo**: (a) la corrida de `run_demo.py`, (b) el import en Claude Science
      (Customize → Skills → Import from GitHub → Preview). Por si falla la conexión en vivo.
- [ ] **Visuales de respaldo**: el one-page artifact/PDF y el diagrama de arquitectura del README, cada
      uno en una pestaña.
- [ ] Fuente de terminal grande (≥18 pt), tema claro, ventana ancha para que el brief se lea.

---

## 1. Hook — el problema del investigador (NO la hipótesis) · ~25 s

*Dirección: parado, sin pantalla todavía. Empezá con el DOLOR, no con IL-6. (Cambio pedido por los dos
revisores clínicos: primero el problema, después la solución, después la ciencia.)*

> **Say (as the researcher):** "I'm a clinical researcher. I have a hypothesis — periodontal inflammation
> may share mechanisms with systemic disease. But testing it means reviewing **hundreds of medical and
> dental records** to build a cohort. That takes **weeks**." *(pausa)* "…and only then do I find out the
> data I need is missing."

> **Say:** "Researchers don't need another chatbot. They need an AI that builds **research-ready cohorts**
> from fragmented clinical data. That's HISTORA — a **clinical-research copilot**. It works *with* you."

---

## 2. El demo que gana — el copiloto de cohortes · ~75 s

*Dirección: corré esto PRIMERO (la capacidad que el jurado entiende al instante). Números 100% reales sobre
NHANES 2009-2010 — nada sintético. Narrá el funnel mientras imprime.*

```bash
python demo/run_cohort.py
```

> **Say (mientras aparece cada bloque):**
> - **El funnel:** "The researcher asks a question — not a patient. Claude filters the corpus:
>   **20,905 → periodontitis → + diabetes → + hs-CRP → a real cohort.** Seconds, not weeks. Every number
>   is real, public NHANES."
> - **② Completeness / lo que falta:** "And here's the honest part — Claude tells you what the data
>   **can't** answer: no repeat CRP, no follow-up, no biologic-exposure timeline. A missing datum is a
>   **collection flag, never guessed.** No researcher wants to discover that three months in."
> - **③ Hipótesis, no conclusión + ④ integrity checklist:** "Claude poses a **falsifiable hypothesis**,
>   consistent with the IL-6R genetics as *plausibility, not proof* — and the card says it plainly:
>   ✓ cohort, ✗ causality, ✗ diagnosis, ✗ therapy."
> - **⑤ Export:** "One button — a **preliminary protocol**: variables, inclusion/exclusion, limitations.
>   It prepares the study. It doesn't do the study."

> **Say (remate):** "That's the copilot. Now — *why* is this cohort worth building? The biology." *(→ Act 3)*

---

## 2b. La ciencia que da plausibilidad — "the inflammatory-proxy walk" · ~75 s

*Dirección: SOLO AHORA aparece IL-6. La profundidad mecanística es tu diferenciador frente a otros equipos;
no la amputes — secuenciala como la plausibilidad biológica de la cohorte.*

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

> **Say:** "We didn't just build it — we **measured** it. On a pre-registered benchmark the integrated
> harness does things separate single-disease models and Claude-without-a-harness **structurally can't**:
> one shared parameter instead of three, and **calibrated ranges with falsification** where the
> alternatives can only give a point and no way to be wrong. That's a **capability gap**, not just a
> higher score. And the associations **survive survey-weighted, multiplicity-controlled** statistics —
> the design-adjusted numbers, the conservative ones. Every number is traceable. This agent is **useful
> because it's honest.**"

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
> **coronary disease is causal, correlated-IVW β≈+0.553 (SE 0.109)** *[show fig_cis_mr.png]*, while circulating CRP is null. **Same
> components, no rewrite** — a Claude Code plugin today, a Claude Science skill today too."

*Nota honesta (tenela lista): las **skills de razonamiento** corren nativas; el **motor determinista** corre
como pipeline (pip-install del paquete pineado + Compute). Ambos probados en vivo. No prometas más que eso.*

---

## 4b. SkillOpt — el diferenciador (opcional, ~25 s; usalo al extender a 5 min o si te lo piden)

*Dirección: liderá con el **portfolio en vivo** (el resultado creíble), después mostrá el mecanismo con el
archivo offline (ADOPTED + REJECTED) que corre en <1 s en el escenario. NO corras SkillOpt en vivo.*

```bash
python src/run_skill_evolution.py --fresh    # el mecanismo, determinista, seguro para escenario
```

> **Say:** "One more thing — the role nobody else shows. HISTORA can **improve its own skills**, and here's
> the honest part first: we ran it live on three skills — Claude improved **two** of them, and **correctly
> refused a third** because that skill was already optimal. It doesn't manufacture a win. And it can
> **never** touch the non-diagnostic guardrail — that lives outside the part it's allowed to edit, and the
> archive carries a hash, identical before and after, that proves it. *[show the offline archive]* Here's
> the mechanism: an edit is kept **only if** it measurably improves — CI excludes zero — **and** the
> guardrail still passes on every case; this rejected sibling gained the same metric but broke the
> guardrail, so it's thrown out. **Self-improvement where breaking the rule scores zero — by construction.**"

*Nota honesta: el **portfolio en vivo** (2 adoptadas por mecanismos distintos, 1 null) está corrido y
documentado en [`evolution/live-run-2026-07.md`](evolution/live-run-2026-07.md) — Claude sonnet como mutador,
Claude haiku como agente puntuado, métricas estructurales verificables por máquina. En escenario mostrás el
archivo **offline** (`run_skill_evolution.py`, determinista, <1 s) como el mecanismo; el portfolio en vivo lo
contás (o lo mostrás grabado). NO corras el loop en vivo. Ver [`EVOLUTION.md`](EVOLUTION.md).*

---

## 5. Cierre — por qué ahora, por qué Anthropic + Gladstone · ~25 s

> **Say:** "It's honest by construction — a **research-integrity gate**: it never fabricates a value, never
> makes an individual claim, never diagnoses; everything is a range, falsifiable, and cited. And the neuro /
> Alzheimer's axis? **One sentence: exploratory — the model extends to other inflammatory axes, but it's not
> a conclusion here.** That discipline is the point."

*Dirección (cierre — Cambio 10 de los revisores): no termines hablando del futuro. Terminá en el PRESENTE.*

> **Say (cierre):** "So — today, preparing a research cohort takes **weeks**." *(pausa)* "HISTORA:
> **it's already prepared.** Thank you."

---

## 6. Q&A — respuestas honestas preparadas

| Si preguntan… | Respondé (honesto, sin defensiva) |
|---|---|
| "The effect sizes are small." | "Yes — periodontitis is **one contributor among many**; that's the honest epidemiology. HISTORA is a **hypothesis generator**, not a risk score. The value is coherence + honesty, not a big number." |
| "The Alzheimer's link didn't hold." | "Correct — the **genetics don't support it causally**, and we **flag that axis exploratory**. Reporting the null *is the feature* — an agent you can trust because it tells you what it can't show." |
| "Are the MR numbers real?" | "Yes — we ran it **live over public OpenGWAS** in Claude Science: verified the study IDs against `gwasinfo`, harmonized, and ran the unit-tested estimator. The repo also ships illustrative panels for offline reproducibility, clearly labeled." |
| "Wait — is it 0.105 or 0.553?" | "Different instrument *and* method. **0.105** is the established literature direction (CRP/IL-6R with **naïve IVW**). **0.553** (SE 0.109) is our **cis IL-6R** run with **correlated (LD-aware) IVW** — the valid estimator when the instruments are in LD; naïve IVW ignores the SNP correlation and under-states the variance. And circulating CRP → CAD is **null** — the marker isn't causal, the IL-6R node is." |
| "Aren't the benchmark baselines a strawman — of course your calibrated model wins on calibration?" | "Fair, and I'll say it first: it's **not a horse race on a shared metric** — it's a **capability gap**. Separate single-disease models and bare Claude **structurally cannot** produce one shared parameter, calibrated ranges, or a falsification condition. The zeros aren't 'they scored low', they're 'they can't do this at all'. The number to trust is the **NHANES validation surviving survey-weighted, FDR-controlled** stats — that one's an honest, external test." |
| "Isn't SkillOpt's 0.00 → 0.93 a metric you designed so your edit trivially wins?" | "It would be — if that were the whole story. That's exactly why the honest headline is the **null**: on `record-normalization` the loop **adopted nothing** because the skill was already at ceiling, and it **declined** a candidate that *lowered* the metric. It improves only where there's real, measured headroom, and it can **never** touch the guardrail. A search that improved everything it touched would be the one gaming its metric — this one doesn't." |
| "Is the cohort real, or did you fake it?" | "**Real.** The funnel runs over **public NHANES 2009-2010** — 20,905 participants down to a real cohort; every N is a real count, nothing synthetic. NHANES is **cross-sectional**, so we say it plainly: it can't answer the *longitudinal* question (repeat CRP, follow-up, biologic timeline) — that needs a real EHR. Showing what the data **can't** do, on real data, is the whole point." |
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
