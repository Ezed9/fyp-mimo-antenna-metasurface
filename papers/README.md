# The two papers

| | File | State |
|---|---|---|
| Paper 1 | `paper1/Paper1_TriBand_Octagonal_Monopole_revised.docx` (+ `.pdf`) | Revised. Two items are highlighted in yellow (the feed gap *p* and the side of *θ* = 0°); do the checks in section 3 before submitting. |
| Paper 2 | `paper2/Paper2_TwoPort_Decagonal_MIMO_Metasurface.docx` (+ `.pdf`) | Complete, 6 pages, no placeholders. It reports ports 1 and 2 only and claims only what the existing simulations support (section 2). The earlier four-port draft, with the invalid ports 3 and 4, is in `paper2/fourport_draft/`. |

No number in either paper was invented. Curve-derived numbers come from `data/*.csv`, which were digitised from the CST
screenshots (about ±0.1 dB, ±0.02 GHz). `check_numbers.py` recomputes all of them.

## 1. Rebuilding

```bash
pip install numpy scipy matplotlib pillow python-docx scikit-rf      # pandoc is also needed (equations)
python papers/make_figures.py
python papers/paper1/build_paper1.py
python papers/paper2/build_paper2.py          # prints the six values still to be checked in CST
papers/render.sh papers/paper1/*.docx papers/paper2/*.docx           # PDF copies (LibreOffice + libreoffice-math)
```

The `.docx` is the deliverable; the PDFs are previews made with LibreOffice, which draws tall equation delimiters
badly (Word draws them correctly).

Replace a digitised curve by saving the CST export (Post-Processing → Import/Export → Plot Data (ASCII)) under the same
name in `data/`. The loader accepts CST's tab-separated format as it is. Then run `check_numbers.py`: Paper 2's text
updates itself; Paper 1's text is typed, so any number that changed must be edited in `build_paper1.py`.

## 2. Paper 2

### 2.1 What the paper is

The authors decided not to simulate again. The paper was therefore cut down to what the existing CST results support:

- **Ports 1 and 2 only** (the lower row, two 15 mm decagons sharing one ground). Ports 3 and 4 are left out: their
  simulated reflection coefficients exceed 0 dB between 7.3 and 9.8 GHz, which a passive antenna cannot do. The paper
  says the upper-row elements are present, terminated and not evaluated, and says why in the limitations.
- **Title and claims are two-port**, not four-port.
- **ECC, diversity gain and CCL are given as bounds.** The supplied S-parameters are magnitudes only. The phase
  enters the two-port ECC only through |S11*·S12 + S21*·S22|, which cannot exceed (|S11| + |S22|)·|S21|, so the largest
  ECC any phase could give is computed exactly (equation (3) of the paper).
- **Nothing is claimed for the metasurface that the data do not show**: it leaves the match unchanged and changes the
  mean directivity over 6–10 GHz by +0.18 dB.

Headline numbers (all recomputed at build time from `data/p2_*.csv`):

| Quantity | Value |
|---|---|
| Port 1 matched, without / with metasurface | 1.73–5.49 and 5.94 to >15 GHz / 1.71–5.48 and 5.73 to >15 GHz |
| Port 2 matched, with metasurface | 1.72 to >15 GHz |
| Isolation, ports 1–2, with metasurface | 7.6 dB at 1.80 GHz (worst); ≥ 15 dB over 79 % of the range and above 9.5 GHz |
| ECC upper bound | < 0.01 over 89 % of the range; 0.10 at the band edge |
| Diversity gain | ≥ 9.46 dB |
| CCL upper bound | 1.0 bit/s/Hz at the band edge; < 0.4 over 93 % of the range |
| Directivity 6–10 GHz, without → with | mean 4.6 → 4.8 dBi, peak 6.7 → 7.1 dBi |

### 2.2 What a reviewer can still question

No wording removes these; they are properties of the data.

1. **Isolation of 7.6 dB** at the low end, where 15 dB is the usual requirement. The paper states it and names the
   cause (parallel, co-polarised elements on a shared ground, no decoupling structure).
2. **Simulation only**, on FR-4 up to 15 GHz, with directivity instead of gain and no efficiency.
3. **The metasurface gives no benefit.** The paper is an honest negative result on that point.
4. **Coupling and ECC exist only with the metasurface**, so nothing can be said about its effect on them.
5. **Directivity with the metasurface covers 6–10 GHz only.**
6. **Four elements are on the board and two are reported.** The limitations paragraph says the upper-row port results
   failed a passivity check and that the effect of correcting them on ports 1 and 2 is not assessed. That sentence is
   uncomfortable, but it is true, and the results of ports 1 and 2 come from the same run. Deleting it would hide a
   known defect of the simulation; keep it.
7. The two rows have different patch radii (15 and 14 mm) with no stated reason.

### 2.3 Six values to check in the CST model

They are printed in the paper but nobody has read them off the model (`build_paper2.py` lists them on every run):

- lower-row ground width 23.2 mm (assumes the ground edge at x = −1.8 mm, i.e. the 0.3 mm slot);
- gap between patch and ground edge, 0.73 mm;
- spacing of the facing patches of the two rows, about 2.4 mm;
- sideways displacement of the upper half of the board, about 5 mm;
- ring-cell pitch along the columns, about 18.5 mm;
- that the grounds of elements 1 and 2 touch at x = 25 mm and form one conductor (the paper calls it a common ground).

Also confirm that the S-parameters are normalised to a fixed 50 Ω.

### 2.4 If simulation becomes possible again

In order of value: correct ports 3 and 4 (centre each port on its own feed strip; the port mode must be the CPW mode
with a line impedance near 50 Ω) and export the complex S-matrix of both models as Touchstone
(`exports/mimo_noMS.s4p`, `exports/mimo_MS.s4p`); directivity with the metasurface over 1–15 GHz; realised gain and
efficiency; a bare FR-4 board in place of the ring board. `paper2/build_paper2_fourport_draft.py` fills the
four-port coupling and diversity sections from the Touchstone files by itself.

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
| `paper2/design.py` | Design facts of Paper 2, each with its source |
| `paper2/build_paper2_fourport_draft.py`, `paper2/design_fourport_draft.py`, `paper2/fourport_draft/` | The earlier four-port draft |
| `paper2/references.py`, `paper2/literature_text.py` | References (each checked against Crossref) and the review |
| `paper2/mimo_results.py` | Coupling and diversity metrics: bounds from the magnitudes, full values from `.s4p` exports |
| `*/cst_screenshots/` | The source screenshots |
