# Paper: tri-band CPW-fed octagonal monopole with a 4 × 4 square-patch metasurface

`Paper.docx` / `Paper.pdf` is a two-column IEEE-style paper (the Word template family of S. Bhattacharya *et al.*,
AJEC 2025), written in the voice and section pattern of that paper:
Abstract → I. Introduction → II. Antenna Design and Analysis → III. Results and Discussion → IV. Conclusion →
References. The analysis and comparison sections follow Rajalakshmi & Gunavathi (PIER-L, 2018).

**Final version (19 Nov 2026).** The team confirmed every dimension, the layer order and the figure assignments, so
the paper has no yellow text left. By the team's decision it reports directivity and no realized gain, has no
Applications section and no author e-mail lines.

## Rebuild

```bash
uv run paper/make_paper_figures.py      # paper/figures/*.png
uv run paper/build_paper.py             # paper/Paper.docx and paper/Paper.pdf (PDF needs LibreOffice)
```

Equations are Office Math. Word shows them directly; LibreOffice needs its Math module to put them in the PDF
(`apt-get install libreoffice-math`). The optional `--compare a.pdf b.pdf` flag counts 8-word sequences shared with the
given PDFs (e.g. the two reference papers). The body text must report 0, and it does now.

| File | Role |
|---|---|
| `design.py` | **All numbers**: dimensions (with `est` flags), S11 band analysis, the Ray and LC estimates, service list |
| `make_paper_figures.py` | The one drawn figure: the side-view sketch (Fig. 2) |
| `build_paper.py` | The text, tables, equations and references, then the docx and PDF. It places the CST screenshots as Figs. 1, 3, 4 and 5 |
| `cst/` | The team's CST screenshots, stored byte-for-byte as received |
| `../exports/paper/cst_s11_*_digitized.csv` | The two S11 curves read from the screenshots (±0.02 GHz, ±0.1 dB); used for the numbers only |
| `../exports/paper/cst_directivity_*_digitized.csv` | The two directivity curves read from the screenshots (±0.02 GHz, ±0.05 dB); numbers only |

## Figures that are CST screenshots (never redrawn)

Figs. 1, 3, 4 and 5 are the screenshots themselves. `build_paper.py` only crops blank margins (`CROP_*` constants); it
does not resize, filter, redraw or annotate them, and every label inside them is kept.

| Fig. | File in `cst/` | Status |
|---|---|---|
| 1(a) | `cst_octagon_antenna.png` | **Old screenshot.** No new antenna image was supplied on 14 Nov; replace this file when one is |
| 1(b) | `cst_ms4x4_top_v2.jpg` | New (14 Nov) |
| 3(a), 3(b) | `cst_s11_no_ms.jpg`, `cst_s11_with_ms.jpg` | S11 of the antenna without and with the metasurface (confirmed 19 Nov) |
| 4(a), 4(b) | `cst_directivity_no_ms.png`, `cst_directivity_with_ms.png` | Directivity against frequency, maximum in the φ = 0° plane, without and with the metasurface (confirmed 19 Nov) |
| 5(a), 5(b) | `cst_pattern_5p3GHz_no_ms.jpg`, `cst_pattern_5p3GHz_with_ms.png` | Directivity pattern, φ = 90° cut, 5.3 GHz, without and with the metasurface (confirmed 19 Nov) |

The 12.5 GHz pattern was removed at the team's request (19 Nov).

## 1. Dimensions (confirmed by the team on 19 Nov 2026)

| Symbol | Meaning | Value (mm) |
|---|---|---|
| Ws × Ls × hs | FR-4 antenna substrate | 27 × 30 × 1.6 |
| R | octagon circumradius | 9 |
| Wf, g | CPW feed width, slot width | 3.0, 0.3 |
| Wg1, Wg2 | left and right ground width | 11.2, 12.2 |
| Lg | ground length (both) | 11 |
| p | gap between the octagon's lower vertex and the ground | 0.22 |
| Wm × Lm, t | metasurface board (FR-4) | 27 × 30, 1.6 |
| Wp, s, P | patch side, gap between patches, period | 5.0, 0.5, 5.5 |
| — | air gap between antenna and metasurface | none |
| — | copper ground | none |

