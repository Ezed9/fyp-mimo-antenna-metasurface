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
| `make_paper_figures.py` | Figs. 1–6; placeholders are replaced automatically when the CST exports exist |
| `build_paper.py` | The text, tables, equations and references, then the docx and PDF |
| `cst/` | The team's CST screenshots (antenna, metasurface, S11) and the cropped S11 plot used for digitizing |
| `../exports/paper/s11_ms4x4_digitized.csv` | S11 with the metasurface, digitized from the screenshot (±0.02 GHz, ±0.1 dB) |

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
| Wp, s, P | patch side, gap between patches, period | 4.8, 0.7, 5.5 |
| t | metasurface substrate thickness (FR-4 assumed) | 1.6 |
| h | air gap, antenna back face to metasurface | 2 (from the earlier design) |
| — | **metasurface has a full copper back?** (`MS_COPPER_BACK`) | assumed yes |

The LC estimate (f0 ≈ 8.0 GHz, in-phase band ≈ 6.9–9.1 GHz) holds only if the back is solid copper. If it is not, Section
II-B must be rewritten.

## 2. Export these from CST and drop them into `exports/paper/`

All are *1D result → right-click → Export → Plot Data (ASCII)*, two columns (frequency in GHz or angle in deg, value).

| File | What | Fills |
|---|---|---|
| `s11_with_ms.txt` | S11 (dB), antenna + metasurface, 1–15 GHz | replaces the digitized curve (exact numbers) |
| `s11_antenna_alone.txt` | S11 (dB), octagon antenna without the metasurface | Fig. 3 second curve, Table II row 1 |
| `gain_antenna_alone.txt` | realized gain (dBi) vs frequency, broadside (θ = 0°), no metasurface | Fig. 4 |
| `gain_with_ms.txt` | the same with the metasurface | Fig. 4 |
| `pattern_5.3GHz_E.txt`, `pattern_5.3GHz_H.txt`, and likewise at 9.9 and 14.5 GHz | farfield polar cuts (angle, dB) | Fig. 5 |

Add farfield monitors at 5.3, 9.9 and 14.5 GHz (one per band, at or near the deepest dip). Change `PATTERN_FREQS` in
`design.py` if you use other frequencies. After exporting, rerun both scripts, then replace the `[xx]` sentences in
`build_paper.py` (search for `«`) with the real numbers.

## 3. Things the team should know (honest review)

1. **Not UWB.** With the metasurface the antenna matches over 3.43–6.13, 7.64–13.25 and 13.93–15+ GHz. It fails at
   6.13–7.64 GHz (peak −6.4 dB at 6.97 GHz) and below 3.43 GHz. The paper therefore says *tri-band*. Do not call
   6.13–7.64 GHz a notch: a −6.4 dB peak is not a notch, and nothing in the design creates it.
2. **Band III is marginal**: about −11 dB, roughly 1 dB of margin, and it runs into the 15 GHz simulation limit. Extend
   the sweep to 18 GHz and refine the mesh before relying on it.
3. **The metasurface's benefit is unproven until the gain is exported.** A reviewer's first question will be "what does the
   metasurface do?". Without Fig. 4 the only answer is that it reshapes S11. If the gain does not rise, the paper needs a
   different story (for example, a plain copper plate at the same gap as a control, as in `GAP_STUDY.md`).
4. **The S11 is digitized from a screenshot** in which the solver was still running. Confirm it is the final run and
   export the ASCII data.
5. **CPW feed impedance.** With Wf = 3.0 mm and g = 0.5 mm on 1.6 mm FR-4, the conformal-mapping formula gives about
   **58 Ω** (`design.cpw_z0()`), not 50 Ω. Check *Port modes → Line impedance* in CST. A narrower slot (about 0.3 mm) or a
   wider strip brings it closer to 50 Ω. This is not mentioned in the paper.
6. **Simulation only.** That is acceptable for AJEC-level journals and conferences (the Bhattacharya paper is simulation
   only). IEEE AWPL, PIER and similar venues expect a fabricated prototype with measured S11, gain and patterns.
7. **Authors.** Order, e-mails and the corresponding author are placeholders. The current order is the four students,
   then the co-guide, then the guide.
