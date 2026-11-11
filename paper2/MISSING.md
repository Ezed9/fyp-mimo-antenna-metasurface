# What is still missing from "MIMO Antenna with FSS"

The paper (`MIMO_Antenna_with_FSS.pdf`, 4 pages) reports **one** result: the simulated S11 curve in
`inputs/04_s11.png`. Everything below is marked in yellow in the paper as "TO BE ADDED" or "TO BE CONFIRMED". Nothing
in this list was estimated or invented.

## 1. To confirm first (changes what the paper may claim)

| # | Question | Where it shows in the paper |
|---|---|---|
| 1 | **Which model produced the S11 plot?** The paper takes it as port 1 of the four-port antenna *with* the FSS. If it is the antenna without the FSS, or another model, the abstract, Section III-A, Fig. 4 and the conclusion must change. | Fig. 4 caption (TO BE CONFIRMED) |
| 2 | Does the FSS board have a copper back? The paper does not say either way. A surface with a full copper back is a reflector or metasurface, not an FSS in the usual sense. | Section II-B |
| 3 | Which patch is port 1, and how are the ports numbered? | Section II-A |

## 2. Results to add (CST)

| # | Result | Placeholder in the paper |
|---|---|---|
| 4 | S11 of the MIMO antenna **without** the FSS, same axes (shows what the FSS changes) | Section III-B (i) |
| 5 | S22, S33, S44 | Section III-B (ii), Fig. 5 |
| 6 | Isolation: S21, S31, S41 (and the other pairs if the layout is not symmetric) | Section III-B (iii), Fig. 5, Table III |
| 7 | Realized gain and efficiency against frequency, with and without the FSS | Abstract, Section III-B (iv), Fig. 6, Table III |
| 8 | ECC and diversity gain (from S-parameters or far fields) | Abstract, Section III-B (v) |
| 9 | Radiation patterns in the two principal planes at a few frequencies | Abstract, Section III-B (vi), Fig. 7 |
| 10 | FSS unit-cell simulation: reflection, transmission and reflection phase against frequency | Section II-B |
| 11 | The S11 sweep beyond 15 GHz, to find the upper edge of the second band | Table II footnote |

## 3. Dimensions and materials to add (Table I)

Substrate material and thickness; board length and width; decagon circumradius; feed-line width and slot width;
ground patch length and width; spacing between elements; outer and inner ring radii; ring width and split width; FSS
cell period and board size; gap h between the antenna and the FSS.

## 4. Other open points

- **Exported S11 data.** The S11 numbers were read from the screenshot with `analysis/digitize_cst_plot.py`
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

## 5. What the S11 curve shows (for reference)

| Quantity | Value |
|---|---|
| S11 < −10 dB | 1.71–5.48 GHz (105 %) and 5.73–15 GHz (end of the sweep) |
| Between the two bands | rises to −9.2 dB at 5.62 GHz |
| Deepest resonance | −34.9 dB at 7.38 GHz |
| Other resonances below −20 dB | 1.90, 2.62, 3.76, 8.50, 9.18 GHz |
| Weak points | −10.1 dB at 4.46 GHz; −11.5 dB at 13.0 GHz |

## Rebuild

```bash
uv run paper2/build_paper.py
```
