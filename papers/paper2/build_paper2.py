"""Build Paper 2 (.docx, IEEE conference format): CPW-fed decagonal-monopole MIMO antenna. Simulation study.

    python papers/make_figures.py && python papers/paper2/build_paper2.py

The metasurface comparison has been taken out at the authors' request: the match, the directivity and the radiation
pattern are those of the antenna alone. One thing could not be taken out. The coupling between the ports (and so the
ECC) was only computed in the run in which the ring board was present, so Section III-D says so and describes that
board in one paragraph. build_paper2_with_metasurface.py is the earlier version with the full comparison.

No result is typed by hand: the numbers are computed at build time from papers/data/p2_*.csv, and the design facts
come from papers/paper2/design.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import mimo_results  # noqa: E402
from build_paper2_with_metasurface import (AUTHORS, PATTERN, Citations, at_least, at_most, band_phrase,  # noqa: E402
                                           db, match, spans)
from check_numbers import cpw, load  # noqa: E402
from design import VERIFY, number, value  # noqa: E402
from ieee_docx import Paper  # noqa: E402
from literature_text import COMPARISON_ROWS, review_mimo  # noqa: E402

FIG = HERE / "figures"
OUT = HERE / "Paper2_Decagonal_MIMO_Antenna.docx"
TITLE = "A Wideband CPW-Fed Decagonal Monopole MIMO Antenna: A Simulation Study"


def build() -> Path:
    c, v = Citations(), value
    m0, m1 = match("noms"), match("ms")
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
    lobe = PATTERN["noMS"]
    f_dir, d_dir = load("p2_dir_noms")
    uwb = (f_dir >= 3.1) & (f_dir <= 10.6)
    inband = f_dir >= f_lo
    d_peak = (float(f_dir[d_dir.argmax()]), float(d_dir.max()))
    d_at_pattern = float(np.interp(float(PATTERN["f"]), f_dir, d_dir))
    board = f"{v('board_x')} mm × {v('board_y')} mm"

    p = Paper()
    p.title(TITLE)
    p.authors(AUTHORS)

    # ------------------------------------------------------------------------------------------------ abstract
    p.abstract(
        "A multiple-input multiple-output (MIMO) antenna made of coplanar-waveguide (CPW)-fed decagonal printed "
        f"monopoles on FR-4 is studied by full-wave simulation. The elements are regular decagons of {v('R')} mm "
        f"circumradius, fed by 50 Ω CPW lines on a board of {board} and {v('h_sub')} mm thickness, with a common "
        f"ground for ports 1 and 2. Port 1 is matched (|*S*_{{11}}| ≤ −10 dB) {band_phrase(m0)}, the limit of the "
        f"simulation; in between, |*S*_{{11}}| rises to {db(gap0[3])} dB. The maximum directivity in the *φ* = 0° "
        f"plane lies between {d_dir[uwb].min():.1f} and {d_dir[uwb].max():.1f} dBi over 3.1–10.6 GHz, with a peak of "
        f"{d_peak[1]:.1f} dBi at {d_peak[0]:.1f} GHz. The coupling between ports 1 and 2 was computed with an FR-4 "
        f"board carrying an array of double split rings placed {v('gap')} mm behind the antenna: the isolation is at "
        f"least 15 dB over {100 * tp['s21_share_15']:.0f}% of the matched range but falls to {db(-s21[1])} dB at "
        f"{s21[0]:.2f} GHz, and the upper bound of the envelope correlation coefficient obtained from the "
        f"S-parameter magnitudes is below 0.01 over {100 * tp['ecc_share_001']:.0f}% of the range and nowhere above "
        f"{at_most(tp['ecc_max'][1])}. The antenna is wideband, and its performance is limited by the coupling at "
        "the lower end of the band.")
    p.keywords("CPW-fed antenna, decagonal monopole, envelope correlation coefficient, MIMO antenna, mutual "
               "coupling, ultra-wideband antenna")

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
    p.body(
        "Most of these designs place neighbouring elements orthogonally and start at about 3 GHz. This paper "
        "reports the simulated behaviour of a MIMO antenna of parallel CPW-fed decagonal monopoles that share one "
        "ground conductor and are sized for a lower band edge below 2 GHz. The reflection coefficient, the "
        "directivity, the radiation pattern, the coupling between the ports and the diversity metrics that follow "
        "from it are reported as obtained, including where the performance is weak. Section II describes the "
        "design, Section III the results and their limitations, and Section IV concludes the paper.")

    # ------------------------------------------------------------------------------------------------ II
    p.heading("II. Antenna Design")
    p.subheading("A. Radiating Element")
    p.body(
        "Each radiating element is a regular decagon of circumradius *R* with a flat side towards the feed, "
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
    p.table("Dimensions of the Antenna (mm)", [
        ["Parameter", "*R*", "*W*_{f}", "*g*", "*L*_{g}", "*W*_{g}", "*p*", "*h*_{s}", "*D*"],
        ["Value", v("R"), v("W_f"), v("g"), v("L_g"), v("W_g"), v("p"), v("h_sub"), v("pitch")],
    ], [0.66, 0.34, 0.34, 0.34, 0.34, 0.36, 0.36, 0.34, 0.34], header_rows=0, bold_first_col=True,
        note="*D*: spacing of the feed lines of elements 1 and 2.")
    p.subheading("B. MIMO Arrangement")
    p.body(
        "Elements 1 and 2 are placed side by side along the lower edge of the board, as shown in Fig. 1, and are "
        "fed from that edge through ports 1 and 2. They are parallel and have the same polarisation. Their feed "
        f"lines are *D* = {v('pitch')} mm apart, which is {number('pitch') / lam(f_lo):.2f} free-space wavelength at "
        f"{f_lo:.2f} GHz, and the adjacent ground planes of these elements meet between them and form one "
        "conductor, so that ports 1 and 2 share a common ground.")
    p.body(
        f"The board, which fits in an outline of {board}, also carries a second row of two elements of the same "
        f"kind with a circumradius of {v('R_upper')} mm, fed from the upper edge through ports 3 and 4. Their "
        f"patches face those of the lower row at a distance of about {v('d_face')} mm, and the upper half of the "
        f"board is displaced sideways by about {v('board_step')} mm. These two elements are present in every "
        "simulation reported here, with their ports terminated, but they are not evaluated in this paper: the "
        "results concern ports 1 and 2.")
    p.figure(FIG / "fig_layout_ports.png",
             "Top view of the simulated antenna (CST Studio Suite) with the port numbers.", width_in=2.7)
    p.subheading("C. Simulation Setup")
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
        "The simulated reflection coefficient of port 1 is shown in Fig. 2. |*S*_{11}| is at or below −10 dB "
        f"{band_phrase(m0)}, the upper limit of the simulation. Between the two ranges it rises to {db(gap0[3])} dB "
        f"at {gap0[2]:.1f} GHz, so that the match is interrupted over {gap0[1] - gap0[0]:.2f} GHz. The lowest value "
        f"is {db(m0['min'][1])} dB at {m0['min'][0]:.2f} GHz. " + thin +
        f"The lower band edge, {f_lo:.2f} GHz, is {100 * (f_ray - f_lo) / f_ray:.0f}% below the estimate of (1), "
        "which is made for a single monopole, whereas here the ground conductor is shared by two elements. Since an "
        "upper band edge is not reached within the simulated range, no fractional bandwidth is quoted.")
    p.figure(FIG / "fig_s11_antenna.png",
             "Simulated reflection coefficient of port 1. The dotted line marks −10 dB.", width_in=3.4)
    p.subheading("B. Directivity")
    p.body(
        "Fig. 3 shows the simulated directivity of port 1 against frequency. The quantity plotted is the highest "
        "directivity found in the *φ* = 0° plane at each frequency; it is not the directivity in a fixed "
        f"direction. It lies between {d_dir[uwb].min():.1f} and {d_dir[uwb].max():.1f} dBi over 3.1–10.6 GHz and "
        f"between {d_dir[inband].min():.1f} and {d_dir[inband].max():.1f} dBi over the whole range above "
        f"{f_lo:.2f} GHz, with a peak of {d_peak[1]:.1f} dBi at {d_peak[0]:.1f} GHz. Below the lower band edge it "
        "falls steeply, as the antenna becomes electrically small and is no longer matched.")
    p.figure(FIG / "fig_directivity_antenna.png",
             "Simulated directivity of port 1 (maximum in the *φ* = 0° plane).", width_in=3.4)
    p.subheading("C. Radiation Pattern")
    p.body(
        f"The simulated directivity pattern of port 1 in the *φ* = 90° plane at {PATTERN['f']} GHz is shown in "
        "Fig. 4. The pattern has several lobes, as expected at a frequency at which the board is more than two "
        f"wavelengths across. The largest lobe of this cut points to *θ* = {lobe['dir']}° with a directivity of "
        f"{lobe['mag']} dBi and a half-power beamwidth of {lobe['hpbw']}°, and the next lobe is only {lobe['sll']} dB "
        f"lower, so the radiation is not concentrated in one direction. The maximum of Fig. 3 at this frequency, "
        f"{d_at_pattern:.1f} dBi, is higher than that of this cut, so the direction of maximum radiation lies outside "
        "it. One plane at one frequency does not establish the behaviour over the band.")
    p.figure(FIG / "fig_pattern_polar_antenna.png",
             f"Simulated directivity pattern of port 1 in the *φ* = 90° plane at {PATTERN['f']} GHz (CST Studio "
             "Suite). Angles are *θ* in degrees; the radial axis is the directivity in dBi.", width_in=3.0)
    p.subheading("D. Mutual Coupling and Diversity Performance")
    above = float(mag["s21"][mag["f"] >= tp["s21_above_m15"][2][1]].max())
    p.body(
        "The coupling between the ports was computed in a simulation in which a second FR-4 board was present "
        f"{v('gap')} mm behind the antenna. This board has the outline of the antenna board and a thickness of "
        f"1.6 mm, carries a 6 × 5 array of concentric double split rings (outer radii {v('r_out')} and {v('r_in')} mm, "
        f"strip width {v('w_ring')} mm, periods {v('pitch_x')} and about {v('pitch_y')} mm) on the face towards the "
        "antenna, and has no backing conductor. With this board, |*S*_{11}| of port 1 is at or below −10 dB "
        f"{band_phrase(m1)}, close to the ranges of Section III-A, so the board changes the match little. Its "
        "effect on the coupling has not been evaluated separately: the values of this subsection are those of the "
        "antenna with the board.")
    p.body(
        "The S-parameters of ports 1 and 2 are shown in Fig. 5. The reflection coefficient of port 2 follows that "
        "of port 1 closely, as expected of two nominally identical elements, and is at or below −10 dB from "
        f"{tp['s22_matched'][0][0]:.2f} GHz to beyond {m1['fmax']:.0f} GHz. Both ports are thus matched from "
        f"{tp['lower_edge']:.2f} GHz upwards, except for port 1 between {gap1[0]:.2f} and {gap1[1]:.2f} GHz; this "
        "is the range referred to below as the matched range. The coupling is strongest at the lower end of the "
        f"band: |*S*_{{21}}| reaches {db(s21[1])} dB at {s21[0]:.2f} GHz, where "
        f"{100 * 10 ** (s21[1] / 10):.0f}% of the power incident at port 1 is delivered to port 2, and it is above "
        f"−10 dB {spans(tp['s21_above_m10'])}. Above {tp['s21_above_m15'][2][1]:.1f} GHz the isolation is at least "
        f"{at_least(-above)} dB, and above {tp['s21_above_m15'][-1][1]:.1f} GHz at least 15 dB. Over the whole "
        f"matched range, the isolation is at least 15 dB at {100 * tp['s21_share_15']:.0f}% of the frequencies. The "
        "weak isolation at the lower end is the consequence of the arrangement: the two monopoles are parallel and "
        "co-polarised, less than a third of a wavelength apart at the lower band edge, and they share their ground "
        "conductor, with no decoupling structure between them.")
    p.figure(figs["sparams"],
             "Simulated S-parameters of ports 1 and 2, computed with the ring board present. The dotted line marks "
             "−10 dB.", width_in=3.4)
    p.body(
        "The envelope correlation coefficient (ECC) of ports 1 and 2 is computed from the S-parameters as "
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
        f"The right-hand side of (3) is plotted in Fig. 6. It is below 0.01 at {100 * tp['ecc_share_001']:.0f}% of "
        f"the frequencies of the matched range and has its highest value, {tp['ecc_max'][1]:.2f}, at the lower band "
        f"edge, {tp['ecc_max'][0]:.2f} GHz, well below the limit of 0.5 commonly required {c('sharawi_apm')}. The "
        f"corresponding apparent diversity gain, 10(1 − *ρ*_{{e}})^{{1/2}} dB {c('dg')}, is at least "
        f"{at_least(tp['dg_min'], 2)} dB. The same bound applied to the channel capacity loss, "
        f"−log_{{2}} det(**I** − **S**^{{H}}**S**) {c('ccl')}, where **S** is the S-matrix of ports 1 and 2, **I** "
        "the identity matrix and H the conjugate transpose, gives at most "
        f"{at_most(tp['ccl_max'][1], 1)} bit/s/Hz at the lower band edge; it is below 0.4 bit/s/Hz at "
        f"{100 * tp['ccl_share_04']:.0f}% of the frequencies and exceeds that value {spans(tp['ccl_above_04'])}, "
        "where the coupling is strongest.", cont=True)
    p.figure(figs["ecc"],
             "Upper bound (3) of the envelope correlation coefficient of ports 1 and 2 over the matched range, "
             "computed with the ring board present. The dotted line marks 0.5.", width_in=3.4)
    p.body(
        "Equation (2) assumes a lossless antenna in a uniform multipath environment. On a lossy FR-4 substrate it "
        "underestimates the correlation, and it does not account for the power absorbed in the substrate and in "
        f"the terminated elements of the upper row {c('hallbjorner', 'sharawi_misuse')}; the value obtained from "
        f"the far fields {c('vaughan')} is the reliable one and remains to be computed.")
    p.subheading("E. Limitations")
    p.body(
        "The results have clear limits. They are simulated and have not been verified against a second solver or a "
        "measurement. The radiation is described by the directivity of port 1 only: the realised gain and the "
        "efficiency, which include the loss of FR-4 and the power coupled into the other port, are not known. The "
        "coupling and the diversity metrics were computed with the ring board of Section III-D present, and the "
        "ECC is given as an upper bound of the S-parameter expression. Finally, the two elements of the upper row "
        "are not evaluated: their simulated port results did not satisfy passivity over part of the band and are "
        "excluded, and the effect of correcting those ports on the results for ports 1 and 2 has not been "
        "assessed.")
    p.subheading("F. Comparison with Reported Works")
    p.body(
        "Table II compares the antenna with reported multi-port UWB designs. These occupy boards of 38–65 mm side "
        f"and isolate their ports by more than 17 dB {c('yin', 'wu', 'zhang', 'ahmad')}, mostly through orthogonal "
        "placement. The present antenna is larger, because its element was sized for a lower band edge below "
        "2 GHz; its evaluated elements are parallel and not orthogonal, and its isolation at the lower end of the "
        "band is correspondingly lower. Its entry gives the simulated directivity, which is not comparable with "
        "the gains of the other works.")
    rows = [["Ref.", "Ports; element", "Size (mm)", "Band (GHz)", "Isolation (dB)", "ECC", "Peak gain (dBi)"]]
    rows += [[c(key), cells[0], cells[1], *cells[3:]] for key, cells in COMPARISON_ROWS
             if key in ("yin", "wu", "zhang", "ahmad")]
    rows.append(["This work", "4^{¶}; CPW decagonal monopoles, parallel", f"{v('board_x')} × {v('board_y')}",
                 f"{f_lo:.2f} to >{m0['fmax']:.0f}^{{‡}}", f"> {at_least(-s21[1])}^{{§}}",
                 f"< {at_most(tp['ecc_max'][1])}^{{§}}", f"{d_peak[1]:.1f}^{{†}}"])
    p.table("Comparison with Reported Multi-Port UWB Antennas", rows, [0.55, 1.75, 1.0, 1.0, 0.8, 0.75, 1.0],
            note="–: not available.  ^{†}Simulated directivity in the *φ* = 0° plane (gain not evaluated).  "
                 f"^{{‡}}Port 1, except {gap0[0]:.2f}–{gap0[1]:.2f} GHz; simulation only.  "
                 "^{§}Ports 1 and 2, computed with the ring board of Section III-D present; the ECC is the upper "
                 "bound (3).  ^{¶}Results for ports 1 and 2; ports 3 and 4 are not evaluated.", wide=True)

    # ------------------------------------------------------------------------------------------------ IV
    p.heading("IV. Conclusion")
    p.body(
        "A MIMO antenna of parallel CPW-fed decagonal monopoles on FR-4 has been studied by simulation. Port 1 is "
        f"matched {band_phrase(m0)}, and the maximum directivity in the *φ* = 0° plane reaches {d_peak[1]:.1f} dBi "
        f"at {d_peak[0]:.1f} GHz. With a ring-loaded FR-4 board behind the antenna, the isolation between ports 1 "
        f"and 2 is at least 15 dB over {100 * tp['s21_share_15']:.0f}% of the matched range but falls to "
        f"{db(-s21[1])} dB at {s21[0]:.2f} GHz, and the upper bound of the S-parameter ECC stays below "
        f"{at_most(tp['ecc_max'][1])}. The antenna is therefore wideband, and it is limited by the coupling of "
        "ports 1 and 2 at the lower end of the band. A decoupling structure between the elements, the coupling of "
        "the antenna without the second board, the evaluation of the realised gain, the efficiency and the "
        "far-field ECC, and the fabrication and measurement of a prototype are the next steps of this work.")
    p.references(c.listing())
    p.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
    print("\nPrinted in the paper without having been read from the CST model. Check before submission:")
    for key, text in VERIFY.items():
        print(f"  - {key}: {text}")
