# Comparison with State of the Art

These rows were collected with automated web research on 2026-10-03 and re-verified on 2026-10-03.
- Full text was read for [5] and [7]–[10]; key numbers for [7]–[10] were spot-checked against the Europe PMC full text.
- [1]–[4] and [6] rest on abstracts or metadata only, because the publishers block automated access.
- **"unverified"** means the accessible text does not settle the value; **"n/r"** means the paper does not report it.
- Check every unverified cell against the PDF (via the university library) before it goes into a paper.

Gain is given as **without reflector → with reflector** where the paper reports both. Category key:
- (a) 4-port UWB with a reflector, AMC or FSS
- (b) 4-port orthogonal UWB, no reflector
- (c) 2-port UWB with an AMC or FSS

| # | Cat. | Ports | Size (mm) | Substrate | Band (GHz) | Isolation (dB) | ECC | DG (dB) | Peak gain (dBi) | Reflector / gap |
|---|---|---|---|---|---|---|---|---|---|---|
| [1] | a | 4 | 0.46λ₀×0.46λ₀×0.01λ₀, λ₀ at 2.08 GHz (≈ 66 mm, computed; mm not stated) | unverified | 2.08–10.4 (notch 2.27–3.62) | > 15 without → > 20 with reflector | unverified | unverified | 7–9.57 in passband (with reflector) | Metal reflector 0.58λ₀ square with 4 vias-metallic probes (not an AMC); h = 0.07λ₀ ≈ 10 mm |
| [2] | a | 4 | unverified | unverified | 3.1–10.6 (notch 5.5) | unverified ("enhanced") | "low" (no value) | unverified | 4.7 → 7 | Circular-ring FSS; gap unverified |
| [3] | a | 4 | 60×60×0.1; AMC 80×80×0.1 | Polyamide 0.1 mm (flexible) | 2–12 | > 25 | unverified | unverified | up to 9.6 (with AMC) | Circular split-ring AMC; gap unverified |
| [4] | c | unverified (orthogonal MIMO) | unverified | unverified | UWB (limits unverified) | unverified | unverified | unverified | 4.2–6.5 with AMC (2.3 dB variation; not an improvement) | Aperture-coupled stepped DRA over dual-AMC reflector (PEC vs AMC discussed); gap unverified |
| [5] | c | 2 | 120×80×1 (single element 80×60); AMC 100×100 as stated | Felt textile, εr 1.3 | 3.7–14 with AMC (3.1–12.75 without) | > 20 over most of band | n/r | n/r | 4.33 → 14.26 peak (at 4.45 GHz); > 5 across band with AMC. Table 3 gives 5.11 without AMC (inconsistent) | 117-cell (13×9) AMC, 5 mm foam spacer |
| [6] | c | 2 | 20×28×1.6 | FR-4 | 3.6–10.6 | > 20 | < 0.005 (measured) | > 9.87 | up to 9.85 (with FSS) | FSS reflector; gap unverified |
| [7] | b | 4 | 38×38×1.6 | FR-4 (εr 4.4, tanδ 0.02) | 3–20 | > 17 | < 0.08 whole band (< 0.02 for 6–20 GHz) | > 9.97 | 1.3–6.2 | none (CPW, perpendicular monopoles) |
| [8] | b | 4 | 45×45×1.6 | FR-4 (εr 4.4) | 3.1–13.1 | > 17 adj. / > 20 diag. | < 0.02 | > 9.9985 | 1.6–7.3 (avg 4) | none (orthogonal, microstrip-fed); TARC < −25 dB |
| [9] | b | 4 | 65×65×0.1 | LCP (εr 2.9) | 2.9–10.86 | > 22 | < 0.01 | > 9.999 | 0.95–6.49 (avg ≈ 4) | none (CPW, orthogonal, cross decoupling branches) |
| [10] | b | 4 | 60×41×1.6 | FR-4 (εr 4.4) | 2.6–10.8 | > 15 low / > 20 high band | 0.0143 avg (< 0.05) | 9.65 avg (9.31–9.99) | 2.3–6.12 | none (orthogonal); TARC < −10 dB |
| **This work** | a | 4 | TBD (board + `h` + AMC) | FR-4 1.6 | TBD | TBD | TBD (S & far-field) | TBD | TBD → TBD | Dual-resonant AMC, `h` = TBD mm (TBD λ) |