**Layer order, top to bottom (confirmed):**

1. 4 × 4 copper patches, on the outer face of the metasurface board
2. metasurface substrate (FR-4, t = 1.6 mm)
3. octagon + CPW copper, at the interface between the two substrates
4. antenna substrate (FR-4, hs = 1.6 mm)

There is no air gap and no ground plane; the total thickness is 3.2 mm. The antenna copper is enclosed between the two
FR-4 layers, so the paper's title says "loaded with" a metasurface, not "backed by".

Two estimates in Section II-B follow from this order (`design.py`):

- **Feed line:** with FR-4 on both sides of the CPW, the effective permittivity rises from about 2.4 to about 3.8 and
  the line impedance falls from about 50 Ω to about 40 Ω (`cpw_z0(covered=True)`).
- **Patch capacitance:** the patches have FR-4 on one side and air on the other, so C ≈ 0.23 pF (`patch_grid()`).
  It was 0.37 pF while the patches were wrongly taken to lie between the two boards.

The earlier reflector model (LC resonance near 8 GHz and the gap condition) does not apply to a structure with no
ground plane and no gap, and was removed.

## 2. Export these from CST and drop them into `exports/paper/`

All are *1D result → right-click → Export → Plot Data (ASCII)*, two columns (frequency in GHz or angle in deg, value).

| File | What | Fills |
|---|---|---|
| `s11_with_ms.txt` | S11 (dB), antenna + metasurface, 1–15 GHz | exact numbers instead of the digitized curve (the figure stays the screenshot) |
| `s11_antenna_alone.txt` | S11 (dB), octagon antenna without the metasurface | the same for Table II row 1 |

Realized gain is not reported, by the team's decision (19 Nov): the paper uses directivity throughout, and Table III
marks this work's value as directivity.

Optional additions, as CST screenshots (they go into `cst/` and are listed in `design.PATTERNS`): the patterns in the
φ = 0° plane and a pattern in band II (near 9.9 GHz), each without and with the metasurface.

## 3. Things the team should know (honest review)

1. **Not UWB.** With the metasurface the antenna matches over 3.42–6.13, 7.63–13.23 and 13.95–15+ GHz. It fails at
   6.13–7.63 GHz (peak −6.5 dB at 6.92 GHz) and below 3.42 GHz. The paper therefore says *tri-band*. Do not call
   6.13–7.63 GHz a notch: a −6.5 dB peak is not a notch, and nothing in the design creates it.
2. **Band III is marginal**: about −11 dB, roughly 1 dB of margin, and it runs into the 15 GHz simulation limit. Extend
   the sweep to 18 GHz and refine the mesh before relying on it.
3. **The metasurface's benefit is mixed.** The antenna is matched *better*
   without the metasurface: 3.52–15 GHz with only a 0.2 dB excursion (−9.8 dB) near 5.5 GHz, against three separate
   bands with it. The paper says this plainly. At 5.3 GHz the pattern stays two-sided: with the metasurface
   the main lobe turns to the front, but the opposite lobe is only 1.3 dB lower, so the reflector effect is weak. A reviewer's first question will be "what does the metasurface do?". The directivity plots (Fig. 4) give a mixed answer: with the
   metasurface the peak rises from 5.2 to 7.0 dBi and bands I and III improve, but over 70 % of band II the
   directivity is lower, with dips to −2.8, −1.0 and −0.3 dBi. The paper reports this as it is.
4. **The S11 numbers are digitized from screenshots.** Export the ASCII data for exact values.
5. **Directivity is not gain.** With no gain result, a reviewer may ask for efficiency. Table III compares this
   work's directivity with other works' gain and says so in a footnote; do not call the 7.0 dBi "gain".
6. **Simulation only.** That is acceptable for AJEC-level journals and conferences (the Bhattacharya paper is simulation
   only). IEEE AWPL, PIER and similar venues expect a fabricated prototype with measured S11, gain and patterns.
7. **Authors.** The order is the four students, then the co-guide, then the guide. There are no e-mail lines, by the
   team's decision; most journals still ask for a corresponding author's e-mail at submission.
