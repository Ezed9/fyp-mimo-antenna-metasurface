# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8", "numpy>=1.26", "pillow>=10"]
# ///
"""Concept sketches for the basics slides (illustrations, not simulation results).

Run from the repo root:  uv run presentation/deck/make_concepts.py
Writes figures/concept_s11.png, figures/concept_pattern.png and figures/cst_metasurface_cell.png.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FIGS = ROOT / "figures"

# deck palette (build_deck.js THEME)
NAVY, COPPER, GREEN, RED, GREY, INK = "#17324D", "#B8651B", "#2E7D5B", "#C0392B", "#8A94A6", "#1F2328"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Calibri", "Carlito", "DejaVu Sans"],
    "font.size": 15,
    "axes.edgecolor": GREY,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "savefig.dpi": 250,
    "savefig.bbox": "tight",
    "savefig.transparent": True,
})


def concept_s11() -> Path:
    """A smooth multi-dip S11 sketch with the −10 dB line and the band where it is below."""
    f = np.linspace(0, 18, 1200)
    inband = 0.5 * (np.tanh((f - 2.3) / 0.28) - np.tanh((f - 15.2) / 0.32))
    s = -1.5 - 0.08 * f - inband * (10.2 + 1.2 * np.cos(2 * np.pi * f / 3.1))
    for f0, depth, w in [(2.9, 14, 0.35), (5.2, 7, 0.6), (8.8, 9, 0.7), (11.9, 6, 0.8), (14.3, 11, 0.45)]:
        s -= depth * np.exp(-((f - f0) / w) ** 2)
    below = s <= -10
    lo, hi = f[below][0], f[below][-1]
    assert below[(f > lo) & (f < hi)].all(), "concept band must be continuous"
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.axvspan(lo, hi, color=GREEN, alpha=0.10, lw=0)
    ax.axhline(-10, color=RED, lw=1.6, ls="--")
    ax.plot(f, s, color=NAVY, lw=2.6)
    ax.annotate("", xy=(lo, -27.5), xytext=(hi, -27.5), arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.8))
    ax.text((lo + hi) / 2, -26.6, "bandwidth (S$_{11}$ below −10 dB)", ha="center", va="bottom", color=GREEN,
            fontsize=14, fontweight="bold")
    ax.text(17.85, -9.3, "−10 dB", ha="right", va="bottom", color=RED, fontsize=14, fontweight="bold")
    for x in (1.0, 16.7):
        ax.text(x, -20, "poor\nmatch", ha="center", va="center", color=GREY, fontsize=12.5)
    ax.set_xlim(0, 18)
    ax.set_ylim(-30, 1)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("S$_{11}$ (dB)")
    ax.set_xticks(range(0, 19, 3))
    ax.set_yticks([0, -10, -20, -30])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#E3E6EB", lw=0.8)
    out = FIGS / "concept_s11.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def concept_pattern() -> Path:
    """Side-view pattern sketch: a monopole sends equally front and back; a reflector folds the back lobe forward."""
    th = np.linspace(0, 2 * np.pi, 721)
    alone = np.abs(np.cos(th)) ** 1.2                              # front (0°) and back (180°) lobes equal
    forward = np.clip(0.5 * (1 + np.cos(th)), 0, None) ** 1.6 * 1.45 + 0.04   # mostly forward
    fig, ax = plt.subplots(figsize=(4.6, 4.2), subplot_kw={"projection": "polar"})
    ax.plot(th, alone, color=GREY, lw=2.4, ls="--", label="monopole alone")
    ax.fill(th, forward, color=COPPER, alpha=0.18, lw=0)
    ax.plot(th, forward, color=COPPER, lw=2.8, label="with a reflector behind")
    ax.set_theta_zero_location("N")
    ax.set_rticks([])
    ax.set_xticks(np.deg2rad([0, 90, 180, 270]))
    ax.set_xticklabels(["front", "", "back", ""], fontsize=14, color=INK)
    ax.set_ylim(0, 1.55)
    ax.spines["polar"].set_color("#D5D9E0")
    ax.grid(color="#E3E6EB")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=1, frameon=False, fontsize=13)
    out = FIGS / "concept_pattern.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def metasurface_cell() -> Path:
    """Close-up of one split-ring cell, cut from the CST top view of the array."""
    im = Image.open(FIGS / "cst_metasurface_top.png").convert("RGB")
    cell = im.crop((10, 10, 172, 172)).resize((648, 648), Image.LANCZOS)
    out = FIGS / "cst_metasurface_cell.png"
    cell.save(out, optimize=True)
    return out


if __name__ == "__main__":
    for p in (concept_s11(), concept_pattern(), metasurface_cell()):
        print(f"Wrote {p.relative_to(ROOT)}")
