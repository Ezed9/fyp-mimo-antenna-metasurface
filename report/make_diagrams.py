# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8", "numpy>=1.26"]
# ///
"""Explanatory figures for the report and the deck (computed or schematic, never simulated results).

Run from the repo root:  uv run report/make_diagrams.py
Writes figures/fig_design_flow.png, figures/fig_stackup.png and figures/fig_gap_phase.png.
If exports/unitcell_phase.txt exists (CST ASCII export of the SRR reflection phase, CST_GUIDE.md §4), it is
overlaid on the gap-phase chart.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
import literature as lit  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "figures"
UNITCELL = ROOT / "exports" / "unitcell_phase.txt"

# Same validated palette and style as analysis/make_figures.py.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
NAVY, TINT, LINE = "#1F497D", "#DCE6F2", "#A6A6A6"
FR4, COPPER = "#8DA35A", "#C07A3A"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 9,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": GRID,
    "grid.linewidth": 0.5,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def _box(ax, x, y, w, h, text, status):
    fill, edge, ink, ls = {"done": (NAVY, NAVY, "white", "-"), "doing": (TINT, NAVY, INK, "-"),
                           "planned": ("white", LINE, MUTED, "--")}[status]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=edge,
                                lw=1.2, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=ink, fontsize=8.5, linespacing=1.25)


def _arrow(ax, p, q):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=10, lw=1.2, color=NAVY))


def design_flow() -> Path:
    steps = [("1. Initial antenna\nin CST", "done"),
             ("2. Ground position\nsweep", "done"),
             ("3. Patch size\nsweep", "done"),
             ("4. Optimised\nantenna (S$_{11}$)", "done"),
             ("5. Metasurface\ndesign (6 × 5 SRR)", "done"),
             ("6. Antenna +\nmetasurface (S$_{11}$)", "done"),
             ("7. Gain vs\nfrequency plots", "doing"),
             ("8. Phase II: MIMO,\nfabrication, testing", "planned")]
    fig, ax = plt.subplots(figsize=(6.0, 2.3))
    w, h, gx = 1.30, 0.54, 0.22
    xs = [k * (w + gx) for k in range(4)]
    y1, y2 = 1.25, 0.38
    for k in range(4):
        _box(ax, xs[k], y1, w, h, *steps[k])
        _box(ax, xs[3 - k], y2, w, h, *steps[4 + k])
    for k in range(3):
        _arrow(ax, (xs[k] + w, y1 + h / 2), (xs[k + 1], y1 + h / 2))
        _arrow(ax, (xs[3 - k], y2 + h / 2), (xs[2 - k] + w, y2 + h / 2))
    _arrow(ax, (xs[3] + w / 2, y1), (xs[3] + w / 2, y2 + h))
    for k, (lab, st) in enumerate([("Done", "done"), ("Remaining (Phase I)", "doing"), ("Planned (Phase II)", "planned")]):
        x0 = 0.4 + k * 1.8
        _box(ax, x0, 0.02, 0.26, 0.18, "", st)
        ax.text(x0 + 0.34, 0.11, lab, va="center", fontsize=8.0, color=INK)
    ax.set_xlim(-0.05, xs[3] + w + 0.05)
    ax.set_ylim(0, y1 + h + 0.05)
    ax.axis("off")
    out = FIGS / "fig_design_flow.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def stackup() -> Path:
    """Side view of antenna, air gap and SRR metasurface (schematic, not to scale)."""
    fig, ax = plt.subplots(figsize=(6.0, 2.7))
    x0, wd = 0.0, 6.0
    ya, ta = 2.0, 0.22          # antenna substrate
    ym, tm = 0.75, 0.22         # metasurface substrate
    ax.add_patch(Rectangle((x0, ya), wd, ta, fc=FR4, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((x0 + 1.9, ya + ta), 2.2, 0.06, fc=COPPER, ec=INK, lw=0.5))   # patch / CPW (top copper)
    ax.add_patch(Rectangle((x0, ym), wd, tm, fc=FR4, ec=INK, lw=0.6))
    n = 9
    cw = wd / n
    for i in range(n):  # SRR cells on top of the metasurface board
        ax.add_patch(Rectangle((x0 + i * cw + 0.15 * cw, ym + tm), 0.7 * cw, 0.05, fc=COPPER, ec=INK, lw=0.4))
    ground = lit.THIS_WORK.get("ms_ground")
    if ground:
        ax.add_patch(Rectangle((x0, ym - 0.05), wd, 0.05, fc=COPPER, ec=INK, lw=0.4))
    # gap dimension
    xd = x0 + wd + 0.25
    ax.annotate("", (xd, ya), (xd, ym + tm + 0.05), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.8))
    ax.text(xd + 0.1, (ya + ym + tm) / 2, f"air gap\n{lit.GAP_MM} mm", va="center", fontsize=8.5)
    # waves
    xa = x0 + 3.0
    ax.add_patch(FancyArrowPatch((xa - 0.35, ya + 0.35), (xa - 0.35, ya + 0.95), arrowstyle="-|>",
                                 mutation_scale=10, lw=1.4, color=BLUE))
    ax.add_patch(FancyArrowPatch((xa + 0.15, ya - 0.05), (xa + 0.15, ym + tm + 0.12), arrowstyle="-|>",
                                 mutation_scale=10, lw=1.4, color=ORANGE))
    ax.add_patch(FancyArrowPatch((xa + 0.5, ym + tm + 0.12), (xa + 0.5, ya + 0.95), arrowstyle="-|>",
                                 mutation_scale=10, lw=1.4, color=BLUE, ls="--"))
    ax.text(xa - 0.45, ya + 0.75, "forward wave", ha="right", va="center", fontsize=8.5, color=INK)
    ax.text(xa + 0.6, ya + 0.75, "reflected wave adds\nto the forward wave", ha="left", va="center",
            fontsize=8.5, color=INK)
    ax.text(xa + 0.05, (ya + ym + tm) / 2, "backward\nwave", ha="right", va="center", fontsize=8.5, color=INK)
    lab = dict(fontsize=8.5, color=INK, va="center")
    ax.text(x0 - 0.1, ya + ta / 2, "antenna substrate", ha="right", **lab)
    ax.text(x0 + 1.85, ya + ta + 0.2, "CPW-fed monopole (copper)", ha="right", **lab)
    ax.text(x0 - 0.1, ym + tm / 2, "metasurface substrate", ha="right", **lab)
    ax.text(x0 + 0.1, ym + tm + 0.2, "split-ring cells", ha="left", **lab)
    ax.text(x0 - 0.1, ym - 0.22, {True: "copper ground", False: "no ground plane",
                                  None: "ground plane: to be confirmed"}[ground], ha="right", **lab)
    ax.text(x0 + wd, 0.25, "schematic, not to scale", ha="right", fontsize=7.5, color=MUTED, style="italic")
    ax.set_xlim(-2.4, wd + 1.6)
    ax.set_ylim(0.1, 3.05)
    ax.axis("off")
    out = FIGS / "fig_stackup.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def _read_two_columns(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rows = []
    for line in path.read_text(errors="ignore").splitlines():
        parts = line.replace(",", " ").split()
        try:
            rows.append((float(parts[0]), float(parts[1])))
        except (IndexError, ValueError):
            continue
    a = np.array(rows)
    return a[:, 0], a[:, 1]


def gap_phase() -> Path:
    """Reflection phase a reflector needs at gap h for in-phase addition (eq. φ_R = 2k0h), vs a PEC plate."""
    h = lit.GAP_MM
    f = np.linspace(2.0, 16.0, 400)
    need = np.array([lit.round_trip_phase_deg(x, h) for x in f])
    f_pec = 90.0 * lit.C_MM_GHZ / (720.0 * h)   # where 2k0h = 90°, i.e. PEC enters the ±90° window
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    ax.fill_between(f, need - 90, need + 90, color=BLUE, alpha=0.12, lw=0)
    ax.plot(f, need, color=BLUE, lw=2, label=f"Required phase $2k_0h$ ($h$ = {h} mm)")
    ax.axhline(180, color=ORANGE, lw=2, ls="--", label="Metal (PEC) plate, 180°")
    if UNITCELL.exists():
        uf, ph = _read_two_columns(UNITCELL)
        ax.plot(uf, ph, color=AQUA, lw=2, label="SRR metasurface (CST)")
    ax.axvline(f_pec, color=MUTED, lw=0.8, ls=":")
    ax.text(f_pec + 0.15, -60, f"PEC within ±90° only\nabove {f_pec:.1f} GHz", fontsize=8, color=INK, va="bottom")
    ax.text(2.2, need[0] + 98, "±90° window: reflection adds to the forward wave", fontsize=8, color=INK)
    ax.text(15.8, 186, "PEC", ha="right", va="bottom", fontsize=8.5, color=INK)
    ax.text(15.8, need[-1] - 12, "required", ha="right", va="top", fontsize=8.5, color=INK)
    ax.set_xlim(2, 16)
    ax.set_ylim(-90, 270)
    ax.set_yticks(range(-90, 271, 45))
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Reflection phase (deg)")
    ax.grid(True)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.95, edgecolor=GRID)
    out = FIGS / "fig_gap_phase.png"
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    FIGS.mkdir(exist_ok=True)
    for path in (design_flow(), stackup(), gap_phase()):
        print(f"Wrote {path.relative_to(ROOT)}")
