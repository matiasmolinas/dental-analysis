"""Download NHANES 2009-2010 XPT files and build a grounded case record.

Reads XPT with ``pandas.read_sas`` (no pyreadstat needed). Network + pandas are
required only at call time; importing this module has no side effects, so it
compiles and imports without them.

This produces values grounded in real NHANES participants to replace invented
numbers in ``record_formats.py``. Longitudinal fields (e.g. prior-visit PPD) have
no NHANES source — use Synthea for progression (see docs/DATASETS.md).

Example:
    from nhanes_loader import download_files, build_case
    paths = download_files("data/nhanes")           # one-time
    case = build_case(paths, seqn=None)             # a random eligible participant
"""

from __future__ import annotations

import os
from typing import Any

from nhanes_mapping import JOIN_KEY, NHANES_BASE_URL, NHANES_FILES


def download_files(dest_dir: str) -> dict[str, str]:
    """Download the needed NHANES 2009-2010 XPT files into ``dest_dir``.

    Returns ``{file_stem: local_path}``. Requires network access.
    """
    import urllib.request

    os.makedirs(dest_dir, exist_ok=True)
    paths: dict[str, str] = {}
    for stem in NHANES_FILES:
        url = f"{NHANES_BASE_URL}/{stem}.XPT"
        local = os.path.join(dest_dir, f"{stem}.XPT")
        if not os.path.exists(local):
            urllib.request.urlretrieve(url, local)
        paths[stem] = local
    return paths


def load_joined(paths: dict[str, str]) -> Any:
    """Load and inner/outer-join all files on SEQN into one DataFrame.

    Requires pandas. Periodontal per-site fields are left raw for the caller to
    aggregate (mean PPD / CAL / %BOP) per the OHXPER_F codebook.
    """
    import pandas as pd

    merged = None
    for stem, path in paths.items():
        df = pd.read_sas(path, format="xport")
        if JOIN_KEY not in df.columns:
            continue
        merged = df if merged is None else merged.merge(df, on=JOIN_KEY, how="left")
    if merged is None:
        raise ValueError("no file contained the SEQN join key")
    return merged


def build_case(paths: dict[str, str], *, seqn: int | None = None) -> dict:
    """Build one schema-shaped case dict from a NHANES participant row.

    ``seqn=None`` picks the first participant with non-null CRP, HbA1c, and a
    periodontal record. This is a scaffold: fill the periodontal aggregation and
    unit conversions against the OHXPER_F codebook before using in analysis.
    """
    df = load_joined(paths)
    # Prefer rows with the mediating markers present so the inflammatory axis is real.
    for col in ("LBXCRP", "LBXGH"):
        if col in df.columns:
            df = df[df[col].notna()]
    if seqn is not None:
        df = df[df[JOIN_KEY] == seqn]
    if len(df) == 0:
        raise ValueError("no eligible participant found for the given filters")
    row = df.iloc[0]

    def g(col: str):
        return None if col not in row or row[col] != row[col] else row[col]  # NaN-safe

    return {
        "provenance": {"source": "NHANES 2009-2010", "seqn": g(JOIN_KEY)},
        "demographics": {"age": g("RIDAGEYR"), "sex": g("RIAGENDR"), "bmi": g("BMXBMI")},
        "shared_risk": {"hba1c": g("LBXGH")},
        "medical_cv": {
            "hs_crp": g("LBXCRP"),
            "ldl": g("LBDLDL"),
            "hdl": g("LBDHDD"),
            "triglycerides": g("LBXTR"),
            "total_cholesterol": g("LBXTC"),
        },
        # periodontal.* requires aggregating OHXPER_F per-site fields (TODO: codebook).
        "periodontal": {"_note": "aggregate OHXPER_F per-site PPD/CAL/BOP"},
    }
