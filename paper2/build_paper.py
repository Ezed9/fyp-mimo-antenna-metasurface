# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pillow>=10", "numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Build the conference paper "MIMO Antenna with FSS": paper2/MIMO_Antenna_with_FSS.docx and .pdf.

Run from the repo root:
  uv run analysis/digitize_cst_plot.py paper2/inputs/04_s11.png --x 0 16 --y -40 0 --step 0.02 \
      --column S11_dB --out paper2/data/s11_digitized.csv          # only when the S11 plot changes
  uv run paper2/build_paper.py

Layout: IEEE two-column conference style (US Letter, Times New Roman, single-column title block, two-column body).
It reuses the text markup, citation numbering and equation helpers of report/docx_helpers.py and the reference
list of report/literature.py; nothing under report/ is changed.

The paper follows the co-guide's order: the single antenna first, then the four-port MIMO antenna with the FSS,
and a comparison of the two results.

Rules this script keeps:
* MIMO antenna with FSS: the only result is the simulated S11 curve in paper2/inputs/04_s11.png. Every number for
  it is computed here from its digitised copy (paper2/data/s11_digitized.csv), so text and tables cannot drift
  from the plot.
* Single antenna: dimensions and results are the team's existing CST values recorded in the repository
  (report/literature.py THIS_WORK, report/build_report.py, GAP_STUDY.md); its S11 plot is figures/
  cst_single_final_s11.png, copied to paper2/inputs/06_single_s11.png.
* Nothing else is reported. Gain, isolation, ECC, efficiency and radiation patterns of the MIMO antenna, and the
  MIMO and FSS dimensions, are not invented: each is a yellow "TO BE ADDED" placeholder (written «like this»
  below) and is listed in paper2/MISSING.md.
* The figures are the team's CST images in paper2/inputs/, only cropped. Fig. 6 redraws the two S11 curves on one
  pair of axes from their digitised copies.
