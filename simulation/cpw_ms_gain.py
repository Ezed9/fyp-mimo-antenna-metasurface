#!/usr/bin/env python3
"""Realized gain of the antenna with/without the metasurface (openEMS near-to-far-field).

Reuses the geometry and mesh of cpw_ms_openems.build() (half model with the PMC
wall on the feed axis; the NF2FF box mirrors it automatically) and adds a
frequency-domain NF2FF recording box. Reports, per frequency:
  broadside (+z, away from the metasurface) realized gain, back (-z) realized
  gain, the maximum realized gain over the sphere, and |S11|.

usage: cpw_ms_gain.py --case ms --h 20 --out DIR
"""
import argparse
import json
import os
import shutil
import time

import numpy as np

import cpw_ms_openems as M

F_GAIN = np.arange(2.0, 15.01, 1.0) * 1e9


def run(case, h, out_root, threads=4, tag=''):
    name = f"gain_{case}" + (f"_h{h:05.2f}" if case != 'bare' else '') + tag
    sim_path = os.path.join(out_root, name)
    if os.path.isdir(sim_path):
        shutil.rmtree(sim_path)
    FDTD, CSX, port, info = M.build(case, h, 'half', sim_path)
    # recording box 5 mm inside the PML-free region on every open side
    grid = CSX.GetGrid()
    lines = [np.array(grid.GetLines(n)) for n in range(3)]
    start = [lines[0][0], lines[1][10], lines[2][10]]
    stop = [lines[0][-11], lines[1][-11], lines[2][-11]]
    nf = FDTD.CreateNF2FFBox(start=start, stop=stop, frequency=F_GAIN)
    CSX.Write2XML(os.path.join(sim_path, 'geometry.xml'))
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=False, numThreads=threads, verbose=1, exact_endcriteria=True)
    info['runtime_s'] = time.time() - t0

    port.CalcPort(sim_path, F_GAIN)
    zin = port.uf_tot / port.if_tot / 2.0
    s11 = (zin - 50.0) / (zin + 50.0)
    p_inc_full = 2.0 * port.P_inc          # the mirrored half carries the other half of the power

    theta = np.arange(0.0, 181.0, 3.0)
    phi = np.array([0.0, 90.0, 180.0, 270.0])
    res = nf.CalcNF2FF(sim_path, F_GAIN, theta, phi, center=[0, 0, 0])
    rows = []
    for k, f in enumerate(F_GAIN):
        e2 = np.abs(res.E_theta[k]) ** 2 + np.abs(res.E_phi[k]) ** 2      # (theta, phi)
        u = e2 * res.r ** 2 / (2 * 376.730313668)
        g_real = 4 * np.pi * u / p_inc_full[k]
        rows.append(dict(f_GHz=f / 1e9, S11_dB=float(20 * np.log10(abs(s11[k]))),
                         G_broadside_dBi=float(10 * np.log10(g_real[0, 0])),
                         G_back_dBi=float(10 * np.log10(g_real[-1, 0])),
                         G_max_cuts_dBi=float(10 * np.log10(np.max(g_real))),
                         Dmax_dBi=float(10 * np.log10(res.Dmax[k])),
                         eff_rad=float(res.Prad[k] / (2.0 * port.P_acc[k]))))
    info['gain'] = rows
    with open(os.path.join(out_root, name + '.json'), 'w') as fh:
        json.dump(info, fh, indent=1)
    for fn in os.listdir(sim_path):
        p = os.path.join(sim_path, fn)
        if os.path.isfile(p) and os.path.getsize(p) > 20e6:
            os.remove(p)
    for r in rows:
        print(json.dumps(r))
    return info


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--case', default='bare', choices=['bare', 'ms', 'plate'])
    ap.add_argument('--h', type=float, default=20.0)
    ap.add_argument('--out', default='results')
    ap.add_argument('--threads', type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    run(a.case, a.h, a.out, threads=a.threads)
