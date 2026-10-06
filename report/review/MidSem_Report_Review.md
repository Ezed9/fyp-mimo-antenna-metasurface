# Mid-Semester Report Review: Figures, Page Budget, Technical Rigor

Reviewed: `report/MidSem_Report.pdf` at commit `46b0263` (7 pages), built by `report/build_report.py` and
`report/docx_helpers.py`.

**How it was checked**

- Rendered all 7 pages and every source figure. Figure text size on paper was measured from glyph heights in pixels.
- Digitized the single-curve CST plots to compare the numbers in the text with the plots themselves.
- Rebuilt the report with LibreOffice 24.2 and Liberation Serif, which has the same metrics as Times New Roman.
  The unchanged code reproduces your PDF to within 2 pt per page. Page-fit figures below should therefore hold on
  your machine to about ±0.03 in.
- Every change proposed here was built and measured. Every variant comes out at exactly 7 pages, with no orphan
  headings and no spill-over.

## Bottom line

1. **The 7-page rule is met, but the layout is not balanced.** Page 3 is 45 % empty and the title page ends with
   3.1 in of blank space, while pages 4–5 squeeze the figures.
2. **Every CST plot is unreadable on paper:** Figs. 2(b), 3(a), 3(b), 4(b) and 5(b). Their tick labels print at
   1.1–1.5 pt. Even at the full 6.0 in text width they would reach only 2.9 pt. No width setting fixes this; the
   plots must be regenerated from CST data (see P1).
3. **More serious than either:** several sentences contradict the report's own figures, and Table 1 misreports two
   cited papers. The metasurface results described as "verified" have not been simulated yet: your own Fig. 1,
   Table 1 and study pack mark them "in progress" or "pending". An examiner comparing text with figures will find
   these. Fix P0 first.
4. **Your study pack is more accurate than the report.** It already states the R-sweep gap coupling (§2.4), the
   boundary optima (§2.7), the interpolation artefacts (§2.8) and the f_L check (§3.1). The condensation to 7 pages
   lost these points and introduced claims the figures do not support.

## What is on this branch

| Item | State |
|---|---|
| Layout fixes in `report/build_report.py` and `report/docx_helpers.py` | **Committed.** Verified at 7 pages. |
| [`content_fixes.patch`](content_fixes.patch): every text and table correction in P0/P3 | Opt-in. Verified at 7 pages. |
| [`report_figures.patch`](report_figures.patch): report-sized replots from CST ASCII exports | Opt-in. Needs your CST exports. |
| `report/MidSem_Report.docx` and `.pdf` | **Not rebuilt.** This sandbox has no Times New Roman. Rebuild on your machine. |

Apply a patch from the repo root, then rebuild:

```bash
git apply report/review/content_fixes.patch
uv run report/build_report.py        # or: cd report && python build_report.py  (needs pillow now)
```

---

## P0: Fix before submission (correctness and integrity)

### P0-1. Metasurface results are claimed but do not exist yet

The report states these results as done:

- **Abstract:** "provides in-phase reflection to substantially boost forward broadside gain without impedance
  detuning".
- **§7:** "Full-wave CST simulations verify that near-field metasurface loading preserves |S11| ≤ −10 dB … while
  substantially enhancing forward broadside gain (Fig. 5(b))".
- **Work Done:** "its loaded S11 performance evaluated".
- **Challenges:** "re-tuning Lg preserves matching" and "unit cells were characterized with Floquet ports".

The evidence says otherwise:

- Fig. 1 marks *5. Metasurface SRR unit cell* and *6. Metasurface loaded S11* as **In progress**.
- Table 1 says "→ pending".
- `MIDSEM_STUDY_PACK.md` §2.9 lists both the unit cell and the antenna + metasurface run as "status: pending".
- **Fig. 5(b), cited as the evidence, is the gain of the antenna alone.** It contains no metasurface, and no
  loaded-S11 plot exists anywhere in the report.

**Fix.** If you have the loaded-antenna results, add the figure and the numbers. If not, describe the work as in
progress. The content patch does this and retitles §7 "Metasurface Reflector Integration (In Progress)".

### P0-2. The baseline S11 description is false (§3, Fig. 2(b))

**The text says** "|S11| above −10 dB (−3 to −8 dB) across almost the entire spectrum".

**The plot shows (digitized):**

