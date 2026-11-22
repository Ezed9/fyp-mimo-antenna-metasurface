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
from check_numbers import bands, load  # noqa: E402
from design import open_items, value  # noqa: E402
from ieee_docx import Paper  # noqa: E402
from references import REFS  # noqa: E402

FIG = HERE / "figures"
SHOTS = HERE / "cst_screenshots"

TITLE = ("A Four-Port CPW-Fed Decagonal Monopole MIMO Antenna and the Effect of a Double-Ring Metasurface: "
         "A Simulation Study")
AFFIL = ("Department of Electronics and Communication Engineering", "National Institute of Technology Silchar",
         "Silchar, Assam 788010, India")
# Copied from Paper 1 as a starting point: confirm the author list and order for this paper.
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
    inside = (f >= bs[0][0])
    return {"f": f, "s": s, "bands": bs, "gaps": gaps, "min": (float(f[k]), float(s[k])), "fmax": float(f[-1]),
            "fmin": float(f[0]), "matched_ghz": sum(hi - lo for lo, hi, _, _ in bs),
            "thin": float(np.sort(s[inside & (s <= -10)])[-1])}


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
    if not mimo:
        todo.append(f"Coupling and diversity results: export the 4 x 4 S-matrix of both models to "
                    f"{exports}/mimo_noMS.s4p and {exports}/mimo_MS.s4p (Sections III-B and III-E are placeholders)")
    partial = d["lo"] > m0["fmin"] + 0.5 or d["hi"] < m0["fmax"] - 0.5
    if partial:
        todo.append(f"Directivity with the metasurface covers only {d['lo']:.0f}-{d['hi']:.0f} GHz: re-run the "
                    f"farfield result over {m0['fmin']:.0f}-{m0['fmax']:.0f} GHz and replace data/p2_dir_ms.csv")

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
    else:
        mimo_abstract = ("[[Isolation and envelope-correlation sentence: to be generated from the four-port "
                         "S-matrix.]] ")
    p.abstract(
        "A four-port multiple-input multiple-output (MIMO) antenna made of coplanar-waveguide (CPW)-fed decagonal "
        f"printed monopoles on a {v('board')} mm FR-4 board is studied by full-wave simulation, alone and with a "
        "6 × 5 array of concentric double-ring cells on a second FR-4 board placed behind it. Without the "
        f"metasurface, the reflection coefficient of port 1 is at or below −10 dB {band_phrase(m0)}; in between it "
        f"rises to {db(gap0[3])} dB at {gap0[2]:.2f} GHz. The metasurface leaves the match almost unchanged: the "
        f"bands become {band_phrase(m1).replace('from ', '', 1)}, and the mismatched region narrows from "
        f"{gap0[1] - gap0[0]:.2f} to {gap1[1] - gap1[0]:.2f} GHz. " + mimo_abstract +
        f"Over {d['lo']:.0f}–{d['hi']:.0f} GHz, the maximum directivity in the *φ* = 0° plane changes by "
        f"{signed(d['mean_diff'])} dB on average with the metasurface (between {signed(d['fall'][1])} and "
        f"{signed(d['rise'][1])} dB), and its peak rises from {d['peak0'][1]:.1f} to {d['peak1'][1]:.1f} dBi. At "
        f"{PATTERN['f']} GHz the main lobe in the *φ* = 90° plane moves from *θ* = {PATTERN['noMS']['dir']}° to "
        f"*θ* = {PATTERN['MS']['dir']}°. The ring surface therefore redirects the radiation at some frequencies but "
        "does not raise the directivity across the band.")
    p.keywords("CPW-fed antenna, decagonal monopole, metasurface, MIMO antenna, split-ring resonator, "
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
        "examines with the same model what a 6 × 5 surface of concentric double rings placed behind it changes. "
        "The reflection coefficient, the coupling between the ports, the diversity metrics, the directivity and "
        "the radiation pattern are compared with and without the surface, and the comparison is reported as "
        "obtained, including where the surface brings no benefit. Section II describes the design, Section III "
        "the results, and Section IV concludes the paper.")

    # ------------------------------------------------------------------------------------------------ II
    p.heading("II. Antenna Design")
    p.subheading("A. Radiating Element")
    p.body(
        f"Each element is a regular decagon of circumradius *R* = {v('R')} mm with a flat side towards the feed, "
        f"printed on an FR-4 substrate (*ε*_{{r}} = {v('eps_r')}, tan *δ* = {v('tan_d')}) of thickness "
        f"*h*_{{s}} = {v('h_sub')} mm. It is fed by a CPW line with a strip of width *W*_{{f}} = {v('W_f')} mm and "
        f"slots of *g* = {v('g')} mm, between two ground planes of width *W*_{{g}} = {v('W_g')} mm and length "
        f"*L*_{{g}} = {v('L_g')} mm. The lower side of the decagon lies *p* = {v('p')} mm above the ground edge, and "
        "the back of the substrate carries no copper. The lower edge of the band of such a monopole can be "
        f"estimated by replacing the patch with a cylindrical monopole of the same height and area {c('ray')}:")
    p.equation(r"f_L = \frac{7.2}{(l + r + p)\,k}\ \text{GHz},\quad r = \frac{A}{2\pi l}")
    p.body(
        "where *l* = 2*R* cos 18° = 28.5 mm is the height of the decagon, *A* = 5*R*^{2} sin 36° = 661 mm^{2} its "
        "area, *r* = 3.7 mm the radius of the equivalent cylinder, all taken in centimetres, and *k* = 1.15 for "
        f"FR-4 {c('ray')}. Equation (1) gives *f*_{{L}} ≈ 1.90 GHz.")
    p.subheading("B. Four-Port Arrangement")
    p.body(
        "The four elements are placed in two rows of two on one board, as shown in Fig. 1(a). The two elements of "
        "the upper row are fed from the upper edge of the board and the two of the lower row from the lower edge, "
        "so that the patches of the two rows face each other across the centre of the board; all four elements "
        f"have the same polarisation. The feed lines of a row are {v('pitch')} mm apart, which is 0.29 free-space "
        f"wavelength at {m0['bands'][0][0]:.2f} GHz, and the facing patches are separated by {v('d_face')} mm. "
        f"In the present model {v('ground_statement')}, and {v('port_map')}.")
    p.figure([SHOTS / "mimo_design_without_metasurface.png", SHOTS / "metasurface_design.png"],
             "Top views of the simulated model (CST Studio Suite): (a) four-port antenna, (b) 6 × 5 double-ring "
             "metasurface.", width_in=1.62, sublabels=True, side_by_side=True)
    p.subheading("C. Metasurface")
    p.body(
        "The metasurface of Fig. 1(b) is a 6 × 5 array of cells, each made of two concentric copper rings of strip "
        f"width {v('w_ring')} mm: an outer ring of outer radius {v('r_out')} mm and an inner ring of outer radius "
        f"{v('r_in')} mm, each with a split of {v('split')} mm. The cells repeat every {v('pitch_x')} mm along the "
        f"rows and every {v('pitch_y')} mm along the columns. The array is printed on a {v('ms_board')} mm FR-4 "
        f"board of thickness 1.6 mm, which {v('ms_ground')}. The board is placed parallel to the antenna, at an "
        f"air gap of {v('gap')} mm from the back of the antenna substrate, with the rings towards the antenna.")
    p.body(
        "A ring resonates when its circumference is close to one guided wavelength, and a split halves the "
        "frequency of the lowest resonance. With an effective permittivity of (*ε*_{r} + 1)/2 = 2.65, the outer "
        "ring is one wavelength long at about 4.0 GHz and the inner ring at about 5.6 GHz, so the lowest "
        f"resonances of the split rings lie near 2.0 and 2.8 GHz {c('pendry')}. All of them are below 6 GHz. Above "
        "that frequency the rings are not resonant, and no in-phase reflection of the kind obtained from a "
        f"high-impedance surface {c('sievenpiper')} is expected from them. The reflection phase of the cell has not "
        "been computed.")
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
        f"ranges it rises to {db(gap0[3])} dB at {gap0[2]:.2f} GHz. The lowest value is {db(m0['min'][1])} dB at "
        f"{m0['min'][0]:.2f} GHz. The lower band edge, {m0['bands'][0][0]:.2f} GHz, is below the estimate of (1), "
        "which was made for an element on its own.")
    p.figure(FIG / "fig_s11.png",
             "Simulated reflection coefficient of port 1 without and with the metasurface.", width_in=3.4)
    f, s0, s1 = m0["f"], m0["s"], np.interp(m0["f"], m1["f"], m1["s"])
    rng = f >= m0["bands"][0][0] + 0.1
    lin = 10 ** (s1[rng] / 20) - 10 ** (s0[rng] / 20)
    p.body(
        f"With the metasurface, |*S*_{{11}}| is at or below −10 dB {band_phrase(m1)}, and the highest value "
        f"between the two ranges is {db(gap1[3])} dB at {gap1[2]:.2f} GHz. The mismatched region thus narrows from "
        f"{gap0[1] - gap0[0]:.2f} to {gap1[1] - gap1[0]:.2f} GHz, but it does not close. Elsewhere the two curves "
        f"follow each other: the lower band edge moves by {abs(m0['bands'][0][0] - m1['bands'][0][0]) * 1000:.0f} "
        f"MHz, and the root-mean-square change of the linear |*S*_{{11}}| over the band is "
        f"{np.sqrt((lin ** 2).mean()):.2f}. The larger differences in decibels are confined to the deep minima, "
        "which move by 0.1–0.3 GHz. The metasurface therefore neither detunes the antenna nor improves its match "
        "appreciably. Since an upper band edge is not reached within the simulated range, no fractional bandwidth "
        "is quoted.")
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
    else:
        p.body(
            "[[The transmission coefficients between the ports have not been exported from the simulation. This "
            "subsection, Fig. 3 and Table I are generated by the build script from the four-port S-matrix of the "
            "two models: all six transmission coefficients against frequency, the highest coupling of each port "
            "pair inside the matched range, and the difference between the reflection coefficients of the four "
            "ports.]]")
        p.body(
            f"The geometry indicates where the coupling is expected to be strongest. The facing patches are "
            f"{v('d_face')} mm apart, 0.014 free-space wavelength at {m0['bands'][0][0]:.2f} GHz, and their facing "
            "edges are the open ends of the two monopoles; the elements of a row are parallel, have the same "
            "polarisation and are less than a third of a wavelength apart at the lower band edge. These two kinds "
            "of pair should be examined first.")
    # --- directivity ---
    p.subheading("C. Directivity")
    part = (f" With the metasurface the result is available from {d['lo']:.0f} to {d['hi']:.0f} GHz only, so the "
            "comparison is limited to that range." if partial else "")
    fig_no = 4 if mimo else 3
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
        f"the directivity drops to {d['min1'][1]:.1f} dBi. The metasurface therefore redistributes the directivity "
        "over frequency without raising its level: the average change is a fraction of a decibel.")
    # --- pattern ---
    a, b = PATTERN["noMS"], PATTERN["MS"]
    p.subheading("D. Radiation Pattern")
    p.body(
        f"The simulated directivity patterns of port 1 in the *φ* = 90° plane at {PATTERN['f']} GHz are shown in "
        f"Fig. {fig_no + 1}. Both patterns have several lobes, as expected of an element that is more than one "
        "wavelength from the far edge of the board at this frequency. Without the metasurface, the largest lobe "
        f"points to *θ* = {a['dir']}°, in the rear half-space, with a directivity of {a['mag']} dBi and a "
        f"half-power beamwidth of {a['hpbw']}°; the next lobe is only {a['sll']} dB lower. With the metasurface, "
        f"the largest lobe points to *θ* = {b['dir']}°, close to the normal to the board, with {b['mag']} dBi and a "
        f"beamwidth of {b['hpbw']}°, and the next lobe is {b['sll']} dB lower. The surface thus moves the strongest "
        f"radiation from the rear to the front half-space and raises the directivity of the largest lobe by "
        f"{float(b['mag']) - float(a['mag']):.2f} dB, but a rear lobe only a few decibels below the main lobe "
        "remains. This is one plane at one frequency and one port; it does not establish the behaviour over the "
        "band.")
    p.figure([FIG / "fig_pattern_without.png", FIG / "fig_pattern_with.png"],
             f"Simulated directivity pattern of port 1 in the *φ* = 90° plane at {PATTERN['f']} GHz: (a) without, "
             "(b) with the metasurface. The radial scales of the two plots differ (CST Studio Suite).",
             width_in=1.66, sublabels=True, side_by_side=True)
    # --- diversity ---
    p.subheading("E. Diversity Performance")
    p.body(
        "The envelope correlation coefficient (ECC) between ports *i* and *j* of an *N*-port antenna is computed "
        f"from the S-parameters as {c('blanch')}")
    p.equation(r"\rho_{e,ij} = \frac{\left|\sum_{n=1}^{N} S_{ni}^{*} S_{nj}\right|^{2}}"
               r"{\left(1 - \sum_{n=1}^{N} |S_{ni}|^{2}\right)\left(1 - \sum_{n=1}^{N} |S_{nj}|^{2}\right)}")
    p.body(
        f"and the apparent diversity gain as DG = 10(1 − *ρ*_{{e}})^{{1/2}} dB {c('dg')}. Equation (2) assumes a "
        "lossless antenna in a uniform multipath environment; on a lossy FR-4 substrate it underestimates the "
        f"correlation, so the value obtained from the far fields {c('vaughan')} should be reported as well "
        f"{c('hallbjorner', 'sharawi_misuse')}. "
        "The total active reflection coefficient (TARC) for an excitation vector **a** and the channel capacity "
        f"loss (CCL) follow from the S-matrix **S** as {c('manteghi', 'ccl')}")
    p.equation(r"\Gamma_a^t = \frac{\lVert \mathbf{S}\mathbf{a} \rVert}{\lVert \mathbf{a} \rVert},\qquad "
               r"C_{loss} = -\log_2 \det\!\left(\mathbf{I} - \mathbf{S}^{H}\mathbf{S}\right)")
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
            "[[The ECC, the diversity gain, the TARC and the CCL of the two models are generated by the build "
            "script from the same four-port S-matrix as Section III-B, together with the ECC figure. Far-field "
            "ECC needs the complex far fields of all four ports.]]")
    # --- discussion ---
    p.subheading("F. Discussion and Limitations")
    p.body(
        "Taken together, the results show a surface that interacts weakly with the antenna. The match is "
        f"practically unchanged, the mean directivity over {d['lo']:.0f}–{d['hi']:.0f} GHz changes by "
        f"{signed(d['mean_diff'])} dB, and the pattern at {PATTERN['f']} GHz is turned towards the front without "
        "becoming unidirectional. This is consistent with Section II-C: in the range in which the directivity was "
        "compared, the rings are above their resonances and cannot provide an in-phase reflection. "
        + reflector_note(c))
    p.body(
        "The present results have clear limits. Only port 1 has been evaluated, and only its directivity: the "
        "realized gain and the efficiency, which include the loss of FR-4 and the power coupled into the other "
        "ports, are not known." + (" The coupling between the ports and the diversity metrics remain to be "
                                   "computed." if not mimo else "") +
        " The effect of the rings has not been separated from that of the board that carries them; simulations "
        "with a bare FR-4 board and with a plain copper plate at the same position are needed for that. Finally, "
        "the model has not been verified against a second solver or a measurement.")
    # --- comparison ---
    p.subheading("G. Comparison with Reported Works")
    p.body(comparison_text(c, "II" if mimo else "I"))
    iso = f"{db(-w1['coupling'])}" if mimo else "[[–]]"
    ecc = f"< {max(e0, e1):.3f}" if mimo else "[[–]]"
    rows = [["Ref.", "Ports; element", "Size (mm)", "Added surface; gap (mm)", "Band (GHz)", "Isolation (dB)",
             "ECC", "Peak gain (dBi)"]]
    rows += [[c(key), *cells] for key, cells in COMPARISON_ROWS]
    rows.append(["This work", "4; CPW decagonal monopole", v("board"), f"6 × 5 double ring; {v('gap')}",
                 f"{m1['bands'][0][0]:.2f}–>{m1['fmax']:.0f}^{{‡}}", iso, ecc, f"{d['peak1'][1]:.1f}^{{†}}"])
    p.table("Comparison with Reported Four-Port Antennas", rows, [0.5, 1.2, 0.9, 1.35, 0.85, 0.7, 0.65, 0.85],
            note=f"–: not stated in the part of the source that was read.  ^{{†}}Simulated directivity in the *φ* = 0° "
                 f"plane (gain not evaluated).  ^{{‡}}Port 1, except {gap1[0]:.2f}–{gap1[1]:.2f} GHz; simulation "
                 "only.", wide=True)

    # ------------------------------------------------------------------------------------------------ IV
    p.heading("IV. Conclusion")
    p.body(
        "A four-port MIMO antenna of CPW-fed decagonal monopoles on FR-4 has been simulated with and without a "
        f"6 × 5 double-ring metasurface. Port 1 is matched {band_phrase(m1)} with the metasurface, and the match "
        f"is practically the same without it. " +
        (f"The lowest isolation is {db(-w1['coupling'])} dB and the highest ECC {e1:.3f}. " if mimo else
         "[[One sentence on isolation and ECC.]] ") +
        f"Over {d['lo']:.0f}–{d['hi']:.0f} GHz the metasurface changes the mean directivity by "
        f"{signed(d['mean_diff'])} dB and its peak from {d['peak0'][1]:.1f} to {d['peak1'][1]:.1f} dBi, and at "
        f"{PATTERN['f']} GHz it turns the main lobe towards the front of the board. The double-ring surface in its "
        "present form therefore does not act as a gain-enhancing reflector over the band. Control simulations with "
        "a bare board and a copper plate, the evaluation of the realized gain and efficiency of all ports, a cell "
        "with an in-phase reflection band inside the operating range, and the fabrication and measurement of a "
        "prototype are the next steps of this work.")
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
