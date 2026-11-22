"""Minimal IEEE-conference-format .docx writer (python-docx), shared by the two paper build scripts.

Layout mirrors the IEEE conference Word template: US Letter, Times New Roman 10 pt, single-column title block, two-column
body, 8 pt captions/tables/references. Full-width figures are placed with continuous section breaks.

Inline markup understood by every text argument:
    *italic*   **bold**   _{subscript}   ^{superscript}   [[highlighted placeholder]]
Equations are written in LaTeX and converted to native Word equations (OMML) with pandoc.
"""
from __future__ import annotations

import copy
import hashlib
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, Twips
from lxml import etree

FONT = "Times New Roman"
COL_IN = 3.5           # column width: (8.5 − 2·0.625 − 0.25) / 2
PAGE_IN = 7.25         # text width
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_TOKEN = re.compile(r"(\*\*|\*|_\{|\^\{|\}|\[\[|\]\])")
_omml_cache: dict[str, etree._Element] = {}


def latex_to_omml(latex: str) -> etree._Element:
    """LaTeX → <m:oMath> element, through pandoc (cached)."""
    key = hashlib.sha1(latex.encode()).hexdigest()
    if key not in _omml_cache:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "eq.docx"
            subprocess.run(["pandoc", "-f", "markdown", "-t", "docx", "-o", str(out)],
                           input=f"${latex}$\n", text=True, check=True)
            xml = zipfile.ZipFile(out).read("word/document.xml")
        found = etree.fromstring(xml).find(f".//{{{M_NS}}}oMath")
        if found is None:
            raise ValueError(f"pandoc produced no equation for: {latex}")
        _omml_cache[key] = found
    return copy.deepcopy(_omml_cache[key])


