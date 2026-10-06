#!/usr/bin/env python3
"""Summarise and plot the openEMS gap sweep (output of cpw_ms_openems.py).

usage: plot_gap_sweep.py <results_dir> <figure_dir>
Writes gap_sweep_summary.csv into <figure_dir> plus three figures.
"""
import glob
import json
import os
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
BLUE, ORANGE, BARE = '#2a78d6', '#eb6834', '#8a8983'
DIVERGING = LinearSegmentedColormap.from_list(
    'good_bad', ['#0d366b', '#2a78d6', '#9ec5f4', '#f0efec', '#f3b4b1', '#e34948', '#8f1f1f'])

plt.rcParams.update({
    'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2,
    'ytick.color': INK2, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
    'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False,
})


def load(res):
    runs = {}
    for js in glob.glob(os.path.join(res, '*.json')):
        tag = os.path.basename(js)[:-5]
        csv = js[:-5] + '.csv'
        if not os.path.exists(csv):
            continue
        info = json.load(open(js))
        d = np.loadtxt(csv, delimiter=',', skiprows=1)
        runs[tag] = (info, d)
    return runs


def worst(d, lo=2.0, hi=15.0):
    m = (d[:, 0] >= lo) & (d[:, 0] <= hi)
    return float(np.max(d[m, 1]))


