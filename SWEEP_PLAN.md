# Gap Sweep Plan: Antenna-to-Metasurface Gap (h) and CPW Feed Gaps (p, G)

Companion to `CST_GUIDE.md`. Geometry is the confirmed CST model (see `MIDSEM_STUDY_PACK.md` §2.2):
decagon R = 15 mm centred at x = 8 mm, 50 × 50 mm FR-4 (εᵣ 4.3, tan δ 0.025, 1.6 mm), W_f = 3 mm,
G = 0.5 mm, Lg = −7 mm (so p = 0.73 mm), ground-backed 6 × 5 double-SRR metasurface at h = 3.9 mm.

Results go into the two CSV templates in `results/` (one row per CST run).

---

## 0. Which "gap" is which

| Symbol | What it is | Current | What it controls | How to treat it |
|---|---|---|---|---|
| **h** | Air gap, antenna substrate bottom → metasurface top copper | 3.9 mm | Reflection phase 2k₀h, gain, F/B, near-field detuning | **Main sweep** |
| **p** | Feed gap, CPW ground edge → patch lower edge | 0.73 mm | Lower band edge, mid-band match (coupling capacitance) | **Secondary sweep, re-tuned with the metasurface in place** |
| **G** | CPW slot width, feed strip ↔ ground | 0.5 mm | Line impedance only | **Calibrate once to 50 Ω, then freeze. Do not optimise it for bandwidth.** |

"CPW feed gap" can mean p or G. This plan treats p as the tuning gap and G as a calibration value, because
optimising G for S11 would just hide an impedance error inside the "optimum".

## 1. Problems to fix before any sweep (these change the result, not just the polish)

1. **G = 0.5 mm is not 50 Ω.** Conformal mapping (W = 3 mm, 1.6 mm FR-4, no back metal) gives:

   | G (mm) | 0.20 | 0.25 | **0.30** | 0.35 | 0.40 | 0.50 | 0.60 |
   |---|---|---|---|---|---|---|---|
   | Z₀ (Ω) | 45.6 | 48.2 | **50.5** | 52.6 | 54.5 | 58.0 | 61.2 |

   So the current design is a ~58 Ω line. Confirm with CST *Port Modes → Line impedance* (Stage 1).
   The geometry was tuned around a mismatched feed; Lg/p will move slightly once G is fixed.

2. **p must be a parameter, not a by-product.** Today p = (8 − R·cos 18°) − Lg, so every R or Lg change
   also moved p. Define `p` in the Parameter List and drive the ground edge from it:
   `Lg = 8 - R*cos(18*pi/180) - p`. Then R and p are independent.

3. **The Lg optimum sat at the end of its range.** Lg = −7 mm was the last value before the parts overlap,
   so the true optimum may be at a smaller p. The p sweep below therefore goes down to 0.2 mm.

4. **Keep the solver you already use, with identical settings in every run.** The existing results are CST 2019,
   frequency-domain solver, 0–18 GHz. Its tetrahedral adaptive mesh resolves sub-mm gaps on its own, so keep adaptive
   mesh refinement on and do not change its settings between runs. The real risk is the broadband-sweep artefacts you
   already saw (jumps near 4.0 and 6.2 GHz, a curve above 0 dB): re-run any point that shows them with more frequency
   samples before ranking it.

5. **The SRR reflection phase is still unknown.** Sweeping h without the unit-cell phase curve is partly blind:
   the best h is where 2k₀h tracks φ_R(f). Run the unit cell (`CST_GUIDE.md` §4) first. It is one cheap run and it tells you
   which h range is worth simulating.

6. **Port vs. metasurface clash at small h.** The CPW waveguide port extends below the board; it must stop ≥ 0.5 mm
   above the metasurface copper. Fix the port's downward extension at **2.5 mm for every run** (so h ≥ 3 mm works)
   and check the line impedance is still ~50 Ω. Changing the port between runs makes the S11 comparison unfair.

7. **A 6 × 5 metasurface breaks the 4-fold MIMO symmetry.** The "Port 1 only" speed-up in `CST_GUIDE.md` §6 is invalid with a
   non-square array. For MIMO runs either use a square array (6 × 6) or excite all ports. Decide this before Stage 6.

## 2. Sweep stages

Sweep settings unless stated: frequency-domain solver, 0–18 GHz, adaptive mesh refinement on, same settings as the
existing Lg and R sweeps. Farfield monitors at **3.5, 5, 6.5, 8, 10 GHz** only (needed for gain; skip the 21-monitor set).

| Stage | Purpose | Variable(s) | Values | Fixed | Runs |
|---|---|---|---|---|---|
| 0 | SRR reflection phase | (unit cell) | as built, then tweak if in-phase band misses 4–8 GHz | — | 1–5 |
| 1 | 50 Ω calibration | G | 0.25, 0.30, 0.35, 0.40, 0.50 mm | p = 0.73, no MS | 5 |
| 2 | Feed gap, no metasurface | p (set via Lg) | 0.2, 0.3, 0.4, 0.5, 0.73, 1.0, 1.5, 2.0 mm | G*, no MS | 8 |
| 3 | Air gap, coarse | h × {AMC, PEC} | 3, 3.9, 5, 6, 8, 10, 12 mm | G*, p* | 14 |
| 4 | Joint refinement | h × p | h* − 1 … h* + 1 step 0.5; p* − 0.2, p*, p* + 0.2 | G* | 15 |
| 5 | Final single element | none / PEC / AMC | best (h, p); tighter ΔS and more frequency samples; full monitor set | — | 3 + 1 convergence |
| 6 | 4-port MIMO check | h | h* − 1, h*, h* + 1, plus no-MS | best p, all ports excited | 4 |

