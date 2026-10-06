#!/usr/bin/env python3
"""openEMS (FDTD) model of the CPW-fed decagon UWB monopole, with or without the
ground-backed double split-ring (SRR) metasurface behind it.

Coordinates follow the team's description (mm):
  x across the board, y along the feed (port at y = -25), z normal to the board.
  Antenna copper is on z = 0 (front face); the antenna FR-4 occupies -1.6 <= z <= 0.
  The metasurface sits behind the antenna: its ring layer faces the antenna at
  z = -1.6 - h, its FR-4 below that, and its full copper ground at z = -3.2 - h.
  h is the air gap between the antenna substrate's back face and the ring layer.

Two model types:
  half : x >= 0 only, PMC wall at x = 0 (the structure and the CPW even mode are
         mirror-symmetric about the feed axis). One 100-ohm lumped port across the
         right CPW slot; its S11 equals the full antenna's 50-ohm S11.
  full : whole structure, openEMS CPW transmission-line port (closer to CST's
         waveguide port). Used to validate the half model.

Copper is modelled as zero-thickness PEC; FR-4 is eps_r = 4.3 with a conductivity
chosen so tan(delta) = 0.025 at 6 GHz.
"""
import argparse
import json
import os
import shutil
import time

import numpy as np
from CSXCAD import ContinuousStructure
from CSXCAD.SmoothMeshLines import SmoothMeshLines
from openEMS import openEMS
from openEMS.physical_constants import C0, EPS0

UNIT = 1e-3
EPS_R, TAND, F_KAPPA = 4.3, 0.025, float(os.environ.get("F_KAPPA", 6e9))
KAPPA = 2 * np.pi * F_KAPPA * EPS0 * EPS_R * TAND

# ---- antenna (team's CST geometry) ----
HALF_BOARD = 25.0
H_SUB = 1.6
W_FEED = 3.0           # strip x = -1.5 .. 1.5
GAP = 0.5              # CPW slots, grounds start at |x| = 2
Y_GND_TOP = -7.0       # grounds: y = -25 .. -7
R_PATCH = 15.0         # decagon circumradius
YC_PATCH = 8.0         # decagon centre
Y_PATCH_BOT = YC_PATCH - R_PATCH * np.cos(np.deg2rad(18.0))   # -6.266, 0.734 mm above the grounds

# ---- metasurface (assumptions marked) ----
MS_X, MS_Y = 100.0, 100.0      # ASSUMED overall size (15 mm rings force >= ~90 mm for 6 x 5 cells)
NX_MS, NY_MS = 5, 6            # ASSUMED: 6 cells along the feed axis, 5 across (from the CST screenshot)
MS_H = 1.6
# (r_in, r_out, split centre angle in degrees); split width SPLIT. Splits on the
# feed axis keep the x = 0 mirror symmetry (ASSUMED orientation and width).
RINGS = [(7.0, 7.5, 270.0), (5.0, 5.5, 90.0)]
SPLIT = 0.5


def decagon(n_pts=10):
    ang = np.deg2rad(np.arange(n_pts) * 36.0)
    return np.array([R_PATCH * np.cos(ang), YC_PATCH + R_PATCH * np.sin(ang)])


def split_ring_polygon(cx, cy, r_in, r_out, split_deg, split_w, n_arc=180):
    """C-shaped polygon whose cut faces are parallel (straight slot of width split_w)."""
    c = np.deg2rad(split_deg)
    d_out = np.arcsin(0.5 * split_w / r_out)
    d_in = np.arcsin(0.5 * split_w / r_in)
    a_out = np.linspace(c + d_out, c + 2 * np.pi - d_out, n_arc)
    a_in = np.linspace(c + 2 * np.pi - d_in, c + d_in, n_arc)
    xs = np.concatenate([cx + r_out * np.cos(a_out), cx + r_in * np.cos(a_in)])
    ys = np.concatenate([cy + r_out * np.sin(a_out), cy + r_in * np.sin(a_in)])
    return np.array([xs, ys])


def ms_centres():
    px, py = MS_X / NX_MS, MS_Y / NY_MS
    cxs = -MS_X / 2 + px * (np.arange(NX_MS) + 0.5)
    cys = -MS_Y / 2 + py * (np.arange(NY_MS) + 0.5)
    return cxs, cys


