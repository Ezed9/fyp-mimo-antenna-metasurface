# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8", "pillow>=10"]
# ///
"""Directivity vs frequency of the antenna alone and with the metasurface, on one chart.

The team's CST results are two screenshots, both titled "Directivity,Phi=0.0,Max. Value (Subrange)": at each
frequency, the highest directivity in the φ = 0° plane. That is directivity, not gain: it leaves out the losses in the
FR-4 and copper and the mismatch at the port (realized gain includes both).

  figures/cst_single_final_directivity.png   antenna alone          dense samples 1–6 GHz, then only 9 and 18 GHz
  figures/cst_single_ms_directivity.jpg      with the metasurface   1–6 GHz, a sample every 0.1 GHz

Run from the repo root:  uv run analysis/plot_directivity.py
  1. digitises both screenshots (analysis/digitize_cst_plot.py) → exports/single_*_directivity_digitized.csv
  2. draws both curves on one chart → figures/fig_directivity_compare.png (report) and
     figures/fig_directivity_compare_deck.png (deck)
  3. prints the numbers quoted in the report and the deck (report/literature.py, THIS_WORK["dir_*"])
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parent))
import digitize_cst_plot as dg  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIGS, EXPORTS = ROOT / "figures", ROOT / "exports"
QUANTITY = "CST Directivity,Phi=0.0,Max. Value (Subrange), dBi: the highest directivity in the phi = 0 deg plane"
ALONE = {"img": "cst_single_final_directivity.png", "x": (0, 18), "y": (-4, 5),
         "csv": "single_final_directivity_digitized.csv", "what": "antenna alone (R = 15 mm, Lg = -7 mm)"}
MS = {"img": "cst_single_ms_directivity.jpg", "x": (1, 6), "y": (-2, 9),
      "csv": "single_ms_directivity_digitized.csv", "what": "antenna with the 6 x 5 split-ring metasurface"}
F_LO, F_HI = 1.0, 6.0   # the metasurface run covers only 1–6 GHz
BAND_LO = 2.0           # matched band starts at ≈ 2.0 GHz with the metasurface (2.16 GHz alone)

STYLES = {
    "report": {
        "out": "fig_directivity_compare.png", "size": (5.4, 2.6), "dpi": 300, "transparent": False,
        "font": {"font.family": "serif", "font.serif": ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"],
                 "mathtext.fontset": "stix", "font.size": 8.5},
        "ms": "#B8651B", "alone": "#5B6472", "ink": "#0b0b0b", "muted": "#52514e", "grid": "#e1e0d9",
        "axis": "#a6a6a6", "below": "#f0efec", "lw": (1.7, 1.3), "dash": (5, 2.2), "dot": 5.5, "ring": 1.2,
    },
    "deck": {
        "out": "fig_directivity_compare_deck.png", "size": (8.4, 4.7), "dpi": 250, "transparent": True,
        "font": {"font.family": "sans-serif", "font.sans-serif": ["Calibri", "Carlito", "DejaVu Sans"],
                 "font.size": 15},
        "ms": "#B8651B", "alone": "#6B7480", "ink": "#1F2328", "muted": "#5B6472", "grid": "#E3E6EB",
        "axis": "#8A94A6", "below": "#F2F4F7", "lw": (2.8, 2.2), "dash": (5, 2.4), "dot": 9.5, "ring": 2.0,
    },
}


# ----------------------------------------------------------------------------------------------- data
def digitise() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Read both screenshots, write the CSVs, and return (f_alone, d_alone, f_ms, d_ms)."""
    pa = dg.read_plot(FIGS / ALONE["img"], ALONE["x"], ALONE["y"])
    fa, da = dg.dense(pa, F_LO, F_HI, 0.05)
    tail, _ = dg.vertices(pa, [6.0, 9.0, 18.0])
    pm = dg.read_plot(FIGS / MS["img"], MS["x"], MS["y"])
    fm = np.round(np.arange(F_LO, F_HI + 0.05, 0.1), 6)
    dm, worst = dg.vertices(pm, list(fm))
    for spec, p, f, d, how in (
            (ALONE, pa, fa, da, ["smooth curve: red-pixel column centroids every 0.05 GHz",
                                 f"above 6 GHz CST has only two samples: 9 GHz {tail[1]:.2f} dBi, 18 GHz {tail[2]:.2f} dBi"
                                 " (joined by straight lines in the screenshot), so they are left out"]),
            (MS, pm, fm, dm, ["CST samples every 0.1 GHz; each value from straight-line fits of the two segments"
                              f" meeting there (worst disagreement {worst * pm.y_per_px:.2f} dB, at the near-vertical"
                              " jumps around 3 GHz)"])):
        dg.write_csv(EXPORTS / spec["csv"], f, d, "directivity_dBi", [
            f"{QUANTITY}; {spec['what']}",
            f"Digitised from figures/{spec['img']} by analysis/plot_directivity.py (analysis/digitize_cst_plot.py)",
            f"scale fitted through every gridline (worst misfit {p.grid_resid_px:.2f} px); 1 px = "
            f"{p.y_per_px:.3f} dB, {p.x_per_px * 1000:.1f} MHz; accuracy about +/-0.05 dB", *how])
    return fa, da, fm, dm


