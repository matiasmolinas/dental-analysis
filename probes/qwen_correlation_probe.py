"""Scoped Qwen measured-lens correlation probe (Phase R6 next-step #5) — GPU / offline only.

NOT part of the Claude-only runtime. This is the one bounded experiment from
docs/analysis/measured-qwen-lens-contradiction-and-colab.md §Q3: does our inferred self-report
correlate with a MEASURED workspace on a proxy? It converts the project's central "we have no
ground truth" caveat (APPROACH.md §8) into a measured (proxy-limited) data point.

Deliverable = epistemic hygiene, explicitly NOT optimization. A positive licenses "the self-report
is a faithful proxy (on Qwen)"; a negative licenses leaning on behavioral corroboration. It CANNOT
cross the transfer gap to Claude (it measures Qwen), and it only reads SINGLE-TOKEN surfaces — so on
our multi-token mediators it is blinder than the verbal self-report it validates. Read those limits
in the companion doc before trusting a result.

Requirements (Colab T4 is enough — inference only, no fitting):
    pip install -e ../jacobian-lens transformers torch scipy
Uses the pre-fitted Hub lens `neuronpedia/jacobian-lens` @ `qwen-n1000` for `Qwen/Qwen3.5-4B`.

Run:  python probes/qwen_correlation_probe.py
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bridge_concepts import BRIDGE_CONCEPTS, MEDIATOR_KEYS  # single-token surfaces already curated
from record_formats import RECORD, format_a_abbrev_table, format_e_json_kb_constraints

MODEL = "Qwen/Qwen3.5-4B"
LENS_REPO, LENS_REV, LENS_FILE = "neuronpedia/jacobian-lens", "qwen-n1000", "model/lens.pt"
BAND = (0.33, 0.66)  # mid-network workspace band, depth fraction


def _single_token_id(tok, surface):
    for cand in (" " + surface, surface):
        ids = tok.encode(cand, add_special_tokens=False)
        if len(ids) == 1:
            return ids[0]
    return None


def mediator_ranks(model, lens, tok, prompt, tail_tokens=40):
    """Min workspace-band vocabulary rank of each mediator's single-token surface (lower = more
    representable). Multi-token mediators return inf and are excluded — the lens can't read them."""
    band = [l for l in lens.source_layers if BAND[0] <= l / model.n_layers <= BAND[1]]
    lens_logits, _, ids = lens.apply(model, prompt, layers=band, positions=None)
    seq = ids.shape[-1]
    tail = list(range(max(0, seq - tail_tokens), seq))
    ranks = {}
    for key in MEDIATOR_KEYS:
        best = math.inf
        for s in BRIDGE_CONCEPTS[key]:
            tid = _single_token_id(tok, s)
            if tid is None:
                continue
            for l in band:
                sub = lens_logits[l][tail]
                r = int((sub > sub[:, tid:tid + 1]).sum(dim=1).min())
                best = min(best, r)
        ranks[key] = best
    return ranks


def spearman(a: list[float], b: list[float]) -> float:
    """Spearman rho between two rankings (measured ranks vs inferred self-report saliences)."""
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).correlation)


def main():
    import transformers
    import jlens

    hf = transformers.AutoModelForCausalLM.from_pretrained(MODEL).cuda()
    tok = transformers.AutoTokenizer.from_pretrained(MODEL)
    model = jlens.from_hf(hf, tok)
    lens = jlens.JacobianLens.from_pretrained(LENS_REPO, filename=LENS_FILE, revision=LENS_REV)

    formats = {"A_naive": format_a_abbrev_table(RECORD),
               "E_converged": format_e_json_kb_constraints(RECORD)}
    measured = {name: mediator_ranks(model, lens, tok, p) for name, p in formats.items()}

    print("=== measured mediator workspace-band ranks (lower = more representable) ===")
    for name, ranks in measured.items():
        finite = {k: v for k, v in ranks.items() if v != math.inf}
        print(name, {k: v for k, v in sorted(finite.items(), key=lambda x: x[1])})
    # Δrank(converged - naive): negative = the converged format made the mediator MORE representable
    common = [k for k in MEDIATOR_KEYS
              if measured["A_naive"][k] != math.inf and measured["E_converged"][k] != math.inf]
    drank = {k: measured["E_converged"][k] - measured["A_naive"][k] for k in common}
    print("Δrank (converged - naive):", drank)

    # To compute the Spearman correlation, paste the inferred self-report salience per mediator
    # (from claude-workspace-probe on the SAME formats) as {mediator_key: salience_int} and compare
    # against the measured ranks here. Left as a manual step — the self-report is a Claude artifact.
    print("\nNext: correlate these measured ranks with the inferred self-report saliences per "
          "mediator (Spearman) — see docs/analysis/measured-qwen-lens-contradiction-and-colab.md.")


if __name__ == "__main__":
    if not os.environ.get("QWEN_PROBE_OK"):
        raise SystemExit("GPU/offline probe. Set QWEN_PROBE_OK=1 on a machine with jlens + a GPU. "
                         "This is NOT part of the Claude-only pipeline (see the module docstring).")
    main()
