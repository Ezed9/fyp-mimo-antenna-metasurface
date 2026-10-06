#!/usr/bin/env python3
"""Bare-antenna validation figure: openEMS at three mesh densities and two port models vs the CST features."""
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False})
res = sys.argv[1] if len(sys.argv) > 1 else 'results/validation'
out = sys.argv[2] if len(sys.argv) > 2 else 'results'
runs = [('half_bare', '0.5 mm mesh, 0.68 M cells', '#9ec5f4', 1.2),
        ('full_bare', '0.5 mm mesh, full model + CPW port', '#86b6ef', 1.2),
        ('half_bare_fine', '0.25 mm mesh, 2.2 M cells', '#3987e5', 1.4),
        ('half_bare_vfine', '0.17 mm mesh, 4.9 M cells', '#104281', 2.0)]
fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=170)
for tag, lab, col, lw in runs:
    d = np.loadtxt(os.path.join(res, tag + '.csv'), delimiter=',', skiprows=1)
    ax.plot(d[:, 0], d[:, 1], color=col, lw=lw, label='openEMS: ' + lab)
# CST features read from figures/cst_single_final_s11_markers.png
cst_pts = [(2.1615, -10.0), (2.7275, -32.65), (4.7824, -21.18), (6.5, -10.3), (9.2265, -22.56),
           (12.2, -10.5), (14.32, -27.07), (15.734, -10.0)]
ax.plot(*zip(*cst_pts), ls='none', marker='D', ms=5, mfc='#eb6834', mec='white', mew=0.8,
        label='CST (team): band edges, dips, weak points')
ax.axhline(-10, color=INK, lw=0.8)
ax.axvspan(10.8, 13.3, color='#f3b4b1', alpha=0.35, lw=0)
ax.text(12.05, -2.2, 'solvers disagree\n(openEMS ~ -7.3 dB)', ha='center', va='top', fontsize=7.5, color=INK2)
ax.set_xlim(1.5, 16)
ax.set_ylim(-35, 0)
ax.set_xlabel('Frequency (GHz)')
ax.set_ylabel('|S11| (dB)')
ax.set_title('Bare antenna: openEMS mesh-convergence runs vs the team\'s CST result', loc='left', fontsize=9)
ax.legend(fontsize=7, loc='lower right', ncol=1)
fig.tight_layout()
fig.savefig(os.path.join(out, 'bare_validation.png'))
