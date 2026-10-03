# CST Build Guide: UWB 4-Port MIMO Antenna with AMC Metasurface

Each step maps to a professor's-checklist item and ends with an **Export** line. Exported files go into
`exports/` using the exact names given, so `analysis/make_figures.py` picks them up automatically (see §9).

> Menu names are from CST Studio Suite 2020–2024. They can differ slightly between versions.
> If a path doesn't match, use the ribbon search box (top right) to find the command by name.

---

## 0. Project setup (once)

1. **New Template → Microwaves & RF/Optical → Antennas → Planar (Patch, Slot, etc.) → Time Domain**.
   Units: mm, GHz, ns. Frequency: **2–12 GHz** (this shows margin on both sides of UWB).
2. Materials: **FR-4 (lossy)** from the library (εr = 4.3, tanδ = 0.025). Use **Copper (annealed)** with t = 0.035 mm for all metal.
   Keep the same materials in every model so the comparisons stay fair.
3. Boundaries: open (add space) on all six sides. The template already does this.
4. **Fix the substrate outline.** The current model has a step/notch on the board edges. Rebuild the substrate
   as one brick driven by parameters (`-Ws/2..Ws/2`, `-Ls/2..Ls/2`, `0..hs`). Delete the old solids left over from boolean operations.

## 1. Parameterize the single element (checklist: Single #1)

In the Parameter List, define and use these everywhere. No hard-coded numbers.

| Param | Meaning | Note |
|---|---|---|
| `Ws`, `Ls` | substrate width/length | current values |
| `hs` = 1.6, `t` = 0.035 | substrate / copper thickness | |
| `R` | octagon circumradius | cylinder with **Segments = 8** |
| `Lg` | CPW ground length (along the feed) | **sweep #1** |
| `Wf` | feed width | about 3 mm for 50 Ω CPW on 1.6 mm FR-4 |
| `g` | CPW slot gap (feed ↔ ground) | about 0.3–0.4 mm |
| `d` | gap between top of ground and bottom of patch | keep fixed |

- **Check 50 Ω:** after the first run, open *2D/3D Results → Port Modes → Port 1 → Line impedance*. It should be
  ~50 Ω. If not, adjust `Wf`/`g` **before** any sweep.
- **Waveguide port for CPW:** the port must cover the feed, both slots and part of each ground. Its height should extend
  ~5–6×`hs` above and below the substrate. Use *Macros → Solver → Ports → Calculate port extension coefficient*
  to size it.
- **Monitors (single element):**
  - Farfield at **4; 7; 10 GHz** for patterns.
  - Farfield at 2:0.5:12 GHz (21 monitors) for gain/efficiency vs frequency. Skip these during sweeps.
- **Mesh:**
  - Sweeps: 15 cells/λ.
  - Final runs: 20–25 cells/λ, accuracy −40 dB (energy decay).
  - Convergence check: rerun the final design at 25 cells/λ. If S11 moves less than ~1 dB in band, it's converged.

**Export:** `single_baseline_s11.txt` (optional, for your notes).

## 2. Ground-length sweep (checklist: Single #2)

*Simulation → Par. Sweep → New Seq. →* `Lg` = nominal −2 … +2 mm, step 1 mm (5 runs). **Turn off** the
21 gain monitors for the sweep.

**Export:** open *1D Results → S-Parameters → S1,1 (dB)* with all sweep curves shown →
*Post-Processing → Import/Export → Plot Data (ASCII)* → `exports/single_Lg_sweep.txt`.

The script ranks curves by **% of 3.1–10.6 GHz with S11 ≤ −10 dB, then by worst in-band S11**, and
prints the best `Lg` in `figures/summary.txt`. Fix `Lg` to that value.

## 3. Patch-radius sweep (checklist: Single #3)

Same as §2 with `R` = nominal −2 … +2 mm, step 1 mm, `Lg` fixed. **Export** `exports/single_R_sweep.txt`.
Fix `R` to the best value. That gives the **optimized single element**.

Final run of the optimized element (fine mesh, all monitors on):
- S11 → `exports/single_final_s11.txt`
- Realized gain vs frequency: *Template Based Post-Processing → Farfield and Antenna Properties → Farfield
  Result* → Realized Gain, max value, all farfield monitors → 1D curve → export `exports/single_final_gain.txt`
- Total efficiency vs frequency → `exports/single_final_eff_tot.txt`. Use *1D Results → Efficiencies* if your
  version has it, or the same template set to "Tot. efficiency".
- Patterns at 4/7/10 GHz → `exports/ff/single_p1_<f>GHz.txt` (see §9 for the far-field export).

## 4. AMC unit cell design & characterization (checklist: Single #5)

1. **New Template → Microwaves & RF/Optical → Periodic Structures → FSS, Metamaterial – Unit Cell →
   Frequency Domain**. Frequency 2–12 GHz.
