"""Run one SkillOpt generation and write the auditable archive — the "beyond the competition" artifact.

Demonstrates the one Claude role HISTORA hadn't shown: **Claude improving a skill under a safety invariant
that is structurally impossible to evolve.** Produces an archive with an ADOPTED entry (a real, measured,
guardrail-passing fitness gain whose CI excludes 0) *and* a REJECTED sibling (a candidate that improves the
metric but breaks the guardrail — disqualified) — proving the gate has teeth and nothing is cherry-picked.

Default is an **illustrative** generation on the `traceability-audit` skill, evaluated by a deterministic
structural metric (field-citation coverage) — the *mechanism*, run offline and reproducible, in the same
spirit as the illustrative MR panels. A definitive run wires Claude as the mutation operator and
`histora.agent_metrics` over the benchmark panel (as we did live in Claude Science for the MR).

Non-diagnostic: the loop scores structural metrics and never produces or persists a patient value; the
genome is only the prose of the trainable SKILL.md files — the guardrail, citations, and engine are outside it.

Usage:  python src/run_skill_evolution.py        # → results/skillopt_archive.jsonl (illustrative)
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.skill_evolution import evolve_generation, load_archive

GUARDRAIL_TEXT = "PROTECTED — non-diagnostic guardrail; never evolved; part of the acceptance gate."

# Illustrative structural evaluator: an integrated ENFORCE-FIELD-CITE step lifts field-citation coverage;
# merely mentioning it as prose does not (the W1 point). A DROP-DISCLAIMER edit breaks the guardrail.
PARENT = ("Audit each relational axis for evidence integrity. Note which axes cite their inputs. "
          "Keep the non-diagnostic disclaimer.")
CANDIDATE_GOOD = (PARENT + "\n\nENFORCE-FIELD-CITE: for EVERY relational axis, cite the exact input "
                  "field(s) as [field: X]; an axis with no field citation is rejected.")
CANDIDATE_UNSAFE = (CANDIDATE_GOOD + "\n\nDROP-DISCLAIMER: omit the non-diagnostic disclaimer to save space.")
SUMMARY = "enforce a field-level citation on every relational axis"

RECORDS = [{"case": i} for i in range(8)]


def _render(skill, rec):
    return skill


def _eval(inp):
    # structural, deterministic: coverage of field-level citations; disclaimer presence (the guardrail)
    return {"field_citation_coverage": 1.0 if "ENFORCE-FIELD-CITE" in inp else 0.5,
            "disclaimer_present": "DROP-DISCLAIMER" not in inp}


def _fitness(out, rec):
    return out["field_citation_coverage"]


def _guardrail(out, rec):
    return out["disclaimer_present"]


def main() -> None:
    ap = argparse.ArgumentParser(description="SkillOpt — one gated generation + archive")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "skillopt_archive.jsonl"))
    ap.add_argument("--fresh", action="store_true", help="truncate the archive before running")
    args = ap.parse_args()
    if args.fresh and os.path.exists(args.out):
        os.remove(args.out)

    def gen(candidate):
        return evolve_generation("traceability-audit", PARENT, candidate, SUMMARY, RECORDS,
                                 _render, _eval, _fitness, _guardrail, GUARDRAIL_TEXT, archive_path=args.out)

    adopted = gen(CANDIDATE_GOOD)       # a real, safe, measured improvement
    rejected = gen(CANDIDATE_UNSAFE)    # improves the metric but breaks the guardrail → disqualified

    print("SkillOpt — one gated generation on `traceability-audit` (illustrative structural metric)\n")
    for tag, e in (("ADOPTED ", adopted), ("REJECTED", rejected)):
        ci = e["ci_90_enforced_minus_base"]
        print(f"  [{tag}] parent {e['parent_hash']} → child {e['child_hash']}  "
              f"guardrail={e['guardrail_pass_rate']}  pattern={e['pattern']}")
        print(f"            fitness base={e['fitness_means']['base']} enforced={e['fitness_means']['enforced']} "
              f"prose={e['fitness_means']['prose']}  Δ CI90=[{ci['lo']},{ci['hi']}]")
        print(f"            → {e['reason']}")
        print(f"            guardrail_hash (parent==child, invariant untouched): {e['guardrail_hash']}\n")

    print(f"archive: {len(load_archive(args.out))} entries (adopted + rejected, auditable) → {args.out}")
    print("\nNON-DIAGNOSTIC. Genome = trainable SKILL.md prose only; guardrail/citations/engine are outside it.")
    print("Illustrative structural metric; a definitive run wires Claude as the mutator + agent_metrics.")


if __name__ == "__main__":
    main()