def compare(fa, da, fm, dm) -> dict:
    """The numbers the report and the deck quote, on a 1 MHz grid (the metasurface curve is CST's polyline)."""
    f = np.round(np.arange(F_LO, F_HI + 1e-9, 0.001), 3)
    a, m = np.interp(f, fa, da), np.interp(f, fm, dm)
    band = f >= BAND_LO
    lower = band & (m < a)
    runs = np.split(np.where(lower)[0], np.where(np.diff(np.where(lower)[0]) > 1)[0] + 1)
    return {
        "peak_alone": (a.max(), f[a == a.max()]), "peak_ms": (m.max(), f[m.argmax()]),
        "mean": (a[band].mean(), m[band].mean()), "higher_pct": 100 * np.mean(m[band] > a[band]),
        "lower": [(f[r[0]], f[r[-1]], (m - a)[r].min(), f[r][np.argmin((m - a)[r])]) for r in runs if len(r)],
        "best": ((m - a)[band].max(), f[band][np.argmax((m - a)[band])]),
        "min_alone": (a[band].min(), f[band][np.argmin(a[band])]), "min_ms": (m[band].min(), f[band][np.argmin(m[band])]),
    }


# ----------------------------------------------------------------------------------------------- figure
def draw(style: str, fa, da, fm, dm) -> Path:
    s = STYLES[style]
    deck = style == "deck"
    with plt.rc_context({**s["font"], "axes.edgecolor": s["axis"], "axes.labelcolor": s["ink"],
                         "xtick.color": s["muted"], "ytick.color": s["muted"], "savefig.dpi": s["dpi"],
                         "savefig.bbox": "tight", "savefig.transparent": s["transparent"]}):
        fig, ax = plt.subplots(figsize=s["size"])
        f = np.round(np.arange(F_LO, F_HI + 1e-9, 0.002), 3)
        a, m = np.interp(f, fa, da), np.interp(f, fm, dm)
        inband = f >= BAND_LO - 1e-9
        # below the matched band: neither case is matched there, so it is greyed out and left out of the shading
        ax.axvspan(F_LO, BAND_LO, color=s["below"], lw=0, zorder=0)
        ax.text((F_LO + BAND_LO) / 2, 9.35, "below the\nmatched band", ha="center", va="top", color=s["muted"],
                fontsize="small", linespacing=1.15)
        # where each one is higher (2–6 GHz)
        ax.fill_between(f, a, m, where=inband & (m >= a), interpolate=True, color=s["ms"], alpha=0.20, lw=0, zorder=1)
        ax.fill_between(f, a, m, where=inband & (m < a), interpolate=True, color=s["alone"], alpha=0.22, lw=0,
                        zorder=1)
        ax.plot(fa, da, color=s["alone"], lw=s["lw"][1], ls=(0, s["dash"]), dash_capstyle="round", zorder=3)
        ax.plot(fm, dm, color=s["ms"], lw=s["lw"][0], solid_joinstyle="round", solid_capstyle="round", zorder=4)
        # the two peaks (dots with a surface ring) and their values
        ka, km = int(np.argmax(da)), int(np.argmax(dm))
        for x, y, col in ((fa[ka], da[ka], s["alone"]), (fm[km], dm[km], s["ms"])):
            ax.plot(x, y, "o", ms=s["dot"], mfc=col, mec="white", mew=s["ring"], zorder=5)
        ax.annotate(f"{dm[km]:.1f} dBi", (fm[km], dm[km]), xytext=(-9, 0), textcoords="offset points", ha="right",
                    va="center", color=s["ink"], fontweight="bold", zorder=6)
        ax.annotate(f"{da[ka]:.1f} dBi", (fa[ka], da[ka]), xytext=(-2, 9 if deck else 7), textcoords="offset points",
                    ha="right", va="bottom", color=s["ink"], fontweight="bold", zorder=6)
        # direct labels for the two shadings, placed inside the widest part of each
        ax.text(5.45, 2.55, "metasurface\nhigher", ha="center", va="center", color=s["ink"], fontsize="small",
                linespacing=1.1, zorder=6)
        lab = ax.text(3.33, -2.3, "antenna alone\nhigher", ha="center", va="center", color=s["ink"],
                      fontsize="small", linespacing=1.1, zorder=6)
        fig.canvas.draw()
        bb = lab.get_window_extent().transformed(ax.transData.inverted())
        for tx, ty in ((2.99, 1.2), (3.62, 2.95)):  # one leader into each of the two "alone higher" regions
            ax.annotate("", (tx, ty), xytext=(float(np.clip(tx, bb.x0 + 0.1, bb.x1 - 0.1)), bb.y1 + 0.12),
                        arrowprops={"arrowstyle": "-", "color": s["muted"], "lw": 0.9 if deck else 0.6,
                                    "shrinkA": 0, "shrinkB": 1}, zorder=6)
        ax.set_xlim(F_LO, F_HI)
        ax.set_ylim(-4, 10)
        ax.set_xticks(np.arange(1, 6.01, 0.5))
        ax.set_xticklabels([f"{v:g}" for v in np.arange(1, 6.01, 0.5)])
        ax.set_yticks(range(-4, 11, 2))
        ax.set_yticklabels([f"{v}".replace("-", "−") for v in range(-4, 11, 2)])
        ax.set_xlabel("Frequency (GHz)")
        ax.set_ylabel("Directivity (dBi)")
        ax.grid(True, color=s["grid"], lw=0.8 if deck else 0.5, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(length=0, pad=6 if deck else 4)
        handles = [Line2D([], [], color=s["ms"], lw=s["lw"][0], label="With metasurface"),
                   Line2D([], [], color=s["alone"], lw=s["lw"][1], ls=(0, s["dash"]), label="Antenna alone")]
        ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False,
                  borderaxespad=0.3, handlelength=2.6 if deck else 2.4, columnspacing=1.6, handletextpad=0.6)
        out = FIGS / s["out"]
        fig.savefig(out)
        plt.close(fig)
    return out