"""
from __future__ import annotations

import io
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "report"))

import docx_helpers as dh  # noqa: E402
import literature as lit  # noqa: E402
import numpy as np  # noqa: E402
from build_report import render_pdf  # noqa: E402
from docx import Document  # noqa: E402
from docx.enum.section import WD_SECTION  # noqa: E402
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_TAB_ALIGNMENT  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402
from PIL import Image  # noqa: E402

INPUTS = HERE / "inputs"
S11_CSV = HERE / "data" / "s11_digitized.csv"                 # four-port MIMO antenna with the FSS, port 1
S11_SINGLE_CSV = HERE / "data" / "s11_single_digitized.csv"   # single antenna (figures/cst_single_final_s11.png)
OUT = HERE / "MIMO_Antenna_with_FSS.docx"

TITLE = "MIMO Antenna with FSS"
FONT = "Times New Roman"
COL_W, PAGE_W = 3.5, 7.25          # column and text-block width, inches
BODY, SMALL = 10, 8
JUSTIFY, CENTER, LEFT = WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT
HL = re.compile(r"«([^»]*)»")
TBA = "«TO BE ADDED»"

# Crops of the CST views, (left, top, right, bottom) in source pixels: the board without the grey background.
CROP_BOARD = (440, 0, 1166, 671)
CROP_S11_SINGLE = (8, 64, 2288, 950)   # 06_single_s11.png without the empty band above the plot title
CROP_CELL = (573, 146, 695, 268)   # one unit cell (row 2, column 2) of 01_fss_array.webp, centred on its rings


# ============================================================================= S11 numbers (from the digitised plot)
def load_s11(path: Path = S11_CSV) -> tuple[np.ndarray, np.ndarray]:
    d = np.genfromtxt(path, delimiter=",", comments="#", skip_header=4)
    return d[:, 0], d[:, 1]


def bands(f: np.ndarray, s: np.ndarray, level: float = -10.0) -> list[tuple[float, float, bool]]:
    """(low edge, high edge, runs to the end of the sweep) of every stretch below `level`."""
    below, out, k = s < level, [], 0
    while k < len(f):
        if not below[k]:
            k += 1
            continue
        j = k
        while j + 1 < len(f) and below[j + 1]:
            j += 1
        lo = f[k] if k == 0 else f[k - 1] + (level - s[k - 1]) / (s[k] - s[k - 1]) * (f[k] - f[k - 1])
        hi = f[j] if j == len(f) - 1 else f[j] + (level - s[j]) / (s[j + 1] - s[j]) * (f[j + 1] - f[j])
        out.append((float(lo), float(hi), j == len(f) - 1))
        k = j + 1
    return out


def dips(f: np.ndarray, s: np.ndarray, below: float = -20.0, half_window: float = 0.24) -> list[tuple[float, float]]:
    """Local minima deeper than `below` (each the lowest point within ±half_window GHz)."""
    w = int(round(half_window / float(np.median(np.diff(f)))))
    out = []
    for i in range(len(s)):
        seg = s[max(0, i - w):i + w + 1]
        if s[i] < below and s[i] == seg.min() and (not out or f[i] - out[-1][0] > half_window):
            out.append((float(f[i]), float(s[i])))
    return out


def peak(f: np.ndarray, s: np.ndarray, lo: float, hi: float) -> tuple[float, float]:
    sel = (f >= lo) & (f <= hi)
    i = int(np.argmax(s[sel]))
    return float(f[sel][i]), float(s[sel][i])


F, S = load_s11()
BANDS = bands(F, S)
assert len(BANDS) == 2 and BANDS[1][2], f"the text below assumes two −10 dB bands, the second open-ended: {BANDS}"
(B1_LO, B1_HI, _), (B2_LO, B2_HI, _) = BANDS
F_STOP = float(F[-1])
DIPS = dips(F, S)
F_MIN, S_MIN = min(DIPS, key=lambda x: x[1])
GAP_F, GAP_S = peak(F, S, B1_HI, B2_LO)            # the short stretch above −10 dB between the two bands
WEAK_F, WEAK_S = peak(F, S, 4.0, 5.0)              # second-weakest point, inside band 1
HIGH_F, HIGH_S = peak(F, S, 10.5, F_STOP)          # weakest point above 10.5 GHz
HIGH_MIN = float(S[F >= 10.5].min())               # and the best point there


def stretch_below(level: float, f_inside: float) -> tuple[float, float]:
    """The continuous frequency range below `level` that contains f_inside."""
    return next((lo, hi) for lo, hi, _ in bands(F, S, level) if lo <= f_inside <= hi)


GOOD_LO, GOOD_HI = stretch_below(-20.0, F_MIN)     # the well-matched region around the deepest resonance


# Single antenna: the band edges and resonances are the team's CST marker values (report/literature.py); the
# digitised curve is used for Fig. 6 and for the two weak points, and must agree with the markers.
FS, SS = load_s11(S11_SINGLE_CSV)
S_LO, S_HI = lit.THIS_WORK["band_ghz"]
_single_band = max(bands(FS, SS), key=lambda b: b[1] - b[0])
assert abs(_single_band[0] - S_LO) < 0.05 and abs(_single_band[1] - S_HI) < 0.05, _single_band
S_WEAK1 = peak(FS, SS, 5.0, 8.0)                   # weakest points inside the single antenna's band
S_WEAK2 = peak(FS, SS, 10.0, 13.5)


def fbw(lo: float, hi: float) -> float:
    return 200 * (hi - lo) / (hi + lo)


def n(x: float, nd: int = 2) -> str:
    return f"{x:.{nd}f}".replace("-", "−")


# ============================================================================= references
EXTRA_REFS = {
    "munk": "B. A. Munk, *Frequency Selective Surfaces: Theory and Design*. New York, NY, USA: Wiley, 2000.",
    "ranga": "Y. Ranga, L. Matekovits, K. P. Esselle, and A. R. Weily, “Multioctave frequency selective surface "
             "reflector for ultrawideband antennas,” *IEEE Antennas Wireless Propag. Lett.*, vol. 10, pp. 219–222, "
             "2011, doi: 10.1109/LAWP.2011.2130509.",
    "kundu": "S. Kundu, A. Chatterjee, S. K. Jana, and S. K. Parui, “Gain enhancement of a printed leaf shaped UWB "
             "antenna using dual FSS layers and experimental study for ground coupling GPR applications,” *Microw. "
             "Opt. Technol. Lett.*, vol. 60, no. 6, pp. 1417–1423, Jun. 2018, doi: 10.1002/mop.31171.",
    "algburi_review": "A. J. A. Al-Gburi, I. M. Ibrahim, Z. Zakaria, M. K. Abdulhameed, and T. Saeidi, “Enhancing "
                      "gain for UWB antennas using FSS: A systematic review,” *Mathematics*, vol. 9, no. 24, "
                      "Art. no. 3301, 2021, doi: 10.3390/math9243301.",
    "ushadevi": "Y. Usha Devi, B. T. P. Madhav, S. Das, T. Islam, and M. El Ghzaoui, “Dual-notched UWB orthogonal "
                "MIMO antenna with improved gain characteristics using frequency selective surfaces for wireless "
                "communication applications,” *J. Circuits, Syst. Comput.*, 2024, doi: 10.1142/S0218126624502323.",
    "blanch": "S. Blanch, J. Romeu, and I. Corbella, “Exact representation of antenna system diversity performance "
              "from input parameter description,” *Electron. Lett.*, vol. 39, no. 9, pp. 705–707, May 2003, "
              "doi: 10.1049/el:20030495.",
}


def ref_lookup(key: str) -> str:
    return EXTRA_REFS[key] if key in EXTRA_REFS else lit.ref_text(key)


CITE = dh.Citer(ref_lookup)


# ============================================================================= writers
def runs(p, text: str, size: float = BODY, bold: bool | None = None, italic: bool | None = None) -> None:
    """docx_helpers mini-markup, [@key] citations, and «yellow highlight» for placeholders."""
    text = CITE.render(text)
    pos, pieces = 0, []
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
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), 1.0
    if indent is not None:
        pf.first_line_indent = Inches(indent)
    pf.keep_with_next = keep
    return p


def para(doc, text: str) -> None:
    runs(fmt(doc.add_paragraph(), indent=0.17), text)


def small_caps_line(doc, text: str, size: float, before: float, after: float) -> None:
    p = fmt(doc.add_paragraph(), CENTER, before=before, after=after, keep=True)
    r = p.add_run(text)
    dh.style_run(r, size)
    r.font.small_caps = True


def h1(doc, numeral: str, text: str) -> None:
    small_caps_line(doc, f"{numeral}. {text}", BODY, 8, 4)


def h2(doc, letter: str, text: str) -> None:
    runs(fmt(doc.add_paragraph(), LEFT, before=4, after=2, keep=True), f"{letter}. {text}", BODY, italic=True)


def png(name: str, crop: tuple[int, int, int, int] | None = None, scale: int = 1) -> io.BytesIO:
    """An input image as an in-memory PNG (python-docx cannot embed WebP), optionally cropped and enlarged."""
    with Image.open(INPUTS / name) as im:
        im = im.convert("RGB")
        if crop:
            im = im.crop(crop)
        if scale > 1:
            im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="PNG")
    buf.seek(0)
    return buf


def caption(doc, num: int, text: str, align=JUSTIFY) -> None:
    runs(fmt(doc.add_paragraph(), align, before=2, after=6), f"Fig. {num}. " + text, SMALL)


def figure(doc, num: int, name: str, text: str, width: float, crop=None, align=JUSTIFY) -> None:
    doc.add_picture(png(name, crop), width=Inches(width))
    fmt(doc.paragraphs[-1], CENTER, before=4, keep=True)
    caption(doc, num, text, align)


def figure_pair(doc, num: int, left: io.BytesIO, w_left: float, right: io.BytesIO, w_right: float, text: str) -> None:
    """Two images side by side with (a)/(b) labels, in a borderless table one column wide."""
    t = doc.add_table(rows=2, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for j, (img, w, label) in enumerate(((left, w_left, "(a)"), (right, w_right, "(b)"))):
        cell_w = w + 0.1
        t.columns[j].width = Inches(cell_w)
        for i in range(2):
            c = t.cell(i, j)
            c.width = Inches(cell_w)
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = fmt(t.cell(0, j).paragraphs[0], CENTER, before=4, keep=True)
        p.add_run().add_picture(img, width=Inches(w))
        runs(fmt(t.cell(1, j).paragraphs[0], CENTER, keep=True), label, SMALL)
    caption(doc, num, text)


def placeholder_figure(doc, num: int, what: str, text: str, height: float = 1.25) -> None:
    """A dashed, column-wide box for a result figure that does not exist yet (never filled with invented data)."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    t.columns[0].width = Inches(3.3)
    c = t.cell(0, 0)
    c.width = Inches(3.3)
    borders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        for k, val in (("w:val", "dashed"), ("w:sz", "8"), ("w:color", "808080"), ("w:space", "0")):
            b.set(qn(k), val)
        borders.append(b)
    c._tc.get_or_add_tcPr().append(borders)
    h = OxmlElement("w:trHeight")
    h.set(qn("w:val"), str(int(height * 1440)))
    h.set(qn("w:hRule"), "atLeast")
    t.rows[0]._tr.get_or_add_trPr().append(h)
    c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    runs(fmt(c.paragraphs[0], CENTER, keep=True), "«TO BE ADDED»", 10, bold=True)
    runs(fmt(c.add_paragraph(), CENTER, keep=True), what, SMALL, italic=True)
    caption(doc, num, text + " «TO BE ADDED.»")


