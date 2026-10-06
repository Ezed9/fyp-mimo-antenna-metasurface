#!/usr/bin/env python3
"""Bare-antenna validation: corrected openEMS model vs the team's CST result.

usage: plot_validation.py <out.png> <cst_digitised.csv> <label>=<csv> [<label>=<csv> ...]
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False})
COLORS = ['#104281', '#3987e5', '#86b6ef']

out, cst = sys.argv[1], sys.argv[2]
fig, ax = plt.subplots(figsize=(7.2, 3.7), dpi=170)
c = np.loadtxt(cst, delimiter=',', comments='#')
ax.plot(c[:, 0], c[:, 1], color='#eb6834', lw=2.0, label='CST, team model (digitised from the report figure)')
for k, arg in enumerate(sys.argv[3:]):
    lab, fn = arg.split('=', 1)
    d = np.loadtxt(fn, delimiter=',', skiprows=1)
    ax.plot(d[:, 0], d[:, 1], color=COLORS[k % len(COLORS)], lw=1.8 if k == 0 else 1.2,
            ls='-' if k == 0 else (0, (5, 2)), label=lab)
ax.axhline(-10, color=INK, lw=0.8)
ax.axvspan(2, 15, color='#f0efec', zorder=0, lw=0)
ax.set_xlim(1.5, 16)
ax.set_ylim(-35, 0)
ax.set_xlabel('Frequency (GHz)')
ax.set_ylabel('|S11| (dB)')
ax.set_title('Antenna alone: openEMS (corrected model) vs CST', loc='left', fontsize=9)
ax.legend(fontsize=7.5, loc='lower right')
fig.tight_layout()
fig.savefig(out)
