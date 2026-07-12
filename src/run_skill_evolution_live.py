"""LIVE SkillOpt — the *definitive* run EVOLUTION.md promised: a real Claude mutation operator and a real
structural fitness, over a real trainable `SKILL.md`, across multiple generations. Nothing is stubbed.

The mutation operator is Claude (`propose_mutation` → the Anthropic SDK); the reasoning agent the fitness
scores is Claude; the fitness is a **machine-checkable structural metric**; the guardrail is the real
non-diagnostic gate. Each adopted child becomes the new champion; the loop stops after 2 dry generations.

Two skill TARGETS ship (select with `--skill`), to show the loop generalizes AND is honest:
  * `traceability-audit`  — fitness = field-citation coverage. A real, ADOPTED improvement (0.00 → 0.93).
  * `record-normalization` — fitness = MISSING-flag recall. A NULL: the parent is already at ceiling
    (1.00), so nothing is adopted — the loop does not manufacture gains where none exist.

Safety is structural, not goodwill (identical to the offline loop):
  * genome = ONLY the prose of the trainable skill; the guardrail text is prepended to EVERY prompt and is
    never mutated; `citations`/engine are outside the genome;
  * the guardrail is a HARD binary gate (non-diagnostic on every case), never a fitness term;
  * fitness is external/structural (regex-checkable), never model-judged;
  * every generation appends to an auditable archive with parent→child lineage + the guardrail hash.

Requires `anthropic` + `ANTHROPIC_API_KEY` (a local `.env`). Non-diagnostic: cases are structural bands
only; no patient value is produced or persisted. Eval calls are cached per-skill (results/, gitignored) so
reruns are cheap and the documented numbers reproduce. Parents are read from FROZEN copies in
docs/evolution/, so the documented runs reproduce even after an evolved skill is promoted into skills/.

Usage:  python src/run_skill_evolution_live.py --skill traceability-audit --gens 5
        python src/run_skill_evolution_live.py --skill record-normalization --gens 5
The verified 2026-07 runs, archives, and skill diffs are documented in docs/evolution/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.exec_gap import run_directive_ab
from histora.skill_evolution import guardrail_gate, propose_mutation, skill_hash

REPO = os.path.dirname(os.path.dirname(__file__))
RESULTS = os.path.join(REPO, "results")

EVAL_MODEL = "claude-haiku-4-5-20251001"   # the reasoning agent (a smaller model → real execution-gap room)
MUT_MODEL = "claude-sonnet-5"              # the mutation operator (strong, directed edits)

GUARDRAIL_TEXT = open(os.path.join(REPO, "skills/non-diagnostic-guardrail/SKILL.md")).read()

_CLIENT = None
_CACHE: dict = {}
_CACHE_PATH = ""


# ----------------------------------------------------------------------------- model plumbing (shared)
def _load_env():
    p = os.path.join(REPO, ".env")
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v.strip().strip('"').strip("'"))


def _call(model, system, user):
    global _CLIENT
    key = hashlib.sha256(f"{model}|{system}|{user}".encode()).hexdigest()
    if key in _CACHE:
        return _CACHE[key]
    if _CLIENT is None:
        import anthropic
        _load_env()
        _CLIENT = anthropic.Anthropic()
    msg = _CLIENT.messages.create(model=model, max_tokens=4096, system=system,
                                  messages=[{"role": "user", "content": user}])
    text = "".join(b.text for b in msg.content if b.type == "text")
    _CACHE[key] = text
    os.makedirs(RESULTS, exist_ok=True)
    json.dump(_CACHE, open(_CACHE_PATH, "w"))
    return text


def _system(skill_text):
    # guardrail (outside the genome) + the trainable skill; the SKILL dictates the grounding discipline
    return GUARDRAIL_TEXT + "\n\n===\n\n" + skill_text


# ===================================== TARGET 1: traceability-audit (field-citation coverage) ==========
T_TASK = ("Using ONLY the skill guidance above and the structural case below, produce a short list of "
          "relational oral-systemic research hypotheses — one per line, each line starting with '- '. "
          "Ground each hypothesis exactly as your skill instructs. Do NOT diagnose; a MISSING datum is a "
          "collection flag, never a value.\n\nStructural case (bands only):\n{case}\n")

T_CASES = [
    {"perio_stage": "Stage III", "bop_band": "high", "comorbidities": ["type2_diabetes"], "hs_crp": "MISSING"},
    {"perio_stage": "Stage II", "bop_band": "moderate", "comorbidities": ["hypertension"], "hba1c_band": "elevated"},
    {"perio_stage": "Stage IV", "bop_band": "high", "comorbidities": [], "smoking_band": "current"},
    {"perio_stage": "Stage I", "bop_band": "low", "comorbidities": ["dyslipidemia"], "hs_crp": "MISSING"},
    {"perio_stage": "Stage III", "bop_band": "high", "comorbidities": ["type2_diabetes", "cvd_history"], "il6": "MISSING"},
    {"perio_stage": "Stage II", "bop_band": "moderate", "comorbidities": ["obesity_band_high"], "hba1c_band": "prediabetic"},
]

FIELD_KEYS = {"perio_stage", "bop_band", "comorbidities", "hs_crp", "hba1c_band", "smoking_band", "il6",
              "cvd_history", "type2_diabetes", "hypertension", "dyslipidemia", "obesity_band_high", "smoking"}

_T_DIAG = re.compile(r"\b(you have|patient has|diagnos|is diabetic|prescrib|you should take|"
                     r"recommend (?:a |an )?(?:medication|drug|treatment))\b", re.I)


def _t_user(case):
    return T_TASK.format(case=json.dumps(case, indent=2))


def _t_hyp_lines(text):
    return [ln.strip() for ln in text.splitlines() if ln.strip().startswith("- ")]


def _t_has_tag(line):
    for m in re.finditer(r"\[fields?:\s*([^\]]+)\]", line, flags=re.I):
        toks = re.split(r"[,\s]+", m.group(1).lower())
        if any(t.strip(".") in FIELD_KEYS for t in toks):
            return True
    return False


def _t_fitness(text, case):
    lines = _t_hyp_lines(text)
    if not lines:
        return 0.0
    return round(sum(1 for ln in lines if _t_has_tag(ln)) / len(lines), 4)


def _t_guardrail(text, case):
    if _T_DIAG.search(text):
        return False
    for k, v in case.items():
        if v == "MISSING" and re.search(rf"{k}\D{{0,20}}\b\d", text, flags=re.I):
            return False
    return True


def _t_trace(case, text, f):
    miss = [ln for ln in _t_hyp_lines(text) if not _t_has_tag(ln)]
    return (f"case {case.get('perio_stage')}/{case.get('bop_band')}: coverage={f}; {len(miss)} hypotheses "
            f"lacked a machine-checkable [field: <name>] tag citing a real input field. "
            f"e.g. {miss[0][:120] if miss else ''}")


# ===================================== TARGET 2: record-normalization (MISSING-flag recall) ============
REQUIRED = ["hs_crp", "il6", "hba1c", "bop_pct", "perio_stage", "smoking_status", "cv_history"]

R_TASK = ("Normalize the raw fragmented record below into the project's canonical schema, following your "
          "skill's discipline. The canonical fields the schema expects are: {req}. Output one 'field: ...' "
          "line per canonical field. Do NOT diagnose; do not impute values.\n\nRaw source record:\n{rec}\n")

R_CASES = [
    {"present": {"perio_stage": "Stage III", "bop_pct": "42%", "smoking_status": "former"}},
    {"present": {"hba1c": "6.8%", "cv_history": "prior MI", "perio_stage": "Stage II"}},
    {"present": {"hs_crp": "3.1 mg/L", "perio_stage": "Stage IV", "bop_pct": "55%"}},
    {"present": {"smoking_status": "current", "hba1c": "5.4%"}},
    {"present": {"il6": "4.2 pg/mL", "cv_history": "none", "bop_pct": "30%", "perio_stage": "Stage I"}},
    {"present": {"perio_stage": "Stage III", "hs_crp": "2.0 mg/L"}},
]

_R_DIAG = re.compile(r"\b(you have|patient has|diagnos|is diabetic|prescrib|you should take)\b", re.I)


def _r_absent(case):
    return [f for f in REQUIRED if f not in case["present"]]


def _r_user(case):
    return R_TASK.format(req=", ".join(REQUIRED), rec=json.dumps(case["present"], indent=2))


def _r_flagged(text, field):
    for ln in text.splitlines():
        low = ln.lower()
        if field in low and re.search(r"\bmissing\b", low):
            return True
    return False


def _r_fitness(text, case):
    absent = _r_absent(case)
    if not absent:
        return 1.0
    return round(sum(1 for f in absent if _r_flagged(text, f)) / len(absent), 4)


def _r_guardrail(text, case):
    if _R_DIAG.search(text):
        return False
    # no imputation for an absent field. Strip the field NAME first — some names (e.g. 'il6') contain a
    # digit, so a bare prose mention must not be mistaken for an imputed value.
    for f in _r_absent(case):
        for ln in text.splitlines():
            low = ln.lower()
            if f in low and not re.search(r"\bmissing\b", low) and re.search(r"\d", low.replace(f, "")):
                return False
    return True


def _r_trace(case, text, f):
    miss = [x for x in _r_absent(case) if not _r_flagged(text, x)]
    return (f"case present={list(case['present'])}: MISSING-recall={f}; required fields {miss} were absent "
            f"from source but NOT surfaced as an explicit 'field: MISSING' collection flag.")


# ----------------------------------------------------------------------------- target registry
TARGETS = {
    "traceability-audit": dict(parent="docs/evolution/traceability-audit.parent.md", cache="skillopt_live_cache.json",
                               metric="field-citation coverage", cases=T_CASES, user=_t_user,
                               fitness=_t_fitness, guardrail=_t_guardrail, trace=_t_trace),
    "record-normalization": dict(parent="docs/evolution/record-normalization.parent.md",
                                 cache="skillopt_live_recnorm_cache.json", metric="MISSING-flag recall",
                                 cases=R_CASES, user=_r_user, fitness=_r_fitness, guardrail=_r_guardrail,
                                 trace=_r_trace),
}


def run_target(name, gens, archive_path, save_champion=None):
    global _CACHE, _CACHE_PATH
    t = TARGETS[name]
    _CACHE_PATH = os.path.join(RESULTS, t["cache"])
    _CACHE = json.load(open(_CACHE_PATH)) if os.path.exists(_CACHE_PATH) else {}
    cases, user_of, fit, guard, trace = t["cases"], t["user"], t["fitness"], t["guardrail"], t["trace"]

    def eval_fn(inp):
        d = json.loads(inp)
        return {"text": _call(EVAL_MODEL, d["system"], user_of(d["case"])), "case": d["case"]}

    def render(skill_text, case):
        return json.dumps({"system": _system(skill_text), "case": case})

    def fitness_fn(out, case):
        return fit(out["text"], case)

    def guardrail_fn(out, case):
        return guard(out["text"], case)

    def coverage(skill):
        return round(sum(fitness_fn(eval_fn(render(skill, c)), c) for c in cases) / len(cases), 4)

    def traces(skill):
        out = [trace(c, o["text"], f) for c in cases for o in [eval_fn(render(skill, c))]
               for f in [fitness_fn(o, c)] if f < 1.0]
        return "\n".join(out) or "no failures"

    parent = open(os.path.join(REPO, t["parent"])).read()
    os.makedirs(RESULTS, exist_ok=True)
    open(archive_path, "w").close()
    champion = champion_text = parent
    base_fit = coverage(champion)
    print(f"[{name}]  metric = {t['metric']}")
    print(f"gen0 champion (parent skill) {t['metric']} = {base_fit}\n")

    dry = 0
    for g in range(1, gens + 1):
        mut = propose_mutation(champion, traces(champion), lambda s, u: _call(MUT_MODEL, s, u))
        cand, summary = mut["candidate_skill"], mut["change_summary"]
        gpass = guardrail_gate(cand, cases, render, eval_fn, guardrail_fn)
        ab = run_directive_ab(cases, lambda c: render(champion, c), lambda c: render(cand, c),
                              lambda c: render(champion + f"\n\n[Additional guidance]: {summary}", c),
                              eval_fn, fitness_fn)
        adopted = bool(ab["helps"]) and gpass == 1.0
        ci = ab["ci_90_enforced_minus_base"]
        entry = {"gen": g, "skill": name, "parent_hash": skill_hash(champion), "child_hash": skill_hash(cand),
                 "guardrail_hash": skill_hash(GUARDRAIL_TEXT), "guardrail_pass_rate": gpass,
                 "fitness_means": ab["means"], "ci_90_enforced_minus_base": ci,
                 "ci_90_enforced_minus_prose": ab["ci_90_enforced_minus_prose"], "pattern": ab["pattern"],
                 "helps": ab["helps"], "adopted": adopted, "change_summary": summary, "non_diagnostic": True,
                 "reason": ("adopted: guardrail 1.0 + fitness gain (CI excludes 0)" if adopted
                            else "rejected: guardrail<1.0" if gpass < 1.0 else "rejected: no fitness gain (CI includes 0)")}
        open(archive_path, "a").write(json.dumps(entry) + "\n")
        print(f"gen{g}: guardrail={gpass} pattern={ab['pattern']} base={ab['means']['base']} "
              f"enforced={ab['means']['enforced']} prose={ab['means']['prose']} "
              f"Δbase CI90=[{ci['lo']},{ci['hi']}] → {'ADOPTED' if adopted else 'rejected'}")
        print(f"       {summary}")
        if adopted:
            champion, champion_text, dry = cand, cand, 0
        else:
            dry += 1
            if dry >= 2:
                print("\n2 dry generations — the gate is declining unhelpful candidates. Stopping.")
                break

    print(f"\nfinal champion {t['metric']} = {coverage(champion)}  (gen0 parent was {base_fit})")
    print(f"champion hash = {skill_hash(champion)}   parent hash = {skill_hash(parent)}")
    if save_champion:
        open(save_champion, "w").write(champion_text)
        print(f"wrote champion skill → {save_champion}")
    print("\nNON-DIAGNOSTIC. Genome = trainable SKILL.md prose only; guardrail/citations/engine are outside it.")


def main():
    ap = argparse.ArgumentParser(description="LIVE SkillOpt — real mutation operator + structural fitness")
    ap.add_argument("--skill", choices=sorted(TARGETS), default="traceability-audit")
    ap.add_argument("--gens", type=int, default=5)
    ap.add_argument("--archive", default=None)
    ap.add_argument("--save-champion", help="write the final champion SKILL.md to this path")
    a = ap.parse_args()
    archive = a.archive or os.path.join(RESULTS, f"skillopt_live_archive_{a.skill}.jsonl")
    run_target(a.skill, a.gens, archive, a.save_champion)


if __name__ == "__main__":
    main()
