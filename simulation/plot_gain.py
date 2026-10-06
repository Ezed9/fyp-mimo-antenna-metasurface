#!/usr/bin/env python3
"""Broadside / back realized gain with and without the metasurface (from cpw_ms_gain.py JSON files).

usage: plot_gain.py <out.png> <label>=<gain_json> [<label>=<gain_json> ...]
"""
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
COLORS = ['#8a8983', '#2a78d6', '#eb6834', '#1baf7a']
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False})

out = sys.argv[1]
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.3), dpi=170, sharey=True)
for k, arg in enumerate(sys.argv[2:]):
    lab, fn = arg.split('=', 1)
    rows = json.load(open(fn))['gain']
    f = [r['f_GHz'] for r in rows]
    axs[0].plot(f, [r['G_broadside_dBi'] for r in rows], color=COLORS[k], lw=2, marker='o', ms=4, label=lab)
    axs[1].plot(f, [r['G_back_dBi'] for r in rows], color=COLORS[k], lw=2, marker='o', ms=4, label=lab)
axs[0].set_title('Broadside (+z, away from the metasurface)', loc='left', fontsize=8.5)
axs[1].set_title('Back (-z, towards the metasurface)', loc='left', fontsize=8.5)
for ax in axs:
    ax.set_xlabel('Frequency (GHz)')
    ax.set_xlim(1.5, 15.5)
axs[0].set_ylabel('Realized gain (dBi)')
axs[0].legend(fontsize=7.5, loc='lower left')
fig.tight_layout()
fig.savefig(out)
