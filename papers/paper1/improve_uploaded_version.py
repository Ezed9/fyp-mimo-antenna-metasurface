"""The authors' own Paper_1.docx (the version with the Applications section), with clearer figures.

    python papers/make_figures.py && python papers/paper1/improve_uploaded_version.py

The text is left as the authors wrote it, including their yellow "TO BE CONFIRMED" notes. Changed:
  * the four CST graph screenshots (S11 and directivity, without / with the metasurface) and the two 5.3 GHz
    radiation-pattern screenshots are replaced by redrawn figures with dark, thick lines, same size and position;
  * the 12.5 GHz pattern, Fig. 5(c), is removed with its paragraph, because the model it belongs to is not known.
"""
from __future__ import annotations

from pathlib import Path

import docx
from docx.oxml.ns import qn

HERE = Path(__file__).resolve().parent
SRC = HERE / "uploaded_version" / "Paper_1_as_uploaded.docx"
OUT = HERE / "uploaded_version" / "Paper_1_clear_figures.docx"
NEW = HERE / "figures_uploaded_version"
REPLACE = {"image4.png": "s11_without.png", "image5.png": "s11_with.png", "image6.png": "directivity_without.png",
           "image7.png": "directivity_with.png", "image8.png": "pattern_5p3GHz_without.png",
           "image9.png": "pattern_5p3GHz_with.png"}
SQUARE = {"image8.png", "image9.png"}                # the patterns: redrawn as large square polar plots
DROP_IMAGE = "image10.png"                           # the 12.5 GHz pattern


def text_of(element) -> str:
    return "".join(t.text or "" for t in element.iter(qn("w:t")))


def main() -> None:
    doc = docx.Document(str(SRC))
    # 1. new pixels for the six figures (the frames keep their size)
    square = {}                                       # rId of the two pattern pictures, which become square
    for rel in doc.part.rels.values():
        name = Path(rel.target_ref).name
        if name in REPLACE:
            rel.target_part._blob = (NEW / REPLACE[name]).read_bytes()
            if name in SQUARE:
                square[rel.rId] = True
    side_w, side_h = int(2.45 * 914400), int(2.45 * 0.98 * 914400)       # EMU: 2.45 in wide, the plot's own shape
    for inline in doc.element.body.iter(qn("wp:inline")):
        if any(b.get(qn("r:embed")) in square for b in inline.iter(qn("a:blip"))):
            for ext in list(inline.iter(qn("wp:extent"))) + list(inline.iter(qn("a:ext"))):
                if ext.get("cx"):
                    ext.set("cx", str(side_w))
                    ext.set("cy", str(side_h))
    # 2. remove Fig. 5(c): its picture, its "(c)" label and the paragraph that discusses it
    body = list(doc.element.body.iterchildren())
    rids = {rel.rId for rel in doc.part.rels.values() if Path(rel.target_ref).name == DROP_IMAGE}
    removed = 0
    for k, el in enumerate(body):
        has_picture = any(b.get(qn("r:embed")) in rids for b in el.iter(qn("a:blip")))
        if has_picture:
            if text_of(body[k + 1]).strip() == "(c)":
                body[k + 1].getparent().remove(body[k + 1])
                removed += 1
            el.getparent().remove(el)
            removed += 1
        elif text_of(el).startswith("At 12.5 GHz (Fig. 5(c))"):
            el.getparent().remove(el)
            removed += 1
    assert removed == 3, removed
    # 3. the two sentences that mention it
    edits = {"; the model of Fig. 5(c) is not known.": ".",
             "; (b) 5.3 GHz, antenna with the metasurface; (c) 12.5 GHz. ":
                 "; (b) 5.3 GHz, antenna with the metasurface. "}
    done = {key: 0 for key in edits}
    for t in doc.element.body.iter(qn("w:t")):
        for old, new in edits.items():
            if t.text and old in t.text:
                t.text = t.text.replace(old, new)
                done[old] += 1
    assert done == {"; the model of Fig. 5(c) is not known.": 2,
                    "; (b) 5.3 GHz, antenna with the metasurface; (c) 12.5 GHz. ": 1}, done
    zoom = doc.settings.element.find(qn("w:zoom"))     # the original lacks a required attribute; add it
    if zoom is not None and zoom.get(qn("w:percent")) is None:
        zoom.set(qn("w:percent"), "100")
    doc.save(str(OUT))
    print(OUT)


if __name__ == "__main__":
    main()
