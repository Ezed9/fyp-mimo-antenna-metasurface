"""python-docx helpers that reproduce the college report template's formatting.

report/UG_Project_Report_Template.docx formats everything at run level: Times New Roman, 12 pt body text, "Heading 1"
paragraphs with 12 pt Times New Roman runs, US Letter, 1" top/bottom and 1.25" left/right margins. These helpers write
new content the same way, so every generated document keeps the template's look.

Text mini-markup: **bold**, *italic*, _{subscript}, ^{superscript}; citations [@key] or [@key1, key2].
"""
from __future__ import annotations

import copy
import re
from collections.abc import Callable
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph

TEMPLATE = Path(__file__).resolve().parent / "UG_Project_Report_Template.docx"
FONT = "Times New Roman"
BODY = 12
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
        if el.tag == qn("w:p") and not "".join(el.itertext()).strip():
            el.getparent().remove(el)
            removed += 1
        el = nxt


def start(first_line: str, title: str, subtitle: str | None, students: list[str],
          supervisors: list[str]) -> DocxDocument:
    """Open the template, fill its title page and remove the placeholder body (the caller adds the content).

    Each extra student/supervisor line replaces one of the template's blank lines, so the page layout is unchanged.
    """
    doc = Document(str(TEMPLATE))
    body = doc.element.body
    inst = _find(doc, "NATIONAL INSTITUTE OF TECHNOLOGY SILCHAR")
    cut = False
    for el in list(body):
        if el is inst._p:
            cut = True
        elif cut and el.tag != qn("w:sectPr"):
            body.remove(el)

    _set_text(doc.paragraphs[0], first_line)
    t = _find(doc, "TITLE OF PROJECT")
    _set_text(t, title.upper())
    if subtitle:
        sub = Paragraph(t._p.getnext(), t._parent)
        _set_text(sub, subtitle)
    for placeholder, lines in (("NAME OF THE STUDENTS", students), ("SUPERVISOR NAME", supervisors)):
        last = _find(doc, placeholder)
        _set_text(last, lines[0])
        for line in lines[1:]:
            last = _clone_after(last, line)
        _drop_empty_after(last, len(lines) - 1)
    return doc


# ----------------------------------------------------------------------------- body blocks
def heading(doc: DocxDocument, text: str, level: int = 1, page_break: bool = False) -> Paragraph:
    p = doc.add_paragraph(style="Heading 1" if level == 1 else "Heading 2")
    _mark_font(p)
    add_runs(p, text, BODY, italic=True if level == 2 else None)
    if page_break:
        p.paragraph_format.page_break_before = True
    return p


def para(doc: DocxDocument, text: str, cite: Citer | None = None, size: float = BODY, align=JUSTIFY,
         space_after: float | None = None, keep_next: bool = False) -> Paragraph:
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    add_runs(p, cite.render(text) if cite else text, size)
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    if keep_next:
        p.paragraph_format.keep_with_next = True
    return p


def bullets(doc: DocxDocument, items: list[str], cite: Citer | None = None, size: float = BODY) -> None:
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.alignment = JUSTIFY
        p.paragraph_format.space_after = Pt(3)
        add_runs(p, cite.render(it) if cite else it, size)


def caption(doc: DocxDocument, label: str, text: str, cite: Citer | None = None, above: bool = False) -> Paragraph:
    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_after = Pt(4 if above else 10)
    p.paragraph_format.keep_with_next = above
    add_runs(p, f"**{label}** " + (cite.render(text) if cite else text), 10)
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
def references(doc: DocxDocument, cite: Citer, size: float = BODY) -> None:
    for n, key in enumerate(cite.order, 1):
        p = doc.add_paragraph()
        p.alignment = JUSTIFY
        pf = p.paragraph_format
        pf.left_indent = Inches(0.45)
        pf.first_line_indent = Inches(-0.45)
        pf.tab_stops.add_tab_stop(Inches(0.45))
        pf.space_after = Pt(4)
        pf.line_spacing = 1.0
        add_runs(p, f"[{n}]\t{cite.lookup(key)}", size)
