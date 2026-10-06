"""python-docx helpers that reproduce the college report template's formatting.

report/UG_Project_Report_Template.docx formats everything at run level: Times New Roman, 12 pt body text, "Heading 1"
paragraphs with 12 pt Times New Roman runs, US Letter, 1" top/bottom and 1.25" left/right margins. These helpers write
new content the same way, so every generated document keeps the template's look.

Text mini-markup: **bold**, *italic*, _{subscript}, ^{superscript}; citations [@key] or [@key1, key2].
"""
from __future__ import annotations

import copy
import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph

TEMPLATE = Path(__file__).resolve().parent / "UG_Project_Report_Template.docx"
FONT = "Times New Roman"
BODY = 10.5
TEXT_W = 6.0  # inches between the template's margins (8.5 − 2 × 1.25)
JUSTIFY = WD_ALIGN_PARAGRAPH.JUSTIFY
CENTER = WD_ALIGN_PARAGRAPH.CENTER


# ----------------------------------------------------------------------------- citations
def format_nums(nums: list[int]) -> str:
    """IEEE style: [1], [3]–[5]."""
    nums = sorted(set(nums))
    out, k = [], 0
    while k < len(nums):
        j = k
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(f"[{nums[k]}]–[{nums[j]}]" if j - k >= 2 else ", ".join(f"[{n}]" for n in nums[k:j + 1]))
        k = j + 1
    return ", ".join(out)


class Citer:
    """Numbers references in order of first citation."""

    def __init__(self, lookup: Callable[[str], str]):
        self.lookup = lookup
        self.order: list[str] = []

    def num(self, key: str) -> int:
        if key not in self.order:
            self.lookup(key)  # KeyError for an unknown key
            self.order.append(key)
        return self.order.index(key) + 1

    def render(self, text: str) -> str:
        def rep(m: re.Match) -> str:
            keys = [k.strip().lstrip("@") for k in m.group(1).split(",")]
            return format_nums([self.num(k) for k in keys])
        return re.sub(r"\[@([^\]]+)\]", rep, text)


# ----------------------------------------------------------------------------- runs
_TOKEN = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|_\{[^}]*\}|\^\{[^}]*\})")


def style_run(run, size: float = BODY, bold: bool | None = None, italic: bool | None = None,
              sub: bool = False, sup: bool = False) -> None:
    f = run.font
    f.name = FONT
    rpr = run._r.get_or_add_rPr()
    rpr.find(qn("w:rFonts")).set(qn("w:cs"), FONT)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    f.size = Pt(size)
    szcs = OxmlElement("w:szCs")  # complex-script size, as in the template; must follow w:sz
    szcs.set(qn("w:val"), str(int(size * 2)))
    rpr.find(qn("w:sz")).addnext(szcs)
    if sub:
        f.subscript = True
    if sup:
        f.superscript = True


def add_runs(p: Paragraph, text: str, size: float = BODY, bold: bool | None = None,
             italic: bool | None = None) -> None:
    for tok in _TOKEN.split(text):
        if not tok:
            continue
        if tok.startswith("**"):
            add_runs(p, tok[2:-2], size, True, italic)
        elif tok.startswith("_{"):
            style_run(p.add_run(tok[2:-1]), size, bold, italic, sub=True)
        elif tok.startswith("^{"):
            style_run(p.add_run(tok[2:-1]), size, bold, italic, sup=True)
        elif tok.startswith("*") and len(tok) > 2:
            add_runs(p, tok[1:-1], size, bold, True)
        else:
            style_run(p.add_run(tok), size, bold, italic)


def _mark_font(p: Paragraph, size: float = BODY) -> None:
    """Paragraph-mark formatting, as the template sets it on its own paragraphs."""
    ppr = p._p.get_or_add_pPr()
    rpr = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(a), FONT)
    sz, szcs = OxmlElement("w:sz"), OxmlElement("w:szCs")
    sz.set(qn("w:val"), str(int(size * 2)))
    szcs.set(qn("w:val"), str(int(size * 2)))
    for el in (rf, sz, szcs):
        rpr.append(el)
    ppr.append(rpr)


# ----------------------------------------------------------------------------- template title page
def el_text(el) -> str:
    """Visible text of a body element (lxml's itertext() repeats text on python-docx elements)."""
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def _find(doc: DocxDocument, startswith: str) -> Paragraph:
    return next(p for p in doc.paragraphs if p.text.strip().startswith(startswith))


