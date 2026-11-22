# The two papers

| | File | State |
|---|---|---|
| Paper 1 | `paper1/Paper1_TriBand_Octagonal_Monopole_revised.docx` (+ `.pdf`) | Revised. Two items are highlighted in yellow (the feed gap *p* and the side of *θ* = 0°); do the checks in section 3 before submitting. |
| Paper 2 | `paper2/Paper2_FourPort_Decagonal_MIMO_draft.docx` (+ `.pdf`) | **Draft, not submittable.** It has no coupling, ECC, gain or confirmed dimensions; everything missing is highlighted in yellow. |

No number in either paper was invented. Curve-derived numbers come from `data/*.csv`, which were digitised from the CST
screenshots (about ±0.1 dB, ±0.02 GHz). `check_numbers.py` recomputes all of them.

## 1. Rebuilding

```bash
pip install numpy scipy matplotlib pillow python-docx scikit-rf      # pandoc is also needed (equations)
python papers/make_figures.py
python papers/paper1/build_paper1.py
python papers/paper2/build_paper2.py          # prints the list of open items
papers/render.sh papers/paper1/*.docx papers/paper2/*.docx           # PDF copies (LibreOffice + libreoffice-math)
```

The `.docx` is the deliverable; the PDFs are previews made with LibreOffice, which draws tall equation delimiters
badly (Word draws them correctly).

Replace a digitised curve by saving the CST export (Post-Processing → Import/Export → Plot Data (ASCII)) under the same
name in `data/`. The loader accepts CST's tab-separated format as it is. Then run `check_numbers.py`: Paper 2's text
updates itself; Paper 1's text is typed, so any number that changed must be edited in `build_paper1.py`.

## 2. Paper 2: what is needed, in order

### 2.0 What the S-parameter screenshots of the model with the metasurface show

Sixteen magnitude plots were supplied (`paper2/cst_screenshots/sparams_with_metasurface/`), digitised into
`data/p2_ms_s??.csv`, and are in the draft (Section III-B, two figures, one table).

| Finding | Numbers |
|---|---|
| Ports 1 and 2 (lower row, 15 mm patches) are matched | port 1 from 1.71 GHz except 5.48–5.73 GHz; port 2 from 1.72 GHz to beyond 15 GHz |
| **Ports 3 and 4 (upper row, 14 mm patches) are not valid** | \|S33\|, \|S44\| above −10 dB up to 10.5 GHz and **above 0 dB from 7.3 to 9.8 GHz** (+2.4 dB at 9.1 GHz); the power sum of the port-3 column reaches 1.75 |
| Isolation between ports 1 and 2 is poor at the low end | \|S21\| = −7.6 dB at 1.80 GHz (18 % of the power goes to port 2); above −10 dB over 1.72–2.04 and 4.38–4.62 GHz; ≥ 15 dB over 79 % of the range |
| Couplings involving ports 3 and 4 are below −21 dB | not interpretable while those ports reflect almost everything |

A passive antenna cannot reflect more than it receives, so the port-3 and port-4 results are a modelling error, not a
property of the design. All curves that involve those ports have a kink at 9.8 GHz and behave normally above it,
which is what a waveguide port does when the mode it uses is below cut-off: the most likely cause is that the ports
of the upper row do not excite the CPW mode. Check, for ports 3 and 4:

1. that the port face is centred on the feed strip of the upper row (the upper feed lines are offset by about 3.3 mm
   from the lower ones; a port copied from the lower row would sit beside the strip);
2. the port mode picture and the line impedance (Navigation tree → Ports → port mode): it must be the quasi-TEM CPW
   mode with a line impedance near 50 Ω, as for ports 1 and 2;
3. that the port touches both ground planes and the substrate, that its orientation points into the structure, and
   that the feed strip actually reaches the 14 mm patch;
4. the adaptive frequency sweep of the frequency-domain solver (more samples, or repeat with the time-domain solver).

What the screenshots cannot give: the phase (so no ECC, diversity gain, TARC, CCL) and the case without the
metasurface (so no statement on what the metasurface does to the coupling). Both come with the Touchstone export of
section 2.3.

### 2.1 Fix the model first (the screenshots show it is not what a paper can describe)

Measured on `paper2/cst_screenshots/mimo_design_without_metasurface.png` at 3.73 px/mm (±0.3 mm):

| What the screenshot shows | Why it matters |
|---|---|
| The two rows are different elements: lower-row patches *R* ≈ 15.0 mm with a feed gap ≈ 0.5 mm; upper-row patches *R* ≈ 14.0 mm with a feed gap ≈ 1.6 mm, narrower and longer grounds | The S11 of port 1 says nothing about the other row. The project's own sweep found that only *R* = 15 mm gives a continuous band |
| The board outline is stepped: two 100 × 50 mm halves shifted sideways by ≈ 4.8 mm | The paper cannot give one board size; it looks like two revisions pasted together |
| Facing patches are ≈ 2.4 mm apart (0.014 λ₀ at 1.73 GHz), flat edge to flat edge | These are the open ends of two co-polarised monopoles. Expect the worst isolation here, probably below 10–12 dB at the low end (a prediction, not data) |
| Upper-row grounds are 4 mm apart, lower-row grounds touch or have a hairline slit, the rows are not connected | Neither a common ground nor clean separate grounds. Reviewers expect a common ground |
| One inner ring (bottom-left cell of the metasurface) is drawn grey, the other 59 dark | Probably a different material or a left-over component |