def fill(lines, lo, hi, step):
    """Equal subdivision (<= step) between consecutive lines inside [lo, hi]."""
    lines = np.unique(np.round(np.asarray(lines, float), 6))
    out = list(lines)
    for a, b in zip(lines[:-1], lines[1:]):
        if a >= lo - 1e-9 and b <= hi + 1e-9 and b - a > step:
            # allow cells up to ~1.35*step rather than creating tiny ones (they shrink the timestep)
            n = max(1, int(np.ceil((b - a) / step - 0.35)))
            out.extend(np.linspace(a, b, n + 1)[1:-1])
    return np.unique(np.round(out, 6))


def prune(lines, min_sp, keep):
    """Drop lines closer than min_sp to a neighbour, never dropping a 'keep' line."""
    lines = np.sort(lines)
    keep = set(np.round(keep, 6))
    out = [lines[0]]
    for v in lines[1:]:
        if v - out[-1] < min_sp:
            if round(v, 6) in keep and round(out[-1], 6) not in keep:
                out[-1] = v
            continue
        out.append(v)
    return np.array(out)


def build(case, h, model, sim_path, f_lo=1.0e9, f_hi=16.0e9, fine=0.5, coarse=2.0,
          margin=45.0, end_crit=1e-4, max_ts=200000, zsub=0.4, fine_ant=None):
    """case: 'bare' | 'ms' (rings + ground) | 'plate' (substrate + ground, no rings)."""
    has_ms = case in ('ms', 'plate')
    FDTD = openEMS(NrTS=max_ts, EndCriteria=end_crit)
    FDTD.SetGaussExcite(0.5 * (f_lo + f_hi), 0.5 * (f_hi - f_lo))
    if model == 'half':
        FDTD.SetBoundaryCond(['PMC', 'PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8'])
    else:
        FDTD.SetBoundaryCond(['PML_8'] * 6)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(UNIT)

    fr4 = CSX.AddMaterial('FR4', epsilon=EPS_R, kappa=KAPPA)
    cu = CSX.AddMetal('copper')

    # ---------------- antenna ----------------
    fr4.AddBox([-HALF_BOARD, -HALF_BOARD, -H_SUB], [HALF_BOARD, HALF_BOARD, 0], priority=1)
    cu.AddBox([-HALF_BOARD, -HALF_BOARD, 0], [-W_FEED / 2 - GAP, Y_GND_TOP, 0], priority=10)
    cu.AddBox([W_FEED / 2 + GAP, -HALF_BOARD, 0], [HALF_BOARD, Y_GND_TOP, 0], priority=10)
    cu.AddBox([-W_FEED / 2, -HALF_BOARD, 0], [W_FEED / 2, Y_PATCH_BOT + 0.5, 0], priority=10)
    dec = decagon()
    cu.AddPolygon(dec, 'z', 0.0, priority=10)

    # ---------------- metasurface ----------------
    ring_x, ring_y = [], []
    if has_ms:
        z_top = -H_SUB - h
        z_gnd = z_top - MS_H
        fr4.AddBox([-MS_X / 2, -MS_Y / 2, z_gnd], [MS_X / 2, MS_Y / 2, z_top], priority=1)
        cu.AddBox([-MS_X / 2, -MS_Y / 2, z_gnd], [MS_X / 2, MS_Y / 2, z_gnd], priority=10)
        if case == 'ms':
            cxs, cys = ms_centres()
            for cx in cxs:
                for cy in cys:
                    for (ri, ro, sd) in RINGS:
                        cu.AddPolygon(split_ring_polygon(cx, cy, ri, ro, sd, SPLIT), 'z', z_top, priority=10)
            rm = [0.5 * (ri + ro) for (ri, ro, _) in RINGS]
            ring_x = [cx + s * r for cx in cxs for r in rm for s in (-1, 1)] + \
                     [cx + s * SPLIT / 2 for cx in cxs for s in (-1, 1)]
            ring_y = [cy + s * r for cy in cys for r in rm for s in (-1, 1)]

    # ---------------- port ----------------
    port_len = 0.5
    if model == 'half':
        port = FDTD.AddLumpedPort(1, 100.0, [W_FEED / 2, -HALF_BOARD, 0],
                                  [W_FEED / 2 + GAP, -HALF_BOARD + port_len, 0], 'x', excite=1.0)
    # (full-model CPW port is added after the mesh exists, it needs the mesh lines)

    # ---------------- mesh ----------------
    ext_x = MS_X / 2 if has_ms else HALF_BOARD
    ext_y = MS_Y / 2 if has_ms else HALF_BOARD
    x_dom = ext_x + margin
    y_dom = ext_y + margin

    x_key = [0.0, W_FEED / 2, W_FEED / 2 + GAP / 2, W_FEED / 2 + GAP, HALF_BOARD,
             R_PATCH * np.cos(np.deg2rad(36)), R_PATCH * np.cos(np.deg2rad(72)), R_PATCH]
    x_key = x_key + [-v for v in x_key]
    if has_ms:
        x_key += [-MS_X / 2, MS_X / 2]
    x_key += ring_x
    y_key = [-HALF_BOARD, -HALF_BOARD + port_len, Y_GND_TOP, Y_PATCH_BOT, HALF_BOARD,
             YC_PATCH, YC_PATCH + R_PATCH * np.sin(np.deg2rad(36)), YC_PATCH - R_PATCH * np.sin(np.deg2rad(36)),
             YC_PATCH + R_PATCH * np.sin(np.deg2rad(72))]
    if has_ms:
        y_key += [-MS_Y / 2, MS_Y / 2]
    y_key += ring_y

    def axis_lines(key, ext, dom, lo_cut):
        k = np.array([v for v in key if lo_cut - 1e-9 <= v <= dom])
        k = prune(np.unique(np.round(k, 6)), 0.2,
                  keep=[0.0, W_FEED / 2, W_FEED / 2 + GAP, -W_FEED / 2, -W_FEED / 2 - GAP,
                        Y_GND_TOP, Y_PATCH_BOT, -HALF_BOARD])
        k = np.unique(np.concatenate([k, [lo_cut if lo_cut > -dom else -dom, dom]]))
        if fine_ant:
            k = fill(k, -HALF_BOARD, HALF_BOARD, fine_ant)
        k = fill(k, -ext, ext, fine)
        return SmoothMeshLines(k, coarse, 1.3, check_symmetry=False)

    x_lines = axis_lines(x_key, ext_x, x_dom, 0.0 if model == 'half' else -x_dom)
    y_lines = axis_lines(y_key, ext_y, y_dom, -y_dom)

    z_air = 45.0
    z_key = [0.0, -H_SUB]
    if has_ms:
        z_key += [-H_SUB - h, -H_SUB - h - MS_H]
    z_bot = min(z_key) - (35.0 if has_ms else z_air)
    z_key += [z_air, z_bot]
    z = np.unique(np.round(z_key, 6))
    z = fill(z, -H_SUB, 0.0, zsub)
    if has_ms:
        z = fill(z, -H_SUB - h - MS_H, -H_SUB - h, zsub)
        z = fill(z, -H_SUB - h, -H_SUB, 1.0)
    z_lines = SmoothMeshLines(z, coarse, 1.3, check_symmetry=False)

    mesh.SetLines('x', x_lines)
    mesh.SetLines('y', y_lines)
    mesh.SetLines('z', z_lines)

    if model == 'full':
        port = FDTD.AddCPWPort(1, cu, [-W_FEED / 2, -HALF_BOARD, 0], [W_FEED / 2, -HALF_BOARD + 6.0, 0],
                               'y', 'x', GAP, excite=1, Feed_R=50.0, FeedShift=1.0, MeasPlaneShift=3.0)

    info = dict(case=case, h=h, model=model,
                nx=len(x_lines), ny=len(y_lines), nz=len(z_lines),
                ncells=int(len(x_lines) * len(y_lines) * len(z_lines)),
                dmin=[float(np.min(np.diff(a))) for a in (x_lines, y_lines, z_lines)],
                dmax=[float(np.max(np.diff(a))) for a in (x_lines, y_lines, z_lines)])
    os.makedirs(sim_path, exist_ok=True)
    CSX.Write2XML(os.path.join(sim_path, 'geometry.xml'))
    return FDTD, CSX, port, info


