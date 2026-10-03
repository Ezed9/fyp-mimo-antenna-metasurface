"""Turn CST exports (see CST_GUIDE.md, "Export conventions") into IEEE-style figures + a summary.

Usage:
    uv run python make_figures.py                 # reads ../exports, writes ../figures
    uv run python make_figures.py --demo          # synthetic data, to check the pipeline
"""

import argparse
import re
import tempfile
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import skrf as rf

import mimo_metrics as mm

ROOT = Path(__file__).resolve().parent.parent
UWB = (3.1, 10.6)
PATTERN_FREQS = (4.0, 7.0, 10.0)
CASES = {"noMS": "Without MS", "MS": "With AMC MS"}

# Validated categorical palette (light surface), fixed order; line styles give B/W-print redundancy.
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
STYLES = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1, 1, 1)), (0, (1, 1)), (0, (6, 2, 1, 2))]
INK, MUTED, BAND = "#0b0b0b", "#52514e", "#f0efec"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 8,
    "axes.labelsize": 8,
    "legend.fontsize": 7,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "grid.color": "#d9d8d4",
    "grid.linewidth": 0.5,
    "lines.linewidth": 1.4,
    "legend.frameon": True,
    "legend.framealpha": 0.9,
    "legend.edgecolor": "#d9d8d4",
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

Curve = tuple[str, np.ndarray, np.ndarray]


# ---------------------------------------------------------------- parsers

def _sweep_labels(param_dicts: list[dict[str, str]]) -> list[str]:
    keys = {k for d in param_dicts for k in d}
    varying = [k for k in sorted(keys) if len({d.get(k) for d in param_dicts}) > 1]
    return [", ".join(f"{k} = {d[k]}" for k in varying) for d in param_dicts]


def read_cst_ascii(path: Path) -> list[Curve]:
    """CST 1D 'Plot Data (ASCII)' export; one block per curve (parameter sweeps give several)."""
    blocks: list[dict] = []
    in_data = False
    for line in path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            if in_data or not blocks:
                blocks.append({"params": {}, "label": "", "rows": []})
                in_data = False
            if s.startswith("#Parameters"):
                body = s.split("{", 1)[-1].rstrip("}")
                blocks[-1]["params"] = dict(
                    kv.strip().split("=", 1) for kv in body.split(";") if "=" in kv
                )
            quoted = re.findall(r'"([^"]+)"', s)
            if len(quoted) >= 2:
                blocks[-1]["label"] = quoted[1]
            continue
        nums = s.replace(",", " ").split()
        try:
            row = [float(v) for v in nums[:2]]
        except ValueError:
            continue
        if not blocks:
            blocks.append({"params": {}, "label": path.stem, "rows": []})
        blocks[-1]["rows"].append(row)
        in_data = True
    blocks = [b for b in blocks if b["rows"]]
    labels = (
        _sweep_labels([b["params"] for b in blocks])
        if len(blocks) > 1 and any(b["params"] for b in blocks)
        else [b["label"] or path.stem for b in blocks]
    )
    out = []
    for label, b in zip(labels, blocks):
        arr = np.array(b["rows"])
        out.append((label, arr[:, 0], arr[:, 1]))
    return out


def read_farfield(path: Path) -> dict[str, np.ndarray]:
    """CST far-field ASCII export: Theta, Phi, Abs(total), Abs(Theta), Phase(Theta), Abs(Phi), Phase(Phi), AR."""
    lines = path.read_text(errors="ignore").splitlines()
    header = lines[0]
    data = np.array(
        [[float(v) for v in ln.split()[:7]] for ln in lines if ln.strip() and ln.split()[0][0] in "-0123456789."
         and not ln.strip().startswith("--")]
    )
    is_db = "dB" in header
    th_u, th_i = np.unique(data[:, 0], return_inverse=True)
    ph_u, ph_i = np.unique(data[:, 1], return_inverse=True)

    def grid(col: np.ndarray) -> np.ndarray:
        g = np.full((th_u.size, ph_u.size), np.nan)
        g[th_i, ph_i] = col
        return g

    amp = (lambda x: 10 ** (x / 20)) if is_db else (lambda x: x)
    e_th = amp(grid(data[:, 3])) * np.exp(1j * np.deg2rad(grid(data[:, 4])))
    e_ph = amp(grid(data[:, 5])) * np.exp(1j * np.deg2rad(grid(data[:, 6])))
    return {"theta": th_u, "phi": ph_u, "e_theta": e_th, "e_phi": e_ph,
            "abs_theta_db": grid(data[:, 3]) if is_db else mm.to_db(grid(data[:, 3])),
            "abs_phi_db": grid(data[:, 5]) if is_db else mm.to_db(grid(data[:, 5]))}