Cheapest route to a publishable design, by benefit per hour:

1. Use the documented element (*R* 15 mm, ground edge −7 mm) four times on one rectangular substrate. About an hour.
2. Rotate each element by 90° (the layout planned in `CST_GUIDE.md` §6). The four 50 mm tiles already fit 100 × 100 mm.
   This removes both the facing pair and the parallel pair; expect 15–22 dB without extra structures.
3. Join the four grounds deliberately (centre cross or strip).

### 2.2 Facts of the CST model

Confirmed by the authors and entered in `paper2/design.py`: patch radii 15 mm (lower row) and 14 mm (upper row),
ground length 18 mm, upper-row ground width 21.5 mm, CPW slot 0.3 mm, board outline 105.5 mm × 100.5 mm, ring radii
7.0–7.5 mm and 5.0–5.5 mm, splits 0.4 mm and 0.3 mm, cell pitch 17 mm along the rows, metasurface board the same size
as the antenna board, air gap 4.5 mm, **no copper on the back of the metasurface board**, CST 2019, frequency-domain
solver, ports 1/2 on the lower-left/right elements and 3/4 on the upper-left/right, same authors as Paper 1.

Still highlighted in the paper, because they were derived from those numbers or measured on the screenshots:

- lower-row ground width (23.2 mm if the ground edge is at x = −1.8 mm; the value given, −1.5 mm, would leave no slot);
- the patch-to-ground gap of each row (0.73 and 1.69 mm); the spacing of the facing patches (2.4 mm);
- how the grounds are joined (lower row: neighbours meet; upper row: 3.4 mm apart; rows not connected);
- the sideways step of the board outline (about 5 mm) and the offset of the upper feed lines (3.3 mm);
- cell pitch along the columns (about 18.5 mm);
- which side *θ* = 0° is. To settle it, read the z-coordinates of the metasurface board: if they are lower than those
  of the antenna board, *θ* = 0° is the copper side of the antenna, away from the metasurface, as the text says.

To verify in CST: that the S-parameters are normalised to a fixed 50 Ω, and the mesh cell count.

The two patch radii are kept as they are by the authors' decision, without a stated reason. A reviewer will ask why
the rows differ, and the S11 of port 1 (a 15 mm element) does not describe ports 3 and 4 (14 mm, 1.7 mm feed gap).
Section 2.1 is still the recommendation.

### 2.3 Simulation outputs, minimum for a MIMO paper

Time-domain solver, 1–16 GHz, −40 dB accuracy, **Source type = All Ports**, S-parameters normalised to fixed 50 Ω,
identical mesh settings in every model.

| # | Output | File |
|---|---|---|
| 1 | 4 × 4 S-matrix, antenna alone (Touchstone, ≥ 1001 points) | `exports/mimo_noMS.s4p` |
| 2 | 4 × 4 S-matrix with the metasurface | `exports/mimo_MS.s4p` |
| 3 | Directivity with the metasurface over the **whole** 1–15 GHz range (it now exists for 6–10 GHz only) | `papers/data/p2_dir_ms.csv` |
| 4 | Realized gain, radiation efficiency and total efficiency against frequency, every port, both models | `exports/mimo_noMS_gain.txt`, `…_eff_tot.txt`, `mimo_MS_…` |
| 5 | Control: a plain copper plate of the same size at the same position | `exports/mimo_PEC.s4p` + gain |
| 6 | Control: the bare FR-4 board (no rings) at the same position | `exports/mimo_FR4.s4p` + gain |
| 7 | Complex far fields of every port at 2, 3.1, 4, 7 and 10 GHz (5° steps, same origin) for the far-field ECC | `exports/ff/<run>_p<port>_<f>GHz.txt` (format in `CST_GUIDE.md` §9) |
| 8 | Pattern cuts (co- and cross-polar, both principal planes, same radial scale) at 3.1, 7 and 10 GHz, port 1 and one port of the other row | polar ASCII |

With files 1 and 2 in place, `build_paper2.py` writes Sections III-B and III-E, the coupling and ECC figures, Table I,
and the isolation/ECC sentences of the abstract and conclusion by itself (tested with synthetic data). Items 4–8 are
not wired into the paper yet: send them and the text is extended.

For a strong paper, add the unit-cell reflection phase (Floquet port), a gap sweep with the copper-plate control at
each gap, a mesh-convergence run, and a measured prototype.

### 2.4 What the present data say

- Port 1 is matched from 1.73 GHz to beyond 15 GHz except 5.49–5.94 GHz (−8.6 dB); with the metasurface from 1.71 GHz
  except 5.48–5.73 GHz (−9.2 dB). The metasurface changes the linear |S11| by 0.04 rms.
- Over 6–10 GHz the directivity changes by +0.18 dB on average (between −2.1 and +1.9 dB); the peak goes from 6.7 to
  7.1 dBi.