class Paper:
    def __init__(self) -> None:
        self.doc = Document()
        normal = self.doc.styles["Normal"]
        normal.font.name = FONT
        normal.font.size = Pt(10)
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        normal.paragraph_format.space_after = Pt(0)
        normal.paragraph_format.space_before = Pt(0)
        normal.paragraph_format.line_spacing = 1.0
        self._page(self.doc.sections[0])
        self._cols(self.doc.sections[0], 2)      # the last section of the document: two columns
        self.fig_no = 0
        self.eq_no = 0
        self.tab_no = 0

    # ---------------------------------------------------------------- page and sections
    @staticmethod
    def _page(section) -> None:
        section.page_width, section.page_height = Inches(8.5), Inches(11)
        section.left_margin = section.right_margin = Inches(0.625)
        section.top_margin, section.bottom_margin = Inches(0.75), Inches(1.0)

    @staticmethod
    def _cols(section, n: int) -> None:
        sect = section._sectPr
        for old in sect.findall(qn("w:cols")):
            sect.remove(old)
        cols = OxmlElement("w:cols")
        if n > 1:
            cols.set(qn("w:num"), str(n))
        cols.set(qn("w:space"), "360")
        sect.append(cols)

    def end_section(self, cols: int) -> None:
        """Close the section written so far as a `cols`-column section; what follows starts a new continuous one."""
        new = self.doc.add_section(WD_SECTION.CONTINUOUS)
        self._page(new)
        self._cols(new, 2)
        self._cols(self.doc.sections[-2], cols)

    # ---------------------------------------------------------------- inline markup
    def runs(self, par, text: str, size: float | None = None, bold: bool = False, italic: bool = False,
             small_caps: bool = False):
        state = {"b": bold, "i": italic, "v": None, "h": False}
        for tok in _TOKEN.split(text):
            if tok == "":
                continue
            if tok == "**":
                state["b"] = not state["b"]
            elif tok == "*":
                state["i"] = not state["i"]
            elif tok == "_{":
                state["v"] = "sub"
            elif tok == "^{":
                state["v"] = "sup"
            elif tok == "}" and state["v"]:
                state["v"] = None
            elif tok == "[[":
                state["h"] = True
            elif tok == "]]":
                state["h"] = False
            else:
                run = par.add_run(tok)
                run.bold = state["b"] or None
                run.italic = state["i"] or None
                if size:
                    run.font.size = Pt(size)
                if small_caps:
                    run.font.small_caps = True
                if state["v"] == "sub":
                    run.font.subscript = True
                elif state["v"] == "sup":
                    run.font.superscript = True
                if state["h"]:
                    run.font.highlight_color = WD_COLOR_INDEX.YELLOW
        return par

    def _par(self, align=None, before: float = 0, after: float = 0, first_indent: bool = False, keep: bool = False):
        par = self.doc.add_paragraph()
        fmt = par.paragraph_format
        fmt.alignment = align
        fmt.space_before, fmt.space_after = Pt(before), Pt(after)
        if first_indent:
            fmt.first_line_indent = Twips(245)
        if keep:
            fmt.keep_with_next = True
        return par

    @staticmethod
    def _fix_widths(table, widths_in: list[float]) -> None:
        """Fixed layout with explicit column widths (python-docx otherwise spreads a table over the full page)."""
        table.autofit = False
        tbl_pr = table._tbl.tblPr
        for old in tbl_pr.findall(qn("w:tblW")):
            tbl_pr.remove(old)
        tbl_pr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="{round(sum(widths_in) * 1440)}" w:type="dxa"/>'))
        for col, width in zip(table._tbl.tblGrid.findall(qn("w:gridCol")), widths_in):
            col.set(qn("w:w"), str(round(width * 1440)))
        for row in table.rows:
            for cell, width in zip(row.cells, widths_in):
                cell.width = Inches(width)

    # ---------------------------------------------------------------- front matter
    def title(self, text: str) -> None:
        self.runs(self._par(WD_ALIGN_PARAGRAPH.CENTER, after=10), text, size=22)

    def authors(self, rows: list[list[tuple[str, ...]]]) -> None:
        """rows: author-block rows; each author is (name, affiliation line 1, line 2, ...)."""
        ncol = max(len(r) for r in rows)
        table = self.doc.add_table(rows=len(rows), cols=ncol)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r, row in enumerate(rows):
            for c, author in enumerate(row):
                cell = table.cell(r, c)
                cell.width = Inches(PAGE_IN / ncol)
                for k, line in enumerate(author):
                    par = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
                    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    if k == len(author) - 1:
                        par.paragraph_format.space_after = Pt(6)
                    self.runs(par, line, size=10.5 if k == 0 else 9, italic=(k == 1))
        self._fix_widths(table, [PAGE_IN / ncol] * ncol)
        self._par()
        self.end_section(1)

    def abstract(self, text: str) -> None:
        par = self._par(WD_ALIGN_PARAGRAPH.JUSTIFY, after=6, first_indent=True)
        self.runs(par, "Abstract", size=9, bold=True, italic=True)
        self.runs(par, "—" + text, size=9, bold=True)

    def keywords(self, text: str) -> None:
        par = self._par(WD_ALIGN_PARAGRAPH.JUSTIFY, after=6, first_indent=True)
        self.runs(par, "Keywords", size=9, bold=True, italic=True)
        self.runs(par, "—" + text, size=9, bold=True, italic=True)

    # ---------------------------------------------------------------- body
    def heading(self, text: str) -> None:
        self.runs(self._par(WD_ALIGN_PARAGRAPH.CENTER, before=8, after=4, keep=True), text, small_caps=True)

    def subheading(self, text: str) -> None:
        self.runs(self._par(before=4, after=2, keep=True), text, italic=True)

    def body(self, text: str) -> None:
        self.runs(self._par(WD_ALIGN_PARAGRAPH.JUSTIFY, first_indent=True), text)

    def equation(self, latex: str) -> int:
        self.eq_no += 1
        par = self._par(before=3, after=3)
        stops = par.paragraph_format.tab_stops
        stops.add_tab_stop(Twips(2520), alignment=1)      # centre
        stops.add_tab_stop(Twips(5040), alignment=2)      # right
        par.add_run("\t")
        par._p.append(latex_to_omml(latex))
        par.add_run(f"\t({self.eq_no})")
        return self.eq_no

    # ---------------------------------------------------------------- figures
    def _picture(self, par, path: Path, width_in: float) -> None:
        par.add_run().add_picture(str(path), width=Inches(width_in))

    def figure(self, images, caption: str, width_in: float = 3.4, sublabels: bool = False,
               side_by_side: bool = False, wide: bool = False) -> int:
        """One figure. `images` is a path or a list of paths. `wide` puts it in its own single-column section.
        `side_by_side` lays the images out in one row (borderless table)."""
        images = [images] if isinstance(images, (str, Path)) else list(images)
        self.fig_no += 1
        if wide:
            self.end_section(2)
        if side_by_side and len(images) > 1:
            table = self.doc.add_table(rows=2 if sublabels else 1, cols=len(images))
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            for c, img in enumerate(images):
                cell = table.cell(0, c)
                cell.width = Inches(width_in + 0.1)
                par = cell.paragraphs[0]
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                par.paragraph_format.keep_with_next = True
                par.paragraph_format.space_before = Pt(4)
                self._picture(par, img, width_in)
                if sublabels:
                    lab = table.cell(1, c)
                    lab.width = Inches(width_in + 0.1)
                    lab.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    lab.paragraphs[0].paragraph_format.keep_with_next = True
                    self.runs(lab.paragraphs[0], f"({chr(97 + c)})", size=8)
            self._fix_widths(table, [width_in + 0.08] * len(images))
        else:
            for k, img in enumerate(images):
                self._picture(self._par(WD_ALIGN_PARAGRAPH.CENTER, before=4, keep=True), img, width_in)
                if sublabels:
                    self.runs(self._par(WD_ALIGN_PARAGRAPH.CENTER, after=2, keep=True), f"({chr(97 + k)})", size=8)
        long = len(caption) > (150 if wide else 60)
        par = self._par(WD_ALIGN_PARAGRAPH.JUSTIFY if long else WD_ALIGN_PARAGRAPH.CENTER, before=2, after=6)
        self.runs(par, f"Fig. {self.fig_no}. {caption}", size=8)
        if wide:
            self.end_section(1)
        return self.fig_no

    # ---------------------------------------------------------------- tables
    def table(self, title: str, rows: list[list[str]], widths_in: list[float], note: str | None = None,
              header_rows: int = 1, bold_first_col: bool = False, wide: bool = False, size: float = 8) -> int:
        self.tab_no += 1
        roman = ["I", "II", "III", "IV", "V", "VI", "VII"][self.tab_no - 1]
        if wide:
            self.end_section(2)
        self.runs(self._par(WD_ALIGN_PARAGRAPH.CENTER, before=6, keep=True), f"TABLE {roman}", size=8)
        self.runs(self._par(WD_ALIGN_PARAGRAPH.CENTER, after=3, keep=True), title, size=8, small_caps=True)
        table = self.doc.add_table(rows=len(rows), cols=len(widths_in))
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        for r, row in enumerate(rows):
            tr_pr = table.rows[r]._tr.get_or_add_trPr()
            tr_pr.append(OxmlElement("w:cantSplit"))
            for c, text in enumerate(row):
                cell = table.cell(r, c)
                cell.width = Inches(widths_in[c])
                cell.vertical_alignment = 1
                margins = parse_xml(f'<w:tcMar {nsdecls("w")}><w:left w:w="50" w:type="dxa"/>'
                                    '<w:right w:w="50" w:type="dxa"/></w:tcMar>')
                cell._tc.get_or_add_tcPr().append(margins)
                lines = text.split("\n")
                for k, line in enumerate(lines):
                    par = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
                    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    if r < len(rows) - 1:
                        par.paragraph_format.keep_with_next = True
                    self.runs(par, line, size=size, bold=(r < header_rows) or (bold_first_col and c == 0))
        self._fix_widths(table, widths_in)
        if note:
            self.runs(self._par(before=2, after=4), note, size=7.5)
        else:
            self._par(after=2)
        if wide:
            self.end_section(1)
        return self.tab_no

    # ---------------------------------------------------------------- back matter
    def references(self, refs: list[str]) -> None:
        self.heading("References")
        for k, ref in enumerate(refs, 1):
            par = self._par(WD_ALIGN_PARAGRAPH.JUSTIFY, after=1)
            fmt = par.paragraph_format
            fmt.left_indent, fmt.first_line_indent = Twips(432), Twips(-432)
            fmt.tab_stops.add_tab_stop(Twips(432))
            self.runs(par, f"[{k}]\t{ref}", size=8)

    def save(self, path: Path) -> None:
        self.doc.save(str(path))
        # Word (through cloud co-editing) has refused archives that carry directory entries; python-docx writes none.
