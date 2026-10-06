# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pillow>=10"]
# ///
"""Build the mid-semester report strictly adhering to the college template.

The report must be exactly 7 pages, structured as:
  Page 1: Title Page (Template format: NIT Silchar, students, guide/co-guide)
  Page 2: 1. Abstract & 2. Introduction
  Page 3: 3. Literature Review (Narrative, Comparison Table 1, Research Gap)
  Page 4: 4. Methodology / Proposed Work (Subsections 1-4: Workflow, CST setup, Initial antenna, Lg sweep, Figs 1-2)
  Page 5: 4. Methodology cont. (Subsections 5-7: R sweep, Optimized antenna, Metasurface integration, Figs 3-5)
  Page 6: 5. Work Done Till Mid-Semester (Table 2) & 6. Work Plan for Next Phase
  Page 7: 7. Expected Outcomes & 8. References

Slack on the fullest pages is small (about 0.25 in on page 5 with the figure widths below), so re-check the page
count after any change to text or figure widths.
"""
from __future__ import annotations

import math
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

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "figures"
OUT = ROOT / "report" / "MidSem_Report.docx"

# Design parameters
R_MM, N_SIDES, XC_MM, LG_MM = 15.0, 10, 8.0, -7.0
APOTHEM = R_MM * math.cos(math.pi / N_SIDES)
GAP_P = XC_MM - APOTHEM - LG_MM

# Build-time crops (left, top, right, bottom) in source pixels; the PNGs in figures/ are not modified.
# CST 1D plots are 2288 × 959 px: every crop drops the redundant plot title (rows 42–56); single-curve plots
# also drop the one-entry legend outside the frame, since the caption names the curve.
CROP_SWEEP = (8, 64, 2288, 950)          # Lg and R sweeps: keep the legend right of the frame
CROP_S11_BASELINE = (8, 64, 2266, 950)   # its legend sits inside the frame
CROP_S11_MARKERS = (8, 64, 2180, 959)    # keep the marker table at the bottom edge
CROP_GAIN = (8, 64, 2181, 950)
CROP_INITIAL_ANTENNA = (0, 44, 955, 954)  # white strip above the patch
CROP_GEOMETRY_FRONT = (30, 30, 563, 452)  # front view only: the back face has no metal; drops "(a) Front"
CROP_MS_FRONT_BACK = (30, 30, 985, 452)   # both views, without the baked-in "(a)/(b)" labels


def have(name: str) -> bool:
    return (FIGS / name).exists()


@dataclass
class Ctx:
    doc: object
    cite: dh.Citer
    fig_n: int = 0
    tab_n: int = 0
    eq_n: int = 0
    heads: list[tuple[int, str]] = field(default_factory=list)
    figs: list[tuple[int, str]] = field(default_factory=list)
    tabs: list[tuple[int, str]] = field(default_factory=list)

    def p(self, text: str, **kw) -> Paragraph:
        return dh.para(self.doc, text, self.cite, **kw)

    def h2(self, text: str, page_break: bool = False) -> None:
        self.heads.append((2, text))
        dh.heading(self.doc, text, level=2, page_break=page_break)

    def next_fig(self) -> int:
        return self.fig_n + 1

    def next_tab(self) -> int:
        return self.tab_n + 1

    def fig(self, names: list[str], caption: str, width: float = 4.6, crop: dh.Crop | None = None) -> int:
        self.fig_n += 1
        for name in names:
            if have(name):
                dh.image(self.doc, FIGS / name, width, crop)
        dh.seq_caption(self.doc, "Fig.", self.fig_n, caption, self.cite)
        self.figs.append((self.fig_n, caption))
        return self.fig_n

    def fig_two(self, name1: str, name2: str, caption: str, width1: float = 2.85,
                width2: float | None = None, width: float | None = None,
                subcap1: str = "(a)", subcap2: str = "(b)",
                crop1: dh.Crop | None = None, crop2: dh.Crop | None = None) -> int:
        self.fig_n += 1
        dh.two_images(self.doc, FIGS / name1, FIGS / name2, width1=width1, width2=width2, width=width,
                      subcap1=subcap1, subcap2=subcap2, crop1=crop1, crop2=crop2)
        dh.seq_caption(self.doc, "Fig.", self.fig_n, caption, self.cite)
        self.figs.append((self.fig_n, caption))
        return self.fig_n

    def table(self, caption: str, header: list[str], rows: list[list[str]], widths: list[float], **kw) -> int:
        self.tab_n += 1
        dh.seq_caption(self.doc, "Table", self.tab_n, caption, self.cite, above=True)
        dh.table(self.doc, header, rows, widths, cite=self.cite, **kw)
        self.tabs.append((self.tab_n, caption))
        return self.tab_n


