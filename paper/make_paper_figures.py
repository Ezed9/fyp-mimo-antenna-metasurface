# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8", "numpy>=1.26", "pillow>=10"]
# ///
"""Drawn figures for the paper (paper/figures/), IEEE column width, 300 dpi.

Run from the repo root:  uv run paper/make_paper_figures.py

Only the schematic and summary figures are drawn here: the stack-up sketch (Fig. 2) and the applications chart
(Fig. 6). The geometry, S11, directivity and radiation-pattern figures (Figs. 1, 3, 4 and 5) are the team's CST
screenshots in paper/cst/; paper/build_paper.py places them unchanged and nothing here redraws them.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
import design as d  # noqa: E402

COL_W = 3.45                      # IEEE two-column width, inches
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"   # categorical slots 1-3 (validated default palette)
BAND_FILL = "#cde2fb"             # blue step 100, for the -10 dB bands
COPPER, FR4 = "#b87333", "#e8dca0"
PH = "#f4f3f0"                    # placeholder panel fill

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "lines.linewidth": 1.4,
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})


def save(fig: plt.Figure, name: str) -> Path:
    d.FIGS.mkdir(parents=True, exist_ok=True)
    out = d.FIGS / name
    fig.savefig(out)
    plt.close(fig)
    print(f"  {out.relative_to(d.ROOT)}")
    return out


def grid(ax: plt.Axes) -> None:
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)


def placeholder(ax: plt.Axes, title: str, detail: str) -> None:
    ax.add_patch(Rectangle((0.03, 0.08), 0.94, 0.84, transform=ax.transAxes, fc=PH, ec=MUTED, lw=0.6,
                           ls=(0, (4, 3)), zorder=5))
    ax.text(0.5, 0.62, title, transform=ax.transAxes, ha="center", va="center", fontsize=8, weight="bold",
            color=INK, zorder=6)
    ax.text(0.5, 0.38, detail, transform=ax.transAxes, ha="center", va="center", fontsize=6.5, color=MUTED,
            zorder=6, linespacing=1.3)


def shade_bands(ax: plt.Axes, bands: list[d.Band], f_max: float) -> None:
    for b in bands:
        ax.axvspan(b.lo, min(b.hi, f_max), color=BAND_FILL, lw=0, zorder=0)


# --------------------------------------------------------------------------- Fig. 2: stack-up (side view)
def fig_stackup() -> Path:
    fig, ax = plt.subplots(figsize=(COL_W, 1.45))
    wd = 6.0
    ya, ta = 1.55, 0.22   # antenna substrate
    ym, tm = 0.55, 0.22   # metasurface substrate
    ax.add_patch(Rectangle((0, ya), wd, ta, fc=FR4, ec=INK, lw=0.5))
    for x0, w in ((0.0, 2.55), (2.62, 0.76), (3.45, 2.55)):     # CPW grounds and feed / octagon (top copper)
        ax.add_patch(Rectangle((x0, ya + ta), w, 0.05, fc=COPPER, ec=INK, lw=0.3))
    ax.add_patch(Rectangle((0, ym), wd, tm, fc=FR4, ec=INK, lw=0.5))
    n, pitch = 4, wd / 4
    for i in range(n):   # square patches on top of the metasurface board
        ax.add_patch(Rectangle((i * pitch + 0.06 * pitch, ym + tm), 0.88 * pitch, 0.05, fc=COPPER, ec=INK, lw=0.3))
    if d.MS_COPPER_BACK:
        ax.add_patch(Rectangle((0, ym - 0.05), wd, 0.05, fc=COPPER, ec=INK, lw=0.3))
    xd = wd + 0.25
    ax.add_patch(FancyArrowPatch((xd, ya), (xd, ym + tm + 0.05), arrowstyle="<|-|>", mutation_scale=6, lw=0.7,
                                 color=INK, shrinkA=0, shrinkB=0))
    ax.text(xd + 0.12, (ya + ym + tm) / 2, "$h$ (air)", va="center", fontsize=7.5)
    xa = 3.0
    ax.add_patch(FancyArrowPatch((xa - 0.4, ya + 0.32), (xa - 0.4, ya + 0.85), arrowstyle="-|>", mutation_scale=7,
                                 lw=1.1, color=BLUE))
    ax.add_patch(FancyArrowPatch((xa + 0.1, ya - 0.04), (xa + 0.1, ym + tm + 0.12), arrowstyle="-|>",
                                 mutation_scale=7, lw=1.1, color=ORANGE))
    ax.add_patch(FancyArrowPatch((xa + 0.45, ym + tm + 0.12), (xa + 0.45, ya + 0.85), arrowstyle="-|>",
                                 mutation_scale=7, lw=1.1, color=BLUE, ls=(0, (3, 2))))
    lab = dict(fontsize=7, color=INK, va="center")
    ax.text(-0.1, ya + ta / 2, "antenna (FR-4)", ha="right", **lab)
    ax.text(-0.1, ya + ta + 0.2, "octagon + CPW", ha="right", **lab)
    ax.text(-0.1, ym + tm / 2 + 0.05, "metasurface (FR-4)", ha="right", **lab)
    ax.text(-0.1, ym + tm + 0.22, "4 × 4 patches", ha="right", **lab)
    ax.text(-0.1, ym - 0.12, "copper ground", ha="right", **lab)
    ax.text(xa - 0.5, ya + 0.62, "forward", ha="right", **lab)
    ax.text(xa + 0.55, ya + 0.62, "reflected", ha="left", **lab)
    ax.text(xa + 0.0, (ya + ym + tm) / 2, "backward", ha="right", **lab)
    ax.text(wd, 0.2, "side view, not to scale", ha="right", fontsize=6.5, color=MUTED, style="italic")
    ax.set_xlim(-2.0, wd + 1.1)
    ax.set_ylim(0.1, 2.45)
    ax.axis("off")
    return save(fig, "fig2_stackup.png")


# --------------------------------------------------------------------------- Fig. 6: applications
def fig_applications() -> Path:
    f, s, _ = d.s11_with_ms()
    bands = d.bands(f, s)
    rows = len(d.SERVICES)
    fig, ax = plt.subplots(figsize=(COL_W, 2.35))
    for b in bands:
        ax.axvspan(b.lo, min(b.hi, f[-1]), color=BAND_FILL, lw=0, zorder=0)
        ax.add_patch(Rectangle((b.lo, rows + 0.15), min(b.hi, f[-1]) - b.lo, 0.6, fc=BLUE, ec="none", zorder=3))
        if b.open_top:
            ax.annotate("", (f[-1] + 0.45, rows + 0.45), (f[-1], rows + 0.45),
                        arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, mutation_scale=6))
    ticks, labels = [rows + 0.45], ["This antenna (|S$_{11}$| < −10 dB)"]
    for i, (label, lo, hi) in enumerate(d.SERVICES):
        y = rows - 1 - i
        cov = d.coverage(lo, hi, bands)
        full = cov > 0.995
        ax.add_patch(Rectangle((lo, y + 0.22), hi - lo, 0.56, fc=INK if full else "white", ec=INK, lw=0.6,
                               hatch=None if full else "////////", zorder=3))
        ticks.append(y + 0.5)
        labels.append(label)
        if not full:
            ax.text(hi + 0.15, y + 0.5, f"{100 * cov:.0f} %", ha="left", va="center", fontsize=6, color=MUTED)
    ax.set_xlim(1, 15.6)
    ax.set_ylim(-0.1, rows + 0.9)
    ax.set_yticks(ticks, labels, fontsize=6.5)
    ax.tick_params(axis="y", length=0)
    ax.set_xticks(range(1, 16, 2))
    ax.set_xlabel("Frequency (GHz)")
    for sp in ("left", "right", "top"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    return save(fig, "fig6_applications.png")


if __name__ == "__main__":
    print("Writing paper figures:")
    for fn in (fig_stackup, fig_applications):
        fn()