- |S11| stays between −2.3 and −7.5 dB from 2.0 to 7.7 GHz.
- It then dips below −10 dB over three intervals: 7.7–9.3 GHz (**−45 dB at 8.56 GHz**), 10.1–11.4 GHz and
  14.1–15.9 GHz.
- In total, 34 % of 2.16–15.73 GHz is matched.

The −45 dB notch is the most visible feature in the figure. The same wrong description appears in
`MIDSEM_STUDY_PACK.md` (§2.2b, "stayed completely above the −10 dB threshold"). Fix it there before the viva.

### P0-3. The R-sweep text contradicts Fig. 3(b)

**The text says** "For R = 4–8 mm, modes resonate above 6 GHz. Increasing R … shifting the lower cutoff downward".

**The plot shows:**

- Every R from 4 to 15 mm has its first resonance at 2.3–2.7 GHz, below −10 dB.
- Increasing R moves that resonance slightly **up**, from ≈ 2.3 to 2.73 GHz.
- What R actually changes is the mid-band match: small patches leave much of 3–12 GHz at −3 to −9 dB.

The patch centre is fixed at 8 mm, so R also sets the feed gap: p ≈ 11.2 mm at R = 4 mm, 0.73 mm at R = 15 mm.
This sweep is therefore partly a gap sweep. The study pack says so (§2.4); the report should too.

### P0-4. Table 1 misreports two cited papers

These rows were checked against your own `report/literature.py` and the publishers' abstracts.

| Row | Report says | Source says |
|---|---|---|
| Hussain 2023 [11] | 1-port UWB disc, 3.4–10.6 GHz, 8 × 8 slotted FSS, 2.2 → 8.4 dBi | CPW-fed hexagonal patch with stubs, 5–17 → 3–18 GHz, 5 × 5 ring-frame FSS, 6.5 → 10.5 dBi |
| Al-Gburi 2022 [10] | 3.08–11.5 GHz, "cross-loop" FSS, 0.10λL | 2.2–11.9 GHz measured with the FSS; patch + circular-loop cells; 10 mm *total profile* = 0.07λ at 2.2 GHz |
| Wu 2023 [13] | "2-port CPW monopole", "Integrated" | `literature.py` marks antenna type and placement *unverified*; the abstract does not settle them |

- "2.2 → 8.4 dBi" and "8 × 8" are Hammache 2024's numbers. The report does not cite that paper.
- "3.08" is Hasan's lower band edge.
- The narrative's "4.5–6 dB gain boosts" should read +4.8 dB (Al-Gburi) and +4.0 dB (Hussain).

### P0-5. "Covers 2.1–15 GHz" is false by the report's own numbers

- The lower −10 dB edge is 2.1615 GHz, which is above 2.1 GHz. Yet the Abstract, §1, §6, Table 2 ("Exceeds") and the
  Outcomes all say 2.1–15 GHz is covered.
- Table 2's FBW spec "≥ 109 %" is the FBW of the FCC 3.1–10.6 GHz band (109.5 %), a leftover. A 2.1–15 GHz target
  would require ≥ 150.9 %.

**Fix:** make the target 2.2–15 GHz. That needs ≥ 148.8 % FBW, which your 151.7 % meets. See *Where I disagree*.

### P0-6. Sweep artefacts are shown while the text says they were resolved

Fig. 3(a) contains three non-physical features:

- One trace jumps to **+10 dB** at 4.0 GHz and decays to 0 dB at 6.2 GHz. |S11| > 0 dB is impossible for a passive
  antenna.
- Both sweeps have steps at 4.0 and 6.2 GHz.
- There is a spike to 0 dB near 7.2 GHz.

The Challenges bullet nevertheless says "refined mesh passes resolved these". Steps at the same frequencies across
many curves are *frequency-sweep interpolation* artefacts, not mesh artefacts. The study pack (§2.8) says the same.

The colour cycle makes it worse. CST cycles through 7 colours, so the +10 dB trace is blue, the same blue as your
optimum Lg = −7 mm and as Lg = −17.1 mm. In Fig. 3(b), R = 15 mm shares brown with R = 6.44 mm. A reader cannot tell
the optimum from the corrupted trace.

**Fix:** re-run both sweeps with more frequency samples, or cross-check with the time-domain solver, and re-export.
Until then, say so in the caption; the content patch does.

---

## P1: Figure legibility (item 1 of your brief)

### Why resizing cannot fix the CST plots

