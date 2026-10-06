# Mid-Sem Study Pack: Wideband MIMO Antenna with Metasurface

**Evaluation:** Wednesday 7 October 2026 (report + presentation + viva), NIT Silchar, Dept. of ECE
**Team:** Chanswarang Boro (2314143), Nishit Baishya (2314088), Anushka Dam (2314115), Sanjana (2314060)
**Guide:** Dr. Ujjal Chakraborty (Associate Professor, ECE) · **Co-guide:** Mr. Sovan Bhattacharya (PhD scholar)

> **Source and rules.** The facts below are aligned with the finalized 7-page `report/MidSem_Report.pdf`
> and `report/Literature_Review.docx`. All antenna geometry, sweeps, figures, and dimensions match the CST model.
> Antenna and metasurface geometry are from the team's CST model (`presentation/STUDY_PROMPT.md` on `main`):
> a **regular 10-sided (decagonal) patch**, R = 15 mm circumradius, on a 50 × 50 mm FR-4 board (εᵣ 4.3, tan δ 0.025, 1.6 mm).
> The metasurface is a **ground-backed 6 × 5 array of double split-ring cells** on 1.6 mm FR-4.
> A decagon is close to a disc, so "disc monopole" theory applies. The pack says "patch" or "decagon" for ours.
> Everything not in the brief is marked **[fill in]**, and Appendix A says how to get each value from CST.
> Numbers marked *(computed)* are hand or Python calculations, **not simulations**. Never present them as results.

---

## 0. Read this first: corrections, risks and things I disagree with

Most of the brief is correct. I checked every number: the FBW 151.7 %, the 2k₀h table, λ/4 = 24.2 mm,
the ≈ 18.7 GHz crossover and the 0.46 dB mismatch bound are all right. The points below are where the brief
is wrong, overstated or risky. Fix them in the slides **before** the evaluation.

1. **"A PEC plate at 2 mm would reduce the forward gain over all of UWB" holds, but know the exact criterion.**
   In the ray model, two equal waves add to *more* than one wave alone whenever their phase difference is within **±120°**, not ±90°.
   ±90° is the conventional "at least +3 dB over the direct wave" criterion.
   For a PEC at 2 mm the phase error is 180° − 2k₀h. That is below 120° only above **≈ 12.5 GHz** *(computed)*.
   Correct statement: *"In the ray picture, a PEC plate at 2 mm cancels the forward wave below ≈ 12.5 GHz
   (about −11.7 dB at 3.1 GHz relative to the direct ray), adds less than 3 dB between 12.5 and 18 GHz, and never reaches the ±90° window in our simulated band (only above ≈ 18.7 GHz).
   Near-field shorting makes the low band even worse."* That is still a damning case against the plate, and it is accurate.

2. **"Every MIMO + metasurface paper reviewed is narrower-band than UWB" is true only of *your* five papers.**
   An earlier version of this repository's `LITERATURE.md` (commit 2cd3ca6, from automated web research) listed 4-port UWB MIMO antennas that already use reflectors or AMCs:
   - Mohanty & Sahu 2022: 2.08–10.4 GHz, metal reflector at ≈ 10 mm.
   - Alekya 2026: 2–12 GHz with a split-ring AMC.
   - Nirmala 2026: UWB with an FSS.

   It also lists two 2-port UWB designs: Azharuddin 2026 with an FSS, and Douhi 2026 with an AMC on a **5 mm** spacer.
   An examiner who knows any of these will puncture a claim like *"UWB MIMO with a metasurface has not been done."*
   **Never say "first".** Say *"among the papers we reviewed"*, and make the novelty the **combination** (§4.3).
   Also, "far smaller than 9–20 mm" becomes "smaller than every design we reviewed". Douhi 2026 used a 5 mm spacer, and the current `LITERATURE.md` lists AboEl-Hassan 2025's air gap as 5 mm (unconfirmed).

3. **Why the metasurface must be ground-backed (it is, in our CST model). Know this argument.**
   - A *bare* (no copper behind) thin SRR sheet reflects with a phase between 90° and 270°. It is ≈ 180° (metal-like) at its own resonance.
   - It can sit inside the ±90° window at the low end of UWB only where its reflection is weak (|Γ| ≈ 0.2–0.3) *(computed, §3.4)*.
   - So **a bare SRR sheet cannot give strong in-phase reflection at 2 mm in the lower UWB band.**
   - A **ground-backed** SRR (SRR + substrate + copper = an AMC) can, over part of the band.
   - Note: outside the cell's in-phase band, our AMC behaves like its copper ground, which sits 2 + 1.6 = 3.6 mm behind the antenna substrate. So the PEC argument applies there, almost as harshly as at 2 mm.

   Our metasurface has a full copper ground on its back, so it is the AMC case. If someone asks why the ground is there, answer with §6 Q-G9.

4. **Do not call it a "magnetic resonance" that gives "negative μ" in your set-up.**
   Your SRRs lie parallel to the antenna, and the wave arrives roughly at normal incidence. So the magnetic field is **in the ring's plane**
   and does not thread the ring. The ring's LC resonance is driven mainly by the **electric field across the split**
   (electric/bianisotropic coupling). What makes a reflector work is the **surface impedance and reflection phase** of the sheet, not μ < 0.
   You *can* say: "the SRR is an LC resonator; its resonance sets where the surface reflects in phase."

5. **The sweep artefacts are *probably* numerical, but you have not proved it.**
   A curve above 0 dB is certainly unphysical. *Which* numerical cause produced it is a hypothesis. If at all possible,
   **re-run that one Lg value** with tighter sweep settings, or with the time-domain solver, before Wednesday
   (Appendix A.4, about 20–40 min). Then you can say "we re-ran it and it is smooth", which is a far stronger answer.

6. **Your two sweep parameters are coupled.**
   - The patch is centred at x = 8 mm, so changing R also moves its lower flat edge (at 8 − R·cos 18°). That changes the feed gap:
     p = (8 − R·cos 18°) − Lg, which is 15 − 0.951·R mm at Lg = −7 mm *(computed)*.
   - So the R sweep was partly also a gap sweep: p ≈ 11.2 mm at R = 4 mm, and **p = 0.73 mm** at R = 15 mm.
   - Be ready for: *"What does Lg = −7 mm mean physically?"* It is the ground's edge coordinate along the feed axis (x in the CST model).
     The grounds run from x = −25 to −7 mm.

7. **The f_L formula is a free-space estimate.**
   7.2/(L + r + p) is for a planar monopole over a large ground, in air. Printed versions often add a substrate correction factor,
   which lowers f_L. For our decagon it gives ≈ 2.18 GHz against 2.16 GHz simulated *(computed)*.
   That is closer than such a rough formula deserves, so present it as a sanity check, not as precise agreement.

8. **The "optimum" is the best within your sweep, not an optimum.**
   Both values sit at the edge of their range, so the true optimum may lie outside it, limited by the board.
   Say "best within the range the board allows". Also, a one-parameter-at-a-time sweep is not a joint optimisation.

9. **Diversity-gain formula varies between papers.** Some use DG = 10√(1−ECC²), others 10√(1−ECC). Your repo's `analysis/mimo_metrics.py`
   uses 10√(1−ECC²). State which one you use.