# ---------------------------------------------------------------- plot helpers

def new_fig(rows: int = 1, h: float = 2.5) -> tuple[plt.Figure, list[plt.Axes]]:
    fig, axes = plt.subplots(rows, 1, figsize=(3.5, h * rows), squeeze=False, sharex=rows > 1)
    return fig, list(axes[:, 0])


def mark_band(ax: plt.Axes, level: float | None = -10.0) -> None:
    ax.axvspan(*UWB, color=BAND, zorder=0, lw=0)
    if level is not None:
        ax.axhline(level, color=MUTED, lw=0.8, ls="--", zorder=1)


def legend(ax: plt.Axes, n: int) -> None:
    """Small legends sit inside; many series go below the axes so no curve is hidden."""
    if n <= 3:
        ax.legend(loc="best")
    else:
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=3 if n != 4 else 2, frameon=False)


def overlay(ax: plt.Axes, curves: list[Curve], start: int = 0) -> None:
    for k, (label, x, y) in enumerate(curves, start):
        ax.plot(x, y, color=COLORS[k % 8], ls=STYLES[k % 8], label=label)
    if len(curves) > 1:
        legend(ax, len(curves))


def save(fig: plt.Figure, out: Path, name: str, made: list[str]) -> None:
    fig.align_ylabels()
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}")
    plt.close(fig)
    made.append(name)


def s_db_axes(ax: plt.Axes, ylabel: str = "S-parameter (dB)") -> None:
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel(ylabel)


# ---------------------------------------------------------------- figure groups

def fig_sweeps(exp: Path, out: Path, made: list[str], summary: list[str]) -> None:
    for name, sym in (("single_Lg_sweep", "L_g"), ("single_R_sweep", "R"), ("single_gap_sweep", "h")):
        p = exp / f"{name}.txt"
        if not p.exists():
            continue
        curves = read_cst_ascii(p)
        fig, (ax,) = new_fig()
        mark_band(ax)
        overlay(ax, curves)
        s_db_axes(ax, "$|S_{11}|$ (dB)")
        save(fig, out, f"fig_{name}", made)
        ranked = sorted(curves, key=lambda c: mm.score_s11(c[1], c[2], UWB), reverse=True)
        summary.append(f"[{name}] ranking (UWB coverage, worst in-band S11):")
        for label, f, s in ranked:
            cov, worst = mm.score_s11(f, s, UWB)
            summary.append(f"    {label:<28} coverage {cov * 100:5.1f} %   worst {-worst:6.2f} dB")
        summary.append(f"    -> best {sym}: {ranked[0][0]}")


def fig_single_final(exp: Path, out: Path, made: list[str], summary: list[str]) -> None:
    s11 = exp / "single_final_s11.txt"
    if s11.exists():
        (_, f, s), *_ = read_cst_ascii(s11)
        fig, (ax,) = new_fig()
        mark_band(ax)
        ax.plot(f, s, color=COLORS[0])
        s_db_axes(ax, "$|S_{11}|$ (dB)")
        save(fig, out, "fig_single_final_s11", made)
        bands = mm.impedance_bandwidth(f, s)
        summary.append("[single final] -10 dB bands: " + ", ".join(f"{a:.2f}-{b:.2f} GHz" for a, b in bands))
    _gain_eff(exp, out, made, summary, "single_final", {"single_final": "Single antenna"})


