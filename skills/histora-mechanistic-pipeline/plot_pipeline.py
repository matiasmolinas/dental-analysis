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


def plot_mr(mr_report: dict, path: str = "fig_mr.png") -> str:
    keys = list(mr_report.keys())
    fig, axes = plt.subplots(1, len(keys), figsize=(5.2 * len(keys), 4.4), squeeze=False)
    for ax, key in zip(axes[0], keys):
        panel = mr_report[key]
        ivw = panel.get("ivw", {})
        slope = ivw.get("estimate", 0.0)
        ax.axline((0, 0), slope=slope, color="#A8323F", lw=2,
                  label=f"IVW β={slope:+.3f} (p={ivw.get('p_value')})")
        ax.axhline(0, color="#bbb", lw=0.6)
        ax.set_xlabel("β exposure (genetic instrument)")
        ax.set_ylabel("β outcome")
        ax.set_title(f"{panel.get('exposure','?')} → {panel.get('outcome','?')}", fontsize=9)
        ax.legend(fontsize=8, loc="best")
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
