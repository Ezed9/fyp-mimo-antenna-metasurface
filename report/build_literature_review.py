# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1"]
# ///
"""Build the standalone literature review (college report-template look) and LITERATURE.md.

Run from the repo root:  uv run report/build_literature_review.py
All content comes from report/literature.py; fields not yet extracted from a PDF show up as visible placeholders
and are listed at the end of the run.
"""
from __future__ import annotations

import re
from pathlib import Path

import docx_helpers as dh
import literature as lit
from docx_helpers import mf, mr, mrad, msub

ROOT = Path(__file__).resolve().parent.parent
OUT_DOCX = ROOT / "report" / "Literature_Review.docx"
OUT_MD = ROOT / "LITERATURE.md"
TODO = "[to be completed from the full text]"


def v(x: str | None) -> str:
    return TODO if x is None else x


def cell(x: str | None) -> str:
    return "?" if x is None else x


def paper_text(p: lit.Paper) -> str:
    return (f"**Problem.** {v(p.problem)} **Method.** {v(p.method)} **Results.** {v(p.results)} "
            f"**Relevance.** {v(p.relevance)}")


def single_rows(cite: dh.Citer | None) -> list[list[str]]:
    rows = [[f"[@{p.key}]" if cite else p.short, cell(p.antenna), cell(p.substrate), cell(p.ms), cell(p.placement),
             cell(p.band), cell(p.gain)] for p in lit.SINGLE]
    tw = lit.THIS_WORK
    lo, hi = tw["band_ghz"]
    rows.append(["**This work**", "CPW-fed planar monopole", "see design", f"{tw['metasurface']} (design ongoing)",
                 f"{tw['gap_mm']} mm, air ({tw['gap_mm'] / lit.wavelength_mm(lo):.3f}λ_{{L}})",
                 f"{lo:.2f}–{hi:.2f} (no MS)", "≈ 1.3–5.1 (IEEE gain, no MS) → pending"])
    return rows


SINGLE_HEAD = ["Ref.", "Antenna / feed", "Substrate", "Reflector: unit cell, array", "Gap, backing",
               "Band (GHz)", "Peak gain (dBi): no MS → MS"]
SINGLE_W = [0.55, 0.9, 0.75, 1.1, 0.85, 0.85, 1.0]

MIMO_HEAD = ["Ref.", "Ports, size (mm)", "Band (GHz)", "Metasurface and its role", "Isolation (dB)", "ECC",
             "Peak gain (dBi)"]
MIMO_W = [0.55, 0.95, 0.8, 1.55, 0.7, 0.6, 0.85]


def mimo_rows(cite: dh.Citer | None) -> list[list[str]]:
    return [[f"[@{p.key}]" if cite else p.short, f"{cell(p.ports)}; {cell(p.size)}", cell(p.band),
             f"{cell(p.ms)}; {cell(p.ms_role)}", cell(p.isolation), cell(p.ecc), cell(p.gain)] for p in lit.MIMO]


# ============================================================================= docx
def build_docx() -> Path:
    pj = lit.PROJECT
    doc = dh.start(
        "B. Tech. PROJECT LITERATURE REVIEW (Mid-Semester Evaluation)", pj["title"], pj["phase1"],
        [f"{n.upper()} ({r})" for n, r in pj["students"]],
        [pj["supervisors"][0][0].upper()] + [f"{n.upper()} (CO-GUIDE)" for n, _ in pj["supervisors"][1:]])
    cite = dh.Citer(lit.ref_text)

    dh.heading(doc, "Scope and Search Method", page_break=True)
    for t in lit.SCOPE:
        dh.para(doc, t, cite)

    dh.heading(doc, "Background")
    dh.para(doc, lit.BACKGROUND_UWB, cite)
    dh.para(doc, lit.BACKGROUND_SRR, cite, keep_next=True)
    dh.equation(doc, [msub([mr("f")], [mr("0", False)]), mr(" = ", False),
                      mf([mr("1", False)], [mr("2", False), mr("π"), mrad(mr("L"), mr("C"))])], 1)
    dh.para(doc, lit.BACKGROUND_SRR_AFTER, cite)
    dh.para(doc, lit.BACKGROUND_REFLECTOR, cite, keep_next=True)
    dh.equation(doc, [msub([mr("φ")], [mr("R", False)]), mr("−2", False), msub([mr("k")], [mr("0", False)]),
                      mr("h"), mr("=2", False), mr("n"), mr("π")], 2)
    dh.para(doc, lit.BACKGROUND_REFLECTOR_AFTER, cite)

    dh.heading(doc, "Single Antennas with a Metasurface Reflector")
    for p in lit.SINGLE:
        dh.heading(doc, f"{p.short} {cite.render(f'[@{p.key}]')}", level=2)
        dh.para(doc, paper_text(p), cite)

    dh.heading(doc, "MIMO Antennas with Metasurfaces")
    for p in lit.MIMO:
        dh.heading(doc, f"{p.short} {cite.render(f'[@{p.key}]')}", level=2)
        dh.para(doc, paper_text(p), cite)

    dh.heading(doc, "Comparison", page_break=True)
    dh.caption(doc, "Table 1.", "Single wideband antennas with a metasurface, AMC or FSS reflector.", above=True)
    dh.table(doc, SINGLE_HEAD, single_rows(cite), SINGLE_W, size=8.5, cite=cite, highlight_last=True)
    dh.para(doc, "λ_{L}: free-space wavelength at the lowest operating frequency. “No MS → MS”: without → with the "
                 "reflector. “n/r”: not reported; “unverified”: not confirmed in the accessible text.", size=9)
    dh.caption(doc, "Table 2.", "MIMO antennas that use a metasurface (background for Phase II).", above=True)
    dh.table(doc, MIMO_HEAD, mimo_rows(cite), MIMO_W, size=8.5, cite=cite)

    dh.heading(doc, "Research Gap and Position of This Work")
    for t in lit.GAP_POINTS or [TODO]:
        dh.para(doc, t, cite)
    dh.para(doc, lit.gap_paragraph(), cite)

    dh.heading(doc, "References", page_break=True)
    dh.references(doc, cite)

    doc.core_properties.title = f"{pj['title']}: Literature Review"
    doc.core_properties.author = ", ".join(n for n, _ in pj["students"])
    doc.core_properties.last_modified_by = doc.core_properties.author
    doc.save(str(OUT_DOCX))
    return OUT_DOCX