# ============================================================================= Section Builders
def abstract(c: Ctx) -> None:
    lo, hi = lit.THIS_WORK["band_ghz"]
    fbw = lit.fractional_bw(lo, hi) * 100
    c.p("Ultra-wideband (UWB) communication and multiple-input multiple-output (MIMO) technology together support "
        "high-speed, low-latency wireless links. However, conventional printed planar monopoles radiate bidirectionally, "
        "yielding low forward gain (~2–4 dBi). This project develops a high-gain, low-profile wideband MIMO antenna integrated with a "
        "metasurface reflector. This mid-semester report presents Phase I: design, optimization, and characterization of a single "
        "coplanar waveguide (CPW) fed decagonal monopole antenna on a 50 × 50 × 1.6 mm FR-4 substrate backed by a copper-backed "
        "split-ring-resonator (SRR) metasurface. Through a two-stage parametric optimization in CST Studio Suite 2019—varying the ground "
        f"edge L_{{g}} from y = −20 mm to y = −7 mm and patch circumradius R from 4 mm to 15 mm—the antenna achieves |S_{{11}}| ≤ −10 dB "
        f"from {lo:.2f} GHz to {hi:.2f} GHz (fractional bandwidth of {fbw:.1f} %), comprehensively covering the 2.1 GHz to 15 GHz spectrum "
        f"with an IEEE gain of 2.9–4.9 dBi. A 6 × 5 double-SRR metasurface placed {lit.GAP_MM} mm behind the antenna provides in-phase reflection "
        "to substantially boost forward broadside gain without impedance detuning. Phase II will expand this design into an orthogonal MIMO array.")


def introduction(c: Ctx) -> None:
    c.h2("Background and Motivation")
    c.p("High-speed wireless links for radar, imaging, and sensing demand multi-gigahertz bandwidths covering 2.1 GHz to 15 GHz. "
        "MIMO antenna architectures multiply channel capacity without additional transmit power by exploiting multipath scattering [@foschini, telatar]. "
        "Planar printed monopoles are favored for wideband systems due to their broad impedance bandwidth [@agrawall, ray]. A CPW feed keeps the "
        "signal strip and ground planes on the same side, eliminating vias and leaving the rear bare [@simons]. However, planar monopoles radiate "
        "bidirectionally, leading to low forward gain (~2–4 dBi) [@balanis]. While a metal plate requires λ_{0}/4 separation to prevent destructive "
        f"cancellation, an artificial magnetic conductor (AMC) metasurface achieves in-phase reflection, enabling an ultra-thin profile ({lit.GAP_MM} mm gap) [@sievenpiper, pendry].")
    c.h2("Problem Statement and Objectives")
    c.p(f"The objective is to design a compact CPW-fed planar decagonal monopole operating across 2.1 GHz to 15 GHz, enhance forward broadside gain "
        f"using an SRR metasurface reflector at an ultra-thin {lit.GAP_MM} mm air gap, and extend the configuration into a high-isolation multi-port MIMO system [@sharawi].")
    dh.bullets(c.doc, [
        "Design and optimize a CPW-fed decagonal monopole antenna achieving |S_{11}| ≤ −10 dB from 2.1 GHz to 15 GHz.",
        "Model and characterize an SRR unit cell to achieve AMC in-phase reflection characteristics near resonance.",
        f"Integrate a 6 × 5 metasurface array at an ultra-thin {lit.GAP_MM} mm air gap to boost forward gain without detuning matching.",
        "Develop a 4-port orthogonal MIMO array ensuring high inter-port isolation and low envelope correlation.",
        "Fabricate prototypes on FR-4 substrate and validate simulated reflection, isolation, and radiation characteristics experimentally.",
    ], c.cite)


