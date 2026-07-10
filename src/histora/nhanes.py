"""NHANES data access — mapping + loaders for the two cycles the project uses.

Public, de-identified NHANES:
  * **2009-2010** (`_F`): the periodontal + cardiovascular + inflammatory (CRP) anchor.
  * **2011-2012** (`_G`): the periodontal + COGNITIVE battery (CERAD / Animal Fluency / Digit Symbol)
    — the oral↔neuro empirical anchor.

Importing this module has no side effects; network + pandas are needed only at call time. All data is
population-level and de-identified — nothing here is patient-diagnostic.
"""

from __future__ import annotations

import os
import re
from typing import Any

# ------------------------------------------------------------------- 2009-2010 (CV + inflammation)
NHANES_BASE_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles"
NHANES_OMP_URL = "https://wwwn.cdc.gov/Nchs/Nhanes/Omp/Default.aspx"  # oral-microbiome mediator layer
JOIN_KEY = "SEQN"

# schema path -> (NHANES file without extension, variable code(s), note)
SCHEMA_TO_NHANES: dict[str, tuple[str, tuple[str, ...], str]] = {
    "demographics.age": ("DEMO_F", ("RIDAGEYR",), "age in years"),
    "demographics.sex": ("DEMO_F", ("RIAGENDR",), "1=male, 2=female"),
    "demographics.bmi": ("BMX_F", ("BMXBMI",), "kg/m^2"),
    "periodontal.mean_ppd_mm": ("OHXPER_F", ("OHXxxPCx",), "derive mean of per-site probing depth"),
    "periodontal.cal_mm": ("OHXPER_F", ("OHXxxLAx",), "derive mean of per-site attachment loss"),
    "periodontal.bop_pct": ("OHXPER_F", ("OHXxxBP",), "percent sites with bleeding on probing"),
    "medical_cv.hs_crp": ("CRP_F", ("LBXCRP",), "C-reactive protein mg/dL"),
    "shared_risk.hba1c": ("GHB_F", ("LBXGH",), "glycohemoglobin %"),
    "shared_risk.type2_diabetes": ("DIQ_F", ("DIQ010",), "1=yes ever told diabetes"),
    "medical_cv.ldl": ("TRIGLY_F", ("LBDLDL",), "LDL mg/dL, fasting subsample"),
    "medical_cv.hdl": ("HDL_F", ("LBDHDD",), "HDL mg/dL"),
    "medical_cv.triglycerides": ("TRIGLY_F", ("LBXTR",), "triglycerides mg/dL, fasting subsample"),
    "medical_cv.total_cholesterol": ("TCHOL_F", ("LBXTC",), "total cholesterol mg/dL"),
    "shared_risk.blood_pressure_sys": ("BPX_F", ("BPXSY1",), "systolic mmHg"),
    "shared_risk.blood_pressure_dia": ("BPX_F", ("BPXDI1",), "diastolic mmHg"),
    "shared_risk.smoking_status": ("SMQ_F", ("SMQ020", "SMD030"), "ever/onset smoking"),
    "medical_cv.medications": ("RXQ_RX_F", ("RXDDRUG",), "prescription medication names"),
    "medical_cv.prior_cv_event": ("MCQ_F", ("MCQ160C", "MCQ160E", "MCQ160F"), "CHD / MI / stroke ever"),
    "medical_cv.family_history_mi": ("MCQ_F", ("MCQ300A",), "close relative had heart attack"),
    "mediators.oral_microbiome": ("OMP_2009-2012", ("alpha_diversity", "genus_abundance"),
                                  "oral-rinse ASVs; SEQN-linkable; see NHANES_OMP_URL"),
}
NHANES_FILES = sorted({f for f, _, _ in SCHEMA_TO_NHANES.values() if not f.startswith("OMP")})

