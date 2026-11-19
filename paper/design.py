"""Design data for the paper: dimensions, the S11 analysis and the analytical estimates.

Both paper/make_paper_figures.py and paper/build_paper.py read this module, so a number changed here changes the
figures and the text together.

Dimensions marked est=True were read off the team's CST screenshots (paper/cst/), not taken from the CST model:
the CST working-plane grid in both 3D views is 10.9 px per square, and with the 1 mm raster shown in the S11
screenshot that gives a 3.0 mm feed and 0.5 mm CPW slots, the repo's values. The rest follow from the same scale.
They are highlighted in yellow in the paper until the team confirms them; set est=False once checked.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
FIGS = PAPER / "figures"
CST = PAPER / "cst"
EXPORTS = ROOT / "exports" / "paper"

# --------------------------------------------------------------------------- CST exports (optional, fill placeholders)
# The S11 figures in the paper are the CST screenshots themselves (paper/cst/). Their numbers are read from the
# digitised copies below (analysis/digitize_cst_plot.py); a CST "Plot Data (ASCII)" export, if present, is preferred.
S11_MS_SHOT = CST / "cst_s11_with_ms.jpg"                # dips at 5.3, 9.0, 9.9 GHz: antenna with the metasurface
S11_ALONE_SHOT = CST / "cst_s11_no_ms_assumed.jpg"       # dips at 4.1, 7.4, 12.4 GHz: ASSUMED antenna alone
S11_ALONE_ASSUMED = True                                 # set False once the team confirms which model it is
S11_MS_DIGITIZED = EXPORTS / "cst_s11_with_ms_digitized.csv"
S11_ALONE_DIGITIZED = EXPORTS / "cst_s11_no_ms_assumed_digitized.csv"
S11_MS_EXPORT = EXPORTS / "s11_with_ms.txt"
S11_ALONE_EXPORT = EXPORTS / "s11_antenna_alone.txt"

# Directivity against frequency (CST "Directivity, Phi=0.0, Max. Value (Subrange)": the highest directivity in the
# phi = 0 deg plane at each frequency; not gain). Two screenshots; which model each belongs to is ASSUMED from the
# curve shapes (the smooth one as the antenna alone) until the team confirms it.
DIR_ALONE_SHOT = CST / "cst_directivity_no_ms_assumed.png"      # smooth curve, peak about 5.2 dBi near 13.1 GHz
DIR_MS_SHOT = CST / "cst_directivity_with_ms_assumed.png"       # dips near 7.5, 9.6 and 12 GHz, peak 7.0 dBi
DIR_ASSUMED = True                                              # set False once confirmed
DIR_ALONE_DIGITIZED = EXPORTS / "cst_directivity_no_ms_assumed_digitized.csv"
DIR_MS_DIGITIZED = EXPORTS / "cst_directivity_with_ms_assumed_digitized.csv"

# Far-field directivity cuts (phi = 90 deg) supplied as CST screenshots. The values are the read-outs printed in the
# screenshots themselves. Which model each comes from is not confirmed. For the two 5.3 GHz cuts the assignment
# below is ASSUMED: the one whose main lobe points to the front (theta = 2 deg) and has the higher directivity is
# taken as the antenna with the metasurface. "sll_db" is CST's side-lobe level (None when the screenshot gives none).
PATTERNS = [
    {"f": 5.3, "model": "antenna without the metasurface", "shot": CST / "cst_pattern_5p3GHz_lobe176deg.jpg",
     "main_dbi": 3.56, "dir_deg": 176.0, "width_deg": 71.7, "sll_db": None},
    {"f": 5.3, "model": "antenna with the metasurface", "shot": CST / "cst_pattern_5p3GHz_lobe2deg.png",
     "main_dbi": 3.88, "dir_deg": 2.0, "width_deg": 76.8, "sll_db": -1.3},
    {"f": 12.5, "model": None, "shot": CST / "cst_pattern_12p5GHz.jpg",
     "main_dbi": 1.02, "dir_deg": 132.0, "width_deg": 40.9, "sll_db": -2.6},
]
PATTERN_MODEL_CONFIRMED = False


# --------------------------------------------------------------------------- dimensions
@dataclass(frozen=True)
class Dim:
    symbol: str      # mini-markup for the paper, e.g. "W_{s}"
    meaning: str
    value: float     # mm unless stated
    est: bool        # True: read off the screenshot, to be confirmed by the team


# Confirmed by the team on 19 Nov 2026, except R (still read off the screenshot).
ANTENNA = [
    Dim("W_{s}", "substrate width", 27.0, False),
    Dim("L_{s}", "substrate length", 30.0, False),
    Dim("h_{s}", "substrate thickness", 1.6, False),
    Dim("R", "octagon circumradius", 8.7, True),
    Dim("W_{f}", "CPW feed width", 3.0, False),
    Dim("g", "CPW slot width", 0.3, False),
    Dim("L_{g}", "ground length (both grounds)", 11.0, False),
    Dim("W_{g1}", "left ground width", 11.2, False),
    Dim("W_{g2}", "right ground width", 12.2, False),
    Dim("p", "patch-to-ground gap", 0.22, False),
]

METASURFACE = [
    Dim("W_{m}", "metasurface width", 27.0, False),
    Dim("L_{m}", "metasurface length", 30.0, False),
    Dim("t", "metasurface substrate thickness", 1.6, False),
    Dim("W_{p}", "square patch side", 5.0, False),
    Dim("s", "gap between patches", 0.5, False),
    Dim("P", "period (W_{p} + s)", 5.5, False),
]

FR4_EPS = 4.3          # CST "FR-4 (lossy)", as in the rest of the repo
FR4_TAND = 0.025
AIR_GAP = 0.0          # mm: the metasurface board lies directly behind the antenna substrate (confirmed)
MS_COPPER_BACK = False  # confirmed: no copper ground on the back of the metasurface board
# Not stated by the team: which face of the metasurface board carries the patches. Taken as the face that touches
# the antenna substrate (the board's "front"); the paper marks this TO BE CONFIRMED.
MS_PATCH_FACE_CONFIRMED = False


def dim(symbol: str) -> Dim:
    for d in ANTENNA + METASURFACE:
        if d.symbol == symbol:
            return d
    raise KeyError(symbol)


def v(symbol: str) -> float:
    return dim(symbol).value


# --------------------------------------------------------------------------- S11 analysis
def read_two_columns(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """CSV with comment lines, or a CST ASCII export (header lines, then 'f value' pairs)."""
    f, y = [], []
    for line in path.read_text(errors="ignore").splitlines():
        parts = line.replace(",", " ").split()
        if len(parts) < 2:
            continue
        try:
            a, b = float(parts[0]), float(parts[1])
        except ValueError:
            continue
        f.append(a)
        y.append(b)
    return np.array(f), np.array(y)


def s11_with_ms() -> tuple[np.ndarray, np.ndarray, str]:
    if S11_MS_EXPORT.exists():
        f, s = read_two_columns(S11_MS_EXPORT)
        return f, s, "CST export"
    f, s = read_two_columns(S11_MS_DIGITIZED)
    return f, s, "digitized from the CST screenshot"


def directivity() -> tuple[tuple[np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray]]:
    """(f, D) of the antenna alone and of the antenna with the metasurface, read from the two screenshots."""
    return read_two_columns(DIR_ALONE_DIGITIZED), read_two_columns(DIR_MS_DIGITIZED)


def s11_alone() -> tuple[np.ndarray, np.ndarray]:
    return read_two_columns(S11_ALONE_EXPORT if S11_ALONE_EXPORT.exists() else S11_ALONE_DIGITIZED)


@dataclass(frozen=True)
class Band:
    lo: float
    hi: float
    open_top: bool   # True when the band runs past the last simulated frequency

    @property
    def centre(self) -> float:
        return (self.lo + self.hi) / 2

    @property
    def fbw(self) -> float:
        """Fractional bandwidth, %."""
        return 100 * (self.hi - self.lo) / self.centre


def bands(f: np.ndarray, s: np.ndarray, level: float = -10.0, min_width: float = 0.1) -> list[Band]:
    below = s < level
    out, k = [], 0
    while k < len(f):
        if not below[k]:
            k += 1
            continue
        j = k
        while j + 1 < len(f) and below[j + 1]:
            j += 1
        lo = f[k] if k == 0 else f[k - 1] + (level - s[k - 1]) / (s[k] - s[k - 1]) * (f[k] - f[k - 1])
        hi = f[j] if j == len(f) - 1 else f[j] + (level - s[j]) / (s[j + 1] - s[j]) * (f[j + 1] - f[j])
        if hi - lo >= min_width:
            out.append(Band(float(lo), float(hi), j == len(f) - 1))
        k = j + 1
    return out


def dips(f: np.ndarray, s: np.ndarray, below: float = -15.0, half_window: float = 0.25) -> list[tuple[float, float]]:
    """Local minima deeper than `below`, each the lowest point within ±half_window GHz."""
    out = []
    step = float(np.median(np.diff(f)))
    w = max(1, int(round(half_window / step)))
    for i in range(len(s)):
        lo, hi = max(0, i - w), min(len(s), i + w + 1)
        if s[i] < below and s[i] == s[lo:hi].min():
            if not out or f[i] - out[-1][0] > half_window:
                out.append((float(f[i]), float(s[i])))
    return out


def peak_between(f: np.ndarray, s: np.ndarray, lo: float, hi: float) -> tuple[float, float]:
    sel = (f >= lo) & (f <= hi)
    i = int(np.argmax(s[sel]))
    return float(f[sel][i]), float(s[sel][i])


# --------------------------------------------------------------------------- analytical estimates
C0 = 299_792_458.0
MU0 = 4e-7 * math.pi
EPS0 = 8.854_187_8128e-12
ETA0 = MU0 * C0


def octagon_area(r_mm: float) -> float:
    return 2 * math.sqrt(2) * r_mm ** 2


def ray_lower_edge(k: float = 1.15) -> dict[str, float]:
    """Lower band edge of a printed monopole from its equivalent cylindrical monopole (K. P. Ray, IJAP 2008).

    f_L = 7.2 / ((l + r + p) k) GHz with l, r, p in cm. l is the monopole height (2R for an octagon standing on a
    vertex), r = A / (2 pi l) the radius of the cylinder with the same area A, p the gap to the ground and k = 1.15 the
    empirical factor Ray gives for FR-4.
    """
    R, p = v("R"), v("p")
    l = 2 * R
    r = octagon_area(R) / (2 * math.pi * l)
    f = 7.2 / ((l + r + p) / 10 * k)
    return {"l": l, "r": r, "p": p, "k": k, "A": octagon_area(R), "f": f}


def patch_grid() -> dict[str, float]:
    """The ungrounded square-patch array as a capacitive sheet.

    Capacitance between neighbouring patches (Sievenpiper et al., 1999): C = Wp eps0 (e1 + e2) / pi * acosh(P / s),
    with e1, e2 the relative permittivities on the two sides of the patches (FR-4 on both sides when the patches lie
    between the two boards). Without a ground plane there is no inductive return path, so the sheet does not resonate
    as a high-impedance surface. For a plane wave on an unbounded sheet (substrates ignored) the reflection magnitude
    is |Gamma| = b / sqrt(4 + b^2), b = omega C eta0.
    """
    wp, s, per = v("W_{p}") * 1e-3, v("s") * 1e-3, v("P") * 1e-3
    k = wp * EPS0 / math.pi * math.acosh(per / s)
    c_between, c_outer = k * 2 * FR4_EPS, k * (1 + FR4_EPS)

    def gamma(f_ghz: float, c: float) -> float:
        b = 2 * math.pi * f_ghz * 1e9 * c * ETA0
        return b / math.sqrt(4 + b * b)

    return {"C_between_pF": c_between * 1e12, "C_outer_pF": c_outer * 1e12, "gamma": lambda f: gamma(f, c_between),
            "span_mm": 4 * v("W_{p}") + 3 * v("s")}


def wavelength_mm(f_ghz: float) -> float:
    return C0 / (f_ghz * 1e9) * 1e3


# --------------------------------------------------------------------------- services the bands serve (Fig. 6, Table IV)
SERVICES = [  # (label, lo, hi) GHz
    ("5G NR n77 (incl. n78)", 3.3, 4.2),
    ("WiMAX 3.5 GHz", 3.4, 3.6),
    ("C-band satellite downlink", 3.7, 4.2),
    ("5G NR n79", 4.4, 5.0),
    ("5 GHz WLAN", 5.15, 5.85),
    ("X-band satellite uplink", 7.9, 8.4),
    ("X-band radar", 8.0, 12.0),
    ("Ku-band satellite downlink", 10.7, 12.75),
    ("Ku-band VSAT uplink", 14.0, 14.5),
]


def coverage(lo: float, hi: float, bands_: list[Band], f_max: float = 15.0) -> float:
    """Fraction of [lo, hi] inside the -10 dB bands (an open-top band is taken to run to f_max)."""
    covered = sum(max(0.0, min(hi, f_max if b.open_top else b.hi) - max(lo, b.lo)) for b in bands_)
    return covered / (hi - lo)


# --------------------------------------------------------------------------- CPW line (team check, not in the paper)
def _ellip_k(k: float) -> float:
    a, b = 1.0, math.sqrt(1 - k * k)
    for _ in range(30):
        a, b = (a + b) / 2, math.sqrt(a * b)
    return math.pi / (2 * a)


def cpw_z0() -> tuple[float, float]:
    """Characteristic impedance and effective permittivity of the CPW feed on a finite-thickness substrate
    (conformal mapping, Simons 2001): strip W_f, slots g, substrate h_s, no back metal."""
    S, W, h = v("W_{f}"), v("g"), v("h_{s}")
    k0 = S / (S + 2 * W)
    k1 = math.sinh(math.pi * S / (4 * h)) / math.sinh(math.pi * (S + 2 * W) / (4 * h))
    kp = lambda k: math.sqrt(1 - k * k)  # noqa: E731
    q = _ellip_k(kp(k0)) / _ellip_k(k0)
    eeff = 1 + (FR4_EPS - 1) / 2 * (_ellip_k(k1) / _ellip_k(kp(k1))) * q
    return 30 * math.pi / math.sqrt(eeff) * q, eeff


if __name__ == "__main__":
    f, s, src = s11_with_ms()
    print(f"S11 with the metasurface ({src}): {f[0]:.2f}-{f[-1]:.2f} GHz")
    for i, b in enumerate(bands(f, s), 1):
        top = "+" if b.open_top else ""
        print(f"  band {i}: {b.lo:.2f}-{b.hi:.2f}{top} GHz, FBW {b.fbw:.1f} %")
    print("  dips:", ", ".join(f"{a:.2f} GHz ({b:.1f} dB)" for a, b in dips(f, s)))
    print("  Ray lower edge:", {k: round(x, 3) for k, x in ray_lower_edge().items()})
    pg = patch_grid()
    print(f"  patch grid: C = {pg['C_between_pF']:.3f} pF between two FR-4 boards, {pg['C_outer_pF']:.3f} pF facing air; "
          f"array span {pg['span_mm']:g} mm")
    z, e = cpw_z0()
    print(f"  CPW feed: Z0 = {z:.1f} ohm, eps_eff = {e:.2f}")
    bb = bands(f, s)
    for lab, lo, hi in SERVICES:
        print(f"  {lab}: {100 * coverage(lo, hi, bb):.0f} % covered")