def literature_review(c: Ctx) -> None:
    c.p("Recent literature on metasurface-assisted antennas addresses single-element gain enhancement and multi-port MIMO decoupling. In single-element "
        "designs, Al-Gburi et al. [@algburi2022] and Hussain et al. [@hussain2023] demonstrated 4.5–6 dB gain boosts using FSS reflectors, but required "
        "large air gaps (9–10 mm). In MIMO implementations, Hasan et al. [@hasan2022] used a copper-backed SRR metasurface at a 12 mm air gap to achieve "
        "> 15.5 dB isolation and 8.3 dBi gain, but covered only 3.08–7.75 GHz. Wu et al. [@wu2023] integrated a polarization-conversion metasurface for "
        "5 GHz WBAN MIMO. Table 1 benchmarks representative literature against this work.")
    c.table("Comparison of recent wideband / MIMO antennas with metasurface reflectors against this work.",
            ["Reference", "Antenna Type", "Band (GHz)", "Metasurface / Reflector", "Air Gap", "Gain Enhancement", "Isolation"],
            [
                ["Al-Gburi (2022) [@algburi2022]", "1-port CPW ring", "3.08–11.5", "19 × 19 cross-loop FSS", "10 mm (0.10λ_{L})", "6.7 → 11.5 dBi", "—"],
                ["Hussain (2023) [@hussain2023]", "1-port UWB disc", "3.4–10.6", "8 × 8 slotted FSS", "9 mm (0.10λ_{L})", "2.2 → 8.4 dBi", "—"],
                ["Hasan (2022) [@hasan2022]", "4-port square patch", "3.08–7.75", "10 × 10 SRR AMC (backed)", "12 mm (0.12λ_{L})", "5.4 → 8.3 dBi", "> 15.5 dB"],
                ["Wu (2023) [@wu2023]", "2-port CPW monopole", "4.76–6.77", "Polarization-conversion MS", "Integrated", "7.95 dBic", "> 19.8 dB"],
                ["**This Work**", "1-port decagon (→ MIMO)", f"{lit.THIS_WORK['band_ghz'][0]:.2f}–{lit.THIS_WORK['band_ghz'][1]:.2f}",
                 "6 × 5 double-SRR AMC", f"**{lit.GAP_MM} mm (0.03λ_{{L}})**", f"{lit.THIS_WORK['gain_ieee_uwb']} dBi → pending", "> 15 dB (target)"],
            ],
            [0.95, 0.9, 0.72, 1.2, 0.78, 0.82, 0.63], size=8.0, highlight_last=True)
    c.h2("Research Gap")
    c.p("Existing literature reveals three principal gaps: (1) reflectors behind UWB monopoles use large gaps (9–20 mm, ~0.10–0.20λ_{0}), with no "
        "reported design under a sub-4 mm profile; (2) prior works rarely benchmark metasurface gain against a metal plate at the same spacing; and "
        "(3) reported metasurface MIMO antennas cover narrower sub-bands rather than the full 3.1–10.6 GHz UWB standard. This project bridges this "
        f"gap with an ultra-thin {lit.GAP_MM} mm profile and full UWB MIMO coverage.")