def _gain_eff(exp: Path, out: Path, made: list[str], summary: list[str], name: str, cases: dict[str, str]) -> None:
    gains = [(lbl, *read_cst_ascii(exp / f"{c}_gain.txt")[0][1:]) for c, lbl in cases.items()
             if (exp / f"{c}_gain.txt").exists()]
    effs = [(lbl, *read_cst_ascii(exp / f"{c}_eff_tot.txt")[0][1:]) for c, lbl in cases.items()
            if (exp / f"{c}_eff_tot.txt").exists()]
    if not gains and not effs:
        return
    fig, axes = new_fig(rows=2 if gains and effs else 1, h=2.2)
    if gains:
        mark_band(axes[0], None)
        overlay(axes[0], gains)
        axes[0].set_ylabel("Realized gain (dBi)")
        for lbl, f, g in gains:
            m = mm.band_mask(f, UWB)
            summary.append(f"[{name}] {lbl}: realized gain {g[m].min():.2f} to {g[m].max():.2f} dBi in UWB")
    if effs:
        ax = axes[-1]
        mark_band(ax, None)
        effs = [(lbl, f, e * 100 if e.max() <= 1.0 else e) for lbl, f, e in effs]
        overlay(ax, effs)
        ax.set_ylabel("Total efficiency (%)")
    axes[-1].set_xlabel("Frequency (GHz)")
    save(fig, out, f"fig_{name}_gain_eff", made)


def fig_unit_cell(exp: Path, out: Path, made: list[str], summary: list[str]) -> None:
    p = exp / "unitcell_phase.txt"
    if not p.exists():
        return
    (_, f, ph), *_ = read_cst_ascii(p)
    mag_p = exp / "unitcell_mag.txt"
    fig, axes = new_fig(rows=2 if mag_p.exists() else 1, h=2.2)
    ax = axes[0]
    inphase = np.abs(ph) <= 90
    ax.fill_between(f, -180, 180, where=inphase, color=BAND, lw=0, zorder=0)
    for lvl in (-90, 90):
        ax.axhline(lvl, color=MUTED, lw=0.8, ls="--")
    ax.plot(f, ph, color=COLORS[0])
    ax.set_ylim(-180, 180)
    ax.set_yticks(range(-180, 181, 90))
    ax.set_ylabel("Reflection phase (deg)")
    if mag_p.exists():
        (_, fm, mag), *_ = read_cst_ascii(mag_p)
        axes[1].plot(fm, mag, color=COLORS[1])
        axes[1].set_ylabel("Reflection magnitude (dB)")
    axes[-1].set_xlabel("Frequency (GHz)")
    save(fig, out, "fig_unitcell_reflection", made)
    bands = mm.impedance_bandwidth(f, np.abs(ph), level=90)
    summary.append("[unit cell] in-phase (+/-90 deg) band(s): " + ", ".join(f"{a:.2f}-{b:.2f} GHz" for a, b in bands))


def fig_reflector_compare(exp: Path, out: Path, made: list[str], summary: list[str]) -> None:
    cases = {"single_none": "No reflector", "single_pec": "PEC reflector", "single_amc": "AMC reflector"}
    s11 = [(lbl, *read_cst_ascii(exp / f"{c}_s11.txt")[0][1:]) for c, lbl in cases.items()
           if (exp / f"{c}_s11.txt").exists()]
    if s11:
        fig, (ax,) = new_fig()
        mark_band(ax)
        overlay(ax, s11)
        s_db_axes(ax, "$|S_{11}|$ (dB)")
        save(fig, out, "fig_reflector_compare_s11", made)
    _gain_eff(exp, out, made, summary, "reflector_compare", cases)


def load_mimo(exp: Path) -> dict[str, rf.Network]:
    return {c: rf.Network(str(p)) for c in CASES if (p := exp / f"mimo_{c}.s4p").exists()}