def _set_text(p: Paragraph, text: str) -> None:
    runs = p.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]:
            r._r.getparent().remove(r._r)
        return
    r = p.add_run(text)
    mark = p._p.pPr.find(qn("w:rPr")) if p._p.pPr is not None else None
    if mark is not None:
        r._r.insert(0, copy.deepcopy(mark))


def _clone_after(p: Paragraph, text: str) -> Paragraph:
    el = copy.deepcopy(p._p)
    p._p.addnext(el)
    new = Paragraph(el, p._parent)
    _set_text(new, text)
    return new


def _drop_empty_after(p: Paragraph, n: int) -> None:
    el, removed = p._p.getnext(), 0
    while el is not None and removed < n:
        nxt = el.getnext()
        if el.tag == qn("w:p") and not el_text(el).strip():
            el.getparent().remove(el)
            removed += 1
        el = nxt


def start(first_line: str, title: str, subtitle: str | None, students: list[str],
          supervisors: list[str], logo_path: Path | None = None, keep_body: bool = False) -> DocxDocument:
    """Open the template and fill its title page with college logo and balanced layout."""
    doc = Document(str(TEMPLATE))

    # Clean body if keep_body=False
    if not keep_body:
        body = doc.element.body
        inst = _find(doc, "NATIONAL INSTITUTE OF TECHNOLOGY SILCHAR")
        el = inst._p.getnext()
        while el is not None and el.tag != qn("w:sectPr"):
            nxt = el.getnext()
            body.remove(el)
            el = nxt

    p0 = doc.paragraphs[0]
    _set_text(p0, first_line)
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(24)

    t = _find(doc, "TITLE OF PROJECT")
    _set_text(t, title.upper())
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.paragraph_format.space_before = Pt(12)
    t.paragraph_format.space_after = Pt(6)
    for r in t.runs:
        style_run(r, size=15, bold=True)

    prev_el = t
    if subtitle:
        sub = Paragraph(t._p.getnext(), t._parent)
        _set_text(sub, subtitle)
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub.paragraph_format.space_after = Pt(16)
        for r in sub.runs:
            style_run(r, size=11, italic=True)
        prev_el = sub

    # Insert College Logo centered between Title/Subtitle and 'Submitted by:'
    if logo_path and Path(logo_path).exists():
        logo_p = _clone_after(prev_el, "")
        logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        logo_p.paragraph_format.space_before = Pt(12)
        logo_p.paragraph_format.space_after = Pt(20)
        for r in list(logo_p.runs):
            r._r.getparent().remove(r._r)
        r = logo_p.add_run()
        r.add_picture(str(logo_path), width=Inches(1.35))

    sub_by = _find(doc, "Submitted by:")
    sub_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_by.paragraph_format.space_before = Pt(0)
    sub_by.paragraph_format.space_after = Pt(6)
    for r in sub_by.runs:
        style_run(r, size=10.5)

    last_st = _find(doc, "NAME OF THE STUDENTS")
    _set_text(last_st, students[0])
    last_st.alignment = WD_ALIGN_PARAGRAPH.CENTER
    last_st.paragraph_format.space_after = Pt(3)
    for r in last_st.runs:
        style_run(r, size=10.5, bold=True)
    for line in students[1:]:
        last_st = _clone_after(last_st, line)
        last_st.alignment = WD_ALIGN_PARAGRAPH.CENTER
        last_st.paragraph_format.space_after = Pt(3)
        for r in last_st.runs:
            style_run(r, size=10.5, bold=True)
    last_st.paragraph_format.space_after = Pt(20)

    sup_hdr = _find(doc, "SUPERVISOR NAME")
    _set_text(sup_hdr, "Under the Guidance of")
    sup_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sup_hdr.paragraph_format.space_before = Pt(0)
    sup_hdr.paragraph_format.space_after = Pt(6)
    for r in sup_hdr.runs:
        style_run(r, size=10.5, italic=True)
    last_sup = sup_hdr
    for line in supervisors:
        last_sup = _clone_after(last_sup, line)
        last_sup.alignment = WD_ALIGN_PARAGRAPH.CENTER
        last_sup.paragraph_format.space_after = Pt(3)
        for r in last_sup.runs:
            style_run(r, size=10.5, bold=True)
    last_sup.paragraph_format.space_after = Pt(28)

    # Remove SUPERVISOR'S SIGNATURE placeholder
    try:
        sig = _find(doc, "SUPERVISOR’S SIGNATURE")
        sig._p.getparent().remove(sig._p)
    except StopIteration:
        pass

    dept = _find(doc, "DEPARTMENT OF ELECTRONICS")
    dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    dept.paragraph_format.space_before = Pt(0)
    dept.paragraph_format.space_after = Pt(4)
    for r in dept.runs:
        style_run(r, size=10.5, bold=True)

    inst = _find(doc, "NATIONAL INSTITUTE OF TECHNOLOGY SILCHAR")
    inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    inst.paragraph_format.space_before = Pt(0)
    inst.paragraph_format.space_after = Pt(0)
    inst.paragraph_format.line_spacing = 1.2
    _set_text(inst, "NATIONAL INSTITUTE OF TECHNOLOGY SILCHAR, ASSAM (INDIA)-788010\nOCTOBER 2026")
    for r in inst.runs:
        style_run(r, size=10.5, bold=True)

    # Remove unused empty paragraphs on the title page
    p = doc.paragraphs[0]._p.getnext()
    while p is not None and p != inst._p:
        nxt = p.getnext()
        if p.tag == qn("w:p") and not el_text(p).strip() and not p.findall(".//" + qn("w:drawing")):
            p.getparent().remove(p)
        p = nxt

    return doc