ROMAN = ["I", "II", "III", "IV"]


def table(doc, num: int, title: str, rows: list[list[str]], widths: list[float], first_col_left: bool = True,
          note: str | None = None) -> None:
    assert sum(widths) <= COL_W + 1e-6, f"table {num} is wider than the column"
    small_caps_line(doc, f"TABLE {ROMAN[num - 1]}", SMALL, 6, 0)
    small_caps_line(doc, title, SMALL, 0, 3)
    t = doc.add_table(rows=len(rows), cols=len(widths))
    t.style = doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    mar = OxmlElement("w:tblCellMar")              # narrow side margins, so short headers do not wrap
    for side in ("left", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), "50")
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    t._tbl.tblPr.append(mar)
    for j, w in enumerate(widths):
        t.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        t.rows[i]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for j, text in enumerate(row):
            c = t.cell(i, j)
            c.width = Inches(widths[j])
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp = fmt(c.paragraphs[0], LEFT if (j == 0 and first_col_left) else CENTER, keep=i < len(rows) - 1)
            runs(cp, text, SMALL, bold=True if i == 0 else None)
            if note and i == len(rows) - 1:
                cp.paragraph_format.keep_with_next = True
    runs(fmt(doc.add_paragraph(), LEFT, before=1, after=4), note or "", 7.5)


def equation(doc, nodes: list, num: int) -> None:
    p = fmt(doc.add_paragraph(), LEFT, before=3, after=3)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(COL_W / 2), WD_TAB_ALIGNMENT.CENTER)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(COL_W), WD_TAB_ALIGNMENT.RIGHT)
    dh.style_run(p.add_run("\t"), BODY)
    om = OxmlElement("m:oMath")
    for node in nodes:
        om.append(node)
    p._p.append(om)
    dh.style_run(p.add_run(f"\t({num})"), BODY)


