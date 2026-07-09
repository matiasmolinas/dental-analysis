"""Target bridge concepts for the oral-systemic (periodontal <-> cardiovascular) task.

This is the **spec** the Lens Observer scores the inferred-lens readout against: the
mediating concepts that should surface in the primary's self-report for an input
format to count as "good". If the model surfaces them, it is *relating* oral and
systemic data, not merely listing it; if they are absent or faint, that is the
deficiency signal the Observer acts on. (Claude only — a self-report readout, not a
measurement.)

Each concept maps to several candidate surface forms so the readout can be matched
flexibly to how the model happens to name the concept.

MEDIATORS are the unspoken, cross-domain links (inflammation, atherosclerosis,
endothelial dysfunction, bacteremia). SHARED are common risk factors that appear
in the input itself (diabetes, smoking); they matter less as evidence of
relational reasoning because a model can surface them by mere copying.
"""

from __future__ import annotations

BRIDGE_CONCEPTS: dict[str, list[str]] = {
    # --- mediators (unspoken cross-domain links) ---
    "systemic_inflammation": ["inflammation", "inflammatory"],
    "c_reactive_protein": ["CRP", "protein"],  # "hs-CRP" is usually multi-token
    "cytokines": ["cytokine", "interleukin", "IL"],
    "atherosclerosis": ["atherosclerosis", "plaque", "atheroma"],
    "endothelial_dysfunction": ["endothelial", "endothelium", "vascular"],
    "bacteremia": ["bacteremia", "bacteria", "microbial"],
    "oxidative_stress": ["oxidative", "oxidation"],
    "cardiovascular_risk": ["cardiovascular", "coronary", "arterial", "cardiac"],
    # --- shared risk factors (present in the input; weaker evidence) ---
    "shared_diabetes": ["diabetes", "glycemic", "insulin"],
    "shared_smoking": ["smoking", "tobacco", "nicotine"],
}

# Concepts that prove relational reasoning; the optimizer targets these first.
MEDIATOR_KEYS = [
    "systemic_inflammation",
    "c_reactive_protein",
    "cytokines",
    "atherosclerosis",
    "endothelial_dysfunction",
    "bacteremia",
    "oxidative_stress",
    "cardiovascular_risk",
]
