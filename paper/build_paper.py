# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pillow>=10", "numpy>=1.26"]
# ///
"""Build the research paper: paper/Paper.docx and, with LibreOffice installed, paper/Paper.pdf.

Run from the repo root (figures first):
  uv run paper/make_paper_figures.py
  uv run paper/build_paper.py [--compare REF1.pdf REF2.pdf ...]

Layout follows the IEEE two-column conference template in Word, the format of S. Bhattacharya et al., AJEC 2025:
US Letter, Times New Roman, single-column title and author block, two-column body, figures and tables at column
width, numbered IEEE references.

Writing rules:
* The voice and section pattern follow Bhattacharya et al. (AJEC 2025); no sentence is copied from it. --compare
  checks 8-word overlaps with the given PDFs (needs pdftotext) and must report none.
* Every number comes from paper/design.py (CST S11, screenshot dimensions, analytical estimates), so text, tables
  and figures agree.
* «...» marks text shown with a yellow highlight: dimensions read off the screenshots that the team must confirm, and
  [xx] placeholders for CST results not exported yet (gain, patterns, antenna-alone S11). Nothing is claimed about
  gain until that data exists.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "report"))

import design as d  # noqa: E402
import docx_helpers as dh  # noqa: E402
import literature as lit  # noqa: E402
from build_report import render_pdf  # noqa: E402
from docx import Document  # noqa: E402
from docx.enum.section import WD_SECTION  # noqa: E402
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_TAB_ALIGNMENT  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402

OUT = HERE / "Paper.docx"
FONT = "Times New Roman"
COL_W = 3.5           # column width, in (7.25 in text block, 0.25 in gutter)
FIG_W = 3.4
BODY = 10
SMALL = 8
JUSTIFY, CENTER, LEFT = WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT
HL = re.compile(r"«([^»]*)»")
XX = "«[xx]»"

# ============================================================================= numbers from the design data
F, S, S11_SRC = d.s11_with_ms()
BANDS = d.bands(F, S)
B1, B2, B3 = BANDS[0], BANDS[1], BANDS[2]
DIPS = d.dips(F, S)
FMIN, SMIN = min(DIPS, key=lambda x: x[1])
GAP1 = d.peak_between(F, S, B1.hi, B2.lo)     # worst point between band I and band II
GAP2 = d.peak_between(F, S, B2.hi, B3.lo)
RAY = d.ray_lower_edge()
LC = d.patch_ms_lc()
RT = d.round_trip_deg(LC["f0"], d.v("h"))
PROFILE = d.v("h_{s}") + d.v("h") + d.v("t")
LAMBDA_LO = d.wavelength_mm(B1.lo)
COV = {lab: 100 * d.coverage(lo, hi, BANDS) for lab, lo, hi in d.SERVICES}


def num(x: float, nd: int = 2) -> str:
    s = f"{x:.{nd}f}"
    return s.replace("-", "−")


def val(symbol: str) -> str:
    """A dimension in mm, highlighted when it is an estimate from the screenshot."""
    dm = d.dim(symbol)
    s = f"{dm.value:g}"
    return f"«{s}»" if dm.est else s


def band_txt(b: d.Band) -> str:
    return f"{num(b.lo)}–{num(b.hi)} GHz" if not b.open_top else f"{num(b.lo)} GHz to beyond 15 GHz"


EST_ANY = any(x.est for x in d.ANTENNA + d.METASURFACE)
SIZE = f"{val('W_{s}')} mm × {val('L_{s}')} mm × {val('h_{s}')} mm"
BACK = "«with a full copper ground on its back»" if d.MS_COPPER_BACK_EST else "with a full copper ground on its back"

# ============================================================================= references (IEEE)
EXTRA_REFS = {
    "bhattacharya": "S. Bhattacharya, A. Chatterjee, P. P. Sarkar, and A. Swarnakar, “A javelin shaped UWB antenna "
                    "with notch band for remote sensing applications,” *Amer. J. Electron. Commun.*, vol. 5, no. 1, "
                    "pp. 58–61, Jan. 2025.",
    "rajalakshmi": "P. Rajalakshmi and N. Gunavathi, “Gain enhancement of cross shaped patch antenna for IEEE "
                   "802.11ax Wi-Fi applications,” *Prog. Electromagn. Res. Lett.*, vol. 80, pp. 91–99, 2018.",
    "song": "Y. Song, Y.-C. Jiao, G. Zhao, and F.-S. Zhang, “Multiband CPW-fed triangle-shaped monopole antenna for "
            "wireless applications,” *Prog. Electromagn. Res.*, vol. 70, pp. 329–336, 2007.",
    "ahmad": "S. Ahmad, U. Ijaz, S. Naseer, A. Ghaffar, M. A. Qasim, F. Abrar, N. O. Parchin, C. H. See, and "
             "R. Abd-Alhameed, “A jug-shaped CPW-fed ultra-wideband printed monopole antenna for wireless "
             "communications networks,” *Appl. Sci.*, vol. 12, no. 2, Art. no. 821, 2022.",
    "kumar_ellip": "O. P. Kumar, T. Ali, P. Kumar, P. Kumar, and J. Anguera, “An elliptical-shaped dual-band UWB "
                   "notch antenna for wireless applications,” *Appl. Sci.*, vol. 13, no. 3, Art. no. 1310, 2023.",
    "kundu_triple": "S. Kundu and A. Chatterjee, “Sharp triple-notched ultra wideband antenna with gain augmentation "
                    "using FSS for ground penetrating radar,” *Wireless Pers. Commun.*, vol. 117, no. 2, "
                    "pp. 1399–1418, 2021.",
    "kundu_leaf": "S. Kundu, A. Chatterjee, S. K. Jana, and S. K. Parui, “Gain enhancement of a printed leaf shaped "
                  "UWB antenna using dual FSS layers and experimental study for ground coupling GPR applications,” "
                  "*Microw. Opt. Technol. Lett.*, vol. 60, no. 6, pp. 1417–1423, 2018.",
    "chatterjee": "A. Chatterjee and S. K. Parui, “Frequency-dependent directive radiation of monopole-dielectric "
                  "resonator antenna using a conformal frequency selective surface,” *IEEE Trans. Antennas Propag.*, "
                  "vol. 65, no. 5, pp. 2233–2239, May 2017.",
    "kumar_ray": "G. Kumar and K. P. Ray, *Broadband Microstrip Antennas*. Norwood, MA, USA: Artech House, 2003.",
    "3gpp": "3rd Generation Partnership Project, “NR; Base Station (BS) radio transmission and reception,” 3GPP TS "
            "38.104.",
    "ieee80211": "*IEEE Standard for Information Technology—Telecommunications and Information Exchange Between "
                 "Systems—Local and Metropolitan Area Networks—Specific Requirements—Part 11: Wireless LAN Medium "
                 "Access Control (MAC) and Physical Layer (PHY) Specifications*, IEEE Std 802.11-2020, 2021.",
    "ieee521": "*IEEE Standard Letter Designations for Radar-Frequency Bands*, IEEE Std 521-2019, 2020.",
    "itu_rr": "International Telecommunication Union, *Radio Regulations*, Article 5: Frequency allocations. Geneva, "
              "Switzerland: ITU, 2020.",
}


def ref_lookup(key: str) -> str:
    return EXTRA_REFS[key] if key in EXTRA_REFS else lit.ref_text(key)


CITE = dh.Citer(ref_lookup)

# ============================================================================= low-level writers
def runs(p, text: str, size: float = BODY, bold: bool | None = None, italic: bool | None = None) -> None:
    """Mini-markup of docx_helpers plus «highlight»; [@key] citations are numbered on the way."""
    text = CITE.render(text)
    pos = 0
    pieces = []
    for m in HL.finditer(text):
        pieces += [(text[pos:m.start()], False), (m.group(1), True)]
        pos = m.end()
    pieces.append((text[pos:], False))
    for seg, hl in pieces:
        if not seg:
            continue
        n0 = len(p.runs)
        dh.add_runs(p, seg, size, bold, italic)
        if hl:
            for r in p.runs[n0:]:
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW


def fmt(p, align=JUSTIFY, before: float = 0, after: float = 0, indent: float | None = None, keep: bool = False):
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before, pf.space_after = Pt(before), Pt(after)
    pf.line_spacing = 1.0
    if indent is not None:
        pf.first_line_indent = Inches(indent)
    if keep:
        pf.keep_with_next = True
    return p


def para(doc, text: str, indent: float = 0.17, after: float = 0) -> None:
    runs(fmt(doc.add_paragraph(), indent=indent, after=after), text)


def h1(doc, numeral: str, text: str) -> None:
    p = fmt(doc.add_paragraph(), CENTER, before=8, after=4, keep=True)
    r = p.add_run(f"{numeral}. {text}")
    dh.style_run(r, BODY)
    r.font.small_caps = True


def h2(doc, letter: str, text: str) -> None:
    p = fmt(doc.add_paragraph(), LEFT, before=4, after=2, keep=True)
    runs(p, f"{letter}. {text}", BODY, italic=True)


def figure(doc, name: str, n: int, caption: str, width: float = FIG_W) -> None:
    doc.add_picture(str(d.FIGS / name), width=Inches(width))
    fmt(doc.paragraphs[-1], CENTER, before=4, keep=True)
    p = fmt(doc.add_paragraph(), JUSTIFY, before=2, after=6)
    runs(p, f"Fig. {n}. " + caption, SMALL)


ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]


def table(doc, n: int, title: str, rows: list[list[str]], widths: list[float], header_rows: tuple[int, ...] = (0,),
          header_col: bool = False) -> None:
    assert sum(widths) <= COL_W + 1e-6, f"table {n} wider than the column"
    p = fmt(doc.add_paragraph(), CENTER, before=6, after=0, keep=True)
    r = p.add_run(f"TABLE {ROMAN[n - 1]}")
    dh.style_run(r, SMALL)
    p = fmt(doc.add_paragraph(), CENTER, after=3, keep=True)
    r = p.add_run(title)
    dh.style_run(r, SMALL)
    r.font.small_caps = True
    t = doc.add_table(rows=len(rows), cols=len(widths))
    t.style = doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for j, w in enumerate(widths):
        t.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        for j, text in enumerate(row):
            c = t.cell(i, j)
            c.width = Inches(widths[j])
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp = fmt(c.paragraphs[0], CENTER if j or not header_col else LEFT)
            bold = True if (i in header_rows or (header_col and j == 0)) else None
            runs(cp, text, SMALL, bold=bold)
            if i < len(rows) - 1:          # keep the table in one piece (no split across columns or pages)
                for cpar in c.paragraphs:
                    cpar.paragraph_format.keep_with_next = True
        trpr = t.rows[i]._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
    fmt(doc.add_paragraph(), after=4)


def equation(doc, nodes: list, n: int) -> None:
    p = fmt(doc.add_paragraph(), LEFT, before=3, after=3)
    pf = p.paragraph_format
    pf.tab_stops.add_tab_stop(Inches(COL_W / 2), WD_TAB_ALIGNMENT.CENTER)
    pf.tab_stops.add_tab_stop(Inches(COL_W), WD_TAB_ALIGNMENT.RIGHT)
    dh.style_run(p.add_run("\t"), BODY)
    om = OxmlElement("m:oMath")
    for nd in nodes:
        om.append(nd)
    p._p.append(om)
    dh.style_run(p.add_run(f"\t({n})"), BODY)


# math shorthands
mr, mf, msub, msup, mrad, md = dh.mr, dh.mf, dh.msub, dh.msup, dh.mrad, dh.md


def up(t: str):
    return mr(t, italic=False)


def sub(base: str, s: str, upright_sub: bool = True):
    return msub([mr(base)], [up(s) if upright_sub else mr(s)])


# ============================================================================= front matter
TITLE = ("A Compact Tri-Band CPW-Fed Octagonal Monopole Antenna Backed by a 4 × 4 Square-Patch Metasurface for "
         "Sub-6 GHz 5G, WLAN, X-Band and Ku-Band Applications")
DEPT = "Department of Electronics and Communication Engineering"
INST = "National Institute of Technology Silchar"
CITY = "Silchar, Assam 788010, India"
AUTHORS = [n for n, _ in lit.PROJECT["students"]] + [n.replace("Mr. ", "").replace("Dr. ", "")
                                                     for n, _ in reversed(lit.PROJECT["supervisors"])]


def setup(doc) -> None:
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(BODY)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    st.element.rPr.rFonts.set(qn("w:cs"), FONT)
    st.paragraph_format.space_after = Pt(0)
    st.paragraph_format.line_spacing = 1.0
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.top_margin, sec.bottom_margin = Inches(0.75), Inches(1.0)
    sec.left_margin = sec.right_margin = Inches(0.625)
    sec.header_distance = sec.footer_distance = Inches(0.4)


def columns(section, n: int) -> None:
    cols = section._sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        section._sectPr.append(cols)
    cols.set(qn("w:num"), str(n))
    cols.set(qn("w:space"), "360")


def front_matter(doc) -> None:
    p = fmt(doc.add_paragraph(), CENTER, after=10)
    dh.style_run(p.add_run(TITLE), 22)
    t = doc.add_table(rows=2, cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for k, name in enumerate(AUTHORS):
        c = t.cell(k // 3, k % 3)
        c.width = Inches(2.4)
        lines = [(name, 10.5, None), (DEPT, 9, True), (INST, 9, None), (CITY, 9, None), ("«e-mail»", 9, None)]
        for j, (txt, size, it) in enumerate(lines):
            cp = c.paragraphs[0] if j == 0 else c.add_paragraph()
            fmt(cp, CENTER, after=6 if j == len(lines) - 1 else 0)
            runs(cp, txt, size, italic=it)
    p = fmt(doc.add_paragraph(), CENTER, before=2, after=8)
    runs(p, "«Author order, e-mail addresses and the corresponding author to be confirmed by the guides.»", 8,
         italic=True)


# ============================================================================= sections
def abstract(doc) -> None:
    p = fmt(doc.add_paragraph(), JUSTIFY, after=6, indent=0.17)
    runs(p, "*Abstract*—", 9, bold=True)
    runs(p, (
        "In the present manuscript, a compact coplanar waveguide (CPW) fed octagonal monopole antenna backed by a "
        "4 × 4 square-patch metasurface is proposed for multiband wireless applications. The radiator is printed on a "
        f"low-cost FR-4 substrate of {SIZE}, and a metasurface of the same footprint is placed {val('h')} mm behind "
        "it across an air gap. The structure is designed and investigated in the electromagnetic simulator CST "
        "Studio Suite. With the metasurface, the antenna resonates in three bands with |S_{11}| ≤ −10 dB: "
        f"{band_txt(B1)} ({num(B1.fbw, 1)} %), {band_txt(B2)} ({num(B2.fbw, 1)} %) and {band_txt(B3)}. "
        f"Throughout the resonating bands, the lowest reflection coefficient obtained is {num(SMIN, 1)} dB at "
        f"{num(FMIN)} GHz. An equivalent-circuit model places the in-phase reflection of the metasurface near "
        f"{num(LC['f0'], 1)} GHz, inside the second band. The peak realized gain is {XX} dBi at {XX} GHz, compared "
        f"with {XX} dBi for the antenna without the metasurface. The bands cover 5G NR n79, the upper part of "
        "n77/n78, WiMAX, 5 GHz WLAN, the C-band satellite downlink, X-band radar and satellite uplink, and the Ku-band "
        "satellite links, so the proposed antenna is suitable to implement in compact multi-standard communication "
        "and sensing terminals."), 9, bold=True)
    p = fmt(doc.add_paragraph(), JUSTIFY, after=6, indent=0.17)
    runs(p, "*Keywords*—", 9, bold=True)
    runs(p, "CPW-fed antenna, octagonal monopole, metasurface, tri-band, 5G, WLAN, X-band, Ku-band", 9, bold=True,
         italic=True)


def introduction(doc) -> None:
    h1(doc, "I", "Introduction")
    para(doc, (
        "With the steady growth of the wireless industry, the demand for compact and low-cost antennas that serve "
        "several standards at once has risen sharply, since the antenna is one of the basic blocks of every RF "
        "front end [@balanis]. A present-day terminal may have to reach sub-6 GHz 5G new radio and 5 GHz wireless "
        "LAN, while sensing and satellite equipment works in the X and Ku bands [@3gpp, ieee80211, ieee521]. "
        "Planar monopoles fed by a coplanar waveguide (CPW) are widely used for such needs, because the feed line "
        "and the ground planes lie on the same side of the substrate, no via is required, and the impedance "
        "bandwidth is large [@simons, song]. Jug-shaped, triangular, elliptical and javelin-shaped CPW-fed patches "
        "have been reported for wideband operation, often with notches that avoid interference with neighbouring "
        "services [@ahmad, kumar_ellip, bhattacharya]."))
    para(doc, (
        "A printed monopole, however, radiates on both sides of the board, so its gain remains modest. A metal "
        "reflector raises the gain only when it is about a quarter wavelength away, which makes the antenna bulky. "
        "Artificial magnetic conductors (AMC), frequency selective surfaces (FSS) and metasurfaces reflect the "
        "backward wave with an engineered phase and can therefore be placed much closer [@sievenpiper]. Sen *et al.* "
        "backed a UWB monopole with a split-ring metasurface and reported a gain rise of about 5.5 dB [@sen2017]. "
        "Al-Gburi *et al.* raised the peak gain of a CPW-fed ring monopole from 6.7 to 11.5 dBi with a 19 × 19 FSS "
        "and a total profile of 10 mm [@algburi2022]. Hussain *et al.* reached 10.5 dBi with a 5 × 5 FSS 9 mm "
        "behind a CPW hexagonal patch [@hussain2023], and Hammache *et al.* obtained 8.4 dBi with a 7 × 7 FSS at "
        "20 mm [@hammache2024]. A CPW-fed octagonal monopole over a 5 × 5 AMC achieved up to 11.5 dBi over "
        "3.5–6.5 GHz [@aboelhassan2025]. Kundu and Chatterjee loaded printed UWB antennas with FSS layers for "
        "ground penetrating radar [@kundu_triple, kundu_leaf], and a conformal FSS was used to obtain "
        "frequency-dependent directive radiation [@chatterjee]. Rajalakshmi and Gunavathi etched a 2 × 2 hexagonal "
        "metamaterial array behind a cross-shaped patch and increased its gain at 2.4 and 5 GHz to 6 and 10 dBi "
        "[@rajalakshmi]."))
    para(doc, (
        "Most of the reflectors above sit 9–20 mm behind the antenna, and they target a single wide band. In the "
        "works reviewed, a compact CPW monopole backed by a closely spaced single-layer metasurface that serves "
        "sub-6 GHz, X-band and Ku-band links together has received little attention."))
    para(doc, (
        "The primary intent of the present manuscript is to propose a compact CPW-fed octagonal monopole on FR-4 and "
        f"to back it with a 4 × 4 square-patch metasurface placed {val('h')} mm behind it. Section II describes the "
        "design and the analytical estimates, Section III discusses the simulated results, Section IV presents the "
        "applications and Section V concludes the paper."))


def design_section(doc) -> None:
    h1(doc, "II", "Antenna Design and Analysis")
    h2(doc, "A", "Antenna Geometry")
    para(doc, (
        "The geometry of the proposed antenna is depicted in Fig. 1(a), and its dimensions are given in Table I. The "
        f"radiator is a regular octagon of circumradius R = {val('R')} mm standing on one vertex. It is printed on an "
        f"FR-4 substrate (ε_{{r}} = {d.FR4_EPS:g}, tan δ = {d.FR4_TAND:g}) of {val('W_{s}')} mm × {val('L_{s}')} mm "
        f"and {val('h_{s}')} mm thickness. The octagon is fed by a CPW line of width W_{{f}} = {val('W_{f}')} mm, "
        f"separated from the two coplanar ground planes by slots of g = {val('g')} mm; the feed and slot widths are "
        "selected for impedance matching to the 50 Ω port. Each ground plane is "
        f"W_{{g}} = {val('W_{g}')} mm wide and L_{{g}} = {val('L_{g}')} mm long, and the lower vertex of the octagon "
        f"lies p = {val('p')} mm above the ground edge. Since the CPW grounds carry current and take part in the "
        "radiation, their length and the patch-to-ground gap mainly control the matching at the lower end of the "
        "band [@simons]."))
    figure(doc, "fig1_geometry.png", 1, (
        "Geometry of the proposed structure: (a) CPW-fed octagonal monopole antenna, (b) 4 × 4 square-patch "
        "metasurface (top view, CST Studio Suite)."))
    para(doc, (
        "To estimate the lower edge of the operating band, the octagon is replaced by a cylindrical monopole of the "
        "same height and the same surface area [@ray, kumar_ray]:"))
    equation(doc, [sub("f", "L"), up(" = "),
                   mf([up("7.2")], [md([mr("l"), up(" + "), mr("r"), up(" + "), mr("p")]), mr("k")]),
                   up(" GHz")], 1)
    equation(doc, [mr("r"), up(" = "), mf([mr("A")], [up("2π"), mr("l")])], 2)
    para(doc, (
        f"where l = 2R = {num(RAY['l'], 1)} mm is the height of the octagon, A = 2√2R^{{2}} = {num(RAY['A'], 1)} "
        f"mm^{{2}} its area, r = {num(RAY['r'])} mm the radius of the equivalent cylinder and p = {val('p')} mm the "
        "gap to the ground, all taken in centimetres in (1); k = 1.15 is the empirical factor for an FR-4 substrate "
        f"[@ray]. Equation (1) gives f_{{L}} ≈ {num(RAY['f'])} GHz, within "
        f"{num(100 * (B1.lo - RAY['f']) / B1.lo, 0)} % of the simulated lower edge of {num(B1.lo)} GHz "
        "(Section III). The small difference is expected, because (1) ignores the metasurface and the finite CPW "
        "ground."))
    h2(doc, "B", "Metasurface Design")
    para(doc, (
        f"The metasurface of Fig. 1(b) is a 4 × 4 array of square copper patches of side W_{{p}} = {val('W_{p}')} mm "
        f"and period P = {val('P')} mm, so that adjacent patches are separated by s = {val('s')} mm. It is printed "
        f"on a {val('t')} mm FR-4 board of the same footprint as the antenna, {BACK}. Such a surface behaves as a "
        "parallel LC resonator [@sievenpiper]: the gaps between the patches provide the capacitance, and the current "
        "loop through the ground provides the inductance,"))
    equation(doc, [mr("L"), up(" = "), sub("μ", "0"), mr("t")], 3)
    equation(doc, [mr("C"), up(" = "),
                   mf([sub("W", "p", False), sub("ε", "0"), md([up("1 + "), sub("ε", "r", False)])], [up("π")]),
                   msup([up("cosh")], [up("−1")]), md([mf([mr("P")], [mr("s")])])], 4)
    equation(doc, [sub("f", "0"), up(" = "), mf([up("1")], [up("2π"), mrad(mr("L"), mr("C"))]), up(" ,   "),
                   up("BW = "), mf([up("1")], [sub("η", "0")]), mrad(mf([mr("L")], [mr("C")]))], 5)
    para(doc, (
        "where t is the thickness of the metasurface substrate and η_{0} ≈ 377 Ω is the free-space impedance. With "
        f"the dimensions of Table I, (3)–(5) give L = {num(LC['L_nH'])} nH, C = {num(LC['C_pF'], 3)} pF and "
        f"f_{{0}} ≈ {num(LC['f0'], 1)} GHz, with a reflection phase within ±90° over about {num(LC['bw'], 0)} % "
        f"({num(LC['f_lo'], 1)}–{num(LC['f_hi'], 1)} GHz). Near f_{{0}} the surface reflects in phase, whereas a "
        "metal plate reflects with a phase reversal of 180°."))
    para(doc, (
        "The wave radiated backwards crosses the air gap h, is reflected by the metasurface and returns to the "
        "antenna. It reinforces the forward radiation when [@hussain2023]"))
    equation(doc, [sub("φ", "MS"), up(" − 2"), sub("k", "0"), mr("h"), up(" = 2"), mr("n"), up("π,   "), mr("n"),
                   up(" = 0, 1, …")], 6)
    para(doc, (
        "where φ_{MS} is the reflection phase of the metasurface and k_{0} = 2π/λ_{0}. At f_{0}, φ_{MS} ≈ 0 and "
        f"h = {val('h')} mm gives 2k_{{0}}h ≈ {num(RT, 0)}°, so the reflected wave returns within ±90° of the "
        "forward wave across the in-phase band of the metasurface. A metal plate at the same gap (φ = 180°) would "
        "cancel the forward wave instead."))
    table(doc, 1, "Dimensions of the Proposed Antenna and Metasurface (mm)", _dims_rows(),
          [0.74] + [0.46] * 6, header_rows=(0, 2, 4), header_col=True)
    h2(doc, "C", "Design Stages")
    para(doc, (
        "The design is carried out in two stages, as depicted in Fig. 2. In stage 1, the octagonal antenna is "
        "designed alone and its ground and patch are tuned for impedance matching. In stage 2, the metasurface is "
        "placed behind the antenna across the air gap h and the complete structure is simulated again. The "
        "simulations use the frequency-domain solver of CST Studio Suite with a waveguide port at the CPW feed, from "
        "1 to 15 GHz."))
    figure(doc, "fig2_stackup.png", 2, (
        "Side view of the proposed structure: the backward wave of the antenna is reflected by the metasurface and "
        "adds to the forward wave (schematic, not to scale)."))


def _dims_rows() -> list[list[str]]:
    dims = d.ANTENNA + d.METASURFACE
    rows = []
    for k in range(0, len(dims), 6):
        chunk = dims[k:k + 6]
        pad = [""] * (6 - len(chunk))
        rows.append(["Parameter"] + [x.symbol for x in chunk] + pad)
        rows.append(["Value"] + [val(x.symbol) for x in chunk] + pad)
    return rows


def results(doc) -> None:
    h1(doc, "III", "Results and Discussion")
    h2(doc, "A", "Reflection Coefficient")
    others = [f for f, _ in DIPS if abs(f - FMIN) > 0.05]
    para(doc, (
        "The simulated reflection coefficient of the proposed antenna with the metasurface is depicted in Fig. 3, "
        f"and the bands are summarized in Table II. The structure exhibits three −10 dB bands: band I from "
        f"{num(B1.lo)} to {num(B1.hi)} GHz, band II from {num(B2.lo)} to {num(B2.hi)} GHz and band III from "
        f"{num(B3.lo)} GHz to beyond 15 GHz, the upper limit of the simulation. The percentage bandwidths of bands I "
        f"and II are {num(B1.fbw, 1)} % and {num(B2.fbw, 1)} %. Throughout the resonating bands, the lowest "
        f"reflection coefficient obtained is {num(SMIN, 1)} dB at {num(FMIN)} GHz, and further resonances appear at "
        f"{', '.join(num(f) for f in others[:-1])} and {num(others[-1])} GHz. Between the bands, |S_{{11}}| rises "
        f"to {num(GAP1[1], 1)} dB at {num(GAP1[0])} GHz and to {num(GAP2[1], 1)} dB at {num(GAP2[0])} GHz. These "
        "regions are not designed notches; they mark the edges of the operating bands. Band III stays only about "
        "1 dB below the −10 dB level, so it is marginal and should be confirmed with a finer mesh and by "
        "measurement."))
    figure(doc, "fig3_s11.png", 3, (
        "Simulated reflection coefficient of the proposed antenna with the metasurface; the shaded regions are the "
        "three −10 dB bands. «The antenna-alone curve (stage 1) is to be added from CST.»"))
    para(doc, (
        f"Because the copper ground of the metasurface lies only {val('h')} mm behind the antenna, outside the "
        "in-phase band of Section II-B it acts close to a metal mirror, and the low-frequency matching of the antenna "
        "is expected to be affected most. «The reflection coefficient of the antenna without the metasurface "
        "(stage 1), to be added to Fig. 3 and Table II, quantifies this effect: lower band edge [xx] GHz without "
        "the metasurface.»"))
    table(doc, 2, "Simulated Performance of the Design Stages", [
        ["Stage", "−10 dB band (GHz)", "FBW (%)", "Lowest |S_{11}| (dB)", "Peak gain (dBi)"],
        ["1: antenna alone", XX, XX, XX, XX],
        ["2: with metasurface",
         f"{num(B1.lo)}–{num(B1.hi)}\n{num(B2.lo)}–{num(B2.hi)}\n{num(B3.lo)}–>15",
         f"{num(B1.fbw, 1)}\n{num(B2.fbw, 1)}\n≥ {num(B3.fbw, 1)}",
         f"{num(SMIN, 1)} at {num(FMIN)} GHz", XX],
    ], [0.85, 0.95, 0.5, 0.7, 0.45], header_col=True)
    h2(doc, "B", "Gain")
    para(doc, (
        "The simulated realized gain in the broadside direction, with and without the metasurface, is depicted in "
        "Fig. 4. «[To be completed from the CST gain results: the peak realized gain with the metasurface is [xx] "
        "dBi at [xx] GHz against [xx] dBi without it. The largest improvement is expected in band II, where the "
        "metasurface reflects in phase (Section II-B); a reduction at frequencies where (6) is not met should be "
        "reported as well.]»"))
    figure(doc, "fig4_gain.png", 4, "Simulated realized gain of the antenna with and without the metasurface.")
    h2(doc, "C", "Radiation Pattern")
    para(doc, (
        f"The E-plane and H-plane radiation patterns at {', '.join(f'{f:g}' for f in d.PATTERN_FREQS[:-1])} and "
        f"{d.PATTERN_FREQS[-1]:g} GHz, one frequency in each band, are depicted in Fig. 5. «[To be completed from the "
        "CST far-field results: the pattern shape in each band, the direction of maximum radiation and the "
        "front-to-back ratio with and without the metasurface.]»"))
    figure(doc, "fig5_patterns.png", 5, (
        f"Simulated E-plane and H-plane radiation patterns (dB) at "
        f"{', '.join(f'{f:g}' for f in d.PATTERN_FREQS[:-1])} and {d.PATTERN_FREQS[-1]:g} GHz."))
    h2(doc, "D", "Comparison with Reported Works")
    lam = num(PROFILE / LAMBDA_LO, 3)
    para(doc, (
        "Table III compares the proposed antenna with reported printed antennas that use a reflector or a "
        f"metamaterial layer. The total profile of the proposed structure is «{num(PROFILE, 1)}» mm (about «{lam}» "
        f"λ_{{0}} at {num(B1.lo)} GHz), lower than that of the FSS-backed designs [@algburi2022, hussain2023, "
        "hammache2024], and its metasurface is no larger than the antenna itself. The metamaterial of "
        "[@rajalakshmi] is thinner still, as it is etched on the antenna substrate, but it serves two narrow Wi-Fi "
        f"bands. The gain of the proposed antenna, {XX} dBi, is to be compared once the CST results are available."))
    table(doc, 3, "Comparison with Reported Antennas", [
        ["Ref.", "Antenna; reflector", "Size (mm)", "Gap (mm)", "Band (GHz)", "Peak gain (dBi)"],
        ["[@algburi2022]", "CPW ring monopole; 19 × 19 FSS", "50 × 50", "10 (total)", "2.2–11.9", "11.3 (meas.)"],
        ["[@hussain2023]", "CPW hexagon; 5 × 5 FSS", "32 × 25; FSS 50 × 50", "9", "3–18", "10.5"],
        ["[@hammache2024]", "CPW hexagon; 7 × 7 FSS", "30 × 30", "20", "UWB", "8.4"],
        ["[@aboelhassan2025]", "CPW octagon; 5 × 5 AMC", "27 × 37; AMC 70 × 70", "air gap", "3.5–6.5", "9.9–11.5"],
        ["[@rajalakshmi]", "Cross patch; 2 × 2 hexagonal CSRR array", "20 × 25", "0", "2.4, 5", "6, 10 (meas.)"],
        ["This work", "CPW octagon; 4 × 4 patch metasurface", f"{val('W_{s}')} × {val('L_{s}')}", f"{val('h')}",
         f"{num(B1.lo)}–{num(B1.hi)}\n{num(B2.lo)}–{num(B2.hi)}\n{num(B3.lo)}–>15", XX],
    ], [0.43, 0.82, 0.6, 0.45, 0.65, 0.55], header_col=False)


def applications(doc) -> None:
    h1(doc, "IV", "Applications")
    n77 = COV["5G NR n77 (incl. n78)"]
    para(doc, (
        "The bands of the proposed antenna are mapped onto the services they serve in Fig. 6 and Table IV. Band I "
        f"({num(B1.lo)}–{num(B1.hi)} GHz) covers the whole of 5G NR n79 (4.4–5.0 GHz), the C-band satellite "
        "downlink (3.7–4.2 GHz) and the 5 GHz WLAN channels of IEEE 802.11a/n/ac/ax (5.15–5.85 GHz) "
        f"[@3gpp, ieee80211], together with {num(n77, 0)} % of 5G NR n77 (3.3–4.2 GHz, which contains n78) and of "
        f"the 3.5 GHz WiMAX band. Band II ({num(B2.lo)}–{num(B2.hi)} GHz) contains the complete X band (8–12 GHz) "
        "[@ieee521], used by marine and weather radars near 9.4 GHz and by the X-band satellite uplink "
        "(7.9–8.4 GHz), as well as the Ku-band satellite downlink (10.7–12.75 GHz) [@itu_rr]. Band III includes the "
        "Ku-band VSAT uplink (14.0–14.5 GHz)."))
    figure(doc, "fig6_applications.png", 6, (
        "Bands of the proposed antenna (top) and the services they serve; solid bars are fully covered, hatched bars "
        "partly, with the covered share shown."))
    table(doc, 4, "Applications of the Proposed Antenna", [
        ["Band", "Range (GHz)", "Applications"],
        ["I", f"{num(B1.lo)}–{num(B1.hi)}", "5G NR n77/n78 (upper part), n79; WiMAX; C-band satellite downlink; "
                                           "5 GHz WLAN and ISM"],
        ["II", f"{num(B2.lo)}–{num(B2.hi)}", "X-band satellite uplink; X-band marine, weather and short-range radar; "
                                            "Ku-band satellite downlink (DTH)"],
        ["III", f"{num(B3.lo)}–>15", "Ku-band VSAT uplink"],
    ], [0.45, 0.85, 2.15], header_col=True)
    para(doc, (
        "A practical use is a compact multi-standard terminal in which one radiator serves the 5G and WLAN links of "
        "band I and an X-band sensing or satellite link of band II. For short-range sensing, two identical antennas "
        "can act as the transmitter and receiver of an X-band radar, in the way UWB antennas are used in "
        "surface-penetrating radar [@bhattacharya, kundu_triple]: the transmission coefficient S_{21} between them "
        "is recorded with and without a target, and the difference reveals the target. The metasurface directs the "
        "radiation away from the ground side, which reduces coupling to the electronics placed behind the antenna "
        f"«(to be confirmed with the front-to-back ratio of Fig. 5)». Since bands I and II are separated by the "
        f"unmatched region of {num(B1.hi)}–{num(B2.lo)} GHz, the antenna is not intended for impulse (UWB) radar."))


def conclusion(doc) -> None:
    h1(doc, "V", "Conclusion")
    para(doc, (
        "A compact CPW-fed octagonal monopole antenna backed by a 4 × 4 square-patch metasurface has been proposed. "
        f"The outcomes demonstrate that the structure, with a footprint of {val('W_{s}')} mm × {val('L_{s}')} mm "
        f"and a total profile of «{num(PROFILE, 1)}» mm, provides three impedance bands with |S_{{11}}| ≤ −10 dB: "
        f"{band_txt(B1)}, {band_txt(B2)} and {band_txt(B3)}, with a lowest reflection coefficient of "
        f"{num(SMIN, 1)} dB at {num(FMIN)} GHz. The equivalent-circuit model places the in-phase reflection of the "
        f"metasurface near {num(LC['f0'], 1)} GHz, inside the second band. «[Gain sentence: the peak realized gain "
        "is [xx] dBi, an improvement of [xx] dB over the antenna alone.]» The bands serve sub-6 GHz 5G, WLAN, X-band "
        "radar and satellite links and the Ku-band satellite links, so the proposed antenna is suitable to implement "
        "in compact multi-standard communication and sensing systems. Fabrication and measurement of the prototype "
        "are the next step of this work."))


def reference_list(doc) -> None:
    p = fmt(doc.add_paragraph(), CENTER, before=8, after=4, keep=True)
    r = p.add_run("References")
    dh.style_run(r, BODY)
    r.font.small_caps = True
    for n, key in enumerate(CITE.order, 1):
        p = fmt(doc.add_paragraph(), JUSTIFY, after=1)
        pf = p.paragraph_format
        pf.left_indent = Inches(0.3)
        pf.first_line_indent = Inches(-0.3)
        pf.tab_stops.add_tab_stop(Inches(0.3))
        dh.add_runs(p, f"[{n}]\t{ref_lookup(key)}", SMALL)


# ============================================================================= checks
def plain_text(doc, body_only: bool = False) -> str:
    """All text; body_only drops the author block and the reference list (titles there must match the sources)."""
    parts = []
    for p in doc.paragraphs:
        if body_only and p.text.strip() == "References":
            break
        parts.append(p.text)
    for t in doc.tables[1 if body_only else 0:]:
        for row in t.rows:
            parts += [c.text for c in row.cells]
    return "\n".join(parts)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def similarity(text: str, pdfs: list[Path], n: int = 8) -> int:
    """Count n-word sequences shared with each reference PDF (via pdftotext); prints every match."""
    mine = _words(text)
    grams = {tuple(mine[i:i + n]) for i in range(len(mine) - n + 1)}
    total = 0
    for pdf in pdfs:
        ref = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
        rw = _words(ref)
        hits = {tuple(rw[i:i + n]) for i in range(len(rw) - n + 1)} & grams
        total += len(hits)
        print(f"  {pdf.name}: {len(hits)} shared {n}-word sequences")
        for h in sorted(hits):
            print("    ", " ".join(h))
    return total


def build() -> Path:
    doc = Document()
    setup(doc)
    front_matter(doc)
    body = doc.add_section(WD_SECTION.CONTINUOUS)
    columns(body, 2)
    abstract(doc)
    introduction(doc)
    design_section(doc)
    results(doc)
    applications(doc)
    conclusion(doc)
    reference_list(doc)
    end = doc.add_section(WD_SECTION.CONTINUOUS)   # a trailing continuous break balances the last page's columns
    columns(end, 2)
    doc.core_properties.title = TITLE
    doc.core_properties.author = ", ".join(AUTHORS)
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", nargs="*", type=Path, default=[], help="reference PDFs for the 8-word overlap check")
    a = ap.parse_args()
    out = build()
    built = Document(str(out))
    text = plain_text(built)
    print(f"Generated {out.relative_to(d.ROOT)}  (S11: {S11_SRC}; {len(CITE.order)} references)")
    flagged = re.findall(r"\[xx\]", text)
    print(f"  [xx] placeholders: {len(flagged)}")
    if a.compare:
        print(f"  overlap check (body, without author block and references): "
              f"{similarity(plain_text(built, body_only=True), a.compare)} shared sequences in total")
    pdf = render_pdf(out)
    if pdf:
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", info)
        print(f"Rendered {pdf.relative_to(d.ROOT)}: {m.group(1) if m else '?'} pages")
    else:
        print("LibreOffice (soffice) not found: open Paper.docx in Word and export to PDF.")
