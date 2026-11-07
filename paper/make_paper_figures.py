# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8", "numpy>=1.26", "pillow>=10"]
# ///
"""Figures for the paper (paper/figures/), IEEE column width, 300 dpi.

Run from the repo root:  uv run paper/make_paper_figures.py

Results that are not exported from CST yet (antenna-alone S11, realized gain, radiation patterns) are drawn as
clearly labelled placeholders. Drop the CST ASCII exports named in paper/design.py into exports/paper/ and run the
script again: the placeholders are replaced by the data.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle
from PIL import Image

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


# --------------------------------------------------------------------------- Fig. 1: geometry (annotated screenshots)
def dim_arrow(ax, p, q, label, *, text_xy=None, color=INK, fs=7.5, rot=0, ha="center", va="center", text_color=None):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="<|-|>", mutation_scale=6, lw=0.7, color=color,
                                 shrinkA=0, shrinkB=0))
    tx, ty = text_xy if text_xy else ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    ax.text(tx, ty, label, fontsize=fs, rotation=rot, ha=ha, va=va, color=text_color or color, style="italic")


def fig_geometry() -> Path:
    ant = np.asarray(Image.open(d.CST / "cst_octagon_antenna.png").convert("RGB"))
    ms = np.asarray(Image.open(d.CST / "cst_ms4x4_top.png").convert("RGB"))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL_W, 2.05), gridspec_kw={"wspace": 0.12})
    W = "white"
    # (a) antenna: pixel coordinates measured on paper/cst/cst_octagon_antenna.png (board x 45-338, y 58-392)
    a1.imshow(ant)
    a1.set_xlim(-8, 400)
    a1.set_ylim(430, 18)
    dim_arrow(a1, (45, 40), (338, 40), "$W_s$", text_xy=(191, 26))
    dim_arrow(a1, (25, 58), (25, 392), "$L_s$", text_xy=(9, 225), rot=90)
    dim_arrow(a1, (360, 268), (360, 392), "$L_g$", text_xy=(378, 330), rot=90)
    dim_arrow(a1, (52, 320), (180, 320), "$W_g$", text_xy=(116, 307), color=W)
    a1.plot([198, 293], [171, 170], color=W, lw=0.8)
    a1.plot([198], [171], "o", ms=2, color=W)
    a1.text(246, 158, "$R$", color=W, fontsize=8, ha="center", style="italic")
    a1.annotate("$W_f$", (201, 382), (150, 414), fontsize=7.5, ha="center", va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=INK, mutation_scale=5))
    a1.annotate("$g$", (219, 382), (262, 414), fontsize=7.5, ha="center", va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=INK, mutation_scale=5))
    # (b) metasurface: board x 14-305, y 17-349; patches 47-100, 108-160, ... (columns), 57-108, 117-168 (rows)
    a2.imshow(ms)
    a2.set_xlim(-30, 345)
    a2.set_ylim(400, -12)
    dim_arrow(a2, (14, 2), (305, 2), "$W_m$", text_xy=(160, -9))
    dim_arrow(a2, (-8, 17), (-8, 349), "$L_m$", text_xy=(-22, 183), rot=90)
    dim_arrow(a2, (49, 70), (99, 70), "$W_p$", text_xy=(74, 90), color=W)
    dim_arrow(a2, (46, 312), (105, 312), "$P$", text_xy=(76, 328))
    a2.annotate("$s$", (103, 284), (150, 330), fontsize=7.5, ha="center", va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=INK, mutation_scale=5))
    for a in (a1, a2):
        a.axis("off")
    fig.text(0.27, 0.1, "(a)", ha="center", fontsize=8)
    fig.text(0.74, 0.1, "(b)", ha="center", fontsize=8)
    return save(fig, "fig1_geometry.png")


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


# --------------------------------------------------------------------------- Fig. 3: S11
def fig_s11() -> Path:
    f, s, src = d.s11_with_ms()
    bands = d.bands(f, s)
    alone = d.s11_alone()
    fig, ax = plt.subplots(figsize=(COL_W, 2.15))
    shade_bands(ax, bands, f[-1])
    ax.axhline(-10, color=MUTED, lw=0.7, ls=(0, (4, 2)), zorder=1)
    if alone is not None:
        ax.plot(alone[0], alone[1], color=ORANGE, lw=1.2, ls=(0, (5, 2)), label="Antenna alone", zorder=3)
    ax.plot(f, s, color=BLUE, label="Antenna with metasurface", zorder=4)
    for i, b in enumerate(bands, 1):
        ax.text(b.centre if not b.open_top else (b.lo + f[-1]) / 2, -1.6, ["I", "II", "III"][i - 1],
                ha="center", va="center", fontsize=7.5, color=INK, weight="bold")
    for fd, sd in d.dips(f, s, below=-20):
        left = fd < 9.5 and fd > 8   # 9.03 GHz sits next to the 9.4 GHz hump: label it on the left
        ax.annotate(f"{fd:.2f} GHz", (fd, sd), (fd - 0.3 if left else fd + 0.3, sd), fontsize=6.5, color=INK,
                    va="center", ha="right" if left else "left")
    ax.set_xlim(1, 15)
    ax.set_ylim(-32, 0)
    ax.set_xticks(range(1, 16, 2))
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("$|S_{11}|$ (dB)")
    grid(ax)
    handles, labels = ax.get_legend_handles_labels()
    if alone is None:
        ax.text(0.99, 0.03, "antenna-alone curve: placeholder,\nadd exports/paper/s11_antenna_alone.txt",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=6, color=MUTED, style="italic")
    ax.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False,
              handlelength=2.5)
    return save(fig, "fig3_s11.png")


# --------------------------------------------------------------------------- Fig. 4: realized gain
def fig_gain() -> Path:
    f, s, _ = d.s11_with_ms()
    bands = d.bands(f, s)
    fig, ax = plt.subplots(figsize=(COL_W, 2.0))
    shade_bands(ax, bands, f[-1])
    have = False
    for path, label, color, ls in ((d.GAIN_ALONE_EXPORT, "Antenna alone", ORANGE, (0, (5, 2))),
                                   (d.GAIN_MS_EXPORT, "Antenna with metasurface", BLUE, "-")):
        if path.exists():
            gf, gv = d.read_two_columns(path)
            ax.plot(gf, gv, color=color, ls=ls, label=label)
            have = True
    ax.set_xlim(1, 15)
    ax.set_xticks(range(1, 16, 2))
    ax.set_ylim(-10, 12)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Realized gain (dBi)")
    grid(ax)
    if have:
        ax.legend(loc="lower right", frameon=True, framealpha=0.95, edgecolor=GRID)
    else:
        placeholder(ax, "PLACEHOLDER: realized gain vs frequency",
                    "antenna alone vs with metasurface (broadside, CST)\n"
                    "export to exports/paper/gain_antenna_alone.txt\nand exports/paper/gain_with_ms.txt")
    return save(fig, "fig4_gain.png")


# --------------------------------------------------------------------------- Fig. 5: radiation patterns
def fig_patterns() -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(COL_W, 1.6), subplot_kw={"projection": "polar"},
                             gridspec_kw={"wspace": 0.55})
    any_data = False
    for ax, fq in zip(axes, d.PATTERN_FREQS):
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_rlim(-30, 10)
        ax.set_rticks([-20, -10, 0])
        ax.tick_params(labelsize=5.5, pad=0)
        ax.set_xticks(np.deg2rad(range(0, 360, 90)), ["0°", "90°", "180°", ""], fontsize=5.5)
        ax.set_rlabel_position(330)
        ax.grid(color=GRID, lw=0.4)
        for plane, color, ls in (("E", BLUE, "-"), ("H", ORANGE, (0, (4, 2)))):
            path = d.pattern_export(fq, plane)
            if path.exists():
                ang, val = d.read_two_columns(path)
                ax.plot(np.deg2rad(ang), val, color=color, ls=ls, lw=1.0, label=f"{plane}-plane")
                any_data = True
        ax.set_title(f"{fq:g} GHz", fontsize=7.5, pad=6)
    if any_data:
        axes[-1].legend(loc="upper right", bbox_to_anchor=(1.55, 1.25), fontsize=6, frameon=False)
    else:
        fig.text(0.5, 0.42, "PLACEHOLDER: E- and H-plane patterns (CST far-field cuts)\n"
                 "export to exports/paper/pattern_<f>GHz_E.txt / _H.txt",
                 ha="center", va="center", fontsize=6.5, color=MUTED,
                 bbox=dict(boxstyle="square,pad=0.5", fc=PH, ec=MUTED, lw=0.6, ls=(0, (4, 3))))
    return save(fig, "fig5_patterns.png")


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
    for fn in (fig_geometry, fig_stackup, fig_s11, fig_gain, fig_patterns, fig_applications):
        fn()