The CST screenshots are 2288 × 959 px with 11 px-tall tick digits (8 pt Tahoma captured from a ≈ 24 in wide
window). This is how large that text prints:

| Printed width | 2.3 in (now) | 2.9 in | 3.9 in | 6.0 in (full text width) |
|---|---|---|---|---|
| Tick-label font size | 1.1 pt | 1.4 pt | 1.9 pt | 2.9 pt |

IEEE asks for 8–10 pt; your captions are 9 pt. Even a full-width plot would print at a third of the minimum.

### Figure by figure

| Fig. | Panel (file) | Width now | Text on paper | Problems | Committed change |
|---|---|---|---|---|---|
| Title | crest `nits_logo.png` (316 × 315 px) | 1.35 in | — | none; 180 dpi at the new size | 1.75 in. A ≥ 600 px crest would print the ring text more crisply. |
| 1 | workflow `fig_design_flow.png` (8.5 pt text on a 4.85 in canvas) | 3.5 in | 6.1 pt | readable but small | **4.6 in → 8.1 pt** |
| 2(a) | `cst_initial_antenna.png` | 1.4 in | — | no dimensions | 1.55 in; white strip above the patch cropped |
| 2(b) | `cst_initial_ground_s11.png` | 3.0 in | 1.5 pt | illegible | 3.9 in; plot title cropped (1.9 pt). Replot. |
| 3(a) | `cst_single_Lg_sweep.png`, 10 curves | 2.3 in | 1.1 pt | illegible; colours repeat; artefacts | 2.85 in, title cropped (1.4 pt). Replot with 5 curves. |
| 3(b) | `cst_single_R_sweep.png`, 13 curves | 2.3 in | 1.1 pt | illegible; R = 15 mm and R = 6.44 mm are both brown; legend order non-monotonic (two runs merged) | 2.85 in, title cropped. Replot. |
| 4(a) | `cst_single_geometry.png` with baked-in "(a) Front / (b) Back" | 2.0 in | labels 3.6 pt | labels clash with the report's own (a)/(b); the back view is a blank square | **front view only, labels cropped**, 1.5 in |
| 4(b) | `cst_single_final_s11_markers.png` | 2.3 in | 1.1 pt | illegible; marker table overlaps the frequency axis and is cut off at the image edge | 2.9 in, title and one-entry legend cropped. Replot. |
| 5(a) | `cst_ms_array.png` with baked-in labels | 1.9 in | labels 3.6 pt | the ring splits are invisible even at native resolution | both views, labels cropped, 2.65 in, subcaption "(a) front (left) and copper back (right)" |
| 5(b) | `cst_single_final_gain_ieee.png` | 2.3 in | 1.1 pt | illegible | 2.85 in, title and legend cropped. Replot. |

**Subcaptions.** The old helper placed both images in equal 3.0 in columns, so a narrow image floated in a wide cell
and each pair looked off-centre. In Fig. 2, panel (a) had 0.8 in of padding on each side while (b) had none. Each
column is now its image width plus a 0.12 in gutter. Subcaptions sit centred under their own image, and none wrap.

### Committed code: the exact calls

Crops run at build time with Pillow (`dh._picture`); the PNGs in `figures/` are never modified. Crop boxes are
`(left, top, right, bottom)` in source pixels, measured from the images. They are defined once at the top of
`build_report.py`:

```python
CROP_SWEEP = (8, 64, 2288, 950)          # Lg and R sweeps: keep the legend right of the frame
CROP_S11_BASELINE = (8, 64, 2266, 950)   # its legend sits inside the frame
CROP_S11_MARKERS = (8, 64, 2180, 959)    # keep the marker table at the bottom edge
CROP_GAIN = (8, 64, 2181, 950)
CROP_INITIAL_ANTENNA = (0, 44, 955, 954)  # white strip above the patch
CROP_GEOMETRY_FRONT = (30, 30, 563, 452)  # front view only: the back face has no metal; drops "(a) Front"
CROP_MS_FRONT_BACK = (30, 30, 985, 452)   # both views, without the baked-in "(a)/(b)" labels
```

