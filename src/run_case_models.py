"""Harness tool CLI — mechanistic predictions for one case (the model backend of the plugin).

Reads an integrated oral+systemic record (JSON from --record PATH, or stdin, or the built-in grounded
case) and prints the non-diagnostic mechanistic prediction block: systemic (IL-6/CRP), CV, neuro,
counterfactual levers, and ranges over the swept uncertain parameters. Offline (no API/GPU).

Usage:
  python src/run_case_models.py --record case.json
  cat case.json | python src/run_case_models.py
  python src/run_case_models.py            # the built-in NHANES-grounded case
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.case_tools import case_mechanistic_predictions
from histora.record_formats import RECORD


def main() -> None:
    ap = argparse.ArgumentParser(description="Mechanistic predictions for one oral-systemic case")
    ap.add_argument("--record", help="path to a record JSON; omit to read stdin or use the built-in case")
    ap.add_argument("--n", type=int, default=200, help="ensemble samples for the ranges")
    args = ap.parse_args()

    if args.record:
        with open(args.record) as f:
            record = json.load(f)
    elif not sys.stdin.isatty():
        data = sys.stdin.read().strip()
        record = json.loads(data) if data else RECORD
    else:
        record = RECORD

    print(json.dumps(case_mechanistic_predictions(record, n_ensemble=args.n), indent=2))


if __name__ == "__main__":
    main()
