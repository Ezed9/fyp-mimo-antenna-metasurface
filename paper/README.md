# Paper: tri-band CPW-fed octagonal monopole with a 4 × 4 square-patch metasurface

`Paper.docx` / `Paper.pdf` is a two-column IEEE-style paper (the Word template family of S. Bhattacharya *et al.*,
AJEC 2025), written in the voice and section pattern of that paper:
Abstract → I. Introduction → II. Antenna Design and Analysis → III. Results and Discussion → IV. Applications →
V. Conclusion → References. The analysis and comparison sections follow Rajalakshmi & Gunavathi (PIER-L, 2018).

**Yellow text in the paper = not final.** Either a dimension estimated from the screenshots or an `[xx]` placeholder
for a CST result that has not been exported yet. Nothing about gain is claimed until the gain data exists.

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
| `make_paper_figures.py` | Only the drawn figures: stack-up sketch (Fig. 2) and applications chart (Fig. 6) |
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
| 3(a) | `cst_s11_no_ms_assumed.jpg` | New (14 Nov). **Assumed** to be the antenna without the metasurface; marked TO BE CONFIRMED in the paper. Set `S11_ALONE_ASSUMED = False` in `design.py` once confirmed |
| 3(b) | `cst_s11_with_ms.jpg` | New (14 Nov). Same curve as the earlier with-metasurface run |
| 4(a) | `cst_directivity_no_ms_assumed.png` | New (17 Nov). Directivity against frequency, maximum in the φ = 0° plane. The smooth curve (peak 5.2 dBi) is **assumed** to be the antenna alone; marked TO BE CONFIRMED |
| 4(b) | `cst_directivity_with_ms_assumed.png` | New (17 Nov). The curve with dips near 7.5, 9.6 and 12 GHz (peak 7.0 dBi) is **assumed** to be the antenna with the metasurface. Set `DIR_ASSUMED = False` in `design.py` once confirmed |
| 5(a) | `cst_pattern_5p3GHz_lobe176deg.jpg` | 14 Nov. Directivity, φ = 90° cut, 5.3 GHz, main lobe at 176° (3.56 dBi). **Assumed** antenna without the metasurface |
| 5(b) | `cst_pattern_5p3GHz_lobe2deg.png` | New (19 Nov). Same cut, main lobe at 2° (3.88 dBi, side-lobe level −1.3 dB). **Assumed** antenna with the metasurface |
| 5(c) | `cst_pattern_12p5GHz.jpg` | 14 Nov. 12.5 GHz. **Model not known.** All three are marked TO BE CONFIRMED; set `PATTERN_MODEL_CONFIRMED = True` and fix the `model` entries in `design.PATTERNS` once known |

If the two S11 plots, or the two directivity plots, are the other way round, swap the two files (and their digitised
CSVs) and rebuild: the text of Sections III-A and III-B and Table II follow the data.

## 1. Confirm these dimensions (set `est=False` in `design.py` once checked)