About **55 runs** in total. Stages 1–2 are cheap (no metasurface, few monitors). Stage 3 is the expensive one.

Notes per stage:

- **Stage 1.** The grounds' inner edges sit at y = ±(W_f/2 + G), so G = 0.30 mm puts them at ±1.80 mm (they are at ±2.00 mm now).
  Pick the G whose port line impedance is 48–52 Ω (expect ≈ 0.30 mm). Check your PCB house can etch it;
  0.3 mm is fine for most, 0.2 mm is risky. Freeze G = G*.
- **Stage 2.** Keep R = 15 mm and the patch centre fixed; only the ground edge moves. The patch's lower flat edge is at
  x = 8 − 15·cos 18° = −6.27 mm, so Lg = −6.27 − p. Values to type in:

  | p (mm) | 0.2 | 0.3 | 0.4 | 0.5 | 0.73 (now) | 1.0 | 1.5 | 2.0 |
  |---|---|---|---|---|---|---|---|---|
  | **Lg (mm)** | −6.47 | −6.57 | −6.67 | −6.77 | −7.00 | −7.27 | −7.77 | −8.27 |

  Record p*. Below ~0.2 mm, fabrication tolerance (±0.05 mm) becomes a large fraction of p, so a p* at 0.2 is a warning, not a win.
- **Stage 3.** Run the **PEC plate at every h**, same footprint, same port, same mesh. The AMC-minus-PEC gain curve versus h is the
  figure that justifies the metasurface. Extend to 15 mm only if gain is still rising at 12 mm. Use the no-reflector run from
  Stage 2 (at p*) as the reference, with the same five farfield monitors.
- **Stage 4.** The metasurface loads the antenna in the near field (λ/2π > 3.9 mm below ≈ 12 GHz), so p* without it is not p* with it.
  Re-sweep p around the best h. Skip this stage if Stage 3's best h already meets the S11 gate with ≥ 1 dB margin.
- **Stage 6.** Only once the 4-port layout exists. This is where S21/S31/S41 isolation and ECC come in. h can change coupling
  through the metasurface (surface waves on the AMC), so check it, do not assume it.

## 3. Metrics and how a run is ranked

Per single-element run:

| Metric | Definition | Source |
|---|---|---|
| UWB coverage | % of 3.1–10.6 GHz with S11 ≤ −10 dB | `mimo_metrics.score_s11` |
| Worst in-band S11 | max S11 (dB) over 3.1–10.6 GHz, and where | same |
| −10 dB band | f_low – f_high (GHz), FBW % | `impedance_bandwidth` |
| Realized gain | at 3.5 / 5 / 6.5 / 8 / 10 GHz, **realized**, not IEEE | farfield monitors |
| ΔG vs none | realized gain (reflector) − realized gain (no reflector), per frequency | derived |
| F/B ratio | at 5 and 8 GHz | Farfield → 0D results |
| Total efficiency | minimum over the five frequencies | farfield monitors |
| Port Z₀ | line impedance at port 1 | Port Modes |
| Mesh convergence | adaptive passes and final ΔS | solver log |

Per MIMO run (Stage 6), from the `.s4p` file and far-fields: worst S21, S31, S41 over 3.1–10.6 GHz; max ECC (from S and from far-field);
min DG; max TARC; max CCL; MEG spread.

**Ranking rule (decide it now, before seeing the numbers):**

1. **Gate:** UWB coverage = 100 %, adaptive mesh converged, and no sweep artefacts (no S11 above 0 dB, no isolated jumps). Runs that fail are recorded but not ranked.
2. **Primary:** the largest **minimum ΔG** over the five frequencies. This rewards a reflector that helps everywhere and
   punishes one that adds 4 dB at 10 GHz but loses 3 dB at 3.5 GHz.
3. **Secondary:** mean ΔG.
4. **Tie-break:** smaller h (lower profile), then larger S11 margin.
5. **MIMO gate (Stage 6):** worst isolation ≥ 15 dB and ECC < 0.01 across 3.1–10.6 GHz.

## 4. What to expect (so the result does not surprise you)

The ray model in `MIDSEM_STUDY_PACK.md` §3.4 already says h = 3.9 mm is too close for the low band: the required reflection phase
there is ≈ +29° at 3.1 GHz, and a single SRR resonance cannot hold a +10°…+120° window over 3.1–10.6 GHz. Likely outcomes:

- The best h by the ranking rule is larger than 3.9 mm (somewhere in 6–10 mm), which weakens the "low profile" claim.
- Or a small h wins only if you accept a gain improvement over a sub-band.

Either is a valid result. Present it as a **gain-versus-profile curve** (min ΔG and mean ΔG against h, AMC and PEC on the same plot)
and choose the operating point from it. That is more defensible in a viva than a single "optimum".

## 5. Results tables

- `results/gap_sweep_single.csv`: one row per single-element run (Stages 1–5).
- `results/gap_sweep_mimo.csv`: one row per MIMO run (Stage 6).

Fill one row as soon as each run finishes, including failed and gated-out runs. Write gains in dBi, S-parameters in dB,
frequencies in GHz, lengths in mm. Put anything odd (S11 above 0 dB, ripple, not decayed) in `notes`.

Export the S11 of every run too, using the `CST_GUIDE.md` §9 names, e.g. `exports/single_gap_sweep.txt` for Stage 3 (AMC) and
`exports/single_gap_sweep_pec.txt` for the PEC runs.
