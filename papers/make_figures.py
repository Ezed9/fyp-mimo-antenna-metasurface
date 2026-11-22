"""Paper figures: with/without overlays of the CST curves, and cropped pattern/geometry panels.

Curves come from papers/data/*.csv (two columns: frequency in GHz, value). Those files are digitised CST screenshots;
overwrite them with the CST ASCII exports (same two columns) and re-run to get the camera-ready figures.

    python papers/make_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d8d2"
WITH, WITHOUT = "#1c5cab", "#52514e"      # blue solid = with the added board; grey dashed = antenna alone
BAND = "#cde2fb"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5, "axes.linewidth": 0.6, "axes.edgecolor": INK, "xtick.direction": "in",
    "ytick.direction": "in", "xtick.major.width": 0.5, "ytick.major.width": 0.5, "savefig.dpi": 600,
})


def load(name: str) -> tuple[np.ndarray, np.ndarray]:
    rows = [line.split(",") for line in (DATA / f"{name}.csv").read_text().splitlines()
            if line and (line[0].isdigit() or line[0] == "-")]
    arr = np.array(rows, dtype=float)
    return arr[:, 0], arr[:, 1]


def bands(f: np.ndarray, s: np.ndarray, level: float = -10.0) -> list[tuple[float, float]]:
    """Frequency intervals where s <= level (edges linearly interpolated)."""
    below, out, i = s <= level, [], 0
    while i < len(f):
        if not below[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(f) and below[j + 1]:
            j += 1
        lo = f[i] if i == 0 else f[i - 1] + (level - s[i - 1]) * (f[i] - f[i - 1]) / (s[i] - s[i - 1])
        hi = f[j] if j + 1 == len(f) else f[j] + (level - s[j]) * (f[j + 1] - f[j]) / (s[j + 1] - s[j])
        out.append((float(lo), float(hi)))
        i = j + 1
    return out


def _axes(ylabel: str, ylim: tuple[float, float], height: float = 2.05):
    fig, ax = plt.subplots(figsize=(3.4, height))
    ax.set_xlim(1, 15)
    ax.set_ylim(*ylim)
    ax.set_xticks(range(1, 16, 2))
    ax.set_xticks(range(1, 16), minor=True)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel(ylabel)
    ax.grid(True, color=GRID, linewidth=0.4)
    ax.set_axisbelow(True)
    return fig, ax


def _finish(fig, ax, out: Path, legend_loc: str) -> None:
    ax.legend(loc=legend_loc, frameon=True, framealpha=0.92, edgecolor=GRID, handlelength=2.4, borderpad=0.35)
    fig.tight_layout(pad=0.3)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)


def s11_overlay(tag: str, out: Path, label_with: str, label_without: str, ylim: tuple[float, float],
                shade_with: bool, legend_loc: str = "lower left") -> None:
    f0, s0 = load(f"{tag}_s11_noms")
    f1, s1 = load(f"{tag}_s11_ms")
    fig, ax = _axes(r"$|S_{11}|$ (dB)", ylim)
    if shade_with:
        for lo, hi in bands(f1, s1):
            ax.axvspan(lo, hi, color=BAND, alpha=0.55, linewidth=0)
    ax.axhline(-10, color=INK, linewidth=0.6, linestyle=(0, (1, 1.5)))
    ax.text(1.15, -9.4, "−10 dB", fontsize=7, color=MUTED, va="bottom")
    ax.plot(f0, s0, color=WITHOUT, linewidth=1.0, linestyle=(0, (4, 1.6)), label=label_without)
    ax.plot(f1, s1, color=WITH, linewidth=1.15, label=label_with)
    _finish(fig, ax, out, legend_loc)


def directivity_overlay(tag: str, out: Path, label_with: str, label_without: str, ylim: tuple[float, float],
                        legend_loc: str = "lower right", note: str | None = None) -> None:
    f0, d0 = load(f"{tag}_dir_noms")
    f1, d1 = load(f"{tag}_dir_ms")
    fig, ax = _axes("Directivity (dBi)", ylim)
    if f1[0] > 1.5 or f1[-1] < 14.5:               # the with-curve covers only part of the sweep: mark the part
        ax.axvspan(f1[0], f1[-1], color=BAND, alpha=0.45, linewidth=0)
    ax.axhline(0, color=INK, linewidth=0.4)
    ax.plot(f0, d0, color=WITHOUT, linewidth=1.0, linestyle=(0, (4, 1.6)), label=label_without)
    ax.plot(f1, d1, color=WITH, linewidth=1.15, label=label_with)
    if note:
        ax.text(0.5 * (f1[0] + f1[-1]), ylim[0] + 0.04 * (ylim[1] - ylim[0]), note, fontsize=6.8, color=MUTED,
                ha="center", va="bottom")
    _finish(fig, ax, out, legend_loc)


def crop(src: Path, out: Path, box: tuple[int, int, int, int], blank: tuple[int, int, int, int] | None = None) -> None:
    """Crop a screenshot; `blank` (in source pixels) is painted white first, to remove a legend box."""
    out.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(src).convert("RGBA")
    white = Image.new("RGBA", image.size, "white")
    image = Image.alpha_composite(white, image).convert("RGB")
    if blank:
        image.paste("white", blank)
    image.crop(box).save(out)


def _dim(ax, p0, p1, label, offset=(0, 0), color="white", ha="center", va="center", fontsize=7.5):
    """Dimension line p0–p1 (pixel coordinates) with arrowheads at both ends and an italic label."""
    ax.annotate("", xy=p0, xytext=p1, arrowprops=dict(arrowstyle="<->", color=color, linewidth=0.7,
                                                       shrinkA=0, shrinkB=0, mutation_scale=6))
    ax.text((p0[0] + p1[0]) / 2 + offset[0], (p0[1] + p1[1]) / 2 + offset[1], label, color=color, ha=ha, va=va,
            fontsize=fontsize)


def _geometry_axes(src: Path, pad: int = 52):
    image = Image.open(src).convert("RGB")
    w, h = image.size
    fig, ax = plt.subplots(figsize=(1.65, 1.65 * (h + 2 * pad) / (w + 2 * pad)))
    ax.imshow(image, extent=(0, w, h, 0), interpolation="lanczos")
    ax.set_xlim(-pad, w + pad)
    ax.set_ylim(h + pad, -pad)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    return fig, ax, w, h


def paper1_geometry(shots: Path, out_dir: Path) -> None:
    """Paper 1, Fig. 1: the two CST top views with the symbols of Table I. Copper edges were located in the
    screenshots (pixels); the labels carry the symbols only, the values are in Table I."""
    fig, ax, w, h = _geometry_axes(shots / "antenna_top.png")
    ink = INK
    _dim(ax, (0, -14), (w, -14), r"$W_s$", (0, -18), ink)
    _dim(ax, (w + 14, 0), (w + 14, h), r"$L_s$", (20, 0), ink)
    _dim(ax, (157, 125), (267, 125), r"$R$", (0, -13))
    _dim(ax, (22, 228), (22, h), r"$L_g$", (17, -42))
    _dim(ax, (0, 338), (135, 338), r"$W_{g1}$", (10, -14))
    _dim(ax, (178, 338), (w, 338), r"$W_{g2}$", (0, -14))
    _dim(ax, (138, h + 12), (176, h + 12), r"$W_f$", (0, 20), ink)
    ax.annotate(r"$g$", xy=(136.5, 262), xytext=(100, 262), color="white", fontsize=7.5, va="center", ha="right",
                arrowprops=dict(arrowstyle="->", color="white", linewidth=0.6, shrinkA=1, shrinkB=0,
                                mutation_scale=5))
    ax.annotate(r"$p$", xy=(196, 226), xytext=(246, 213), color=ink, fontsize=7.5, va="center", ha="left",
                arrowprops=dict(arrowstyle="->", color=ink, linewidth=0.6, shrinkA=1, shrinkB=0, mutation_scale=5))
    fig.savefig(out_dir / "fig_geometry_antenna.png")
    plt.close(fig)

    fig, ax, w, h = _geometry_axes(shots / "metasurface_top.png")
    _dim(ax, (0, -14), (w, -14), r"$W_m$", (0, -18), ink)
    _dim(ax, (w + 14, 0), (w + 14, h), r"$L_m$", (22, 0), ink)
    _dim(ax, (37, 74), (100, 74), r"$W_p$", (0, -12))
    _dim(ax, (37, 330), (106, 330), r"$P$", (0, 16), ink)
    ax.annotate(r"$s$", xy=(172, 318), xytext=(172, 352), color=ink, fontsize=7.5, va="center", ha="center",
                arrowprops=dict(arrowstyle="->", color=ink, linewidth=0.6, shrinkA=1, shrinkB=0, mutation_scale=5))
    fig.savefig(out_dir / "fig_geometry_metasurface.png")
    plt.close(fig)


def main() -> None:
    p1, p2 = HERE / "paper1", HERE / "paper2"
    s11_overlay("p1", p1 / "figures" / "fig_s11.png", "with the patch board", "antenna alone", (-40, 0), True)
    directivity_overlay("p1", p1 / "figures" / "fig_directivity.png", "with the patch board", "antenna alone",
                        (-5, 8), "lower right")
    s11_overlay("p2", p2 / "figures" / "fig_s11.png", "with the metasurface", "without the metasurface", (-50, 0),
                False, "lower left")
    directivity_overlay("p2", p2 / "figures" / "fig_directivity.png", "with the metasurface (6–10 GHz)",
                        "without the metasurface", (-4, 8), "lower right")
    paper1_geometry(p1 / "cst_screenshots", p1 / "figures")
    crop(p1 / "cst_screenshots" / "pattern_5p3GHz_without.png", p1 / "figures" / "fig_pattern_without.png",
         (0, 40, 340, 383), (286, 30, 480, 62))
    crop(p1 / "cst_screenshots" / "pattern_5p3GHz_with.png", p1 / "figures" / "fig_pattern_with.png",
         (0, 40, 340, 383), (286, 30, 480, 62))
    shots = p2 / "cst_screenshots"
    polar = (560, 0, 1560, 959)                     # the polar plot without the legend and the lobe read-out
    crop(shots / "7p4GHz_radiation_pattern_port1_without_metasurface.png", p2 / "figures" / "fig_pattern_without.png",
         polar)
    crop(shots / "7p4GHz_radiation_pattern_port1_with_metasurface.png", p2 / "figures" / "fig_pattern_with.png", polar)


if __name__ == "__main__":
    main()