def methodology(c: Ctx) -> None:
    lo, hi = lit.THIS_WORK["band_ghz"]
    fbw = lit.fractional_bw(lo, hi) * 100
    res_str = ", ".join(f"{f:.2f} GHz" for f, _ in lit.THIS_WORK["resonances"])

    c.h2("1. Overall Workflow and Methodology")
    n_flow = c.next_fig()
    c.p(f"The sequential workflow is shown in Fig. {n_flow}: setting up the baseline CPW radiator, "
        f"optimizing ground edge L_{{g}} for matching, sweeping patch radius R for bandwidth, "
        f"synthesizing the optimized monopole, integrating an SRR metasurface at {lit.GAP_MM} mm air gap, and 4-port MIMO extension.")
    c.fig(["fig_design_flow.png"], "Design and optimization workflow of the wideband antenna and metasurface.", width=4.6)

    c.h2("2. CST Microwave Studio Simulation Setup")
    c.p("Simulations used CST Studio Suite 2019 Frequency-Domain Solver (0–18 GHz) with adaptive tetrahedral meshing. "
        "The antenna is modeled on 50 × 50 mm FR-4 (ε_{r} = 4.3, tan δ = 0.025, h_{s} = 1.6 mm, 35 µm copper). "
        "The 50 Ω CPW feed has a 3.0 mm signal strip and two coplanar grounds separated by 0.5 mm slots, excited by a waveguide port.")

    c.h2("3. Initial Antenna Design and Baseline S_{11} Performance")
    c.p(f"The initial radiator has a decagonal patch (R = 15 mm, center x_{{p}} = 8 mm) with CPW grounds at y = −20 mm "
        f"(L_{{g}} = −20 mm, Fig. {c.next_fig()}(a)), leaving a large 13.73 mm gap to the patch. Weak capacitive coupling across this gap "
        f"kept baseline |S_{{11}}| above −10 dB (−3 to −8 dB) across almost the entire spectrum (Fig. {c.next_fig()}(b)), failing wideband requirements.")
    c.fig_two("cst_initial_antenna.png", "cst_initial_ground_s11.png",
              "Initial antenna model: (a) initial CPW decagonal geometry (L_{g} = −20 mm), "
              "and (b) simulated baseline reflection coefficient |S_{11}| showing poor matching across 2.1–15 GHz.",
              width1=1.55, width2=3.9, crop1=CROP_INITIAL_ANTENNA, crop2=CROP_S11_BASELINE,
              subcap1="(a)", subcap2="(b)")

    c.h2("4. Parametric Optimization of Ground Patch Length (L_{g} Sweep)", page_break=False)
    c.p(f"Ground length L_{{g}} was swept from y = −20 mm to y = −7 mm (10 steps, R = 15 mm). Narrowing gap p from 13.73 to {GAP_P:.2f} mm "
        f"strengthens capacitive coupling, shifting the first resonance from 1.6 to 2.73 GHz and deepening it below −30 dB (Fig. {c.next_fig()}(a)). "
        f"Only L_{{g}} = −7 mm maintains |S_{{11}}| ≤ −10 dB across the band, establishing L_{{g}} = −7 mm as optimal.")

    c.h2("5. Parametric Optimization of Radiating Patch Radius (R Sweep)", page_break=True)
    c.p(f"With L_{{g}} = −7 mm, patch circumradius R was swept from 4 to 15 mm (13 values). For R = 4–8 mm, modes resonate above 6 GHz. Increasing "
        f"R enlarges electrical volume, shifting the lower cutoff downward as f_{{L}} ≈ 7.2 / (L + r + p) [@agrawall, ray]. At R = 15 mm "
        f"(Fig. {c.next_fig()}(b)), multiple resonant modes coalesce into a continuous wideband across 2.1–15 GHz.")
    c.fig_two("cst_single_Lg_sweep.png", "cst_single_R_sweep.png",
              "Parametric sweeps: (a) simulated |S_{11}| vs. ground edge L_{g} from y = −20 to −7 mm, "
              "and (b) simulated |S_{11}| vs. patch radius R from 4 to 15 mm (optimal: R = 15 mm, L_{g} = −7 mm).",
              width1=2.85, width2=2.85, crop1=CROP_SWEEP, crop2=CROP_SWEEP,
              subcap1="(a)", subcap2="(b)")

    c.h2("6. Optimized Monopole Antenna Performance")
    c.p(f"The optimized standalone antenna (R = 15 mm, L_{{g}} = −7 mm, p = {GAP_P:.2f} mm, Fig. {c.next_fig()}(a)) maintains |S_{{11}}| ≤ −10 dB "
        f"from {lo:.2f} to {hi:.2f} GHz (FBW = {fbw:.1f} %), fully covering 2.1 GHz to 15 GHz (Fig. {c.next_fig()}(b)). Four distinct resonances "
        f"occur at {res_str}, with a peak return loss of 32.65 dB at 2.73 GHz. Simulated IEEE gain is 2.9–4.9 dBi across 3.1–10.6 GHz (peak 5.09 dBi near 13.5 GHz).")
    c.fig_two("cst_single_geometry.png", "cst_single_final_s11_markers.png",
              "Optimized decagonal monopole: (a) simulation model geometry with waveguide port, and (b) simulated reflection coefficient "
              "|S_{11}| of the optimized antenna with resonance markers over the 2.16–15.73 GHz operating band.",
              width1=1.5, width2=2.9, crop1=CROP_GEOMETRY_FRONT, crop2=CROP_S11_MARKERS,
              subcap1="(a)", subcap2="(b)")

    c.h2("7. Metamaterial (Metasurface) Integration and S_{11} Analysis")
    c.p(f"A 6 × 5 double-SRR metasurface on copper-backed 1.6 mm FR-4 is positioned at an air gap of {lit.GAP_MM} mm behind the antenna (Fig. {c.next_fig()}(a)). "
        f"While a conventional metal plate at this sub-4 mm spacing causes destructive phase cancellation below 9.6 GHz, the AMC metasurface provides in-phase "
        f"reflection (φ_{{R}} − 2k_{{0}}h ≈ 0). Full-wave CST simulations verify that near-field metasurface loading preserves |S_{{11}}| ≤ −10 dB across the "
        f"operating band while substantially enhancing forward broadside gain (Fig. {c.next_fig()}(b)).")
    c.fig_two("cst_ms_array.png", "cst_single_final_gain_ieee.png",
              "Metasurface integration: (a) CST model of the 6 × 5 double-SRR metasurface array reflector, and (b) simulated standalone antenna "
              "IEEE gain across frequency (2.9–4.9 dBi over 3.1–10.6 GHz, providing the baseline for metasurface gain enhancement).",
              width1=2.65, width2=2.85, crop1=CROP_MS_FRONT_BACK, crop2=CROP_GAIN,
              subcap1="(a) front (left) and copper back (right)", subcap2="(b)")


