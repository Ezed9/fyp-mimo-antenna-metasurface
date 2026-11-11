# What is still missing from "MIMO Antenna with FSS"

The paper (`MIMO_Antenna_with_FSS.pdf`, 5 pages) follows the co-guide's order: the single antenna first, then the
four-port MIMO antenna with the FSS, then a comparison of the two.

- **Single antenna:** dimensions, S11 (2.16–15.73 GHz) and gain are the team's existing CST results already recorded
  in this repository (`report/literature.py`, `report/build_report.py`, `GAP_STUDY.md`, `figures/`).
- **MIMO antenna with FSS:** the only result is the simulated S11 curve in `inputs/04_s11.png`.

Everything below is marked in yellow in the paper as "TO BE ADDED" or "TO BE CONFIRMED". Nothing in this list was
estimated or invented.

## 1. To confirm first (changes what the paper may claim)

| # | Question | Where it shows in the paper |
|---|---|---|
| 1 | **Which model produced the S11 plot?** The paper takes it as port 1 of the four-port antenna *with* the FSS. If it is the antenna without the FSS, or another model, the abstract, Sections III-B and III-C, Figs. 5–6, Table II and the conclusion must change. | Fig. 5 caption (TO BE CONFIRMED) |
| 2 | **Are the four MIMO elements the same as the single antenna** (R = 15 mm decagon, 3.0 mm strip, 0.5 mm slots, same ground)? The paper says they are of the same kind and marks the dimensions as to be confirmed. | Section II-B (TO BE CONFIRMED) |
| 3 | Does the FSS board have a copper back? The paper does not say either way. A surface with a full copper back is a reflector or metasurface, not an FSS in the usual sense. | Section II-C |
| 4 | Which patch is port 1, and how are the ports numbered? | Section II-B |

## 2. Results to add (CST)

| # | Result | Placeholder in the paper |
|---|---|---|
| 5 | **S11 of the MIMO antenna without the FSS**, same axes. Without it the comparison cannot say whether a change comes from the extra elements or from the FSS. | Sections III-C and III-D (i) |
| 6 | S22, S33, S44 | Section III-D (ii), Fig. 7 |
| 7 | Isolation: S21, S31, S41 (and the other pairs if the layout is not symmetric) | Section III-D (iii), Fig. 7, Tables II and III |
| 8 | Realized gain and efficiency against frequency, with and without the FSS | Abstract, Section III-D (iv), Fig. 8, Tables II and III |
| 9 | ECC and diversity gain (from S-parameters or far fields) | Abstract, Section III-D (v), Table II |
| 10 | Radiation patterns in the two principal planes at a few frequencies | Abstract, Section III-D (vi), Fig. 9 |
| 11 | FSS unit-cell simulation: reflection, transmission and reflection phase against frequency | Section II-C |
| 12 | The S11 sweep beyond 15 GHz, to find the upper edge of the second band | Table II footnote |

## 3. Dimensions and materials to add (Table I)

The single-antenna rows are filled from the repository. Still to add: MIMO board length and width; spacing between
elements; outer and inner ring radii; ring width and split width; FSS cell period, board size and substrate; gap h
between the antenna and the FSS.

## 4. Other open points

- **Single-antenna gain.** The value in the paper (about 2.9–4.9 dBi over 3.1–10.6 GHz) is CST "Gain" read from
  `figures/cst_single_final_gain_ieee.png`, as recorded in `report/literature.py`. No gain plot is shown.
- **Sweep ranges differ.** The single antenna was simulated over 0–18 GHz and the MIMO antenna over 1–15 GHz.
- **Exported S11 data.** The MIMO S11 numbers were read from the screenshot with `analysis/digitize_cst_plot.py`
  (`data/s11_digitized.csv`). Reading accuracy is about ±0.03 GHz and ±0.3 dB. The narrow dip near 2.6 GHz is sharper
  than the digitiser can follow (it reads −28 dB; the plot shows about −31 dB), so the paper gives only its frequency.
  A CST ASCII export would remove this limit.
- **Author e-mail addresses** and the corresponding author are not in the mid-semester report, so the title block has
  none.
- **Two images in the upload were not used** (`inputs/not_used/`): an S22 plot (0–15 GHz) and a two-port antenna with a
  meander line between the elements. Neither was described, and the S22 plot cannot be tied to a model.
- **Input file formats.** The upload held JPEG files. They were stored under the requested names as lossless WebP/PNG
  copies; the pixels are unchanged.
- **Measurement.** The paper is simulation only. A fabricated prototype with measured S-parameters is listed as
  future work.
- **References.** All 19 are real. Thirteen come from `report/literature.py`. Six are new and were checked by web
  search in this session (Munk 2000; Ranga 2011; Kundu 2018; Al-Gburi 2021; Blanch 2003; Usha Devi 2024). For Usha
  Devi 2024 the search confirmed the title, authors, journal and DOI but not the volume and issue, so those are left
  out. The DOI resolver itself could not be reached from this environment.

## 5. What the two S11 curves show (for reference)

| Quantity | Single antenna | MIMO with FSS (port 1) |
|---|---|---|
| S11 < −10 dB | 2.16–15.73 GHz (152 %) | 1.71–5.48 GHz (105 %) and 5.73–15 GHz (end of the sweep) |
| Lower band edge | 2.16 GHz | 1.71 GHz |
| Deepest resonance | −32.6 dB at 2.73 GHz | −34.9 dB at 7.38 GHz |
| Weakest point | −10.3 dB near 6.5 GHz | −9.2 dB at 5.62 GHz (splits the range into two bands) |
| Below −20 dB | only at the resonances | 6.5–10.0 GHz |

## Rebuild

```bash
uv run paper2/build_paper.py
```