def run(case, h, model, out_root, threads=4, keep=False, tag='', **kw):
    tag = f"{model}_{case}" + (f"_h{h:05.2f}" if case != 'bare' else '') + tag
    sim_path = os.path.join(out_root, tag)
    if os.path.isdir(sim_path):
        shutil.rmtree(sim_path)
    FDTD, CSX, port, info = build(case, h, model, sim_path, **kw)
    print(json.dumps(info), flush=True)
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=False, numThreads=threads, verbose=1)
    info['runtime_s'] = time.time() - t0

    f = np.linspace(1.0e9, 16.0e9, 1501)
    port.CalcPort(sim_path, f)
    s11 = port.uf_ref / port.uf_inc
    zin = port.uf_tot / port.if_tot
    if model == 'half':
        zin = zin / 2.0   # two mirrored 100-ohm slot ports in parallel
    data = np.column_stack([f / 1e9, 20 * np.log10(np.abs(s11)), np.angle(s11, deg=True), zin.real, zin.imag])
    np.savetxt(os.path.join(out_root, tag + '.csv'), data, delimiter=',',
               header='f_GHz,S11_dB,S11_deg,ReZin_ohm,ImZin_ohm', comments='')
    info.update(metrics(f / 1e9, 20 * np.log10(np.abs(s11))))
    with open(os.path.join(out_root, tag + '.json'), 'w') as fh:
        json.dump(info, fh, indent=1)
    if not keep:
        for fn in os.listdir(sim_path):
            p = os.path.join(sim_path, fn)
            if os.path.isfile(p) and os.path.getsize(p) > 20e6:
                os.remove(p)
    print(json.dumps(info), flush=True)
    return info


