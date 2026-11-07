# Next design: what to build instead of "octagon + patch metasurface"

**Why this file exists.** The octagon (or decagon) monopole with a square-patch or split-ring metasurface behind it is
already published: AboEl-Hassan 2025 (octagon + AMC), Kumari 2024 (octagonal fractal MIMO + metasurface), and more than
40 UWB-monopole + FSS papers by 2021. The team needs a design that is **different, better, and still theirs to publish**.

**How it was found.**
- Two literature sweeps, about 150 searches in total, covering single-antenna reflectors and MIMO with metasurfaces.
- Seven independent "vetting" agents, one per candidate direction. Each searched for prior art that would kill its idea
  and checked the physics numerically.
- A dedicated prior-art check on the winner.
- Analytical models, checked against the team's own openEMS gap study (GAP_STUDY.md):
  - transmission-line AMC, Langley–Parker FSS, image theory;
  - a spectral-integral dipole-over-surface model, which reproduces the full-wave S11 failure bands at 13.2, 23.2 and
    33.2 mm;
  - a circuit-model polarization-conversion metasurface (PCM).

No full-wave simulation was run in this session: building openEMS was not permitted here. **Every number below is a
first-order estimate (about ±10–15 % in frequency) that CST must confirm.** Several publisher sites were blocked, so some
prior art was judged from abstracts. Before submitting, rerun the IEEE Xplore/Scopus queries given in §5.

---

## 1. The lesson that kills most "monopole + reflector" ideas

| Fact | Consequence |
|---|---|
| A plain **copper plate ~11 mm** behind a UWB monopole gives +1.4 to +6 dB broadside over 3–11 GHz (image theory) | Any metasurface reflector must beat a **plate at the same gap**, or a reviewer will ask why not use a plate. Most published FSS reflectors work only because their gap is ≈ λ/4 at mid-band, where a plate works too. |
| A thin passive reflector cannot stay in phase over an octave (Foster; Brewitt-Taylor). A single 1.6 mm FR-4 AMC covers only 20–35 %. | "Low-profile metasurface + full UWB gain" is physically impossible. Pick a ≤ 2.5:1 band, or change what the metasurface does. |
| A ground-backed layer close behind a monopole collapses its low-band resistance (R/R0 ≈ 0.05 at 4 mm, 3.1 GHz) | This is exactly why the team's 2 mm designs lost the low band and went tri-band. |
| The bare monopole's **broadside** gain falls to −5…−17 dBi above 6 GHz (its pattern tilts toward the board plane) | No reflector can make broadside gain flat across UWB. Quote realized gain vs frequency, not one peak value. |

---

## 2. Ranking

| Rank | Concept | Novelty (after prior-art hunt) | Physics | Feasible in CST, FR-4, 8–12 wk | Fits "Wideband MIMO Antenna with Metasurface" |
|---|---|---|---|---|---|
| **1** | **Mirrored polarization-conversion metasurface (PCM) behind a co-polarized 2-port wideband MIMO** | **Partly novel; the core mechanism is not found anywhere** | Sound over ~3.3–7.5 GHz | Yes | **Exactly**: the metasurface does the MIMO job |
| 2 | 2-port MIMO whose radiators **are** CPW-slot-fed 4×4 patch metasurfaces (your patch array becomes the antenna) | Partly novel (incremental) | Sound if the cell is scaled to a ~12 mm period on an air-loaded 3.9 mm stack | Yes (CMA helps) | Yes |
| 3 | AMC-backed printed monopole pair for **UWB angle-of-arrival** (IEEE 802.15.4z channels 5 + 9) | Narrowly novel | Sound (4.9 mm profile vs 12.4 mm for a λ/4 plate) | Yes, but angle accuracy needs a turntable | Partly (34 % band) |
| 4 | Re-tune the existing tri-band design to the **6G FR3 candidate bands** (WRC-27: 4.4–4.8, 7.125–8.4, 14.8–15.35 GHz) | Only the band plan is new | Already works roughly | Easiest | Weak |
| ✗ | Band-split / dichroic FSS reflector | **Not novel** (Yahya 2016–18, Pasian 2010, Chatterjee 2022); loses to a plate | – | – | – |
| ✗ | Dual-polarized polarimetric GPR pair + shared reflector | **Not novel** (Yahya ~2017, Ojaroudi Parchin 2019/2022; Sun 2021 for the GPR use) | No thin reflector covers 2–8 GHz | – | – |
| ✗ | One un-grounded layer for notch + gain + isolation | Notch part = Zhu 2023 | **Gain part fails** (Foster), isolation changes < 1.5 dB | – | – |

The absorber-backed GPR MIMO is still under review; see §6.

---

## 3. Recommended design: mirrored-PCM co-polarized wideband MIMO