def up(t: str):
    return dh.mr(t, italic=False)


def sub(base: str, s: str):
    return dh.msub([dh.mr(base)], [up(s)])


def columns(section, count: int) -> None:
    cols = section._sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        section._sectPr.append(cols)
    cols.set(qn("w:num"), str(count))
    cols.set(qn("w:space"), "360")


def new_section(doc, count: int) -> None:
    columns(doc.add_section(WD_SECTION.CONTINUOUS), count)


# ============================================================================= content
def setup(doc) -> None:
    st = doc.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(BODY)
    for attr in ("w:eastAsia", "w:cs"):
        st.element.rPr.rFonts.set(qn(attr), FONT)
    st.paragraph_format.space_after, st.paragraph_format.line_spacing = Pt(0), 1.0
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.top_margin, sec.bottom_margin = Inches(0.75), Inches(1.0)
    sec.left_margin = sec.right_margin = Inches(0.625)


def front_matter(doc) -> None:
    """Title block. Authors, affiliation and guides are those of report/MidSem_Report.pdf (report/literature.py)."""
    pj = lit.PROJECT
    dh.style_run(fmt(doc.add_paragraph(), CENTER, after=10).add_run(TITLE), 24)
    students = [name for name, _ in pj["students"]]
    runs(fmt(doc.add_paragraph(), CENTER, after=3), ", ".join(students), 11)
    runs(fmt(doc.add_paragraph(), CENTER), "Department of Electronics and Communication Engineering", 10, italic=True)
    runs(fmt(doc.add_paragraph(), CENTER, after=3), "National Institute of Technology Silchar, Assam (India)-788010",
         10, italic=True)
    guide, coguide = pj["supervisors"][0][0], pj["supervisors"][1][0]
    runs(fmt(doc.add_paragraph(), CENTER, after=12), f"Under the guidance of {guide} and {coguide} (Co-Guide)", 10)


def abstract(doc) -> None:
    p = fmt(doc.add_paragraph(), JUSTIFY, after=6, indent=0.17)
    runs(p, "*Abstract*—", 9, bold=True)
    runs(p, (
        "This paper presents a four-port multiple-input multiple-output (MIMO) antenna placed over a frequency "
        "selective surface (FSS), and compares it with the single antenna from which it is built. The single "
        "antenna is a ten-sided (decagonal) patch with a coplanar-waveguide (CPW) feed on an FR-4 board. In "
        f"simulation, its reflection coefficient is below −10 dB from {n(S_LO)} to {n(S_HI)} GHz. Four such "
        "elements form the MIMO antenna, and the FSS behind it is a 6 × 5 array of concentric split rings. "
        "All models are simulated in CST Studio Suite. With the FSS, the reflection coefficient at port 1 of the "
        f"MIMO antenna is below −10 dB from {n(B1_LO)} to {n(B1_HI)} GHz and from {n(B2_LO)} GHz to the end of "
        f"the simulated range at {n(F_STOP, 0)} GHz, with a short rise to {n(GAP_S, 1)} dB at {n(GAP_F)} GHz "
        f"between them. The lower band edge moves down from {n(S_LO)} to {n(B1_LO)} GHz. "
        "«Port isolation, gain, envelope correlation coefficient and radiation patterns of the MIMO antenna: "
        "TO BE ADDED.»"), 9, bold=True)
    p = fmt(doc.add_paragraph(), JUSTIFY, after=6, indent=0.17)
    runs(p, "*Keywords*—", 9, bold=True)
    runs(p, "MIMO antenna, frequency selective surface, split-ring resonator, CPW feed, wideband antenna", 9,
         bold=True, italic=True)


def introduction(doc) -> None:
    h1(doc, "I", "Introduction")
    para(doc, (
        "A MIMO system uses several antennas at each end of a wireless link. It can carry more data than a "
        "single-antenna link without using more bandwidth or more transmit power [@foschini, telatar]. For this "
        "to work, the antennas must be well matched and must stay independent of each other, so a MIMO antenna is "
        "judged by its port isolation and its envelope correlation coefficient (ECC) as well as by its bandwidth "
        "and gain [@sharawi, blanch]."))
    para(doc, (
        "Wideband systems, such as ultra-wideband (UWB) links in the 3.1–10.6 GHz band [@fcc], need antennas that "
        "stay matched over several gigahertz. Printed planar monopoles are a common choice, because a flat patch "
        "behaves like a thick monopole and gives a very wide impedance bandwidth [@agrawall, ray]. A CPW feed "
        "keeps the feed line and the ground on the same side of the board, which makes the antenna easy to "
        "fabricate [@simons]. The weak point of a printed monopole is its gain. It radiates to the front and to "
        "the back of the board, so about half of the power goes in the unwanted direction [@balanis]."))
    para(doc, (
        "An FSS is a flat periodic array of metal cells that reflects or passes a wave depending on its frequency "
        "[@munk]. Placed behind an antenna, it sends the backward wave to the front and raises the gain. Many "
        "single-port wideband antennas use an FSS in this way [@algburi_review]. Ranga *et al.* used a dual-layer "
        "FSS reflector behind a UWB antenna [@ranga]. Kundu *et al.* added two FSS layers to a printed UWB antenna "
        "and reached a peak gain of 8.7 dBi [@kundu]. With single-layer FSS reflectors, peak gains of 11.5 dBi "
        "[@algburi2022], 10.5 dBi [@hussain2023] and 8.4 dBi [@hammache2024] have been reported for CPW-fed "
        "monopoles. A reflector made of split-ring cells was used behind a UWB monopole in [@sen2017]."))
    para(doc, (
        "Fewer works combine a periodic surface with a MIMO antenna. A four-port antenna over a metasurface of "
        "split-ring cells reached 8.3 dBi with more than 15.5 dB isolation in [@hasan2022], and a two-port UWB "
        "antenna with FSS layers was reported in [@ushadevi]. This paper follows the design in two steps. First, "
        "a single CPW-fed decagonal antenna is designed and its result is given. Then four such elements are "
        "arranged as a MIMO antenna and placed over an FSS made of concentric split rings, and the result is "
        "compared with that of the single antenna. Section II describes the structures, Section III gives and "
        "compares the simulated results, and Section IV concludes the paper."))


