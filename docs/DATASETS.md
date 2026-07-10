# Datasets

Real and synthetic data sources for the HISTORA oral-systemic project, why each was
chosen, how it maps to our schema, and its limitations. Decision:

> **Primary real anchor: NHANES 2009–2010** (public, de-identified, downloadable).
> **Mediator layer: NHANES Oral Microbiome 2009–2012** (SEQN-linkable; overlaps
> perio + CRP in 2009–2010). **Longitudinal / shareable demo data: Synthea** with a
> custom periodontal module. All non-PHI. Imaging datasets (BRAR/Tufts/DENTEX) are
> deferred; real EDR+EHR (BigMouth) and longitudinal CV cohorts (ARIC) are named as
> access-gated validation targets, not used in the event.
>
> This composite reality — no single public dataset has everything — is itself the
> point: integrating fragmented oral + systemic sources is exactly what HISTORA is.

---

## 1. NHANES 2009–2010 — primary real anchor

US CDC National Health and Nutrition Examination Survey. Nationally
representative, **de-identified, direct download** (no application, no DUA) from
<https://wwwn.cdc.gov/nchs/nhanes/>. The 2009–2010 cycle is the sweet spot: the
**full-mouth periodontal exam** (protocol ran 2009–2014) coexists with **CRP**
(the inflammatory mediator; hs-CRP only returns in 2015–2018, after the periodontal
exam ended). So 2009–2010 uniquely pairs periodontal + CRP + HbA1c + lipids + BP +
smoking + CV history.

### Schema ↔ NHANES 2009–2010 mapping (files use the `_F` suffix)

| Our schema field | NHANES file | Variable(s) |
|---|---|---|
| `demographics.age` / `sex` | `DEMO_F` | `RIDAGEYR` / `RIAGENDR` |
| `demographics.bmi` | `BMX_F` | `BMXBMI` |
| `periodontal.*` (PPD, CAL) | `OHXPER_F` | per-site probing depth / attachment loss (derive mean PPD, CAL) |
| `medical_cv.hs_crp` (inflammatory mediator) | `CRP_F` | `LBXCRP` (mg/dL) |
| `shared_risk.hba1c` | `GHB_F` | `LBXGH` (%) |
| `shared_risk.type2_diabetes` | `DIQ_F` | `DIQ010` |
| `medical_cv.ldl` / `hdl` / `triglycerides` | `TRIGLY_F`, `HDL_F`, `TCHOL_F` | `LBDLDL` (fasting subsample), `LBDHDD`, `LBXTC` |
| `shared_risk.blood_pressure` / `hypertension` | `BPX_F` | `BPXSY1` / `BPXDI1` |
| `shared_risk.smoking_*` | `SMQ_F` (+ `COT_F` cotinine) | `SMQ020`, `SMD030` |
| `medical_cv.medications` | `RXQ_RX_F` | `RXDDRUG` |
| `medical_cv.prior_cv_event` / `family_history_mi` | `MCQ_F` | `MCQ160C/E/F`, `MCQ300A` |

Exact per-site periodontal variable names must be confirmed against the `OHXPER_F`
codebook. The mapping is encoded in [`../src/histora/nhanes.py`](../src/histora/nhanes.py);
a documented download + case-builder is in [`../src/histora/nhanes.py`](../src/histora/nhanes.py)
(reads XPT via `pandas.read_sas`, no extra deps).

### Uses in the project

- Ground the synthetic case values in real distributions (replace invented numbers).
- Validate that our agent's relational axes match known epidemiology.
- **Reproducible mini-analysis (Research-track flavor):** replicate the
  CRP ↔ periodontitis association/mediation on 2009–2010.

### CRP availability — important correction

CRP is the crown-jewel mediator, and it is **cycle-limited**. Standard CRP exists
only in **2005-2006, 2007-2008, 2009-2010**; there is **no CRP in 2011-2012 or
2013-2014**, and high-sensitivity CRP only returns in **2015-2018** (after the
full-mouth periodontal exam ended in 2014). Therefore the **periodontal-full-mouth ×
CRP overlap is uniquely 2009-2010.** Do not extend to "2009-2014" for the
inflammatory-axis work — you would keep the periodontal exam but lose CRP. Use
2009-2014 only for periodontal + cardiometabolic (HbA1c, lipids, BP, smoking)
without CRP, when a larger N matters more than the inflammatory mediator.

### Limitations

- **Cross-sectional** — no per-patient longitudinal progression (our
  `ppd_18m_ago_mm` field has no NHANES source). Use Synthea for progression.
- Survey/exam data, not integrated per-patient clinical narratives — we assemble
  the narrative; NHANES supplies grounded values.
- LDL only on the fasting subsample; CRP is standard, not high-sensitivity.

---

## 1b. NHANES Oral Microbiome 2009-2012 — mediator layer

Oral-rinse microbiome testing on NHANES participants (cycles 2009-2010 and
2011-2012): amplicon sequence variants, alpha/beta diversity, and genus-level
abundance tables, **linkable by `SEQN`** to the periodontal exam and full phenotype.
Hosted at <https://wwwn.cdc.gov/Nchs/Nhanes/Omp/> (separate from the standard XPT
set; see `NHANES_OMP_URL` in `src/histora/nhanes.py`).