Fill in the "This work" row from `figures/summary.txt`.

## References
1. A. Mohanty and S. Sahu, "4-port UWB MIMO antenna with Bluetooth-LTE-WiMax band-rejection and vias-MCP loaded reflector with improved performance," *AEU – Int. J. Electron. Commun.*, vol. 144, Art. no. 154065, 2022, doi: 10.1016/j.aeue.2021.154065.
2. M. Nirmala and N. Deepika Rani, "A spatially selective and electromagnetically tailored low-profile high-gain notched UWB MIMO antenna for 5G and ultra-wideband wireless systems," *Franklin Open*, vol. 16, Art. no. 100687, 2026, doi: 10.1016/j.fraope.2026.100687. (Second author's name form unverified.)
3. B. Alekya, N. A. Murugan, and B. T. P. Madhav, "Artificial magnetic conductor-integrated high-gain quad-port hexagonal antenna for conformal ultra-wideband applications," *ETRI J.*, vol. 48, no. 4, pp. 604–619, 2026, doi: 10.4218/etrij.2025-0252.
4. P. Kumari, R. K. Gangwar, and R. K. Chaudhary, "An aperture-coupled stepped dielectric resonator UWB MIMO antenna with AMC," *IEEE Antennas Wireless Propag. Lett.*, vol. 21, no. 10, pp. 2040–2044, Oct. 2022, doi: 10.1109/LAWP.2022.3189694.
5. S. Douhi, Z. Zahriladha, and A. Eddiai, "A high-gain, low-SAR UWB all-textile two-port MIMO antenna based on an AMC structure for wireless body area networks," *Sci. Rep.*, vol. 16, Art. no. 25405, 2026, doi: 10.1038/s41598-026-45917-z.
6. M. Azharuddin and K. Mondal, "FSS-based gain and isolation optimization in a two-element MIMO antenna for ultra-wideband operations," *Sādhanā*, vol. 51, no. 1, Art. no. 23, 2026, doi: 10.1007/s12046-025-02989-3.
7. W. Yin, S. Chen, J. Chang, C. Li, and S. K. Khamas, "CPW fed compact UWB 4-element MIMO antenna with high isolation," *Sensors*, vol. 21, no. 8, Art. no. 2688, 2021, doi: 10.3390/s21082688.
8. A. Wu, M. Zhao, P. Zhang, and Z. Zhang, "A compact four-port MIMO antenna for UWB applications," *Sensors*, vol. 22, no. 15, Art. no. 5788, 2022, doi: 10.3390/s22155788.
9. J. Zhang, C. Du, and R. Wang, "Design of a four-port flexible UWB-MIMO antenna with high isolation for wearable and IoT applications," *Micromachines*, vol. 13, no. 12, Art. no. 2141, 2022, doi: 10.3390/mi13122141.
10. K. Ramanathan, S. Gopalakrishnan, and T. Chandrakanthan, "Miniaturized dual and quad port MIMO antenna variants featuring elevated diversity performance for UWB and 5G-midband applications," *Micromachines*, vol. 16, no. 6, Art. no. 716, 2025, doi: 10.3390/mi16060716.

## What will make this work stand out
- **ECC < 0.01 and DG > 9.9 dB are standard.** Every paper reports them, so they won't set your design apart. Report them, but don't lead with them.
- **The gap in the literature:** only a few 4-port UWB designs pair the array with a reflector ([1]–[3]), and none of them uses CPW-fed octagonal
  monopoles with an AMC. That combination is your novelty claim.
- **Report gain with vs without the AMC across the full band**, not just one peak frequency ([5] headlines a single-frequency peak of 14.26 dBi).
- **Include the PEC-plate comparison and give the gap `h` in mm and in λ.** Many papers leave the gap unstated.
- **Show the AMC doesn't cost isolation or bandwidth,** and report far-field ECC as well as S-parameter ECC (FR-4 is lossy).
- For a journal (not just the FYP), you'll need **measured** S-parameters and patterns. Plan fabrication after the presentation.
