"""Build Paper 2 (.docx, IEEE conference format): two-port CPW-fed decagonal-monopole MIMO antenna backed by a
double-ring metasurface. Simulation study; every result comes from the CST runs the authors supplied.

    python papers/make_figures.py && python papers/paper2/build_paper2.py

No result is typed by hand: the numbers are computed at build time from papers/data/p2_*.csv, and the design facts
come from papers/paper2/design.py. The paper covers ports 1 and 2 (the lower row). Ports 3 and 4 (the upper row) are
left out because their simulated reflection coefficients are not passive; build_paper2_fourport_draft.py is the
earlier four-port draft that shows them.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import mimo_results  # noqa: E402
from check_numbers import bands, cpw, load  # noqa: E402
from design import VERIFY, number, value  # noqa: E402
from ieee_docx import Paper  # noqa: E402
from literature_text import COMPARISON_ROWS, review_metasurface, review_mimo  # noqa: E402
from references import REFS  # noqa: E402

FIG = HERE / "figures"
SHOTS = HERE / "cst_screenshots"
OUT = HERE / "Paper2_TwoPort_Decagonal_MIMO_Metasurface.docx"

TITLE = ("A Wideband Two-Port CPW-Fed Decagonal Monopole MIMO Antenna Backed by a Double-Ring Metasurface: "
         "A Simulation Study")
AFFIL = ("Department of Electronics and Communication Engineering", "National Institute of Technology Silchar",
         "Silchar, Assam 788010, India")
AUTHORS = [[("Chanswarang Boro", *AFFIL), ("Nishit Baishya", *AFFIL), ("Anushka Dam", *AFFIL)],
           [("Sanjana", *AFFIL), ("Sovan Bhattacharya", *AFFIL), ("Ujjal Chakraborty", *AFFIL)]]

# CST lobe read-outs of the two polar plots (phi = 90 deg cut, 7.4 GHz, port 1), copied from the screenshots.
PATTERN = {"f": "7.4", "noMS": {"mag": "3.62", "dir": "156", "hpbw": "21.2", "sll": "0.6"},
           "MS": {"mag": "4.14", "dir": "6", "hpbw": "21.4", "sll": "2.3"}}


class Citations:
    """IEEE numbering in order of first citation: c('a', 'b') -> '[3], [4]' (runs of three or more become ranges)."""

    def __init__(self) -> None:
        self.order: list[str] = []

    def __call__(self, *keys: str) -> str:
        for key in keys:
            if key not in REFS:
                raise KeyError(f"no reference '{key}' in references.py")
            if key not in self.order:
                self.order.append(key)
        nums = sorted(self.order.index(key) + 1 for key in keys)
        parts, i = [], 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
                j += 1
            parts.append(f"[{nums[i]}]–[{nums[j]}]" if j - i >= 2 else ", ".join(f"[{n}]" for n in nums[i:j + 1]))
            i = j + 1
        return ", ".join(parts)

    def listing(self) -> list[str]:
        return [REFS[key] for key in self.order]


def match(case: str) -> dict:
    """Bands, mismatched regions inside the range, thin margins and the lowest value of one |S11| curve."""
    f, s = load(f"p2_s11_{case}")
    bs = bands(f, s)
    gaps = []
    for (_, hi, _, _), (lo, _, _, _) in zip(bs, bs[1:]):
        m = (f > hi) & (f < lo)
        k = int(np.argmax(s[m]))
        gaps.append((hi, lo, float(f[m][k]), float(s[m][k])))
    k = int(np.argmin(s))
    humps, _ = find_peaks(s, prominence=1.0)
    thin = [(float(f[i]), float(s[i])) for i in humps if -11.0 < s[i] <= -10.0 and f[i] > bs[0][0]]
    return {"f": f, "s": s, "bands": bs, "gaps": gaps, "min": (float(f[k]), float(s[k])), "fmax": float(f[-1]),
            "fmin": float(f[0]), "thin": thin}


def band_phrase(m: dict) -> str:
    parts = []
    for lo, hi, _, _ in m["bands"]:
        parts.append(f"from {lo:.2f} GHz to beyond {m['fmax']:.0f} GHz" if hi >= m["fmax"]
                     else f"from {lo:.2f} to {hi:.2f} GHz")
    return " and ".join(parts)


def band_cell(m: dict) -> str:
    return "\n".join(f"{lo:.2f} to >{m['fmax']:.0f}" if hi >= m["fmax"] else f"{lo:.2f}–{hi:.2f}"
                     for lo, hi, _, _ in m["bands"])


def db(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace("-", "−")


def signed(x: float, digits: int = 1) -> str:
    return ("+" if x >= 0 else "−") + f"{abs(x):.{digits}f}"


def at_most(x: float, digits: int = 2) -> str:
    """x rounded UP, for statements of the form 'below ...' or 'at most ...'."""
    q = 10 ** digits
    return f"{np.ceil(x * q - 1e-9) / q:.{digits}f}"


def at_least(x: float, digits: int = 1) -> str:
    """x rounded DOWN, for statements of the form 'at least ...'."""
    q = 10 ** digits
    return f"{np.floor(x * q + 1e-9) / q:.{digits}f}"


def spans(ranges: list[tuple[float, float]]) -> str:
    return " and ".join(f"from {a:.2f} to {b:.2f} GHz" for a, b in ranges)


def directivity() -> dict:
    f0, d0 = load("p2_dir_noms")
    f1, d1 = load("p2_dir_ms")
    lo, hi = max(f0[0], f1[0]), min(f0[-1], f1[-1])
    g = np.arange(lo, hi + 1e-9, 0.05)
    a, b = np.interp(g, f0, d0), np.interp(g, f1, d1)
    diff = b - a
    uwb = (f0 >= 3.1) & (f0 <= 10.6)
    at = float(PATTERN["f"])
    return {"lo": lo, "hi": hi, "mean0": a.mean(), "mean1": b.mean(), "mean_diff": diff.mean(),
            "peak0": (float(g[a.argmax()]), float(a.max())), "peak1": (float(g[b.argmax()]), float(b.max())),
            "peak0_full": (float(f0[d0.argmax()]), float(d0.max())),
            "rise": (float(g[diff.argmax()]), float(diff.max())), "fall": (float(g[diff.argmin()]), float(diff.min())),
            "frac_higher": float((diff > 0).mean()), "uwb_range": (float(d0[uwb].min()), float(d0[uwb].max())),
            "min1": (float(g[b.argmin()]), float(b.min())),
            "at_pattern": (float(np.interp(at, f0, d0)), float(np.interp(at, f1, d1)))}


def build() -> Path:
    c, v = Citations(), value
    m0, m1, d = match("noms"), match("ms"), directivity()
    mag = mimo_results.load_magnitudes()
    tp = mimo_results.two_port_bounds(mag)
    figs = mimo_results.two_port_figures(mag, tp, FIG)
    gap0, gap1 = m0["gaps"][0], m1["gaps"][0]
    lam = lambda f_ghz: 299.79 / f_ghz                                       # free-space wavelength, mm
    f_lo = m0["bands"][0][0]
    z0 = cpw(number("W_f"), number("g"), number("h_sub"), number("eps_r"), False)[1]
    height = 2 * number("R") * np.cos(np.radians(18))
    area = 5 * number("R") ** 2 * np.sin(np.radians(36))
    r_eq = area / (2 * np.pi * height)
    f_ray = 7.2 / ((height + r_eq + number("p")) / 10 * 1.15)
    s21 = tp["s21_max"]
    a, b = PATTERN["noMS"], PATTERN["MS"]
    board = f"{v('board_x')} mm × {v('board_y')} mm"

    p = Paper()
    p.title(TITLE)
    p.authors(AUTHORS)

    # ------------------------------------------------------------------------------------------------ abstract
    p.abstract(
        "A two-port multiple-input multiple-output (MIMO) antenna made of two coplanar-waveguide (CPW)-fed decagonal "
        "printed monopoles on FR-4 is studied by full-wave simulation, alone and with a 6 × 5 array of concentric "
        f"double split rings on a second FR-4 board placed {v('gap')} mm behind it. The ring board has no backing "
        f"conductor. Without the metasurface, port 1 is matched (|*S*_{{11}}| ≤ −10 dB) {band_phrase(m0)}, the "
        f"limit of the simulation; in between, |*S*_{{11}}| rises to {db(gap0[3])} dB. With the metasurface the "
        f"match is almost unchanged, and port 2 is matched from {tp['s22_matched'][0][0]:.2f} GHz to beyond "
        f"{m1['fmax']:.0f} GHz. The isolation between the two ports with the metasurface is at least 15 dB over "
        f"{100 * tp['s21_share_15']:.0f}% of the matched range but falls to {db(-s21[1])} dB at {s21[0]:.2f} GHz, "
        "and the upper bound of the envelope correlation coefficient obtained from the S-parameter magnitudes is "
        f"below 0.01 over {100 * tp['ecc_share_001']:.0f}% of the range and nowhere above {at_most(tp['ecc_max'][1])}. "
        f"Over {d['lo']:.0f}–{d['hi']:.0f} GHz, the maximum directivity in the *φ* = 0° plane changes by "
        f"{signed(d['mean_diff'])} dB on average with the metasurface (between {signed(d['fall'][1])} and "
        f"{signed(d['rise'][1])} dB), and its peak rises from {d['peak0'][1]:.1f} to {d['peak1'][1]:.1f} dBi. The "
        "unbacked ring metasurface therefore changes the direction of the radiation at individual frequencies but "
        "does not raise the level of the directivity, and the performance of the antenna is limited by the "
        "coupling at the lower end of the band.")
    p.keywords("CPW-fed antenna, decagonal monopole, envelope correlation coefficient, metasurface, MIMO antenna, "
               "split-ring resonator, ultra-wideband antenna")

    # ------------------------------------------------------------------------------------------------ I
    p.heading("I. Introduction")
    p.body(
        "Multiple-input multiple-output (MIMO) operation raises the capacity and the reliability of a wireless link "
        "without additional spectrum, provided that the antenna elements are well matched and weakly coupled "
        f"{c('sharawi_apm')}. For wideband and ultra-wideband (UWB, 3.1–10.6 GHz {c('fcc')}) terminals, the elements "
        "are usually printed monopoles, and those fed by a coplanar waveguide (CPW) are attractive because the feed "
        f"line and its ground planes lie on one side of the substrate {c('simons', 'ray')}. The difficulty is that "
        "the elements of a compact MIMO antenna share one board, and the coupling between them must stay low over "
        "the whole band.")
    p.body(review_mimo(c))
    p.body(review_metasurface(c))
    p.body(
        "This paper reports the simulated behaviour of two parallel CPW-fed decagonal monopoles that share one "
        "ground conductor, and examines with the same model what a 6 × 5 metasurface of concentric double split "
        "rings without a backing conductor, placed behind the antenna, changes. The reflection coefficient, the "
        "coupling between the ports, the diversity metrics that follow from them, the directivity and the radiation "
        "pattern are reported as obtained, including where the metasurface brings no benefit. Section II describes "
        "the design, Section III the results and their limitations, and Section IV concludes the paper.")

    # ------------------------------------------------------------------------------------------------ II
    p.heading("II. Antenna Design")
    p.subheading("A. Radiating Element")
    p.body(
        "Each of the two elements is a regular decagon of circumradius *R* with a flat side towards the feed, "
        f"printed on an FR-4 substrate (*ε*_{{r}} = {v('eps_r')}, tan *δ* = {v('tan_d')}) of thickness *h*_{{s}}. It "
        "is fed by a CPW line with a strip of width *W*_{f} and slots of width *g*, between two ground planes of "
        "width *W*_{g} and length *L*_{g}; the side of the decagon that faces the feed lies at a distance *p* from "
        "the ground edge, and the back of the substrate carries no copper. The dimensions are listed in Table I. "
        f"With a {v('W_f')} mm strip and {v('g')} mm slots, the conformal-mapping expressions of {c('simons')} give "
        f"a line impedance of {z0:.0f} Ω. The lower edge of the band of such a monopole can be estimated by replacing "
        f"the patch with a cylindrical monopole of the same height and area {c('ray')}:")
    p.equation(r"f_L = \frac{7.2}{(l + r + p)\,k}\ \text{GHz}")
    p.body(
        f"where *l* = 2*R* cos 18° = {height:.1f} mm is the height of the decagon, *r* = *A*/(2π*l*) = {r_eq:.1f} mm "
        f"the radius of the equivalent cylinder and *A* = 5*R*^{{2}} sin 36° = {area:.0f} mm^{{2}} the area of the "
        f"decagon, all lengths taken in centimetres in (1), and *k* = 1.15 for FR-4 {c('ray')}. Equation (1) gives "
        f"*f*_{{L}} ≈ {f_ray:.2f} GHz.", cont=True)
    p.table("Dimensions of the Antenna and the Metasurface (mm)", [
        ["Parameter", "*R*", "*W*_{f}", "*g*", "*L*_{g}", "*W*_{g}", "*p*"],
        ["Value", v("R"), v("W_f"), v("g"), v("L_g"), v("W_g"), v("p")],
        ["Parameter", "*h*_{s}", "*D*", "*r*_{o}", "*r*_{i}", "*w*", "*s*_{o}"],
        ["Value", v("h_sub"), v("pitch"), v("r_out"), v("r_in"), v("w_ring"), v("split_out")],
        ["Parameter", "*s*_{i}", "*a*_{x}", "*a*_{y}", "*h*", "", ""],
        ["Value", v("split_in"), v("pitch_x"), v("pitch_y"), v("gap"), "", ""],
    ], [0.74, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44], header_rows=0, bold_first_col=True,
        note="*D*: spacing of the two feed lines. *r*_{o}, *r*_{i}: outer radii of the outer and inner rings. *w*: ring "
             "strip width. *s*_{o}, *s*_{i}: splits of the outer and inner rings. *a*_{x}, *a*_{y}: cell periods. "
             "*h*: air gap between the two boards.")
    p.subheading("B. Two-Port Arrangement")
    p.body(
        "The two elements are placed side by side along the lower edge of the board, as shown in Fig. 1(a), and are "
        "fed from that edge through ports 1 and 2. They are parallel and have the same polarisation. Their feed "
        f"lines are *D* = {v('pitch')} mm apart, which is {number('pitch') / lam(f_lo):.2f} free-space wavelength at "
        f"{f_lo:.2f} GHz, and the adjacent ground planes of the two elements meet between them and form one "
        "conductor, so that the two ports share a common ground.")
    p.body(
        f"The board, which fits in an outline of {board}, also carries a second row of two elements of the same "
        f"kind with a circumradius of {v('R_upper')} mm, fed from the upper edge through ports 3 and 4. Their "
        f"patches face those of the lower row at a distance of about {v('d_face')} mm, and the upper half of the "
        f"board is displaced sideways by about {v('board_step')} mm. These two elements are present in every "
        "simulation reported here, with their ports terminated, but they are not evaluated in this paper: the "
        "results concern ports 1 and 2.")
    p.figure([FIG / "fig_layout_ports.png", SHOTS / "metasurface_design.png"],
             "Top views of the simulated model (CST Studio Suite): (a) antenna board with the port numbers, "
             "(b) 6 × 5 double-ring metasurface.", width_in=1.62, sublabels=True, side_by_side=True)
    p.subheading("C. Metasurface")
    cell_lo = min(number("pitch_x"), number("pitch_y")) / lam(d["lo"])
    cell_hi = max(number("pitch_x"), number("pitch_y")) / lam(d["hi"])
    p.body(
        "The metasurface of Fig. 1(b) is a 6 × 5 array of cells, each made of two concentric copper rings of strip "
        f"width *w* = {v('w_ring')} mm: an outer ring of outer radius *r*_{{o}} = {v('r_out')} mm with a split of "
        f"{v('split_out')} mm, and an inner ring of outer radius *r*_{{i}} = {v('r_in')} mm with a split of "
        f"{v('split_in')} mm. The cells repeat every {v('pitch_x')} mm along the rows and about every "
        f"{v('pitch_y')} mm along the columns. The array is printed on an FR-4 board of thickness 1.6 mm and of the "
        "same outline as the antenna board, which has no copper on its rear face. The board is placed parallel to "
        f"the antenna, at an air gap of *h* = {v('gap')} mm from the back of the antenna substrate, with the rings "
        f"towards the antenna. The gap is {number('gap') / lam(f_lo):.3f} free-space wavelength at {f_lo:.2f} GHz "
        f"and {number('gap') / lam(d['lo']):.2f}–{number('gap') / lam(d['hi']):.2f} wavelength over "
        f"{d['lo']:.0f}–{d['hi']:.0f} GHz.")
    p.body(
        "A closed ring resonates first when its circumference is about one guided wavelength, and a split lowers "
        "the first resonance to about half that frequency. With an effective permittivity of (*ε*_{r} + 1)/2 = 2.65, "
        "the outer ring is one wavelength long at about 4.0 GHz and the inner ring at about 5.6 GHz, so the first "
        f"resonances of the split rings {c('pendry')} lie between about 2 and 6 GHz. In the "
        f"{d['lo']:.0f}–{d['hi']:.0f} GHz range, in which the directivity is compared in Section III, the rings are at "
        f"higher-order resonances and the cell period is {cell_lo:.2f}–{cell_hi:.2f} free-space wavelength, so the "
        "array is not electrically dense there. Without a backing conductor it cannot form a high-impedance surface "
        f"{c('sievenpiper')} either: it is a partly transparent sheet of resonant rings, which reflects appreciably "
        "only near its resonances. The reflection and the transmission of the cell have not been computed.")
    p.subheading("D. Simulation Setup")
    p.body(
        f"The model is simulated in CST Studio Suite {v('cst_version')} with the {v('solver')} solver from "
        f"{m0['fmin']:.0f} to {m0['fmax']:.0f} GHz, with a waveguide port at the end of each CPW line and open "
        "boundaries. The antenna lies in the *xy* plane with the feed lines along *y*, and *θ* is measured from the "
        "normal to the board. The far field is evaluated with port 1 excited and the other ports terminated. The "
        "far-field quantity is the directivity, which does not include the dielectric and conductor losses or the "
        "mismatch.")

    # ------------------------------------------------------------------------------------------------ III
    p.heading("III. Results and Discussion")
    p.subheading("A. Reflection Coefficient")
    thin = ("Inside the matched ranges the margin is small at " +
            " and ".join(f"{fq:.1f} GHz ({db(val)} dB)" for fq, val in m0["thin"][:2]) + ". ") if m0["thin"] else ""
    p.body(
        "The simulated reflection coefficient of port 1 is shown in Fig. 2. Without the metasurface, "
        f"|*S*_{{11}}| is at or below −10 dB {band_phrase(m0)}, the upper limit of the simulation. Between the two "
        f"ranges it rises to {db(gap0[3])} dB at {gap0[2]:.1f} GHz. The lowest value is {db(m0['min'][1])} dB at "
        f"{m0['min'][0]:.2f} GHz. " + thin +
        f"The lower band edge, {f_lo:.2f} GHz, is {100 * (f_ray - f_lo) / f_ray:.0f}% below the estimate of (1), "
        "which is made for a single monopole, whereas here the ground conductor is shared by two elements.")
    p.figure(FIG / "fig_s11.png",
             "Simulated reflection coefficient of port 1 without and with the metasurface. The dotted line marks "
             "−10 dB.", width_in=3.4)
    f, s0, s1 = m0["f"], m0["s"], np.interp(m0["f"], m1["f"], m1["s"])
    lin = 10 ** (s1[f >= f_lo + 0.1] / 20) - 10 ** (s0[f >= f_lo + 0.1] / 20)
    p.body(
        f"With the metasurface, |*S*_{{11}}| is at or below −10 dB {band_phrase(m1)}, and the highest value "
        f"between the two ranges is {db(gap1[3])} dB at {gap1[2]:.1f} GHz. The mismatched region thus narrows from "
        f"{gap0[1] - gap0[0]:.2f} to {gap1[1] - gap1[0]:.2f} GHz, but it does not close. The lower band edge moves "
        f"from {m0['bands'][0][0]:.2f} to {m1['bands'][0][0]:.2f} GHz. The minima move down by 0.1–0.3 GHz and "
        f"change in depth, the deepest from {db(m0['min'][1])} to {db(m1['min'][1])} dB, but away from the minima "
        "the two curves follow each other: from the lower band edge to the end of the range, the "
        f"root-mean-square change of the linear |*S*_{{11}}| is {np.sqrt((lin ** 2).mean()):.2f}. The metasurface "
        "therefore leaves the matched ranges almost as they are. Since an upper band edge is not reached within "
        "the simulated range, no fractional bandwidth is quoted.")
    p.body(
        "The reflection coefficient of port 2 with the metasurface is shown in Fig. 3. It follows that of port 1 "
        f"closely, as expected of two nominally identical elements, and is at or below −10 dB from "
        f"{tp['s22_matched'][0][0]:.2f} GHz to beyond {m1['fmax']:.0f} GHz without interruption. Both ports are "
        f"thus matched from {tp['lower_edge']:.2f} GHz upwards, except for port 1 between {gap1[0]:.2f} and "
        f"{gap1[1]:.2f} GHz; this is the range referred to below as the matched range.")
    p.figure(figs["sparams"],
             "Simulated S-parameters of ports 1 and 2 with the metasurface. The dotted line marks −10 dB.",
             width_in=3.4)
    p.subheading("B. Mutual Coupling")
    above_52 = float(mag["s21"][mag["f"] >= tp["s21_above_m15"][2][1]].max())
    p.body(
        "The transmission coefficient between the two ports with the metasurface is also shown in Fig. 3. The "
        f"coupling is strongest at the lower end of the band: |*S*_{{21}}| reaches {db(s21[1])} dB at "
        f"{s21[0]:.2f} GHz, where {100 * 10 ** (s21[1] / 10):.0f}% of the power incident at port 1 is delivered to "
        f"port 2, and it is above −10 dB {spans(tp['s21_above_m10'])}. Above {tp['s21_above_m15'][2][1]:.1f} GHz the "
        f"isolation is at least {at_least(-above_52)} dB, and above {tp['s21_above_m15'][-1][1]:.1f} GHz at least 15 dB. "
        f"Over the whole matched range, the isolation is at least 15 dB at {100 * tp['s21_share_15']:.0f}% of the "
        "frequencies. The weak isolation at the lower end is the consequence of the arrangement: the two monopoles "
        "are parallel and co-polarised, less than a third of a wavelength apart at the lower band edge, and they "
        "share their ground conductor, with no decoupling structure between them.")
    p.subheading("C. Diversity Performance")
    p.body(
        "The envelope correlation coefficient (ECC) of the two ports is computed from the S-parameters as "
        f"{c('blanch')}")
    p.equation(r"\rho_e = \frac{|\overline{S_{11}}\,S_{12} + \overline{S_{21}}\,S_{22}|^{2}}"
               r"{(1 - |S_{11}|^{2} - |S_{21}|^{2})(1 - |S_{22}|^{2} - |S_{12}|^{2})}")
    p.body(
        "where the bar denotes the complex conjugate. Only the magnitudes of the S-parameters are used here. The "
        "numerator of (2) depends on their phases, but it cannot exceed the value it takes when its two terms add "
        "in phase, so that, with |*S*_{12}| = |*S*_{21}|,", cont=True)
    p.equation(r"\rho_e \le \frac{(|S_{11}| + |S_{22}|)^{2}\,|S_{21}|^{2}}"
               r"{(1 - |S_{11}|^{2} - |S_{21}|^{2})(1 - |S_{22}|^{2} - |S_{21}|^{2})}")
    p.body(
        f"The right-hand side of (3) is plotted in Fig. 4. It is below 0.01 at {100 * tp['ecc_share_001']:.0f}% of "
        f"the frequencies of the matched range and has its highest value, {tp['ecc_max'][1]:.2f}, at the lower band "
        f"edge, {tp['ecc_max'][0]:.2f} GHz, well below the limit of 0.5 commonly required {c('sharawi_apm')}. The "
        f"corresponding apparent diversity gain, 10(1 − *ρ*_{{e}})^{{1/2}} dB {c('dg')}, is at least "
        f"{at_least(tp['dg_min'], 2)} dB. The same bound applied to the channel capacity loss, "
        f"−log_{{2}} det(**I** − **S**^{{H}}**S**) {c('ccl')}, where **S** is the S-matrix of the two ports, **I** the "
        "identity matrix and H the conjugate transpose, gives at most "
        f"{at_most(tp['ccl_max'][1], 1)} bit/s/Hz at the lower band edge; it is below 0.4 bit/s/Hz at "
        f"{100 * tp['ccl_share_04']:.0f}% of the frequencies and exceeds that value {spans(tp['ccl_above_04'])}, "
        "where the coupling is strongest.", cont=True)
    p.figure(figs["ecc"],
             "Upper bound (3) of the envelope correlation coefficient of ports 1 and 2 with the metasurface, over the "
             "matched range. The dotted line marks 0.5.", width_in=3.4)
    p.body(
        "Equation (2) assumes a lossless antenna in a uniform multipath environment. On a lossy FR-4 substrate it "
        "underestimates the correlation, and it does not account for the power absorbed in the substrate and in "
        f"the terminated elements of the upper row {c('hallbjorner', 'sharawi_misuse')}; the value obtained from "
        f"the far fields {c('vaughan')} is the reliable one and remains to be computed.")
    p.subheading("D. Directivity")
    p.body(
        "Fig. 5 shows the simulated directivity of port 1 against frequency. The quantity plotted is the highest "
        "directivity found in the *φ* = 0° plane at each frequency; it is not the directivity in a fixed "
        f"direction. Without the metasurface it lies between {d['uwb_range'][0]:.1f} and {d['uwb_range'][1]:.1f} dBi "
        f"over 3.1–10.6 GHz, with a peak of {d['peak0_full'][1]:.1f} dBi at {d['peak0_full'][0]:.1f} GHz. With the "
        f"metasurface this quantity was computed from {d['lo']:.0f} to {d['hi']:.0f} GHz, so the comparison is "
        "limited to that range.")
    p.figure(FIG / "fig_directivity.png",
             "Simulated directivity of port 1 (maximum in the *φ* = 0° plane) without and with the metasurface. The "
             f"result with the metasurface covers {d['lo']:.0f}–{d['hi']:.0f} GHz (shaded).", width_in=3.4)
    p.body(
        f"Over {d['lo']:.0f}–{d['hi']:.0f} GHz, the mean directivity is {d['mean0']:.1f} dBi without the "
        f"metasurface and {d['mean1']:.1f} dBi with it, a difference of {signed(d['mean_diff'])} dB. The peak rises "
        f"from {d['peak0'][1]:.1f} dBi at {d['peak0'][0]:.1f} GHz to {d['peak1'][1]:.1f} dBi at "
        f"{d['peak1'][0]:.1f} GHz. The directivity with the metasurface is the higher one over "
        f"{100 * d['frac_higher']:.0f}% of the range; the largest rise is {abs(d['rise'][1]):.1f} dB at "
        f"{d['rise'][0]:.1f} GHz, and the largest fall is {abs(d['fall'][1]):.1f} dB at {d['fall'][0]:.1f} GHz, where "
        f"the directivity drops to {d['min1'][1]:.1f} dBi. In this range the metasurface therefore redistributes the "
        "directivity over frequency without raising its level: the average change is a fraction of a decibel.")
    p.subheading("E. Radiation Pattern")
    p.body(
        f"The simulated directivity patterns of port 1 in the *φ* = 90° plane at {PATTERN['f']} GHz are shown in "
        "Fig. 6. Both patterns have several lobes, as expected at a frequency at which the board is more than two "
        f"wavelengths across. Without the metasurface, the largest lobe of this cut points to *θ* = {a['dir']}° "
        f"with a directivity of {a['mag']} dBi and a half-power beamwidth of {a['hpbw']}°; the next lobe is only "
        f"{a['sll']} dB lower. With the metasurface, the largest lobe points to *θ* = {b['dir']}°, close to the "
        f"normal to the board, with {b['mag']} dBi and a beamwidth of {b['hpbw']}°, and the next lobe is "
        f"{b['sll']} dB lower. In this plane the metasurface thus moves the largest lobe from one half-space to the "
        f"other and raises its directivity by {float(b['mag']) - float(a['mag']):.2f} dB, but a lobe only a few "
        "decibels below it remains in the opposite half-space, so the radiation does not become unidirectional. The "
        f"maxima of Fig. 5 at this frequency, {d['at_pattern'][0]:.1f} and {d['at_pattern'][1]:.1f} dBi, are higher "
        "than those of this cut, so the direction of maximum radiation lies outside it. One plane at one frequency "
        "does not establish the behaviour over the band.")
    p.figure([FIG / "fig_pattern_without.png", FIG / "fig_pattern_with.png"],
             f"Simulated directivity pattern of port 1 in the *φ* = 90° plane at {PATTERN['f']} GHz (CST Studio "
             "Suite): (a) without, (b) with the metasurface. The radial scales of the two plots differ. The circle "
             "and the straight lines are the markers of the main lobe and its half-power width.",
             width_in=2.2, sublabels=True)
    p.table("Summary of the Simulated Results", [
        ["Quantity", "Without metasurface", "With metasurface"],
        ["|*S*_{11}| ≤ −10 dB (GHz)", band_cell(m0), band_cell(m1)],
        ["|*S*_{22}| ≤ −10 dB (GHz)", "–", f"{tp['s22_matched'][0][0]:.2f} to >{m1['fmax']:.0f}"],
        ["Lowest isolation (dB)", "–", f"{db(-s21[1])} at {s21[0]:.2f} GHz"],
        ["Highest ECC, bound (3)", "–", f"{tp['ecc_max'][1]:.2f} at {tp['ecc_max'][0]:.2f} GHz"],
        [f"Mean directivity, {d['lo']:.0f}–{d['hi']:.0f} GHz (dBi)", f"{d['mean0']:.1f}", f"{d['mean1']:.1f}"],
        [f"Peak directivity, {d['lo']:.0f}–{d['hi']:.0f} GHz (dBi)", f"{d['peak0'][1]:.1f} at {d['peak0'][0]:.1f} GHz",
         f"{d['peak1'][1]:.1f} at {d['peak1'][0]:.1f} GHz"],
        [f"Largest lobe, {PATTERN['f']} GHz, *φ* = 90°", f"{a['mag']} dBi at *θ* = {a['dir']}°",
         f"{b['mag']} dBi at *θ* = {b['dir']}°"],
    ], [1.3, 1.05, 1.05], bold_first_col=True, note="–: not evaluated.")
    p.subheading("F. Discussion and Limitations")
    p.body(
        "Taken together, the results show a metasurface that changes the pattern at individual frequencies but not "
        f"the overall performance. The matched ranges are almost unchanged, the mean directivity over "
        f"{d['lo']:.0f}–{d['hi']:.0f} GHz changes by {signed(d['mean_diff'])} dB, and the pattern at {PATTERN['f']} GHz is "
        "redirected in one plane without becoming unidirectional. This is consistent with Section II-C: the "
        "metasurface has no backing conductor, so part of the radiation passes through it, and no in-phase "
        "reflection band has been designed or demonstrated for its cell. The surfaces that raise the gain in the "
        f"reported designs are backed by a conductor and spaced from the antenna; in {c('hasan')}, for example, the "
        "surface is copper-backed and 12 mm behind the antenna. What limits the present antenna is not the "
        f"metasurface but the coupling between its two ports below about {tp['s21_above_m15'][2][1]:.0f} GHz.")
    p.body(
        "The results have clear limits. They are simulated and have not been verified against a second solver or a "
        "measurement. The radiation is described by the directivity of port 1 only: the realised gain and the "
        "efficiency, which include the loss of FR-4 and the power coupled into the other port, are not known, and "
        f"with the metasurface the directivity is available for {d['lo']:.0f}–{d['hi']:.0f} GHz only. The coupling "
        "and the diversity metrics are given with the metasurface only, and the ECC as an upper bound of the "
        "S-parameter expression. The effect of the rings has not been separated from that of the board that "
        "carries them; simulations with a bare FR-4 board at the same position are needed for that. Finally, the "
        "two elements of the upper row are not evaluated: their simulated port results did not satisfy passivity "
        "over part of the band and are excluded, and the effect of correcting those ports on the results for "
        "ports 1 and 2 has not been assessed.")
    p.subheading("G. Comparison with Reported Works")
    p.body(
        "Table III compares the antenna with reported multi-port designs. The antennas without an added surface "
        f"occupy boards of 38–65 mm side and isolate their ports by more than 17 dB {c('yin', 'wu', 'zhang', 'ahmad')}, "
        "mostly through orthogonal placement; those with a conductor-backed surface or an FSS reach gains of about "
        f"8–10 dBi {c('hasan', 'alekya', 'kumar')}. The present antenna is larger, because its element was sized for "
        "a lower band edge below 2 GHz, its two evaluated elements are parallel and not orthogonal, and its "
        "isolation at the lower end of the band is correspondingly lower. Its entry gives the simulated "
        "directivity, which is not comparable with the gains of the other works.")
    rows = [["Ref.", "Ports; element", "Size (mm)", "Added surface; gap (mm)", "Band (GHz)", "Isolation (dB)",
             "ECC", "Peak gain (dBi)"]]
    rows += [[c(key), *cells] for key, cells in COMPARISON_ROWS]
    rows.append(["This work", "2; CPW decagonal monopoles, parallel", f"{v('board_x')} × {v('board_y')}^{{¶}}",
                 f"6 × 5 double split rings, no backing; {v('gap')}", f"{tp['lower_edge']:.2f} to >{m1['fmax']:.0f}^{{‡}}",
                 f"> {at_least(-s21[1])}", f"< {at_most(tp['ecc_max'][1])}^{{§}}", f"{d['peak1'][1]:.1f}^{{†}}"])
    p.table("Comparison with Reported Multi-Port Antennas", rows, [0.5, 1.2, 0.9, 1.35, 0.85, 0.7, 0.65, 0.85],
            note=f"–: not available.  ^{{†}}Simulated directivity in the *φ* = 0° plane over "
                 f"{d['lo']:.0f}–{d['hi']:.0f} GHz (gain not evaluated).  ^{{‡}}Both ports, except port 1 between "
                 f"{gap1[0]:.2f} and {gap1[1]:.2f} GHz; simulation only.  ^{{§}}Upper bound (3).  ^{{¶}}Outline of "
                 "the board, which also carries the two elements of the upper row.", wide=True)

    # ------------------------------------------------------------------------------------------------ IV
    p.heading("IV. Conclusion")
    p.body(
        "A two-port MIMO antenna of two parallel CPW-fed decagonal monopoles on FR-4, with and without a 6 × 5 "
        "metasurface of double split rings without a backing conductor, has been studied by simulation. The two "
        f"ports are matched from {tp['lower_edge']:.2f} GHz to beyond {m1['fmax']:.0f} GHz, except for port 1 between "
        f"{gap1[0]:.2f} and {gap1[1]:.2f} GHz, and the metasurface leaves this match almost unchanged. With the "
        f"metasurface, the isolation between the ports is at least 15 dB over {100 * tp['s21_share_15']:.0f}% of the "
        f"matched range but falls to {db(-s21[1])} dB at {s21[0]:.2f} GHz, and the upper bound of the S-parameter ECC "
        f"stays below {at_most(tp['ecc_max'][1])}. Over {d['lo']:.0f}–{d['hi']:.0f} GHz the metasurface changes the mean "
        f"directivity by {signed(d['mean_diff'])} dB and its peak from {d['peak0'][1]:.1f} to "
        f"{d['peak1'][1]:.1f} dBi, and at {PATTERN['f']} GHz it moves the largest lobe of the *φ* = 90° plane to the "
        "opposite half-space. In its present form the unbacked double-ring metasurface is therefore not a "
        "gain-enhancing reflector, and the antenna is limited by the coupling of its two ports at the lower end of "
        "the band. A decoupling structure between the two elements, a conductor-backed cell with an in-phase "
        "reflection band inside the operating range, the evaluation of the realised gain, the efficiency and the "
        "far-field ECC, and the fabrication and measurement of a prototype are the next steps of this work.")
    p.references(c.listing())
    p.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
    print("\nPrinted in the paper without having been read from the CST model. Check before submission:")
    for key, text in VERIFY.items():
        print(f"  - {key}: {text}")