# ============================================================================= markdown
def md(text: str, cite: dh.Citer) -> str:
    text = cite.render(text)
    text = re.sub(r"_\{([^}]*)\}", r"<sub>\1</sub>", text)
    return re.sub(r"\^\{([^}]*)\}", r"<sup>\1</sup>", text)


def md_table(head: list[str], rows: list[list[str]], cite: dh.Citer) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(md(c, cite).replace("|", "/") for c in r) + " |" for r in rows]
    return "\n".join(out)


def build_md() -> Path:
    cite = dh.Citer(lit.ref_text)
    s = ["# Literature Review", "",
         "Generated by `report/build_literature_review.py` from `report/literature.py`. Edit the data there, not here.",
         "",
         "- Every value was checked against the paper’s full text (PDF). **unverified** means the text does not settle "
         "it; **n/r** means the paper does not report it.",
         "- Gain is given as **without → with** the metasurface/reflector where the paper reports both.",
         "", "## Scope and search", ""]
    s += [md(t, cite) + "\n" for t in lit.SCOPE]
    s += ["## Table A: single antennas with a metasurface reflector (Phase I)", "",
          md_table(SINGLE_HEAD, single_rows(cite), cite), "",
          "## Table B: MIMO antennas with metasurfaces (Phase II background)", "",
          md_table(MIMO_HEAD, mimo_rows(cite), cite), "", "## Paper notes", ""]
    for p in lit.PAPERS:
        s += [f"**{p.short}** {md(f'[@{p.key}]', cite)}: {md(paper_text(p), cite)}", ""]
    s += ["## Research gap and position of this work", ""]
    s += [md(t, cite) + "\n" for t in lit.GAP_POINTS or [TODO]]
    s += [md(lit.gap_paragraph(), cite), "", "## References", ""]
    s += [f"{n}. {md(lit.ref_text(k), cite)}" for n, k in enumerate(cite.order, 1)]
    OUT_MD.write_text("\n".join(s) + "\n", encoding="utf-8")
    return OUT_MD


def missing() -> list[str]:
    fields = ["antenna", "substrate", "ms", "placement", "band", "gain", "problem", "method", "results", "relevance"]
    mimo_fields = ["ports", "size", "isolation", "ecc", "ms_role"]
    out = []
    for p in lit.PAPERS:
        need = [f for f in fields + (mimo_fields if p.group == "mimo" else []) if getattr(p, f) is None]
        if need:
            out.append(f"{p.key}: {', '.join(need)}")
        if not p.ref_checked:
            out.append(f"{p.key}: reference not yet checked against the PDF")
    if not lit.GAP_POINTS:
        out.append("GAP_POINTS: research gap not written yet")
    return out


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, help="write both files into this folder instead (preview)")
    args = ap.parse_args()
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        OUT_DOCX, OUT_MD = args.out / OUT_DOCX.name, args.out / OUT_MD.name
    for path in (build_docx(), build_md()):
        print(f"Wrote {path}")
    todo = missing()
    print(f"Missing ({len(todo)}):" if todo else "Missing: none")
    for t in todo:
        print("  -", t)