### 3.1 The idea in one paragraph
Two **identical, parallel, same-polarization** CPW monopoles share one metasurface reflector placed close behind them.
The reflector is a **polarization-conversion metasurface**: its anisotropic cells reflect an x-polarized wave as
y-polarized, and the reverse. The left half has its cells rotated **+45°** and the right half **−45°**, mirror images of
each other.
- Port 1 radiates (direct + converted) = (a, 1) and port 2 radiates (−a, 1). These are **orthogonal whenever the
  conversion is complete (|a| = 1), whatever the phase**. Two co-polarized elements therefore become
  polarization-diverse without rotating them 90°, which gives broadband low ECC.
- The co-polarized image is suppressed, so the backing does **not** short the monopole's low band at a small gap the way
  copper or an AMC does (R/R0 ≈ 1.0 vs 0.05 for PEC at 4 mm, 3.1 GHz). Profile ≈ 0.11λ at 3.1 GHz.
- PCM conversion depends on the **phase difference** of the cell's two axes, not on in-phase reflection. That is why it
  survives over ~2.3:1, where an AMC manages only 20–30 %.

### 3.2 What is new, and what you must cite as already known
- **New** (not found in 31 + 33 targeted searches):
  - one PCM split into mirrored ±45° halves, used as a **port-selective polarization assigner** for co-polarized MIMO;
  - using this as a **broadband ECC-reduction method** in a compact wideband MIMO on FR-4.
- **Cite as the base:**
  - Sahu & Mishra, IEEE AWPL 22(1):194, 2023 (PCM under a monopole; cell orientation sets the CP handedness, single
    port);
  - Lail & Han, ACES J. 2022 (polarization-converting ground keeps bandwidth at ~λ/10 where a PEC fails);
  - W. Yang et al., IEEE TAP 2014/2015 (polarization-rotation AMC dipoles);
  - Wang & Zhang, IEEE Access 9:44881, 2021 (dual-CP 2-port with a PCM, but orthogonal feeds).
- **Do not claim:** "PCM gives low profile" (known physics) or "dual-CP MIMO" (exists).

### 3.3 Starting dimensions (estimates; tune in CST)
| Item | Value |
|---|---|
| Elements | 2 × the team's CPW octagon, ~27×31 mm, R ≈ 8.7 mm (check its bare band first). Use a CPW slot of 0.3 mm, not 0.5 mm, to get 50 Ω instead of 58 Ω. |
| Layout | Side by side, **same orientation**, centre spacing 35 mm (sweep 25–45), one 70 × 40 mm FR-4 board |
| Gap, antenna copper → PCM copper | ≈ 4 mm (1.6 mm substrate + 2.4 mm air), sweep 3–6 |
| PCM sheet | 0.8 mm FR-4, pattern facing the antenna, 70 × 48 mm. Left half cells at +45°, right half at −45°; remove partial cells; try a 2–3 mm metal-free strip on the mirror line |
| PCM cell (start) | Lattice 14 × 8 mm (u × v). I-bar/dumbbell strip 13.0 × 0.3 mm along u with 5.0 × 0.5 mm end caps; 1.0 mm gap between facing caps |
| Air spacer under the PCM sheet | 6.0 mm (nylon standoffs); the conversion band is most sensitive to this (±0.5 mm shifts it ±0.2 GHz at the low edge) |
| Ground | Copper-clad FR-4, 80 × 60 mm |
| Total height | Antenna copper → ground ≈ 10.8 mm (0.11λ at 3.1 GHz; λ/4 would be 24.2 mm) |

### 3.4 Honest expected results
| Quantity | Expected | Comparison |
|---|---|---|
| PCM conversion ratio ≥ 0.9 | ~3.3–7.5 GHz (2:1–2.3:1 with tolerances); ≥ 0.85 up to ~10 GHz in the ideal model | Do **not** claim 3.1–10.6 GHz |
| \|S11\| < −10 dB (each port, with the PCM) | ~3.3–10 GHz, ±2 dB ripple | A copper plate at the same 10.8 mm should fail ~3.2–4.5 GHz (control run) |
| ECC (from far fields) | ≤ 0.06 at 3.2–8 GHz even with 30 % cross-illumination of the wrong half | Same pair over PEC: 0.3–0.56 at 3–4 GHz; uniform PCM: 0.26–0.39 |
| Isolation \|S21\| | 12–20 dB (co-polarized side by side is the hardest case; not the headline claim) | – |
| Broadside total realized gain | +1.5 to +3 dB over the bare antenna; no λ/2 nulls | – |
| Front-to-back | 6–10 dB at 3.3 GHz, 10–15 dB above 5 GHz | – |
| Polarization | Each port elliptical/circular, opposite handedness. Report axial ratio and the ECC–axial-ratio relation | – |

