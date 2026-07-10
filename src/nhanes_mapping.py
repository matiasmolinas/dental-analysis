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
# CDC restructured NHANES download URLs in 2024; the old /Nchs/Nhanes/2009-2010/ path
# now serves a soft-404 HTML page. Files live under /Nchs/Data/Nhanes/Public/<year>/DataFiles/.
NHANES_BASE_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles"

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


# ---------------------------------------------------------------------------------------------
# Neuro axis (oral <-> Alzheimer) — NHANES 2011-2012 (_G). The COGNITIVE FUNCTIONING module (CFQ)
# — CERAD Word Learning, Animal Fluency, Digit Symbol — coexists with the full-mouth periodontal
# exam (OHXPER) in the SAME participants (SEQN-linkable), giving the oral<->neuro empirical anchor
# the CV axis has via 2009-2010.
#
# HONEST DATA CAVEATS (documented, not worked around):
#   * The 2009-2010 CV-anchor cycle has NO cognition module; the 2011-2014 cognition cycles have NO
#     CRP (standard CRP was discontinued after 2009-2010; hs-CRP returns only in 2015-2016, HSCRP_I).
#     So NO single public NHANES cycle carries periodontal + CRP + cognition together. The
#     inflammation MEDIATOR (which mech_neuro models) is therefore not measurable in-cycle with
#     cognition — the neuro data work is a population-level periodontal<->cognition ASSOCIATION
#     (the mechanistic mediation is a modeled hypothesis, not a measured per-participant chain).
#   * NHANES-III (1988-1994) additionally carries serum P. gingivalis IgG + cognition (Noble 2009),
#     a different file structure — a second, cross-cycle option, not wired here.
NHANES_NEURO_BASE_URL_2011 = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles"

SCHEMA_TO_NHANES_NEURO: dict[str, tuple[str, tuple[str, ...], str]] = {
    "cognition.cerad_word_learning": ("CFQ_G", ("CFDCST1", "CFDCST2", "CFDCST3"),
                                      "CERAD immediate word-learning trials 1-3 total"),
    "cognition.cerad_delayed_recall": ("CFQ_G", ("CFDCSR",), "CERAD delayed recall total"),
    "cognition.animal_fluency": ("CFQ_G", ("CFDAST",), "Animal Fluency total score"),
    "cognition.digit_symbol": ("CFQ_G", ("CFDDS",), "Digit Symbol Substitution score"),
    # periodontal exam IN THE SAME CYCLE so perio <-> cognition are SEQN-linkable per participant
    "periodontal.mean_ppd_mm_2011": ("OHXPER_G", ("OHXxxPCx",),
                                     "derive mean per-site probing depth (2011-2012)"),
    "periodontal.cal_mm_2011": ("OHXPER_G", ("OHXxxLAx",),
                               "derive mean per-site attachment loss (2011-2012)"),
    # shared risk factors available in-cycle (confounders to adjust for in any association)
    "shared_risk.hba1c_2011": ("GHB_G", ("LBXGH",), "glycohemoglobin % (2011-2012)"),
    "shared_risk.smoking_status_2011": ("SMQ_G", ("SMQ020", "SMD030"), "ever/onset smoking (2011-2012)"),
    "demographics.age_2011": ("DEMO_G", ("RIDAGEYR",), "age — the dominant cognition/perio confounder"),
    "demographics.education_2011": ("DEMO_G", ("DMDEDUC2",), "education — key cognition confounder"),
}

# Unique 2011-2012 XPT files for the neuro (perio + cognition + confounders) join.
NHANES_NEURO_FILES = sorted({f for f, _, _ in SCHEMA_TO_NHANES_NEURO.values()})