def main() -> None:
    fa, da, fm, dm = digitise()
    c = compare(fa, da, fm, dm)
    for style in STYLES:
        print(f"Wrote {draw(style, fa, da, fm, dm).relative_to(ROOT)}")
    print(f"Wrote exports/{ALONE['csv']} and exports/{MS['csv']}")
    pa, fpa = c["peak_alone"]
    print(f"\nPeak directivity, {F_LO:g}–{F_HI:g} GHz: antenna alone {pa:.2f} dBi at {fpa.min():.2f}–{fpa.max():.2f} GHz;"
          f" with metasurface {c['peak_ms'][0]:.2f} dBi at {c['peak_ms'][1]:.2f} GHz"
          f" (+{c['peak_ms'][0] - pa:.2f} dB)")
    print(f"{BAND_LO:g}–{F_HI:g} GHz: metasurface higher on {c['higher_pct']:.1f} % of the band; mean"
          f" {c['mean'][0]:.2f} → {c['mean'][1]:.2f} dBi ({c['mean'][1] - c['mean'][0]:+.2f} dB)")
    for lo, hi, worst, at in c["lower"]:
        print(f"  antenna alone higher at {lo:.3f}–{hi:.3f} GHz (worst {worst:+.2f} dB at {at:.2f} GHz)")
    print(f"  largest gain from the metasurface {c['best'][0]:+.2f} dB at {c['best'][1]:.2f} GHz"
          f" (antenna alone dips to {c['min_alone'][0]:.2f} dBi at {c['min_alone'][1]:.2f} GHz in this plane)")
    print(f"  metasurface minimum {c['min_ms'][0]:.2f} dBi at {c['min_ms'][1]:.2f} GHz")


if __name__ == "__main__":
    main()
