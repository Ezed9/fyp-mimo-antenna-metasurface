"""Recompute every curve-derived number quoted in the two papers from papers/data/*.csv.

    python papers/check_numbers.py

Run it again after replacing the digitised CSVs with CST ASCII exports: any number in the text that no longer matches
the printout has to be updated in papers/paper1/build_paper1.py or papers/paper2/build_paper2.py.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks
from scipy.special import ellipk

DATA = Path(__file__).resolve().parent / "data"


def load(name: str) -> tuple[np.ndarray, np.ndarray]:
    # Accepts the digitised CSV and a CST "Plot Data (ASCII)" export alike: comment and header lines are skipped,
    # columns may be separated by commas, tabs or spaces.
    rows = []
    for line in (DATA / f"{name}.csv").read_text().splitlines():
        cells = re.split(r"[,;\s]+", line.strip())
        try:
            rows.append((float(cells[0]), float(cells[1])))
        except (ValueError, IndexError):
            continue                                  # comment, header or separator line
    arr = np.array(rows, dtype=float)
    arr = arr[np.argsort(arr[:, 0])]
    return arr[:, 0], arr[:, 1]


def bands(f: np.ndarray, s: np.ndarray, level: float = -10.0) -> list[tuple[float, float, float, float]]:
    """(low edge, high edge, frequency of the minimum, minimum) of every interval with s <= level."""
    below, out, i = s <= level, [], 0
    while i < len(f):
        if not below[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(f) and below[j + 1]:
            j += 1
        lo = f[i] if i == 0 else f[i - 1] + (level - s[i - 1]) * (f[i] - f[i - 1]) / (s[i] - s[i - 1])
        hi = f[j] if j + 1 == len(f) else f[j] + (level - s[j]) * (f[j + 1] - f[j]) / (s[j + 1] - s[j])
        k = i + int(np.argmin(s[i:j + 1]))
        out.append((float(lo), float(hi), float(f[k]), float(s[k])))
        i = j + 1
    return out


def extrema(f: np.ndarray, s: np.ndarray, prominence: float, minima: bool) -> str:
    idx, _ = find_peaks(-s if minima else s, prominence=prominence)
    return ", ".join(f"{s[k]:.1f} at {f[k]:.2f}" for k in idx)


def report_s11(tag: str, case: str) -> None:
    f, s = load(f"{tag}_s11_{case}")
    print(f"  |S11| {case}:")
    for lo, hi, fm, sm in bands(f, s):
        end = ">15" if hi >= f[-1] else f"{hi:.2f}"
        print(f"    band {lo:.2f}-{end} GHz, FBW {200 * (hi - lo) / (hi + lo):.1f} %, lowest {sm:.1f} dB at {fm:.2f} GHz")
    print(f"    dips  (dB at GHz): {extrema(f, s, 1.0, True)}")
    print(f"    humps (dB at GHz): {extrema(f, s, 1.0, False)}")


def report_dir(tag: str, case: str) -> None:
    f, d = load(f"{tag}_dir_{case}")
    print(f"  directivity {case} ({f[0]:.0f}-{f[-1]:.0f} GHz): peak {d.max():.2f} dBi at {f[d.argmax()]:.2f} GHz; "
          f"dips (dBi at GHz): {extrema(f, d, 0.8, True)}")


def cpw(strip: float, slot: float, h: float, er: float, cover: bool) -> tuple[float, float]:
    """Effective permittivity and Z0 of a CPW on a substrate of thickness h (conformal mapping, [Simons, ch. 2]);
    cover=True adds an identical dielectric layer on top."""
    a, b = strip / 2, strip / 2 + slot
    k0 = a / b
    k1 = np.sinh(np.pi * a / (2 * h)) / np.sinh(np.pi * b / (2 * h))
    ratio0 = ellipk(1 - k0 ** 2) / ellipk(k0 ** 2)             # K(k0') / K(k0)
    q = 0.5 * (er - 1) * ellipk(k1 ** 2) / ellipk(1 - k1 ** 2) * ratio0
    eps = 1 + (2 * q if cover else q)
    return float(eps), float(30 * np.pi / np.sqrt(eps) * ratio0)


def paper1() -> None:
    print("PAPER 1 (octagonal monopole, 4 x 4 patch board)")
    for case in ("noms", "ms"):
        report_s11("p1", case)
    for case in ("noms", "ms"):
        report_dir("p1", case)
    f0, d0 = load("p1_dir_noms")
    f1, d1 = load("p1_dir_ms")
    for lo, hi in ((3.42, 6.13), (7.63, 13.23), (13.95, 15.0)):
        g = np.arange(lo, hi, 0.02)
        a, b = np.interp(g, f0, d0), np.interp(g, f1, d1)
        print(f"  mean directivity {lo}-{hi} GHz: alone {a.mean():.2f}, with board {b.mean():.2f} dBi; "
              f"with board lower over {100 * (b < a).mean():.0f} % of the band")
    g = np.arange(3.42, 15.001, 0.02)
    print(f"  mean directivity 3.42-15 GHz: alone {np.interp(g, f0, d0).mean():.2f}, with board "
          f"{np.interp(g, f1, d1).mean():.2f} dBi; at 13.9 GHz: alone {np.interp(13.9, f0, d0):.2f}, with board "
          f"{np.interp(13.9, f1, d1):.2f} dBi; at 13.1 GHz with board {np.interp(13.1, f1, d1):.2f} dBi")
    R, p, k = 9.0, 0.22, 1.15
    l, area = 2 * R, 2 * np.sqrt(2) * R ** 2
    r = area / (2 * np.pi * l)
    f_l = 7.2 / ((l + r + p) / 10 * k)
    print(f"  eq. (1)-(2): l {l:.1f} mm, A {area:.1f} mm2, r {r:.2f} mm, fL {f_l:.2f} GHz "
          f"({100 * (3.52 - f_l) / 3.52:.1f} % below 3.52 GHz)")
    cap = 5e-3 * 8.854e-12 * (4.3 + 1) / np.pi * np.arccosh(5.5 / 0.5)
    for f in (3.42, 10.0):
        b = 2 * np.pi * f * 1e9 * cap * 376.73
        print(f"  eq. (3)-(4): C {cap * 1e12:.3f} pF, |Gamma| {b / np.sqrt(4 + b * b):.2f} at {f} GHz")
    print(f"  CPW 3 mm / 0.3 mm on 1.6 mm FR-4: eps_eff, Z0 = {cpw(3, 0.3, 1.6, 4.3, False)} alone, "
          f"{cpw(3, 0.3, 1.6, 4.3, True)} covered")
    lam = 299.792458 / 3.42
    print(f"  at 3.42 GHz: profile 3.2 mm = {3.2 / lam:.3f} lambda0; array 21.5 mm = {21.5 / lam:.2f} lambda0; "
          f"board {27 / lam:.2f} x {30 / lam:.2f} lambda0")


def paper2() -> None:
    print("\nPAPER 2 (four-port decagonal-monopole MIMO antenna, ring metasurface)")
    for case in ("noms", "ms"):
        report_s11("p2", case)
    for case in ("noms", "ms"):
        report_dir("p2", case)
    f0, s0 = load("p2_s11_noms")
    f1, s1 = load("p2_s11_ms")
    g = np.arange(1.8, 15.001, 0.02)
    diff = np.interp(g, f1, s1) - np.interp(g, f0, s0)
    print(f"  |S11| with minus without, 1.8-15 GHz: mean {diff.mean():+.2f} dB, rms {np.sqrt((diff ** 2).mean()):.2f} dB")
    lo = bands(f0, s0)[0][0] + 0.1
    lin = 10 ** (np.interp(f0, f1, s1)[f0 >= lo] / 20) - 10 ** (s0[f0 >= lo] / 20)
    print(f"  rms change of the linear |S11| from {lo:.2f} GHz to 15 GHz: {np.sqrt((lin ** 2).mean()):.3f}")
    f0, d0 = load("p2_dir_noms")
    f1, d1 = load("p2_dir_ms")
    g = np.arange(6.0, 10.001, 0.05)
    a, b = np.interp(g, f0, d0), np.interp(g, f1, d1)
    print(f"  directivity 6-10 GHz: mean without {a.mean():.2f}, with {b.mean():.2f} dBi (difference "
          f"{(b - a).mean():+.2f} dB); largest rise {(b - a).max():+.2f} dB at {g[(b - a).argmax()]:.2f} GHz; "
          f"largest fall {(b - a).min():+.2f} dB at {g[(b - a).argmin()]:.2f} GHz; "
          f"with > without over {100 * (b > a).mean():.0f} % of the range")
    print(f"  CPW 3 mm / 0.5 mm on 1.6 mm FR-4: eps_eff, Z0 = {cpw(3, 0.5, 1.6, 4.3, False)}")


if __name__ == "__main__":
    paper1()
    paper2()