# ------------------------------------------------------------------- 2011-2012 (perio + cognition)
# The 2009-2010 CV cycle has NO cognition module; the 2011-2014 cognition cycles have NO CRP (standard
# CRP was discontinued after 2009-2010; hs-CRP returns only in 2015-2016). So NO single public cycle
# carries periodontal + CRP + cognition — the neuro data work is a population-level perio<->cognition
# ASSOCIATION; the inflammatory MEDIATOR is the modeled hypothesis, not a measured per-participant chain.
NHANES_NEURO_BASE_URL_2011 = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles"

SCHEMA_TO_NHANES_NEURO: dict[str, tuple[str, tuple[str, ...], str]] = {
    "cognition.cerad_word_learning": ("CFQ_G", ("CFDCST1", "CFDCST2", "CFDCST3"),
                                      "CERAD immediate word-learning trials 1-3 total"),
    "cognition.cerad_delayed_recall": ("CFQ_G", ("CFDCSR",), "CERAD delayed recall total"),
    "cognition.animal_fluency": ("CFQ_G", ("CFDAST",), "Animal Fluency total score"),
    "cognition.digit_symbol": ("CFQ_G", ("CFDDS",), "Digit Symbol Substitution score"),
    "periodontal.mean_ppd_mm_2011": ("OHXPER_G", ("OHXxxPCx",), "mean per-site probing depth (2011-12)"),
    "periodontal.cal_mm_2011": ("OHXPER_G", ("OHXxxLAx",), "mean per-site attachment loss (2011-12)"),
    "shared_risk.hba1c_2011": ("GHB_G", ("LBXGH",), "glycohemoglobin % (2011-12)"),
    "shared_risk.smoking_status_2011": ("SMQ_G", ("SMQ020", "SMD030"), "ever/onset smoking (2011-12)"),
    "demographics.age_2011": ("DEMO_G", ("RIDAGEYR",), "age — dominant cognition/perio confounder"),
    "demographics.education_2011": ("DEMO_G", ("DMDEDUC2",), "education — key cognition confounder"),
}
NHANES_NEURO_FILES = sorted({f for f, _, _ in SCHEMA_TO_NHANES_NEURO.values()})

_LA_RE = re.compile(r"^OHX\d{2}LA[A-Z]$")   # per-site loss of attachment (mm)
_PC_RE = re.compile(r"^OHX\d{2}PC[A-Z]$")   # per-site pocket depth (mm)


