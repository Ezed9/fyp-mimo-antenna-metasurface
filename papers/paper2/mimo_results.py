"""Coupling and diversity results of the four-port antenna, from the CST Touchstone exports.

Reads exports/mimo_noMS.s4p (antenna alone) and exports/mimo_MS.s4p (with the metasurface): the 4 x 4 S-matrix of an
"All Ports" run, normalised to 50 ohm (see CST_GUIDE.md, section 7). Returns None while the files are missing, and
build_paper2.py then prints highlighted placeholders instead of numbers.
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
import mimo_metrics as mm  # noqa: E402

CASES = {"noMS": "without the metasurface", "MS": "with the metasurface"}
# Validated categorical palette of analysis/make_figures.py; line styles repeat the identity for black-and-white print.
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
STYLES = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1, 1, 1))]
GRID, INK = "#d9d8d2", "#0b0b0b"


def diversity_gain(ecc: np.ndarray) -> np.ndarray:
    """Apparent diversity gain in dB, 10*sqrt(1 - rho_e), with rho_e the envelope correlation coefficient."""
    return 10 * np.sqrt(1 - np.clip(ecc, 0, 1))


def load(exports: Path) -> dict[str, tuple[np.ndarray, np.ndarray]] | None:
    paths = {case: exports / f"mimo_{case}.s4p" for case in CASES}
    if not all(p.exists() for p in paths.values()):
        return None
    import skrf

    out = {}
    for case, path in paths.items():
        net = skrf.Network(str(path))
        if net.nports != 4:
            raise ValueError(f"{path} has {net.nports} ports, expected 4")
        out[case] = (net.f / 1e9, net.s)
    return out


def analyse(data: dict[str, tuple[np.ndarray, np.ndarray]]) -> dict:
    """Per case: the range in which every port is matched, and the worst coupling, ECC, DG, CCL, TARC inside it."""
    res = {}
    for case, (f, S) in data.items():
        refl = np.max([mm.to_db(S[:, i, i]) for i in range(4)], axis=0)          # worst port at each frequency
        matched = refl <= -10.0
        lo = float(f[np.argmax(matched)]) if matched.any() else float(f[0])
        band = f >= lo
        pairs = {}
        for i, j in combinations(range(4), 2):
            c = mm.to_db(S[:, j, i])
            ecc = mm.ecc_from_s(S, i, j)
            k, m = int(np.argmax(np.where(band, c, -np.inf))), int(np.argmax(np.where(band, ecc, -np.inf)))
            pairs[(i + 1, j + 1)] = {"coupling": float(c[k]), "f_coupling": float(f[k]),
                                     "ecc": float(ecc[m]), "f_ecc": float(f[m]),
                                     "dg": float(diversity_gain(ecc[band]).min())}
        tarc = mm.to_db(mm.tarc(S, mm.random_excitations(4, 50)))
        res[case] = {
            "f": f, "S": S, "lower_edge": lo, "upper": float(f[-1]),
            "worst_reflection": float(refl[band].max()), "f_worst_reflection": float(f[band][refl[band].argmax()]),
            "matched_fraction": float(np.mean(refl[band] <= -10.0)),
            "port_spread": float(np.max(np.ptp([mm.to_db(S[band, i, i]) for i in range(4)], axis=0))),
            "pairs": pairs,
            "ccl": float(mm.ccl(S)[band].max()), "tarc": float(tarc[:, band].max()),
        }
    return res


def _axes(ylabel: str, height: float = 1.9):
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                         "mathtext.fontset": "stix", "font.size": 8, "axes.linewidth": 0.6, "savefig.dpi": 600,
                         "xtick.direction": "in", "ytick.direction": "in", "legend.fontsize": 6.8})
    fig, ax = plt.subplots(figsize=(3.4, height))
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel(ylabel)
    ax.grid(True, color=GRID, linewidth=0.4)
    ax.set_axisbelow(True)
    return fig, ax


def figures(res: dict, out: Path) -> dict[str, Path]:
    out.mkdir(parents=True, exist_ok=True)
    made = {}
    for case, r in res.items():
        fig, ax = _axes("Transmission coefficient (dB)")
        for k, (i, j) in enumerate(combinations(range(4), 2)):
            ax.plot(r["f"], mm.to_db(r["S"][:, j, i]), color=COLORS[k], linestyle=STYLES[k], linewidth=1.0,
                    label=f"$S_{{{j + 1}{i + 1}}}$")
        ax.axhline(-15, color=INK, linewidth=0.6, linestyle=(0, (1, 1.5)))
        ax.set_xlim(r["f"][0], r["f"][-1])
        ax.set_ylim(-60, 0)
        ax.legend(ncol=3, loc="lower right", frameon=True, framealpha=0.92, edgecolor=GRID, columnspacing=0.9)
        fig.tight_layout(pad=0.3)
        made[f"coupling_{case}"] = out / f"fig_coupling_{case}.png"
        fig.savefig(made[f"coupling_{case}"])
        plt.close(fig)
    fig, ax = _axes("ECC")
    for k, (case, r) in enumerate(res.items()):
        worst = np.max([mm.ecc_from_s(r["S"], i, j) for i, j in combinations(range(4), 2)], axis=0)
        ax.semilogy(r["f"], np.clip(worst, 1e-6, None), color=["#52514e", "#1c5cab"][k],
                    linestyle=[(0, (4, 1.6)), "-"][k], linewidth=1.1, label=CASES[case])
    ax.set_xlim(r["f"][0], r["f"][-1])
    ax.set_ylim(1e-5, 1)
    ax.legend(loc="upper right", frameon=True, framealpha=0.92, edgecolor=GRID)
    fig.tight_layout(pad=0.3)
    made["ecc"] = out / "fig_ecc.png"
    fig.savefig(made["ecc"])
    plt.close(fig)
    return made
