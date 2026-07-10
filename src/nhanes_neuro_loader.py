"""Download NHANES 2011-2012 (_G) files and build the perio↔cognition analysis table (Track 2).

Fetches the Cognitive Functioning module (CFQ_G: CERAD, Animal Fluency, Digit Symbol) + the
full-mouth periodontal exam (OHXPER_G) + confounders (DEMO_G age/education, SMQ_G smoking, GHB_G
HbA1c), joins on SEQN, and derives a clean per-participant table for `perio_cognition.analyze`.

Periodontal severity is derived DEFENSIVELY by column-pattern matching (per-site loss-of-attachment
`OHX##LA#` and pocket-depth `OHX##PC#` variables averaged over plausible values), so it does not
hardcode the ~168 site-variable names. Network + pandas required only at call time; importing has no
side effects. Non-diagnostic (population data).
"""

from __future__ import annotations

import os
import re
from typing import Any

from nhanes_mapping import JOIN_KEY, NHANES_NEURO_BASE_URL_2011, NHANES_NEURO_FILES

_LA_RE = re.compile(r"^OHX\d{2}LA[A-Z]$")   # per-site loss of attachment (mm)
_PC_RE = re.compile(r"^OHX\d{2}PC[A-Z]$")   # per-site pocket depth (mm)


def _is_xport(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(6) == b"HEADER"
    except OSError:
        return False


def download_neuro_files(dest_dir: str) -> dict[str, str]:
    """Download the 2011-2012 XPT files into dest_dir. Returns {stem: path}. Requires network."""
    import urllib.request

    os.makedirs(dest_dir, exist_ok=True)
    paths: dict[str, str] = {}
    for stem in NHANES_NEURO_FILES:
        url = f"{NHANES_NEURO_BASE_URL_2011}/{stem}.xpt"
        local = os.path.join(dest_dir, f"{stem}.XPT")
        if not _is_xport(local):
            req = urllib.request.Request(url, headers={"User-Agent": "dental-analysis NHANES loader"})
            with urllib.request.urlopen(req, timeout=90) as r, open(local, "wb") as f:
                f.write(r.read())
            if not _is_xport(local):
                raise ValueError(f"{stem}: downloaded file is not an XPORT (CDC soft-404?): {url}")
        paths[stem] = local
    return paths


def _mean_plausible(row, cols, lo: float, hi: float):
    """Mean of the row's values across `cols` that fall in [lo, hi] (mm); None if none plausible."""
    vals = [row[c] for c in cols if c in row and row[c] == row[c] and lo <= row[c] <= hi]
    return sum(vals) / len(vals) if vals else None


def _plausible(v, lo: float, hi: float):
    return v if (v is not None and v == v and lo <= v <= hi) else None


def load_neuro_table(paths: dict[str, str]) -> list[dict[str, Any]]:
    """Join the files on SEQN and derive the analysis records. Each record has: seqn, perio_cal,
    perio_ppd (mm, mean over plausible sites), cerad_immediate (0-30), cerad_delayed (0-10),
    animal_fluency, digit_symbol, age, education (1-5), smoking (1 ever / 0 never), hba1c. Missing →
    None. Requires pandas."""
    import pandas as pd

    merged = None
    for stem, path in paths.items():
        df = pd.read_sas(path, format="xport")
        if JOIN_KEY not in df.columns:
            continue
        merged = df if merged is None else merged.merge(df, on=JOIN_KEY, how="outer")
    if merged is None:
        raise ValueError("no file contained the SEQN join key")

    la_cols = [c for c in merged.columns if _LA_RE.match(c)]
    pc_cols = [c for c in merged.columns if _PC_RE.match(c)]

    records = []
    for _, row in merged.iterrows():
        def g(col):
            return None if col not in row or row[col] != row[col] else float(row[col])

        # cognition (filter NHANES refused/dk codes via plausible ranges)
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