**Why it matters — the real, reproducible mediator chain.** In **2009-2010** the
microbiome overlaps with the full-mouth periodontal exam **and** CRP **in the same
participants**, so one public dataset supports:

```
periodontal burden -> oral microbiome profile -> systemic inflammation (CRP) -> CV risk
```

This operationalizes our `bacteremia` / `microbial` bridge concepts with real data
and is a strong reproducible **Research-track** finding (does the oral microbiome
profile mediate the periodontal↔CRP association?). Pair with HOMD (see the KB skill)
to name specific pathogens. **Limitation:** oral-rinse (not subgingival) sampling;
still associational.

---

## 2. Synthea — longitudinal, shareable synthetic data

Open-source synthetic patient generator (<https://synthetichealth.github.io/synthea/>),
also published as OMOP on the AWS Open Data registry. Fully synthetic → **no PHI**,
freely shareable for the demo and writeup.

- No built-in dental/periodontal module, but the Generic Module Framework lets us
  author one (periodontitis progression, BOP, bone loss) alongside its existing
  diabetes / hypertension / lipids modules.
- Fills NHANES's gap: **longitudinal integrated dental + medical records** with
  time-aligned events — exactly our record format's progression dimension.

### Uses

- Demo cases with real longitudinal progression (PPD rising over months).
- Stress-test the record normalizer and the capacity probe at record sizes NHANES
  single rows don't reach.

### Limitation

- Synthetic associations are model-authored, not empirical — do not use Synthea to
  *validate* oral-systemic associations (that is NHANES's job); use it for
  pipeline/UX and longitudinal structure.

---

## 3. Imaging datasets — deferred (not on the critical path)

Radiograph → structured-feature extraction is a separate vision sub-project,
orthogonal to our interpretability loop and expensive for a one-week event. Our
`radiographic_bone_loss` field stays a structured value (NHANES/Synthea/note), not a
CV imaging pipeline. Named for a later "imaging-enhanced" version:

- **BRAR** — 1,104 patients, full-mouth panoramic radiographs with periodontist
  annotations and a Bone Resorption Age Ratio. Good for bone-loss features; not for
  oral-systemic inference (no shared patients with NHANES).
- **Tufts Dental Database** / **DENTEX** — panoramic radiographs with tooth and
  anomaly labels; auxiliary dental vision only (no systemic layer).

## 4. Named but not used (access-gated — real-world / longitudinal validation targets)

- **BigMouth Dental Data Repository** (UTHealth; NIDCR/DDSHub, i2b2) — real dental
  EDR: demographics, diagnoses, procedures, periodontal charts, medications, forms.
  The closest public-adjacent analogue to HISTORA's world; access by project
  proposal. Ideal to test the agent on messy, incomplete, longitudinal real records.
- **ARIC / Dental ARIC** (BioLINCC, application + DUA) — population CV cohort with
  full-mouth periodontal measurements in a subgroup and **longitudinal CV outcomes**.
  The strongest scientific validation ("do the oral representations associate with
  *incident* CV events?"), far stronger than cross-sectional correlation.
- **Linked EDR + EHR datasets** (Indiana Univ. ~28,908 patients; Rochester
  Epidemiology Project; Patel et al. 2026 linked model) — exactly our use case; the
  real-world target HISTORA represents; institutional access / DUA.
- **UK Biobank** — large, longitudinal, strong CV outcomes, but periodontal is
  **self-report proxies only** (no clinical probing) and access is application-gated.

---

## Sources

- NHANES: <https://www.cdc.gov/nchs/nhanes/> · 2009–2010 CRP codebook
  <https://wwwn.cdc.gov/nchs/nhanes/2009-2010/CRP_F.htm> · hs-CRP 2017–2018 (shows CRP
  cycle gap) <https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/HSCRP_J.htm>
- NHANES Oral Microbiome 2009–2012: <https://wwwn.cdc.gov/Nchs/Nhanes/Omp/Default.aspx>
  · documentation <https://wwwn.cdc.gov/nchs/data/nhanes/omp/OralMicrobiomeDataDocumentation-508.pdf>
- CRP ↔ periodontitis (NHANES 2009–2010): PMC10362674
- AHA statement (periodontal ↔ ASCVD, association not causation):
  <https://professional.heart.org/en/science-news/periodontal-disease-and-atherosclerotic-cardiovascular-disease/top-things-to-know>
- HOMD (Human Oral Microbiome Database): <https://www.homd.org/>
- Biobanks review (Frontiers Oral Health, 2026): froh.2026.1774868
- Synthea: <https://synthetichealth.github.io/synthea/> · OMOP on AWS:
  <https://registry.opendata.aws/synthea-omop/>
- BigMouth: <https://www.uth.edu/bigmouth/> · ARIC (BioLINCC):
  <https://biolincc.nhlbi.nih.gov/studies/aric/> · BRAR: Scientific Data
  s41597-025-06400-y · Linked EDR+EHR (Patel et al., 2026): JDR Clin & Transl Research