def fig_mimo_sparams(nets: dict[str, rf.Network], out: Path, made: list[str], summary: list[str]) -> None:
    for case, net in nets.items():
        f, S = net.f / 1e9, net.s
        n = S.shape[1]
        fig, (ax,) = new_fig()
        mark_band(ax)
        overlay(ax, [(f"$S_{{{i + 1}{i + 1}}}$", f, mm.to_db(S[:, i, i])) for i in range(n)])
        s_db_axes(ax, "Reflection coefficient (dB)")
        save(fig, out, f"fig_mimo_{case}_reflection", made)

        pairs = list(combinations(range(n), 2))
        fig, (ax,) = new_fig()
        mark_band(ax, -15.0)
        overlay(ax, [(f"$S_{{{j + 1}{i + 1}}}$", f, mm.to_db(S[:, j, i])) for i, j in pairs])
        s_db_axes(ax, "Transmission coefficient (dB)")
        save(fig, out, f"fig_mimo_{case}_coupling", made)

        m = mm.band_mask(f, UWB)
        worst_s = max(mm.to_db(S[m, i, i]).max() for i in range(n))
        worst_iso = -max(mm.to_db(S[m, j, i]).max() for i, j in pairs)
        summary.append(f"[MIMO {CASES[case]}] worst in-band Sii {worst_s:.2f} dB, min isolation {worst_iso:.2f} dB")
        for a, b in mm.impedance_bandwidth(f, mm.to_db(S[:, 0, 0])):
            summary.append(f"    port-1 -10 dB band {a:.2f}-{b:.2f} GHz")

    if len(nets) == 2:
        fig, axes = new_fig(rows=2, h=2.2)
        for k, (case, net) in enumerate(nets.items()):
            f, S = net.f / 1e9, net.s
            axes[0].plot(f, mm.to_db(S[:, 0, 0]), color=COLORS[k], ls=STYLES[k], label=CASES[case])
            worst = np.max([mm.to_db(S[:, j, i]) for i, j in combinations(range(S.shape[1]), 2)], axis=0)
            axes[1].plot(f, worst, color=COLORS[k], ls=STYLES[k], label=CASES[case])
        mark_band(axes[0])
        mark_band(axes[1], -15.0)
        axes[0].set_ylabel("$|S_{11}|$ (dB)")
        axes[1].set_ylabel("Worst coupling (dB)")
        axes[0].legend(loc="best")
        axes[1].set_xlabel("Frequency (GHz)")
        save(fig, out, "fig_mimo_ms_comparison", made)


def fig_mimo_metrics(nets: dict[str, rf.Network], out: Path, made: list[str], summary: list[str]) -> None:
    if not nets:
        return
    n = next(iter(nets.values())).s.shape[1]
    pairs = [(0, j) for j in range(1, n)]
    per_case = {}
    for case, net in nets.items():
        f, S = net.f / 1e9, net.s
        ecc = {p: mm.ecc_from_s(S, *p) for p in pairs}
        all_ecc = np.max([mm.ecc_from_s(S, i, j) for i, j in combinations(range(n), 2)], axis=0)
        t = mm.to_db(mm.tarc(S, mm.random_excitations(n, 20)))
        per_case[case] = (f, S, ecc, all_ecc, t)
        m = mm.band_mask(f, UWB)
        meg = mm.meg_db(S)[m]
        summary += [
            f"[MIMO {CASES[case]}] in UWB: max ECC(S) {all_ecc[m].max():.4f}, "
            f"min DG {mm.diversity_gain(all_ecc[m]).min():.3f} dB, max TARC {t[:, m].max():.2f} dB, "
            f"max CCL {mm.ccl(S)[m].max():.3f} bit/s/Hz",
            f"    MEG range {meg.min():.2f} to {meg.max():.2f} dB, "
            f"max |MEGi-MEGj| {np.max(meg.max(axis=1) - meg.min(axis=1)):.2f} dB",
        ]

    def per_metric(name: str, ylabel: str, fn, hline: float | None = None, log: bool = False) -> None:
        fig, (ax,) = new_fig()
        mark_band(ax, hline)
        k = 0
        for case, (f, S, ecc, *_rest) in per_case.items():
            for p in pairs:
                tag = f"Ports {p[0] + 1}-{p[1] + 1}"
                lbl = tag if len(per_case) == 1 else f"{tag}, {CASES[case]}"
                ax.plot(f, fn(ecc[p], S, p), color=COLORS[k % 8], ls=STYLES[k % 8], label=lbl)
                k += 1
        if log:
            ax.set_yscale("log")
        legend(ax, k)
        s_db_axes(ax, ylabel)
        save(fig, out, f"fig_mimo_{name}", made)

    per_metric("ecc", "ECC", lambda e, S, p: np.clip(e, 1e-6, None), log=True)
    per_metric("dg", "Diversity gain (dB)", lambda e, S, p: mm.diversity_gain(e))

    fig, (ax,) = new_fig()
    mark_band(ax)
    for k, (case, (f, _S, _e, _a, t)) in enumerate(per_case.items()):
        ax.fill_between(f, t.min(axis=0), t.max(axis=0), color=COLORS[k], alpha=0.25, lw=0)
        ax.plot(f, t.max(axis=0), color=COLORS[k], ls=STYLES[k], label=f"{CASES[case]} (worst of 20 phases)")
    ax.legend(loc="best")
    s_db_axes(ax, "TARC (dB)")
    save(fig, out, "fig_mimo_tarc", made)

    fig, (ax,) = new_fig()
    mark_band(ax, 0.4)
    overlay(ax, [(CASES[c], f, mm.ccl(S)) for c, (f, S, *_r) in per_case.items()])
    s_db_axes(ax, "CCL (bit/s/Hz)")
    save(fig, out, "fig_mimo_ccl", made)

    fig, (ax,) = new_fig()
    mark_band(ax, None)
    k = 0
    for case, (f, S, *_r) in per_case.items():
        meg = mm.meg_db(S)
        for i in range(n):
            lbl = f"Port {i + 1}" if len(per_case) == 1 else f"Port {i + 1}, {CASES[case]}"
            ax.plot(f, meg[:, i], color=COLORS[k % 8], ls=STYLES[k % 8], label=lbl)
            k += 1
    legend(ax, k)
    s_db_axes(ax, "MEG (dB)")
    save(fig, out, "fig_mimo_meg", made)


