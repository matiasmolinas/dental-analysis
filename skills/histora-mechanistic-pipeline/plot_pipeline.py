"""Render HISTORA pipeline outputs as figures — the "graphics" half a science demo needs.

Turns the deterministic JSON from `run_pipeline.py` into publication-style PNGs:
  - **envelopes**  — a forest plot of each axis output's 90% band (median marker) — "ranges, not points".
  - **sensitivity** — a tornado of which swept parameter dominates each output's uncertainty.
  - **mr**         — the Mendelian-randomization scatter (β_exposure vs β_outcome) with the IVW slope.
  - **benchmark**  — grouped bars of the S-vs-H comparative metrics.

Needs matplotlib (`pip install matplotlib`). Non-diagnostic: parameter-level ranges, never a patient value.

Usage:  python plot_pipeline.py [predictions.json] [--mr mr_report.json] [--benchmark benchmark_report.json]
"""

from __future__ import annotations

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_envelopes(predictions: dict, path: str = "fig_envelopes.png") -> str:
    """Forest plot of each output's 90% band, **normalized to its own median** so outputs on very
    different scales (CRP ~mg/L, tau ~fraction, onset ~years) are comparable; the absolute median is
    annotated on each row."""
    env = predictions["ranges_over_uncertainty"]
    labels = list(env.keys())
    fig, ax = plt.subplots(figsize=(7.5, 0.6 * len(labels) + 1.6))
    for i, k in enumerate(labels):
        lo, med, hi = env[k]["lo"], env[k]["median"], env[k]["hi"]
        if med:
            rlo, rmed, rhi = lo / med, 1.0, hi / med
        else:
            rlo, rmed, rhi = lo, med, hi
        ax.plot([rlo, rhi], [i, i], color="#A8323F", lw=3, solid_capstyle="round", alpha=0.55)
        ax.plot(rmed, i, "o", color="#A8323F", ms=8)
        ax.annotate(f"median = {med:g}", (rhi, i), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=8, color="#555")
    ax.axvline(1.0, color="#bbb", lw=0.8, ls="--")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("90% ensemble band, normalized to the median (dashed = median)")
    ax.set_xlim(0, ax.get_xlim()[1] * 1.15)
    ax.set_title("HISTORA — mechanistic predictions as ranges, not points", fontsize=11)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_sensitivity(sensitivity: dict, output: str = "crp_mg_l", path: str = "fig_sensitivity.png") -> str:
    params = sensitivity.get(output, {})
    items = sorted(params.items(), key=lambda kv: abs(kv[1]))
    names = [k for k, _ in items]
    vals = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(7, 0.5 * len(names) + 1.5))
    ax.barh(names, vals, color=["#2F7D5B" if v >= 0 else "#9C6B12" for v in vals])
    ax.axvline(0, color="#444", lw=0.8)
    ax.set_xlabel("normalized elasticity (dOutput/dParam)")
    ax.set_title(f"Sensitivity of {output} — which unknown dominates", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def _mr_panels(report: dict) -> list[tuple[str, dict]]:
    """Normalize any MR report shape into (title, panel) pairs. `run_cis_mr` is a single pair with a
    `correlated_ivw`; `run_real_mr` nests results under `outcomes`; the illustrative `run_mr` is a flat
    {key: panel}."""
    if "correlated_ivw" in report and "instruments" in report:   # cis_mr shape
        panel = dict(report, ivw=report["correlated_ivw"])
        return [(f"{report.get('exposure', '?')} → {report.get('outcome', '?')}", panel)]
    if isinstance(report.get("outcomes"), dict):                 # real_mr shape
        exp = report.get("exposure", "exposure")
        return [(f"{p.get('exposure', exp)} → {p.get('outcome', k)}", p)
                for k, p in report["outcomes"].items()]
    return [(f"{p.get('exposure', '?')} → {p.get('outcome', k)}", p)   # illustrative shape
            for k, p in report.items() if isinstance(p, dict) and "ivw" in p]


def plot_mr(mr_report: dict, path: str = "fig_mr.png") -> str:
    """MR scatter: per-SNP instrument points (with x/y error bars) + the IVW and MR-Egger slopes when
    the per-instrument data is present (real_mr); otherwise a bare IVW slope (illustrative)."""
    panels = _mr_panels(mr_report)
    if not panels:
        raise ValueError("no MR panels found in report")
    fig, axes = plt.subplots(1, len(panels), figsize=(4.9 * len(panels), 4.4), squeeze=False)
    for ax, (title, panel) in zip(axes[0], panels):
        ivw = panel.get("ivw", {})
        egg = panel.get("mr_egger", {})
        slope = ivw.get("estimate", 0.0)
        insts = panel.get("instruments") or []
        if insts:                                                # proper per-SNP scatter
            bx = [i["beta_exposure"] for i in insts]
            by = [i["beta_outcome"] for i in insts]
            ex = [i.get("se_exposure", 0) for i in insts]
            ey = [i.get("se_outcome", 0) for i in insts]
            ax.errorbar(bx, by, xerr=ex, yerr=ey, fmt="o", ms=5, color="#333", ecolor="#bbb",
                        elinewidth=0.8, capsize=2, label=f"instruments (n={len(insts)})")
        ax.axline((0, 0), slope=slope, color="#A8323F", lw=2,
                  label=f"IVW β={slope:+.3f} (p={ivw.get('p_value')})")
        if egg.get("slope") is not None:
            ax.axline((0, egg.get("intercept", 0.0)), slope=egg["slope"], color="#3A5A8C", lw=1.6,
                      ls="--", label=f"MR-Egger β={egg['slope']:+.3f}"
                                     + (" · pleiotropy!" if egg.get("pleiotropy_flagged") else ""))
        ax.axhline(0, color="#ddd", lw=0.6)
        ax.axvline(0, color="#ddd", lw=0.6)
        ax.set_xlabel("β exposure (CRP-raising allele)")
        ax.set_ylabel("β outcome (log-OR)")
        ax.set_title(title, fontsize=9)
        ax.legend(fontsize=7.5, loc="best")
    fig.suptitle("Mendelian randomization — genetic causal probe of the shared proxy", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_benchmark(report: dict, path: str = "fig_benchmark.png") -> str:
    agg = report["aggregate"]
    arms = list(agg.keys())
    metrics = ["M1_free_params_joint", "M3_calibration_error", "M5_uncertainty_honesty", "M7_falsifiability"]
    labels = ["free params ↓", "calib. err ↓", "uncertainty ↑", "falsifiability ↑"]
    x = range(len(metrics))
    w = 0.8 / len(arms)
    colors = {"separate_models": "#8A9099", "bare_claude": "#9C6B12", "histora_harness": "#2F7D5B"}
    fig, ax = plt.subplots(figsize=(8, 4.4))
    for j, arm in enumerate(arms):
        ax.bar([i + j * w for i in x], [agg[arm][m] for m in metrics], width=w,
               label=arm, color=colors.get(arm, "#777"))
    ax.set_xticks([i + w * (len(arms) - 1) / 2 for i in x])
    ax.set_xticklabels(labels)
    ax.set_title("Comparative benchmark — separate models vs. bare Claude vs. HISTORA", fontsize=11)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_stage3(report: dict, traj: dict, outdir: str = ".") -> list[str]:
    """Render the Stage-3 physiology figures (deepened mechanisms):
      - cv_plaque   : oxLDL / macrophage / foam-cell (plaque) trajectories, oral source vs baseline.
      - glucose     : the Bergman meal glucose response, oral inflammation vs baseline.
      - one_lever   : the integrative 'one lever, many axes' therapy response across CV/metabolic/neuro.
    These are the figures that make each mechanism legible; in Claude Science the same data renders as
    native (interactive/animated) figures with UniProt/PDB + OpenGWAS connectors grounding the proteins."""
    made = []

    # --- CV plaque trajectory ---
    p, b = traj["plaque"], traj["plaque_baseline"]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(p["t"], p["foam"], color="#A8323F", lw=2.4, label="foam cells / plaque (with oral inflammation)")
    ax.plot(b["t"], b["foam"], color="#A8323F", lw=1.4, ls="--", label="baseline (therapy limit)")
    ax.plot(p["t"], p["oxldl"], color="#9C6B12", lw=1.2, alpha=0.7, label="oxLDL")
    ax.plot(p["t"], p["macrophage"], color="#2F7D5B", lw=1.2, alpha=0.7, label="macrophages")
    ax.set_xlabel("time (arb. units)"); ax.set_ylabel("burden")
    ax.set_title("CV axis — atherosclerosis foam-cell process (Ougrinovskaia E2.6)", fontsize=10)
    ax.legend(fontsize=7.5); fig.tight_layout()
    path = os.path.join(outdir, "fig_stage3_cv_plaque.png"); fig.savefig(path, dpi=150); plt.close(fig)
    made.append(path)

    # --- Bergman glucose response ---
    g, gb = traj["glucose"], traj["glucose_baseline"]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(g["t"], g["glucose"], color="#A8323F", lw=2.2, label="glucose (with oral inflammation)")
    ax.plot(gb["t"], gb["glucose"], color="#3A5A8C", lw=1.6, ls="--", label="baseline (therapy limit)")
    ax.set_xlabel("time (min)"); ax.set_ylabel("plasma glucose (mg/dL)")
    ax.set_title("Metabolic axis — Bergman meal response; degraded S_I (E3.1)", fontsize=10)
    ax.legend(fontsize=8); fig.tight_layout()
    path = os.path.join(outdir, "fig_stage3_glucose.png"); fig.savefig(path, dpi=150); plt.close(fig)
    made.append(path)

    # --- one lever, many axes ---
    lever = report["one_lever_many_axes"]["coherent_multi_axis_response_to_therapy"]
    labels = ["CV plaque\n↓ (rel)", "HbA1c\n↓ (pp)", "tau onset\ndelay (yr)", "amyloid\n↓ (rel)"]
    keys = ["cardiovascular_plaque_rel_reduction", "metabolic_hba1c_drop_pp",
            "neuro_tau_onset_delay_years", "neuro_amyloid_rel_reduction"]
    vals = [lever.get(k) or 0.0 for k in keys]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.bar(labels, vals, color=["#A8323F", "#9C6B12", "#3A5A8C", "#2F7D5B"])
    ax.set_title("One lever, many axes — periodontal therapy's coherent multi-axis response", fontsize=10)
    ax.set_ylabel("axis response to source→0")
    for i, v in enumerate(vals):
        ax.annotate(f"{v:g}", (i, v), ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    path = os.path.join(outdir, "fig_stage3_one_lever.png"); fig.savefig(path, dpi=150); plt.close(fig)
    made.append(path)
    return made


def main() -> None:
    ap = argparse.ArgumentParser(description="Render HISTORA pipeline figures")
    ap.add_argument("predictions", nargs="?", default="predictions.json")
    ap.add_argument("--mr", default=None)
    ap.add_argument("--benchmark", default=None)
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()
    made = []
    if os.path.exists(args.predictions):
        preds = json.load(open(args.predictions))
        made.append(plot_envelopes(preds, os.path.join(args.outdir, "fig_envelopes.png")))
    if args.mr and os.path.exists(args.mr):
        made.append(plot_mr(json.load(open(args.mr)), os.path.join(args.outdir, "fig_mr.png")))
    if args.benchmark and os.path.exists(args.benchmark):
        made.append(plot_benchmark(json.load(open(args.benchmark)), os.path.join(args.outdir, "fig_benchmark.png")))
    print("wrote figures:", ", ".join(made) if made else "(no input JSON found)")


if __name__ == "__main__":
    main()