2. Geometry (square lattice, period `p`):
   - Bottom: full copper ground.
   - Middle: FR-4 slab, `hs` = 1.6.
   - Top: **square ring** (outer `b`, width `wr`) plus a **centred square patch** (side `a`).
   This is a dual-resonant cell, used to widen the in-phase band.
   Starting values: `p` = 10, `b` = 9.4, `wr` = 0.6, `a` = 6 mm.
3. Boundaries:
   - x and y: **unit cell**.
   - Zmax: **Floquet port** (open add space).
   - Zmin: electric. The ground plane blocks transmission anyway.
4. **De-embed** the Zmax Floquet port to the top copper surface (*Ports → Floquet → Distance to reference
   plane* = minus the air gap between the port and the cell top). The phase then refers to the AMC surface.
5. **Sanity checks (do these, they take 1 min each):**
   - Delete the top metal → phase ≈ ±180° at low frequency (it behaves like a PEC).
   - With the full cell → the phase crosses **0°** at resonance.
6. Sweep `a` and `b` until the **±90° in-phase band** is as wide as possible and centred near 6–7 GHz.

> **Physics reality check:** a single 1.6 mm FR-4 AMC typically gives only ~20–30% in-phase bandwidth.
> If you need more, the two levers are a thicker AMC substrate (two FR-4 boards stacked, 3.2 mm) and the dual-resonant cell.
> No passive AMC is in-phase over all of 3.1–10.6 GHz. The gap `h` in §5 makes up for part of that. Say so honestly in the paper.

**Export:**
- Reflection phase (deg) of SZmax(1),Zmax(1) → `exports/unitcell_phase.txt`.
- Magnitude (dB) → `exports/unitcell_mag.txt`.

## 5. Single antenna + AMC (checklist: Single #4)

1. Build an **N×N AMC array** under the board. N·`p` should be ≥ the board size (e.g. 5×5 cells for a 50 mm board).
   AMC cells face the antenna, AMC ground faces away. The air gap `h` runs from the antenna substrate bottom to the AMC top copper.
2. **Port vs. AMC clash:** the waveguide port's lower extension must not cut into the AMC. Limit the downward
   extension to ≤ `h` − 0.5 mm, then confirm the port line impedance is still ~50 Ω.
3. Sweep `h` = 3, 5, 7, 10, 12 mm. **Export** `exports/single_gap_sweep.txt`.
4. With the best `h`, make **three final runs** with identical mesh and monitors:
   - no reflector → `single_none_s11.txt`, `single_none_gain.txt`
   - **PEC plate** (copper sheet, same footprint, same `h`) → `single_pec_s11.txt`, `single_pec_gain.txt`
   - **AMC** → `single_amc_s11.txt`, `single_amc_gain.txt`

   The PEC comparison is what justifies "why a metasurface and not just a metal plate". It's the key result for the paper.
5. If the AMC detunes the low band (S11 > −10 dB near 3.1 GHz), retune `Lg` by ±1 mm with the AMC in place.
6. Also note the **front-to-back ratio** (*Farfield → 0D results*) at 4/7/10 GHz for none / PEC / AMC.

## 6. Build the 4-port orthogonal MIMO (checklist: MIMO #1)

1. Start a new project from the optimized element. Make the substrate a square board `Wb` × `Wb`, centred at the origin.
2. Place element 1 with its CPW feed at the **bottom edge**, offset sideways by `off` (`off` = 0 means centred).
3. **Transform → Rotate → Copy**: 90° about the z-axis through the origin, repeated 3 times. You get elements 2, 3, 4,
   one per edge and each rotated 90° (polarization + pattern diversity). Rotate the ports the same way
   (ports 1–4, numbered counter-clockwise).
4. **Common ground:** join each element's CPW ground to a **central plus-shaped strip** of width `wc`.
   Build the strip once, then rotate-copy it so it stays 4-fold symmetric.
5. **Symmetry speed-up (use it for all MIMO sweeps):** the structure is 4-fold rotationally symmetric. In the Time
   Domain solver set **Source type = Port 1** (not "All ports"). One run gives S11, S21, S31, S41, and the
   rest follow by symmetry (S22 = S11, S32 = S21, S42 = S31, S43 = S21, …). That's about 4× faster.
   Alternatively, define *S-Parameter symmetries* in the solver dialog.
6. Port-1-only sweep of `wc` (e.g. 0.5, 1, 2, 3 mm) and/or `off`. Pick the value with the lowest worst coupling
   while S11 still covers UWB. Typical target: isolation > 15 dB, aim for 20 dB.
7. **Common mistake:** if anything breaks the symmetry (port sizes, a stray solid, a non-centred AMC), the symmetry
   shortcut is invalid. Always do the final run with **all ports** excited.

## 7. Final MIMO runs (checklist: MIMO #2–#7)

Two overnight runs, **Source type = All ports**, fine mesh:

