"""Build Paper 2 (.docx, IEEE conference format): four-port CPW-fed decagonal-monopole MIMO antenna + ring metasurface.

    python papers/make_figures.py && python papers/paper2/build_paper2.py [--exports DIR] [--out FILE]

No result is typed by hand:
  * reflection-coefficient and directivity numbers are computed from papers/data/p2_*.csv at build time;
  * coupling, ECC, diversity gain, CCL and TARC are computed from exports/mimo_noMS.s4p and exports/mimo_MS.s4p; while
    those files are missing the text carries highlighted placeholders and the paper is NOT ready for submission;
  * design facts come from papers/paper2/design.py; unconfirmed ones are highlighted.
The script prints the list of everything that is still open.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import mimo_results  # noqa: E402
from check_numbers import bands, cpw, load  # noqa: E402
from scipy.signal import find_peaks  # noqa: E402
from design import MS_GROUNDED, guess, open_items, value  # noqa: E402
from ieee_docx import Paper  # noqa: E402
from references import REFS  # noqa: E402

FIG = HERE / "figures"
SHOTS = HERE / "cst_screenshots"

TITLE = ("A Four-Port CPW-Fed Decagonal Monopole MIMO Antenna and the Effect of a Double-Ring Metasurface: "
         "A Simulation Study")
AFFIL = ("Department of Electronics and Communication Engineering", "National Institute of Technology Silchar",
         "Silchar, Assam 788010, India")
# Same author list as Paper 1 (confirmed by the authors).
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
    """Bands, mismatched regions inside the range, and the lowest value of one |S11| curve."""
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
        if hi >= m["fmax"]:
            parts.append(f"from {lo:.2f} GHz to beyond {m['fmax']:.0f} GHz")
        else:
            parts.append(f"from {lo:.2f} to {hi:.2f} GHz")
    return " and ".join(parts)


def db(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace("-", "−")


def signed(x: float, digits: int = 1) -> str:
    return ("+" if x >= 0 else "−") + f"{abs(x):.{digits}f}"


def directivity() -> dict:
    f0, d0 = load("p2_dir_noms")
    f1, d1 = load("p2_dir_ms")
    lo, hi = max(f0[0], f1[0]), min(f0[-1], f1[-1])
    g = np.arange(lo, hi + 1e-9, 0.05)
    a, b = np.interp(g, f0, d0), np.interp(g, f1, d1)
    diff = b - a
    inband = (f0 >= 3.1) & (f0 <= 10.6)
    return {"lo": lo, "hi": hi, "mean0": a.mean(), "mean1": b.mean(), "mean_diff": diff.mean(),
            "peak0": (float(g[a.argmax()]), float(a.max())), "peak1": (float(g[b.argmax()]), float(b.max())),
            "peak0_full": (float(f0[d0.argmax()]), float(d0.max())),
            "rise": (float(g[diff.argmax()]), float(diff.max())), "fall": (float(g[diff.argmin()]), float(diff.min())),
            "frac_higher": float((diff > 0).mean()), "full_range": (float(f0[0]), float(f0[-1])),
            "uwb_range": (float(d0[inband].min()), float(d0[inband].max())),
            "min1": (float(g[b.argmin()]), float(b.min())), "at_min1_without": float(a[b.argmin()])}


def build(exports: Path, out: Path) -> tuple[Path, list[str]]:
    c = Citations()
    v = value
    todo: list[str] = []
    m0, m1, d = match("noms"), match("ms"), directivity()
    mimo_data = mimo_results.load(exports)
    mimo = mimo_results.analyse(mimo_data) if mimo_data else None
    mimo_figs = mimo_results.figures(mimo, out.parent / "figures") if mimo else {}   # next to the output file
    mag_data = None if mimo else mimo_results.load_magnitudes()
    mag = mimo_results.analyse_magnitudes(mag_data) if mag_data else None
    mag_figs = mimo_results.magnitude_figures(mag_data, out.parent / "figures") if mag else {}
    bad_ports = [k for k in (1, 2, 3, 4) if k not in mag["valid_ports"]] if mag else []
    if bad_ports:
        todo.insert(0, "PORTS " + " and ".join(map(str, bad_ports)) + " ARE NOT VALID: their reflection coefficient "
                    "exceeds 0 dB (a passive antenna cannot reflect more power than it receives) and stays above "
                    "-10 dB up to about 10.5 GHz. Check the port definition and the port mode, then re-simulate")
    if mag:
        todo.append("ECC, diversity gain, TARC and CCL need the phase: export the complex S-matrix (Touchstone) of "
                    f"BOTH models to {exports}/mimo_noMS.s4p and {exports}/mimo_MS.s4p. The screenshots give "
                    "magnitudes with the metasurface only")
    if not mimo and not mag:
        todo.append(f"Coupling and diversity results: export the 4 x 4 S-matrix of both models to "
                    f"{exports}/mimo_noMS.s4p and {exports}/mimo_MS.s4p (Sections III-B and III-E are placeholders)")
    partial = d["lo"] > m0["fmin"] + 0.5 or d["hi"] < m0["fmax"] - 0.5
    if partial:
        todo.append(f"Directivity with the metasurface covers only {d['lo']:.0f}-{d['hi']:.0f} GHz: re-run the "
                    f"farfield result over {m0['fmin']:.0f}-{m0['fmax']:.0f} GHz and replace data/p2_dir_ms.csv")

    lam = lambda f_ghz: 299.79 / f_ghz                                       # free-space wavelength, mm
    f_lo = m0["bands"][0][0]
    z0 = cpw(guess("W_f"), guess("g"), guess("h_sub"), guess("eps_r"), False)[1]

    def ray(radius: float, gap_p: float) -> float:
        """Lower band edge (GHz) of a decagonal monopole from the equivalent-cylinder estimate, k = 1.15."""
        height = 2 * radius * np.cos(np.radians(18))
        r_eq = 5 * radius ** 2 * np.sin(np.radians(36)) / (2 * np.pi * height)
        return 7.2 / ((height + r_eq + gap_p) / 10 * 1.15)

    p = Paper()
    p.title(TITLE)
    p.authors(AUTHORS)

    # ------------------------------------------------------------------------------------------------ abstract
    gap0, gap1 = m0["gaps"][0], m1["gaps"][0]
    if mimo:
        w0 = max(mimo["noMS"]["pairs"].values(), key=lambda q: q["coupling"])
        w1 = max(mimo["MS"]["pairs"].values(), key=lambda q: q["coupling"])
        e0 = max(q["ecc"] for q in mimo["noMS"]["pairs"].values())
        e1 = max(q["ecc"] for q in mimo["MS"]["pairs"].values())
        mimo_abstract = (f"The lowest isolation between two ports is {db(-w0['coupling'])} dB without the "
                         f"metasurface and {db(-w1['coupling'])} dB with it, and the envelope correlation "
                         f"coefficient computed from the S-parameters stays below {max(e0, e1):.3f}. ")
    elif mag:
        w21 = mag["pairs"][(2, 1)]
        mimo_abstract = (
            f"With the metasurface, port 2 is matched from {mag['ports'][2]['matched'][0][0]:.2f} GHz upwards, and "
            f"the isolation between ports 1 and 2 falls to {db(-w21['coupling'])} dB at {w21['f_coupling']:.2f} GHz "
            f"and is at least 15 dB over {100 * w21['share_15dB']:.0f}% of the matched range. "
            + ("[[Ports " + " and ".join(map(str, bad_ports)) + " are not valid in the present simulation and are "
               "not reported; the envelope correlation coefficient needs the complex S-matrix.]] " if bad_ports else
               "[[Envelope correlation coefficient: needs the complex S-matrix.]] "))
    else:
        mimo_abstract = ("[[Isolation and envelope-correlation sentence: to be generated from the four-port "
                         "S-matrix.]] ")
    p.abstract(
        "A four-port multiple-input multiple-output (MIMO) antenna made of coplanar-waveguide (CPW)-fed decagonal "
        f"printed monopoles on a {v('board')} mm FR-4 board is studied by full-wave simulation, alone and with a "
        f"6 × 5 array of concentric double-ring cells on a second FR-4 board placed {v('gap')} mm behind it. Without "
        "the "
        f"metasurface, the reflection coefficient of port 1 is at or below −10 dB {band_phrase(m0)}; in between it "
        f"rises to {db(gap0[3])} dB at {gap0[2]:.1f} GHz. The metasurface leaves the match almost unchanged: the "
        f"bands become {band_phrase(m1).replace('from ', '', 1)}, and the mismatched region narrows from "
        f"{gap0[1] - gap0[0]:.2f} to {gap1[1] - gap1[0]:.2f} GHz. " + mimo_abstract +
        f"Over {d['lo']:.0f}–{d['hi']:.0f} GHz, the maximum directivity in the *φ* = 0° plane changes by "
        f"{signed(d['mean_diff'])} dB on average with the metasurface (between {signed(d['fall'][1])} and "
        f"{signed(d['rise'][1])} dB), and its peak rises from {d['peak0'][1]:.1f} to {d['peak1'][1]:.1f} dBi. At "
        f"{PATTERN['f']} GHz the main lobe in the *φ* = 90° plane moves from *θ* = {PATTERN['noMS']['dir']}° to "
        f"*θ* = {PATTERN['MS']['dir']}°. In the range and the planes evaluated, the metasurface therefore changes the "
        "direction of the radiation at individual frequencies but does not raise the level of the directivity.")
    p.keywords("CPW-fed antenna, decagonal monopole, double-ring cell, metasurface, MIMO antenna, "
               "ultra-wideband antenna")

    # ------------------------------------------------------------------------------------------------ I
    p.heading("I. Introduction")
    p.body(
        "Multiple-input multiple-output (MIMO) operation raises the capacity and the reliability of a wireless link "
        f"without additional spectrum, provided that the antenna elements are well matched and weakly coupled "
        f"{c('sharawi_apm')}. For wideband and ultra-wideband (UWB, 3.1–10.6 GHz {c('fcc')}) terminals, the elements "
        "are usually printed monopoles, and those fed by a coplanar waveguide (CPW) are attractive because the feed "
        f"line and its ground planes lie on one side of the substrate {c('simons', 'ray')}. The difficulty is that "
        "the elements of a compact MIMO antenna share one board, and the coupling between them must stay low over "
        "the whole band.")
    p.body(review_mimo(c))
    p.body(review_metasurface(c))
    p.body(
        "This paper reports the simulated behaviour of a four-port arrangement of CPW-fed decagonal monopoles, and "
        "examines with the same model what a 6 × 5 metasurface of concentric double rings placed behind it changes. "
        + ("The reflection coefficient, the coupling between the ports, the diversity metrics, the directivity and "
           "the radiation pattern" if mimo else "The reflection coefficient, the directivity and the radiation "
           "pattern [[and, once exported, the coupling between the ports and the diversity metrics]]") +
        " are compared with and without the metasurface, and the comparison is reported as obtained, including "
        "where the metasurface brings no benefit. Section II describes the design, Section III the results, and "
        "Section IV concludes the paper.")

    # ------------------------------------------------------------------------------------------------ II
    p.heading("II. Antenna Design")
    p.subheading("A. Radiating Element")
    p.body(
        "Each element is a regular decagon with a flat side towards the feed, printed on an FR-4 substrate "
        f"(*ε*_{{r}} = {v('eps_r')}, tan *δ* = {v('tan_d')}) of thickness *h*_{{s}} = {v('h_sub')} mm. The "
        f"circumradius is *R* = {v('R_lower')} mm for the two elements of the lower row and {v('R_upper')} mm for the "
        f"two of the upper row. Each element is fed by a CPW line with a strip of width *W*_{{f}} = {v('W_f')} mm and "
        f"slots of *g* = {v('g')} mm (a line impedance of about {z0:.0f} Ω from the conformal-mapping expressions of "
        f"{c('simons')}), between two ground planes of length *L*_{{g}} = {v('L_g')} mm and of width "
        f"*W*_{{g}} = {v('W_g_lower')} mm in the lower row and {v('W_g_upper')} mm in the upper row. The side of the decagon that faces the feed lies *p* = {v('p_lower')} mm from the "
        f"ground edge in the lower row and {v('p_upper')} mm in the upper row, and the back of the substrate carries "
        "no copper. The lower edge of the band of such a monopole can be estimated by replacing the patch with a "
        f"cylindrical monopole of the same height and area {c('ray')}:")
    p.equation(r"f_L = \frac{7.2}{(l + r + p)\,k}\ \text{GHz}")
    p.body(
        "where *l* = 2*R* cos 18° is the height of the decagon, *r* = *A*/(2π*l*) the radius of the equivalent "
        "cylinder and *A* = 5*R*^{2} sin 36° the area of the decagon, all lengths taken in centimetres, and "
        f"*k* = 1.15 for FR-4 {c('ray')}. Equation (1) gives *f*_{{L}} ≈ {ray(guess('R_lower'), guess('p_lower')):.2f} GHz "
        f"for the lower-row elements and {ray(guess('R_upper'), guess('p_upper')):.2f} GHz for the upper-row "
        "elements.", cont=True)
    p.subheading("B. Four-Port Arrangement")
    p.body(
        "The four elements are placed in two rows of two on one board, as shown in Fig. 1(a). The two elements of "
        "the upper row are fed from the upper edge of the board and the two of the lower row from the lower edge, "
        "so that the patches of the two rows face each other across the centre of the board; all four elements "
        f"have the same polarisation. The feed lines of a row are {v('pitch')} mm apart, which is "
        f"{guess('pitch') / lam(f_lo):.2f} free-space wavelength at {f_lo:.2f} GHz, and the facing patches are "
        f"separated by {v('d_face')} mm. The board fits in an outline of {v('board')} mm; its upper half is displaced "
        f"sideways by {v('board_step')} mm with respect to the lower half, so that the feed lines of the upper row "
        f"are offset by {v('feed_offset')} mm from those of the lower row. In the present model "
        f"{v('ground_statement')}, and {v('port_map')}.")
    p.figure([SHOTS / "mimo_design_without_metasurface.png", SHOTS / "metasurface_design.png"],
             "Top views of the simulated model (CST Studio Suite): (a) four-port antenna, (b) 6 × 5 double-ring "
             "metasurface.", width_in=1.62, sublabels=True, side_by_side=True)
    p.subheading("C. Metasurface")
    p.body(
        "The metasurface of Fig. 1(b) is a 6 × 5 array of cells, each made of two concentric copper rings of strip "
        f"width {v('w_ring')} mm: an outer ring of outer radius {v('r_out')} mm with a split of {v('split_out')} mm, "
        f"and an inner ring of outer radius {v('r_in')} mm with a split of {v('split_in')} mm. The cells repeat every "
        f"{v('pitch_x')} mm along the rows and every {v('pitch_y')} mm along the columns. The array is printed on a "
        f"{v('ms_board')} mm FR-4 board of thickness 1.6 mm, which {v('ms_ground')}. The board is placed parallel to "
        f"the antenna, at an air gap of {v('gap')} mm from the back of the antenna substrate, with the rings towards "
        f"the antenna. The gap is {guess('gap') / lam(f_lo):.3f} free-space wavelength at {f_lo:.2f} GHz and "
        f"{guess('gap') / lam(d['lo']):.2f}–{guess('gap') / lam(d['hi']):.2f} wavelength over "
        f"{d['lo']:.0f}–{d['hi']:.0f} GHz.")
    cell_lo, cell_hi = min(guess("pitch_x"), guess("pitch_y")) / lam(d["lo"]), max(guess("pitch_x"), guess("pitch_y")) / lam(d["hi"])
    p.body(
        "A closed ring resonates first when its circumference is about one guided wavelength, and a split lowers "
        "the first resonance to about half that frequency. With an effective permittivity of (*ε*_{r} + 1)/2 = 2.65, "
        "the outer ring is one wavelength long at about 4.0 GHz and the inner ring at about 5.6 GHz, so the first "
        f"resonances of the rings lie between about 2 and 6 GHz. In the {d['lo']:.0f}–{d['hi']:.0f} GHz range, in "
        "which the directivity is compared in Section III, the rings are at higher-order resonances and the cell "
        f"period is {cell_lo:.2f}–{cell_hi:.2f} free-space wavelength, so the array is not electrically dense there. "
        + ("It is backed by a conductor, but its reflection phase, which decides whether it can act as a "
           f"high-impedance surface {c('sievenpiper')}, has not been computed." if MS_GROUNDED else
           f"Without a backing conductor it cannot form a high-impedance surface {c('sievenpiper')} either: it is a "
           "partly transparent sheet of resonant rings, which reflects appreciably only near its resonances. The "
           "reflection and the transmission of the cell have not been computed."))
    p.subheading("D. Simulation Setup")
    p.body(
        f"The model is simulated in CST Studio Suite {v('cst_version')} with the {v('solver')} solver from "
        f"{m0['fmin']:.0f} to {m0['fmax']:.0f} GHz, with a waveguide port at the end of each CPW line and open "
        f"boundaries. Port 1 feeds {v('port1_position')}. The reflection coefficient and the far field are "
        "evaluated with port 1 excited and the other ports terminated. The far-field quantity is the directivity, "
        "which does not include the dielectric and conductor losses or the mismatch. The antenna lies in the *xy* "
        f"plane, and *θ* = 0° is the normal to the board on {v('theta0_side')}.")

    # ------------------------------------------------------------------------------------------------ III
    p.heading("III. Results and Discussion")
    p.subheading("A. Reflection Coefficient")
    p.body(
        "The simulated reflection coefficient of port 1 is shown in Fig. 2. Without the metasurface, "
        f"|*S*_{{11}}| is at or below −10 dB {band_phrase(m0)}, the upper limit of the simulation. Between the two "
        f"ranges it rises to {db(gap0[3])} dB at {gap0[2]:.1f} GHz. The lowest value is {db(m0['min'][1])} dB at "
        f"{m0['min'][0]:.2f} GHz. " + (
            "Inside the matched ranges the margin is small at " +
            " and ".join(f"{fq:.1f} GHz ({db(val)} dB)" for fq, val in m0["thin"][:2]) + ". " if m0["thin"] else "") +
        f"The lower band edge, {m0['bands'][0][0]:.2f} GHz, is below the estimate of (1), which was made for an "
        "element on its own.")
    p.figure(FIG / "fig_s11.png",
             "Simulated reflection coefficient of port 1 without and with the metasurface. The dotted line marks "
             "−10 dB.", width_in=3.4)
    f, s0, s1 = m0["f"], m0["s"], np.interp(m0["f"], m1["f"], m1["s"])
    rng = f >= m0["bands"][0][0] + 0.1
    lin = 10 ** (s1[rng] / 20) - 10 ** (s0[rng] / 20)
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
    # --- coupling ---
    p.subheading("B. Mutual Coupling")
    if mimo:
        r0, r1 = mimo["noMS"], mimo["MS"]
        p.body(
            "The simulated transmission coefficients between the ports are shown in Fig. 3, and their highest "
            "values inside the matched range are listed in Table I. Without the metasurface, the strongest "
            f"coupling is {db(w0['coupling'])} dB at {w0['f_coupling']:.2f} GHz; with it, {db(w1['coupling'])} dB at "
            f"{w1['f_coupling']:.2f} GHz. The reflection coefficients of the four ports differ by up to "
            f"{r1['port_spread']:.1f} dB, and the highest of them inside the range is {db(r1['worst_reflection'])} dB "
            f"at {r1['f_worst_reflection']:.2f} GHz.")
        p.figure([mimo_figs["coupling_noMS"], mimo_figs["coupling_MS"]],
                 "Simulated transmission coefficients between the ports: (a) without, (b) with the metasurface. "
                 "The dotted line marks −15 dB.", width_in=3.4, sublabels=True)
        rows = [["Ports", "Highest |*S*_{ij}| without (dB at GHz)", "Highest |*S*_{ij}| with (dB at GHz)",
                 "Highest ECC without", "Highest ECC with"]]
        for pair in r0["pairs"]:
            a, b = r0["pairs"][pair], r1["pairs"][pair]
            rows.append([f"{pair[0]}–{pair[1]}", f"{db(a['coupling'])} at {a['f_coupling']:.2f}",
                         f"{db(b['coupling'])} at {b['f_coupling']:.2f}", f"{a['ecc']:.4f}", f"{b['ecc']:.4f}"])
        p.table("Highest Coupling and Envelope Correlation Coefficient Inside the Matched Range", rows,
                [0.42, 0.85, 0.85, 0.62, 0.62])
    elif mag:
        pt, w21 = mag["ports"], mag["pairs"][(2, 1)]
        span = lambda rs: " and ".join(f"from {a:.2f} to {b:.2f} GHz" for a, b in rs)
        p.body(
            "The reflection coefficients of the four ports with the metasurface are shown in Fig. 3. Port 2, the "
            f"second element of the lower row, is matched from {pt[2]['matched'][0][0]:.2f} GHz to beyond "
            f"{mag['upper']:.0f} GHz and follows port 1 closely.")
        if bad_ports:
            k = bad_ports[0]
            p.body(
                "[[Ports " + " and ".join(map(str, bad_ports)) + ", the two elements of the upper row, are not "
                f"valid in the present simulation. Their reflection coefficient stays above −10 dB up to "
                f"{pt[k]['matched'][0][0]:.1f} GHz and exceeds 0 dB {span(pt[k]['above_0dB'])}, reaching "
                f"{signed(pt[k]['max'][1])} dB at {pt[k]['max'][0]:.1f} GHz, so that the sum of |*S*_{{i" + str(k) +
                "}}|^{2} over the four ports reaches " + f"{pt[k]['power_sum_max']:.2f}. A passive antenna cannot "
                "return more power than it receives; the port definition or the port mode of these two ports has to "
                "be corrected and the model simulated again. Every value below that involves port "
                + " or ".join(map(str, bad_ports)) + " is provisional.]]")
        p.figure(mag_figs["reflection"],
                 "Simulated reflection coefficients of the four ports with the metasurface. The dotted line marks "
                 "−10 dB." + (" [[Ports " + " and ".join(map(str, bad_ports)) + ": not valid, see text.]]"
                              if bad_ports else ""), width_in=3.4)
        last15 = w21["above_m15"][-1][1]
        p.body(
            "The transmission coefficients between the ports with the metasurface are shown in Fig. 4, and Table I "
            f"lists their highest values above the lower band edge, {m1['bands'][0][0]:.2f} GHz. The strongest "
            "coupling is between ports 1 and 2, the two elements of the lower row, which are parallel, have the same "
            f"polarisation and share one ground conductor: |*S*_{{21}}| reaches {db(w21['coupling'])} dB at "
            f"{w21['f_coupling']:.2f} GHz, where {100 * 10 ** (w21['coupling'] / 10):.0f}% of the power incident at "
            f"port 1 is delivered to port 2, and it is above −10 dB {span(w21['above_m10'])}. The isolation between "
            f"these two ports is at least 15 dB over {100 * w21['share_15dB']:.0f}% of the range, and at all "
            f"frequencies above {last15:.1f} GHz. The transmission coefficients that involve ports 3 and 4 are below "
            f"{db(max(q['coupling'] for pr, q in mag['pairs'].items() if pr != (2, 1)))} dB"
            + ("; [[they cannot be interpreted as long as these ports reflect most of the incident power]]."
               if bad_ports else ".") +
            " [[The transmission coefficients without the metasurface have not been exported, so the effect of the "
            "metasurface on the coupling is not known.]]")
        p.figure(mag_figs["coupling"],
                 "Simulated transmission coefficients between the ports with the metasurface. The dotted line marks "
                 "−15 dB.", width_in=3.4)
        rows = [["Ports", "Highest |*S*_{ij}| (dB)", "at (GHz)", "Share of the range with isolation ≥ 15 dB"]]
        for (i, j), q in mag["pairs"].items():
            flag = "^{†}" if (i in bad_ports or j in bad_ports) else ""
            rows.append([f"{j}–{i}{flag}", db(q["coupling"]), f"{q['f_coupling']:.2f}",
                         f"{100 * q['share_15dB']:.0f}%"])
        p.table("Highest Coupling With the Metasurface Above the Lower Band Edge", rows, [0.5, 0.95, 0.7, 1.25],
                note=("^{†}Provisional: involves a port that is not valid in the present simulation."
                      if bad_ports else None))
    else:
        p.body(
            "[[The transmission coefficients between the ports have not been exported from the simulation. This "
            "subsection, with a figure and a table, is generated by the build script from the four-port S-matrix "
            "of the two models: all six transmission coefficients against frequency, the highest coupling of each "
            "port pair inside the matched range, and the difference between the reflection coefficients of the "
            "four ports.]]")
        p.body(
            f"The geometry indicates where the coupling is expected to be strongest. The facing patches are "
            f"{v('d_face')} mm apart, {guess('d_face') / lam(f_lo):.3f} free-space wavelength at {f_lo:.2f} GHz, and their "
            "facing "
            "edges are the open ends of the two monopoles; the elements of a row are parallel, have the same "
            "polarisation and are less than a third of a wavelength apart at the lower band edge. The coupling of "
            "these two kinds of pair is therefore the quantity on which the usefulness of the arrangement "
            "depends.")
    # --- directivity ---
    p.subheading("C. Directivity")
    part = (f" With the metasurface the result is available from {d['lo']:.0f} to {d['hi']:.0f} GHz only, so the "
            "comparison is limited to that range." if partial else "")
    fig_no = 5 if mag else 4 if mimo else 3
    p.body(
        f"Fig. {fig_no} shows the simulated directivity of port 1 against frequency. The quantity plotted is the highest "
        "directivity found in the *φ* = 0° plane at each frequency; it is not the directivity in a fixed "
        f"direction. Without the metasurface it lies between {d['uwb_range'][0]:.1f} and {d['uwb_range'][1]:.1f} dBi "
        f"over 3.1–10.6 GHz, with a peak of {d['peak0_full'][1]:.1f} dBi at {d['peak0_full'][0]:.1f} GHz." + part)
    p.figure(FIG / "fig_directivity.png",
             "Simulated directivity of port 1 (maximum in the *φ* = 0° plane) without and with the metasurface. "
             + (f"The result with the metasurface covers {d['lo']:.0f}–{d['hi']:.0f} GHz (shaded)." if partial else ""),
             width_in=3.4)
    p.body(
        f"Over {d['lo']:.0f}–{d['hi']:.0f} GHz, the mean directivity is {d['mean0']:.1f} dBi without the "
        f"metasurface and {d['mean1']:.1f} dBi with it, a difference of {signed(d['mean_diff'])} dB. The peak rises "
        f"from {d['peak0'][1]:.1f} dBi at {d['peak0'][0]:.1f} GHz to {d['peak1'][1]:.1f} dBi at "
        f"{d['peak1'][0]:.1f} GHz. The directivity with the metasurface is the higher one over "
        f"{100 * d['frac_higher']:.0f}% of the range; the largest rise is {abs(d['rise'][1]):.1f} dB at "
        f"{d['rise'][0]:.1f} GHz, and the largest fall is {abs(d['fall'][1]):.1f} dB at {d['fall'][0]:.1f} GHz, where "
        f"the directivity drops to {d['min1'][1]:.1f} dBi. In this range the metasurface therefore redistributes the "
        "directivity over frequency without raising its level: the average change is a fraction of a decibel.")
    # --- pattern ---
    a, b = PATTERN["noMS"], PATTERN["MS"]
    p.subheading("D. Radiation Pattern")
    at_f = float(PATTERN["f"])
    f0d, d0d = load("p2_dir_noms")
    f1d, d1d = load("p2_dir_ms")
    p.body(
        f"The simulated directivity patterns of port 1 in the *φ* = 90° plane at {PATTERN['f']} GHz are shown in "
        f"Fig. {fig_no + 1}. Both patterns have several lobes, as expected at a frequency at which the board is more "
        "than two wavelengths across. Without the metasurface, the largest lobe of this cut points to "
        f"*θ* = {a['dir']}°, in the rear half-space, with a directivity of {a['mag']} dBi and a half-power "
        f"beamwidth of {a['hpbw']}°; the next lobe is only {a['sll']} dB lower. With the metasurface, the largest "
        f"lobe points to *θ* = {b['dir']}°, close to the normal to the board, with {b['mag']} dBi and a beamwidth of "
        f"{b['hpbw']}°, and the next lobe is {b['sll']} dB lower. In this plane the metasurface thus moves the "
        "largest lobe from the rear to the front half-space and raises its directivity by "
        f"{float(b['mag']) - float(a['mag']):.2f} dB, but a rear lobe only a few decibels below it remains. The "
        f"maxima of Fig. {fig_no} at this frequency, {np.interp(at_f, f0d, d0d):.1f} and "
        f"{np.interp(at_f, f1d, d1d):.1f} dBi, are higher than those of this cut, so the direction of maximum "
        "radiation lies outside it. One plane at one frequency and one port does not establish the behaviour over "
        "the band.")
    p.figure([FIG / "fig_pattern_without.png", FIG / "fig_pattern_with.png"],
             f"Simulated directivity pattern of port 1 in the *φ* = 90° plane at {PATTERN['f']} GHz (CST Studio "
             "Suite): (a) without, (b) with the metasurface. The radial scales of the two plots differ. The circle "
             "and the straight lines are the markers of the main lobe and its half-power width.",
             width_in=2.9, sublabels=True, side_by_side=True, wide=True)
    # --- diversity ---
    p.subheading("E. Diversity Performance")
    p.body(
        "The envelope correlation coefficient (ECC) between ports *i* and *j* of an *N*-port antenna is computed "
        f"from the S-parameters as {c('blanch')}")
    p.equation(r"\rho_{e,ij} = \frac{|\sum_{n=1}^{N} \overline{S_{ni}}\, S_{nj}|^{2}}"
               r"{(1 - \sum_{n=1}^{N} |S_{ni}|^{2})(1 - \sum_{n=1}^{N} |S_{nj}|^{2})}")
    p.body(
        "where the bar denotes the complex conjugate, and the apparent diversity gain as "
        f"DG = 10(1 − *ρ*_{{e}})^{{1/2}} dB {c('dg')}. Equation (2) assumes a lossless antenna in a uniform "
        "multipath environment; on a lossy FR-4 substrate it underestimates the correlation, so the value obtained "
        f"from the far fields {c('vaughan')} should be reported as well {c('hallbjorner', 'sharawi_misuse')}. The "
        "total active reflection coefficient (TARC) for incident waves *a*_{i} and reflected waves *b*_{i} at the "
        f"ports is {c('manteghi')}", cont=True)
    p.equation(r"\Gamma_a^t = \sqrt{\frac{\sum_{i=1}^{N} |b_i|^{2}}{\sum_{i=1}^{N} |a_i|^{2}}}")
    p.body(
        f"and the channel capacity loss (CCL) is {c('ccl')}", cont=True)
    p.equation(r"C_{\mathrm{loss}} = -\log_2 \operatorname{det}(\mathbf{I} - \mathbf{S}^{\mathrm{H}}\mathbf{S})")
    p.body(
        "where **S** is the S-matrix, **I** the identity matrix and the superscript H the conjugate transpose.",
        cont=True)
    if mimo:
        r0, r1 = mimo["noMS"], mimo["MS"]
        dg0 = min(q["dg"] for q in r0["pairs"].values())
        dg1 = min(q["dg"] for q in r1["pairs"].values())
        p.body(
            f"The ECC of the worst port pair against frequency is shown in Fig. {fig_no + 2}, and Table I lists the "
            f"highest value of each pair inside the matched range. The highest ECC is {e0:.4f} without the "
            f"metasurface and {e1:.4f} with it, and the lowest diversity gain is {dg0:.2f} and {dg1:.2f} dB. The CCL "
            f"stays below {r0['ccl']:.2f} and {r1['ccl']:.2f} bit/s/Hz, and the TARC, taken as the worst of 50 "
            f"random sets of excitation phases, below {db(r0['tarc'])} and {db(r1['tarc'])} dB. These values come "
            "from the S-parameters alone and do not include the loss of the substrate.")
        p.figure(mimo_figs["ecc"], "Envelope correlation coefficient of the worst port pair, computed from the "
                 "S-parameters with (2).", width_in=3.4)
    else:
        p.body(
            "[[The ECC, the diversity gain, the TARC and the CCL are generated by the build script from the complex "
            "four-port S-matrix of the two models (Touchstone export), together with the ECC figure. "
            + ("The magnitudes of Section III-B are not sufficient: (2) needs the phase. " if mag else "") +
            "Far-field ECC needs the complex far fields of all four ports.]]")
    # --- discussion ---
    p.subheading("F. Discussion and Limitations")
    p.body(
        "Taken together, the results show a metasurface that changes the pattern at individual frequencies but "
        f"not the overall performance. The matched ranges are almost unchanged, the mean directivity over "
        f"{d['lo']:.0f}–{d['hi']:.0f} GHz changes by {signed(d['mean_diff'])} dB, and the pattern at {PATTERN['f']} GHz "
        "is turned towards the front in one plane without becoming unidirectional. No in-phase reflection band "
        "has been designed or demonstrated for this cell (Section II-C), so a broadband rise of the directivity "
        "was not to be expected. " + reflector_note(c) +
        ("" if MS_GROUNDED else " The present metasurface has no backing conductor, so part of the backward "
                                "radiation passes through it."))
    p.body(
        "The present results have clear limits. Only port 1 has been evaluated, and only its directivity: the "
        "realised gain and the efficiency, which include the loss of FR-4 and the power coupled into the other "
        "ports, are not known. " + (f"With the metasurface, the directivity is available for "
                                    f"{d['lo']:.0f}–{d['hi']:.0f} GHz only. " if partial else "") +
        ("The coupling is known with the metasurface only and in magnitude only, so the diversity metrics cannot "
         "be computed yet" + (", and the two upper-row ports are not valid in the present simulation. " if bad_ports
                              else ". ") if mag else
         "The coupling between the ports and the diversity metrics remain to be computed. " if not mimo else "") +
        "The effect of the rings has not been separated from that of the board that carries them; simulations "
        "with a bare FR-4 board and with a plain copper plate at the same position are needed for that. Finally, "
        "the model has not been verified against a second solver or a measurement.")
    # --- comparison ---
    p.subheading("G. Comparison with Reported Works")
    p.body(comparison_text(c, "II" if (mimo or mag) else "I"))
    iso = (f"{db(-w1['coupling'])}" if mimo else
           f"> {db(-mag['pairs'][(2, 1)]['coupling'])}^{{§}}" if mag else "[[–]]")
    ecc = f"< {max(e0, e1):.3f}" if mimo else "[[–]]"
    rows = [["Ref.", "Ports; element", "Size (mm)", "Added surface; gap (mm)", "Band (GHz)", "Isolation (dB)",
             "ECC", "Peak gain (dBi)"]]
    rows += [[c(key), *cells] for key, cells in COMPARISON_ROWS]
    rows.append(["This work", "4; CPW decagonal monopole", v("board"), f"6 × 5 double ring; {v('gap')}",
                 f"{m1['bands'][0][0]:.2f} to >{m1['fmax']:.0f}^{{‡}}", iso, ecc, f"{d['peak1'][1]:.1f}^{{†}}"])
    p.table("Comparison with Reported Four-Port Antennas", rows, [0.5, 1.2, 0.9, 1.35, 0.85, 0.7, 0.65, 0.85],
            note=f"–: not available.  ^{{†}}Simulated directivity in the *φ* = 0° plane (gain not evaluated).  "
                 f"^{{‡}}Port 1, except {gap1[0]:.2f}–{gap1[1]:.2f} GHz; simulation only."
                 + ("  ^{§}Between ports 1 and 2." if mag else ""), wide=True)

    # ------------------------------------------------------------------------------------------------ IV
    p.heading("IV. Conclusion")
    p.body(
        "A four-port MIMO antenna of CPW-fed decagonal monopoles on FR-4 has been simulated with and without a "
        f"6 × 5 double-ring metasurface. Port 1 is matched {band_phrase(m1)} with the metasurface, and the match "
        f"is practically the same without it. " +
        (f"The lowest isolation is {db(-w1['coupling'])} dB and the highest ECC {e1:.3f}. " if mimo else
         (f"With the metasurface, the isolation between the two lower-row ports falls to "
          f"{db(-mag['pairs'][(2, 1)]['coupling'])} dB at {mag['pairs'][(2, 1)]['f_coupling']:.2f} GHz and is at "
          f"least 15 dB over {100 * mag['pairs'][(2, 1)]['share_15dB']:.0f}% of the matched range"
          + ("; [[the two upper-row ports are not valid in the present simulation]]. " if bad_ports else ". ")
          if mag else "[[One sentence on isolation and ECC.]] ")) +
        f"Over {d['lo']:.0f}–{d['hi']:.0f} GHz the metasurface changes the mean directivity by "
        f"{signed(d['mean_diff'])} dB and its peak from {d['peak0'][1]:.1f} to {d['peak1'][1]:.1f} dBi, and at "
        f"{PATTERN['f']} GHz it moves the largest lobe of the *φ* = 90° plane towards the front of the board. In "
        "the range evaluated, the double-ring metasurface in its present form therefore does not act as a "
        "gain-enhancing reflector. " + ("A decoupling structure between the two lower-row elements, " if mag else "") +
        ("control" if mag else "Control") + " simulations with a bare board and a copper plate, the evaluation of "
        "the realised gain and efficiency of all ports, a cell with an in-phase reflection band inside the "
        "operating range, and the fabrication and measurement of a prototype are the next steps of this work.")
    p.references(c.listing())
    out.parent.mkdir(parents=True, exist_ok=True)
    p.save(out)
    todo += [f"design.py '{key}': {item.why}" for key, item in open_items()]
    return out, todo


# ---------------------------------------------------------------------------------------------- literature text
# Kept apart from build() so that the review can be edited without touching the result logic.
from literature_text import (COMPARISON_ROWS, comparison_text, reflector_note, review_metasurface,  # noqa: E402
                             review_mimo)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exports", type=Path, default=ROOT / "exports")
    ap.add_argument("--out", type=Path, default=HERE / "Paper2_FourPort_Decagonal_MIMO_draft.docx")
    args = ap.parse_args()
    path, open_list = build(args.exports, args.out)
    print(path)
    print(f"\n{len(open_list)} open item(s) before this paper can be submitted:")
    for line in open_list:
        print("  -", re.sub(r"\s+", " ", line))