```python
c.fig(["fig_design_flow.png"], "...", width=4.6)                                    # Fig. 1 (was 3.5)
c.fig_two("cst_initial_antenna.png", "cst_initial_ground_s11.png", "...",           # Fig. 2 (was 1.4 / 3.0)
          width1=1.55, width2=3.9, crop1=CROP_INITIAL_ANTENNA, crop2=CROP_S11_BASELINE)
c.fig_two("cst_single_Lg_sweep.png", "cst_single_R_sweep.png", "...",               # Fig. 3 (was 2.3 / 2.3)
          width1=2.85, width2=2.85, crop1=CROP_SWEEP, crop2=CROP_SWEEP)
c.fig_two("cst_single_geometry.png", "cst_single_final_s11_markers.png", "...",     # Fig. 4 (was 2.0 / 2.3)
          width1=1.5, width2=2.9, crop1=CROP_GEOMETRY_FRONT, crop2=CROP_S11_MARKERS)
c.fig_two("cst_ms_array.png", "cst_single_final_gain_ieee.png", "...",              # Fig. 5 (was 1.9 / 2.3)
          width1=2.65, width2=2.85, crop1=CROP_MS_FRONT_BACK, crop2=CROP_GAIN,
          subcap1="(a) front (left) and copper back (right)")
```

`dh.two_images` now asserts `width1 + width2 + 2 × gap ≤ 6.0 in`, with `gap = 0.12`. It also writes its table
properties in the order the OOXML schema requires. Before, `tblBorders` came after `tblLook` and `shd` after
`vAlign` in 22 places; LibreOffice ignores this, but Word can report "unreadable content".

**Why not larger?** After these widths, page 4 has 0.37 in to spare and page 5 has 0.26 in. On a plot with a
2.4:1 aspect ratio, every extra 0.1 in of width costs 0.04 in of height. Fig. 4(b) could reach 3.2 in (leaving
0.13 in on page 5), but I would keep at least 0.2 in because your Times New Roman / LibreOffice 26.2 build can
differ by a line.

### The real fix: replot from CST data (`report_figures.patch`)

1. **Re-run the sweeps** with more frequency samples (P0-6).
2. **Export the data.** For each result, use *Post-Processing → Import/Export → Plot Data (ASCII)* and save into
   `exports/` under the names `CST_GUIDE.md` §9 already defines: `single_Lg_sweep.txt` (all Lg curves in one file),
   `single_R_sweep.txt`, `single_final_s11.txt` and `single_final_gain.txt`.
3. **Generate the panels.** Run `git apply report/review/report_figures.patch`, then
   `cd analysis && uv run python make_figures.py`. The patch adds `fig_report_rows()`, which writes
   `figures/rep_*.png`:
   - each panel is drawn at its exact printed size, with 7 pt labels, 6.5 pt ticks and 6 pt legends;
   - each sweep shows 5 representative curves, with distinct colours **and** line styles;
   - every panel has a −10 dB line and the 2.16–15.73 GHz band shaded;
   - band edges and resonance frequencies are read from the data and labelled.
4. **Point the builder at the new panels.** The widths must stay equal to `REPORT_SIZE` in `make_figures.py`, and the
   crops are dropped for the replaced panels:

```python
c.fig_two("cst_initial_antenna.png", "rep_baseline_s11.png", "...", width1=1.55, width2=3.9, crop1=CROP_INITIAL_ANTENNA)
c.fig_two("rep_Lg_sweep.png", "rep_R_sweep.png", "...", width1=2.85, width2=2.85)
c.fig_two("cst_single_geometry.png", "rep_final_s11.png", "...", width1=1.5, width2=2.9, crop1=CROP_GEOMETRY_FRONT)
c.fig_two("cst_ms_array.png", "rep_final_gain.png", "...", width1=2.65, width2=2.85, crop1=CROP_MS_FRONT_BACK,
          subcap1="(a) front (left) and copper back (right)")
```

**What was tested:**

- The function runs through your existing `read_cst_ascii` parser on synthetic CST-format files and inside
  `make_figures.py --demo`.
- The 9 analysis tests still pass.
- A report build with panels of exactly these sizes is 7 pages, with 0.23 in to spare on page 5.

**Not yet tested on your real exports.** Once you have them, check the legend placement (use the `legend={...}`
argument) and the gain axis label. CST "Gain" is IEEE gain; "Realized Gain" includes mismatch.

`two_images` does not skip missing files, so switch the build lines only after the `rep_*.png` files exist.

### Other figure content gaps (not patched)

- **No figure gives a single dimension.** Add a dimension table or a labelled drawing: R, Lg, p, the 3.0 mm strip,
  the 0.5 mm slots, the 50 × 50 mm board.
