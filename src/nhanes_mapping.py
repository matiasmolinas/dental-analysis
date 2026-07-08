"""Mapping from our record schema to NHANES 2009-2010 files and variables.

NHANES 2009-2010 is the primary real anchor (public, de-identified, downloadable):
the full-mouth periodontal exam coexists with CRP, HbA1c, lipids, BP, smoking, and
CV history in this cycle. See docs/DATASETS.md.

Files use the 2009-2010 `_F` suffix. Per-site periodontal variable names must be
confirmed against the OHXPER_F codebook; here we record the file and the derived
measures we compute from it.
"""

from __future__ import annotations

# NHANES 2009-2010 XPT base URL (each file is <NAME>.XPT).
NHANES_BASE_URL = "https://wwwn.cdc.gov/Nchs/Nhanes/2009-2010"

# NHANES Oral Microbiome (2009-2010 + 2011-2012): oral-rinse ASVs, alpha/beta
# diversity, and genus-level abundance tables, SEQN-linkable to the periodontal exam
# and phenotype. In 2009-2010 it overlaps with the full-mouth periodontal exam AND
# CRP in the same participants -> a real, reproducible mediator chain
# (periodontal -> oral microbiome -> systemic inflammation -> CV risk). See docs/DATASETS.md.
NHANES_OMP_URL = "https://wwwn.cdc.gov/Nchs/Nhanes/Omp/Default.aspx"

# schema path -> (NHANES file without extension, variable code(s), note)
SCHEMA_TO_NHANES: dict[str, tuple[str, tuple[str, ...], str]] = {
    "demographics.age": ("DEMO_F", ("RIDAGEYR",), "age in years"),
    "demographics.sex": ("DEMO_F", ("RIAGENDR",), "1=male, 2=female"),
    "demographics.bmi": ("BMX_F", ("BMXBMI",), "kg/m^2"),
    # Periodontal: derive mean PPD and CAL from per-site probing/attachment fields.
    "periodontal.mean_ppd_mm": ("OHXPER_F", ("OHXxxPCx",), "derive mean of per-site probing depth"),
    "periodontal.cal_mm": ("OHXPER_F", ("OHXxxLAx",), "derive mean of per-site attachment loss"),
    "periodontal.bop_pct": ("OHXPER_F", ("OHXxxBP",), "percent sites with bleeding on probing"),
    # Inflammatory mediator (the bridge to cardiovascular risk).
    "medical_cv.hs_crp": ("CRP_F", ("LBXCRP",), "C-reactive protein mg/dL (standard, not hs)"),
    "shared_risk.hba1c": ("GHB_F", ("LBXGH",), "glycohemoglobin %"),
    "shared_risk.type2_diabetes": ("DIQ_F", ("DIQ010",), "1=yes ever told diabetes"),
    "medical_cv.ldl": ("TRIGLY_F", ("LBDLDL",), "LDL mg/dL, fasting subsample"),
    "medical_cv.hdl": ("HDL_F", ("LBDHDD",), "HDL mg/dL"),
    "medical_cv.triglycerides": ("TRIGLY_F", ("LBXTR",), "triglycerides mg/dL, fasting subsample"),
    "medical_cv.total_cholesterol": ("TCHOL_F", ("LBXTC",), "total cholesterol mg/dL"),
    "shared_risk.blood_pressure_sys": ("BPX_F", ("BPXSY1",), "systolic mmHg (1st reading)"),
    "shared_risk.blood_pressure_dia": ("BPX_F", ("BPXDI1",), "diastolic mmHg (1st reading)"),
    "shared_risk.smoking_status": ("SMQ_F", ("SMQ020", "SMD030"), "ever/onset smoking; COT_F cotinine corroborates"),
    "medical_cv.medications": ("RXQ_RX_F", ("RXDDRUG",), "prescription medication names"),
    "medical_cv.prior_cv_event": ("MCQ_F", ("MCQ160C", "MCQ160E", "MCQ160F"), "CHD / MI / stroke ever"),
    "medical_cv.family_history_mi": ("MCQ_F", ("MCQ300A",), "close relative had heart attack"),
    # Mediator layer: oral microbiome (separate OMP files, not the 2009-2010 XPT set).
    "mediators.oral_microbiome": ("OMP_2009-2012", ("alpha_diversity", "genus_abundance"),
                                  "oral-rinse ASVs; SEQN-linkable; see NHANES_OMP_URL"),
}

# Unique standard 2009-2010 XPT files to download for a full case (join on SEQN).
# The oral-microbiome layer (OMP_*) is hosted separately (NHANES_OMP_URL) and is
# excluded here so the XPT loader does not try to fetch it as an .XPT.
NHANES_FILES = sorted(
    {f for f, _, _ in SCHEMA_TO_NHANES.values() if not f.startswith("OMP")}
)

JOIN_KEY = "SEQN"  # NHANES respondent sequence number; join all files on this.