def design(doc) -> None:
    h1(doc, "II", "Antenna Design")
    h2(doc, "A", "Single Antenna")
    para(doc, (
        "The single antenna is shown in Fig. 1. It is printed in copper on one face of a 50 × 50 × 1.6 mm FR-4 "
        "board (ε_{r} = 4.3). The radiator is a ten-sided (decagonal) patch of circumradius R = 15 mm. It is fed "
        "by a CPW line with a 3.0 mm signal strip and 0.5 mm slots, and a rectangular ground lies on each side of "
        "the strip. The top edge of the ground stops 0.73 mm below the patch. This small gap was chosen by "
        "sweeping the ground position and the patch radius, because it controls the match at the low end of the "
        "band. The dimensions are listed in Table I."))
    figure(doc, 1, "05_single_antenna.png", "Single CPW-fed decagonal antenna (copper pattern, CST).", 2.4, None,
           CENTER)
    h2(doc, "B", "Four-Port MIMO Antenna")
    para(doc, (
        "Fig. 2 shows the four-port MIMO antenna. It uses four elements of the same kind as the single antenna, "
        "arranged in two rows and two columns. «TO BE CONFIRMED: patch and feed dimensions equal to those of the "
        "single antenna.» The two upper elements are fed from the top edge of the board and the two lower "
        "elements from the bottom edge, so the upper pair is a mirror image of the lower pair and the four "
        "patches face each other at the middle of the board. The upper and lower halves are shifted sideways by "
        "a small amount, which gives the board a stepped outline. «Board size, element spacing and port "
        "numbering: TO BE ADDED.»"))
    figure(doc, 2, "02_mimo_4port.webp", "Four-port MIMO antenna with decagonal patches and CPW-style feeds "
           "(top view, CST).", 3.3, CROP_BOARD, CENTER)
    h2(doc, "C", "FSS Unit Cell and Array")
    para(doc, (
        "The FSS is shown in Fig. 3. Its unit cell has two concentric metal rings, and each ring is cut by a "
        "narrow split. The cell is repeated in 6 columns and 5 rows, which gives 30 cells on one board. A split "
        "ring acts as a resonant circuit: the metal ring gives an inductance L, and the split and the gap between "
        "the two rings give a capacitance C. The cell resonates at"))
    equation(doc, [sub("f", "0"), up(" = "), dh.mf([up("1")], [up("2π"), dh.mrad(dh.mr("L"), dh.mr("C"))])], 1)
    para(doc, (
        "Near this frequency the surface reflects most of the wave that falls on it [@munk]. Two rings of "
        "different size resonate at two different frequencies, which widens the range over which the surface "
        "reflects. «Unit-cell simulation (reflection and transmission of the FSS, and its reflection phase): "
        "TO BE ADDED.»"))
    figure_pair(doc, 3, png("01_fss_array.webp", CROP_CELL, 4), 1.0, png("01_fss_array.webp", CROP_BOARD), 2.15,
                "FSS: (a) unit cell with two concentric split rings, (b) 6 × 5 array (top view, CST).")
    h2(doc, "D", "MIMO Antenna over the FSS")
    para(doc, (
        "In the combined structure of Fig. 4, the MIMO antenna is placed over the FSS, so the FSS lies behind "
        "all four elements. The two boards have nearly the same footprint. The wave that the antenna radiates "
        "backwards travels across the gap h, is reflected by the FSS and returns to the antenna. It adds to the "
        "forward wave when [@hussain2023]"))
    equation(doc, [sub("φ", "FSS"), up(" − 2"), sub("k", "0"), dh.mr("h"), up(" = 2"), dh.mr("n"), up("π,   "),
                   dh.mr("n"), up(" = 0, 1, 2, …")], 2)
    para(doc, (
        "where φ_{FSS} is the reflection phase of the FSS and k_{0} is the free-space wavenumber. The gap "
        "h therefore decides at which frequencies the FSS helps. «Gap h between the antenna and the FSS: "
        "TO BE ADDED.»"))
    figure(doc, 4, "03_mimo_4port_over_fss.webp", "Four-port MIMO antenna placed over the FSS (top view, CST).",
           3.3, CROP_BOARD, CENTER)
    table(doc, 1, "Dimensions of the Structures", [
        ["Part", "Parameter", "Value (mm)"],
        ["Single antenna", "FR-4 board, length × width × thickness", "50 × 50 × 1.6"],
        ["Single antenna", "Decagon circumradius R", "15"],
        ["Single antenna", "CPW strip width; slot width", "3.0; 0.5"],
        ["Single antenna", "Ground length (along the feed)", "18"],
        ["Single antenna", "Gap between ground and patch", "0.73"],
        ["MIMO antenna", "Board length × width", TBA],
        ["MIMO antenna", "Spacing between elements", TBA],
        ["FSS cell", "Outer and inner ring radii", TBA],
        ["FSS cell", "Ring width and split width", TBA],
        ["FSS", "Cell period; board size; substrate", TBA],
        ["Stack", "Gap h, antenna to FSS", TBA],
    ], [0.8, 1.75, 0.95])