# ----------------------------------------------------------------------------- body blocks
def heading(doc: DocxDocument, text: str, level: int = 1, page_break: bool = False) -> Paragraph:
    p = doc.add_paragraph(style="Heading 1" if level == 1 else "Heading 2")
    _mark_font(p, 12 if level == 1 else 11)
    add_runs(p, text, 12 if level == 1 else 11, italic=True if level == 2 else None, bold=True)
    p.paragraph_format.space_before = Pt(3.5 if level == 2 else 6)
    p.paragraph_format.space_after = Pt(1.5 if level == 2 else 2)
    p.paragraph_format.keep_with_next = True
    if page_break:
        p.paragraph_format.page_break_before = True
    return p


def para(doc: DocxDocument, text: str, cite: Citer | None = None, size: float = BODY, align=JUSTIFY,
         space_after: float | None = 2.0, keep_next: bool = False) -> Paragraph:
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    add_runs(p, cite.render(text) if cite else text, size)
    p.paragraph_format.space_after = Pt(2.0 if space_after is None else space_after)
    p.paragraph_format.line_spacing = 1.12
    if keep_next:
        p.paragraph_format.keep_with_next = True
    return p


def bullets(doc: DocxDocument, items: list[str], cite: Citer | None = None, size: float = BODY) -> None:
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.alignment = JUSTIFY
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.line_spacing = 1.12
        add_runs(p, cite.render(it) if cite else it, size)


def caption(doc: DocxDocument, label: str, text: str, cite: Citer | None = None, above: bool = False) -> Paragraph:
    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3 if above else 4)
    p.paragraph_format.keep_with_next = above
    add_runs(p, f"**{label}** " + (cite.render(text) if cite else text), 9.0)
    return p


def _shade(cell, fill_hex: str) -> None:
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    cell._tc.get_or_add_tcPr().append(shd)


def table(doc: DocxDocument, header: list[str], rows: list[list[str]], widths: list[float], size: float = 9,
          cite: Citer | None = None, highlight_last: bool = False) -> None:
    assert abs(sum(widths) - TEXT_W) < 0.02 or sum(widths) < TEXT_W, "table wider than the text block"
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.style = doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for j, w in enumerate(widths):
        t.columns[j].width = Inches(w)
    for i, row in enumerate([header] + rows):
        tr = t.rows[i]._tr
        if i == 0:
            hdr = OxmlElement("w:tblHeader")
            tr.get_or_add_trPr().append(hdr)
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.width = Inches(widths[j])
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else CENTER
            pf = p.paragraph_format
            pf.space_after = Pt(0)
            pf.line_spacing = 1.0
            add_runs(p, cite.render(val) if cite else val, size, bold=True if i == 0 else None)
            if i == 0:
                _shade(c, "D9D9D9")
            elif highlight_last and i == len(rows):
                _shade(c, "DCE6F2")
    after = doc.add_paragraph()
    after.paragraph_format.space_after = Pt(2)


def figure(doc: DocxDocument, path: Path, width: float, label: str, text: str, cite: Citer | None = None) -> None:
    doc.add_picture(str(path), width=Inches(width))
    pic = doc.paragraphs[-1]
    pic.alignment = CENTER
    pic.paragraph_format.keep_with_next = True
    pic.paragraph_format.space_after = Pt(2)
    caption(doc, label, text, cite)


# ----------------------------------------------------------------------------- equations (Office Math)
def _m(tag: str):
    return OxmlElement(f"m:{tag}")


def _wrap(tag: str, *children):
    e = _m(tag)
    for c in children:
        e.append(c)
    return e