def metrics(f, s):
    out = {}
    for lo, hi in ((2.0, 15.0), (2.16, 15.0), (3.1, 10.6)):
        m = (f >= lo) & (f <= hi)
        out[f'max_S11_dB_{lo}_{hi}'] = float(np.max(s[m]))
        out[f'frac_below10_{lo}_{hi}'] = float(np.mean(s[m] <= -10))
    # continuous -10 dB band that contains 6 GHz
    i6 = int(np.argmin(np.abs(f - 6.0)))
    if s[i6] <= -10:
        a = i6
        while a > 0 and s[a - 1] <= -10:
            a -= 1
        b = i6
        while b < len(f) - 1 and s[b + 1] <= -10:
            b += 1
        out['band_lo_GHz'], out['band_hi_GHz'] = float(f[a]), float(f[b])
    above = f[(s > -10) & (f >= 2.0) & (f <= 15.0)]
    out['fail_GHz_ranges'] = ranges(above)
    return out


def ranges(v, step=0.011):
    if len(v) == 0:
        return []
    r, start, prev = [], v[0], v[0]
    for x in v[1:]:
        if x - prev > step:
            r.append([round(float(start), 3), round(float(prev), 3)])
            start = x
        prev = x
    r.append([round(float(start), 3), round(float(prev), 3)])
    return r


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--case', default='bare', choices=['bare', 'ms', 'plate'])
    ap.add_argument('--h', type=float, nargs='*', default=[3.9])
    ap.add_argument('--model', default='half', choices=['half', 'full'])
    ap.add_argument('--out', default='results')
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--fine', type=float, default=0.5)
    ap.add_argument('--end', type=float, default=1e-4)
    ap.add_argument('--zsub', type=float, default=0.4)
    ap.add_argument('--tag', default='')
    ap.add_argument('--fine_ant', type=float, default=None)
    ap.add_argument('--dry', action='store_true', help='build and report mesh only')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for h in (a.h if a.case != 'bare' else [0.0]):
        if a.dry:
            _, _, _, info = build(a.case, h, a.model, os.path.join(a.out, 'dry'), fine=a.fine, zsub=a.zsub, fine_ant=a.fine_ant)
            print(json.dumps(info))
        else:
            run(a.case, h, a.model, a.out, threads=a.threads, fine=a.fine, end_crit=a.end, zsub=a.zsub, tag=a.tag, fine_ant=a.fine_ant)