def main(res, figdir):
    os.makedirs(figdir, exist_ok=True)
    runs = load(res)
    bare = next((v for k, v in runs.items() if v[0]['case'] == 'bare'), None)
    ms = sorted([v for v in runs.values() if v[0]['case'] == 'ms'], key=lambda v: v[0]['h'])
    plate = sorted([v for v in runs.values() if v[0]['case'] == 'plate'], key=lambda v: v[0]['h'])

    # ---- summary table ----
    def spans(mask, f):
        out, start = [], None
        for i, m in enumerate(mask):
            if m and start is None:
                start = f[i]
            if (not m or i == len(mask) - 1) and start is not None:
                out.append(f'{start:.2f}-{f[i - 1 if not m else i]:.2f}')
                start = None
        return ';'.join(out)

    rows = []
    for name, group in (('bare', [bare] if bare else []), ('ms', ms), ('plate', plate)):
        for info, d in group:
            band = (d[:, 0] >= 2.0) & (d[:, 0] <= 15.0)
            fb = d[band, 0]
            if bare is not None and name != 'bare':
                sb = bare[1][band, 1]
                breaks = spans((d[band, 1] > -10) & (sb <= -10), fb)
                fixes = spans((d[band, 1] <= -10) & (sb > -10), fb)
            else:
                breaks = fixes = ''
            rows.append(dict(case=name, h=info['h'], breaks=breaks, fixes=fixes,
                             worst_2_15=worst(d), worst_216_15=worst(d, 2.16, 15.0),
                             worst_31_106=worst(d, 3.1, 10.6),
                             frac_2_15=info['frac_below10_2.0_15.0'],
                             fail=';'.join(f'{a:.2f}-{b:.2f}' for a, b in info['fail_GHz_ranges']),
                             cells=info['ncells'], runtime_s=round(info.get('runtime_s', 0))))
    with open(os.path.join(figdir, 'gap_sweep_summary.csv'), 'w') as fh:
        keys = list(rows[0].keys())
        fh.write(','.join(keys) + '\n')
        for r in rows:
            fh.write(','.join(f'{r[k]:.3f}' if isinstance(r[k], float) else str(r[k]) for k in keys) + '\n')
    for r in rows:
        print(f"{r['case']:5s} h={r['h']:5.1f}  worst2-15={r['worst_2_15']:6.2f} dB  "
              f"worst3.1-10.6={r['worst_31_106']:6.2f}  below-10 {100*r['frac_2_15']:5.1f}%  fails: {r['fail']}"
              f"  | MS breaks: {r['breaks']}  | MS fixes: {r['fixes']}")

    if not ms:
        return

    # ---- 1. heat map: gap vs frequency ----
    hs = np.array([v[0]['h'] for v in ms])
    f = ms[0][1][:, 0]
    Z = np.array([v[1][:, 1] for v in ms])
    edges = np.concatenate([[hs[0] - (hs[1] - hs[0]) / 2 if len(hs) > 1 else hs[0] - 1],
                            0.5 * (hs[1:] + hs[:-1]),
                            [hs[-1] + (hs[-1] - hs[-2]) / 2 if len(hs) > 1 else hs[0] + 1]])
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=170)
    norm = TwoSlopeNorm(vmin=-30, vcenter=-10, vmax=0)
    pc = ax.pcolormesh(f, edges, np.clip(Z, -30, 0), cmap=DIVERGING, norm=norm, shading='nearest')
    ax.contour(f, hs, Z, levels=[-10], colors=INK, linewidths=0.9)
    for x in (2.0, 15.0):
        ax.axvline(x, color=INK, lw=0.8, ls=(0, (4, 3)))
    ax.set_xlim(1.5, 16)
    ax.set_xlabel('Frequency (GHz)')
    ax.set_ylabel('Air gap h (mm)')
    ax.set_yticks(hs)
    ax.set_yticklabels([f'{h:g}' for h in hs])
    ax.grid(False)
    cb = fig.colorbar(pc, ax=ax, pad=0.02)
    cb.set_label('|S11| (dB)   blue = matched, red = mismatched')
    ax.set_title('|S11| with the metasurface vs air gap (black line = -10 dB; dashed = 2 and 15 GHz)',
                 fontsize=9, color=INK, loc='left')
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, 'gap_sweep_heatmap.png'))
    plt.close(fig)

    # ---- 2. worst-case |S11| in 2-15 GHz vs gap ----
    fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=170)
    ax.plot(hs, [worst(v[1]) for v in ms], color=BLUE, lw=2, marker='o', ms=5,
            label='Antenna + SRR metasurface (ground-backed)')
    if plate:
        ax.plot([v[0]['h'] for v in plate], [worst(v[1]) for v in plate], color=ORANGE, lw=2,
                marker='s', ms=5, label='Antenna + plain copper-backed board (no rings)')
    if bare:
        ax.axhline(worst(bare[1]), color=BARE, lw=1.5, ls=(0, (6, 3)), label='Antenna alone')
    ax.axhline(-10, color=INK, lw=0.8)
    ax.text(hs[-1], -10.4, '-10 dB target', ha='right', va='top', color=INK2, fontsize=8)
    ax.set_xlabel('Air gap h (mm)')
    ax.set_ylabel('Worst |S11| over 2-15 GHz (dB)')
    ax.legend(loc='upper right', fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, 'gap_sweep_worst.png'))
    plt.close(fig)

    # ---- 3. small multiples: S11 curves for selected gaps ----
    pick = [v for v in ms if v[0]['h'] in (3.9, 6.0, 10.0, 15.0, 20.0, 25.0, 30.0)] or ms
    n = len(pick)
    cols = 2 if n > 1 else 1
    rws = int(np.ceil(n / cols))
    fig, axs = plt.subplots(rws, cols, figsize=(7.2, 1.9 * rws + 0.4), dpi=170, sharex=True, sharey=True,
                            squeeze=False)
    for ax, (info, d) in zip(axs.flat, pick):
        if bare:
            ax.plot(bare[1][:, 0], bare[1][:, 1], color=BARE, lw=1.2, label='Antenna alone')
        ax.plot(d[:, 0], d[:, 1], color=BLUE, lw=1.6, label='With metasurface')
        pl = [v for v in plate if abs(v[0]['h'] - info['h']) < 1e-6]
        if pl:
            ax.plot(pl[0][1][:, 0], pl[0][1][:, 1], color=ORANGE, lw=1.2, label='Plain copper-backed board')
        ax.axhline(-10, color=INK, lw=0.7)
        ax.axvspan(2, 15, color='#f0efec', zorder=0, lw=0)
        ax.set_title(f'h = {info["h"]:g} mm   (worst 2-15 GHz: {worst(d):.1f} dB)', fontsize=8.5,
                     loc='left', color=INK)
        ax.set_xlim(1.5, 16)
        ax.set_ylim(-40, 0)
    for ax in axs.flat[n:]:
        ax.axis('off')
    for ax in axs[-1]:
        ax.set_xlabel('Frequency (GHz)')
    for ax in axs[:, 0]:
        ax.set_ylabel('|S11| (dB)')
    handles, labels = axs.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=3, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(figdir, 'gap_sweep_curves.png'))
    plt.close(fig)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