10. **"Why do you want more gain if FCC caps EIRP?"** This is a sharp UWB question, so have it ready (Q-D6).
    The −41.3 dBm/MHz limit is on **EIRP** (gain × transmit power). Extra transmit gain does not let you radiate more.
    It does help on **receive**, lets you reach the limit with less amplifier power, and focuses energy in one direction
    (less towards the user's body or the device behind). This also applies to imaging, radar and WBAN.

---

## 1. Fundamentals, from zero to deep

Each topic follows the same pattern: **Simple** (with an analogy), then **Deep** (equations with units), then **Examiner may ask**.

### 1.1 EM waves, wavelength and frequency

**Simple.** An electromagnetic wave is a travelling ripple of electric (E) and magnetic (H) fields. The two fields are
perpendicular to each other and to the direction of travel.
*Analogy:* ripples on a pond. The **frequency** is how many crests pass you per second. The **wavelength** is the distance
from one crest to the next. A faster wave, or fewer crests per second, means a longer wavelength.

**Deep.**
- c = f·λ, with c = 2.998 × 10⁸ m/s. Handy form: **λ₀ [mm] = 299.8 / f [GHz]**.
- In a dielectric (μᵣ = 1): λ = λ₀/√εᵣ. On a printed line use εeff, which lies between 1 and εᵣ.
- Free-space wavenumber: k₀ = 2π/λ₀ (rad/m). The phase accumulated over a distance d is k₀·d.
- Wave impedance of free space: η₀ = E/H = √(μ₀/ε₀) ≈ 120π ≈ 377 Ω.
- Power density of a plane wave (peak amplitude E): S = |E|²/(2η₀) W/m².

Our key wavelengths *(computed)*:

| f (GHz) | 2.16 | 3.1 | 6.85 | 10.6 | 15.73 |
|---|---|---|---|---|---|
| λ₀ (mm) | 138.7 | 96.7 | 43.8 | 28.3 | 19.1 |

**Examiner may ask.**
- *"What is the wavelength at 10 GHz?"* About 30 mm in air, and roughly 30/√εeff on the board.
- *"What is electrical size?"* Physical size divided by wavelength. Antenna behaviour depends on electrical size, not millimetres.

### 1.2 Transmission lines, characteristic impedance, reflection coefficient, S-parameters

**Simple.** A transmission line is a guided road for the wave, for example a coax cable or the CPW feed.
Its **characteristic impedance Z₀** is the voltage-to-current ratio of a wave travelling on it. It is fixed by the line's geometry and
materials, not by its length.
If the wave reaches a load whose impedance differs from Z₀, part of it bounces back.
*Analogy:* a thin rope tied to a thick rope. Shake the thin one and part of the pulse reflects at the knot.

**Deep.**
- Lossless line: Z₀ = √(L′/C′) (Ω), where L′ and C′ are per-unit-length inductance and capacitance.
- **Reflection coefficient** at a load Z_L: **Γ = (Z_L − Z₀)/(Z_L + Z₀)**. It is complex and dimensionless.
  For any passive load (Re Z_L ≥ 0), **|Γ| ≤ 1**.
- **S-parameters.** Write aᵢ for the wave going into port i and bᵢ for the wave coming out. Then **b = S·a**, and
  Sᵢⱼ = bᵢ/aⱼ with all other ports matched.
  - S₁₁ is the input reflection coefficient at port 1.
  - S₂₁ is the transmission from port 1 to port 2.
- A passive network satisfies Σᵢ|Sᵢⱼ|² ≤ 1 for every column j. A lossless network has a unitary S. A reciprocal one has Sᵢⱼ = Sⱼᵢ.
- For a 1-port antenna: |S₁₁|² is the fraction of incident power reflected, and 1 − |S₁₁|² is the fraction accepted.
  The accepted part is then radiated or lost as heat.

**Examiner may ask.**
- *"Why S-parameters and not Z-parameters at GHz?"* Z and Y need true opens and shorts, which are hard to make at GHz and can make active devices oscillate.
  S-parameters need matched loads, which are easy. A VNA measures them directly.
- *"Can |S₁₁| exceed 1?"* Not for a passive antenna. That would mean more power coming back than was sent in.

### 1.3 S₁₁ in dB, return loss, VSWR, matching and the −10 dB criterion

**Simple.** Matching means making the antenna look like the line's 50 Ω, so the wave goes into the antenna instead of
bouncing back. **S₁₁ in dB** tells you how much bounces back: −10 dB means 10 % of the power is reflected and 90 % is accepted.

**Deep.**
- |S₁₁|(dB) = 20·log₁₀|Γ| (negative for a passive load).
- **Return loss** RL = −20·log₁₀|Γ| (positive). "S₁₁ = −10 dB" and "RL = 10 dB" mean the same thing. Mind the sign.
- **VSWR** = (1 + |Γ|)/(1 − |Γ|).
- **Mismatch loss** = −10·log₁₀(1 − |Γ|²) dB.

| S₁₁ | \|Γ\| | Reflected power | VSWR | Mismatch loss |
|---|---|---|---|---|
| −6 dB (phone spec) | 0.50 | 25 % | 3.0 | 1.26 dB |
| **−10 dB** | **0.316** | **10 %** | **1.92** | **0.46 dB** |
| −20 dB | 0.10 | 1 % | 1.22 | 0.04 dB |
| −32.65 dB (our best dip) | 0.023 | 0.05 % | 1.05 | 0.002 dB |

*(computed)*

- **Why −10 dB?** It is a convention: 90 % of the power is accepted and VSWR < 2. Handsets often accept −6 dB.
- **Conjugate match** (Z_L = Z_s*) gives maximum power transfer. Z_L = Z₀ gives no reflection on the line.

**Examiner may ask.**
- *"What is VSWR at −10 dB?"* About 1.92.
- *"How much power is lost at −10 dB?"* 10 % reflected, which is a 0.46 dB mismatch loss.

### 1.4 Antenna parameters

**Radiation pattern.** This is the plot of radiated power (or field) against direction (θ, φ) in the far field.
- *Analogy:* a torch beam versus a bare bulb. A torch is directional, a bulb is near-omnidirectional.
- Plots are usually normalised dB polar cuts in two **principal planes**:
  - The **E-plane** contains the E-field vector and the direction of maximum radiation.
  - The **H-plane** contains the H-field vector and the direction of maximum radiation.
- Typical for a planar monopole at low frequency: the H-plane is near-omnidirectional and the E-plane is a figure-8, like a dipole.
  At higher frequencies the pattern distorts and tilts.
- For our board: E/H-plane orientation = [fill in from the CST axes; see Appendix A.6].

**Directivity.** D = 4π·U_max / P_rad. It is dimensionless and quoted in dBi (relative to isotropic).
It only measures how concentrated the beam is and ignores losses entirely.
Reference values: isotropic 0 dBi, short dipole 1.76 dBi, half-wave dipole 2.15 dBi.

**Gain: IEEE versus realized.**
- **IEEE gain:** G = e_rad·D = 4π·U_max / P_accepted. It includes conductor and dielectric loss but **excludes port mismatch**.
- **Realized gain:** G_R = (1 − |Γ|²)·G = 4π·U_max / P_incident. It **includes mismatch**. This is what a link budget actually sees.
- CST naming: "Directivity", "Gain" (= IEEE gain), "Realized Gain". **Our brief's gain plot is CST "Gain" (IEEE).**
- Inside our −10 dB band, G_R ≥ G − 0.46 dB *(computed)*. At the weak points:
  - near 6.5 GHz (≈ −10.3 dB): G_R ≈ G − 0.43 dB;
  - near 12.2 GHz (≈ −10.5 dB): G_R ≈ G − 0.41 dB.

**Efficiency.**
- Radiation efficiency e_rad = P_rad/P_accepted (copper and FR-4 losses).
- Total efficiency e_tot = e_rad·(1 − |Γ|²).
- So G = e_rad·D and G_R = e_tot·D.

**Bandwidth.**
- Impedance bandwidth is where |S₁₁| ≤ −10 dB. There are also pattern, gain (−3 dB) and axial-ratio bandwidths.
- **Fractional bandwidth:** FBW = 2(f_H − f_L)/(f_H + f_L) × 100 %.
- Ours: 2.1615–15.734 GHz gives **151.7 %**, a **7.28 : 1** ratio.
- UWB itself (3.1–10.6 GHz) is 109.5 %, a 3.42 : 1 ratio *(computed)*.

**Polarization.** This is the shape traced by the tip of the E-field vector over time, seen looking along the direction of travel.
- **Linear:** one direction.
- **Circular:** two equal orthogonal components 90° out of phase (RHCP or LHCP).
- **Elliptical:** the general case.
- **Axial ratio** AR = major/minor axis. AR ≤ 3 dB is the usual criterion for "circularly polarized".
- Polarization loss factor PLF = |ρ̂_w·ρ̂_a|². A linear antenna receiving CP loses 3 dB.
- Our decagonal monopole is **linearly polarized**, along the feed axis. Check co- and cross-pol in CST (Appendix A.6).

**Front-to-back ratio.** F/B = 10·log₁₀(U_front/U_back) dB.
A bare monopole radiates nearly equally to both sides, so F/B ≈ 0 dB. A good reflector should raise it a lot.
This is one of the cleanest ways to show the reflector works.

**Near field versus far field.**
- **Reactive near field:** for an electrically small antenna, r < λ/2π. For a large one, r < 0.62√(D³/λ).
  Here energy sloshes back and forth (stored) rather than radiating.
- **Radiating near field (Fresnel):** out to 2D²/λ.
- **Far field (Fraunhofer):** r > 2D²/λ, with r ≫ D and r ≫ λ. The pattern no longer changes with distance.
  Gain and patterns are defined here.
- **Key fact for us:** λ/2π = 15.4 mm at 3.1 GHz and 4.5 mm at 10.6 GHz.
  It equals 2 mm at ≈ 23.9 GHz *(computed)*. So the metasurface at 2 mm is **inside the reactive near field across all of UWB**.
  That is why the ray picture is only a guide, and why S₁₁ must be re-checked with the metasurface in place.

**Examiner may ask.**
- *"Directivity versus gain?"* Gain = efficiency × directivity.
- *"Why is realized gain lower?"* It also counts the power reflected at the port.
- *"How do you define the far field?"* r > 2D²/λ.
- *"What is your polarization?"* Linear.

### 1.5 Microstrip versus coplanar waveguide (CPW)

**Simple.**
- A **microstrip** is a strip on top of a board with a full ground plane on the bottom.
- A **CPW** puts the signal strip and **both ground planes on the same side**, separated by two thin slots.
- *Analogy:* microstrip is a road over a basement; CPW is a road with two pavements beside it.

**Deep.**

*Microstrip.*
- Quasi-TEM wave. Z₀ is set by W/h and εᵣ.
- A 50 Ω line on 1.6 mm FR-4 is ≈ 3 mm wide (standard design-chart value).

*CPW.* Strip width W, slot width G.
- Use k = W/(W + 2G).
- **Z₀ = (30π/√εeff) · K(k′)/K(k)**, where K is the complete elliptic integral and k′ = √(1 − k²).
- For a thick substrate, εeff ≈ (εᵣ + 1)/2 ≈ 2.7 on FR-4.
- Z₀ is set mainly by W and G. Substrate thickness matters less.

*CPW advantages for us.*
- **Uniplanar**, so single-sided etching and no vias.
- Easy series and shunt mounting.
- Low dispersion and wideband.
- Most importantly, **the CPW ground is in the same plane as the patch**, so the ground acts as the monopole's counterpoise.
  Its edge is a design parameter (Lg).
- The back of the board is free, so a reflector can sit behind it without shorting a ground plane.

*CPW disadvantages.*
- An unwanted **slotline (odd) mode** appears if the two grounds are not held at the same potential.
- The side grounds take up area.
- The design is sensitive to the slot width.

*Waveguide port in CST.*
- CST solves the 2D eigenmode of the line cross-section at the port plane. This gives an accurate Z₀ and a pure mode.
- The port rectangle must cover the strip, both slots and enough of each ground, and extend above and below the substrate by several times h.
- A port that is too small gives the wrong impedance. One that is too large can let **higher-order modes propagate** above some frequency.
- Our values: W = 3 mm, G = 0.5 mm, port line impedance = [fill in] Ω (Appendix A.1).
- **Check this one.** The textbook CPW formula for W = 3 mm and G = 0.5 mm on 1.6 mm FR-4 (εᵣ 4.3) gives ≈ 55–58 Ω, not 50 Ω *(computed)*.
  A 58 Ω line on a 50 Ω system reflects only |Γ| ≈ 0.07 (VSWR ≈ 1.16), so the effect is minor. Read the real value from CST's port-mode line impedance and quote that.

**Examiner may ask.**
- *"Why CPW?"* Uniplanar, wideband, same-plane ground for the monopole, and a free back side.
- *"How did you get 50 Ω?"* From W and G. Check the port line impedance in CST.
- *"What is the odd mode?"* A slotline mode that appears when the two grounds are at different potentials. Symmetry, or air bridges in circuits, suppress it.

### 1.6 Ultra-wideband (UWB)

**Simple.** UWB spreads a very weak signal over a huge slice of spectrum, from 3.1 to 10.6 GHz.
*Analogy:* whispering across the whole piano keyboard at once instead of shouting one note.
Each frequency is so quiet that it does not disturb other users, but the very short pulses allow precise timing and high data rates.

**Deep.**
- **FCC (2002):** 3.1–10.6 GHz, unlicensed, EIRP spectral density ≤ **−41.3 dBm/MHz**.
- **Definition of a UWB signal:** −10 dB bandwidth ≥ **500 MHz** or fractional bandwidth ≥ **20 %**.
- **Uses:**
  - short-range high-rate links;
  - centimetre-level ranging and positioning (UWB chips in phones and tags);
  - radar and through-wall imaging, ground-penetrating radar;
  - medical imaging, wireless body-area networks (WBAN), sensors.
- **Why UWB antennas are hard:**
  1. Matching over a 3.4 : 1 band.
  2. Keeping the pattern and gain stable while the electrical size changes 3.4×.
  3. Low group-delay variation, so the pulse is not distorted (pulse fidelity).
  4. Staying compact.
  5. In MIMO, isolation must hold across the whole band. Spacing elements by λ/2 at 3.1 GHz would need 48 mm.
  6. Adding a reflector: an ordinary reflector works only over a limited band (§3.4).

**Examiner may ask.**
- *"What is the FCC mask?"* 3.1–10.6 GHz at −41.3 dBm/MHz.
- *"Why does UWB need wideband antennas?"* The pulses are very short, so their spectrum is very wide.
- *"Gain versus the EIRP limit?"* See §0 item 10 and Q-D6.

### 1.7 Printed planar monopoles

**Simple.** Start with a quarter-wave wire standing on a ground plane. Flatten it into a wide disc.
A wide, smooth shape supports many closely spaced resonances. They overlap, so the match never drops out, and that gives a huge band.
*Analogy:* one guitar string rings at one note. A drum skin rings at many closely spaced notes.

**Deep.**

*Equivalent cylinder (Kumar & Ray).*
- A planar monopole of height L and area A behaves like a cylinder of the same height with radius r, where 2πrL = A.
- For a disc of radius R: L = 2R and A = πR², so **r = R/4**.
- For our **regular decagon** (circumradius R, flat side facing the ground): L = 2R·cos 18° and A = 5R²·sin 36°, with r = A/(2πL).
- **Lower band edge:** **f_L ≈ 7.2/(L + r + p) GHz**, with all lengths in cm and p = feed gap (ground edge to patch).
- The 7.2 comes from λ/4 = 7.5/f (cm). An empirical factor (0.24 rather than 0.25) accounts for the fringing and thickness of the wide element.

*Ours (decagon, R = 15 mm, p = 0.73 mm)* *(computed)*:
- L = 28.5 mm, A = 661 mm², so r = 3.7 mm.
- f_L ≈ 7.2/(2.853 + 0.369 + 0.073) = **≈ 2.18 GHz**. CST gives a lower edge of **2.16 GHz**.
- The same formula explains the Lg sweep: at Lg = −20 mm, p = 13.7 mm, so f_L ≈ 1.57 GHz, which matches the ≈ 1.6 GHz first dip.
- Printed monopoles often need a substrate correction that lowers the estimate (§0 item 7), so the close match is partly luck.

*Overlapping resonances.*
- Our S₁₁ dips are at 2.73, 4.78, 9.23 and 14.32 GHz.
- Between the dips the match stays under −10 dB. The weakest points are ≈ 6.5 GHz and ≈ 12.2 GHz.
- These are not simple harmonics. The patch and the ground edges both support current modes.

*Role of the ground.*
- In a printed monopole the CPW ground is **the other half of the antenna**: an asymmetric dipole.
  Strong currents flow along the ground's top edge.
- Ground size sets the low-frequency match.
- The **gap p** between the ground and the patch acts as a coupling capacitance. It controls the impedance transition and the match, especially in the mid and high band.
- This is why Lg was the first thing we swept.
- It is also why a **shared ground couples MIMO elements**: ground currents from one element reach the others.

*Patterns.*
- Low frequency: dipole-like, with an omnidirectional H-plane.
- High frequency: higher-order currents give a distorted, tilted pattern and higher cross-polarization.

**Examiner may ask.**
- *"Why a decagon and not a rectangle?"* A 10-sided polygon is nearly a disc. Its smooth outline gives gradual impedance transitions and more overlapping modes, so a wider band. It is also easy to model in CST: a cylinder with 10 segments.
- *"What sets the lowest frequency?"* The overall length L + r + p, which is roughly a quarter wavelength.
- *"Why does the ground matter?"* It is part of the radiator.

### 1.8 MIMO basics

**Simple.**
- MIMO uses several antennas at each end, sending different data streams on the same frequency at the same time.
- Multipath (reflections off walls) makes each transmit-to-receive path different, so the receiver can separate the streams.
- *Analogy:* four people talking in a room. If four listeners stand in different spots, each hears a different mix, and together they can work out who said what.
- For this to work, the antennas must **not "hear the same thing"**. They must be weakly coupled and their patterns must be uncorrelated.

**Deep.**

*Capacity.*
- SISO: C = B·log₂(1 + SNR).
- MIMO: **C = B·log₂ det(I_Nr + (SNR/N_t)·H·Hᴴ)** bit/s.
- In rich scattering C grows roughly as min(N_t, N_r)·log₂(1 + SNR), so capacity grows linearly with the number of antennas.

*Diversity.*
- Several independently fading copies of the signal make deep fades unlikely.
- Types: spatial, **pattern** and **polarization** diversity. Orthogonal elements give the last two.

*Mutual coupling.*
- Current on one element induces current on another through three paths: space waves, surface waves, and **shared ground currents**.
- Effects: efficiency drops, patterns become correlated, and the match changes.
- **Isolation** = −|S₂₁| (dB). Target > 15 dB for compact UWB, > 20 dB is good.

*Isolation techniques.* Spacing, orthogonal orientation, ground slots or stubs (DGS), neutralization lines, parasitic decouplers,
EBG or metasurface layers, and shorting pins.

**ECC (envelope correlation coefficient)** measures how alike the two received signals are. 0 is ideal and 1 is identical.

*From S-parameters (Blanch 2003, 2-port):*
ρₑ = |S₁₁*S₁₂ + S₂₁*S₂₂|² / [(1 − |S₁₁|² − |S₂₁|²)(1 − |S₂₂|² − |S₁₂|²)].
- This assumes **lossless** antennas and a uniform environment.
- On lossy FR-4 it is optimistic, so also compute ECC from the far field.

*From the far field:*
ρₑ = |∬ **F₁**(θ,φ)·**F₂***(θ,φ) dΩ|² / (∬|**F₁**|² dΩ · ∬|**F₂**|² dΩ).
- This needs complex θ and φ patterns of both ports, with a common phase centre.

*Target:* < 0.5 (practical limit). Good designs reach < 0.01.

**DG (diversity gain)** = 10·√(1 − ECC²) dB. Some papers use 10√(1 − ECC).
The ideal is 10 dB. Good designs reach > 9.9 dB.

**TARC (total active reflection coefficient).** This is the "S₁₁" of the whole array when all ports are driven with random phases:
Γ_t = √(Σ|bᵢ|²) / √(Σ|aᵢ|²).
For 2 ports with relative phase θ: Γ_t = √(|S₁₁ + S₁₂e^{jθ}|² + |S₂₁ + S₂₂e^{jθ}|²) / √2.
*Target:* < −10 dB across the band for all θ.

**CCL (channel capacity loss).** The capacity lost to correlation and coupling:
C_loss = −log₂ det(Ψ_R), with Ψ_R = [ρ₁₁ ρ₁₂; ρ₂₁ ρ₂₂],
where ρᵢᵢ = 1 − (|Sᵢᵢ|² + |Sᵢⱼ|²) and ρᵢⱼ = −(Sᵢᵢ*Sᵢⱼ + Sⱼᵢ*Sⱼⱼ).
*Target:* **< 0.4 bit/s/Hz**.

**MEG (mean effective gain).** The average gain received in a multipath environment:
MEGᵢ ≈ 0.5·(1 − Σⱼ|Sᵢⱼ|²) (≈ 0.5·η_rad,i for an isotropic environment).
*Target:* ≈ **−3 dB** (≤ −3 dB), and |MEGᵢ − MEGⱼ| < 3 dB so that the branches have balanced power.

**Examiner may ask.**
- *"Define ECC and give a target."* See above: < 0.5, ideally < 0.01.
- *"Why compute far-field ECC too?"* The S-parameter formula assumes lossless antennas.
- *"Why orthogonal elements?"* Polarization and pattern diversity, and lower coupling.

### 1.9 Metamaterial, metasurface, FSS, AMC and EBG

**Simple.** All of these are man-made periodic patterns of small metal shapes. They differ in what they are made to do.

| Term | What it is | Cell size | Characterised by | Typical use |
|---|---|---|---|---|
| **Metamaterial** | 3D bulk of sub-wavelength cells | ≪ λ (≈ λ/10) | Effective ε, μ (can be negative) | Negative index, cloaking, lenses |
| **Metasurface** | 2D (one or a few layers) version | ≪ λ | Surface impedance, reflection and transmission amplitude and phase | Reflectors, polarization converters, absorbers, beam steering |
| **FSS** | Periodic patches or apertures acting as a **spatial filter** | Often ≈ λ/2 at resonance | Transmission and reflection versus frequency | Radomes, band-stop reflectors, shielding |
| **AMC** | Surface that reflects with **0° phase** at resonance (like a PMC), usually ground-backed | Sub-wavelength | Reflection phase, ±90° band | Low-profile reflectors |
| **EBG** | Periodic structure that **stops surface waves** in a band | Sub-wavelength (mushroom) | Dispersion diagram, bandgap | Suppressing coupling, patch arrays, MIMO decoupling |

The Sievenpiper "mushroom" (patches on a grounded substrate with vias) is *both* an AMC and an EBG.
A ground-backed FSS often behaves as an AMC.
**Our SRR layer is a metasurface. Because it is ground-backed, it is an AMC. Without the ground it would behave like a resonant FSS.**

**Examiner may ask.**
- *"Is your metasurface a metamaterial?"* It is a single-layer, sub-wavelength periodic surface, so a metasurface.
  We characterise it by its reflection phase, not by ε and μ.

### 1.10 Split-ring resonator (SRR)

**Simple.** A metal ring with a cut in it.
- The ring is a one-turn coil, an **inductor L**. The cut is a tiny **capacitor C**. Together they form an **LC tank** that resonates at one frequency.
- *Analogy:* a child on a swing. Push at the right rhythm and the motion grows. The SRR is pushed by the incoming wave.

**Deep.**
- **f₀ = 1/(2π√(LC))** (Hz, with L in H and C in F).
- **L** grows with ring size. For a thin wire loop of radius r and wire radius a: L ≈ μ₀·r·[ln(8r/a) − 2].
  A flat strip of width w behaves roughly like a wire of radius a ≈ w/4.
- **C** is the split-gap capacitance plus, for a double SRR, the much larger inter-ring capacitance.
  A higher εᵣ substrate raises C.
- **Rough length rule (single split ring):** the strip, opened out, resonates like a half-wave line, so mean circumference ≈ λ_g/2
  with λ_g = λ₀/√εeff and εeff ≈ (εᵣ + 1)/2. Use this only for a starting size. Get f₀ from CST.
- **Pendry (1999):** with H **normal** to the ring plane, the induced circulating current is a strong magnetic dipole.
  Just above f₀ the medium has μeff < 0, with a Lorentz shape: μeff = 1 − Fω²/(ω² − ω₀² + jωΓ).
- **Our orientation** (see §0 item 4): at normal incidence H lies in the ring plane, so the ring is excited **electrically** across the split.
  The response depends on polarization (E parallel or perpendicular to the split side), so **align the split with the monopole's
  polarization** and simulate both Floquet polarizations.
- **Tuning knobs:**
  - bigger ring → lower f₀;
  - narrower split, or a second inner ring → more C → lower f₀ (the inner ring also adds a second resonance);
  - higher εᵣ → lower f₀ and a narrower band;
  - thicker grounded substrate → wider in-phase band (§1.11).
- **Our SRR:** two concentric split rings (Pendry type) per cell, 6 × 5 cells on 1.6 mm FR-4, full copper ground on the back. Ring dimensions: [fill in]. Unit-cell period: [fill in].

**Examiner may ask.**
- *"Derive f₀."* f₀ = 1/(2π√(LC)), as above.
- *"What happens if you reduce the gap?"* C rises, so f₀ falls.
- *"Is it magnetic?"* Only for H normal to the ring. In our geometry it is excited electrically, and what matters is the reflection phase.

### 1.11 High-impedance surface (Sievenpiper) and the ±90° band

**Simple.** A metal sheet reflects a wave upside-down (180°). A **high-impedance surface** is patterned so that, near its resonance,
it reflects the wave **right-way-up (0°)**, like an imaginary "magnetic conductor".
*Analogy:* a mirror that keeps a wave's crest as a crest instead of turning it into a trough.

**Deep (mushroom or patch-on-ground model).**
- The surface behaves like a parallel LC with sheet impedance **Z_s = jωL/(1 − ω²LC)**.
  - **L = μ₀μᵣ·t**, where t is the substrate thickness: the current loop through the ground.
  - C comes from the gaps between patches. For square patches of width W and gap g: C ≈ (W·ε₀(1 + εᵣ)/π)·cosh⁻¹((W + g)/g).
- **f₀ = 1/(2π√(LC))**.
- **Reflection:** Γ = (Z_s − η₀)/(Z_s + η₀).
  - At low frequency Z_s → 0, so Γ → −1 (**180°**, PEC-like).
  - At f₀, Z_s → ∞, so Γ → +1 (**0°**, PMC-like).
  - At high frequency the phase heads to −180°.
- **The ±90° band** is where |Z_s| ≥ η₀. Its fractional bandwidth is **≈ (1/η₀)√(L/C) = k₀·t** (μᵣ = 1).
  - Example *(computed)*: t = 1.6 mm at 6 GHz gives ≈ **20 %**.
  - That is why a single-layer FR-4 AMC covers only about 20–30 %, and why a **thicker** substrate widens it.
- **Why ±90°?** A reflected wave within ±90° of the direct wave adds at least +3 dB to it (for equal amplitudes).
- Vias are needed for the **surface-wave bandgap** (EBG). For normal-incidence in-phase reflection, a via-less patch-on-ground AMC also works.

**Examiner may ask.**
- *"What is the in-phase band?"* Where the reflection phase lies between −90° and +90°.
- *"How do you widen it?"* Thicker substrate, lower εᵣ, multiple resonances, or multilayer cells.

### 1.12 Reflector theory: image theory, the PEC λ/4 rule, low-profile AMC

**Simple.** Put a mirror behind the antenna so that the wave going backwards is reflected forwards.
If the reflected wave arrives back **in step** with the wave already going forwards, they add and the forward gain rises.
If it arrives **out of step**, they cancel.

**Deep.**
- **Image theory.** A horizontal current at height h above an infinite PEC behaves like itself plus an **opposite** image at −h.
  - Broadside factor: 2j·sin(k₀h). This peaks at **h = λ/4**.
  - As h → 0 it vanishes: the antenna is "shorted" and its radiation resistance collapses.
- **Above a PMC** the image is **in phase**. The factor is 2cos(k₀h), which is a maximum as h → 0.
  This is why an AMC (an approximate PMC) allows a **low profile**.
- **General ray model.** E_forward ∝ 1 + |Γ|·e^{j(φ_R − 2k₀h)}. **In-phase condition:** φ_R − 2k₀h = 2nπ.
  - Required reflection phase: φ_R = 2k₀h (n = 0).
  - ±90° of that is the "+3 dB" window. ±120° is break-even.
- **PEC needs λ/4.** At 3.1 GHz that is 24.2 mm.
- **Even a PEC at the right spacing cannot cover all of UWB.**
  - With h = λ_c/4, the PEC stays within ±90° only for f between 0.5f_c and 1.5f_c, a 3 : 1 range.
  - Example *(computed)*: h ≈ 12.1 mm (λ/4 at 6.2 GHz) covers ≈ 3.1–9.3 GHz in the ray model.
  - This is why papers using a plain reflector sit at 10–20 mm. **The metasurface's real job is a lower profile.**

**Examiner may ask.**
- *"Why not just use a metal plate?"* At 2 mm a plate is ≈ 165° out of phase at 3.1 GHz.
  It would need ≈ 12 mm to cover most of UWB. We want the profile six times smaller.

### 1.13 CST basics

| | **Time-domain (transient) solver** | **Frequency-domain solver** (what we used) |
|---|---|---|
| Method | FIT on a hexahedral mesh, Gaussian pulse excitation | FEM on a tetrahedral mesh (default), solves at discrete frequencies |
| Broadband | One run gives the whole band | Broadband sweep interpolates between adaptive samples |
| Strengths | Large, broadband, low-Q structures (typical UWB antennas) | Resonant/high-Q, electrically small, curved geometry, **unit cells with Floquet ports** (incl. oblique incidence) |
| Watch out | Needs energy decay to ≈ −40 dB; struggles with high-Q | Interpolation can misbehave (our artefacts); memory grows with mesh |
| Convergence | Refine cells/λ and compare | **Adaptive mesh refinement**: passes until ΔS < threshold |

- **Mesh and convergence.** A result is converged when refining the mesh changes it by less than a tolerance.
  - TD: compare runs at, for example, 15 and 25 cells per wavelength.
  - FD: read the adaptive-refinement passes and ΔS in the solver log.
  - Ours: [fill in] (Appendix A.3).
- **Ports.**
  - *Waveguide port:* 2D eigenmode, correct line impedance. Use it for CPW and microstrip feeds at the board edge.
  - *Discrete port:* a lumped source with internal impedance between two points. Quick, but it adds a lumped gap. Fine for internal feeds and early tests.
- **Boundary conditions.**
  - *Open (add space):* an absorbing boundary (PML) with extra air added, so radiation leaves and the far field can be computed.
  - *Electric* (E_t = 0) and *magnetic* (H_t = 0): symmetry planes and walls.
  - *Unit cell:* periodic boundaries with a phase shift, which model an infinite array.
  - *Floquet port:* the excitation and readout for a periodic cell. At normal incidence, modes TE(0,0) and TM(0,0) carry the two polarizations.
    De-embed the port to the cell's top surface so the phase refers to the surface.
- **Parameter sweep.** Simulation → Parameter Sweep, add a sequence (start, stop, steps). The 1D results overlay all curves.
- **Far-field monitors.** One per frequency. They give directivity, IEEE gain and realized gain; polar cuts; 3D plots;
  0D values (max gain, F/B, efficiencies). **Gain-versus-frequency curves need a monitor at every plotted frequency.**

---

## 2. Our design, step by step

### 2.1 Why wideband (2.1–15 GHz), why a CPW feed, why a monopole

- **Why 2.1–15 GHz wideband.**
  - Covers multiple critical wireless standards in a single compact aperture: 5G sub-6 GHz (n77/n78/n79), the unlicensed UWB spectrum (3.1–10.6 GHz), C-band satellite downlinks, X-band radar, and Ku-band satellite communication up to 15 GHz.
  - Consolidating these bands eliminates the need for multiple narrowband antennas in integrated terminals.
  - Adding MIMO in Phase II dramatically raises channel capacity, spectral efficiency, and multipath link reliability.
- **Why a CPW feed.**
  - It is uniplanar, so one copper layer and cheap fabrication.
  - The ground lies beside the patch in the same plane and is part of the radiator. Its edge (Lg) is a strong tuning knob.
  - The back of the board has no copper, so a reflector can be placed behind it, which is the whole point of Phase I.
- **Why a disc-like (decagonal) monopole.**
  - It is the textbook wideband radiator: many overlapping modes, a simple geometry, near-omnidirectional patterns and modest gain.
  - Its weakness is that it radiates **both ways**, giving low forward gain (a few dBi) and F/B ≈ 0 dB.
  - That weakness is exactly what the metasurface is meant to fix.

### 2.2 Geometry and dimension table

| Parameter | Meaning | Value |
|---|---|---|
| Substrate | FR-4 (lossy) | εᵣ = 4.3, tan δ = 0.025, h = 1.6 mm; copper on the front only, back bare |
| Ws × Ls | Board size | 50 × 50 mm |
| R | Circumradius of the regular decagon, centred at x = 8 mm | **15 mm** (optimised) |
| Lg | Coordinate of the CPW grounds' edge along the feed axis (x) | **−7 mm** (optimised; initial baseline was −20 mm) |
| W_f | Feed strip width | 3 mm |
| G | CPW slot width | 0.5 mm |
| Ground planes | Each ground plane's extent | x from −25 to −7 mm (18 mm); 23 mm wide (|y| from 2 to 25 mm) |
| p | Feed gap = patch's lower edge − Lg | **0.73 mm** (optimised) / **13.73 mm** (initial baseline) |
| Copper | Thickness t | 0.035 mm (standard 1 oz copper) |
| h (gap) | Antenna-to-metasurface air gap | **2 mm** |
| SRR cell | Two concentric split rings; period, ring radii, strip width, split | [fill in] |
| Metasurface | Cells, substrate, back | 6 × 5 cells, 1.6 mm FR-4, full copper ground |
| Board margin | Patch top to board edge | 2.7 mm (limits R) |
| Total profile | 1.6 + 2 + 1.6 mm | ≈ 5.2 mm plus copper *(computed)* |

### 2.2b Initial Antenna Baseline and Baseline S₁₁ (Lg = −20 mm)

- **Initial Geometry:**
  - In the unoptimized initial design, the ground patch ended at Lg = −20 mm (along the feed axis), creating an unusually large feed gap p = (8 − 15·cos 18°) − (−20) ≈ 13.73 mm.
  - The patch radius was set to R = 15 mm.
- **Baseline S₁₁ Response:**
  - The baseline reflection coefficient showed **very poor impedance matching across almost the entire 2.1–15 GHz operating band**.
  - Except for an isolated, solitary dip near ≈ 1.6 GHz (|S₁₁| ≈ −14 dB), the curve stayed completely above the −10 dB threshold (|S₁₁| > −10 dB from 2.5 GHz all the way to 18 GHz).
- **Physical Reason for Failure:**
  - The large 13.73 mm gap between the ground planes and the patch introduced excessive series inductance and failed to provide capacitive coupling at the feed transition.
  - Furthermore, the long exposed feed line acted as an extended radiator, creating an unintended low resonance at 1.6 GHz while failing to excite broadband higher-order modes.
- **Optimization Strategy:**
  - This poor baseline directly motivated the parametric sweep of Lg from −20 mm up to −7 mm to find the optimal transition gap.

### 2.3 What Lg does physically, and how to read the Lg sweep

- **Physics.** Lg is the coordinate of the CPW grounds' edge along the feed axis. Moving it from −20 mm towards −7 mm moves the ground edge **closer to the patch**, shrinking the gap from p ≈ 13.7 mm to 0.73 mm.
  1. The length of exposed feed line between the ground and the patch **shrinks**. A long exposed feed radiates as an extension of the monopole,
     so the effective radiator is long and the first resonance is low (≈ 1.6 GHz). A shorter exposed feed raises it towards ≈ 2.7 GHz.
     This matches the f_L formula: smaller p gives a higher f_L.
  2. The **ground–patch gap p** sets the coupling capacitance at the feed transition. A smaller gap gives a smoother impedance transition from 50 Ω to the radiator,
     so the dips get deeper and the match improves across the band.
- **Reading the plot.**
  - The x-axis is frequency (0–18 GHz) and the y-axis is |S₁₁| in dB, with one curve per Lg value. Draw the −10 dB line.
  - For each curve, look at the **lowest frequency where it crosses −10 dB**, then **whether it stays below −10 dB** to the top of UWB.
  - The **best curve** is the one with the widest continuous region under −10 dB that covers 3.1–10.6 GHz with margin.
  - Point out the trend: the first dip shifts right and deepens as Lg goes from −20 to −7.
- **Best: Lg = −7 mm.**

### 2.4 What R does physically, and how to read the R sweep

- **Physics.**
  - The patch radius sets the radiator size, so it sets the **lowest frequency** (L = 2R·cos 18° in the f_L formula).
  - A bigger patch also supports more, closer-spaced modes, so it gives a **wider continuous band**.
  - Small patches (4 mm) are too short to resonate low and give narrow, high-frequency matches.
  - As R grows towards 15 mm the band extends downwards and fills in.
- **Coupling caveat.** The patch is placed by its centre (x = 8 mm), so changing R also changed the feed gap p, from ≈ 11.2 mm at R = 4 mm to 0.73 mm at R = 15 mm (§0 item 6). Say so if asked.
- **Reading the plot.** The axes are the same as for Lg. Follow the **lower −10 dB edge moving left** as R increases, and the gaps between dips filling in.
- **Best: R = 15 mm**, the widest continuous −10 dB band.

### 2.5 The optimised S₁₁: four resonances and weak points

- **−10 dB band:** **2.1615 → 15.734 GHz**, a **151.7 % FBW**. It covers all of 3.1–10.6 GHz, with a 0.94 GHz margin below 3.1 GHz
  and a 5.1 GHz margin above 10.6 GHz *(computed)*.
- **Resonances (dips):**

  | f (GHz) | \|S₁₁\| (dB) |
  |---|---|
  | 2.7275 | −32.65 |
  | 4.7824 | −21.18 |
  | 9.2265 | −22.56 |
  | 14.32 | −27.07 |

- **Weak points:** ≈ 6.5 GHz (≈ −10.3 dB) and ≈ 12.2 GHz (≈ −10.5 dB).
  - These are the "valleys between dips", where one mode has faded and the next has not yet taken over.
  - They are only 0.3–0.5 dB inside the limit, so **little margin**. Fabrication tolerance or the metasurface could push them above −10 dB.
  - Say this yourself before the examiner does.
  - Possible fixes if they break: re-tune Lg or p, change the feed gap shape (taper or bevel), or add a ground slot.
- **Why the band extends far beyond 10.6 GHz.** A disc-like monopole is naturally very wideband.
  The extra band is margin. We do not claim operation there, because the pattern degrades at high frequency.

### 2.6 How to read the gain plot

- The x-axis is frequency and the y-axis is CST "Gain" (IEEE) in dBi, the maximum over all directions at each frequency.
- **Values (read from the plot, ±0.1 dB):**
  - ≈ 1 dBi at 2 GHz;
  - ≈ 3.3 dBi near 3.6 GHz;
  - **≈ 2.9–4.9 dBi across 3.1–10.6 GHz** (lowest near 6.3 GHz, highest near 8.5 GHz);
  - peak ≈ 5.1 dBi near 13.5 GHz.
- **Interpretation.**
  - These values are typical of a bidirectional planar monopole: 2–5 dBi in the literature.
  - The rise with frequency comes from growing electrical size, which makes the pattern more directive.
  - The dip near 6.3 GHz coincides with the weak match near 6.5 GHz. It probably marks a **current-mode transition** where the pattern changes shape.
    *Hypothesis: confirm by looking at the 3D pattern or surface current at 6.3 GHz.*
  - **This is IEEE gain.** Realized gain is at most 0.46 dB lower inside the −10 dB band (§1.4).

### 2.7 What "best" means, and why the optima sit at the sweep edge

- **Criterion.**
  1. The −10 dB band must cover all of 3.1–10.6 GHz.
  2. Among the curves that do, pick the widest continuous band and the deepest worst-case in-band S₁₁.

  State this criterion explicitly. Examiners dislike a "best" with no definition.
- **Edge optimum.**
  - Lg = −7 mm leaves a gap of only p = 0.73 mm. Moving further would shrink the gap towards zero and then make the parts overlap.
  - R = 15 mm puts the patch top 2.7 mm from the edge of the 50 mm board. A bigger patch would not fit.
  - So "best" means **best within the constraint**, and the true unconstrained optimum may lie beyond it.
  - That is normal when the board size is fixed. Mention that a joint optimisation (CST optimiser, Trust Region) is possible.

### 2.8 The sweep artefacts (say it before they ask)

- **What we see.** Some sweep curves jump at ≈ 4.0 and ≈ 6.2 GHz, and one Lg curve rises **above 0 dB**.
- **Why above 0 dB is impossible.** For a passive antenna |S₁₁| ≤ 1, so |S₁₁|(dB) ≤ 0. Above 0 dB would mean more power coming out than going in.
- **Why we think it is numerical.**
  - The frequency-domain solver's broadband sweep computes the field at a limited number of frequency samples and **interpolates** a rational-function model between them.
  - If the sweep stops before it converges, or a resonance falls between samples, the interpolated curve can jump or exceed physical limits.
  - Jumps at the **same frequencies in several curves** point to the sweep, or to the port's mode set (a higher-order port mode switching on), rather than to antenna physics.
  - The final optimised run is smooth and physically valid.
- **What we did and will do.** We use only the final smooth run for numbers.
  To confirm, re-run the affected parameter values with more frequency samples and a tighter convergence setting, or with the time-domain solver,
  and check the port-mode cut-off list (Appendix A.4).

### 2.9 The SRR unit cell, the antenna + metasurface step, and why the PEC baseline matters

**Unit cell (status: pending).**
1. Draw one double-split-ring cell on 1.6 mm FR-4 with its copper ground.
2. Set **unit-cell boundaries** in x and y and a **Floquet port** on Zmax. Our cell is ground-backed, so Zmin can be an electric wall.
3. Read the reflection **phase and magnitude** of S(Zmax,Zmax), de-embedded to the cell surface.
4. Compare it with the required curve φ_R = 2k₀h ± 90° (§3.4).

Appendix A.5 gives the steps.

**Antenna + metasurface (status: pending).**
- Place the 6 × 5 array at h = 2 mm behind the board.
- Re-run S₁₁ (near-field loading will detune it, so expect to re-tune Lg) and the gain, F/B and patterns.

**Why the PEC baseline matters.**
- Without it, any gain increase could be credited to "having a reflector" rather than to the metasurface's phase engineering.
- A **metal plate of the same size at the same 2 mm** is the fair control. Theory predicts it fails across UWB (§3.4).
- If the SRR beats the plate, that is direct evidence that the reflection phase is doing the work.
- Very few papers show this comparison, so it is a strength of our plan.

---

## 3. Theory with equations and intuition

### 3.1 Lower band-edge estimate

- **Formula:** f_L ≈ 7.2/(L + r + p) GHz, with lengths in cm.
  - For a disc: L = 2R and r = R/4. For our decagon: L = 2R·cos 18° = 28.5 mm and r = A/(2πL) = 3.7 mm (A = 661 mm²). p is the feed gap.
- **Our numbers** *(computed)*:
  - L + r + p = 2.853 + 0.369 + 0.073 = 3.295 cm, so f_L ≈ **2.18 GHz**. CST gives 2.16 GHz.
  - At Lg = −20 mm (p = 13.7 mm), f_L ≈ 1.57 GHz, which matches the ≈ 1.6 GHz first dip in the Lg sweep.
- **Intuition.** L + r + p is roughly the quarter-wave "electrical height" of the monopole. A bigger patch means a longer quarter-wave, so a lower f_L.
- **Caveats.**
  - The formula is empirical and assumes free space over a large ground.
  - Printed monopoles add a substrate correction that lowers f_L.
  - Treat agreement within ≈ 10–20 % as good.

### 3.2 Fractional bandwidth; realized versus IEEE gain

- **FBW** = 2(f_H − f_L)/(f_H + f_L) = 2(15.734 − 2.1615)/(17.8955) = **151.7 %**. The ratio bandwidth is 7.28 : 1.
- **For UWB:** 2(10.6 − 3.1)/13.7 = 109.5 % (3.42 : 1).
- **Realized gain:** G_R = (1 − |S₁₁|²)·G.
  - At −10 dB, 1 − 0.1 = 0.9, which is −0.46 dB.
  - At the deep dips the difference is negligible (≈ 0.03 dB at −21 dB).
  - Below 3.1 GHz, near the lower band edge, the difference grows quickly: −1.26 dB at −6 dB.
  - So **the ≈ 1 dBi at 2 GHz is IEEE gain at a frequency outside the band. Realized gain there is lower still.**

### 3.3 SRR resonance

- f₀ = 1/(2π√(LC)).
- Size down or C down gives a higher f₀. A bigger ring or a narrower split gives a lower f₀.
- Double rings add inter-ring C, which lowers f₀ and can add a second resonance.
- With a ground behind it, the cell becomes a resonant surface impedance. Below f₀ the reflection phase is positive and falls through 0° at about f₀.
- **Our SRR:** f₀ = [fill in from unit-cell simulation]. Phase-crossing frequency (0°) = [fill in]. ±90° band = [fill in].

### 3.4 The full in-phase gap analysis, with our numbers

**Set-up.**
- The antenna radiates forwards (+z) and backwards (−z).
- The backward wave travels h = 2 mm, reflects with coefficient |Γ|e^{jφ_R}, and travels 2 mm back.
- Relative to the forward wave it carries the phase **φ_R − 2k₀h**.
- **In-phase condition:** φ_R − 2k₀h = 2nπ, which gives the **required reflection phase φ_R = 2k₀h** (n = 0).
- Here 2k₀h in degrees = 720°·h/λ₀.

**Phase table** *(computed; ray model, |Γ| = 1, near field ignored)*

| f (GHz) | λ₀ (mm) | h/λ₀ | 2k₀h = required φ_R | ±90° window for φ_R | PEC phase error 180° − 2k₀h | PEC ray factor vs direct ray alone |
|---|---|---|---|---|---|---|
| 2.16 | 138.7 | 0.014 | 10° | −80° … 100° | 170° | 0.18 (−14.9 dB) |
| 3.1 | 96.7 | **0.021** | **15°** | −75° … 105° | **165°** | 0.26 (**−11.7 dB**) |
| 4.78 | 62.7 | 0.032 | 23° | −67° … 113° | 157° | 0.40 (−8.0 dB) |
| 6.85 | 43.8 | 0.046 | 33° | −57° … 123° | 147° | 0.57 (−4.9 dB) |
| 10.6 | 28.3 | 0.071 | 51° | −39° … 141° | 129° | 0.86 (−1.3 dB) |
| 12.5 | 24.0 | 0.083 | 60° | −30° … 150° | 120° | 1.00 (0 dB, break-even) |
| 15.73 | 19.1 | 0.105 | 76° | −14° … 166° | 104° | 1.23 (+1.8 dB) |
| 18 | 16.7 | 0.120 | 86° | −4° … 176° | 94° | 1.37 (+2.7 dB) |

The ray factor is |1 + e^{jΔ}| = 2|cos(Δ/2)|, where Δ is the phase error.

**(a) Why a metal plate fails at 2 mm.**
- A PEC has φ_R = 180°. It would need 2k₀h = 180°, that is **h = λ/4 = 24.2 mm at 3.1 GHz**.
- At 2 mm it is 165° out of phase at 3.1 GHz, so the ray model gives about −11.7 dB relative to the direct ray.
- It never enters the ±90° window in our simulated band (only above ≈ 18.7 GHz) and breaks even only at ≈ 12.5 GHz.
- **In the near field** it is worse. The image current is opposite and only 2 × 2 mm away, so it largely **cancels the antenna's own current**.
  Radiation resistance collapses and the match is destroyed, especially at low frequency.
- **Conclusion:** a plate at 2 mm hurts all of UWB and helps only slightly (under +3 dB) above ≈ 12.5 GHz.

**(b) The reflection-phase curve our SRR must have.**
- Over 3.1–10.6 GHz, the windows intersect at **φ_R ∈ [−39°, 105°]**.
- In words: the surface must reflect with a phase **between about −40° and +105° across the whole band**.
  A small, slowly varying phase, centred near ≈ +33°, would satisfy every frequency.
- Over the full simulated band (2.16–15.73 GHz) the strip narrows to [−14°, 100°].

**(c) Why one SRR resonance cannot cover a 7 : 1 band (or even 3.4 : 1).**
1. **Foster's reactance theorem.** For a lossless passive surface, the reflection phase **decreases** monotonically with frequency.
   But the *required* phase 2k₀h **increases** with frequency. So the two curves move in opposite directions and can stay close only over a limited band.
2. **Bandwidth.**
   - A single-resonance ground-backed cell sweeps from +180° through 0° to −180°.
   - Its ±90° bandwidth is only ≈ k₀·t, about **20 %** for 1.6 mm FR-4 at 6 GHz *(computed)*.
   - Staying inside a 144°-wide strip over a 109 % band would need a phase curve many times flatter than that.
3. **Bare (no-ground) sheet.**
   - Γ = −1/(1 + 2Z_s/η₀) gives a phase between 90° and 270°, and ≈ 180° at the SRR's own resonance.
   - It can be inside the window at 3.1 GHz (≤ 105°) only where |Γ| ≤ ≈ 0.26. At 100° |Γ| ≈ 0.17 *(computed)*.
   - So it reflects weakly exactly where we need help. It can help only near the top of the band, where the window approaches 180° (166° at 15.73 GHz).
4. **Honest expectation.** The metasurface will improve the gain over **part** of UWB, probably a sub-band of a few GHz, unless the cell is broadened.

**(d) Ways to widen the in-phase band.**
- **Dual or multiple resonances:** two rings, or ring + patch. Two adjacent resonances create a **phase plateau** between them.
- **Varying split angle across the array, as in Sen 2017:** cells with different resonances spread the response over frequency.
- **Multi-layer stacks:** two SRR layers at different heights or sizes.
- **Thicker substrate:** the ±90° band scales roughly as k₀·t, so 3.2 mm stacked FR-4 roughly doubles it. A lower-εᵣ (or foam) spacer also helps in practice, and has lower loss.
- **Accept a sub-band** and say so: "gain improvement over X–Y GHz, no degradation elsewhere".
- **Trade the gap:** a sweep of h (for example 2 to 10 mm) gives a gain-versus-profile curve. That is a useful result in itself.

**(e) Near-field loading and re-tuning Lg.**
- At 0.021λ the metasurface sits inside the reactive near field (λ/2π > 2 mm below ≈ 23.9 GHz).
- It adds capacitance and inductance to the antenna's input impedance. This typically **shifts the resonances and the weak points** (6.5 and 12.2 GHz have only ≈ 0.3–0.5 dB margin).
- Plan: simulate antenna + metasurface, then **re-sweep Lg (and p) with the metasurface in place**, then report S₁₁ and gain, both IEEE and realized.
- Watch for the band edges and the two weak valleys.
- Also report **realized gain**: a metasurface that adds 3 dB of directivity but ruins the match can lose it all at the port.

---

## 4. Literature review explained

> Two papers were read in full. The other eight come from abstracts and publisher pages. Say this if asked (§7).
> All numbers are as given in our literature review. Check any number before you defend it in detail.

### 4.1 Part 1: single antennas with a reflector

- **Sen 2017.**
  - Split-ring metasurface reflector behind a UWB circular monopole, with ≈ +5.5 dB gain.
  - **Relevance:** closest to our Phase I idea (SRR behind a UWB disc-like monopole).
  - Its trick of **varying split angles** to broaden the response is one of our widening options.
- **Al-Gburi 2022.**
  - CPW-fed ring monopole on 1.6 mm FR-4, grown from a 15 mm-radius disc, so the same size as our R = 15 mm patch.
  - A 19 × 19 ground-backed FSS gives a 10 mm total profile.
  - Gain 6.7 → 11.5 dB; measured band 2.2–11.9 GHz.
  - **Relevance:** same feed, substrate and patch size. It shows that a large ground-backed FSS can nearly double the gain in dB terms.
- **Hussain 2023.**
  - CPW hexagonal patch on Rogers 6002 with a 5 × 5 FSS at 9 mm.
  - The band widened from 5–17 to 3–18 GHz and the gain rose from 6.5 to 10.5 dBi. Measured.
  - **Relevance:** the reflector can **widen** the band as well as raise the gain, at a 9 mm gap.
- **Hammache 2024.**
  - A 30 × 30 mm CPW hexagon with a 7 × 7 FSS at **20 mm**.
  - **Realized** gain 2.2 → 8.4 dBi.
  - **Relevance:** a large improvement, but at a profile ten times ours.
- **AboEl-Hassan 2025.**
  - CPW octagonal monopole over a 5 × 5 ground-backed AMC across an air gap.
  - Band 3.5–6.5 GHz (not full UWB). Gain up to 9.9–11.5 dBi (the sources differ).
  - **Relevance:** an AMC gives high gain but over a narrower band. This is the bandwidth limit of §3.4 in action.

### 4.2 Part 2: MIMO with a metasurface

- **Sufian 2021.**
  - 4-port, 3.3–3.87 GHz (narrowband 5G).
  - Isolation > 32 dB, ECC < 0.001.
  - Ground slots + shorting pins; element gain 6.3 → 8.1 dBi.
  - **Relevance:** shows the isolation techniques we may borrow.
- **Sehrai 2021** (IEEE Access 9, 125348; not Tariq).
  - 4-port mm-wave, 23.5–29.4 GHz, 24 × 24 mm.
  - A 2 × 2 metasurface behind; gain ≈ 7 → 10.44 dB.
  - **Relevance:** the same "metasurface behind MIMO" concept at mm-wave.
- **Hasan 2022: our closest MIMO counterpart.**
  - 4-port with a copper-backed 10 × 10 metasurface of square-enclosed circular SRRs at a **12 mm** air gap.
  - Band ≈ 3.1–7.7 GHz. Realized gain 5.4 → 8.3 dBi.
  - Isolation > 15.5 dB, ECC < 0.004.
- **Althuwayb 2023.**
  - Flexible 2 × 2 array; slotted radiators + EBG.
  - 5.0–6.6 GHz; isolation > 34.8 dB; ≈ 10 dBi.
  - **Relevance:** EBG for decoupling.
- **Wu 2023.**
  - 2-port wearable with a polarization-conversion metasurface.
  - 4.76–6.77 GHz, **circularly polarized**, 7.95 dBic.
  - **Relevance:** a metasurface can also change the polarization, not just the gain.

### 4.3 Comparison table: how to present it

Put this on slide 5 or a backup slide. Use **one row per paper** and **one row for "This work (Phase I / planned)"**.
Columns: Ports | Band (GHz) | Feed | Reflector type | Gap (mm / λ) | Gain without → with | Isolation / ECC | Measured?

| Work | Ports | Band (GHz) | Reflector | Gap | Gain (without → with) |
|---|---|---|---|---|---|
| Sen 2017 | 1 | UWB | SRR metasurface | [check] | ≈ +5.5 dB |
| Al-Gburi 2022 | 1 | 2.2–11.9 (meas.) | 19×19 ground-backed FSS | 10 mm total profile | 6.7 → 11.5 dB |
| Hussain 2023 | 1 | 3–18 | 5×5 FSS | 9 mm | 6.5 → 10.5 dBi |
| Hammache 2024 | 1 | [check] | 7×7 FSS | 20 mm | 2.2 → 8.4 dBi (realized) |
| AboEl-Hassan 2025 | 1 | 3.5–6.5 | 5×5 ground-backed AMC | air gap [check] | up to 9.9–11.5 dBi |
| Sufian 2021 | 4 | 3.3–3.87 | metasurface + slots/pins | [check] | 6.3 → 8.1 dBi |
| Sehrai 2021 | 4 | 23.5–29.4 | 2×2 metasurface | [check] | ≈ 7 → 10.44 dB |
| **Hasan 2022** | 4 | ≈ 3.1–7.7 | 10×10 SRR, copper-backed | 12 mm | 5.4 → 8.3 dBi (realized) |
| Althuwayb 2023 | 2×2 | 5.0–6.6 | EBG | [check] | ≈ 10 dBi |
| Wu 2023 | 2 | 4.76–6.77 | polarization-conversion metasurface | [check] | 7.95 dBic |
| **This work** | 1 → 4 (Phase II) | 2.16–15.73 (antenna alone, sim.) | SRR metasurface | **2 mm (0.021λ at 3.1 GHz)** | 2.9–4.9 dBi (IEEE, alone) → [pending] |

How to talk through it:
1. Read the table **by column, not by row**: "Look at the gap column: 9, 10, 12, 20 mm. Ours is 2."
2. "Look at the band column for the MIMO papers: none of the five we reviewed covers full UWB."
3. "Every paper shows gain with and without the reflector, but few compare against a metal plate at the same gap."

### 4.4 Research gap and novelty: confident but honest

**Gap statement (say it like this):**
> "Among the papers we reviewed, reflectors behind UWB monopoles use gaps of about 9 to 20 mm, which is roughly 0.1 to 0.2 λ at 3.1 GHz.
> Split-ring cells behind a full-UWB CPW antenna are rare. Papers rarely compare their metasurface against a plain metal plate at the same gap.
> The MIMO-plus-metasurface designs we reviewed are all narrower than UWB, such as Hasan 2022 at 3.1–7.7 GHz.
> We are aiming at the intersection: a full-UWB CPW antenna, an SRR reflector at only 2 mm (0.021 λ), a fair metal-plate baseline, and then a 4-port MIMO."

**Novelty versus Hasan 2022:**
- Their band is ≈ 3.1–7.7 GHz. We target the full 3.1–10.6 GHz.
- Their gap is 12 mm. Ours is 2 mm, six times thinner.
- We plan an explicit PEC baseline at the same gap.

**Novelty versus Al-Gburi 2022:**
- Theirs is a single antenna. Ours goes on to MIMO.
- Their profile is 10 mm with a 19×19 FSS. Ours has a 2 mm gap.
- We use SRR cells rather than their FSS cell.

**Honest caveat to keep in mind:** UWB MIMO antennas with reflectors or AMCs *do* exist outside our review (§0 item 2).
So the novelty is the **combination** (SRR + 0.021 λ gap + PEC baseline + full UWB + MIMO), not any single element.
And until the metasurface results are in, the novelty is a **hypothesis we are testing**, not a result.

---

## 5. Presentation: slide-by-slide (≈ 15 min)

**Default speaker split.** The team chose to set the split themselves but did not send it, so this is a contiguous default.
Swap names freely; the timings stay.

| Speaker | Slides | Time |
|---|---|---|
| **Chanswarang Boro** | 1, 2, 3 and 15 | ≈ 3:00 |
| **Anushka Dam** | 4, 5, 6 | ≈ 3:15 |
| **Nishit Baishya** | 7, 8, 9, 10 | ≈ 4:00 |
| **Sanjana** | 11, 12, 13, 14 | ≈ 4:15 |

Total ≈ 14:30, which leaves 30 s of slack. Speaking rate ≈ 130 words per minute.
Each script below is roughly what to say, not something to read out. **Bold** marks the one message each slide must land.

---

**Slide 1: Title (Chanswarang, 0:30)**
- *Points:* title, team, guide and co-guide, date.
- *Script:* "Good morning. We are presenting our final-year project, *Wideband MIMO Antenna with Metasurface*,
  under the guidance of Dr. Ujjal Chakraborty, with Mr. Sovan Bhattacharya as co-guide. I'm Chanswarang, and with me are Nishit, Anushka and Sanjana.
  In one line: **we are building an ultra-wideband antenna and placing a thin metasurface just 2 mm behind it to push its radiation forward.**
  Later it becomes a MIMO antenna."

**Slide 2: Introduction and problem statement (Chanswarang, 1:15)**
- *Points:*
  - UWB 3.1–10.6 GHz (FCC), used for ranging, imaging and high-rate short links.
  - MIMO gives capacity and reliability.
  - Printed monopoles are wideband but radiate both ways, so their gain is low (a few dBi).
  - A metal reflector needs λ/4 (24 mm at 3.1 GHz), which is too thick.
- *Script:* "UWB uses the 3.1 to 10.6 gigahertz band the FCC opened in 2002, for precise positioning, imaging and fast short-range links.
  Printed monopole antennas cover this band easily, but they radiate equally forwards and backwards, so their gain is only a few dBi.
  The classic fix is a metal plate behind the antenna. But a metal plate must sit a quarter wavelength away, which is about 24 millimetres at 3.1 gigahertz,
  and even then it works over only part of the band.
  **Our problem is: can we get forward gain over UWB with a much thinner reflector?** That is what a metasurface promises."

**Slide 3: Objectives (Chanswarang, 0:45)**
- *Points:*
  1. A CPW-fed decagonal monopole covering all of UWB (|S₁₁| ≤ −10 dB).
  2. Optimise it by parametric study (Lg, R).
  3. Design an SRR metasurface and place it 2 mm behind; compare with no reflector and a metal plate.
  4. Phase II: 2- or 4-port MIMO with the metasurface, then fabrication and measurement.
- *Script:* "We have four objectives. First, a single CPW-fed decagonal monopole covering the full UWB band. Second, optimise it with a parametric study.
  Third, design a split-ring-resonator metasurface and test it 2 millimetres behind the antenna, **compared fairly against both no reflector and a metal plate at the same gap**.
  Fourth, after mid-sem, extend it to a multi-port MIMO antenna and fabricate it. Today we report objectives one and two complete, and three in progress.
  I'll hand over to Anushka for the literature."

**Slide 4: Literature I, single-antenna reflectors (Anushka, 1:15)**
- *Points:* Sen 2017, Al-Gburi 2022, Hussain 2023, Hammache 2024, AboEl-Hassan 2025 (one line each). Gains of +4 to +6 dB, but at gaps of 9–20 mm.
- *Script:* "We reviewed ten papers in two groups. Single antennas first.
  Sen 2017 put a split-ring metasurface behind a UWB circular monopole and gained about 5.5 dB.
  Al-Gburi 2022 used a CPW ring monopole on FR-4, grown from a 15 mm disc, the same size as our patch, with a ground-backed FSS: gain from 6.7 to 11.5 dB, with a 10 mm profile.
  Hussain 2023 placed an FSS at 9 mm, and Hammache 2024 at 20 mm, raising realized gain from 2.2 to 8.4 dBi.
  AboEl-Hassan 2025 reached about 10 dBi with an AMC, but only from 3.5 to 6.5 GHz.
  **The pattern: big gains, but at gaps of 9 to 20 millimetres, or over a narrower band.**"

**Slide 5: Literature II, MIMO + metasurface and the research gap (Anushka, 1:15)**
- *Points:* Sufian, Sehrai, Hasan, Althuwayb, Wu. Hasan 2022 is closest. All five are narrower than UWB. Then the four-point research gap.
- *Script:* "For MIMO with metasurfaces, the closest to us is Hasan 2022: four ports, a copper-backed split-ring metasurface 12 mm behind,
  realized gain from 5.4 to 8.3 dBi, isolation above 15.5 dB, but covering only about 3.1 to 7.7 GHz.
  The others (Sufian, Sehrai, Althuwayb and Wu) are narrowband sub-6, mm-wave, or wearable designs.
  **So the gap, among the papers we reviewed, is: no full-UWB design with an SRR reflector at a gap as small as ours, few fair comparisons against a metal plate,
  and no MIMO-plus-metasurface design covering full UWB.** That is where we aim."

**Slide 6: Proposed methodology (Anushka, 0:45)**
- *Points:* a flow chart:
  1. decagonal monopole;
  2. Lg sweep;
  3. R sweep;
  4. optimised antenna;
  5. SRR unit cell (Floquet);
  6. antenna + metasurface versus PEC;
  7. 2/4-port MIMO;
  8. fabrication and measurement.

  CST 2019, frequency-domain solver, 0–18 GHz.
- *Script:* "Our method is step by step: design the element, sweep the ground edge, then the radius, and fix the optimum.
  Separately, design the SRR unit cell with periodic boundaries to get its reflection phase. Then put the metasurface behind the antenna and compare it with a metal plate.
  Phase II builds the MIMO version. Everything is simulated in CST 2019 with the frequency-domain solver from 0 to 18 GHz.
  Nishit will now explain why 2 millimetres is hard."

**Slide 7: Theory: why a metasurface at 2 mm (Nishit, 1:15)**
- *Points:*
  - In-phase condition φ_R − 2k₀h = 2nπ.
  - Table: 2k₀h = 15° at 3.1 GHz, 51° at 10.6 GHz.
  - A metal plate (180°) is 165° off at 3.1 GHz and never within ±90° in our band (only above ≈ 18.7 GHz).
  - The required metasurface phase is ≈ −40° to +105°.
  - Caveat: the near field at 0.021 λ.
- *Script:* "The backward wave travels to the reflector and back, which is 4 millimetres in total. It comes back with an extra phase of 2k-naught-h plus whatever phase the reflector adds.
  For it to add to the forward wave, the reflector phase must equal 2k-naught-h. At 2 mm that is only 15 degrees at 3.1 GHz and 51 degrees at 10.6 GHz.
  A metal plate reflects with 180 degrees, so at 3.1 GHz it is 165 degrees out of phase. It cancels rather than adds.
  It never gets within 90 degrees anywhere in our band; that would take about 18.7 GHz.
  **So a metal plate cannot work at this gap. We need a surface with a small positive reflection phase, which is what a metasurface can engineer.**
  One caveat: 2 mm is only 0.021 wavelengths, deep in the near field, so this ray picture is a guide and we must re-check the matching in simulation."

**Slide 8: Antenna design (Nishit, 0:45)**
- *Points:* geometry figure (`figures/cst_single_geometry.png`); dimension table (50 × 50 mm FR-4, εᵣ 4.3, 1.6 mm; decagon R = 15 mm; Lg = −7 mm; feed 3 mm, slots 0.5 mm; gap p = 0.73 mm); waveguide port; open boundaries.
- *Script:* "This is our antenna: a ten-sided patch, almost a disc, fed by a coplanar waveguide on a 50 by 50 millimetre FR-4 board. The two CPW grounds sit beside the feed on the same side, and act as the other half of the antenna.
  The final dimensions are in the table: radius 15 mm, ground edge at minus 7 mm, which leaves a 0.73 mm gap to the patch. We excite it with a waveguide port, and the boundaries are open."

**Slide 9: Parametric study, Lg (Nishit, 1:00)**
- *Points:* ten values from −20 to −7 mm at R = 15 mm. The first resonance moves from ≈ 1.6 to ≈ 2.7 GHz and the matching improves. Best Lg = −7 mm.
- *Script:* "First we swept the ground edge position Lg over ten values from minus 20 to minus 7 mm.
  Moving the ground towards the patch shortens the exposed feed and tightens the coupling gap, so the first resonance moves up from about 1.6 to 2.7 GHz,
  and the matching across the band improves. **Lg = −7 mm gave the best match.**
  [Point at the curve.] You'll notice some curves jump near 4 and 6.2 GHz, and one goes above 0 dB. That is physically impossible for a passive antenna.
  It's a numerical artefact of the broadband frequency sweep, which we explain on a backup slide. The final optimised run is smooth."

**Slide 10: Parametric study, R (Nishit, 1:00)**
- *Points:* 13 values from 4 to 15 mm at Lg = −7 mm. A bigger patch gives a lower band edge and more overlapping modes. Best R = 15 mm. Both optima sit at the edge, set by the board.
- *Script:* "Then, with Lg fixed, we swept the patch radius from 4 to 15 mm. A bigger patch is a longer radiator, so the band starts lower,
  and it supports more overlapping resonances, so the band fills in. **R = 15 mm gave the widest continuous band.**
  Both optimum values sit at the edge of their sweep range. That's because the board size limits how big the patch can be, with only 2.7 mm left to the board edge, and how close the ground can come, with only a 0.73 mm gap left.
  So these are the best values within the board constraint. Sanjana will now show the optimised result."

**Slide 11: Optimised antenna, S₁₁ and gain (Sanjana, 1:15)**
- *Points:*
  - −10 dB band 2.1615–15.734 GHz: FBW 151.7 %, covering all of UWB.
  - Four dips: 2.73, 4.78, 9.23, 14.32 GHz.
  - Weak points at 6.5 and 12.2 GHz.
  - Gain 2.9–4.9 dBi across UWB, peak ≈ 5.1 dBi (IEEE gain).
- *Script:* "The optimised antenna is matched below minus 10 dB from 2.16 to 15.73 GHz, a fractional bandwidth of 151.7 percent, covering the whole UWB band with margin.
  There are four resonances, at 2.73, 4.78, 9.23 and 14.32 GHz. The deepest is minus 32.6 dB.
  Between them the match is weakest near 6.5 and 12.2 GHz, at about minus 10.3 and minus 10.5 dB. That's within spec, but with little margin, and we're watching it.
  The gain across UWB is between about 2.9 and 4.9 dBi, typical for a monopole that radiates both ways.
  This is IEEE gain, which excludes port mismatch. **Inside the band, realized gain is at most 0.46 dB lower.**
  **This 3 to 5 dBi is the baseline the metasurface must beat.**"

**Slide 12: SRR metasurface and antenna + metasurface (Sanjana, 1:15)**
- *Points:*
  - SRR as an LC resonator: f₀ = 1/(2π√LC).
  - Unit cell with unit-cell boundaries and a Floquet port gives the reflection phase.
  - Target phase ≈ −40° to +105° over UWB.
  - Plan: antenna + metasurface versus PEC at 2 mm.
  - Status: [results pending / fill in].
- *Script (if no results):* "The metasurface is built from split-ring resonators. Each ring is a tiny LC circuit, and its resonance sets where the surface reflects in phase.
  We are characterising the unit cell with periodic boundaries and a Floquet port to get its reflection phase,
  and we will compare it with the target curve from slide 7, roughly minus 40 to plus 105 degrees.
  Then we will simulate the antenna with the metasurface, the antenna with a metal plate at the same 2 mm, and the antenna alone, with the same mesh and settings.
  **These metasurface results are still running, and we will present them at the end-semester evaluation.** One thing we already expect from theory:
  a single resonance cannot stay in phase over the whole 3.4-to-1 band, so we are also preparing a dual-resonance cell."
- *If results arrive:* replace the script with the real phase curve and the S₁₁ and gain comparison. Never estimate.

**Slide 13: Work done and challenges (Sanjana, 0:45)**
- *Points:*
  - *Done:* literature review, antenna design, Lg and R sweeps, optimised antenna (S₁₁ and gain), gap theory.
  - *Challenges:* sweep artefacts (we use only the final smooth run), 2 mm is in the near field, one resonance cannot cover UWB, simulation time.
- *Script:* "So far we've completed the review, the antenna design and optimisation, and the theory for the gap.
  Our challenges are the sweep artefacts we showed, the near-field coupling at such a small gap, and the bandwidth limit of a single SRR resonance."

**Slide 14: Future work and expected outcomes (Sanjana, 1:00)**
- *Points:*
  - Finish the unit cell, the antenna + metasurface, the PEC baseline, realized gain, patterns and F/B.
  - Phase II: 2/4-port MIMO (orthogonal elements), isolation > 15 dB, ECC < 0.01 target, DG, TARC, CCL, MEG.
  - Fabrication on FR-4, VNA and anechoic-chamber measurement.
  - Timeline: [fill in month by month].
- *Script:* "Next we finish the metasurface comparison. Then in Phase II we build the MIMO version, place the elements orthogonally for isolation,
  and evaluate isolation, ECC, diversity gain, TARC, channel capacity loss and MEG.
  Finally we fabricate on FR-4 and measure S-parameters on a VNA and patterns in an anechoic chamber. We expect [targets, not results]:
  full-UWB matching, isolation above 15 dB, and a gain improvement over at least part of the band compared with both no reflector and a metal plate. Back to Chanswarang."

**Slide 15: Conclusion and references (Chanswarang, 0:30)**
- *Points:* three take-aways plus a references list.
- *Script:* "To conclude: one, our CPW-fed decagonal monopole covers 2.16 to 15.73 GHz with 3 to 5 dBi gain. Two, theory shows a metal plate cannot work 2 mm behind it, but a metasurface with the right reflection phase can. Three, the metasurface and MIMO stages are next.
  Thank you. We're happy to take questions."

**Transitions (memorise these):**
- Chanswarang → Anushka: "I'll hand over to Anushka for the literature."
- Anushka → Nishit: "Nishit will now explain why 2 millimetres is hard."
- Nishit → Sanjana: "Sanjana will now show the optimised result."
- Sanjana → Chanswarang: "Back to Chanswarang."

**Backup slides (after slide 15; open only if asked):**
- **B1, sweep artefacts:** the plot with the jumps circled. "Above 0 dB is impossible, because |S₁₁| ≤ 1 for a passive antenna. Cause: broadband frequency-sweep interpolation. Final run is smooth. [Re-run result if done.]"
- **B2, phase table:** the full table from §3.4, including the PEC ray-factor column.
- **B3, full literature table:** §4.3.
- **B4, MIMO metrics:** ECC (S and far-field), DG, TARC, CCL and MEG formulas with targets (§1.8).
- *Optional:* **B5,** realized gain versus IEEE gain formula; **B6,** the f_L estimate with numbers.

---

## 6. Viva preparation: 135 questions with model answers

Answers are 2–5 sentences. Questions marked ★ are likely. Section K covers the tough ones, each with a safe fallback answer.

### A. EM and transmission-line basics

**A1★. What is the relation between frequency and wavelength?**
λ = c/f, so λ₀ (mm) ≈ 300/f (GHz). At 3.1 GHz λ₀ ≈ 96.7 mm and at 10.6 GHz ≈ 28.3 mm. In a dielectric the wavelength shrinks by √εᵣ (or √εeff on a printed line).

**A2. What is the free-space wave impedance?**
η₀ = √(μ₀/ε₀) ≈ 377 Ω, the ratio E/H of a plane wave in air. It is the reference against which we compare a metasurface's surface impedance.

**A3. What is the wavenumber?**
k = 2π/λ, in rad/m. It converts a distance into a phase: travelling d metres adds a phase of k·d. In our gap analysis the round trip adds 2k₀h.

**A4★. What is characteristic impedance?**
The ratio of voltage to current for a single travelling wave on a line, Z₀ = √(L′/C′) for a lossless line. It depends on geometry and materials, not length. Ours is designed for 50 Ω.

**A5. Why 50 Ω?**
It is a historical compromise for coax between minimum loss (≈ 77 Ω) and maximum power handling (≈ 30 Ω). All our instruments, cables and connectors are 50 Ω, so the antenna must match it.

**A6★. What is the reflection coefficient?**
Γ = (Z_L − Z₀)/(Z_L + Z₀), the ratio of the reflected to the incident voltage wave. |Γ| = 0 means a perfect match and |Γ| = 1 means total reflection. For a passive load |Γ| ≤ 1.

**A7. What does a transmission line do to an impedance?**
It transforms it: Z_in = Z₀(Z_L + jZ₀tan βl)/(Z₀ + jZ_L tan βl). A quarter-wave line inverts the impedance (Z_in = Z₀²/Z_L). That is why feed length and gaps change the match.

**A8. What is the difference between phase velocity and group velocity?**
Phase velocity is the speed of a single-frequency crest, ω/β. Group velocity, dω/dβ, is the speed of a pulse's envelope. For UWB pulses, a dispersive antenna or line (group velocity varying with frequency) distorts the pulse.

**A9. What is a TEM mode, and is a CPW TEM?**
In a TEM mode both E and H are purely transverse, as in coax. Microstrip and CPW are **quasi-TEM** because the fields sit partly in air and partly in the dielectric, so a small longitudinal component exists.

**A10. What is skin depth, and does it matter here?**
Current flows in a surface layer δ = 1/√(πfμσ), about 1 µm in copper at 5 GHz. The 35 µm copper is many skin depths thick, so it acts as a good conductor. Surface roughness adds a little loss.

**A11. What is dielectric loss tangent?**
tan δ = ε″/ε′, the ratio of lossy to stored response in the dielectric. Dielectric loss grows with frequency × tan δ. FR-4's tan δ ≈ 0.02 is high, so it costs efficiency at the upper UWB band.

**A12. What is a standing wave?**
The interference pattern of forward and reflected waves on a mismatched line. VSWR is the ratio of the maximum to the minimum voltage along the line.

### B. Matching and S-parameters

**B1★. What is S₁₁?**
The ratio of the reflected wave to the incident wave at port 1, with the other ports matched. For a single antenna it is its input reflection coefficient. We plot 20·log₁₀|S₁₁|.

**B2★. Why −10 dB?**
At −10 dB, 10 % of the power is reflected and 90 % accepted, with VSWR ≈ 1.92. It is the standard convention for impedance bandwidth (handsets often accept −6 dB).

**B3. What is return loss?**
RL = −20·log₁₀|Γ|, a positive number. "Return loss 10 dB" and "S₁₁ = −10 dB" are the same thing. Saying "return loss of −10 dB" is technically wrong.

**B4. What is VSWR, and its value at −10 dB?**
VSWR = (1 + |Γ|)/(1 − |Γ|). At −10 dB, |Γ| = 0.316, so VSWR ≈ 1.92.

**B5. What is mismatch loss?**
−10·log₁₀(1 − |Γ|²), the power lost by reflection: 0.46 dB at −10 dB and 1.26 dB at −6 dB. It is the difference between IEEE gain and realized gain.

**B6. What is S₂₁, and how does it relate to isolation?**
S₂₁ is the transmission from port 1 to port 2. In MIMO, isolation = −|S₂₁| (dB), so S₂₁ = −20 dB means 20 dB of isolation.

**B7. What does it mean if S₂₁ = S₁₂?**
The network is reciprocal, which holds for any antenna without ferrites or active parts. It lets us simulate fewer excitations.

**B8. How do you measure S₁₁?**
With a VNA (vector network analyser) calibrated with SOLT (short-open-load-thru) standards at the cable end. Connect the antenna via its SMA connector and read S₁₁ in dB over the band.

**B9. What is impedance matching, and how is it achieved in your antenna?**
Making the antenna's input impedance close to 50 Ω over the band. In our antenna it is achieved by the CPW feed width and slot width (a 50 Ω line), the ground-to-patch gap (Lg, giving p = 0.73 mm), and the disc size (R).

**B10. What is a Smith chart used for here?**
It plots the complex Γ (or impedance) against frequency. A wideband antenna's locus circles tightly inside the VSWR = 2 circle. It shows *why* a frequency is mismatched (too capacitive or too inductive), which tells you which dimension to change.

### C. Antenna parameters

**C1★. Define directivity.**
D = 4πU_max/P_rad, how concentrated the radiation is compared with an isotropic radiator. It ignores losses. Quoted in dBi.

**C2★. Define gain. IEEE versus realized?**
IEEE gain G = e_rad·D includes ohmic and dielectric loss but not mismatch. Realized gain G_R = (1 − |S₁₁|²)·G also includes mismatch. CST's "Gain" is IEEE; "Realized Gain" is a separate option.

**C3★. What is your gain?**
IEEE gain ≈ 2.9–4.9 dBi across 3.1–10.6 GHz (lowest near 6.3 GHz, highest near 8.5 GHz), with a peak ≈ 5.1 dBi near 13.5 GHz. These values are read from the CST plot to ±0.1 dB. Realized gain inside the band is at most 0.46 dB lower.

**C4. What is radiation efficiency?**
e_rad = P_rad/P_accepted. Losses in copper and FR-4 reduce it. Total efficiency also multiplies by (1 − |S₁₁|²). Ours is [fill in from CST].

**C5★. What is a radiation pattern? E-plane and H-plane?**
The angular distribution of radiated power in the far field. The E-plane contains the E-vector and the direction of maximum radiation; the H-plane contains the H-vector and the direction of maximum radiation. For a monopole at low frequency the H-plane is near-omnidirectional and the E-plane is a figure-8.

**C6. What polarization is your antenna?**
Linear, along the feed axis, because the dominant currents flow along that axis. At higher frequencies the cross-polarization rises as current paths diversify.

**C7. What is axial ratio?**
The ratio of the major to the minor axis of the polarization ellipse. AR = 0 dB is perfect CP. AR ≤ 3 dB counts as circular. A linear antenna has a very large AR.

**C8. What is front-to-back ratio, and what should a reflector do to it?**
F/B = U_front/U_back in dB. A bare monopole has F/B ≈ 0 dB. A good reflector should raise it substantially, and it is a direct measure of whether the reflector works.

**C9★. What are the near-field and far-field regions?**
- Reactive near field: within ≈ λ/2π for a small antenna. Energy is stored there.
- Radiating near field: out to 2D²/λ.
- Far field: beyond 2D²/λ, where the pattern no longer depends on distance.

Our metasurface at 2 mm is inside λ/2π for all frequencies below ≈ 23.9 GHz.

**C10. What is bandwidth? Fractional bandwidth?**
The frequency range over which a specification holds (here |S₁₁| ≤ −10 dB). FBW = 2(f_H − f_L)/(f_H + f_L). Ours is 151.7 % (2.1615–15.734 GHz). UWB itself is 109.5 %.

**C11. What is HPBW?**
Half-power beamwidth: the angle between the −3 dB points of the main lobe. A reflector narrows it on the front side.

**C12. What is EIRP?**
Effective isotropic radiated power: P_t·G_t. The FCC UWB limit of −41.3 dBm/MHz is on EIRP.

**C13. Why does gain vary with frequency in your plot?**
The electrical size grows with frequency, so the pattern becomes more directive and gain rises. Near mode transitions (≈ 6.3 GHz) the pattern changes shape and gain dips. Losses in FR-4 also grow with frequency.

**C14. Why is gain only ≈ 1 dBi at 2 GHz?**
2 GHz is below our −10 dB band, and the antenna is electrically small there, with a dipole-like pattern (≈ 2 dBi directivity) plus some loss. Realized gain there would be lower still because of mismatch.

### D. CPW, UWB and monopoles

**D1★. Why CPW and not microstrip?**
CPW is uniplanar: signal and grounds on one side, a single etching step, no vias. The coplanar ground acts as part of the monopole and is easy to tune (Lg). The back side is free for a reflector.

**D2. How is the 50 Ω CPW designed?**
Z₀ = (30π/√εeff)·K(k′)/K(k) with k = W/(W + 2G) and εeff ≈ (εᵣ + 1)/2. We chose W = 3 mm and G = 0.5 mm, then confirm the value in CST from the port's line impedance. The textbook formula gives ≈ 55–58 Ω for these values *(computed)*, so quote CST's number, not "exactly 50".

**D3. What is the odd (slotline) mode in CPW?**
A mode where the two grounds are at different potentials. It is excited by asymmetry. It is suppressed by keeping the structure symmetric, or with air bridges or vias in circuits.

**D4★. What are the FCC UWB rules?**
3.1–10.6 GHz, unlicensed, EIRP spectral density ≤ −41.3 dBm/MHz. A UWB signal has a −10 dB bandwidth ≥ 500 MHz or a fractional bandwidth ≥ 20 %.

**D5. What are UWB applications?**
Precise indoor positioning and ranging (phones, tags), short-range high-rate links, radar and through-wall imaging, ground-penetrating radar, medical imaging, and WBAN sensors.

**D6★. If FCC caps EIRP, why increase gain?**
The cap is on EIRP, so transmit gain does not raise the allowed radiated power. Higher gain still improves the **receive** side, lets the transmitter reach the limit with less amplifier power, and directs energy away from the body or the device behind. Imaging and radar also benefit from directivity.

**D7★. Why is a UWB antenna hard to design?**
It must stay matched over 3.4 : 1, keep a stable pattern and gain while its electrical size triples, and keep the group delay flat so pulses are not distorted, all while staying compact. In MIMO, isolation must hold over the whole band.

**D8★. How does a planar monopole achieve wide bandwidth?**
The wide, smooth element supports many closely spaced current modes, so the resonances overlap and the match never drops out. Ours shows dips at 2.73, 4.78, 9.23 and 14.32 GHz.

**D9★. Estimate your lowest frequency from theory.**
f_L ≈ 7.2/(L + r + p) GHz with L = 2R = 3 cm and r = R/4 = 0.375 cm. That gives ≈ 2.1 GHz for a small gap p, and CST gives 2.16 GHz. The formula is an empirical free-space estimate, so it confirms the order of magnitude, not a precise value.

**D10. What is the role of the ground plane?**
It is the other arm of the antenna (an asymmetric dipole). Its edge currents radiate, and the ground-to-patch gap controls the match. Changing Lg moved our first resonance from ≈ 1.6 to ≈ 2.7 GHz.

**D11. Why a decagon (nearly a disc) rather than a rectangle?**
A 10-sided patch behaves almost like a disc. Its curvature gives a gradually varying gap to the ground, so the impedance changes smoothly with frequency and more modes overlap. The result is a wider band than a sharp-cornered rectangle.

**D12. What is pulse fidelity / group delay?**
How well the received pulse keeps the shape of the transmitted one. A flat group delay (variation under ≈ 1 ns) means little distortion. We have not evaluated it yet; it can be done in CST with probes.

### E. Our design and results

**E1★. Describe your antenna in 30 seconds.**
A regular decagonal patch of circumradius 15 mm, fed by a coplanar waveguide (3 mm strip, 0.5 mm slots) on a 50 × 50 mm, 1.6 mm FR-4 board, with the CPW grounds on the same side and their edge at Lg = −7 mm, a 0.73 mm gap from the patch. It is matched from 2.16 to 15.73 GHz (151.7 % FBW) with 2.9–4.9 dBi IEEE gain over UWB. An SRR metasurface 2 mm behind it is the next step.

**E2★. What is Lg, physically?**
The coordinate of the CPW grounds' edge along the feed axis (x in the CST model). It sets how close the ground comes to the patch, which sets the exposed feed length and the coupling gap: p = 0.73 mm at Lg = −7 mm.

**E3★. Why did moving the ground edge up raise the first resonance?**
A long exposed feed radiates as part of the monopole and makes it electrically longer, so the resonance is lower (≈ 1.6 GHz). Moving the ground up shortens it, which raises the resonance (≈ 2.7 GHz). The smaller gap also smooths the impedance transition, so the match improves.

**E4★. What does R do?**
The radius sets the radiator size, so it sets the lower band edge (L = 2R) and the number of overlapping modes. A larger R gives a lower f_L and a fuller band. R = 15 mm gave the widest continuous −10 dB band.

**E5. Why sweep Lg before R?**
The ground edge sets the feed transition, which controls the match everywhere. With R at its expected large value (15 mm), we fixed the feed first, then refined the radius. One-at-a-time sweeps are simple but can miss interactions, so a joint optimisation is possible later.

**E6★. What does "best" mean?**
The curve whose −10 dB region covers all of 3.1–10.6 GHz as one continuous band, with the widest band and the deepest worst-case in-band S₁₁. We judged it by looking at the band edges and the worst in-band point.

**E7★. Read out your final band and resonances.**
|S₁₁| ≤ −10 dB from 2.1615 to 15.734 GHz. Dips at 2.7275 GHz (−32.65 dB), 4.7824 GHz (−21.18 dB), 9.2265 GHz (−22.56 dB) and 14.32 GHz (−27.07 dB).

**E8★. Where is your antenna weakest?**
Near 6.5 GHz (≈ −10.3 dB) and 12.2 GHz (≈ −10.5 dB), the valleys between resonances. They are within spec but with only ≈ 0.3–0.5 dB of margin, so fabrication tolerance or the metasurface could push them over. We will watch them after adding the metasurface.

**E9. Why does the band extend to 15.7 GHz if you only need 10.6?**
A disc-like monopole is naturally very wideband. The extra range is margin and is not a design goal. We do not claim operation above 10.6 GHz, because the pattern degrades there.

**E10. How does your FBW compare to UWB's requirement?**
UWB needs 109.5 % (3.1–10.6 GHz). We have 151.7 %, with ≈ 0.94 GHz of margin below 3.1 GHz and ≈ 5.1 GHz above 10.6 GHz.

**E11★. Is about 5 dBi good?**
For a bidirectional planar monopole, yes: 2–5 dBi is typical. It is low compared with the 8–11 dBi reflector-backed designs in the literature, which is exactly the motivation for adding the metasurface.

**E12. Why is the gain lowest near 6.3 GHz?**
That is where one current mode hands over to the next, coinciding with the weak match at 6.5 GHz. The pattern likely changes shape there. We would confirm by plotting the pattern and surface current at 6.3 GHz.

**E13. What substrate did you use and why?**
FR-4 (lossy), 1.6 mm, with εᵣ = 4.3 and tan δ = 0.025 (CST library). It is cheap, available in the institute lab, and standard in the literature, so comparisons are fair. Its loss (tan δ ≈ 0.02) reduces efficiency at higher frequencies.

**E14. Board size?**
50 × 50 mm. With R = 15 mm the patch top is only 2.7 mm from the board edge, and the gap to the ground is 0.73 mm. That is why the optima sit at the sweep edges.

**E15. What is the overall profile with the metasurface?**
1.6 mm antenna substrate + 2 mm air gap + 1.6 mm metasurface substrate, giving ≈ 5.2 mm in total, plus copper. That is 0.021 λ for the gap alone at 3.1 GHz.

**E16★. Why 2 mm specifically?**
Answer honestly: [fill in the real reason: guide's suggestion, available spacer, or a target profile]. Theory: at 2 mm the required reflection phase is small and positive (15° at 3.1 GHz to 51° at 10.6 GHz), which a metasurface can plausibly provide and a metal plate cannot. It keeps the profile low. A sweep of h is planned to see the trade-off.

**E17. Did you look at surface currents?**
[fill in]. If not: "Not yet. We plan to plot them at the resonances to confirm the mode picture, for example strong ground-edge current at the first resonance."

**E18. What changes will the metasurface cause to S₁₁?**
At 0.021 λ it will load the antenna in the near field and shift the resonances, so the weak points may break. We will re-tune Lg (and p) with the metasurface in place.

### F. CST and simulation

**F1★. Which solver did you use, and why?**
The frequency-domain solver in CST Studio Suite 2019, 0–18 GHz. It handles curved geometry well with tetrahedral meshing and adaptive refinement, and the unit-cell/Floquet simulation for the metasurface also uses it, so we kept the same solver for consistency. The time-domain solver is also a valid and often faster choice for broadband antennas.

**F2★. Time-domain versus frequency-domain?**
TD (FIT, hexahedral mesh) excites a broadband pulse and gives the whole band in one run, which suits low-Q broadband antennas. FD (FEM) solves at frequency samples and interpolates; it is better for resonant or high-Q, small or curved structures and periodic unit cells. For a UWB monopole both should agree. Cross-checking with TD is good practice.

**F3★. What is a waveguide port, and why use it?**
A 2D port that solves the eigenmode of the feed's cross-section, so the excitation has the correct field shape and line impedance. It must cover the strip, both slots and part of the grounds, and extend several substrate thicknesses above and below.

**F4. Waveguide port versus discrete port?**
A discrete port is a lumped source between two points, with an internal impedance. It is simple but adds a lumped gap and is less accurate for printed line feeds. A waveguide port models the line itself.

**F5★. What boundaries did you use?**
Open (add space) on all sides: an absorbing (PML-type) boundary with extra air, so waves leave without reflecting and the far field can be computed.

**F6★. What are unit-cell boundaries and Floquet ports?**
Unit-cell boundaries make one cell behave like an infinite periodic array (periodic with a phase shift). Floquet ports excite plane-wave modes (TE₀₀/TM₀₀ at normal incidence) and give the reflection and transmission of the surface. We read the phase of S(Zmax,Zmax), de-embedded to the cell surface.

**F7★. What is mesh convergence, and did you check it?**
A result is converged when refining the mesh changes it by less than a tolerance. In FD, CST's adaptive mesh refinement repeats passes until ΔS falls below a threshold. Ours: [fill in from the solver log]. See K4 for the fallback.

**F8. How does a parameter sweep work in CST?**
You define parameters (Lg, R), add sequences with start/stop/steps under Simulation → Parameter Sweep, and CST runs each combination, storing all results so they can be overlaid in 1D results.

**F9. How did you get gain versus frequency?**
Far-field monitors at several frequencies, then the maximum gain at each frequency plotted as a 1D curve. The curve is only as dense as the monitor set: [fill in which frequencies].

**F10. How do you get realized gain in CST?**
Choose "Realized Gain" in the far-field plot properties, or use template-based post-processing (Farfield and Antenna Properties → Realized Gain, maximum value) over all monitors. Or compute G_R = (1 − |S₁₁|²)·G from the IEEE gain.

**F11. Why simulate up to 18 GHz?**
To see the full upper band edge (15.73 GHz) and the margin beyond UWB, and to check that nothing odd happens near the band. The cost is a finer mesh.

**F12. How long did a run take, and what limited you?**
[fill in]. The sweeps took longest because each of the 10 (Lg) and 13 (R) values is a full broadband run. That is one reason we did one-at-a-time sweeps.

### G. Metasurface, SRR, AMC and reflectors

**G1★. What is a metasurface?**
A thin, usually single-layer, periodic array of sub-wavelength elements. It controls the amplitude, phase or polarization of reflected or transmitted waves. It is described by surface impedance or reflection phase rather than bulk ε and μ.

**G2★. Metamaterial versus metasurface versus FSS versus AMC versus EBG?**
- Metamaterial: 3D bulk with effective ε and μ.
- Metasurface: its 2D version.
- FSS: a periodic spatial filter.
- AMC: a surface with 0° reflection phase at resonance, usually ground-backed.
- EBG: blocks surface waves in a band.

The Sievenpiper mushroom is both an AMC and an EBG.

**G3★. What is an SRR, and what is its resonant frequency?**
A ring with a split. The ring is an inductor and the split a capacitor, so it is an LC resonator with f₀ = 1/(2π√LC). A bigger ring or a narrower split lowers f₀.

**G4. Where does the SRR's "magnetic" behaviour come from?**
When H passes through the ring, it induces a circulating current, which creates a magnetic dipole, giving μeff < 0 just above f₀ (Pendry 1999). In our planar geometry at normal incidence, H lies in the ring plane, so the ring is mainly driven electrically across the split. What matters for us is the reflection phase.

**G5★. What is reflection phase, and why does it matter?**
The phase of the reflected wave relative to the incident wave at the surface. It decides whether the wave reflected backwards adds to or cancels the forward wave. We need φ_R ≈ 2k₀h.

**G6★. What is the in-phase condition?**
φ_R − 2k₀h = 2nπ: the reflector phase minus the round-trip phase must be a multiple of 360°. At h = 2 mm, 2k₀h = 15° at 3.1 GHz and 51° at 10.6 GHz.

**G7★. Why does a metal plate need λ/4?**
A PEC reflects with 180°. The extra 180° from a λ/2 round trip (2 × λ/4) brings the wave back in phase. At 3.1 GHz that is 24.2 mm.

**G8★. What happens with a metal plate at 2 mm?**
It is 165° out of phase at 3.1 GHz, so in the ray model it cancels about three-quarters of the forward field (−11.7 dB). It breaks even only near 12.5 GHz and never gets within ±90° in our simulated band (only above ≈ 18.7 GHz). In the near field its opposite image current also shorts out the antenna's radiation resistance.

**G9★. Why is your metasurface ground-backed?**
A ground-backed SRR (an AMC) reflects almost totally, with a phase sweeping +180° → 0° → −180°, so it can give the small positive phase we need over part of the band. A bare SRR sheet reflects partially, with a phase between 90° and 270° (≈ 180° at resonance, like metal), so in the low band it can be in the window only where its reflection is weak. That is why ours has a full copper ground on the back.

**G10. What is the ±90° bandwidth?**
The frequency range where the reflection phase lies within ±90° of the target, so the reflected wave adds at least +3 dB to the direct wave (equal amplitudes). For a classical AMC the target is 0°; for us it is 2k₀h.

**G11★. Why can one SRR not cover a 7 : 1 band?**
Foster's theorem: a passive lossless surface's reflection phase *falls* with frequency, while the needed phase 2k₀h *rises*. A single resonance's ±90° band is only about k₀t ≈ 20 % for 1.6 mm FR-4 at 6 GHz. We would need the phase to stay between ≈ −40° and +105° over a 109 % band.

**G12★. How can you widen it?**
Dual-resonant cells (two rings, or ring + patch) that create a phase plateau; varying split angles across the array (Sen 2017); multiple layers; a thicker or lower-loss spacer substrate. Or accept a sub-band, or increase h.

**G13. How many cells do you need?**
Enough to cover at least the antenna footprint, and ideally to extend past it, because edge cells behave differently from an infinite array. Ours is 6 × 5 cells. Hasan used 10 × 10, Al-Gburi 19 × 19, Hussain 5 × 5.

**G14. Does a finite array behave like the unit-cell simulation?**
Only approximately. The unit cell assumes an infinite array and plane-wave incidence, but the antenna's near field is not a plane wave and the edges diffract. That is why the full antenna + metasurface simulation is the real test.

**G15. Does the metasurface affect polarization?**
An SRR is anisotropic, so its response depends on whether E lies along the split side. We align it with the monopole's linear polarization. Wu 2023 deliberately used a metasurface to convert to circular polarization.

### H. MIMO

**H1★. Why MIMO?**
Several antennas exploit multipath to carry parallel streams (spatial multiplexing) and to combat fading (diversity). Capacity grows roughly linearly with min(N_t, N_r).

**H2. Write the MIMO capacity formula.**
C = B·log₂ det(I + (SNR/N_t)·H·Hᴴ), where H is the channel matrix. With uncorrelated antennas, H has full rank and capacity scales with the number of antennas.

**H3★. What is mutual coupling, and why is it bad?**
Energy radiated or conducted from one element into another, through space, surface waves and shared ground currents. It lowers efficiency, correlates the patterns and detunes the match.

**H4★. How will you get isolation?**
Orthogonal placement of the elements (polarization and pattern diversity), spacing, and if needed a decoupling structure: a ground stub, slot or cross, a neutralization line, or an EBG/metasurface. The metasurface itself may change coupling and must be checked. Target > 15 dB, aim for 20 dB.

**H5★. Define ECC. How is it computed? Target?**
The correlation between the signal envelopes of two antennas. From S-parameters: |S₁₁*S₁₂ + S₂₁*S₂₂|² / [(1 − |S₁₁|² − |S₂₁|²)(1 − |S₂₂|² − |S₁₂|²)], valid for lossless antennas. From far-field patterns: the normalised overlap integral of the complex patterns. Target < 0.5; good designs reach < 0.01.

**H6★. Why compute ECC from far fields too?**
The S-parameter formula assumes 100 % radiation efficiency and an isotropic environment. On lossy FR-4 it underestimates ECC. The far-field method uses the actual patterns.

**H7★. Define diversity gain.**
The SNR improvement from diversity combining compared with one antenna: DG = 10√(1 − ECC²) dB (some use 10√(1 − ECC)). Ideal is 10 dB. Target > 9.9 dB.

**H8★. Define TARC.**
Total active reflection coefficient: the ratio of total reflected to total incident power when all ports are driven with random phases. For 2 ports: √(|S₁₁ + S₁₂e^{jθ}|² + |S₂₁ + S₂₂e^{jθ}|²)/√2. Target < −10 dB.

**H9★. Define CCL.**
Channel capacity loss from correlation: C_loss = −log₂ det(Ψ_R), where ρᵢᵢ = 1 − |Sᵢᵢ|² − |Sᵢⱼ|² and ρᵢⱼ = −(Sᵢᵢ*Sᵢⱼ + Sⱼᵢ*Sⱼⱼ). Target < 0.4 bit/s/Hz.

**H10★. Define MEG.**
Mean effective gain: the average received power in a multipath environment relative to an isotropic antenna. For an isotropic environment, MEGᵢ ≈ 0.5(1 − Σⱼ|Sᵢⱼ|²). Target ≈ −3 dB, and |MEG₁ − MEG₂| < 3 dB for balanced branches.

**H11. Why should the grounds be connected in MIMO?**
Real devices have one common ground. Separate grounds give unrealistically good isolation. Connecting them makes the design practical, but it adds coupling through ground currents, which we then have to suppress.

**H12. 2-port or 4-port, and why orthogonal?**
Phase II starts at 2 ports and extends to 4. Orthogonal placement, each element rotated 90°, gives polarization and pattern diversity and lower coupling at no extra area cost.

### I. Literature and novelty

**I1★. What is your closest prior work?**
Hasan 2022: a 4-port antenna with a copper-backed 10 × 10 square-enclosed circular-SRR metasurface at 12 mm, ≈ 3.1–7.7 GHz, realized gain 5.4 → 8.3 dBi, isolation > 15.5 dB, ECC < 0.004.

**I2★. What exactly is novel compared with Hasan 2022 and Al-Gburi 2022?**
Compared with Hasan: we target full UWB (3.1–10.6 GHz rather than ≈ 3.1–7.7), at a gap six times smaller (2 mm versus 12 mm), with a metal-plate baseline at the same gap.
Compared with Al-Gburi: they have a single antenna with a ground-backed FSS and a 10 mm profile; we use an SRR reflector at a 2 mm gap and go on to MIMO.
The novelty is the combination, and it is a target until our metasurface results are in.

**I3. Has anyone done UWB MIMO with a reflector?**
Yes, outside our core review: for example Mohanty & Sahu 2022 (4-port, 2.08–10.4 GHz, metal reflector at ≈ 10 mm) and recent AMC/FSS UWB MIMO papers. That is why we claim the specific combination (SRR, 0.021 λ gap, PEC baseline), not "first".

**I4. Why did you pick these ten papers?**
They span single-antenna reflectors (to learn gain-enhancement methods and gaps) and MIMO with metasurfaces (to learn isolation and diversity methods), focused on recent IEEE, Elsevier and MDPI work. [Add your search keywords and databases.]

**I5. Did you read all of them fully?**
No. Two were read in full and eight from abstracts and publisher pages, so some details (gaps, gains) may need checking against the full text before the final report.

**I6. Sen 2017's trick?**
A split-ring metasurface reflector behind a UWB circular monopole, ≈ +5.5 dB gain. Varying the split angles across the cells broadens the response, which is one of our widening options.

### J. Fabrication and measurement

**J1★. How will you fabricate?**
Etch or mill the antenna on 1.6 mm FR-4 (photolithography or a PCB milling machine) and mount an SMA end-launch connector on the CPW. Fabricate the metasurface board the same way and hold it at 2 mm with non-metallic (nylon or Teflon) spacers or foam.

**J2★. How will you measure?**
S-parameters on a calibrated VNA (SOLT). Patterns and gain in an anechoic chamber using the gain-comparison (substitution) method with a standard horn: G_AUT = G_ref + (P_AUT − P_ref) in dB.

**J3★. Why FR-4, and what are its losses?**
It is cheap, widely available and standard. But εᵣ varies (≈ 4.2–4.7) between batches and with frequency, and tan δ ≈ 0.02 gives dielectric loss that grows with frequency, reducing efficiency in the upper UWB band. Rogers boards (tan δ ≈ 0.001–0.004) are better but expensive.

**J4. What differences do you expect between simulation and measurement?**
Frequency shifts from εᵣ tolerance, fabrication tolerance (± tens of µm on slots), connector and solder effects, cable radiation at low frequency, and air-gap tolerance. Most of all, our weak 6.5 and 12.2 GHz points could cross −10 dB.

**J5. How will you hold a 2 mm air gap accurately?**
With precision nylon spacers at the corners, outside the radiating region, or a low-εᵣ foam layer (εᵣ ≈ 1.05). We would simulate the spacers if they are close to the antenna.

**J6. Far-field distance for measurement?**
r > 2D²/λ at the highest frequency, with D the largest antenna dimension, plus r ≫ λ. Our D = [fill in], so [compute] metres at 10.6 GHz.

**J7. Would the cable affect measurements?**
Yes. For small CPW antennas the cable shield carries current and radiates, especially at low frequency. Use ferrite chokes or a balun, and route the cable behind the antenna.

**J8. How do you measure ECC?**
From measured S-parameters (with the lossless caveat), or better from measured complex 3D patterns of each port in the chamber.

### K. Tough questions, with model answers and safe fallbacks

**K1★. Why does one sweep curve go above 0 dB?**
- *Answer:* "It can't physically. For a passive antenna |S₁₁| ≤ 1, so 0 dB is the ceiling. The frequency-domain solver's broadband sweep interpolates between a limited number of frequency samples. For that parameter value the interpolation did not converge properly, giving a non-physical overshoot. The jumps at the same frequencies, ≈ 4.0 and 6.2 GHz, in several curves point to the sweep or the port's mode set rather than to the antenna. The final optimised run is smooth, and only that run is used for our numbers."
- *Fallback:* "That point is non-physical, so we've excluded it. We are re-running that case with more frequency samples and the time-domain solver to confirm, and it does not affect our chosen design."

**K2★. Why is your optimum at the edge of the sweep?**
- *Answer:* "Both parameters are constrained by the board: R = 15 mm leaves only 2.7 mm to the board edge, and Lg = −7 mm leaves only a 0.73 mm gap to the patch. So these are the best values within the constraint, not unconstrained optima. Going further would mean a bigger board."
- *Fallback:* "You're right that the true optimum may lie beyond. We chose to keep the board size fixed. A joint optimisation over Lg and R, and a sweep slightly past the edge if the geometry allows, is on our list."

**K3★. Why the frequency-domain solver for UWB? Would time-domain be better?**
- *Answer:* "Time-domain is usually the default for broadband antennas, because one pulse gives the whole band, and it would be a valid choice here. We used the frequency-domain solver because it meshes the many-sided curved patch well with tetrahedra, it has adaptive mesh refinement, and our metasurface unit-cell simulation with Floquet ports also uses it, so the whole project stays on one solver. The downside is the broadband-sweep artefacts you've seen."
- *Fallback:* "Cross-validating the final design with the time-domain solver is the right check, and we'll include it. If the two agree, the solver choice doesn't matter."

**K4★. Did you check mesh convergence?**
- *Answer if yes:* "Yes. Adaptive mesh refinement ran [n] passes and converged to ΔS < [x]. [Optionally:] we also compared the final S₁₁ at a finer mesh, and it changed by less than [y] dB in band."
- *Fallback if not:* "The frequency-domain solver's adaptive mesh refinement provides the basic check. We haven't yet done a separate refinement study on the final design. We'll do it before the metasurface runs, because the 2 mm gap needs a fine mesh in the gap."

**K5★. Why 2 mm? What if you used a metal plate?**
- *Answer:* "We want a low profile, and 2 mm is only 0.021 λ at 3.1 GHz. At that gap the round trip adds only 15° at 3.1 GHz and 51° at 10.6 GHz. A metal plate adds 180°, so it's 165° out of phase at 3.1 GHz, about −11.7 dB in the ray model, and it never gets within ±90° in our band (only above ≈ 18.7 GHz). In the near field it also shorts out the antenna. So a plate fails at this gap, and that's why the metasurface's reflection phase matters. A plate would need ≈ 24 mm for 3.1 GHz, or ≈ 12 mm to cover most of UWB."
- *Fallback:* "We're simulating the metal plate at the same 2 mm as a baseline, so the comparison will be shown, not just argued. [Real reason for 2 mm: fill in.]"

**K6★. How do you know the SRR reflects in phase?**
- *Answer:* "We simulate one cell with unit-cell boundaries and a Floquet port, and read the phase of S(Zmax,Zmax) de-embedded to the surface. Then we check it against the required band, φ_R between ≈ −40° and +105° over UWB. As sanity checks: removing the rings should give ≈ 180° (a bare ground), and the cell's phase should cross 0° near its resonance."
- *Fallback:* "We don't know yet. That simulation is in progress, and until it's done our gap analysis says what the SRR must do, not what it does."

**K7★. Will the metasurface spoil your bandwidth?**
- *Answer:* "It might. At 0.021 λ it loads the antenna in the near field, and our weak points at 6.5 and 12.2 GHz have only about 0.3–0.5 dB of margin. Our plan is to simulate with the metasurface in place, re-tune Lg and the gap if needed, and report both S₁₁ and realized gain. Some papers, such as Hussain 2023, saw the band widen, so it can go either way."
- *Fallback:* "If the full UWB band can't be kept at 2 mm, we'll report the trade-off: either increase the gap, or report the band that is kept and the gain gained."

**K8★. Is ≈ 5 dBi good? IEEE versus realized?**
- *Answer:* "For a bidirectional monopole, 2.9–4.9 dBi across UWB is typical, not high. Reflector-backed antennas in our review reach 8–11 dBi, which is our motivation. Our numbers are CST 'Gain', which is IEEE gain and excludes port mismatch. Realized gain = (1 − |S₁₁|²)·G, so inside the −10 dB band it is at most 0.46 dB lower."
- *Fallback:* "We'll add the realized-gain curve directly from CST in the next version, but the bound already tells us it is within half a dB in band."

**K9★. What exactly is novel compared with Hasan 2022 and Al-Gburi 2022?**
- See I2.
- *Fallback:* "Honestly, the individual pieces exist. Our contribution is combining them at a much smaller gap, over full UWB, with a fair metal-plate comparison. Whether it works is what Phase I is testing."

**K10★. How will you get isolation in MIMO? Define ECC, DG, TARC, CCL and MEG, and give targets.**
- *Answer:* "Orthogonal placement for polarization and pattern diversity, plus a decoupling structure on the common ground if needed. We then check that the metasurface doesn't add coupling. Targets:
  - isolation > 15 dB (aim 20);
  - ECC < 0.01 (spec < 0.5), computed from both S-parameters and far fields;
  - DG = 10√(1 − ECC²) > 9.9 dB;
  - TARC < −10 dB;
  - CCL < 0.4 bit/s/Hz;
  - MEG ≈ −3 dB, with port-to-port difference < 3 dB."
  (Definitions: H5–H10.)
- *Fallback:* "Those targets are from the literature. Phase II will tell us which decoupling method is needed."

**K11★. How will you fabricate and measure? Why FR-4, and what are its losses?**
- See J1–J3.
- *Fallback:* "FR-4 was chosen for cost and availability. Its tan δ ≈ 0.02 loss will show up as lower efficiency at the top of the band, and we'll report realized gain so the loss is included."

**K12★. What if the metasurface does not improve the gain?**
- *Answer:* "Then we'll report that, with the reason. Our phase analysis and the metal-plate baseline will tell us whether the phase was wrong, the near-field loading dominated, or the band was too wide for one resonance. Then we fix it: a dual-resonant or graded cell, a thicker spacer, or a larger gap, and we report gain against gap. A justified negative result with a fair baseline is still a valid result."
- *Fallback:* "Theory already predicts the improvement will be partial over UWB, not uniform. So our success criterion is a clear gain increase over part of the band without losing the match, compared with both no reflector and a metal plate."

**K13. Your f_L formula gives 2.18 GHz against 2.16 GHz simulated. Isn't the agreement suspicious?**
"It's an empirical estimate for a monopole over a large ground in air. Printed versions often need a substrate correction, which would lower it. The agreement within a few percent is partly luck. We use it only to show the order of magnitude is right."

**K14. Doesn't the R sweep also change the feed gap?**
"Yes. The patch is centred at x = 8 mm, so increasing R moves its lower edge towards the ground. The gap went from about 11.2 mm at R = 4 mm to 0.73 mm at R = 15 mm. So the R sweep is partly a gap sweep, and that coupling is one reason a joint optimisation would be better."

**K15. Is 0.021 λ in the far field of the metasurface? Can you use reflection phase at all?**
"No. It's in the reactive near field, because λ/2π > 2 mm below ≈ 23.9 GHz. The plane-wave reflection phase is a design guide, which is standard practice in AMC papers. The full-wave simulation of the antenna and metasurface is the real answer."

**K16. Your ±90° rule: where does it come from?**
"Two equal waves within ±90° add to at least √2 times one wave, which is +3 dB. They still exceed one wave up to ±120°. So ±90° is a convention for 'clearly constructive'."

---

## 7. Honest answers for weak spots: how to say it without sounding unprepared

The formula: **state the fact → give the reason → say what you are doing about it → move on.**
Never apologise twice, never guess a number, and never let an examiner discover a weakness you already knew about.

- **Metasurface results are pending.**
  > "The metasurface stage is in progress. What we can show today is the theory that sets its target, which is a reflection phase of roughly −40° to +105° across UWB at our 2 mm gap. We've also defined the fair test: antenna alone versus a metal plate versus the metasurface, all at the same gap and mesh. We'll present those results at the end-semester evaluation. We didn't want to show partial numbers before they're verified."
- **Gain was read from a plot.**
  > "The gain values are read from the CST gain-versus-frequency plot, so they're accurate to about ±0.1 dB. They're IEEE gain. We'll export the data and the realized-gain curve directly for the final report."
- **Sweep artefacts exist.**
  > "Yes, a few sweep curves have numerical artefacts: jumps near 4 and 6.2 GHz, and one value above 0 dB, which is physically impossible for a passive antenna. They come from the broadband frequency-sweep interpolation for those parameter values. We didn't use those curves for any number. The final optimised run is smooth, and [we have re-run the case / we are re-running it to confirm]."
- **Some literature values come from abstracts.**
  > "Two of the ten papers were studied in full. For the other eight we used the abstracts and publisher pages, so values like gap or gain should be read as reported headline figures. We'll verify them against the full texts through the library for the final report."
- **Optimum at the sweep edge.** "Best within the board constraint", see K2.
- **No mesh-convergence study yet (if true).** See K4's fallback.
- **Don't know the answer at all.**
  > "I'm not certain. I'd check it by [specific CST step or reference] rather than guess."

  Examiners respect this far more than a confident wrong answer. One teammate can add something if they genuinely know.

---

## 8. One-page cheat sheet

**Project numbers (simulated, CST 2019, frequency-domain solver, 0–18 GHz, waveguide port, open boundaries)**

| Item | Value |
|---|---|
| Antenna | CPW-fed regular decagon, R = 15 mm, on 50 × 50 mm FR-4 (εᵣ 4.3, tan δ 0.025, 1.6 mm); feed 3 mm, slots 0.5 mm; p = 0.73 mm |
| Metasurface | 6 × 5 double-split-ring cells on 1.6 mm FR-4, full copper ground, 2 mm air gap; total profile ≈ 5.2 mm |
| Optimised parameters | R = 15 mm, Lg = −7 mm |
| Lg sweep | 10 values from −20 to −7 mm (R = 15); first resonance ≈ 1.6 → 2.7 GHz |
| R sweep | 13 values from 4 to 15 mm (Lg = −7) |
| −10 dB band | **2.1615–15.734 GHz**, FBW **151.7 %** (7.28 : 1); covers 3.1–10.6 GHz |
| Resonances | 2.7275 (−32.65), 4.7824 (−21.18), 9.2265 (−22.56), 14.32 (−27.07) GHz (dB) |
| Weak points | ≈ 6.5 GHz (−10.3 dB), ≈ 12.2 GHz (−10.5 dB) |
| IEEE gain | ≈ 1 dBi at 2 GHz; 3.3 dBi near 3.6 GHz; **2.9–4.9 dBi over UWB** (min near 6.3, max near 8.5 GHz); peak ≈ 5.1 dBi near 13.5 GHz (±0.1 dB, read from plot) |
| Realized gain bound | G_R ≥ G − 0.46 dB inside the −10 dB band |
| Gap | h = 2 mm = 0.021 λ at 3.1 GHz |
| 2k₀h | 10° (2.16), 15° (3.1), 33° (6.85), 51° (10.6), 76° (15.73 GHz) |
| PEC | λ/4 = 24.2 mm at 3.1 GHz; at 2 mm, 165° off at 3.1 GHz; never within ±90° in our band (only above ≈ 18.7 GHz); break-even ≈ 12.5 GHz |
| Required metasurface phase | ≈ −39° … +105° across 3.1–10.6 GHz *(computed)* |
| Near field | λ/2π > 2 mm below ≈ 23.9 GHz |
| Pending | SRR period and ring sizes, unit-cell phase, antenna + MS, PEC baseline, realized gain, patterns, CST port impedance |

**Formulas**
- λ₀ (mm) = 299.8/f (GHz); k₀ = 2π/λ₀; η₀ ≈ 377 Ω
- Γ = (Z_L − Z₀)/(Z_L + Z₀); |S₁₁|_dB = 20 log|Γ|; RL = −20 log|Γ|; VSWR = (1 + |Γ|)/(1 − |Γ|)
- −10 dB: |Γ| = 0.316, 10 % reflected, VSWR 1.92, mismatch 0.46 dB
- D = 4πU_max/P_rad; G = e_rad·D; G_R = (1 − |Γ|²)·G; e_tot = e_rad(1 − |Γ|²)
- FBW = 2(f_H − f_L)/(f_H + f_L)
- f_L ≈ 7.2/(L + r + p) GHz (cm); disc: L = 2R, r = R/4; our decagon: L = 28.5 mm, r = 3.7 mm, p = 0.73 mm, so ≈ 2.18 GHz
- CPW: Z₀ = (30π/√εeff)·K(k′)/K(k), k = W/(W + 2G), εeff ≈ (εᵣ + 1)/2
- SRR / AMC: f₀ = 1/(2π√LC); HIS: Z_s = jωL/(1 − ω²LC), L = μ₀t, ±90° BW ≈ k₀t
- Reflector: in phase when φ_R − 2k₀h = 2nπ; 2k₀h (deg) = 720·h/λ₀; PEC needs λ/4
- Far field r > 2D²/λ; reactive near field ≲ λ/2π
- ECC_S = |S₁₁*S₁₂ + S₂₁*S₂₂|² / [(1 − |S₁₁|² − |S₂₁|²)(1 − |S₂₂|² − |S₁₂|²)]
- DG = 10√(1 − ECC²); TARC (2-port) = √(|S₁₁ + S₁₂e^{jθ}|² + |S₂₁ + S₂₂e^{jθ}|²)/√2
- CCL = −log₂ det Ψ_R; MEGᵢ ≈ 0.5(1 − Σⱼ|Sᵢⱼ|²)
- C = B log₂ det(I + (SNR/N_t)HHᴴ)

**MIMO targets:** isolation > 15 dB (aim 20) · ECC < 0.01 (spec < 0.5) · DG > 9.9 dB · TARC < −10 dB · CCL < 0.4 bit/s/Hz · MEG ≈ −3 dB, |ΔMEG| < 3 dB

**UWB (FCC 2002):** 3.1–10.6 GHz, −41.3 dBm/MHz EIRP; UWB = BW ≥ 500 MHz or FBW ≥ 20 %

**Literature one-liners:**
- Sen 2017: SRR, +5.5 dB
- Al-Gburi 2022: FSS, 6.7 → 11.5 dB, 10 mm
- Hussain 2023: 9 mm, 3–18 GHz, 6.5 → 10.5 dBi
- Hammache 2024: 20 mm, 2.2 → 8.4 dBi realized
- AboEl-Hassan 2025: AMC, 3.5–6.5 GHz, ≈ 10–11.5 dBi
- Sufian 2021: 4-port, > 32 dB isolation
- Sehrai 2021: mm-wave, 7 → 10.44 dB
- **Hasan 2022: 4-port, SRR, 12 mm, 3.1–7.7 GHz, 5.4 → 8.3 dBi**
- Althuwayb 2023: EBG, > 34.8 dB isolation
- Wu 2023: CP, 7.95 dBic

**Abbreviations:**

| Abbr. | Meaning |
|---|---|
| UWB | ultra-wideband |
| MIMO | multiple-input multiple-output |
| CPW | coplanar waveguide |
| SRR | split-ring resonator |
| FSS | frequency-selective surface |
| AMC | artificial magnetic conductor |
| EBG | electromagnetic bandgap |
| HIS | high-impedance surface |
| PEC / PMC | perfect electric / magnetic conductor |
| FBW | fractional bandwidth |
| VSWR | voltage standing-wave ratio |
| RL | return loss |
| ECC | envelope correlation coefficient |
| DG | diversity gain |
| TARC | total active reflection coefficient |
| CCL | channel capacity loss |
| MEG | mean effective gain |
| F/B | front-to-back ratio |
| HPBW | half-power beamwidth |
| AR | axial ratio |
| CP | circular polarization |
| EIRP | effective isotropic radiated power |
| VNA | vector network analyser |
| SOLT | short-open-load-thru (calibration) |
| FIT / FEM | finite integration technique / finite element method |
| PML | perfectly matched layer |
| WBAN | wireless body-area network |
| FR-4 | flame-retardant glass-epoxy laminate |
| dBi | dB relative to isotropic |
| dBic | dBi for circular polarization |

---

## 9. Two-day study plan (Mon 5 Oct and Tue 6 Oct; evaluation Wed 7 Oct)

Speakers as in §5 (swap if your split differs). Times are approximate.

**Day 1 (Monday 5 Oct): understand and fix facts**

| Time | Chanswarang (slides 1–3, 15) | Anushka (4–6) | Nishit (7–10) | Sanjana (11–14) |
|---|---|---|---|---|
| 2 h | §1.1–1.4, §1.6 (basics, UWB) | §1.9–1.12 (metasurfaces, SRR, HIS, reflectors) + §4 | §1.5, 1.7, 1.13 (CPW, monopoles, CST) + §3 | §1.8 (MIMO) + §2.5–2.9 |
| 1.5 h | **Together:** fix the slides with §0 items 1–3, 6 and 9. Agree the "2 mm reason" (E16). Get the SRR period and ring sizes from CST. | | | |
| 2 h | **CST tasks** (whoever has the CST PC, Appendix A): read the parameter list and fill the dimension table (A.1); find mesh-convergence info in the log (A.3); re-run the > 0 dB Lg case (A.4). If time allows, start the PEC-plate run (A.7) overnight. | | | |
| 1 h | Each person writes their own slide notes from §5 in their own words, and rehearses alone twice. | | | |

**Day 2 (Tuesday 6 Oct): rehearse and drill**

| Time | Activity |
|---|---|
| 1 h | Every person reads all of §6 sections A–E. Everyone must be able to answer the ★ questions, not just the "owner". |
| 1.5 h | **Full run-through 1** with a timer (target 14:30), then fix the slides. |
| 1.5 h | **Mock viva:** each person asks another 15 random questions from §6, rotating so everyone faces K1–K16. Practise the §7 phrasing aloud. |
| 1 h | Topic owners deep-dive their likely grilling: Nishit on §3.4 and K1–K5; Sanjana on H1–H12 and K6–K12; Anushka on §4 and I1–I6; Chanswarang on A–D. |
| 1 h | **Full run-through 2**, plus backup slides B1–B4. Print the §8 cheat sheet for everyone. |
| Evening | Light review only. Check the laptop, PPT on a pen drive plus email, CST screenshots, and the timing. |

**Wednesday morning:** 20 minutes on the cheat sheet. Agree **who answers which topic**, so you don't talk over each other:
- basics: Chanswarang;
- literature and novelty: Anushka;
- design, CST and theory: Nishit;
- metasurface status and MIMO: Sanjana.

Anyone can add a sentence after the lead answers.

---

## Appendix A: how to get every [fill in] from CST (CST Studio Suite 2019)

> Menu names can differ slightly between versions. Use the ribbon search box (top right) to find any command by name.

**A.1 Substrate and dimension table**
- **Parameter List:** View → Parameter List (usually docked at the bottom). Copy all names and values (R, Lg, W_f, G, board size, …).
- **Material:** FR-4 (lossy), εᵣ = 4.3, tan δ = 0.025 (already known). Navigation Tree → Materials → right-click the substrate → Properties to confirm.
- **Feed gap p:** already computed as 0.73 mm (patch centre x = 8 mm, lower flat edge at 8 − 15·cos 18° = −6.27 mm, ground edge at −7 mm). Confirm it in the History List (Modeling → History List).
- **Port line impedance:** after a run, 2D/3D Results → Port Modes → Port 1 → e1 → check "Line impedance" (should be ≈ 50 Ω). Also note the cut-off frequencies of any higher-order modes listed.

**A.2 Board size and profile**
Read Ws and Ls from the Parameter List, or from the substrate brick's dimensions in the History List.

**A.3 Mesh convergence (frequency-domain solver)**
- Simulation → Setup Solver → (FD) → Adaptive Mesh Refinement (properties) shows whether it is on and the ΔS threshold.
- After a run, open the Message window or the solver log (Navigation Tree → 1D Results → Adaptive Meshing → Delta S / mesh cells per pass). Note the number of passes and the final ΔS.
- *Extra check:* tighten the threshold (or set a finer mesh in Mesh → Global Properties), re-run the final design, and compare S₁₁. A change under ≈ 0.5–1 dB in band counts as converged.

**A.4 Re-running the artefact case**
1. Set Lg to the bad value.
2. Simulation → Setup Solver → Frequency Domain → (Frequency samples / Broadband sweep settings). Increase the maximum number of samples, tighten the sweep's convergence setting, and/or add fixed samples near 4.0 and 6.2 GHz.
3. Run it. If it is still odd, run the same model with the Time Domain solver (Simulation → Setup Solver → Time Domain, accuracy −40 dB).
4. Also look at the Port Modes results: if a second port mode appears above ≈ 4 or 6 GHz, shrink the port (keeping it ≈ 50 Ω).
5. Read the solver messages for "sweep not converged" warnings.

**A.5 SRR unit cell: reflection phase**
1. File → New → template **Microwaves & RF/Optical → Periodic Structures → FSS, Metamaterial – Unit Cell** (frequency domain).
2. Draw one cell: 1.6 mm FR-4 with a full copper ground on the back, and the two concentric split rings on top. Set the period p_c.
3. Boundaries: x and y = **unit cell**. Zmax = Floquet port (open/add space). Zmin = electric (the copper ground blocks transmission).
4. De-embed Zmax to the SRR's top surface (Floquet port → distance to reference plane), so the phase refers to the surface.
5. Run the sweep from 2–16 GHz, then plot **arg S(Zmax(1),Zmax(1))** and the magnitude. Check both polarizations, Zmax(1) and Zmax(2) (TE/TM).
6. **Sanity check:** with the SRR deleted and the ground present, the phase should be ≈ 180° at low frequency.
7. Overlay the target band: φ_R = 720·2/λ₀ ± 90° (§3.4 table).

**A.6 Patterns, E/H planes, realized gain, F/B, efficiency**
- **Monitors:** Simulation → Field Monitor → Farfield/RCS at e.g. 3, 4, 6, 8 and 10 GHz (more for gain-versus-frequency).
- **Patterns:** Navigation Tree → Farfields → farfield (f = …) → Farfield Plot → Properties → Polar plot, with cuts φ = 0° and φ = 90°.
  - The E-plane is the cut containing the feed axis (polarization direction).
  - The H-plane is the cut perpendicular to it.
- **Realized gain:** in Farfield Plot properties choose "Realized Gain". For a curve versus frequency use Post-Processing → Template Based Post-Processing → Farfield and Antenna Properties → Farfield Result → Realized Gain (max value) over all monitors.
- **Efficiencies:** shown in the farfield plot's info box (Rad. effic., Tot. effic.) or as 1D results.
- **F/B:** the farfield 0D values or the polar plot readout. F/B = gain at the front direction minus gain at the back direction (dB).

**A.7 PEC baseline (same gap)**
1. Copy the project.
2. Replace the metasurface with a single PEC (or copper) brick of the **same footprint**, 2 mm behind the antenna substrate's bottom face.
3. Use the same mesh, frequencies and monitors.
4. Export S₁₁, realized gain and F/B for three cases: antenna alone, PEC and metasurface.

**A.8 Antenna + metasurface**
1. Build the 6 × 5 cells, centred under the antenna, 2 mm behind.
2. Make sure the waveguide port does not cut into the metasurface (limit its downward extension), and re-check its line impedance.
3. Run the model. If S₁₁ breaks near 6.5 or 12.2 GHz or the band edge, re-sweep Lg with the metasurface in place.

---

*Prepared for the 7 Oct 2026 mid-semester evaluation. Numbers are from the team's brief, and computed values are labelled.
Update this file when the metasurface results arrive.*
