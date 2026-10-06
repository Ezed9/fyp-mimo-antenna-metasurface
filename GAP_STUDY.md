# Air-gap study: CPW decagon UWB antenna + ground-backed SRR metasurface

**Question asked:** what air gap between the 6 × 5 split-ring metasurface and the CPW antenna keeps
|S11| < −10 dB over the whole 2–15 GHz band?

> Status: RESULTS SECTION IS FILLED IN BELOW AS THE SIMULATIONS FINISH.

---

## 1. Short answer

_(written last; see §5)_

---

## 2. What was simulated

### Antenna (from the team's CST model, unchanged)

| Item | Value |
|---|---|
| Board | FR-4, εr 4.3, tan δ 0.025, 50 × 50 × 1.6 mm, copper on the front only |
| CPW feed | strip x = −1.5…1.5 mm, slots 0.5 mm |
| Grounds | x = −25…−2 and 2…25 mm, y = −25…−7 mm (18 mm long) |
| Patch | regular decagon, circumradius 15 mm, centre (0, 8) mm, flat edges top and bottom; bottom edge at y = −6.27 mm (0.73 mm above the grounds) |
| Port | at the board edge y = −25 mm |

### Metasurface: what was given and what had to be assumed

| Item | Value | Source |
|---|---|---|
| Rings | outer ring r = 7.0–7.5 mm, inner ring r = 5.0–5.5 mm (0.5 mm strips, 1.5 mm apart) | **given** |
| Array | 6 × 5 cells | **given** |
| Substrate / back | 1.6 mm FR-4 with a full copper ground (from `MIDSEM_STUDY_PACK.md` and the CST screenshot) | repo |
| Cell pitch / board size | 16.67 mm (6 cells, along the feed) × 20 mm (5 cells, across) → 100 × 100 mm board | **assumed**: 15 mm rings force ≥ 90 mm, and the CST screenshot shows a near-square board with these pitch ratios |
| Splits | 0.5 mm straight cuts on the feed axis; outer ring split toward the port, inner ring split toward the patch top | **assumed** (not visible at the screenshot's resolution) |
| Placement | centred under the antenna, rings facing the antenna | **assumed** |
| Gap h | air between the antenna substrate's back face and the ring layer; antenna copper → metasurface ground = h + 3.2 mm | definition used throughout |

If any assumption is wrong (in particular if the "R" values are really **diameters** and the metasurface is a
50 × 50 mm board), tell us: the conclusions about the low band do not change, but the ring-resonance details do.

---

## 3. Method

* **Solver:** openEMS (open-source FDTD, built from source in this environment), cross-checked against the
  team's CST result and against two independent "council" reviews (analytical model and literature).
* **Model:** half model with a PMC symmetry wall on the feed axis and a 100 Ω lumped port across one CPW slot
  (equivalent to the full antenna's 50 Ω port). Validated against a full model with a de-embedded CPW
  transmission-line port.
* **Material:** FR-4 as a causal Debye fit to εr 4.3 / tan δ 0.025 (tan δ 0.023–0.027 over 2–15 GHz),
  copper as zero-thickness PEC.
* **Mesh:** 0.25 mm cells over the antenna, 0.5 mm over the rest of the metasurface, 0.2 mm through both
  substrates, graded ≤ 1.3–1.6 elsewhere; PML ≥ 55 mm from the structure; 2.7 M (antenna alone) to
  ~7.7 M cells (with the metasurface); energy end criterion −40 dB.
* **Independent audit:** a red-team review of the first version of the model found three real problems
  (symmetry wall half a cell off the feed axis, an over-lossy FR-4 model at 2 GHz, PML too close). All three
  were fixed and every result below was produced with the corrected model.

---

## 4. Validation: bare antenna, openEMS vs CST

_(table and figure filled in from `simulation/results/`)_

---

## 5. Gap sweep results

_(table and figures filled in from `simulation/results/gap_sweep/`)_

---

## 6. Why: the physics in five lines

_(written last)_

---

## 7. How to confirm this in CST

_(written last)_

---

## 8. Reproducing the simulations

```bash
# one-off: build openEMS (see simulation/README section in this file) then
cd simulation
LD_LIBRARY_PATH=/opt/openEMS/lib python cpw_ms_openems.py --case bare --model half --out results/run
LD_LIBRARY_PATH=/opt/openEMS/lib python cpw_ms_openems.py --case ms --h 10 20 30 --out results/run
LD_LIBRARY_PATH=/opt/openEMS/lib python cpw_ms_openems.py --case plate --h 20 --out results/run
python plot_gap_sweep.py results/run results/figures
```
