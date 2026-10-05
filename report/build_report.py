# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1"]
# ///
"""Build the mid-semester report from the college template (report/UG_Project_Report_Template.docx).

Run from the repo root:  uv run report/make_diagrams.py && uv run report/build_report.py

The template is filled in place: its title page, the eight section headings and its page breaks stay as they are,
and each "Write content here..." becomes that section's content. The contents page and the lists of figures and
tables are Word fields; their entries and page numbers are taken from a LibreOffice render (two passes), so they are
correct when the file is opened. After editing the .docx in Word, press Ctrl+A then F9 to refresh them.

Results that do not exist yet are dashed "pending" boxes. Nothing is invented: every number below comes from the
team's CST screenshots (figures/cst_*.png), from report/literature.py, or is computed and labelled as computed.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import docx_helpers as dh
import literature as lit
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx_helpers import md, mf, mr, mrad, msub, msup

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "figures"
OUT = ROOT / "report" / "MidSem_Report.docx"

# ============================================================================= design data
# From the team's CST model. None = not received yet; shown as "pending" in the report.
DIMENSIONS: list[tuple[str, str, str | None]] = [
    ("W_{s} × L_{s}", "Substrate (board) size", None),
    ("h_{s}", "Substrate thickness", None),
    ("R", "Radius of the radiating patch", "15"),
    ("L_{g}", "y-coordinate of the top edge of the CPW ground planes", "−7"),
    ("W_{f}", "Width of the CPW signal strip", None),
    ("g", "Width of the CPW slots", None),
]
SUBSTRATE: str | None = None        # e.g. "FR-4 (ε_{r} = 4.3, tan δ = 0.025), 1.6 mm"
SRR: dict[str, str | None] = {"cell": None, "period": None, "array": None, "substrate": None}

LG_VALUES = "ten values from −20 mm to −7 mm"        # legend of figures/cst_single_Lg_sweep.png
R_VALUES = "4 mm to 15 mm (13 values)"                # legend of figures/cst_single_R_sweep.png

# Result screenshots expected from the team (pending boxes until they exist).
GEOMETRY = "cst_single_geometry.png"
UNITCELL_FIGS = ["cst_srr_unitcell.png", "cst_srr_phase.png"]
MS_FIGS = ["cst_single_ms_s11.png", "cst_single_ms_gain.png"]


def have(name: str) -> bool:
    return (FIGS / name).exists()


def mm(x: str | None) -> str:
    return "pending" if x is None else x


# ============================================================================= numbering context
@dataclass
class Ctx:
    doc: object
    cite: dh.Citer
    pages: dict[str, int]
    fig_n: int = 0
    tab_n: int = 0
    eq_n: int = 0
    heads: list[tuple[int, str]] = field(default_factory=list)
    figs: list[tuple[int, str]] = field(default_factory=list)
    tabs: list[tuple[int, str]] = field(default_factory=list)

    def p(self, text: str, **kw) -> Paragraph:
        return dh.para(self.doc, text, self.cite, **kw)

    def h2(self, text: str) -> None:
        self.heads.append((2, text))
        dh.heading(self.doc, text, level=2)

    def eq(self, nodes: list) -> int:
        self.eq_n += 1
        self.doc.paragraphs[-1].paragraph_format.keep_with_next = True  # the sentence that introduces it
        dh.equation(self.doc, nodes, self.eq_n)
        return self.eq_n

    def next_fig(self) -> int:
        return self.fig_n + 1

    def next_tab(self) -> int:
        return self.tab_n + 1

    def fig(self, names: list[str], caption: str, width: float = 6.0, pending: str | None = None) -> int:
        """One or more stacked images; any missing image becomes a pending box (never a made-up plot)."""
        self.fig_n += 1
        if not any(have(n) for n in names):
            dh.pending_box(self.doc, "Result pending: CST simulation", pending or ", ".join(names), height=1.1)
        for name in names:
            if have(name):
                dh.image(self.doc, FIGS / name, width)
        dh.seq_caption(self.doc, "Fig.", self.fig_n, caption, self.cite)
        self.figs.append((self.fig_n, caption))
        return self.fig_n

    def table(self, caption: str, header: list[str], rows: list[list[str]], widths: list[float], **kw) -> int:
        self.tab_n += 1
        dh.seq_caption(self.doc, "Table", self.tab_n, caption, self.cite, above=True)
        dh.table(self.doc, header, rows, widths, cite=self.cite, **kw)
        self.tabs.append((self.tab_n, caption))
        return self.tab_n


# ============================================================================= sections
def abstract(c: Ctx) -> None:
    lo, hi = lit.THIS_WORK["band_ghz"]
    fbw = lit.fractional_bw(lo, hi) * 100
    ms_status = ("The characterisation of the metasurface unit cell and the simulation of the antenna with the "
                 "metasurface are in progress; their results will be added before the final submission.")
    c.p("Ultra-wideband (UWB) radios and multiple-input multiple-output (MIMO) antennas together support high data "
        "rates over short ranges, but the printed monopoles normally used for UWB radiate on both sides of the board "
        "and therefore have low gain. This project develops a wideband MIMO antenna with a metasurface. This "
        "mid-semester report covers Phase I: a single coplanar-waveguide (CPW) fed planar monopole backed by a "
        "split-ring-resonator (SRR) metasurface.")
    c.p(f"The monopole was modelled in CST Studio Suite and optimised through two parametric sweeps: the position of "
        f"the CPW ground-plane edge (L_{{g}}) and the patch radius (R). The optimised antenna (L_{{g}} = −7 mm, "
        f"R = 15 mm) has |S_{{11}}| ≤ −10 dB from {lo:.2f} GHz to {hi:.2f} GHz, a fractional bandwidth of "
        f"{fbw:.1f} %, which covers the whole 3.1–10.6 GHz UWB band. Its simulated IEEE gain is about "
        f"{lit.THIS_WORK['gain_ieee_uwb'].strip('≈ ')} dBi across that band. To redirect the backward radiation, a "
        f"single-SRR metasurface is placed {lit.GAP_MM} mm behind the antenna across an air gap. A reflection-phase "
        f"analysis shows that, at this small gap, a plain metal plate would work against the forward radiation over "
        f"most of the UWB band, which is why an in-phase metasurface is needed. {ms_status}")
    c.p("A review of ten recent papers on metasurface-loaded single and MIMO antennas places the work in context. "
        "Phase II will extend the design to a multi-port MIMO antenna, evaluate its isolation and diversity "
        "performance, and validate a fabricated prototype by measurement.")


def introduction(c: Ctx) -> None:
    c.h2("Background and Motivation")
    c.p("Short-range wireless links for high-definition video, personal-area networks, imaging and sensing need data "
        "rates that narrowband radios cannot provide. Ultra-wideband (UWB) technology meets this need by spreading "
        "very low-power signals over a very wide band: in 2002 the FCC allowed unlicensed UWB operation from 3.1 to "
        "10.6 GHz at a power spectral density of at most −41.3 dBm/MHz [@fcc]. Multiple-input multiple-output (MIMO) "
        "techniques raise capacity further: with several antennas at each end of the link, capacity grows roughly in "
        "proportion to the number of antennas without extra bandwidth or transmit power [@foschini, telatar]. "
        "Combining the two needs several wideband antennas that are compact, well matched over the whole band and "
        "weakly coupled to each other [@sharawi].")
    c.p("Printed planar monopoles are the most common UWB radiators. A planar disc or polygon above a ground plane "
        "behaves like a thick cylindrical monopole, and its closely spaced resonances overlap into a very wide "
        "impedance band [@agrawall, ray]. A coplanar-waveguide (CPW) feed keeps the signal strip and the ground on the "
        "same side of the substrate, needs no vias and lets several elements share one ground later [@simons]. The "
        "price is gain: a printed monopole radiates almost equally into both half-spaces, so roughly half of its "
        "power leaves through the back of the board and the gain stays at a few dBi [@balanis].")
    c.p("A reflector behind the antenna can turn the backward radiation forward. A metal plate, however, reflects with "
        "a 180° phase shift and must sit a quarter wavelength away (24.2 mm at 3.1 GHz) for the reflected wave to add "
        "in phase, and over a band as wide as UWB no fixed gap satisfies that. Metasurfaces, two-dimensional arrays "
        "of sub-wavelength resonant cells [@holloway], can be designed to reflect in phase near their resonance "
        "[@sievenpiper, yang], so they can sit much closer to the antenna and keep the structure thin. The "
        "split-ring resonator (SRR) [@pendry] is a compact cell whose resonance is tuned by its geometry alone.")
    c.h2("Problem Statement")
    c.p("Design a compact CPW-fed planar monopole that covers the full 3.1–10.6 GHz UWB band, and raise its gain with "
        f"a split-ring-resonator metasurface placed {lit.GAP_MM} mm behind it across an air gap without losing the "
        "impedance bandwidth. Then extend the design to a multi-port MIMO antenna with high isolation and good "
        "diversity performance.")
    c.h2("Objectives")
    dh.bullets(c.doc, [
        "**O1 (Phase I, done):** design and optimise a CPW-fed planar monopole with |S_{11}| ≤ −10 dB over at least "
        "3.1–10.6 GHz.",
        "**O2 (Phase I, in progress):** design a split-ring-resonator unit cell and characterise its reflection phase.",
        f"**O3 (Phase I, in progress):** place the metasurface {lit.GAP_MM} mm behind the antenna and quantify the "
        "change in gain, radiation pattern and matching, compared with no reflector and with a plain metal plate at "
        "the same gap.",
        "**O4 (Phase II):** extend the design to a 2-/4-port MIMO antenna with the metasurface and evaluate isolation, "
        "envelope correlation coefficient (ECC), diversity gain (DG), total active reflection coefficient (TARC), "
        "channel capacity loss (CCL) and mean effective gain (MEG).",
        "**O5 (Phase II):** fabricate a prototype and validate it by measurement.",
    ], c.cite)
    c.h2("Organisation of the Report")
    c.p("The Literature Review summarises ten recent papers on metasurface-loaded single and MIMO antennas. "
        "Methodology describes the design flow, the governing equations and the simulation set-up. Work Done Till "
        "Mid-Semester presents the parametric study, the optimised antenna and the status of the metasurface. The "
        "Work Plan and Expected Outcomes describe the rest of the project.")


def literature_review(c: Ctx) -> None:
    c.p("The review covers two groups of papers, selected as described in the separate literature-review document: "
        "(i) single wideband antennas whose gain is raised by a metasurface, artificial magnetic conductor (AMC) or "
        "frequency selective surface (FSS) reflector, which bear directly on Phase I, and (ii) MIMO antennas that use "
        "metasurfaces, which inform Phase II. Every value below was checked against the full text of each paper.")
    c.h2("Single Antennas with a Metasurface Reflector")
    for p in lit.SINGLE:
        c.p(f"**{p.short}** [@{p.key}]: {p.summary or '[to be completed from the full text]'}")
    c.h2("MIMO Antennas with Metasurfaces")
    for p in lit.MIMO:
        c.p(f"**{p.short}** [@{p.key}]: {p.summary or '[to be completed from the full text]'}")
    c.h2("Comparison and Research Gap")
    import build_literature_review as blr
    c.table("Single wideband antennas with a metasurface, AMC or FSS reflector.", blr.SINGLE_HEAD,
            blr.single_rows(c.cite), blr.SINGLE_W, size=8.5, highlight_last=True)
    c.table("MIMO antennas that use a metasurface (background for Phase II).", blr.MIMO_HEAD, blr.mimo_rows(c.cite),
            blr.MIMO_W, size=8.5)
    for t in lit.GAP_POINTS or ["[Research gap: to be completed from the full texts.]"]:
        c.p(t)


def methodology(c: Ctx) -> None:
    lo, hi = lit.THIS_WORK["band_ghz"]
    c.h2("Design Flow")
    n = c.next_fig()
    c.p(f"The work follows the flow of Fig. {n}. The antenna is optimised first, one parameter at a time, so that the "
        "effect of each parameter is visible. The metasurface is then designed as a unit cell, placed behind the "
        "optimised antenna and compared with no reflector and with a plain metal plate at the same gap. Phase II "
        "reuses the optimised antenna as the MIMO element.")
    c.fig(["fig_design_flow.png"], "Design flow of the project; steps 1–4 are complete.", width=5.4)

    c.h2("Antenna Design")
    shape = "a planar patch"
    c.p(f"The radiator is {shape} of radius R fed by a 50 Ω CPW line. The signal strip of width W_{{f}} is separated "
        "from the two coplanar ground planes by slots of width g, and the top edge of the ground planes lies at "
        "y = L_{g}, so L_{g} sets how close the ground comes to the patch. Two quantities dominate the matching of a "
        "printed monopole: the ground geometry near the feed, which controls the coupling between patch and ground, "
        "and the patch size, which sets the lowest resonance and how the higher-order resonances overlap [@ray]. "
        "The lower band edge of a planar monopole can be estimated from an equivalent cylindrical monopole "
        "[@agrawall, ray]:")
    e1 = c.eq([msub([mr("f")], [mr("L", False)]), mr("≈", False),
               mf([mr("7.2", False)], [mr("L"), mr("+", False), mr("r"), mr("+", False), mr("p")]),
               mr(" GHz", False)])
    c.p(f"where L is the height of the patch, r the radius of the equivalent cylinder (2πrL equals the patch area) and "
        f"p the gap between the patch and the ground, all in centimetres. Equation ({e1}) ignores the substrate, which "
        "lowers the frequency further, so it serves only as a starting point for the CST sweeps. The bandwidth is "
        "reported as the fractional bandwidth")
    e2 = c.eq([mr("FBW", False), mr("=", False),
               mf([mr("2", False), md([msub([mr("f")], [mr("H", False)]), mr("−", False),
                                       msub([mr("f")], [mr("L", False)])])],
                  [msub([mr("f")], [mr("H", False)]), mr("+", False), msub([mr("f")], [mr("L", False)])])])
    c.p(f"where f_{{L}} and f_{{H}} are the lower and upper −10 dB frequencies; UWB operation requires f_{{L}} ≤ 3.1 GHz "
        f"and f_{{H}} ≥ 10.6 GHz, i.e. FBW ≥ 109 % from ({e2}). CST reports the IEEE gain G, which includes conduction "
        "and dielectric losses but not the mismatch at the port; the realized gain also includes the mismatch:")
    e3 = c.eq([msub([mr("G")], [mr("R", False)]), mr("=", False),
               md([mr("1", False), mr("−", False), msup([md([mr("Γ")], "|", "|")], [mr("2", False)])]), mr("G")])
    c.p(f"where Γ = S_{{11}} is the reflection coefficient at the port. Inside the −10 dB band |Γ|^{{2}} ≤ 0.1, so "
        f"the realized gain is at most 0.46 dB below the IEEE gain "
        f"(computed from ({e3})). Table {c.next_tab()} lists the antenna dimensions.")
    c.table("Dimensions of the optimised antenna (mm).", ["Symbol", "Description", "Value"],
            [[s, d, mm(v)] for s, d, v in DIMENSIONS], [1.2, 3.6, 1.2], size=10)

    c.h2("Split-Ring-Resonator Metasurface")
    c.p("Each metasurface cell is a single split-ring resonator: a metal ring interrupted by one split. The ring "
        "behaves as an inductance L and the split as a capacitance C [@pendry], so the cell resonates at")
    e4 = c.eq([msub([mr("f")], [mr("0", False)]), mr("=", False),
               mf([mr("1", False)], [mr("2", False), mr("π"), mrad(mr("L"), mr("C"))])])
    c.p(f"A larger ring raises L and a narrower split raises C, and both lower f_{{0}} in ({e4}). The cell is "
        "characterised on its own with unit-cell (periodic) boundaries and a Floquet port, which gives the reflection "
        "phase φ_{R} of an infinite array under normal incidence. Near resonance an in-phase reflector has φ_{R} close "
        "to 0°, and its useful band is usually taken as the range where φ_{R} stays within ±90° [@sievenpiper, yang].")

    c.h2("Antenna with the Metasurface Reflector")
    n_stack, n_phase, t_phase = c.next_fig(), c.next_fig() + 1, c.next_tab()
    c.p(f"The metasurface is placed {lit.GAP_MM} mm behind the antenna substrate with only air in between "
        f"(Fig. {n_stack}).")
    c.fig(["fig_stackup.png"], f"Side view of the antenna, the {lit.GAP_MM} mm air gap and the SRR metasurface "
          "(schematic, not to scale).", width=4.4)
    c.p("The wave radiated backwards travels to the metasurface and back, a round trip of 2h, and is reflected with "
        "phase φ_{R}. It adds constructively to the forward wave when", keep_next=True)
    e5 = c.eq([msub([mr("φ")], [mr("R", False)]), mr("−2", False), msub([mr("k")], [mr("0", False)]),
               mr("h"), mr("=2", False), mr("n"), mr("π")])
    c.p(f"where k_{{0}} = 2π/λ_{{0}} and n is an integer; the reflection still helps as long as the phase error stays "
        f"within ±90°. A metal (PEC) plate has φ_{{R}} = 180°, so ({e5}) would require h = λ_{{0}}/4. Table {t_phase} and "
        f"Fig. {n_phase} evaluate ({e5}) at h = {lit.GAP_MM} mm (computed, not simulated).")
    rows = []
    for f in (lo, 3.1, 5.0, 6.85, 9.61, 10.6, hi):
        lam = lit.wavelength_mm(f)
        need = lit.round_trip_phase_deg(f, lit.GAP_MM)
        err = 180 - need
        rows.append([f"{f:.2f}", f"{lam:.1f}", f"{lit.GAP_MM / lam:.3f}", f"{need:.0f}°", f"{err:.0f}°",
                     "boundary" if abs(err - 90) < 0.5 else ("adds" if err < 90 else "reduces")])
    c.table(f"Reflection phase needed at h = {lit.GAP_MM} mm and the error of a metal plate (computed from "
            f"equation ({e5})).", ["f (GHz)", "λ_{0} (mm)", "h/λ_{0}", "Needed φ_{R} = 2k_{0}h",
                                    "PEC error 180° − 2k_{0}h", "PEC reflection"],
            rows, [0.75, 0.8, 0.75, 1.3, 1.35, 1.05], size=9.5)
    c.fig(["fig_gap_phase.png"], f"Reflection phase needed for in-phase addition at h = {lit.GAP_MM} mm (line) with the "
          "±90° window (band), compared with a metal plate (computed).", width=5.0)
    c.p(f"The needed phase rises from {lit.round_trip_phase_deg(lo, lit.GAP_MM):.0f}° at {lo:.2f} GHz to "
        f"{lit.round_trip_phase_deg(hi, lit.GAP_MM):.0f}° at {hi:.2f} GHz. A metal plate lies more than 90° away "
        "from it below about 9.6 GHz, so at this gap it would reduce the forward gain over most of the UWB band. A "
        "metasurface whose reflection phase follows the band in Fig. {n} can instead add to the forward beam. This "
        "ray picture ignores the near-field coupling between antenna and metasurface, which is strong at "
        f"{lit.GAP_MM / lit.wavelength_mm(3.1):.3f}λ_{{0}} (at 3.1 GHz); the metasurface also loads the antenna, so "
        "its matching must be re-checked, and L_{g} re-tuned if needed, with the metasurface in place."
        .replace("{n}", str(n_phase)))

    c.h2("Simulation Set-up")
    c.p("All simulations use CST Studio Suite 2019 with the frequency-domain solver over 0–18 GHz. The CPW line is "
        "excited by a waveguide port that spans the signal strip, both slots and part of each ground plane, and open "
        f"(add-space) boundaries surround the structure. The ground-edge sweep used {LG_VALUES} and the radius sweep "
        f"{R_VALUES}. Gain was obtained from far-field monitors spread over 1–18 GHz. The metasurface unit cell uses "
        "unit-cell boundaries in x and y and a Floquet port in z.")


def work_done(c: Ctx) -> None:
    lo, hi = lit.THIS_WORK["band_ghz"]
    tw = lit.THIS_WORK
    c.h2("Antenna Geometry")
    n = c.next_fig()
    c.p(f"Fig. {n} shows the CPW-fed antenna; its dimensions are listed in Table 3. "
        f"Substrate: {SUBSTRATE or 'pending (from the CST parameter list)'}.")
    c.fig([GEOMETRY], "Geometry of the CPW-fed antenna (CST model).", pending="CST screenshot of the antenna geometry")

    c.h2("Parametric Study")
    n_lg, n_r = c.next_fig(), c.next_fig() + 1
    c.p(f"Fig. {n_lg} shows |S_{{11}}| for {LG_VALUES} of the ground-edge position L_{{g}} with R = 15 mm. As L_{{g}} "
        "increases, the ground edge moves towards the patch: the first resonance moves up from about 1.6 GHz to "
        "2.7 GHz and becomes much deeper, and the matching between 3 and 10 GHz improves. For most ground positions "
        "|S_{11}| stays between about −3 dB and −10 dB over large parts of 3–10 GHz; only L_{g} = −7 mm keeps it below "
        "−10 dB across the whole band, so this value was fixed.")
    c.fig(["cst_single_Lg_sweep.png"], "|S_{11}| for different ground-edge positions L_{g} (R = 15 mm); best: "
          "L_{g} = −7 mm.", width=5.2)
    c.p(f"Fig. {n_r} shows the radius sweep, {R_VALUES}, with L_{{g}} = −7 mm. Small patches resonate too high and "
        "leave much of the band poorly matched; enlarging the patch lowers the first resonance and brings the "
        "higher-order resonances together, and R = 15 mm gives the widest continuous −10 dB band of all radii "
        "simulated. Both selected values lie at the upper end of their sweep ranges, which were limited by the board "
        "size.")
    c.fig(["cst_single_R_sweep.png"], "|S_{11}| for different patch radii R (L_{g} = −7 mm); best: R = 15 mm.",
          width=5.2)
    c.p("Some sweep curves show abrupt steps at about 4.0 GHz and 6.2 GHz, and one curve of the ground sweep rises "
        "above 0 dB between these frequencies. A passive antenna cannot reflect more power than it receives "
        "(|S_{11}| ≤ 0 dB), so these are numerical artefacts of the broadband frequency sweep for those parameter "
        "values, not physical behaviour. They do not affect the selected design, whose final response (Fig. "
        f"{c.next_fig()}) is smooth; the affected points will be re-simulated with denser frequency sampling.")

    c.h2("Optimised Antenna")
    n_s, n_g = c.next_fig(), c.next_fig() + 1
    fbw = lit.fractional_bw(lo, hi) * 100
    res = ", ".join(f"{f:.2f} GHz ({d:.1f} dB)" for f, d in tw["resonances"])
    c.p(f"Fig. {n_s} shows the response of the optimised antenna (L_{{g}} = −7 mm, R = 15 mm). |S_{{11}}| stays below "
        f"−10 dB from {lo:.2f} GHz to {hi:.2f} GHz, a fractional bandwidth of {fbw:.1f} % from ({2}), which covers the "
        f"entire UWB band with margin at both ends. Four resonances, at {res}, overlap to form the band. The weakest "
        "points are near 6.5 GHz and 12.2 GHz, where |S_{11}| is only about −10.3 dB and −10.5 dB; these points "
        "will be watched when the metasurface is added.")
    c.fig(["cst_single_final_s11_markers.png", "cst_single_final_s11_bandwidth.png"],
          "|S_{11}| of the optimised antenna: (top) resonance markers, (bottom) −10 dB band edges at "
          f"{lo:.4f} GHz and {hi:.3f} GHz.", width=4.8)
    c.p(f"Fig. {n_g} shows the simulated IEEE gain. It rises from about 1 dBi at 2 GHz to 3.3 dBi near 3.6 GHz, stays "
        f"between about 2.9 and 4.9 dBi across 3.1–10.6 GHz (lowest near 6.3 GHz, highest near 8.5 GHz) and peaks at "
        f"{tw['gain_ieee_peak']} (values read from the plot). These values are typical of a printed monopole that "
        "radiates on both sides of the board, and they are the baseline the metasurface has to improve. Realized gain "
        "and radiation patterns will be added with the metasurface results.")
    c.fig(["cst_single_final_gain_ieee.png"], "Simulated IEEE gain of the optimised antenna versus frequency.",
          width=4.8)
    c.table("Simulated performance of the optimised antenna (no metasurface).", ["Quantity", "Value"], [
        ["−10 dB band", f"{lo:.2f}–{hi:.2f} GHz"],
        ["Fractional bandwidth", f"{fbw:.1f} %"],
        ["Resonances", ", ".join(f"{f:.2f}" for f, _ in tw["resonances"]) + " GHz"],
        ["Deepest |S_{11}|", f"{min(d for _, d in tw['resonances']):.2f} dB at {tw['resonances'][0][0]:.2f} GHz"],
        ["IEEE gain, 3.1–10.6 GHz", f"{tw['gain_ieee_uwb']} dBi (read from plot)"],
        ["Peak IEEE gain", tw["gain_ieee_peak"]],
    ], [2.6, 3.4], size=10)

    c.h2("Metasurface Unit Cell")
    c.p("The single-SRR unit cell is being simulated with unit-cell boundaries and a Floquet port to obtain its "
        "reflection phase, which will be compared with the window of Fig. 3. "
        f"Cell: {mm(SRR['cell'])}; period: {mm(SRR['period'])}; array: {mm(SRR['array'])}; "
        f"substrate: {mm(SRR['substrate'])}.")
    c.fig(UNITCELL_FIGS, "SRR unit cell: geometry and simulated reflection phase.",
          pending="SRR unit cell geometry and reflection phase (Floquet port)")

    c.h2("Antenna with the Metasurface")
    c.p(f"The antenna with the SRR metasurface {lit.GAP_MM} mm behind it is being simulated with the same mesh and "
        "monitors as the antenna alone, together with a plain metal plate at the same gap as a baseline.")
    c.fig(MS_FIGS, "|S_{11}| and gain of the antenna without and with the SRR metasurface.",
          pending="S11 and gain: no reflector / metal plate / SRR metasurface")

    c.h2("Challenges")
    dh.bullets(c.doc, [
        "**Simulation time.** Each full-band run takes a long time on the available PC, so sweeps use coarser "
        "settings and the final design is re-run on its own.",
        "**Sweep artefacts.** Non-physical steps (and one curve above 0 dB) in the broadband frequency sweeps; the "
        "affected points will be re-run with denser frequency sampling.",
        "**Sweep limits.** The selected L_{g} and R lie at the edge of their ranges, which the board size bounds.",
        "**Marginal matching.** |S_{11}| is only about 0.3–0.5 dB below the −10 dB line near 6.5 and 12.2 GHz; the "
        "metasurface may detune these points.",
        "**Metasurface bandwidth.** The antenna covers a 7:1 band, while a single SRR resonance is in phase over a "
        "much narrower range, so the metasurface is expected to raise the gain over part of the band only.",
    ], c.cite)


TIMELINE = [
    ("7–15 Oct", "Unit-cell reflection phase; antenna with metasurface; metal-plate baseline; realized gain and "
                 "patterns", "Phase I results"),
    ("16–31 Oct", "2-port, then 4-port layout on a shared ground; isolation study", "MIMO S-parameters"),
    ("1–15 Nov", "MIMO with metasurface; ECC, DG, TARC, CCL, MEG; patterns", "Full simulated MIMO results"),
    ("16–25 Nov", "Fabrication; measurement on a VNA and in an anechoic chamber", "Measured results"),
    ("26 Nov–early Dec", "Comparison of measurement and simulation; final report and presentation",
     "End-semester submission"),
]


def work_plan(c: Ctx) -> None:
    c.h2("Completing Phase I")
    dh.bullets(c.doc, [
        "Characterise the SRR unit cell (reflection phase and magnitude) and compare it with the in-phase window "
        f"at h = {lit.GAP_MM} mm.",
        "Simulate the antenna with the metasurface and with a metal plate at the same gap; compare |S_{11}|, "
        "realized gain, front-to-back ratio and radiation patterns at 4, 7 and 10 GHz.",
        "Re-tune L_{g} if the metasurface detunes the band, and re-run the sweep points that showed artefacts.",
    ], c.cite)
    c.h2("Phase II: MIMO Antenna with Metasurface")
    c.p("The optimised antenna becomes the MIMO element. Two and then four elements will be placed with 90° "
        "rotations, so that neighbouring elements are orthogonally polarised, on a shared CPW ground as in practical "
        "devices; the metasurface will extend under the whole board. The design will be judged by the standard MIMO "
        "metrics [@sharawi]: isolation between ports (target above 15 dB, aiming for 20 dB), envelope correlation "
        "coefficient (target below 0.01, from S-parameters and from far-field patterns), diversity gain (close to "
        "10 dB), total active reflection coefficient, channel capacity loss (below 0.4 bit/s/Hz) and mean effective "
        "gain. The team's Python post-processing scripts already compute all of these from CST Touchstone exports.")
    c.h2("Fabrication and Measurement")
    c.p("The antenna and the metasurface will be fabricated as separate printed boards and held "
        f"{lit.GAP_MM} mm apart with non-metallic spacers. S-parameters will be measured on a vector network analyser "
        "and radiation patterns and gain in an anechoic chamber, then compared with simulation.")
    c.h2("Timeline")
    c.table("Work plan from mid-October to the end-semester evaluation (early December).",
            ["Period", "Task", "Output"], [list(r) for r in TIMELINE], [1.25, 3.25, 1.5], size=10)


def outcomes(c: Ctx) -> None:
    dh.bullets(c.doc, [
        f"A low-profile CPW-fed UWB antenna (air gap {lit.GAP_MM} mm, about "
        f"{lit.GAP_MM / lit.wavelength_mm(3.1):.2f}λ_{{0}} at 3.1 GHz) whose SRR metasurface raises the forward gain "
        "and front-to-back ratio wherever its reflection phase meets the in-phase condition, while keeping the "
        "2.16–15.73 GHz impedance band.",
        "A fair comparison of no reflector, a metal plate and the SRR metasurface at the same gap.",
        "A 2-/4-port MIMO antenna with the metasurface, with isolation above 15 dB (target 20 dB) and ECC below 0.01 "
        "across the UWB band.",
        "A fabricated and measured prototype, and a draft paper.",
    ], c.cite)


SECTIONS = [
    ("Abstract", abstract),
    ("Introduction", introduction),
    ("Literature Review", literature_review),
    ("Methodology / Proposed Work", methodology),
    ("Work Done Till Mid-Semester", work_done),
    ("Work Plan for Next Phase", work_plan),
    ("Expected Outcomes", outcomes),
]


# ============================================================================= assembly
def _heading_par(doc, text: str) -> Paragraph:
    return next(p for p in doc.paragraphs if p.style.name == "Heading 1" and p.text.strip() == text)


def _fill(doc, c: Ctx, heading: str, builder) -> None:
    h = _heading_par(doc, heading)
    ph = Paragraph(h._p.getnext(), h._parent)       # the template's "Write content here..." line
    c.heads.append((1, heading))
    with dh.placed_after(doc, ph._p) as moved:
        builder(c)
    el = moved[-1].getnext() if moved else ph._p.getnext()
    while (el is not None and el.tag == qn("w:p") and not dh.el_text(el).strip()
           and not el.findall(".//" + qn("w:br"))):
        nxt = el.getnext()
        el.getparent().remove(el)
        el = nxt
    ph._p.getparent().remove(ph._p)


def _front_matter(doc, c: Ctx, anchor) -> None:
    with dh.placed_after(doc, anchor):
        for title, instr, entries in (
                ("Contents", 'TOC \\o "1-2" \\h \\z \\u',
                 [(lv, t, c.pages.get(f"h:{t}")) for lv, t in c.heads]),
                ("List of Figures", 'TOC \\h \\z \\c "Figure"',
                 [(1, f"Fig. {n}. {dh_plain(t)}", c.pages.get(f"f:{n}")) for n, t in c.figs]),
                ("List of Tables", 'TOC \\h \\z \\c "Table"',
                 [(1, f"Table {n}. {dh_plain(t)}", c.pages.get(f"t:{n}")) for n, t in c.tabs])):
            p = doc.add_paragraph(style="TOC Heading")
            dh.add_runs(p, title, 14)
            p.paragraph_format.page_break_before = title != "List of Tables"
            p.paragraph_format.space_after = dh.Pt(12)
            dh.toc_field(doc, instr, entries)


def dh_plain(text: str) -> str:
    """Caption text for the lists (citations removed, mini-markup kept)."""
    return re.sub(r"\s*\[@[^\]]+\]", "", text)


def build(pages: dict[str, int]) -> tuple[Path, Ctx]:
    pj = lit.PROJECT
    doc = dh.start("B. Tech. PROJECT REPORT (Mid-Semester Evaluation)", pj["title"], pj["phase1"],
                   [f"{n.upper()} ({r})" for n, r in pj["students"]],
                   [pj["supervisors"][0][0].upper()] + [f"{n.upper()} (CO-GUIDE)" for n, _ in pj["supervisors"][1:]],
                   keep_body=True)
    c = Ctx(doc, dh.Citer(lit.ref_text), pages)
    title_end = next(p for p in doc.paragraphs if p.text.startswith("NATIONAL INSTITUTE OF TECHNOLOGY SILCHAR"))
    for heading, builder in SECTIONS:
        _fill(doc, c, heading, builder)
    _heading_par(doc, "Abstract").paragraph_format.page_break_before = True
    refs = _heading_par(doc, "References")
    c.heads.append((1, "References"))
    with dh.placed_after(doc, refs._p):
        dh.references(doc, c.cite)
    for el in list(doc.element.body):  # the References placeholder (now after the list)
        if el.tag == qn("w:p") and dh.el_text(el).strip() == "Write content here...":
            el.getparent().remove(el)
    _front_matter(doc, c, title_end._p)
    dh.page_number_footer(doc)
    doc.core_properties.title = f"{pj['title']}: Mid-Semester Report"
    doc.core_properties.author = ", ".join(n for n, _ in pj["students"])
    doc.core_properties.last_modified_by = doc.core_properties.author
    doc.save(str(OUT))
    return OUT, c


# ============================================================================= page numbers via LibreOffice
def render_pdf(docx: Path) -> Path | None:
    soffice = shutil.which("soffice")
    if not soffice:
        return None
    tmp = Path(tempfile.mkdtemp(prefix="report_render_"))
    env = {**os.environ, "SAL_USE_VCLPLUGIN": "svp"}
    subprocess.run([soffice, f"-env:UserInstallation={(tmp / 'profile').as_uri()}", "--headless", "--convert-to",
                    "pdf", "--outdir", str(tmp), str(docx)], capture_output=True, timeout=300, env=env)
    pdf = tmp / f"{docx.stem}.pdf"
    return pdf if pdf.exists() else None


def page_map(pdf: Path, c: Ctx) -> dict[str, int]:
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                                                          text=True).stdout).group(1))
    pages = [[ln.strip() for ln in subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), str(pdf), "-"],
                                                  capture_output=True, text=True).stdout.splitlines()]
             for i in range(1, n + 1)]
    start = next(i for i, lines in enumerate(pages) if "Abstract" in lines)
    out: dict[str, int] = {}
    k = start
    for _, text in c.heads:
        plain = re.sub(r"[_^]\{([^}]*)\}", r"\1", text)
        for i in range(k, n):
            if plain in pages[i]:
                out[f"h:{text}"], k = i + 1, i
                break
    for prefix, label, items in (("f", "Fig.", c.figs), ("t", "Table", c.tabs)):
        for num, _ in items:
            tag = f"{label} {num}."
            hit = next((i for i in range(start, n) if any(ln.startswith(tag) for ln in pages[i])), None)
            if hit is not None:
                out[f"{prefix}:{num}"] = hit + 1
    return out


if __name__ == "__main__":
    pages: dict[str, int] = {}
    out, c = build(pages)
    for attempt in range(3):
        pdf = render_pdf(out)
        if pdf is None:
            print("LibreOffice not found: lists keep placeholder entries; update them in Word (Ctrl+A, F9).")
            break
        new = page_map(pdf, c)
        if new == pages:
            break
        pages = new
        out, c = build(pages)
    print(f"Wrote {out.relative_to(ROOT)}  ({c.fig_n} figures, {c.tab_n} tables, {c.eq_n} equations)")
    missing = [n for n in [GEOMETRY, *UNITCELL_FIGS, *MS_FIGS] if not have(n)]
    if missing:
        print("Pending figures:", ", ".join(missing))
    if any(v is None for _, _, v in DIMENSIONS) or SUBSTRATE is None:
        print("Pending: antenna dimensions / substrate (CST parameter list)")