def fig_patterns(exp: Path, out: Path, made: list[str], summary: list[str]) -> None:
    ffdir = exp / "ff"
    files = sorted(ffdir.glob("*.txt")) if ffdir.exists() else []
    pat = re.compile(r"(?P<case>\w+?)_p(?P<port>\d)_(?P<f>[\d.]+)GHz")
    groups: dict[tuple[str, str], dict[int, dict]] = {}
    for p in files:
        m = pat.fullmatch(p.stem)
        if not m:
            continue
        ff = read_farfield(p)
        groups.setdefault((m["case"], m["f"]), {})[int(m["port"])] = ff
        _polar(ff, out, f"fig_pattern_{p.stem}", made)
    for (case, f), ports in sorted(groups.items()):
        for a, b in combinations(sorted(ports), 2):
            A, B = ports[a], ports[b]
            th = A["theta"][:, None]
            e = mm.ecc_from_farfield(A["e_theta"], A["e_phi"], B["e_theta"], B["e_phi"], th)
            summary.append(f"[far-field ECC] {case} @ {f} GHz, ports {a}-{b}: {e:.5f}")


def _polar(ff: dict, out: Path, name: str, made: list[str]) -> None:
    th, ph = ff["theta"], ff["phi"]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4), subplot_kw={"projection": "polar"},
                             gridspec_kw={"wspace": 0.45})
    peak = np.nanmax(np.maximum(ff["abs_theta_db"], ff["abs_phi_db"]))
    for ax, (cut, title) in zip(axes, ((0.0, r"$\phi = 0^\circ$ plane"), (90.0, r"$\phi = 90^\circ$ plane"))):
        i0 = np.argmin(np.abs(ph - cut))
        i1 = np.argmin(np.abs(ph - (cut + 180) % 360))
        ang = np.deg2rad(np.concatenate([th, 360 - th[::-1]]))
        for k, (key, lbl) in enumerate((("abs_theta_db", r"$E_\theta$"), ("abs_phi_db", r"$E_\phi$"))):
            r = np.concatenate([ff[key][:, i0], ff[key][::-1, i1]])
            ax.plot(ang, np.clip(r, peak - 40, None), color=COLORS[k], ls=STYLES[k], label=lbl)
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_rlim(peak - 40, peak + 1)
        ax.set_rlabel_position(160)
        ax.set_title(title, pad=14)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=2, frameon=False,
               bbox_to_anchor=(0.5, -0.04))
    save(fig, out, name, made)


