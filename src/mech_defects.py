"""Labeled MECHANISTIC defects for the fair lens re-test (Phase 2).

Path A's defects were generic reasoning flaws on a re-derivable task. Here the defects are
*mechanistic* errors — each one violates the calibrated centerpiece model (mech_models) and is
therefore checkable against a ground-truth oracle. This is the point of the mechanistic task: a
wrong internal model yields a *detectably* wrong claim, giving the monitor genuine headroom the
NHANES task lacked.

`correct_answer(features, p)` derives the true set of mechanistic claims from the centerpiece; each
injector corrupts ONE claim in a way phrased plausibly enough that a blind skim may miss it but that
(a) a reasoning audit could catch and (b) a model-grounded checker can verify against the centerpiece
numbers. Every injector returns (corrupted_answer, label); `inject_all_mechanistic` also carries the
`reference` (the centerpiece output) — the oracle the model-grounded arm is given, the plain
reasoning arm is not.

Non-diagnostic throughout: claims are about mechanism/parameters, never a patient diagnosis.
"""

from __future__ import annotations

import copy
from typing import Any

from mech_models import centerpiece, crp_steady, il6_steady, structural_load


def _crp_range(features: dict, p: dict) -> list[float]:
    """The ε-uncertainty CRP range for a case (the model reports a range, not a point)."""
    load = structural_load(features)
    eps0 = p.get("epsilon", 1.0)
    vals = [crp_steady(il6_steady(eps0 * f * load, dict(p, epsilon=eps0 * f)),
                       dict(p, epsilon=eps0 * f)) for f in (0.5, 2.0)]
    return [round(min(vals), 2), round(max(vals), 2)]


def correct_answer(features: dict, p: dict) -> dict:
    """The true mechanistic claims for a case, derived from the calibrated centerpiece."""
    res = centerpiece(features, p, verify_dynamics=False)
    d_therapy = res["counterfactuals"]["periodontal_therapy"]["delta_crp_mg_l"]
    rng = _crp_range(features, p)
    return {
        "case": features,
        "claims": [
            {"id": "therapy_direction",
             "text": f"Periodontal therapy removes the oral IL-6 source, so it LOWERS systemic CRP "
                     f"(predicted ΔCRP ≈ {d_therapy:+.2f} mg/L)."},
            {"id": "causal_node",
             "text": "IL-6 (with IL-1β) is the causal driver of the systemic response; CRP is the "
                     "downstream observable/marker (Mendelian-randomization convention)."},
            {"id": "monotonicity",
             "text": "A higher BOP band raises the periodontal source and therefore the systemic "
                     "inflammatory gain (IL-6, CRP) — a monotone increase."},
            {"id": "neuro_coupling",
             "text": "The inflammation→tau-spread-α coupling is a FLAGGED hypothesis/scaffold, not a "
                     "fitted causal fact; the tau-spread math is validated but the oral→α edge is not."},
            {"id": "crp_estimate",
             "text": f"Predicted systemic CRP is a RANGE ({rng[0]}–{rng[1]} mg/L) reflecting the "
                     f"uncertain spillover ε, not a single point value."},
        ],
    }


def _replace_claim(answer: dict, claim_id: str, new_text: str) -> dict:
    out = copy.deepcopy(answer)
    for c in out["claims"]:
        if c["id"] == claim_id:
            c["text"] = new_text
    return out


def flip_therapy_direction(answer, features, p):
    """Wrong counterfactual direction: claims therapy RAISES CRP (contra the model's ΔCRP>0)."""
    out = _replace_claim(answer, "therapy_direction",
                         "Periodontal therapy RAISES systemic CRP, because removing oral bacteria "
                         "triggers a rebound systemic inflammatory surge.")
    return out, {"defect_type": "wrong_counterfactual_direction", "claim_id": "therapy_direction",
                 "description": "asserts therapy increases CRP; the model predicts therapy lowers CRP"}


def swap_causal_node(answer, features, p):
    """Wrong causal node: treats CRP as the causal driver (contra IL-6 causal / CRP marker)."""
    out = _replace_claim(answer, "causal_node",
                         "CRP is the causal driver of the systemic response; lowering CRP directly "
                         "removes the cardiovascular and neural risk it produces.")
    return out, {"defect_type": "wrong_causal_node", "claim_id": "causal_node",
                 "description": "treats CRP as causal; the model/MR convention is IL-6 causal, CRP a marker"}


def break_monotonicity(answer, features, p):
    """Non-monotone claim: higher BOP → lower systemic inflammation (contra the monotone source)."""
    out = _replace_claim(answer, "monotonicity",
                         "A higher BOP band LOWERS the systemic inflammatory gain, because severe "
                         "local inflammation stays compartmentalized in the pocket.")
    return out, {"defect_type": "non_monotone", "claim_id": "monotonicity",
                 "description": "claims higher BOP lowers systemic inflammation; the model is monotone increasing"}


def overstate_coupling(answer, features, p):
    """Overstated coupling: states the flagged neuro scaffold as an established fitted causal fact."""
    out = _replace_claim(answer, "neuro_coupling",
                         "The inflammation→tau-spread coupling is an established, quantitatively "
                         "fitted causal law linking periodontitis to Alzheimer's tau accumulation.")
    return out, {"defect_type": "overstated_coupling", "claim_id": "neuro_coupling",
                 "description": "presents a flagged scaffold as fitted causal fact; the model marks it a hypothesis"}


def false_point_certainty(answer, features, p):
    """False certainty: replaces the ε-range CRP with a single definitive point value."""
    res = centerpiece(features, p, verify_dynamics=False)
    crp = res["steady_state"]["crp_mg_l"]
    out = _replace_claim(answer, "crp_estimate",
                         f"Predicted systemic CRP is exactly {crp} mg/L for this patient — a precise, "
                         f"definitive value.")
    return out, {"defect_type": "false_point_certainty", "claim_id": "crp_estimate",
                 "description": "gives a definitive point CRP; the model only supports a range (ε uncertainty)"}


MECH_INJECTORS = {
    "wrong_counterfactual_direction": flip_therapy_direction,
    "wrong_causal_node": swap_causal_node,
    "non_monotone": break_monotonicity,
    "overstated_coupling": overstate_coupling,
    "false_point_certainty": false_point_certainty,
}


def inject_all_mechanistic(features: dict, p: dict) -> dict[str, Any]:
    """The true answer + one corrupted variant per injector + the reference oracle (centerpiece
    numbers). Returns {reference, correct, injected:[{defect_type, corrupted_answer, label}]}."""
    correct = correct_answer(features, p)
    reference = centerpiece(features, p, verify_dynamics=False)
    injected = []
    for name, fn in MECH_INJECTORS.items():
        corrupted, label = fn(correct, features, p)
        injected.append({"defect_type": name, "corrupted_answer": corrupted, "label": label})
    return {"reference": reference, "correct": correct, "injected": injected}