- **The SRR unit cell is undefined.** Its ring radii, width, split and period are "[fill in]" in the study pack and
  absent from the report. Without a close-up, Fig. 5(a) looks like closed concentric rings, not split rings.
- **A better source for Fig. 4(b) exists.** `cst_single_final_s11_bandwidth.png` marks the −10 dB edges (2.1615 and
  15.734 GHz), which proves the bandwidth claim better than the markers plot. Delete its stray −21.731 dB marker
  line before re-exporting.

---

## P2: Page budget (item 2 of your brief)

Free space below the last line on each page, in inches. "Before" is my rebuild of `46b0263`; your PDF reads 3.10,
0.73, 3.70, 0.98, 0.84, 1.57 and 1.69.

| Page | Content | Before | Layout commit | + content patch | + optional gap-phase figure |
|---|---|---|---|---|---|
| 1 | Title | 3.09 (top-heavy) | 1.28 | 1.28 | 1.28 |
| 2 | Abstract, (Keywords), Introduction | 0.75 | 0.75 | 0.35 | 0.35 |
| 3 | Literature Review, Table 1, Research Gap | **3.68** | 3.93 | 2.84 | 0.32 |
| 4 | Methodology 1–4, Figs. 1–2 | 0.95 | 0.37 | 0.37 | 0.37 |
| 5 | Methodology 5–7, Figs. 3–5 | 0.81 | 0.26 | 0.24 | 0.24 |
| 6 | Work Done, Table 2, Work Plan | 1.56 | 1.56 | 1.12 | 1.12 |
| 7 | Expected Outcomes, References | 1.69 | 1.69 | 0.84 (15 refs) | 0.84 |

- **No layout defects.** No variant has an orphan heading, a stranded line or an 8th page. Headings are
  keep-with-next, and every page was checked visually.
- **Page 3 is the weak spot.** Fill it with substance, not spacing. Both options below are verified:
  - The content patch adds two rows to Table 1. **Sen 2017** placed an SRR metasurface behind a UWB monopole; it is
    the paper an examiner is most likely to raise against your novelty claim. **Hammache 2024** is the source of your
    "20 mm" figure.
  - The computed chart `fig_gap_phase.png` (see *Optional extras*) fills most of the rest.
- **Title page (committed).** Content used to end 6.9 in from the top. The logo is now 1.75 in (was 1.35 in) and the
  spacing is spread over the page.
- **Table 1 header (committed).** "Enhance-ment" and "Isolati-on" broke mid-word because their columns were 0.65 in
  and 0.50 in, while the words need 0.80 in and 0.56 in. New widths: `[0.95, 0.9, 0.72, 1.2, 0.78, 0.82, 0.63]`.
- **Page-count check (committed).** It used to print SUCCESS for any count ≤ 7; it now warns unless the count is
  exactly 7.
- **Optional:** the template's Heading 1 has 24 pt space-before. Every page-opening section heading therefore sits
  0.33 in below the top margin on pages 2, 3, 4, 6 and 7. Zeroing it frees 0.33 in on each of those pages (code
  under *Optional extras*).

---

## P3: Technical rigor and references (items 3–4 of your brief)

| Check from your brief | Result |
|---|---|
| "FCC 2002" or "O1/O2" tags | None remain ✓ |
| Band given as 2.1–15 GHz | False at the lower edge (P0-5) |
| Remaining 3.1–10.6 GHz framing | 5 places: Research Gap (3), §6 gain, Fig. 5 caption, Table 2 gain row, Table 2 "0.04λ0 at 3.1 GHz". Plus "≥ 109 %". |
| Optimization narrative order | Workflow → setup → baseline (Lg = −20 mm) → Lg sweep → R sweep → final → metasurface ✓. Content is wrong in places (P0-2, P0-3). |
| Work Plan format | One paragraph; no table, dates or numerical targets ✓. It skips the pending metasurface work (unit cell, loaded S11/gain, metal-plate baseline), which has to come first. |
| In-text citations vs. bibliography | [1]–[13] all cited, numbered by first appearance ✓; pairs written "[1], [2]" ✓; no uncited entries ✓ |
| IEEE reference format | Correct throughout ✓ (abbreviated journals, vol./no./pp., month abbreviations, DOIs). Three entry-level issues below. |

### Smaller technical items