- At 7.4 GHz the main lobe of the *φ* = 90° cut moves from *θ* = 156° to 6° and gains 0.5 dB.

So the ring surface, as simulated, is not a gain-enhancing metasurface. The draft says so. If the aim is a paper that
claims gain enhancement, the surface has to change (a conductor-backed surface at 10–15 mm with a sub-band claim, or
a cell with an in-phase band inside the operating range), not the wording.

## 3. Paper 1: checks before submission

### 3.1 Check in the CST model (each takes minutes)

1. **Feed gap *p*.** The text says the lower vertex of the octagon is 0.22 mm *above* the ground edge. In the top-view
   screenshot the vertex is hidden in the feed strip and extrapolates to 0.3–0.55 mm *below* the ground edge, with the
   octagon top about 1.2 mm from the board edge (0.78 mm if the text were right). Read the octagon centre coordinate
   and correct *p*, or its definition, and equation (1) with it.
2. **S-parameter reference impedance.** CST normalises a waveguide port to its own line impedance unless "normalize
   to fixed impedance, 50 Ω" is ticked. The line is 50 Ω alone and 40 Ω under the cover, so the two |S11| curves may be
   referred to different impedances. If so, re-export both at 50 Ω: the bands will move.
3. **What Fig. 4 is.** The CST result is "Directivity, Phi=0, Max. Value (Subrange)". It reads −4.5 dBi at 1 GHz, which
   a full cut of total directivity cannot do (an electrically small antenna gives 1.76 dBi in that plane). State the
   θ range and the field component used, or re-export the 3D maximum. The figure now starts at 3 GHz.
4. **Which side *θ* = 0° is** (highlighted in §II-C), and where the 4 × 4 array sits on its board. In the screenshot
   it is not centred, and its lowest row lies over the CPW grounds and the feed.
5. **Why the grounds are 11.2 and 12.2 mm.** The feed is 0.5 mm off the board axis. If it is a drafting slip, make
   them 11.7 / 11.7 mm.

### 3.2 New simulations, by value

1. **Cover-only control**: the stage-2 model without the 16 patches. It decides whether the patches do anything; until
   then the paper can only say "the board", not "the metasurface".
2. **Realized gain and efficiency** against frequency for all three models. The paper reports directivity only; on
   FR-4 with the radiator buried in dielectric, a directivity rise can coexist with a gain fall.
3. Extend the sweep to 18–20 GHz so that the third band has an upper edge, and repeat stage 2 with the time-domain
   solver.
4. Re-tune the slot under the cover (0.65 mm restores 50 Ω). It may close the mismatched regions.
5. Patterns in both planes at 5.3, 9.9 and 13.9 GHz, with cross-polarisation.

### 3.3 References (audited entry by entry against Crossref)

All 21 original references are real. Corrected in the revision: the page range of [12] (1419–1436), the DOIs and
months that were missing, and five statements that did not match the sources (the gain units and the two gain values
of [12]; the size of its FSS; the "air gap" and "9.9" of [15]; the description of [19]; "CPW-fed" for [6]–[9]).
Equation (3) is not in the Sievenpiper journal paper [10]; it is in his dissertation, now cited as [26]. Five
references were added ([20]–[22], [25], [26]), so Ray's two are now [23] and [24]. Still to do by hand:

- [2] (3GPP TS 38.104) needs the version and date you used; a reviewer may prefer TS 38.101-1, the terminal spec.
- [3] and [4] may have been superseded (IEEE Std 802.11-2024; a 2026 edition of IEEE Std 521 is reported). Check.
- [9] is a self-citation in a journal with no DOI and no indexing that could be found. It is the entry a reviewer is
  most likely to query; keep it only if you need it.
- In Table III the spacing of [15] and the board size and spacing of [19] could not be read (shown as "–").
  Fill them in from the PDFs.

### 3.4 The title

The revised paper keeps your title. The body now says plainly that the antenna alone is matched over more spectrum
(10.9 GHz of the 3.42–15 GHz range against 9.4 GHz with the board), so a reviewer may read "tri-band" as a loss and
"metasurface" as too strong for 16 ungrounded patches. `build_paper1.py` holds an alternative (`ALT_TITLE`) that
claims only what the data show; switching is one line.

## 4. Files

| Path | What |
|---|---|
| `ieee_docx.py` | IEEE-conference-format `.docx` writer (two columns, native Word equations) |
| `make_figures.py` | With/without overlays, annotated geometry, cropped patterns |
| `check_numbers.py` | Recomputes every curve-derived number of both papers |
| `data/` | The eight CST curves (digitised) |
| `paper1/build_paper1.py`, `paper2/build_paper2.py` | The papers' text |
| `paper2/design.py` | Design facts of Paper 2; unconfirmed ones are highlighted in the paper |
| `paper2/references.py`, `paper2/literature_text.py` | References (each checked against Crossref) and the review |
| `paper2/mimo_results.py` | Coupling, ECC, DG, TARC, CCL from the `.s4p` exports |
| `*/cst_screenshots/` | The source screenshots |