# --------------------------------------------------------------------------- download helpers
def _is_xport(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(6) == b"HEADER"
    except OSError:
        return False


def _download(stems: list[str], base_url: str, dest_dir: str, timeout: int = 90) -> dict[str, str]:
    import urllib.request

    os.makedirs(dest_dir, exist_ok=True)
    paths: dict[str, str] = {}
    for stem in stems:
        local = os.path.join(dest_dir, f"{stem}.XPT")
        if not _is_xport(local):  # (re)download if absent or a poisoned HTML soft-404
            req = urllib.request.Request(f"{base_url}/{stem}.xpt",
                                         headers={"User-Agent": "HISTORA NHANES loader"})
            with urllib.request.urlopen(req, timeout=timeout) as r, open(local, "wb") as f:
                f.write(r.read())
            if not _is_xport(local):
                raise ValueError(f"{stem}: downloaded file is not an XPORT (CDC soft-404?)")
        paths[stem] = local
    return paths


def download_files(dest_dir: str) -> dict[str, str]:
    """Download the 2009-2010 (CV/inflammation) XPT files. Requires network."""
    return _download(NHANES_FILES, NHANES_BASE_URL, dest_dir, timeout=60)


def download_neuro_files(dest_dir: str) -> dict[str, str]:
    """Download the 2011-2012 (perio + cognition) XPT files. Requires network."""
    return _download(NHANES_NEURO_FILES, NHANES_NEURO_BASE_URL_2011, dest_dir)


def _load_joined(paths: dict[str, str], how: str = "left") -> Any:
    import pandas as pd

    merged = None
    for _, path in paths.items():
        df = pd.read_sas(path, format="xport")
        if JOIN_KEY not in df.columns:
            continue
        merged = df if merged is None else merged.merge(df, on=JOIN_KEY, how=how)
    if merged is None:
        raise ValueError("no file contained the SEQN join key")
    return merged


# --------------------------------------------------------------------------- 2009-2010 case builder
def build_case(paths: dict[str, str], *, seqn: int | None = None) -> dict:
    """Build one schema-shaped case dict from a NHANES 2009-2010 participant row (CV anchor).
    `seqn=None` picks the first participant with non-null CRP + HbA1c."""
    df = _load_joined(paths)
    for col in ("LBXCRP", "LBXGH"):
        if col in df.columns:
            df = df[df[col].notna()]
    if seqn is not None:
        df = df[df[JOIN_KEY] == seqn]
    if len(df) == 0:
        raise ValueError("no eligible participant found for the given filters")
    row = df.iloc[0]

    def g(col):
        return None if col not in row or row[col] != row[col] else row[col]

    return {
        "provenance": {"source": "NHANES 2009-2010", "seqn": g(JOIN_KEY)},
        "demographics": {"age": g("RIDAGEYR"), "sex": g("RIAGENDR"), "bmi": g("BMXBMI")},
        "shared_risk": {"hba1c": g("LBXGH")},
        "medical_cv": {"hs_crp": g("LBXCRP"), "ldl": g("LBDLDL"), "hdl": g("LBDHDD"),
                       "triglycerides": g("LBXTR"), "total_cholesterol": g("LBXTC")},
        "periodontal": {"_note": "aggregate OHXPER_F per-site PPD/CAL/BOP against the codebook"},
    }


# --------------------------------------------------------------------------- 2011-2012 neuro table
def _mean_plausible(row, cols, lo, hi):
    vals = [row[c] for c in cols if c in row and row[c] == row[c] and lo <= row[c] <= hi]
    return sum(vals) / len(vals) if vals else None


def _plausible(v, lo, hi):
    return v if (v is not None and v == v and lo <= v <= hi) else None


def load_neuro_table(paths: dict[str, str]) -> list[dict[str, Any]]:
    """Join the 2011-2012 files on SEQN and derive the perio↔cognition analysis records. Periodontal
    severity is derived defensively by column-pattern matching (per-site OHX##LA#/OHX##PC# averaged
    over plausible mm). Missing → None. Requires pandas."""
    merged = _load_joined(paths, how="outer")
    la_cols = [c for c in merged.columns if _LA_RE.match(c)]
    pc_cols = [c for c in merged.columns if _PC_RE.match(c)]

    records = []
    for _, row in merged.iterrows():
        def g(col):
            return None if col not in row or row[col] != row[col] else float(row[col])

        cst = [_plausible(g(c), 0, 10) for c in ("CFDCST1", "CFDCST2", "CFDCST3")]
        cerad_immediate = sum(cst) if all(v is not None for v in cst) else None
        smoke = g("SMQ020")  # 1=yes ever, 2=no
        records.append({
            "seqn": g(JOIN_KEY),
            "perio_cal": _mean_plausible(row, la_cols, 0, 20),
            "perio_ppd": _mean_plausible(row, pc_cols, 0, 20),
            "cerad_immediate": cerad_immediate,
            "cerad_delayed": _plausible(g("CFDCSR"), 0, 10),
            "animal_fluency": _plausible(g("CFDAST"), 0, 60),
            "digit_symbol": _plausible(g("CFDDS"), 0, 120),
            "age": _plausible(g("RIDAGEYR"), 0, 130),
            "education": _plausible(g("DMDEDUC2"), 1, 5),
            "smoking": (1.0 if smoke == 1 else 0.0 if smoke == 2 else None),
            "hba1c": _plausible(g("LBXGH"), 3, 20),
        })
    return records