# ---------------------------------------------------------------- demo data

def _write_ascii(path: Path, curves: list[tuple[dict[str, float], np.ndarray, np.ndarray]], ylabel: str) -> None:
    lines = []
    for params, x, y in curves:
        if params:
            lines.append("#Parameters = {" + "; ".join(f"{k}={v}" for k, v in params.items()) + "}")
        lines += [f'#"Frequency / GHz"\t"{ylabel}"', "#" + "-" * 60]
        lines += [f"{a:.6f}\t{b:.6f}" for a, b in zip(x, y)]
        lines.append("")
    path.write_text("\n".join(lines))


def _demo_s11(f: np.ndarray, shift: float = 0.0, depth: float = 14.0) -> np.ndarray:
    sig = lambda z: 1 / (1 + np.exp(-z))
    return -5 - depth * (sig((f - 3.0 - shift) / 0.15) - sig((f - 11.0 - shift) / 0.2)) + 3 * np.sin(2 * np.pi * f / 2.3)


def write_demo(exp: Path) -> None:
    f = np.linspace(2, 12, 401)
    sweep = lambda name, values: [({name: v, "Wf": 3}, f, _demo_s11(f, (v - values[2]) * 0.25, 10 + 2 * k))
                                  for k, v in enumerate(values)]
    _write_ascii(exp / "single_Lg_sweep.txt", sweep("Lg", [8, 9, 10, 11, 12]), "S1,1 [Magnitude in dB]")
    _write_ascii(exp / "single_R_sweep.txt", sweep("R", [10, 11, 12, 13, 14]), "S1,1 [Magnitude in dB]")
    _write_ascii(exp / "single_gap_sweep.txt", sweep("h", [3, 5, 7, 10, 12]), "S1,1 [Magnitude in dB]")
    _write_ascii(exp / "single_final_s11.txt", [({}, f, _demo_s11(f))], "S1,1 [Magnitude in dB]")
    base_gain = 1.5 + 0.35 * (f - 2)
    _write_ascii(exp / "single_final_gain.txt", [({}, f, base_gain)], "Realized Gain [dBi]")
    _write_ascii(exp / "single_final_eff_tot.txt", [({}, f, 0.85 - 0.02 * (f - 2))], "Tot. Efficiency")
    phase = -np.rad2deg(2 * np.arctan((f - 6.5) / 2.0))
    _write_ascii(exp / "unitcell_phase.txt", [({}, f, phase)], "Phase [deg]")
    _write_ascii(exp / "unitcell_mag.txt", [({}, f, -0.2 - 0.3 * np.exp(-((f - 6.5) / 1.5) ** 2))], "Mag [dB]")
    for case, extra, dip in (("none", 0, 0), ("pec", 1.5, 0.3), ("amc", 3.0, 0.15)):
        _write_ascii(exp / f"single_{case}_s11.txt", [({}, f, _demo_s11(f, dip))], "S1,1")
        _write_ascii(exp / f"single_{case}_gain.txt",
                     [({}, f, base_gain + extra * np.exp(-((f - 6.5) / 3.5) ** 2))], "Realized Gain [dBi]")

    rng = np.random.default_rng(1)
    for case, iso in (("noMS", 20), ("MS", 18)):
        S = np.zeros((f.size, 4, 4), complex)
        for i in range(4):
            S[:, i, i] = 10 ** (_demo_s11(f, 0.05 * i) / 20) * np.exp(-1j * 2 * np.pi * f * (0.3 + 0.01 * i))
        for i, j in combinations(range(4), 2):
            lvl = iso + (0 if (j - i) % 2 else -2) + 3 * np.sin(f + i + j)
            S[:, i, j] = S[:, j, i] = 10 ** (-lvl / 20) * np.exp(-1j * (2 * np.pi * f * 0.4 + rng.uniform(0, 6)))
        rf.Network(frequency=rf.Frequency.from_f(f, unit="ghz"), s=S).write_touchstone(str(exp / f"mimo_{case}"))
        bump = 3.0 if case == "MS" else 0.0
        _write_ascii(exp / f"mimo_{case}_gain.txt", [({}, f, base_gain + bump * np.exp(-((f - 6.5) / 3.5) ** 2))],
                     "Realized Gain [dBi]")
        _write_ascii(exp / f"mimo_{case}_eff_tot.txt", [({}, f, 0.82 - 0.02 * (f - 2) - 0.03 * bump)], "Tot. Eff.")
        for port in range(1, 5):
            for fr in PATTERN_FREQS:
                _write_demo_farfield(exp / "ff" / f"{case}_p{port}_{fr:g}GHz.txt", port, fr, case == "MS")