def s11_figure(doc) -> None:
    """Fig. 5 across both columns, so the CST axis labels stay readable: the two S11 plots, one above the other."""
    new_section(doc, 1)
    doc.add_picture(png("06_single_s11.png", CROP_S11_SINGLE), width=Inches(6.6))
    fmt(doc.paragraphs[-1], CENTER, before=4, keep=True)
    runs(fmt(doc.add_paragraph(), CENTER, after=2, keep=True), "(a)", SMALL)
    doc.add_picture(png("04_s11.png"), width=Inches(6.6))
    fmt(doc.paragraphs[-1], CENTER, keep=True)
    runs(fmt(doc.add_paragraph(), CENTER, keep=True), "(b)", SMALL)
    caption(doc, 5, "Simulated reflection coefficient S_{11} (CST): (a) single antenna, 0–18 GHz; (b) port 1 of the "
            "four-port MIMO antenna, 1–15 GHz. «TO BE CONFIRMED: (b) is taken here as the MIMO antenna with the "
            "FSS.»", CENTER)
    new_section(doc, 2)


def comparison_plot() -> io.BytesIO:
    """Fig. 6: the two S11 curves on the same axes, drawn from their digitised copies."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                         "mathtext.fontset": "stix", "font.size": 8, "axes.linewidth": 0.6})
    fig, ax = plt.subplots(figsize=(3.45, 2.3))
    ax.axhline(-10, color="#52514e", lw=0.7, ls=(0, (4, 2)))
    ax.plot(FS, SS, color="#eb6834", lw=1.2, ls=(0, (5, 2)), label="Single antenna")
    ax.plot(F, S, color="#2a78d6", lw=1.4, label="Four-port MIMO with FSS (port 1)")
    ax.set_xlim(0, 18)
    ax.set_ylim(-40, 0)
    ax.set_xticks(range(0, 19, 2))
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("$S_{11}$ (dB)")
    ax.grid(True, color="#d9d8d4", lw=0.5)
    ax.set_axisbelow(True)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=1, frameon=False, fontsize=7.5, handlelength=2.6)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    (HERE / "figures").mkdir(exist_ok=True)
    (HERE / "figures" / "fig6_s11_comparison.png").write_bytes(buf.getvalue())
    buf.seek(0)
    return buf


def results(doc) -> None:
    h1(doc, "III", "Results and Discussion")
    h2(doc, "A", "Single Antenna")
    res = lit.THIS_WORK["resonances"]
    res_txt = ", ".join(f"{n(f0)} GHz ({n(s0, 1)} dB)" for f0, s0 in res[:-1])
    res_txt += f" and {n(res[-1][0])} GHz ({n(res[-1][1], 1)} dB)"
    para(doc, (
        "The single antenna was simulated in CST Studio Suite from 0 to 18 GHz. Its reflection coefficient is "
        "shown in Fig. 5(a). An antenna is taken as matched where S_{11} is below −10 dB, which means that less "
        f"than 10 % of the input power is reflected. S_{{11}} is below −10 dB from {n(S_LO)} to {n(S_HI)} GHz, a "
        f"single band {n(S_HI - S_LO, 1)} GHz wide with a fractional bandwidth of {n(fbw(S_LO, S_HI), 0)} %. "
        f"The resonances are at {res_txt}. The match is weakest near {n(S_WEAK1[0], 1)} GHz "
        f"({n(S_WEAK1[1], 1)} dB) and near {n(S_WEAK2[0], 1)} GHz ({n(S_WEAK2[1], 1)} dB), where the curve only "
        "just stays below the limit. The simulated gain of the single antenna is about "
        f"{lit.THIS_WORK['gain_ieee_uwb'].replace('≈ ', '')} dBi over 3.1–10.6 GHz."))
    h2(doc, "B", "MIMO Antenna with FSS")
    others = [fd for fd, _ in DIPS if abs(fd - F_MIN) > 0.05]
    dip_txt = ", ".join(n(fd) for fd in others[:-1]) + f" and {n(others[-1])} GHz"
    para(doc, (
        "The MIMO antenna was simulated from 1 to 15 GHz. Fig. 5(b) shows the reflection coefficient at port 1. "
        f"S_{{11}} falls below −10 dB at {n(B1_LO)} GHz and stays below it up to {n(B1_HI)} GHz, a fractional "
        f"bandwidth of {n(fbw(B1_LO, B1_HI), 0)} %. From {n(B1_HI)} to {n(B2_LO)} GHz the curve rises slightly "
        f"above the limit and reaches {n(GAP_S, 1)} dB at {n(GAP_F)} GHz. From {n(B2_LO)} GHz it is below −10 dB "
        f"again up to {n(F_STOP, 0)} GHz, the end of the simulated range, so the upper edge of this second band "
        "is not known yet."))
    para(doc, (
        f"The deepest resonance is {n(S_MIN, 1)} dB at {n(F_MIN)} GHz. Other resonances deeper than −20 dB are at "
        f"{dip_txt}. The match is best from {n(GOOD_LO, 1)} to {n(GOOD_HI, 1)} GHz, where S_{{11}} stays below "
        f"−20 dB. Above 10.5 GHz it stays between {n(HIGH_S, 1)} and {n(HIGH_MIN, 1)} dB."))
    h2(doc, "C", "Comparison of the Two Results")
    para(doc, (
        "Fig. 6 draws the two curves on the same axes, and Table II lists the main values side by side. Three "
        f"changes can be seen. First, the lower band edge moves down from {n(S_LO)} to {n(B1_LO)} GHz, so the "
        f"MIMO antenna with the FSS is matched {n(S_LO - B1_LO)} GHz lower than the single antenna. Second, the "
        f"best match moves to the middle of the band. The single antenna has its deepest resonance at "
        f"{n(res[0][0])} GHz and is only just matched near {n(S_WEAK1[0], 1)} GHz, while the MIMO antenna with the "
        f"FSS stays below −20 dB from {n(GOOD_LO, 1)} to {n(GOOD_HI, 1)} GHz. Third, the single antenna is matched "
        f"over one continuous band, but the MIMO antenna with the FSS rises to {n(GAP_S, 1)} dB at {n(GAP_F)} GHz, "
        "which splits its matched range into two bands. A small change of the feed gap or of the gap h could be "
        "tried to remove this rise."))
    doc.add_picture(comparison_plot(), width=Inches(3.4))
    fmt(doc.paragraphs[-1], CENTER, before=4, keep=True)
    caption(doc, 6, "S_{11} of the single antenna and of the four-port MIMO antenna with the FSS on the same axes "
            "(curves read from the CST plots of Fig. 5).")
    para(doc, (
        "This comparison has a limit. The two models differ in two ways at once, because the MIMO antenna has "
        "three more elements and also the FSS behind it. The changes above cannot yet be assigned to one cause. "
        "«S_{11} of the MIMO antenna without the FSS: TO BE ADDED.»"))
    table(doc, 2, "Single Antenna and MIMO Antenna with FSS (Simulated)", [
        ["Quantity", "Single antenna", "MIMO with FSS (port 1)"],
        ["Simulated range (GHz)", "0–18", f"1–{n(F_STOP, 0)}"],
        ["S_{11} < −10 dB (GHz)", f"{n(S_LO)}–{n(S_HI)}",
         f"{n(B1_LO)}–{n(B1_HI)} and {n(B2_LO)}–{n(F_STOP, 0)}^{{†}}"],
        ["Fractional bandwidth (%)", n(fbw(S_LO, S_HI), 0),
         f"{n(fbw(B1_LO, B1_HI), 0)} and ≥ {n(fbw(B2_LO, F_STOP), 0)}"],
        ["Lower band edge (GHz)", n(S_LO), n(B1_LO)],
        ["Deepest resonance", f"{n(res[0][1], 1)} dB at {n(res[0][0])} GHz", f"{n(S_MIN, 1)} dB at {n(F_MIN)} GHz"],
        ["Weakest point in the matched range", f"{n(S_WEAK1[1], 1)} dB near {n(S_WEAK1[0], 1)} GHz",
         f"{n(GAP_S, 1)} dB at {n(GAP_F)} GHz"],
        ["Gain, 3.1–10.6 GHz (dBi)", lit.THIS_WORK["gain_ieee_uwb"].replace("≈ ", ""), TBA],
        ["Isolation; ECC", "not applicable", TBA],
    ], [1.2, 1.0, 1.3], note="^{†}End of the simulated range; the upper edge of this band is not known.")
    h2(doc, "D", "Results to Be Added")
    para(doc, (
        "The reflection coefficient at one port is the only result of the MIMO antenna available at present. The "
        "following results are needed to complete the paper and are not reported here: «(i) S_{11} of the MIMO "
        "antenna without the FSS; (ii) reflection coefficients at ports 2, 3 and 4; (iii) isolation between the "
        "ports (S_{21}, S_{31}, S_{41}); (iv) gain and efficiency against frequency, with and without the FSS; "
        "(v) ECC and diversity gain; (vi) radiation patterns: TO BE ADDED.» Figs. 7–9 keep the place of the main "
        "missing plots. The ECC can be computed from the S-parameters with the method of [@blanch] or from the "
        "far-field patterns [@sharawi]."))
    placeholder_figure(doc, 7, "CST S-parameters of all four ports, 1–15 GHz",
                       "Reflection coefficients of ports 2–4 and isolation between the ports.", 0.95)
    placeholder_figure(doc, 8, "CST realized gain (and efficiency) against frequency",
                       "Gain of the MIMO antenna with and without the FSS.", 0.95)
    placeholder_figure(doc, 9, "CST far-field cuts in the two principal planes",
                       "Radiation patterns at selected frequencies.", 0.95)
    h2(doc, "E", "Comparison with Reported Work")
    para(doc, (
        "Table III places this work next to reported antennas that use an FSS or a metasurface reflector. The "
        "values of the other works are those given by their authors. The matched range of the present antenna is "
        "wide, but its gain and isolation must be added before a fair comparison can be made."))
    table(doc, 3, "Comparison with Reported Antennas", [
        ["Ref.", "Ports", "Reflector", "Band (GHz)", "Peak gain (dBi)", "Isolation (dB)"],
        ["[@algburi2022]", "1", "19 × 19 FSS", "2.2–11.9", "11.3", "—"],
        ["[@hussain2023]", "1", "5 × 5 FSS", "3–18", "10.5", "—"],
        ["[@hasan2022]", "4", "10 × 10 split-ring metasurface", "3.08–7.75", "8.3", "> 15.5"],
        ["This work", "4", "6 × 5 split-ring FSS", f"{n(B1_LO)}–{n(B1_HI)}, {n(B2_LO)}–{n(F_STOP, 0)}", TBA, TBA],
    ], [0.45, 0.38, 0.85, 0.7, 0.56, 0.56], first_col_left=False,
        note="—: single-port antenna. Values of the other works are peak gains reported by their authors.")


def conclusion(doc) -> None:
    h1(doc, "IV", "Conclusion")
    para(doc, (
        "A single CPW-fed decagonal antenna on FR-4 was designed first. In simulation it is matched "
        f"(S_{{11}} below −10 dB) from {n(S_LO)} to {n(S_HI)} GHz. Four such elements were then arranged as a "
        "four-port MIMO antenna and placed over an FSS made of a 6 × 5 array of concentric split rings. The "
        f"simulated reflection coefficient at port 1 of this structure is below −10 dB from {n(B1_LO)} to "
        f"{n(B1_HI)} GHz and from {n(B2_LO)} to {n(F_STOP, 0)} GHz, with a short rise to {n(GAP_S, 1)} dB at "
        f"{n(GAP_F)} GHz between them. Compared with the single antenna, the lower band edge moves down by "
        f"{n(S_LO - B1_LO)} GHz and the best match moves to {n(GOOD_LO, 1)}–{n(GOOD_HI, 1)} GHz, but the matched "
        "range is no longer one continuous band. The remaining dimensions, the result of the MIMO antenna "
        "without the FSS, the isolation between the ports, the gain, the ECC and the radiation patterns are "
        "still to be added, and they will show how much the FSS improves the antenna. Fabrication and "
        "measurement of the antenna are planned as the next step."))


def reference_list(doc) -> None:
    small_caps_line(doc, "References", BODY, 8, 4)
    for num, key in enumerate(CITE.order, 1):
        p = fmt(doc.add_paragraph(), JUSTIFY, after=1)
        pf = p.paragraph_format
        pf.left_indent, pf.first_line_indent = Inches(0.3), Inches(-0.3)
        pf.tab_stops.add_tab_stop(Inches(0.3))
        dh.add_runs(p, f"[{num}]\t{ref_lookup(key)}", SMALL)


def build() -> Path:
    doc = Document()
    setup(doc)
    front_matter(doc)
    new_section(doc, 2)
    abstract(doc)
    introduction(doc)
    design(doc)
    s11_figure(doc)
    results(doc)
    conclusion(doc)
    reference_list(doc)
    new_section(doc, 2)            # a trailing continuous break balances the columns of the last page
    doc.core_properties.title = TITLE
    doc.core_properties.author = ", ".join(name for name, _ in lit.PROJECT["students"])
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    out = build()
    built = Document(str(out))
    text = "\n".join([p.text for p in built.paragraphs] + [c.text for t in built.tables for r in t.rows for c in r.cells])
    print(f"Generated {out.relative_to(ROOT)}: {len(CITE.order)} references, "
          f"{len(re.findall('TO BE ADDED', text))} 'TO BE ADDED' and {len(re.findall('TO BE CONFIRMED', text))} "
          f"'TO BE CONFIRMED' placeholders")
    print(f"  S11 < -10 dB: {B1_LO:.2f}-{B1_HI:.2f} GHz and {B2_LO:.2f}-{F_STOP:.0f} GHz; "
          f"{GAP_S:.1f} dB at {GAP_F:.2f} GHz between; deepest {S_MIN:.1f} dB at {F_MIN:.2f} GHz")
    print("  dips below -20 dB:", ", ".join(f"{a:.2f} GHz ({b:.1f} dB)" for a, b in DIPS))
    pdf = render_pdf(out)
    if pdf:
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", info)
        print(f"Rendered {pdf.relative_to(ROOT)}: {m.group(1) if m else '?'} pages")
    else:
        print("LibreOffice (soffice) not found: open the .docx in Word and export it to PDF.")