### 3.5 CST plan (≈ 10 weeks)
1. **Unit cell** (wk 1–2): frequency-domain solver, unit-cell boundaries, Floquet port, ground below.
   - E along the bar gives Γu; E across it gives Γv.
   - Compute r_xx = (Γu+Γv)/2, r_yx = (Γu−Γv)/2 and PCR = |r_yx|²/(|r_xx|²+|r_yx|²).
   - Sweep bar and cap lengths, cap gap and air spacer; check 30° incidence.
2. **Bare element** (wk 2): confirm the octagon's band with a 0.3 mm CPW slot.
3. **One element over one half** (wk 3): sweep the gap from 3 to 6 mm and look at S11 and the far-field axial ratio.
4. **Pair, four backings at the same height** (wk 4–6): none, **copper plate**, uniform PCM, **mirrored PCM**.
   - Record S-parameters, realized gain vs frequency, front-to-back ratio and patterns.
   - Export complex Eθ/Eφ per port and compute **far-field ECC** with `analysis/mimo_metrics.py`. S-parameter ECC is
     invalid on lossy FR-4.
   - Also report DG, TARC, CCL and MEG (at XPR 0 dB and 6 dB).
5. **Robustness** (wk 6–7): mirror-line strip width, spacing 25–45 mm, spacer ±0.5 mm.
6. **Fabricate** three backings (copper, uniform PCM, mirrored PCM) plus the antenna board, all with standoffs
   (wk 8–10). Measure S-parameters on the VNA, and patterns if a chamber is available. ECC can also be measured with the
   two-port VNA method plus patterns.

**Draft title:** *Mirrored Polarization-Conversion Metasurface for Broadband Port Orthogonality in a Compact Co-Polarized
Wideband MIMO Antenna*

**Risks:**
- Each element also lights up the other half, so separation degrades at the low band.
- Real cells may reach only ~2:1.
- FR-4 loss.
- Uncontrolled polarization will draw reviewer questions; answer with mean effective gain (MEG) and the ECC–axial-ratio
  relation.
- A paywalled paper could still exist; rerun the §5 queries.

---

## 4. Backup: metasurface-radiator 2-port MIMO (if the PCM cell will not convert well enough on FR-4)
- **Concept:** turn the 4×4 patch array into the radiator, fed by a CPW slot in the ground below it (Jiang 2023
  topology). Then build a spatial 2-port.
- **The team's 5.5 mm cell is too small:** as a radiator its TM10 mode sits at ~9 GHz.
- **Starting dimensions:**
  - 4×4 patches 10.8 mm, gap 1.2 mm (period 12 mm), 0.8 mm FR-4;
  - 1.5 mm air, then a 1.6 mm FR-4 feed board with the CPW and a 16 × 1.5 mm slot in its ground; total 3.9 mm;
  - CPW strip 3.0 mm, slots 0.3 mm.
- **Expected:** ~4.2–7.6 GHz if TM10, the slot mode and TM30 merge (fallback: two bands); 6.5–8.5 dBi broadside;
  efficiency 75–88 %.
- **2-port:** in the **H-plane**, centres 57 mm apart, giving 20–28 dB isolation and ECC < 0.01. Avoid the E-plane: TM30
  couples at −16 dB there.
- **Prior art to cite:** Jiang 2023, Lin & Chen 2017/2018, Salehi 2024, Tran 2023, Sufian 2021. What is new is a
  ≥ 50 % FR-4 metasurface-radiator spatial MIMO at 4–7.5 GHz, with a characteristic-mode explanation of its coupling.

## 5. Before committing: prior-art queries to run in IEEE Xplore / Scopus
- ("polarization conversion" OR "polarization rotation") AND (metasurface OR AMC) AND MIMO AND (ECC OR "envelope correlation")
- mirrored OR chiral OR "opposite handedness" AND metasurface AND "co-polarized" AND MIMO
- (for the backup) metasurface antenna AND MIMO AND (CPW OR slot) AND (FR-4 OR FR4) AND wideband

## 6. Other candidates
- **Angle-of-arrival (802.15.4z channels 5/9):**
  - Size the AMC on *total* phase: 0° at ≈ 9.3 GHz, D = 5.0 mm, gap 0.6 mm on 1.6 mm FR-4, 2.5 mm air.
  - Element pitch 18.0 mm; profile 4.9 mm.
  - Isolation must be ≥ 25 dB: at 20 dB, coupling alone gives 5–9° of angle error.
  - Prior art: Gordebeke 2025 (cavity-backed angle-of-arrival array), Hokmabadi IEEE TIM 2026.
- **FR3 re-tune:** shift band 2 down ~0.6 GHz (to cover 7.125–8.4) and push band 3 beyond 15.4 GHz; then four
  elements at 90°.
- **Absorber-backed GPR MIMO:** result pending at the time of writing.