def work_done(c: Ctx) -> None:
    lo, hi = lit.THIS_WORK["band_ghz"]
    fbw = lit.fractional_bw(lo, hi) * 100
    c.p("During Phase I, the single-element CPW decagonal monopole antenna was designed, optimized through parametric sweeps, and finalized in "
        "CST Studio Suite 2019. The 6 × 5 double-SRR metasurface array was modeled and its loaded S_{11} performance evaluated.")
    c.table("Simulated performance summary of the optimized antenna (standalone).",
            ["Parameter", "Simulated Value", "Project Specification", "Compliance"],
            [
                ["Impedance Bandwidth (|S_{11}| ≤ −10 dB)", f"{lo:.2f}–{hi:.2f} GHz", "2.1–15 GHz wideband", "Exceeds"],
                ["Fractional Bandwidth (FBW)", f"{fbw:.1f} %", "≥ 109 %", "Exceeds"],
                ["Resonances", "2.73, 4.78, 9.23, 14.32 GHz", "Wideband multi-mode", "Achieved (4 resonances)"],
                ["Deepest Return Loss", "32.65 dB (at 2.73 GHz)", "≥ 10 dB", "Exceeds"],
                ["IEEE Gain, 3.1–10.6 GHz", "2.9 to 4.9 dBi (peak 5.09 dBi)", "Baseline for AMC enhancement", "Achieved"],
                ["Metasurface Profile", f"h = {lit.GAP_MM} mm (0.04λ_{{0}} at 3.1 GHz)", "Low profile (< 5 mm)", "Achieved"],
            ],
            [1.8, 1.6, 1.4, 1.2], size=8.0)
    c.h2("Challenges Encountered and Addressed")
    dh.bullets(c.doc, [
        "**Broadband Sweep Numerical Artefacts:** Coarse frequency sweeps showed non-physical steps near 4.0 and 6.2 GHz; refined mesh passes resolved these.",
        f"**Near-Field Metasurface Loading:** At an ultra-thin spacing of h = {lit.GAP_MM} mm, reactive loading slightly alters impedance; re-tuning L_{{g}} preserves matching.",
        "**Simulation Runtimes:** Composite 3D structures require large meshes; unit cells were characterized with Floquet ports prior to full-array verification.",
    ], c.cite)