def mr(text: str, italic: bool = True):
    """Math run; italic for variables, upright for numbers, units and operators."""
    r = _m("r")
    if not italic:
        rpr, sty = _m("rPr"), _m("sty")
        sty.set(qn("m:val"), "p")
        rpr.append(sty)
        r.append(rpr)
    t = _m("t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    return r


def mf(num: list, den: list):
    return _wrap("f", _wrap("num", *num), _wrap("den", *den))


def mrad(*content):
    pr, hide = _m("radPr"), _m("degHide")
    hide.set(qn("m:val"), "1")
    pr.append(hide)
    return _wrap("rad", pr, _m("deg"), _wrap("e", *content))


def md(content: list, beg: str = "(", end: str = ")"):
    """Delimiters that grow with their content: (…) by default, |…| for magnitudes."""
    pr = _m("dPr")
    for tag, ch in (("begChr", beg), ("endChr", end)):
        e = _m(tag)
        e.set(qn("m:val"), ch)
        pr.append(e)
    return _wrap("d", pr, _wrap("e", *content))


def msup(base: list, sup: list):
    return _wrap("sSup", _wrap("e", *base), _wrap("sup", *sup))


def msub(base: list, sub: list):
    return _wrap("sSub", _wrap("e", *base), _wrap("sub", *sub))


def equation(doc: DocxDocument, nodes: list, number: int) -> Paragraph:
    """Centred equation with its number right-aligned, e.g. (1)."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.tab_stops.add_tab_stop(Inches(TEXT_W / 2), WD_TAB_ALIGNMENT.CENTER)
    pf.tab_stops.add_tab_stop(Inches(TEXT_W), WD_TAB_ALIGNMENT.RIGHT)
    style_run(p.add_run("\t"))
    p._p.append(_wrap("oMath", *nodes))
    style_run(p.add_run(f"\t({number})"))
    return p


# ----------------------------------------------------------------------------- references
def references(doc: DocxDocument, cite: Citer, size: float = 8.5) -> None:
    for n, key in enumerate(cite.order, 1):
        p = doc.add_paragraph()
        p.alignment = JUSTIFY
        pf = p.paragraph_format
        pf.left_indent = Inches(0.35)
        pf.first_line_indent = Inches(-0.35)
        pf.tab_stops.add_tab_stop(Inches(0.35))
        pf.space_after = Pt(1.5)
        pf.line_spacing = 1.0
        add_runs(p, f"[{n}]\t{cite.lookup(key)}", size)


# ----------------------------------------------------------------------------- fields, numbered captions, front matter
def field(p: Paragraph, instr: str, cached: str = "", size: float = BODY, bold: bool | None = None) -> None:
    """Complex field (begin, instruction, separate, cached result, end) inside one paragraph."""
    for kind in ("begin", "instr", "separate", "text", "end"):
        if kind == "text" and not cached:
            continue
        r = p.add_run(cached if kind == "text" else None)
        style_run(r, size, bold)
        if kind == "instr":
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = f" {instr} "
            r._r.append(it)
        elif kind != "text":
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            r._r.append(fc)


def seq_caption(doc: DocxDocument, kind: str, n: int, text: str, cite: Citer | None = None,
                above: bool = False) -> Paragraph:
    """'Fig. 3. ...' or 'Table 2. ...' with a SEQ field, so Word can rebuild the lists of figures and tables."""
    p = doc.add_paragraph()
    p.alignment = CENTER
    pf = p.paragraph_format
    pf.space_before = Pt(1)
    pf.space_after = Pt(2 if above else 2)
    pf.keep_with_next = above
    style_run(p.add_run(f"{kind} "), 9.0, True)
    field(p, f"SEQ {'Figure' if kind.startswith('Fig') else 'Table'} \\* ARABIC", str(n), 9.0, True)
    style_run(p.add_run(". "), 9.0, True)
    add_runs(p, cite.render(text) if cite else text, 9.0)
    return p


def image(doc: DocxDocument, path: Path, width: float) -> Paragraph:
    doc.add_picture(str(path), width=Inches(width))
    pic = doc.paragraphs[-1]
    pic.alignment = CENTER
    pic.paragraph_format.keep_with_next = True
    pic.paragraph_format.space_after = Pt(1)
    return pic


def two_images(doc: DocxDocument, path1: Path, path2: Path, width1: float = 2.85,
               width2: float | None = None, width: float | None = None,
               subcap1: str = "(a)", subcap2: str = "(b)") -> None:
    w1 = width if width is not None else width1
    w2 = width if width is not None else (width2 if width2 is not None else width1)
    t = doc.add_table(rows=2, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = t._tbl.tblPr
    tblBorders = OxmlElement("w:tblBorders")
    for b in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement(f"w:{b}")
        border.set(qn("w:val"), "none")
        tblBorders.append(border)
    tblPr.append(tblBorders)

    c0 = t.cell(0, 0)
    p0 = c0.paragraphs[0]
    p0.alignment = CENTER
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(0)
    p0.paragraph_format.keep_with_next = True
    r0 = p0.add_run()
    r0.add_picture(str(path1), width=Inches(w1))

    c1 = t.cell(0, 1)
    p1 = c1.paragraphs[0]
    p1.alignment = CENTER
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(0)
    p1.paragraph_format.keep_with_next = True
    r1 = p1.add_run()
    r1.add_picture(str(path2), width=Inches(w2))

    p0_sub = t.cell(1, 0).paragraphs[0]
    p0_sub.alignment = CENTER
    p0_sub.paragraph_format.space_before = Pt(0)
    p0_sub.paragraph_format.space_after = Pt(0)
    p0_sub.paragraph_format.keep_with_next = True
    add_runs(p0_sub, subcap1, 8.5)

    p1_sub = t.cell(1, 1).paragraphs[0]
    p1_sub.alignment = CENTER
    p1_sub.paragraph_format.space_before = Pt(0)
    p1_sub.paragraph_format.space_after = Pt(0)
    p1_sub.paragraph_format.keep_with_next = True
    add_runs(p1_sub, subcap2, 8.5)


def pending_box(doc: DocxDocument, title: str, detail: str, height: float = 1.6) -> None:
    """Dashed placeholder for a result that does not exist yet (never filled with invented data)."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    c.width = Inches(TEXT_W * 0.8)
    tcpr = c._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        for k, val in (("w:val", "dashed"), ("w:sz", "8"), ("w:color", "808080"), ("w:space", "0")):
            b.set(qn(k), val)
        borders.append(b)
    tcpr.append(borders)
    _shade(c, "F2F2F2")
    tr = t.rows[0]._tr.get_or_add_trPr()
    h = OxmlElement("w:trHeight")
    h.set(qn("w:val"), str(int(height * 1440)))
    h.set(qn("w:hRule"), "atLeast")
    tr.append(h)
    c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p = c.paragraphs[0]
    p.alignment = CENTER
    add_runs(p, f"**{title}**", 11)
    p2 = c.add_paragraph()
    p2.alignment = CENTER
    add_runs(p2, detail, 10, italic=True)
    for q in (p, p2):
        q.paragraph_format.keep_with_next = True


def toc_field(doc: DocxDocument, instr: str, entries: list[tuple[int, str, int | None]]) -> None:
    """A TOC field spanning one paragraph per entry, with a cached result (level, text, page).

    The cached entries make the table correct as soon as the file opens; Word rebuilds it with Update Field.
    """
    entries = entries or [(1, "Right-click here and choose Update Field.", None)]
    for k, (level, text, page) in enumerate(entries):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.tab_stops.add_tab_stop(Inches(TEXT_W), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        pf.left_indent = Inches(0.3 * (level - 1))
        pf.space_after = Pt(4)
        if k == 0:
            for kind in ("begin", "instr", "separate"):
                r = p.add_run()
                if kind == "instr":
                    it = OxmlElement("w:instrText")
                    it.set(qn("xml:space"), "preserve")
                    it.text = f" {instr} "
                    r._r.append(it)
                else:
                    fc = OxmlElement("w:fldChar")
                    fc.set(qn("w:fldCharType"), kind)
                    r._r.append(fc)
        add_runs(p, text, BODY)
        if page is not None:
            style_run(p.add_run(f"\t{page}"))
        if k == len(entries) - 1:
            r = p.add_run()
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), "end")
            r._r.append(fc)


def page_number_footer(doc: DocxDocument) -> None:
    """Centred page number on every page except the title page."""
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True
    sec.footer.is_linked_to_previous = False
    p = sec.footer.paragraphs[0]
    p.alignment = CENTER
    field(p, "PAGE", "1", 11)


@contextmanager
def placed_after(doc: DocxDocument, anchor) -> Iterator[list]:
    """Content added inside the block is moved to just after `anchor`; the yielded list receives the moved elements."""
    body = doc.element.body
    n0 = len(body)  # the last child is w:sectPr; new content is added just before it
    moved: list = []
    yield moved
    moved.extend(list(body)[n0 - 1:-1])
    for el in reversed(moved):
        anchor.addnext(el)
