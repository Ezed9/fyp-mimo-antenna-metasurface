# Presentation Outline (≈ 18 slides, ~15 min)

The figure filenames refer to `figures/*.png` produced by `analysis/make_figures.py`. Show one message per slide, stated in the slide title.

| # | Slide title (the message) | Content | Figure(s) / source |
|---|---|---|---|
| 1 | Title | Project title, names, supervisors (professor + PhD instructor), date | — |
| 2 | Why UWB MIMO + metasurface | UWB 3.1–10.6 GHz. MIMO gives capacity. Compact boards cause coupling. Monopoles radiate both ways, so the gain is low | — |
| 3 | Objectives & specs | S11 ≤ −10 dB over UWB, isolation > 15–20 dB, ECC < 0.01, higher gain from the AMC | targets table, CST_GUIDE §10 |
| 4 | Design flow | Single element → Lg sweep → R sweep → AMC unit cell → single + AMC → 4-port MIMO → MIMO + AMC | flow diagram |
| 5 | Single element geometry | CPW-fed octagon, dimension table, FR-4 1.6 mm | CST screenshot (front, labelled parameters) |
| 6 | **Ground length sets the low-band match** | Lg sweep and the chosen value | `fig_single_Lg_sweep` |
| 7 | **Patch radius controls bandwidth** | R sweep and the chosen value | `fig_single_R_sweep` |
| 8 | Optimized single antenna | S11 band; realized gain and efficiency | `fig_single_final_s11`, `fig_single_final_gain_eff` |
| 9 | **AMC unit cell gives in-phase reflection over X–Y GHz** | Cell geometry, Floquet setup, ±90° band | cell screenshot, `fig_unitcell_reflection` |
| 10 | **AMC raises gain by +N dBi, beating a PEC plate** | No reflector vs PEC vs AMC; gap choice | `fig_single_gap_sweep`, `fig_reflector_compare_s11`, `fig_reflector_compare_gain_eff` |
| 11 | 4-port orthogonal MIMO layout | 90° rotation (polarization diversity), central ground cross, symmetry trick | CST screenshot (top + perspective) |
| 12 | **All ports matched across UWB** | S11–S44 | `fig_mimo_noMS_reflection` |
| 13 | **Isolation > N dB between all ports** | 6 couplings | `fig_mimo_noMS_coupling` |
| 14 | MIMO with AMC: matching & isolation kept | With vs without MS | `fig_mimo_ms_comparison`, `fig_mimo_MS_reflection`, `fig_mimo_MS_coupling` |
| 15 | MIMO gain & efficiency | With vs without MS | `fig_mimo_gain_gain_eff` |
| 16 | Radiation patterns | 4/7/10 GHz, ports 1 & 2 (diversity), with and without MS | `fig_pattern_*` (one 2×3 grid) |
| 17 | Current distribution | Port 1 excited at 4/7/10 GHz; weak current on the other ports | CST surface-current images |
| 18 | **Diversity performance** | ECC (S and far-field), DG, TARC, CCL, MEG, with a summary table | `fig_mimo_ecc`, `fig_mimo_dg`, `fig_mimo_tarc`, `fig_mimo_ccl`, `fig_mimo_meg`, `summary.txt` |
| 19 | Comparison with state of the art | Table: size, band, isolation, ECC, gain, reflector | `LITERATURE.md` |
| 20 | Conclusion & next steps | Key numbers. Next: fabrication + measurement (VNA, anechoic chamber), then journal submission | — |

## Expect these questions
- *Why an AMC and not a metal plate?* → Slide 10: the PEC comparison at the same gap.
- *Why are the grounds connected?* → Real devices share one ground. Isolated grounds give unrealistically good isolation.
- *ECC from S-parameters assumes a lossless antenna. Is that valid on FR-4?* → We also report far-field ECC.
- *Is the gain improvement flat across UWB?* → No. State the band where it is ≥ +2 dB and explain the AMC phase limit.
- *Mesh convergence?* → S11 at 15 vs 25 cells/λ differs by < 1 dB.
- *Any measurement?* → Planned. Name the fabrication date.