Read off the CST screenshots using the CST working-plane grid. In both 3D views it is 10.9 px per square, and with the
1 mm raster shown in the S11 screenshot this gives a 3.0 mm feed and 0.5 mm slots (the earlier design's values). So the
scale is probably right, but **every value below is an estimate**.

| Symbol | Meaning | Estimate (mm) |
|---|---|---|
| Ws × Ls | antenna substrate | 27 × 31 |
| R | octagon circumradius (vertex at top and bottom) | 8.7 |
| Wf, g | CPW feed width, slot width | 3.0, 0.5 |
| Lg, Wg | ground length, ground width (each side) | 11, 11.5 |
| p | gap between the octagon's lower vertex and the ground | 0.5 |
| Wm × Lm | metasurface board | 27 × 31 |
| Wp, s, P | patch side, gap between patches, period | 4.8, 0.7, 5.5 (see the note below) |
| t | metasurface substrate thickness (FR-4 assumed) | 1.6 |
| h | air gap, antenna back face to metasurface | 2 (from the earlier design) |
| — | **metasurface has a full copper back?** (`MS_COPPER_BACK`) | assumed yes |

The LC estimate (f0 ≈ 8.0 GHz, in-phase band ≈ 6.9–9.1 GHz) holds only if the back is solid copper. If it is not, Section
II-B must be rewritten.

**Note from the new metasurface screenshot (14 Nov).** In the clean view the patch is 63 px, the gap 6 px and the board
339 × 377 px. With the board taken as 27 mm wide this gives a patch of about **5.0 mm**, a gap of about **0.5 mm**
(period still 5.5 mm) and a board of about **27 × 30 mm**, not 4.8 / 0.7 / 27 × 31. The table and the paper still
carry the old estimates. With 5.0 / 0.5 the LC estimate drops to about 7.4 GHz, which is **below** band II, so the
sentences that place it "inside the second band" (abstract, Section II-B, conclusion) would have to change. Give the
real CST values before deciding.

## 2. Export these from CST and drop them into `exports/paper/`

All are *1D result → right-click → Export → Plot Data (ASCII)*, two columns (frequency in GHz or angle in deg, value).

| File | What | Fills |
|---|---|---|
| `s11_with_ms.txt` | S11 (dB), antenna + metasurface, 1–15 GHz | exact numbers instead of the digitized curve (the figure stays the screenshot) |
| `s11_antenna_alone.txt` | S11 (dB), octagon antenna without the metasurface | the same for Table II row 1 |

Realized gain and efficiency against frequency, with and without the metasurface, are still missing (yellow in the
abstract, Section III-B, Table III and the conclusion). Send them as CST screenshots, like the directivity plots.

Still needed as CST screenshots (they go into `cst/` and are listed in `design.PATTERNS`): the patterns in the φ = 0°
plane, a pattern in band II (near 9.9 GHz), and the same cuts for the other model (with / without the metasurface).
After adding data, rerun both scripts, then replace the `[xx]` sentences in `build_paper.py` (search for `«`) with
the real numbers.

## 3. Things the team should know (honest review)

1. **Not UWB.** With the metasurface the antenna matches over 3.42–6.13, 7.63–13.23 and 13.95–15+ GHz. It fails at
   6.13–7.63 GHz (peak −6.5 dB at 6.92 GHz) and below 3.42 GHz. The paper therefore says *tri-band*. Do not call
   6.13–7.63 GHz a notch: a −6.5 dB peak is not a notch, and nothing in the design creates it.
2. **Band III is marginal**: about −11 dB, roughly 1 dB of margin, and it runs into the 15 GHz simulation limit. Extend
   the sweep to 18 GHz and refine the mesh before relying on it.
3. **The metasurface's benefit is still unproven.** If Fig. 3(a) is the antenna alone, the antenna is matched *better*
   without the metasurface: 3.52–15 GHz with only a 0.2 dB excursion (−9.8 dB) near 5.5 GHz, against three separate
   bands with it. The paper says this plainly. At 5.3 GHz the pattern stays two-sided: with the metasurface (as
   assumed) the main lobe turns to the front, but the opposite lobe is only 1.3 dB lower, so the reflector effect is weak. A reviewer's first question will be "what does the metasurface do?"; the answer
   needs the realized gain with and without it. The directivity plots (Fig. 4) give a mixed answer: with the
   metasurface the peak rises from 5.2 to 7.0 dBi and bands I and III improve, but over 70 % of band II the
   directivity is lower, with dips to −2.8, −1.0 and −0.3 dBi. The paper reports this as it is.
4. **The S11 numbers are digitized from screenshots.** Export the ASCII data for exact values.
5. **CPW feed impedance.** With Wf = 3.0 mm and g = 0.5 mm on 1.6 mm FR-4, the conformal-mapping formula gives about
   **58 Ω** (`design.cpw_z0()`), not 50 Ω. Check *Port modes → Line impedance* in CST. A narrower slot (about 0.3 mm) or a
   wider strip brings it closer to 50 Ω. This is not mentioned in the paper.
6. **Simulation only.** That is acceptable for AJEC-level journals and conferences (the Bhattacharya paper is simulation
   only). IEEE AWPL, PIER and similar venues expect a fabricated prototype with measured S11, gain and patterns.
7. **Authors.** Order, e-mails and the corresponding author are placeholders. The current order is the four students,
   then the co-guide, then the guide.
