# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pillow>=10"]
# ///
"""Build the mid-semester report strictly adhering to the college template.

The report must be exactly 7 pages, structured as:
  Page 1: Title page (template format: NIT Silchar, students, guide/co-guide)
  Page 2: Abstract & Introduction (Fig. 1: proposed structure, side view + metasurface top view)
  Page 3: Literature Review (narrative, Table 1, Research Gap)
  Page 4: Methodology / Proposed Work, subsections 1-4 (workflow, setup, initial antenna, sweep text; Figs. 2-3)
  Page 5: Methodology cont. (Fig. 4 sweeps; subsections 5-7: optimised antenna, metasurface, antenna +
          metasurface; Figs. 5-6)
  Page 6: Work Done Till Mid-Semester (Table 2, challenges) & Work Plan for Next Phase
  Page 7: Expected Outcomes & References

Writing rules for this checkpoint: plain English and short sentences; "wideband", never "UWB"; no equations and no
wavelength fractions; no gain numbers (gain plots are still pending). Only CST results that exist are reported.
Re-check the page count after any change to text or figure widths.
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
from docx.shared import Pt
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "figures"
OUT = ROOT / "report" / "MidSem_Report.docx"


GAP = lit.GAP_MM  # air gap between the antenna and the metasurface, mm
FIG_IDEA = 1  # stack-up sketch + metasurface top view: the first figure (Introduction)

# Build-time crops (left, top, right, bottom) in source pixels; the PNGs in figures/ are not modified.
# CST 1D plots are 2288 × 959 px: every crop drops the plot title (rows 42–56). The sweep plots also drop the
# legend right of the frame (the caption names the highlighted curve); the single-curve plots drop the one-entry
# "S1,1" legend.
CROP_S11_BASELINE = (8, 64, 2266, 950)    # its legend sits inside the frame
CROP_LG_BEST = (8, 64, 2080, 950)         # frame ends at x = 2067, legend starts at 2083
CROP_R_BEST = (8, 64, 2090, 950)          # frame ends at x = 2078, legend starts at 2094
CROP_S11_SINGLE = (8, 64, 2180, 950)      # frame ends at x = 2168, legend starts at 2185
CROP_S11_BANDWIDTH = (8, 64, 2177, 959)   # keeps the band-edge marker labels at the bottom edge
CROP_INITIAL_ANTENNA = (0, 44, 955, 954)  # white strip above the patch
CROP_FLOW = (14, 15, 1440, 580)           # white margins
CROP_STACKUP = (25, 37, 1380, 645)        # white margins


_UNIT = re.compile(r"(\d) (GHz|dBic|dBi|dB|mm|Ω)(?![\w])")


def nb(text: str) -> str:
    """Keep a number and its unit, and "L_g = −7", on the same line (no-break spaces)."""
    return _UNIT.sub("\\1\u00a0\\2", text).replace(" = ", "\u00a0=\u00a0")


def have(name: str) -> bool:
    return (FIGS / name).exists()


@dataclass
class Ctx:
    doc: object
    cite: dh.Citer
    fig_n: int = 0
    tab_n: int = 0
    heads: list[tuple[int, str]] = field(default_factory=list)
    figs: list[tuple[int, str]] = field(default_factory=list)
    tabs: list[tuple[int, str]] = field(default_factory=list)

    def p(self, text: str, **kw) -> Paragraph:
        return dh.para(self.doc, nb(text), self.cite, **kw)

    def h2(self, text: str, page_break: bool = False) -> None:
        self.heads.append((2, text))
        dh.heading(self.doc, text, level=2, page_break=page_break)

    def bullets(self, items: list[str]) -> None:
        dh.bullets(self.doc, [nb(t) for t in items], self.cite)

    def next_fig(self) -> int:
        return self.fig_n + 1

    def next_tab(self) -> int:
        return self.tab_n + 1

    def fig(self, names: list[str], caption: str, width: float = 4.6, crop: dh.Crop | None = None) -> int:
        self.fig_n += 1
        for name in names:
            if have(name):
                dh.image(self.doc, FIGS / name, width, crop)
        dh.seq_caption(self.doc, "Fig.", self.fig_n, nb(caption), self.cite)
        self.figs.append((self.fig_n, caption))
        return self.fig_n

    def fig_two(self, name1: str, name2: str, caption: str, width1: float = 2.85,
                width2: float | None = None, width: float | None = None,
                subcap1: str = "(a)", subcap2: str = "(b)",
                crop1: dh.Crop | None = None, crop2: dh.Crop | None = None) -> int:
        self.fig_n += 1
        dh.two_images(self.doc, FIGS / name1, FIGS / name2, width1=width1, width2=width2, width=width,
                      subcap1=subcap1, subcap2=subcap2, crop1=crop1, crop2=crop2)
        dh.seq_caption(self.doc, "Fig.", self.fig_n, nb(caption), self.cite)
        self.figs.append((self.fig_n, caption))
        return self.fig_n

    def table(self, caption: str, header: list[str], rows: list[list[str]], widths: list[float], **kw) -> int:
        self.tab_n += 1
        dh.seq_caption(self.doc, "Table", self.tab_n, caption, self.cite, above=True)
        dh.table(self.doc, header, [[nb(v) for v in r] for r in rows], widths, cite=self.cite, **kw)
        self.tabs.append((self.tab_n, caption))
        return self.tab_n


# ============================================================================= Section Builders
def abstract(c: Ctx) -> None:
    c.p("Fast wireless links need wideband antennas, and multiple-input multiple-output (MIMO) systems need several "
        "of them. A printed monopole gives a wide band but low gain, because it radiates to both sides of the "
        "board. A metal plate behind it raises the gain only when placed far away, which makes the antenna thick. "
        "This project places a thin metasurface close behind the antenna instead. This report covers Phase I. "
        "A coplanar waveguide (CPW) fed decagonal monopole was designed on a 50 × 50 × 1.6 mm FR-4 board in CST "
        "Studio Suite 2019. Moving the ground closer to the patch and using a 15 mm patch radius gave S_{11} below "
        f"−10 dB from 2.16 to 15.73 GHz. A 6 × 5 split-ring metasurface was placed {GAP} mm behind the antenna. "
        "The match holds over most of the band, but three narrow mismatch gaps appear between 3.0 and 5.6 GHz. Gain "
        "plots, metasurface tuning and a MIMO version are the next steps.")


def introduction(c: Ctx) -> None:
    c.h2("Background and Motivation")
    c.p("Modern wireless systems need antennas that work over a wide range of frequencies. MIMO systems use several "
        "antennas at each end of the link to carry more data without more transmit power [@foschini, telatar]. A "
        "compact wideband antenna that can later be repeated in a MIMO layout is therefore useful [@sharawi].")
    c.p("Printed monopole antennas are a common choice for wideband use. A flat disc or polygon patch has several "
        "close resonances that join into one wide band [@agrawall, ray]. A CPW feed puts the feed line and the ground "
        "on the same side of the board, so no vias are needed [@simons]. The weak point of such an antenna is its "
        "gain. It radiates almost equally to the front and to the back, so much of the power is lost behind it "
        "[@balanis].")
    c.p("A metal plate behind the antenna can turn the backward wave forward. However, a plain metal plate helps only "
        "when it is far from the antenna, so the antenna becomes thick. A metasurface is a thin board covered with "
        "many small, repeated metal cells that shape the reflected wave [@holloway]. Because of this, it can sit much "
        "closer to the antenna. The split ring is a widely used metasurface cell [@pendry]. Fig. "
        f"{c.next_fig()} shows the structure proposed in this project.")
    assert c.next_fig() == FIG_IDEA
    c.fig_two("fig_stackup.png", "cst_metasurface_top.png",
              f"Proposed structure: (a) side view of the antenna, the {GAP} mm air gap and the metasurface (schematic, "
              "not to scale), and (b) CST model of the 6 × 5 double split-ring metasurface, top view.",
              width1=3.0, width2=1.5, crop1=CROP_STACKUP)
    c.h2("Problem Statement and Objectives")
    c.p("A printed monopole gives a wide band but low gain, and a metal reflector would make it thick. This project "
        "aims to build a thin wideband antenna with higher gain, and later a MIMO version of it. The objectives are:")
    c.bullets([
        "To design a CPW-fed wideband monopole antenna that covers about 2.2–15 GHz.",
        "To optimise the ground position and the patch size for the best impedance match.",
        f"To add a split-ring metasurface {GAP} mm behind the antenna to raise its gain.",
        "To extend the design to a MIMO antenna, then fabricate and measure it (Phase II).",
    ])


def literature_review(c: Ctx) -> None:
    n_tab = c.next_tab()
    c.p("Several groups have placed a reflector behind a wideband printed antenna to raise its gain. Table "
        f"{n_tab} lists the works closest to this project.")
    c.p("Sen et al. [@sen2017] placed a metasurface of double split rings behind a circular monopole. The split "
        "angle changes from column to column, and the gain rose by about 5.5 dB. Al-Gburi et al. [@algburi2022] "
        "placed a CPW-fed ring monopole over a 19 × 19 loop frequency selective surface (FSS) with a ground plane. "
        "The peak gain rose from 6.7 to 11.5 dBi, and the whole structure is 10 mm thick. Hussain et al. [@hussain2023] "
        "put a 5 × 5 FSS 9 mm behind a CPW-fed hexagonal patch, and the peak gain rose from 6.5 to 10.5 dBi. "
        "Hammache et al. [@hammache2024] used a 7 × 7 FSS 20 mm behind a CPW-fed hexagonal monopole, and the gain "
        "rose from 2.2 to 8.4 dBi.")
    c.p("Metasurfaces are also used in MIMO antennas. Hasan et al. [@hasan2022] placed a copper-backed 10 × 10 "
        "split-ring metasurface 12 mm behind a 4-port antenna for 3.08–7.75 GHz. The gain rose from 5.4 to 8.3 dBi, "
        "and the isolation between ports stayed above 15.5 dB. Wu et al. [@wu2023] used a polarization-conversion "
        "metasurface in a 2-port antenna for 4.76–6.77 GHz, with a gain of 7.95 dBic and isolation above 19.8 dB.")
    c.p("These works show that a reflector or metasurface can raise the gain of a printed antenna by several dB. "
        "In most of them, however, the reflector sits far behind the antenna. From them, this project takes three "
        "ideas: a CPW-fed monopole as the radiator [@algburi2022, hussain2023, hammache2024], split-ring cells for "
        "the metasurface [@sen2017, hasan2022], and a copper-backed metasurface behind a MIMO antenna for Phase II "
        "[@hasan2022].")
    c.table("Printed antennas with a reflector or metasurface behind them, compared with this work. "
            "Gain is the peak gain without → with the reflector.",
            ["Reference", "Antenna", "Reflector", "Gap", "Peak gain"],
            [
                ["Sen et al. (2017) [@sen2017]", "Circular monopole",
                 "Double split-ring metasurface (graded splits)", "Not given in abstract", "About +5.5 dB"],
                ["Al-Gburi et al. (2022) [@algburi2022]", "CPW-fed ring monopole",
                 "19 × 19 loop FSS with ground plane", "10 mm (total height)", "6.7 → 11.5 dBi"],
                ["Hussain et al. (2023) [@hussain2023]", "CPW-fed hexagonal patch",
                 "5 × 5 ring-frame FSS", "9 mm", "6.5 → 10.5 dBi"],
                ["Hammache et al. (2024) [@hammache2024]", "CPW-fed hexagonal monopole",
                 "7 × 7 FSS", "20 mm", "2.2 → 8.4 dBi"],
                ["Hasan et al. (2022) [@hasan2022]", "4-port MIMO patch (3.08–7.75 GHz)",
                 "10 × 10 copper-backed split-ring metasurface", "12 mm",
                 "5.4 → 8.3 dBi; isolation > 15.5 dB"],
                ["**This work**", "CPW-fed decagonal monopole",
                 "6 × 5 double split-ring metasurface, copper-backed", f"**{GAP} mm**", "Under simulation"],
            ],
            [1.25, 1.2, 1.55, 0.8, 1.2], size=9.0, highlight_last=True)
    c.h2("Research Gap")
    c.p("In the reviewed works, the reflector usually sits 9–20 mm behind the antenna [@algburi2022, hussain2023, "
        "hammache2024, hasan2022]. This makes the antenna thick. A much thinner metasurface, only a few millimetres behind the "
        "antenna, working over a band as wide as about 2–15 GHz, is rarely reported. The reviewed metasurface MIMO "
        "antennas also cover narrower bands [@hasan2022, wu2023]. This project therefore aims to place a split-ring "
        f"metasurface only {GAP} mm behind a wideband antenna, and then to build a MIMO version of it.")


def methodology(c: Ctx) -> None:
    lo, hi = lit.THIS_WORK["band_ghz"]

    c.h2("1. Design Workflow")
    n = c.next_fig()
    c.p(f"Fig. {n} shows the design steps. Steps 1–6 are done, step 7 remains, and step 8 is Phase II.")
    c.fig(["fig_design_flow.png"], "Design workflow (dark: done; light: remaining in Phase I; dashed: Phase II).",
          width=4.4, crop=CROP_FLOW)

    c.h2("2. Simulation Setup")
    c.p("All simulations use CST Studio Suite 2019 (frequency-domain solver, 0–18 GHz). The antenna is printed in "
        "copper on a 50 × 50 × 1.6 mm FR-4 board. The radiator is a decagonal (10-sided) patch of circumradius R, "
        "with its centre fixed at 8 mm on the feed axis. The CPW feed has a 3.0 mm signal strip and 0.5 mm slots, "
        "and a waveguide port referenced to 50 Ω excites it. L_{g} is the position of the ground edge: −20 mm puts "
        "the ground far from the patch, and −7 mm brings it close.")

    c.h2("3. Initial Antenna")
    n = c.next_fig()
    c.p(f"The first design used R = 15 mm and L_{{g}} = −20 mm (Fig. {n}(a)), which leaves a 13.73 mm gap between "
        f"the ground and the patch. Its match is poor (Fig. {n}(b)): from 2 to 7.7 GHz, S_{{11}} stays between about "
        "−2.3 and −7.5 dB. Above 7.7 GHz there are only a few narrow dips below −10 dB, the deepest about −45 dB "
        "at 8.56 GHz.")
    c.fig_two("cst_initial_antenna.png", "cst_initial_ground_s11.png",
              "Initial antenna (R = 15 mm, L_{g} = −20 mm): (a) CST model and (b) simulated S_{11}.",
              width1=1.5, width2=3.85, crop1=CROP_INITIAL_ANTENNA, crop2=CROP_S11_BASELINE)

    c.h2("4. Ground Position and Patch Size Sweeps")
    n = c.next_fig()
    c.p(f"First, L_{{g}} was swept from −20 to −7 mm in 10 values, with R = 15 mm (Fig. {n}(a)). Moving the ground "
        "closer to the patch strengthens their coupling and improves the low-frequency match. Only L_{g} = −7 mm "
        "keeps S_{11} below −10 dB across the band, so it was chosen; the feed gap is then about 0.73 mm.")
    c.p(f"Next, R was swept from 4 to 15 mm in 13 values, with L_{{g}} = −7 mm (Fig. {n}(b)). Every patch size gives "
        "a first dip near 2.3–2.7 GHz, but small patches leave much of 3–12 GHz poorly matched (−3 to −9 dB). Only "
        "R = 15 mm joins the resonances into one continuous band. Because the patch centre is fixed, a larger R also "
        "narrows the feed gap.")
    c.fig_two("cst_single_Lg_best.png", "cst_single_R_best.png",
              "S_{11} sweeps: (a) L_{g} from −20 to −7 mm (blue: −7 mm) and (b) R from 4 to 15 mm (brown: 15 mm); "
              "other values are grey. Jumps near 4.0 and 6.2 GHz in some grey curves are sampling artefacts.",
              width1=2.85, width2=2.85, crop1=CROP_LG_BEST, crop2=CROP_R_BEST)

    c.h2("5. Optimised Antenna")
    n = c.next_fig()
    c.p(f"The optimised antenna (R = 15 mm, L_{{g}} = −7 mm) is shown in Fig. {n}(a). Its S_{{11}} is below −10 dB "
        f"from {lo:.2f} to {hi:.2f} GHz, about 13.6 GHz of bandwidth (Fig. {n}(b)). It has resonances at 2.73, 4.78, "
        "9.23 and 14.32 GHz; the deepest is −32.65 dB at 2.73 GHz. The match is thin near 6.45 GHz (−10.3 dB) and "
        "12.2 GHz (−10.5 dB).")
    c.fig_two("cst_final_antenna.png", "cst_single_final_s11_bandwidth.png",
              f"Optimised antenna (R = 15 mm, L_{{g}} = −7 mm): (a) CST model, front view, and (b) simulated S_{{11}} "
              f"with markers at the −10 dB band edges ({lo:.2f} and {hi:.2f} GHz).",
              width1=1.45, width2=3.75, crop2=CROP_S11_BANDWIDTH)

    c.h2("6. Metasurface Design")
    c.p(f"The metasurface is a 6 × 5 array of double split-ring cells, each with two concentric split rings, printed "
        f"on FR-4 with full copper on the back (Fig. {FIG_IDEA}(b)). It is placed {GAP} mm behind the antenna across "
        f"an air gap (Fig. {FIG_IDEA}(a)). The reflection phase of a single cell has not been simulated yet.")

    c.h2("7. Antenna with Metasurface")
    n = c.next_fig()
    c.p("With the metasurface, S_{11} is below −10 dB from about 2.0 GHz up to 18 GHz, the end of the simulation, "
        "except in three narrow gaps: 3.0–3.4 GHz (worst −6.6 dB near 3.14 GHz), 4.5–4.7 GHz (worst −9.7 dB) and "
        f"5.1–5.6 GHz (worst −8.8 dB near 5.34 GHz) (Fig. {n}). At such a small gap, the metasurface loads the "
        "antenna and changes its input match. The gap, ring size and ground position will be tuned to remove these "
        "gaps. The effect on gain is not yet known.")
    c.fig_two("cst_single_final_s11.png", "cst_single_ms_s11.png",
              f"Simulated S_{{11}}: (a) antenna alone and (b) antenna with the metasurface {GAP} mm behind it.",
              width1=2.85, width2=2.85, crop1=CROP_S11_SINGLE, crop2=CROP_S11_SINGLE,
              subcap1="(a) Antenna alone", subcap2="(b) Antenna + metasurface")


def work_done(c: Ctx) -> None:
    n_tab = c.next_tab()
    c.p("In Phase I so far, the single antenna was designed and optimised in CST, and the split-ring metasurface "
        f"was designed and simulated together with the antenna. Table {n_tab} gives the status of each Phase I task "
        "and its main result.")
    c.table("Status of Phase I.",
            ["Task", "Status", "Main result"],
            [
                ["Initial antenna (R = 15 mm, L_{g} = −20 mm)", "Done", "Poor match from 2 to 7.7 GHz"],
                ["Ground position sweep (L_{g} from −20 to −7 mm)", "Done", "L_{g} = −7 mm chosen"],
                ["Patch size sweep (R from 4 to 15 mm)", "Done", "R = 15 mm chosen"],
                ["Optimised antenna, S_{11}", "Done", "Below −10 dB from 2.16 to 15.73 GHz"],
                ["Metasurface design (6 × 5 double split rings)", "Done", f"Placed {GAP} mm behind the antenna"],
                ["Antenna + metasurface, S_{11}", "Done",
                 "Below −10 dB from about 2.0 to 18 GHz, except 3.0–3.4, 4.5–4.7 and 5.1–5.6 GHz"],
                ["Gain vs frequency, antenna alone", "Remaining", "—"],
                ["Gain vs frequency, antenna + metasurface", "Remaining", "—"],
                ["Metasurface tuning to remove the mismatch gaps", "Remaining", "—"],
            ],
            [2.75, 0.75, 2.5], size=9.0)
    c.h2("Challenges")
    c.bullets([
        "**Long run times:** the parametric sweeps and the antenna + metasurface model take a long time to "
        "simulate.",
        "**Sweep artefacts:** some sweep curves show sudden jumps near 4.0 and 6.2 GHz, and one curve goes above "
        "0 dB, which is not physical. They come from too few frequency samples, not from the mesh. These sweeps "
        "will be re-run with more samples.",
        "**Thin match margin:** the optimised antenna is only just matched near 6.45 GHz (−10.3 dB) and 12.2 GHz "
        "(−10.5 dB), so small fabrication errors could push these points above −10 dB.",
        f"**Metasurface detuning:** at a {GAP} mm gap the metasurface changes the input match and opens three "
        "narrow mismatch gaps between 3.0 and 5.6 GHz.",
    ])


def work_plan(c: Ctx) -> None:
    c.p("The remaining Phase I work comes first:")
    c.bullets([
        "Plot gain vs frequency for the antenna alone.",
        "Plot gain vs frequency for the antenna with the metasurface, and compare the two plots.",
        "Tune the metasurface (gap and ring size) and the ground position to remove the three mismatch gaps, and "
        "re-run the sweeps with more frequency samples.",
    ])
    c.p("Phase II will then cover the MIMO antenna and the hardware:")
    c.bullets([
        "Build a 4-port MIMO antenna from four copies of the antenna, each rotated by 90°, backed by the metasurface.",
        "Check the isolation between ports and the envelope correlation coefficient (ECC).",
        "Fabricate the antenna and the metasurface on FR-4, and measure them with a vector network analyser (VNA) "
        "and in an anechoic chamber.",
    ])


def outcomes(c: Ctx) -> None:
    c.bullets([
        "A simulated CPW-fed wideband antenna covering about 2.2–15 GHz, with gain vs frequency plots with and "
        "without the metasurface.",
        f"A tuned split-ring metasurface close behind the antenna ({GAP} mm) that keeps the antenna matched across "
        "the band. How much it raises the gain will be known from the gain plots.",
        "A 4-port MIMO version of the antenna with the metasurface, checked for isolation and ECC.",
        "A fabricated prototype whose measured S-parameters and radiation patterns are compared with simulation.",
    ])


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
    doc = dh.start("B. Tech. PROJECT REPORT (Mid-Semester Evaluation)", pj["title"], lit.PROJECT["phase1"],
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

    # Page breaks that fix the 7-page layout (see the module docstring)
    for h, brk in (("Abstract", True), ("Introduction", False), ("Literature Review", True),
                   ("Methodology / Proposed Work", True), ("Work Done Till Mid-Semester", True),
                   ("Work Plan for Next Phase", False), ("Expected Outcomes", True), ("References", False)):
        _heading_par(doc, h).paragraph_format.page_break_before = brk

    for h in ("Abstract", "Literature Review", "Methodology / Proposed Work", "Work Done Till Mid-Semester",
              "Expected Outcomes"):
        _heading_par(doc, h).paragraph_format.space_before = Pt(0)
    for h in ("Introduction", "Work Plan for Next Phase", "References"):
        _heading_par(doc, h).paragraph_format.space_before = Pt(10)

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
