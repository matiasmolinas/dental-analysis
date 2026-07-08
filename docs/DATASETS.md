# Datasets

Real and synthetic data sources for the HISTORA oral-systemic project, why each was
chosen, how it maps to our schema, and its limitations. Decision:

> **Primary real anchor: NHANES 2009–2010** (public, de-identified, downloadable).
> **Longitudinal / shareable demo data: Synthea** with a custom periodontal module.
> Both are non-PHI. Real linked EDR+EHR datasets and UK Biobank are named as the
> real-world target/validation but are access-gated and not used in the event.

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
codebook. The mapping is encoded in [`../src/nhanes_mapping.py`](../src/nhanes_mapping.py);
a documented download + case-builder is in [`../src/nhanes_loader.py`](../src/nhanes_loader.py)
(reads XPT via `pandas.read_sas`, no extra deps).

### Uses in the project

- Ground the synthetic case values in real distributions (replace invented numbers).
- Validate that our agent's relational axes match known epidemiology.
- **Reproducible mini-analysis (Research-track flavor):** replicate the
  CRP ↔ periodontitis association/mediation on 2009–2010.

### Limitations

- **Cross-sectional** — no per-patient longitudinal progression (our
  `ppd_18m_ago_mm` field has no NHANES source). Use Synthea for progression.
- Survey/exam data, not integrated per-patient clinical narratives — we assemble
  the narrative; NHANES supplies grounded values.
- LDL only on the fasting subsample; CRP is standard, not high-sensitivity.

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

## 3. Named but not used (access-gated)

- **Linked EDR + EHR datasets** (Indiana Univ. ~28,908 patients; Rochester
  Epidemiology Project; Patel et al. 2026 linked model) — exactly our use case
  (real linked dental+medical longitudinal), but institutional access / DUA
  required. These are the real-world target HISTORA represents and future
  validation partners.
- **UK Biobank** — large, longitudinal, strong CV outcomes, but periodontal is
  **self-report proxies only** (no clinical probing) and access is application-gated.

---

## Sources

- NHANES: <https://www.cdc.gov/nchs/nhanes/> · 2009–2010 CRP codebook
  <https://wwwn.cdc.gov/nchs/nhanes/2009-2010/CRP_F.htm>
- CRP ↔ periodontitis (NHANES 2009–2010): PMC10362674
- Biobanks review (Frontiers Oral Health, 2026): froh.2026.1774868
- Synthea: <https://synthetichealth.github.io/synthea/> · OMOP on AWS:
  <https://registry.opendata.aws/synthea-omop/>
- Linked EDR+EHR model (Patel et al., 2026): JDR Clinical & Translational Research
