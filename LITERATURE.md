# Comparison with State of the Art

These rows were collected with automated web research on 2026-10-03.
- **"unverified"** means the value could not be confirmed from accessible text (several publishers block automated
  access). **Check every unverified cell against the PDF** (via the university library) before it goes into the paper.
- Rows 5 and 7–10 were read from open-access full text. Rows 1–4 and 6 rest on abstracts or Crossref only.

Gain is given as **without reflector → with reflector** where the paper reports both. Category key:
- (a) 4-port UWB with a reflector/AMC/FSS
- (b) 4-port orthogonal UWB, no reflector
- (c) 2-port UWB with AMC/FSS

| # | Cat. | Ports | Size (mm) | Substrate | Band (GHz) | Isolation (dB) | ECC | DG (dB) | Peak gain (dBi) | Reflector / gap |
|---|---|---|---|---|---|---|---|---|---|---|
| [1] | a | 4 | 0.46λ₀×0.46λ₀ (λ₀ at 2.08 GHz; mm not reported) | unverified | 2.08–10.4 (notch 2.27–3.62) | > 20 | unverified | unverified | 7–9.57 (with reflector) | Reflector with vias and metallic probes (not an AMC); gap unverified |
| [2] | a | 4 | unverified | unverified | 3.1–10.6 (notch 5.5) | "improved" | "low" | unverified | 4.7 → 7 | Circular-ring FSS; gap unverified |
| [3] | a | 4 | 60×60×0.1; AMC 80×80 | Polyamide (flexible) | 2–12 | > 25 | unverified | unverified | up to 9.6 (with AMC) | Circular split-ring AMC; gap unverified |
| [4] | c | 2 | n/r | unverified | UWB | unverified | unverified | unverified | ≈ +2.3 dB (unverified) | AMC under a stepped DRA |
| [5] | c | 2 | 80×60×1; AMC 100×100 | Felt textile | 3.7–14 | > 20 (most of band) | n/r | n/r | 4.33 → 14.26 (at 4.45 GHz only) | 9×13 AMC cells, 5 mm spacer |
| [6] | c | 2 | 20×28×1.6 | FR-4 | 3.6–10.6 | > 20 | < 0.005 | > 9.87 | up to 9.85 (with FSS) | FSS reflector; gap unverified |
| [7] | b | 4 | 38×38×1.6 | FR-4 | 3–20 | > 17 | < 0.1 (< 0.02 above 6 GHz) | > 9.97 | 1.3–6.2 | none (CPW, perpendicular monopoles) |
| [8] | b | 4 | 45×45×1.6 | FR-4 | 3.1–13.1 | > 17 adj. / > 20 diag. | < 0.02 | > 9.998 | ≈ 4 avg | none (orthogonal); TARC < −25 dB |
| [9] | b | 4 | 65×65×0.1 | LCP (flexible) | 2.9–10.86 | > 22 | < 0.01 | 9.999 | ≈ 4 avg | none (CPW, orthogonal, cross decoupling branches) |
| [10] | b | 4 | 60×41×1.6 | FR-4 | 2.6–10.8 | > 15 low / > 20 high band | 0.0143 avg | 9.65 avg | 6.12 | none (orthogonal); TARC < −10 dB |
| **This work** | a | 4 | TBD (board + `h` + AMC) | FR-4 1.6 | TBD | TBD | TBD (S & far-field) | TBD | TBD → TBD | Dual-resonant AMC, `h` = TBD mm (TBD λ) |

Fill in the "This work" row from `figures/summary.txt`.

## References
1. A. Mohanty and S. Sahu, "4-port UWB MIMO antenna with bluetooth-LTE-WiMax band-rejection and vias-MCP loaded reflector with improved performance," *AEU – Int. J. Electron. Commun.*, vol. 144, 154065, 2022. doi:10.1016/j.aeue.2021.154065
2. M. Nirmala and D. Rani N., "A spatially selective and electromagnetically tailored low-profile high-gain notched UWB MIMO antenna for 5G and Ultra-Wideband wireless systems," *Franklin Open*, vol. 16, 2026. doi:10.1016/j.fraope.2026.100687
3. B. Alekya, N. A. Murugan and B. T. P. Madhav, "Artificial magnetic conductor-integrated high-gain quad-port hexagonal antenna for conformal ultra-wideband applications," *ETRI Journal*, vol. 48, no. 4, 2026. doi:10.4218/etrij.2025-0252
4. P. Kumari, R. K. Gangwar and R. K. Chaudhary, "An aperture-coupled stepped dielectric resonator UWB MIMO antenna with AMC," *IEEE AWPL*, vol. 21, no. 10, pp. 2040–2044, 2022. doi:10.1109/LAWP.2022.3189694
5. S. Douhi, Z. Zahriladha and A. Eddiai, "A high-gain, low-SAR UWB all-textile two-port MIMO antenna based on an AMC structure for wireless body area networks," *Scientific Reports*, 2026. doi:10.1038/s41598-026-45917-z
6. M. Azharuddin and K. Mondal, "FSS-based gain and isolation optimization in a two-element MIMO antenna for ultra-wideband operations," *Sādhanā*, vol. 51, art. 23, 2026. doi:10.1007/s12046-025-02989-3
7. W. Yin *et al.*, "CPW Fed Compact UWB 4-Element MIMO Antenna with High Isolation," *Sensors*, 2021. doi:10.3390/s21082688
8. Wu *et al.*, "A Compact Four-Port MIMO Antenna for UWB Applications," *Sensors*, vol. 22, 5788, 2022. doi:10.3390/s22155788
9. J. Zhang, C. Du and R. Wang, "Design of a Four-Port Flexible UWB-MIMO Antenna with High Isolation for Wearable and IoT Applications," *Micromachines*, 2022. doi:10.3390/mi13122141
10. K. Ramanathan *et al.*, "Miniaturized Dual and Quad Port MIMO Antenna Variants Featuring Elevated Diversity Performance for UWB and 5G-Midband Applications," *Micromachines*, 2025. doi:10.3390/mi16060716

## What will make this work stand out
- **ECC < 0.01 and DG > 9.9 dB are standard.** Every paper reports them, so they won't set your design apart. Report them, but don't lead with them.
- **The gap in the literature:** only a few 4-port UWB designs pair the array with a reflector ([1]–[3]), and none of them uses CPW-fed octagonal
  monopoles with an AMC. That combination is your novelty claim.
- **Report gain with vs without the AMC across the full band**, not just one peak frequency ([5] quotes one frequency only).
- **Include the PEC-plate comparison and give the gap `h` in mm and in λ.** Many papers leave the gap unstated.
- **Show the AMC doesn't cost isolation or bandwidth,** and report far-field ECC as well as S-parameter ECC (FR-4 is lossy).
- For a journal (not just the FYP), you'll need **measured** S-parameters and patterns. Plan fabrication after the presentation.