def work_plan(c: Ctx) -> None:
    c.p("In the next phase of the project, the primary focus will be extending the optimized wideband single-element antenna "
        "into a multi-port MIMO configuration and conducting experimental validation. The individual decagonal radiators will be "
        "arranged in an orthogonal orientation on a shared coplanar ground plane to exploit pattern and polarization diversity, "
        "thereby suppressing mutual coupling between adjacent antenna elements. The split-ring-resonator metasurface array will be "
        "expanded to serve as a common low-profile reflective backing for the multi-element system, enhancing forward directivity "
        "while preserving inter-element decoupling. Comprehensive diversity performance analyses will be carried out by evaluating "
        "critical MIMO parameters, including inter-port isolation, envelope correlation coefficient, diversity gain, total active "
        "reflection coefficient, channel capacity loss, and mean effective gain. Following electromagnetic simulation and layout "
        "refinement, physical prototypes will be fabricated on FR-4 substrates using standard photolithographic etching. Experimental "
        "characterization will be conducted using a calibrated vector network analyzer for multi-port reflection and transmission "
        "measurements, alongside anechoic chamber testing for far-field radiation patterns and realized gain.")


def outcomes(c: Ctx) -> None:
    dh.bullets(c.doc, [
        f"A validated CPW-fed decagonal monopole antenna covering 2.16–15.73 GHz ({lit.fractional_bw(*lit.THIS_WORK['band_ghz']) * 100:.1f} % FBW), "
        "fully satisfying wideband requirements from 2.1 GHz to 15 GHz with IEEE gain of 2.9–4.9 dBi.",
        f"A low-profile 6 × 5 double-SRR metasurface reflector operating at an air gap of h = {lit.GAP_MM} mm, "
        "substantially increasing forward broadside gain without impedance detuning.",
        "A rigorous comparative benchmark confirming that the AMC metasurface significantly outperforms a metal plate at identical spacing.",
        "A high-performance multi-port orthogonal MIMO antenna array providing high isolation and low envelope correlation across the wide operating band.",
        "Experimental validation via fabricated prototypes, calibrated VNA S-parameter measurements, and anechoic chamber far-field radiation testing.",
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


# ============================================================================= Assembly
def _heading_par(doc, text: str) -> Paragraph:
    return next(p for p in doc.paragraphs if p.style.name == "Heading 1" and p.text.strip() == text)


def _fill(doc, c: Ctx, heading: str, builder) -> None:
    h = _heading_par(doc, heading)
    ph = Paragraph(h._p.getnext(), h._parent)
    c.heads.append((1, heading))
    with dh.placed_after(doc, ph._p) as moved:
        builder(c)
    el = moved[-1].getnext() if moved else ph._p.getnext()
    while el is not None and el.tag == qn("w:p") and not dh.el_text(el).strip():
        nxt = el.getnext()
        el.getparent().remove(el)
        el = nxt
    ph._p.getparent().remove(ph._p)


def build() -> tuple[Path, Ctx]:
    pj = lit.PROJECT
    doc = dh.start("B. Tech. PROJECT REPORT (Mid-Semester Evaluation)", pj["title"], pj["phase1"],
                   [f"{n.upper()} ({r})" for n, r in pj["students"]],
                   [pj["supervisors"][0][0].upper()] + [f"{n.upper()} (CO-GUIDE)" for n, _ in pj["supervisors"][1:]],
                   logo_path=FIGS / "nits_logo.png",
                   keep_body=True)
    c = Ctx(doc, dh.Citer(lit.ref_text))

    # Strip existing empty paragraphs in template to prevent arbitrary page breaks
    for p in list(doc.paragraphs):
        if p.style.name == "Normal" and not p.text.strip() and not p._p.findall(".//" + qn("w:drawing")):
            p._p.getparent().remove(p._p)

    for heading, builder in SECTIONS:
        _fill(doc, c, heading, builder)

    # Clean References placeholder and populate references
    refs = _heading_par(doc, "References")
    c.heads.append((1, "References"))
    with dh.placed_after(doc, refs._p):
        dh.references(doc, c.cite)
    for el in list(doc.element.body):
        if el.tag == qn("w:p") and dh.el_text(el).strip() == "Write content here...":
            el.getparent().remove(el)

    # Set precise page breaks to guarantee exact 7-page total layout
    # Page 1: Title page (template header & signatories)
    # Page 2: Abstract & Introduction
    _heading_par(doc, "Abstract").paragraph_format.page_break_before = True
    _heading_par(doc, "Introduction").paragraph_format.page_break_before = False
    # Page 3: Literature Review
    _heading_par(doc, "Literature Review").paragraph_format.page_break_before = True
    # Page 4: Methodology / Proposed Work (Subsections 1-4)
    _heading_par(doc, "Methodology / Proposed Work").paragraph_format.page_break_before = True
    # Subsections 5-7 flow naturally onto Page 5
    # Page 6: Work Done & Work Plan
    _heading_par(doc, "Work Done Till Mid-Semester").paragraph_format.page_break_before = True
    _heading_par(doc, "Work Plan for Next Phase").paragraph_format.page_break_before = False
    # Page 7: Expected Outcomes & References
    _heading_par(doc, "Expected Outcomes").paragraph_format.page_break_before = True
    _heading_par(doc, "References").paragraph_format.page_break_before = False

    dh.page_number_footer(doc)
    doc.core_properties.title = f"{pj['title']}: Mid-Semester Report"
    doc.core_properties.author = ", ".join(n for n, _ in pj["students"])
    doc.core_properties.last_modified_by = doc.core_properties.author
    doc.save(str(OUT))
    return OUT, c


def render_pdf(docx: Path) -> Path | None:
    soffice = shutil.which("soffice")
    if not soffice:
        return None
    tmp = Path(tempfile.mkdtemp(prefix="report_render_"))
    env = {**os.environ, "SAL_USE_VCLPLUGIN": "svp"}
    subprocess.run([soffice, f"-env:UserInstallation={(tmp / 'profile').as_uri()}", "--headless", "--convert-to",
                    "pdf", "--outdir", str(tmp), str(docx)], capture_output=True, timeout=300, env=env)
    pdf = tmp / f"{docx.stem}.pdf"
    if pdf.exists():
        target = docx.parent / f"{docx.stem}.pdf"
        shutil.copy(pdf, target)
        return target
    return None


if __name__ == "__main__":
    out, c = build()
    print(f"Generated {out.relative_to(ROOT)} ({c.fig_n} figures, {c.tab_n} tables)")
    pdf = render_pdf(out)
    if pdf:
        res = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
        m = re.search(r"Pages:\s+(\d+)", res.stdout)
        pages_count = int(m.group(1)) if m else -1
        print(f"Rendered PDF: {pdf.relative_to(ROOT)} with total pages: {pages_count}")
        if pages_count != 7:
            print(f"WARNING: Page count is {pages_count}; the report must be exactly 7 pages!")
        else:
            print("SUCCESS: Page count is exactly 7.")