def _write_demo_farfield(path: Path, port: int, f_ghz: float, reflector: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    th, ph = np.meshgrid(np.deg2rad(np.arange(0, 181, 5)), np.deg2rad(np.arange(0, 360, 5)), indexing="ij")
    rot = np.deg2rad(90 * (port - 1))
    u = np.array([np.cos(rot), np.sin(rot), 0.0])
    pos = 0.02 * np.array([np.cos(rot), np.sin(rot), 0.0])
    t_hat = np.stack([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])
    p_hat = np.stack([-np.sin(ph), np.cos(ph), np.zeros_like(ph)])
    r_hat = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])
    k = 2 * np.pi * f_ghz * 1e9 / 3e8
    af = np.exp(1j * k * np.tensordot(pos, r_hat, axes=1))
    if reflector:
        af = af * (1 + np.exp(1j * (2 * k * 0.008 * np.cos(th) - np.pi / 2))) * (th <= np.pi / 2 + 0.3)
    e_th = np.tensordot(u, t_hat, axes=1) * af + 1e-4
    e_ph = np.tensordot(u, p_hat, axes=1) * af + 1e-4
    db = lambda e: 20 * np.log10(np.abs(e)) + 1.76
    rows = ["Theta [deg.]  Phi   [deg.]  Abs(Dir.)[dBi   ]   Abs(Theta)[dBi   ]  Phase(Theta)[deg.]  "
            "Abs(Phi  )[dBi   ]  Phase(Phi  )[deg.]  Ax.Ratio[dB    ]", "-" * 150]
    tot = 10 * np.log10(np.abs(e_th) ** 2 + np.abs(e_ph) ** 2) + 1.76
    for a in range(th.shape[0]):
        for b in range(th.shape[1]):
            rows.append(f"{np.rad2deg(th[a, b]):10.3f} {np.rad2deg(ph[a, b]):10.3f} {tot[a, b]:12.4e} "
                        f"{db(e_th[a, b]):12.4e} {np.angle(e_th[a, b], deg=True):12.4e} "
                        f"{db(e_ph[a, b]):12.4e} {np.angle(e_ph[a, b], deg=True):12.4e} {40.0:12.4e}")
    path.write_text("\n".join(rows))


# ---------------------------------------------------------------- main

def run(exp: Path, out: Path) -> list[str]:
    out.mkdir(parents=True, exist_ok=True)
    made: list[str] = []
    summary: list[str] = []
    fig_sweeps(exp, out, made, summary)
    fig_single_final(exp, out, made, summary)
    fig_unit_cell(exp, out, made, summary)
    fig_reflector_compare(exp, out, made, summary)
    nets = load_mimo(exp)
    fig_mimo_sparams(nets, out, made, summary)
    fig_mimo_metrics(nets, out, made, summary)
    _gain_eff(exp, out, made, summary, "mimo_gain", {f"mimo_{c}": lbl for c, lbl in CASES.items()})
    fig_patterns(exp, out, made, summary)
    (out / "summary.txt").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))
    print(f"\n{len(made)} figures written to {out}")
    return made


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exports", type=Path, default=ROOT / "exports")
    ap.add_argument("--out", type=Path, default=ROOT / "figures")
    ap.add_argument("--demo", action="store_true", help="generate synthetic CST-format data and plot it")
    args = ap.parse_args()
    if args.demo:
        with tempfile.TemporaryDirectory() as tmp:
            write_demo(Path(tmp))
            run(Path(tmp), args.out.parent / "figures_demo")
    else:
        run(args.exports, args.out)


if __name__ == "__main__":
    main()