Items 1–13 are fixed in `content_fixes.patch` unless marked otherwise.

1. **Gain is quoted only over 3.1–10.6 GHz** (2.9–4.9 dBi). Over your operating band it is **1.4–5.1 dBi**
   (1.4 dBi at 2.16 GHz; ≥ 2.8 dBi above 3 GHz). "Peak 5.09 dBi" was read off a plot (±0.1 dB per
   `literature.py`); write "≈ 5.1 dBi".
2. **The matching margin is thin.** The shallowest in-band points are −10.3 dB at 6.45 GHz and −10.5 dB at 12.2 GHz.
   State this; fabrication tolerances will probably split the band there. Table 2's "Deepest return loss ≥ 10 dB →
   Exceeds" is a meaningless spec; it is replaced by the shallowest point.
3. **Coordinates are mixed.** "centre x_p = 8 mm" appears beside "grounds at y = −20 mm", but in your CST model both
   are along x (study pack, viva section E). "Ground length Lg = −7 mm" is a negative length: Lg is the ground-edge
   *position*, and the ground is 18 mm long.
4. **"10 steps" is wrong:** it is 10 values, i.e. 9 steps of 1.44 mm.
5. **Both optima sit at geometric limits.** The feed gap p closes at Lg = −6.27 mm, and at Lg = −7 mm the patch would
   touch the ground at R = 15.77 mm. Say this before the examiner does.
6. **"50 Ω CPW" is unsupported.** Quasi-static CPW formulas (Simons [5]) give ≈ 58 Ω for a 3.0 mm strip with 0.5 mm
   slots on 1.6 mm FR-4 (εr 4.3), or ≈ 55 Ω allowing for 35 µm copper; 0.3 mm slots would give ≈ 50 Ω. Quote the
   line impedance CST reports for the port. The patch writes "waveguide port referenced to 50 Ω" instead.
7. **The f_L formula appears without units or definitions.** With the decagon's real height (L = 2 × apothem
   = 2.85 cm), area-equivalent radius r = 0.37 cm and p = 0.07 cm, f_L = 7.2/(L + r + p) = 2.19 GHz, against
   2.16 GHz simulated. Your study pack §3.1 has the same calculation (≈ 2.18 GHz) but the report does not. Ray's
   printed-substrate factor k ≈ 1.15 would give 1.9 GHz; be ready for that question in the viva.
8. **Table 2's air gap is mis-framed.** "Metasurface profile … Achieved" is a design value, not a result. Two
   wavelength normalizations are mixed (0.03λL and 0.04λ0 at 3.1 GHz); use 0.028λ at 2.16 GHz.
9. **Table 2 is never cited in the text**, which IEEE style requires.
10. **The Keywords line is missing**, although your page plan expects one.
11. **The research gap overclaims:**
    - "no reported design under a sub-4 mm profile" is a universal claim drawn from a 10-paper review;
    - "9–20 mm" relies on Hammache, whom the report does not cite;
    - "bridges this gap with … full UWB MIMO coverage" — the MIMO antenna has not been designed yet.
12. **Expected outcome 3 presupposes its result:** "confirming that the AMC metasurface significantly outperforms
    a metal plate".
13. **Wrong term in the §7 heading:** "Metamaterial (Metasurface)" — a metasurface is not a metamaterial.
14. **Heading numbering is inconsistent** (*not patched*). Methodology subsections are numbered "1."–"7." under an
    unnumbered section, while all other subsections are unnumbered. Use 3.1–3.7 or drop the numbers.
15. **The physics question you will get.** In-phase reflection needs φR ≈ 2k0h, which *rises* from 20° to 147°
    across 2.16–15.73 GHz. A passive resonant surface's phase *falls* with frequency (Foster's reactance theorem), so
    a single-resonance SRR can meet the ±90° window over only part of the band. Have an answer ready: graded splits as
    in Sen 2017, dual resonances, or accepting a sub-band.
16. **`analysis/make_figures.py` still uses `UWB = (3.1, 10.6)`** for band shading and sweep ranking (*not patched*;
    the new `fig_report_rows` uses the 2.16–15.73 GHz band).
17. **The supervisor's signature line is gone** (*not patched*). The builder deletes the template's "SUPERVISOR'S
    SIGNATURE" line; check whether your department expects it on the mid-sem report.

### Reference entries