| Run | Model | Export prefix |
|---|---|---|
| A | MIMO without MS | `mimo_noMS` |
| B | MIMO + AMC (N×N lattice centred on the board, best `h` from §5) | `mimo_MS` |

Monitors for both runs:
- Farfield at 4; 7; 10 GHz. CST creates them for every port automatically.
- H-field/surface current at 4; 7; 10 GHz.
- Farfields at 2:0.5:12 GHz if you can afford them (for realized gain vs frequency).

Exports per run:
- **S-parameters (all 16):** *1D Results → S-Parameters → right-click → Export → Touchstone*, 4 ports,
  magnitude/phase → `exports/mimo_noMS.s4p` / `exports/mimo_MS.s4p`.
  The script derives S11–S44, all 6 couplings, ECC (from S), DG, TARC, CCL and MEG from this one file.
- Realized gain and total efficiency, port 1 → `mimo_noMS_gain.txt`, `mimo_noMS_eff_tot.txt` (and `mimo_MS_…`).
- Far-fields, every port at 4/7/10 GHz → `exports/ff/<run>_p<port>_<f>GHz.txt`
  (e.g. `ff/noMS_p1_7GHz.txt`, `ff/MS_p3_10GHz.txt`). The script plots polar cuts and computes the
  **far-field ECC**, which is more accurate than the S-parameter ECC because FR-4 is lossy. Report both.
- Surface current: open *2D/3D Results → Surface Current (f=…) [1]* (port 1 excited, others matched).
  Set a **fixed colour scale** (*Plot Properties → Fixed max*) that's the same for all three frequencies, use the
  top view, then *File → Export → Image*. Make one image per frequency. The current on ports 2–4 shows how strong the coupling is,
  and the ground cross's effect is visible.

## 8. Simulation-time tips (slow PC)

- Use PEC instead of copper **only** for quick exploratory runs. Every reported result uses copper.
- Turn off all farfield/field monitors during parameter sweeps. Monitors cost a lot of time and memory.
- The AMC adds high-Q resonances. If the energy hasn't decayed to −40 dB, raise the *Duration* (solver
  settings) rather than accepting rippled S-parameters.
- Queue the final runs overnight: *Simulation → Start* on run A, then a second project for run B.

## 9. Export conventions & running the analysis

**Far-field ASCII export (needed for ECC and patterns):**
1. Open the 3D farfield (e.g. *Farfields → farfield (f=7) [1]*).
2. Set *Farfield Plot → Properties*: **Theta step 5°, Phi step 5°**, Directivity or Realized Gain, **dB** scaling,
   and the **same origin for all ports** (default: centre of bounding box).
3. *Post-Processing → Import/Export → Plot Data (ASCII)*.

The file must contain the columns `Theta, Phi, Abs(…), Abs(Theta), Phase(Theta), Abs(Phi), Phase(Phi), Ax.Ratio`.
The phase columns are what make far-field ECC possible.

**Filename checklist** (`exports/`). Missing files are skipped, so you can run the script at any stage.

```
single_Lg_sweep.txt  single_R_sweep.txt  single_gap_sweep.txt
single_final_s11.txt single_final_gain.txt single_final_eff_tot.txt
unitcell_phase.txt   unitcell_mag.txt
single_none_s11.txt  single_pec_s11.txt  single_amc_s11.txt
single_none_gain.txt single_pec_gain.txt single_amc_gain.txt
mimo_noMS.s4p  mimo_MS.s4p
mimo_noMS_gain.txt mimo_MS_gain.txt mimo_noMS_eff_tot.txt mimo_MS_eff_tot.txt
ff/noMS_p1_4GHz.txt … ff/MS_p4_10GHz.txt
```

**Run (from the `analysis/` folder):**

```bash
uv run python make_figures.py
```

Output: `figures/*.png` (slides) and `figures/*.pdf` (paper), plus `figures/summary.txt` with every key number
(best sweep values, −10 dB bands, worst isolation, max ECC, min DG, max TARC/CCL, MEG spread, far-field ECC).

To check the pipeline without CST data: `uv run python make_figures.py --demo` writes to `figures_demo/`.

## 10. Targets ("good" for a UWB 4-port paper)

| Metric | Target | Typical in literature |
|---|---|---|
| S11 | ≤ −10 dB across 3.1–10.6 GHz | — |
| Isolation | > 15 dB (aim for 20 dB) | 17–22 dB for orthogonal 4-port |
| ECC | < 0.01 | < 0.01–0.02 |
| DG | > 9.95 dB | > 9.9 dB |
| TARC | < −10 dB | — |
| CCL | < 0.4 bit/s/Hz | — |
| MEG | equal across ports within 3 dB, ≈ −3 dB | — |
| Gain gain from AMC | +2–4 dBi over most of the band, vs both no-reflector and PEC | about +2.5–3 dB on FR-4 stacks |