- **[7]** "N. G. Alexópolous" mixes two spellings. IEEE Xplore and the DOI record list "N. G. Alexopolous" (his name
  is Alexópoulos). The patch uses IEEE's form.
- **[10]** The page range "1425–1436" looks wrong. Indexes give the article as 18 pages, which matches
  **1419–1436**, and your own reading notes cite p. 14 of the PDF, which a 12-page range cannot contain. Verify on
  the publisher's page (blocked from my sandbox); the patch uses 1419–1436.
- **[8]** Pendry is cited for AMC in-phase reflection, but it is the SRR paper. Cite it where the SRR is introduced
  (*not patched*). Consider adding Yang & Rahmat-Samii (2003) for the ±90° criterion; it is already in
  `literature.py` as `yang`.

---

## Where I disagree with the brief

1. **"2.1 GHz to 15 GHz wideband coverage."** Your antenna starts at 2.16 GHz, and 2.1615 rounds to 2.2, not 2.1.
   "Covers 2.1–15 GHz" and "Exceeds" in Table 2 are factual errors an examiner can see in Fig. 4(b). You have two
   honest options:
   - change the target to 2.2–15 GHz (my recommendation, and what the patch does; you still exceed it), or
   - keep 2.1 GHz and write "not met at the lower edge (2.16 GHz)".

   Either way, the introduction must say *why* this band, i.e. which systems need it. Without the FCC band the
   target currently reads as if it were chosen after seeing the result.
2. **"Exactly 7 pages" with a fixed page plan.** The forced breaks leave page 3 half-empty while pages 4–5 are full.
   If 7 pages is only an upper limit, dropping the break before "Work Done" would rebalance the pages. If it is
   exact, fill page 3 with substance (the verified options above).
3. **Figure numbering.** Adding the gap-phase chart to page 3 makes it Fig. 1 and shifts the others by one. The
   builder renumbers automatically, but your figure list in the brief would change.

---

## Optional extras (verified, not applied)

**Gap-phase chart on page 3.** Apply this on top of `content_fixes.patch`. It leaves 0.32 in on page 3 at 4.1 in;
4.3 in leaves 0.21 in.

In `literature_review()`, change point (1) of the research-gap paragraph to reference the figure, then add the
figure right after the paragraph:

```python
        f"[@algburi2022, hussain2023, hammache2024], and none approaches a sub-4 mm gap, where a metal plate is out of phase below 9.6 GHz "
        f"(Fig. {c.next_fig()}); (2) neither paper read in full "
...
    c.fig(["fig_gap_phase.png"], f"Reflection phase needed for in-phase addition at h = {lit.GAP_MM} mm (2k_{{0}}h, with the ±90° window) "
          "against a metal (PEC) plate; computed from the ray model, not simulated.", width=4.1, crop=(22, 20, 1592, 836))
```

**Remove the 0.33 in gap above page-opening headings.** In `build()`, just before `dh.page_number_footer(doc)`, add
the loop below, plus `from docx.shared import Pt`:

```python
    for h in ("Abstract", "Literature Review", "Methodology / Proposed Work", "Work Done Till Mid-Semester", "Expected Outcomes"):
        _heading_par(doc, h).paragraph_format.space_before = Pt(0)  # page-opening headings: no gap under the top margin
```

## Verification log

- My rebuild of `46b0263` matches the committed PDF to within 2.2 pt per page.
- **Layout commit:** 7 pages. Both `build_report.py` and `build_literature_review.py` run under `uv run` with their
  own declared dependencies; Pillow is imported only when a crop is used. The DOCX has 0 schema-order violations
  (22 before).
- **Layout + `content_fixes.patch`:** 7 pages; both patches `git apply --check` clean on this branch.
- **`report_figures.patch`:** `make_figures.py --demo` writes all five `rep_*.png` at the exact sizes; 9/9 analysis
  tests pass; a build using them is 7 pages.
- **Digitized values:**

  | Plot | Values |
  |---|---|
  | Final S11 | −10 dB edges 2.162 and 15.724 GHz (CST markers 2.1615 and 15.734); shallowest −10.31 dB at 6.45 GHz and −10.48 dB at 12.20 GHz |
  | Baseline (Lg = −20 mm) | 34 % of the band matched; −45.2 dB at 8.56 GHz |
  | Gain | 1.38–5.13 dBi over 2.16–15.73 GHz; 2.85–4.92 dBi over 3.1–10.6 GHz |
