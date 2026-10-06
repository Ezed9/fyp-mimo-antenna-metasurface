"""Single source of truth for the literature review.

Used by report/build_literature_review.py (Literature_Review.docx + LITERATURE.md), report/build_report.py and
presentation/build_deck.py, so every number appears once.

Rules for PAPERS:
- Every value comes from the paper's own PDF; `src` records where (page / table / figure).
- None   = not extracted yet (rendered as a visible placeholder).
- UNVER  = the full text does not settle the value.
- NR     = the paper does not report it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

UNVER = "unverified"
NR = "n/r"
C_MM_GHZ = 299.792458  # speed of light, mm·GHz


def wavelength_mm(f_ghz: float) -> float:
    return C_MM_GHZ / f_ghz


def round_trip_phase_deg(f_ghz: float, h_mm: float) -> float:
    """2·k0·h in degrees: the phase a wave gains going from the antenna to a reflector at gap h and back."""
    return 720.0 * h_mm / wavelength_mm(f_ghz)


# ============================================================================= project (confirm before submission)
PROJECT = {
    "title": "Wideband MIMO Antenna with Metasurface",
    "phase1": "Phase I: CPW-fed Wideband Antenna with a Split-Ring Metasurface Reflector",
    # From the existing deck (presentation/build_deck.py); to be confirmed by the team.
    "students": [("Chanswarang Boro", "2314143"), ("Nishit Baishya", "2314088"),
                 ("Anushka Dam", "2314115"), ("Sanjana", "2314060")],
    "supervisors": [("Dr. Ujjal Chakraborty", "Associate Professor, ECE"),
                    ("Mr. Sovan Bhattacharya", "PhD Scholar, ECE (Co-guide)")],
}

# ============================================================================= this work (from the team's CST results)
GAP_MM = 3.9  # air gap between the antenna substrate and the metasurface (team, 2026-10-05)

THIS_WORK = {
    "antenna": "CPW-fed decagonal monopole (R = 15 mm, ground edge L_{g} = −7 mm)",
    "band_ghz": (2.1615, 15.734),         # −10 dB markers, figures/cst_single_final_s11_bandwidth.png
    "resonances": [(2.7275, -32.65), (4.7824, -21.182), (9.2265, -22.556), (14.32, -27.068)],  # markers, cst_single_final_s11_markers.png
    # Read off figures/cst_single_final_gain_ieee.png (CST "Gain", i.e. IEEE gain); ±0.1 dB reading accuracy.
    "gain_ieee_uwb": "≈ 2.9–4.9",         # dBi over 3.1–10.6 GHz (min ≈ 2.9 near 6.3 GHz, max ≈ 4.9 near 8.5 GHz)
    "gain_ieee_peak": "≈ 5.1 dBi at ≈ 13.5 GHz",
    "weak_match": "S11 only ≈ −10.3 dB near 6.5 GHz and ≈ −10.5 dB near 12.2 GHz",
    "metasurface": "6 × 5 SRR cells (two concentric split rings), copper-backed",
    "gap_mm": GAP_MM,
    "ms_ground": True,                    # full copper on the back of the metasurface board (team, 5 Oct)
}


def fractional_bw(f_lo: float, f_hi: float) -> float:
    return 2 * (f_hi - f_lo) / (f_hi + f_lo)


# ============================================================================= references
# IEEE style. Mini-markup used by the builders: *italic*, **bold**, _{sub}, ^{sup}.
FOUNDATIONAL: dict[str, str] = {
    "fcc": "Federal Communications Commission, “Revision of Part 15 of the Commission’s rules regarding "
           "ultra-wideband transmission systems,” First Report and Order, ET Docket 98-153, FCC 02-48, Apr. 2002.",
    "agrawall": "N. P. Agrawall, G. Kumar, and K. P. Ray, “Wide-band planar monopole antennas,” *IEEE Trans. "
                "Antennas Propag.*, vol. 46, no. 2, pp. 294–295, Feb. 1998, doi: 10.1109/8.660976.",
    "ray": "K. P. Ray, “Design aspects of printed monopole antennas for ultra-wide band applications,” *Int. J. "
           "Antennas Propag.*, vol. 2008, Art. no. 713858, 2008, doi: 10.1155/2008/713858.",
    "simons": "R. N. Simons, *Coplanar Waveguide Circuits, Components, and Systems*. New York, NY, USA: Wiley, 2001, "
              "doi: 10.1002/0471224758.",
    "balanis": "C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed. Hoboken, NJ, USA: Wiley, 2016.",
    "holloway": "C. L. Holloway, E. F. Kuester, J. A. Gordon, J. O’Hara, J. Booth, and D. R. Smith, “An overview of "
                "the theory and applications of metasurfaces: The two-dimensional equivalents of metamaterials,” "
                "*IEEE Antennas Propag. Mag.*, vol. 54, no. 2, pp. 10–35, Apr. 2012, doi: 10.1109/MAP.2012.6230714.",
    "pendry": "J. B. Pendry, A. J. Holden, D. J. Robbins, and W. J. Stewart, “Magnetism from conductors and enhanced "
              "nonlinear phenomena,” *IEEE Trans. Microw. Theory Techn.*, vol. 47, no. 11, pp. 2075–2084, Nov. 1999, "
              "doi: 10.1109/22.798002.",
    "smith": "D. R. Smith, W. J. Padilla, D. C. Vier, S. C. Nemat-Nasser, and S. Schultz, “Composite medium with "
             "simultaneously negative permeability and permittivity,” *Phys. Rev. Lett.*, vol. 84, no. 18, "
             "pp. 4184–4187, May 2000, doi: 10.1103/PhysRevLett.84.4184.",
    "sievenpiper": "D. Sievenpiper, L. Zhang, R. F. J. Broas, N. G. Alexópolous, and E. Yablonovitch, “High-impedance "
                   "electromagnetic surfaces with a forbidden frequency band,” *IEEE Trans. Microw. Theory Techn.*, "
                   "vol. 47, no. 11, pp. 2059–2074, Nov. 1999, doi: 10.1109/22.798001.",
    "yang": "F. Yang and Y. Rahmat-Samii, “Reflection phase characterizations of the EBG ground plane for low profile "
            "wire antenna applications,” *IEEE Trans. Antennas Propag.*, vol. 51, no. 10, pp. 2691–2703, Oct. 2003, "
            "doi: 10.1109/TAP.2003.817559.",
    "sharawi": "M. S. Sharawi, “Printed multi-band MIMO antenna systems and their performance metrics,” *IEEE Antennas "
               "Propag. Mag.*, vol. 55, no. 5, pp. 218–232, Oct. 2013, doi: 10.1109/MAP.2013.6735522.",
    "foschini": "G. J. Foschini and M. J. Gans, “On limits of wireless communications in a fading environment when "
                "using multiple antennas,” *Wireless Pers. Commun.*, vol. 6, no. 3, pp. 311–335, Mar. 1998, "
                "doi: 10.1023/A:1008889222784.",
    "telatar": "E. Telatar, “Capacity of multi-antenna Gaussian channels,” *Eur. Trans. Telecommun.*, vol. 10, no. 6, "
               "pp. 585–595, Nov./Dec. 1999, doi: 10.1002/ett.4460100604.",
}


@dataclass
class Paper:
    key: str
    group: str                      # "single" (single antenna + metasurface) or "mimo" (MIMO + metasurface)
    short: str                      # e.g. "Sen et al. (2017)"
    ref: str                        # IEEE reference; completed from the PDF's first page
    ref_checked: bool = False       # True once authors/volume/pages/DOI are checked (PDF or publisher page)
    source: str = "abstract"        # "full text" (PDF read) or "abstract" (abstract and publisher pages only)
    antenna: str | None = None      # radiator and feed
    substrate: str | None = None    # material, εr, thickness
    size: str | None = None         # antenna (or MIMO board) size, mm
    ms: str | None = None           # metasurface unit cell, period, array
    placement: str | None = None    # behind / above / integrated; gap in mm and λ; ground-backed?
    band: str | None = None         # −10 dB band, GHz (without → with metasurface when both are given)
    gain: str | None = None         # peak gain, dBi (without → with metasurface)
    eff: str | None = None          # radiation / total efficiency
    ports: str | None = None        # MIMO only
    isolation: str | None = None    # MIMO only, dB
    ecc: str | None = None          # MIMO only
    dg: str | None = None           # MIMO only, dB
    ms_role: str | None = None      # MIMO only: gain, decoupling, polarization conversion, ...
    measured: str | None = None     # "fabricated and measured" / "simulation only"
    problem: str | None = None      # one or two sentences each, for the review text
    method: str | None = None
    results: str | None = None
    relevance: str | None = None    # limitation and what it means for this project
    summary: str | None = None      # 2–3 sentences for the report's condensed review
    src: dict[str, str] = field(default_factory=dict)


PAPERS: list[Paper] = [
    # ---------------------------------------------------------------- (i) single antenna + metasurface reflector
    Paper("sen2017", "single", "Sen et al. (2017)",
          "G. Sen, A. Banerjee, M. Kumar, and S. Das, “An ultra-wideband monopole antenna with a gain enhanced "
          "performance using a novel split-ring meta-surface reflector,” *Microw. Opt. Technol. Lett.*, vol. 59, "
          "no. 6, pp. 1296–1300, 2017, doi: 10.1002/mop.30527.",
          ref_checked=True,
          antenna="Circular-patch UWB monopole",
          substrate=UNVER,
          size=UNVER,
          ms="Double split rings, split angle varied column by column",
          placement="Behind, low-profile gap (value unverified)",
          band="UWB (limits unverified)",
          gain="≈ +5.5 dB increase",
          eff=UNVER,
          measured="Fabricated and measured",
          problem="A UWB printed monopole radiates on both sides of the board and its gain is low.",
          method="A circular-patch UWB monopole is backed by a metasurface of double split-ring patches whose split "
                 "angle changes from column to column, so that the surface reflects in phase over a broad band "
                 "without disturbing the antenna’s impedance bandwidth.",
          results="The gain rises by nearly 5.5 dB across the UWB range with a low-profile antenna-to-reflector gap, "
                  "and measurements agree with simulation.",
          relevance="The only reviewed design with split-ring cells behind a UWB monopole, the cell type chosen in "
                    "this project. Varying the split angle across the array is one way to widen the in-phase band "
                    "that a single SRR resonance cannot cover.",
          summary="A circular-patch UWB monopole backed by double split-ring cells whose split angle varies across "
                  "the array, so the reflection stays in phase over a broad band; the gain rises by nearly 5.5 dB "
                  "over UWB, confirmed by measurement.",
          src={"all": "abstract and publisher page (Wiley); full text not obtained"}),
    Paper("algburi2022", "single", "Al-Gburi et al. (2022)",
          "A. J. A. Al-Gburi, I. B. M. Ibrahim, Z. Zakaria, B. H. Ahmad, N. A. B. Shairi, and M. Y. Zeain, “High gain "
          "of UWB planar antenna utilising FSS reflector for UWB applications,” *Comput. Mater. Contin.*, vol. 70, "
          "no. 1, pp. 1425–1436, 2022, doi: 10.32604/cmc.2022.019741.",
          ref_checked=True, source="full text",
          antenna="CPW-fed ring monopole with three legs",
          substrate="FR-4 (ε_{r} 4.5), 1.6 mm",
          size="50 × 50 antenna; reflector 100 × 100",
          ms="Two patches + circular loop, 5 × 5 mm cells; 19 × 19 FSS on FR-4, ground plane behind",
          placement="Behind; total profile 10 mm (≈ λ/4 at 7.1 GHz)",
          band="2.1–12.6 → 2.2–11.9 (meas.)",
          gain="6.7 → 11.5 (11.3 meas.)",
          eff="Radiation 97 % → 89 % at 9.8 GHz",
          measured="Fabricated and measured",
          problem="A planar UWB antenna radiates on both sides, so its gain is low and changes across the band.",
          method="A CPW-fed “Mercedes”-shaped ring monopole (50 × 50 × 1.6 mm, FR-4, grown from a 15 mm-radius disc) "
                 "is mounted above a single-layer 19 × 19 FSS of 5 mm cells (two metal patches joined by a circular "
                 "loop) with a ground plane behind it; the FSS has a stopband from 2.2 to 12.7 GHz and a reflection "
                 "phase that falls linearly with frequency.",
          results="The antenna alone covers 2.1–12.6 GHz with a 6.7 dB peak gain. With the reflector the measured band "
                  "is 2.2–11.9 GHz and the gain stays between 8.3 and 11.5 dB (11.3 dB measured at 8.5 GHz), while "
                  "radiation efficiency falls from 97 % to 89 % at 9.8 GHz; the total profile is 10 mm.",
          relevance="Closest in geometry to this project (CPW-fed monopole grown from a 15 mm-radius disc on 1.6 mm "
                    "FR-4). It shows that a reflection phase falling with frequency keeps the gain stable over UWB, "
                    "but it needs about 10 mm of profile, versus 3.9 mm here.",
          summary="A CPW-fed ring monopole (15 mm-radius disc origin, FR-4) above a 19 × 19 single-layer FSS with a "
                  "ground plane; measured gain 8.3–11.5 dB over 2.2–11.9 GHz at a 10 mm profile, with efficiency "
                  "falling from 97 % to 89 %.",
          src={"reference": "p. 1 (DOI); volume/pages from the publisher listing",
               "substrate/size": "p. 3, Table 1 p. 4", "FSS": "pp. 1, 6–7, 10", "profile": "p. 11",
               "band/gain/eff": "pp. 1, 3, 5, 10–11, 14", "note": "image-only PDF, read by OCR; paper writes gain in dB"}),
    Paper("hussain2023", "single", "Hussain et al. (2023)",
          "M. Hussain, M. A. Sufian, M. S. Alzaidi, S. I. Naqvi, N. Hussain, D. H. Elkamchouchi, M. F. A. Sree, and "
          "S. Y. A. Fatah, “Bandwidth and gain enhancement of a CPW antenna using frequency selective surface for UWB "
          "applications,” *Micromachines*, vol. 14, no. 3, Art. no. 591, Feb. 2023, doi: 10.3390/mi14030591.",
          ref_checked=True, source="full text",
          antenna="CPW-fed hexagonal patch with stubs",
          substrate="Rogers RT/Duroid 6002 (ε_{r} 2.94), 1.52 mm",
          size="32 × 25 antenna; FSS 50 × 50",
          ms="Ring joined to a square frame; 5 × 5 FSS",
          placement="Behind, 9 mm foam spacer (0.09λ_{L})",
          band="5–17 → 3–18",
          gain="6.5 → 10.5",
          eff="Radiation > 75 % → > 78 % (simulated)",
          measured="Fabricated and measured",
          problem="Compact printed UWB antennas have modest gain, and the multi-layer reflectors used to raise it make "
                  "the structure large and complex.",
          method="A CPW-fed hexagonal patch with stub loading (32 × 25 × 1.52 mm, Rogers RT/Duroid 6002) is backed by "
                 "a single-layer 5 × 5 frequency selective surface of rings joined to a square frame (50 × 50 mm), "
                 "placed 9 mm behind the antenna on a foam spacer. The gap is chosen from the in-phase condition "
                 "φ − 2βG = 2nπ, the same relation used in this project.",
          results="The reflector widens the band from 5–17 GHz to 3–18 GHz and raises the peak gain from 6.5 dBi to "
                  "10.5 dBi (the text also quotes 10.75 dBi and 11 dBi at 8 GHz and 13.5 GHz), with more than 10 dBi "
                  "across the band and radiation efficiency above 78 %. Measured and simulated results agree.",
          relevance="One reflector layer adds about 4–6 dB over a UWB band, but at a 9 mm gap (0.09λ at 3 GHz), more "
                    "than twice the 3.9 mm gap of this project, and with a low-loss Rogers substrate.",
          summary="A CPW-fed stub-loaded hexagonal patch backed by a single-layer 5 × 5 FSS 9 mm below it; the band "
                  "grows from 5–17 to 3–18 GHz and the peak gain from 6.5 to 10.5 dBi, confirmed by measurement.",
          src={"substrate/size": "p. 3", "FSS": "pp. 6, 11", "gap": "abstract; p. 7 (eq. 1, 9 mm Styrofoam)",
               "band/gain": "abstract; Table 1 p. 11; p. 9 text gives 10.75/11 dBi peaks",
               "efficiency": "p. 9 (Fig. 11, simulated)", "measured": "pp. 7–9"}),
    Paper("hammache2024", "single", "Hammache et al. (2024)",
          "B. Hammache, I. Messaoudene, M. Belazzoug, S. Titouni, A. Messai, and T. A. Denidni, “Gain enhancement of "
          "compact CPW-fed ultra-wideband antenna using an FSS reflector,” *Microw. Opt. Technol. Lett.*, vol. 66, "
          "no. 10, Art. no. e34344, 2024, doi: 10.1002/mop.34344.",
          ref_checked=True,
          antenna="CPW-fed hexagonal UWB monopole",
          substrate=UNVER,
          size="30 × 30 antenna; FSS 56 × 56",
          ms="8 × 8 mm cells, 7 × 7 FSS (stopband 3–11.5 GHz)",
          placement="Behind, 20 mm (0.21λ at 3.1 GHz)",
          band="UWB (limits unverified)",
          gain="2.2 → 8.4 (realized)",
          eff=UNVER,
          measured="Fabricated and measured",
          problem="A compact UWB antenna has low gain and a near-omnidirectional pattern.",
          method="A 30 × 30 mm hexagonal CPW-fed UWB antenna is placed 20 mm above a single-layer FSS of 7 × 7 small "
                 "(8 × 8 mm) cells that stops 3–11.5 GHz.",
          results="Realized gain rises from 2.2 dBi to 8.4 dBi and the radiation becomes directional; measurements "
                  "agree with simulation.",
          relevance="A recent example of the usual price of a reflector: a 20 mm gap, about five times the 3.9 mm "
                    "gap of this project.",
          summary="A compact hexagonal CPW-fed UWB antenna 20 mm above a 7 × 7 single-layer FSS; realized gain rises "
                  "from 2.2 to 8.4 dBi with a directional pattern, confirmed by measurement.",
          src={"all": "abstract and publisher page (Wiley); full text not obtained"}),
    Paper("aboelhassan2025", "single", "AboEl-Hassan et al. (2025)",
          "M. AboEl-Hassan, A. E. Farahat, and K. F. A. Hussein, “Gain enhancement wideband CPW antenna based on "
          "artificial magnetic conductor,” *Sci. Rep.*, vol. 15, Art. no. 7108, 2025, "
          "doi: 10.1038/s41598-025-89622-9.",
          ref_checked=True,
          antenna="CPW-fed octagonal monopole with inverted U-slot",
          substrate="Rogers RT5880, 1.57 mm",
          size="27 × 37 antenna; AMC 70 × 70",
          ms="5 × 5 AMC, 0° reflection at 7.44 GHz, on RO4003C with full ground",
          placement="Behind, air gap (5 mm, unconfirmed)",
          band="3.5–6.3 → 3.5–6.5",
          gain="unverified → 9.9–11.5 (sources differ)",
          eff="Total > 80 %",
          measured="Fabricated and measured",
          problem="A printed monopole radiates almost omnidirectionally with low gain, and a metal reflector must sit "
                  "a quarter wavelength away to avoid cancelling the forward wave.",
          method="A CPW-fed octagonal monopole with an inverted U-slot (27 × 37 mm, Rogers RT5880) is placed over an "
                 "artificial magnetic conductor surface of 5 × 5 cells (70 × 70 mm, on RO4003C with a full ground "
                 "plane) designed for 0° reflection at 7.44 GHz, with an air gap between them.",
          results="Over 3.5–6.5 GHz the antenna with the AMC reaches a realized gain of up to 11.5 dBi (the abstract "
                  "also quotes a maximum gain of 9.9 dBi), total efficiency above 80 % and cross-polarization below "
                  "−30 dB; prototypes were fabricated and measured.",
          relevance="The same configuration as this project (CPW-fed octagonal monopole, ground-backed metasurface, "
                    "air gap), but over a much narrower 3.5–6.5 GHz band, which shows how hard it is to keep in-phase "
                    "reflection across all of UWB.",
          summary="A CPW-fed octagonal monopole over a ground-backed 5 × 5 AMC with an air gap; over 3.5–6.5 GHz the "
                  "realized gain reaches up to 11.5 dBi (9.9 dBi is also quoted) with total efficiency above 80 %.",
          src={"all": "abstract and publisher page (Nature/PMC); gap 5 mm in two search summaries only; gain values "
                      "conflict between summaries"}),
    # ---------------------------------------------------------------- (ii) MIMO + metasurface (team's papers)
    Paper("sufian2021", "mimo", "Sufian et al. (2021)",
          "M. A. Sufian, N. Hussain, H. Askari, S. G. Park, K. S. Shin, and N. Kim, “Isolation enhancement of a "
          "metasurface-based MIMO antenna using slots and shorting pins,” *IEEE Access*, vol. 9, pp. 73533–73543, "
          "2021, doi: 10.1109/ACCESS.2021.3079965.",
          ref_checked=True,
          antenna="Patch between a metasurface and the ground",
          substrate=UNVER,
          ports="4 (2 × 2, orthogonal)",
          size="≈ 1.75λ_{0} square",
          ms="4 × 4 square-patch metasurface above each patch",
          ms_role="gain; strips pinned to ground decouple",
          placement="Integrated (upper substrate)",
          band="3.3–3.87",
          isolation="> 32",
          ecc="< 0.001",
          dg="9.99",
          gain="6.3 → 8.1 (element); 8.72 (array)",
          eff="Radiation < 83 % → > 92 % (element)",
          measured="Fabricated (extent of measurement unverified)",
          problem="Closely spaced MIMO elements couple strongly, which degrades isolation and diversity.",
          method="Each element is a patch sandwiched between a 4 × 4 square-patch metasurface and the ground; four "
                 "elements are rotated orthogonally in a 2 × 2 layout for the 5G n78 band. Slots in the ground and "
                 "metal strips on the metasurface layer, shorted to the ground with pins, suppress the coupling.",
          results="The 4-port antenna covers 3.3–3.87 GHz with isolation above 32 dB, ECC below 0.001 and diversity "
                  "gain of 9.99 dB. The metasurface raises the element gain from 6.3 dBi to 8.1 dBi (8.72 dBi for the "
                  "array) and the radiation efficiency from below 83 % to above 92 %.",
          relevance="Shows that the metasurface layer can also carry the decoupling structure; its band (about 16 %) "
                    "is far narrower than UWB.",
          summary="Four orthogonal patch elements, each under a 4 × 4 square-patch metasurface, for 3.3–3.87 GHz; "
                  "ground slots plus pinned metasurface strips give isolation above 32 dB and ECC below 0.001, and the "
                  "metasurface lifts the element gain from 6.3 to 8.1 dBi.",
          src={"all": "abstract and publisher/repository pages; full text not obtained"}),
    Paper("sehrai2021", "mimo", "Sehrai et al. (2021)",
          "D. A. Sehrai, M. Asif, W. A. Shah, J. Khan, I. Ullah, M. Ibrar, S. Jan, M. Alibakhshikenari, F. Falcone, "
          "and E. Limiti, “Metasurface-based wideband MIMO antenna for 5G millimeter-wave systems,” *IEEE Access*, "
          "vol. 9, pp. 125348–125357, 2021, doi: 10.1109/ACCESS.2021.3110905.",
          ref_checked=True,
          antenna="Four elements rotated in 90° steps",
          substrate=UNVER,
          ports="4 (rotated 90°)",
          size="24 × 24",
          ms="2 × 2 non-uniform metasurface",
          ms_role="behind the array: gain",
          placement="Behind the MIMO antenna",
          band="23.5–29.4",
          isolation=UNVER,
          ecc=UNVER,
          dg=UNVER,
          gain="≈ 7 → 10.44",
          eff="Total > 80 %",
          measured="Fabricated and measured",
          problem="Millimetre-wave 5G antennas must be compact, wideband and high-gain to overcome path loss.",
          method="Four antenna elements are rotated in 90° steps to form a compact 24 × 24 mm MIMO antenna, and a "
                 "2 × 2 non-uniform metasurface placed at the back improves its radiation.",
          results="The antenna covers 23.5–29.4 GHz; the metasurface raises the peak gain from about 7 dB to 10.44 dB "
                  "with total efficiency above 80 %, ECC, diversity gain and channel capacity loss are reported as "
                  "good, and measurements agree with simulation.",
          relevance="Uses the two ideas planned for Phase II, 90° rotation of the elements and a metasurface behind the "
                    "array, at 28 GHz instead of UWB.",
          summary="Four elements rotated in 90° steps (24 × 24 mm) with a 2 × 2 non-uniform metasurface behind them "
                  "for 23.5–29.4 GHz; the peak gain rises from about 7 to 10.44 dB with efficiency above 80 %.",
          src={"all": "abstract and repository records; often confused with Tariq et al., IEEE Access 9, 51805 (a "
                      "different paper)"}),
    Paper("hasan2022", "mimo", "Hasan et al. (2022)",
          "M. M. Hasan, M. T. Islam, M. Samsuzzaman, M. H. Baharuddin, M. S. Soliman, A. Alzamil, I. I. M. Abu "
          "Sulayman, and M. S. Islam, “Gain and isolation enhancement of a wideband MIMO antenna using metasurface "
          "for 5G sub-6 GHz communication systems,” *Sci. Rep.*, vol. 12, Art. no. 9433, 2022, "
          "doi: 10.1038/s41598-022-13522-5.",
          ref_checked=True,
          antenna="Microstrip-fed truncated-corner square patch",
          substrate="Rogers RT5880 (ε_{r} 2.2), 1.575 mm",
          ports="4 (orthogonal)",
          size="1.05λ × 1.05λ",
          ms="10 × 10 square-enclosed circular SRRs, copper-backed, 12 mm air gap below",
          ms_role="reflector: gain and isolation",
          placement="Behind, 12 mm air gap (single-antenna study)",
          band="3.08–7.75 (3.2–7.6 also quoted)",
          isolation="> 15.5",
          ecc="< 0.004",
          dg="> 9.98",
          gain="5.4 → 8.3 (realized)",
          eff="Average total 82 %",
          measured="Fabricated and measured",
          problem="Compact sub-6 GHz MIMO antennas need more gain and isolation without a larger element spacing.",
          method="Four orthogonally rotated, microstrip-fed truncated-corner patches on 1.575 mm Rogers RT5880 sit "
                 "above a 10 × 10 metasurface of square-enclosed circular split-ring resonators with a copper "
                 "backplane, which reflects the back radiation (a 12 mm air gap is used in the single-antenna study).",
          results="The fabricated 4-port antenna covers about 3.1–7.7 GHz with isolation above 15.5 dB, ECC below "
                  "0.004 and diversity gain above 9.98 dB; the metasurface raises the realized gain from 5.4 dBi to "
                  "8.3 dBi with 82 % average total efficiency. The two published author corrections change "
                  "affiliations only.",
          relevance="The closest MIMO counterpart of this project: a copper-backed split-ring metasurface behind the "
                    "antennas across an air gap, which is the configuration planned for Phase II, here over a 2.5:1 "
                    "band rather than UWB.",
          summary="Four orthogonal truncated-corner patches above a copper-backed 10 × 10 array of square-enclosed "
                  "circular split-ring resonators; about 3.1–7.7 GHz, isolation above 15.5 dB, ECC below 0.004, and "
                  "realized gain raised from 5.4 to 8.3 dBi.",
          src={"all": "abstract and publisher page (Nature/PMC); band quoted two ways; corrections checked"}),
    Paper("althuwayb2023", "mimo", "Althuwayb et al. (2023)",
          "A. A. Althuwayb, M. Alibakhshikenari, B. S. Virdee, N. Rashid, K. Kaaniche, A. Ben Atitallah, A. Armghan, "
          "O. I. Elhamrawy, C. H. See, and F. Falcone, “Metasurface-inspired flexible wearable MIMO antenna array for "
          "wireless body area network applications and biomedical telemetry devices,” *IEEE Access*, vol. 11, "
          "pp. 1039–1056, 2023, doi: 10.1109/ACCESS.2022.3233388.",
          ref_checked=True,
          antenna="Triangular radiators, 2 × 2 array",
          substrate="Rogers RT/duroid 5880, 0.8 mm (flexible)",
          ports="4 (2 × 2)",
          size=UNVER,
          ms="Sub-wavelength slots etched in the radiators",
          ms_role="bandwidth and gain; EBG between elements decouples",
          placement="Integrated in the radiators",
          band="5.0–6.6",
          isolation="> 34.8",
          ecc=UNVER,
          dg=UNVER,
          gain="10 (avg.); 8.65–10.5 when bent",
          eff="83 % average (77–83 % when bent)",
          measured="Fabricated (measured/simulated split unverified)",
          problem="Wearable body-area and biomedical-telemetry devices need compact, flexible MIMO arrays whose "
                  "closely spaced elements stay isolated.",
          method="A flexible 2 × 2 array of triangular radiators on 0.8 mm Rogers RT/duroid 5880 is turned into a "
                 "metasurface by etching sub-wavelength slots into the radiators, and an electromagnetic-bandgap (EBG) "
                 "structure between the elements blocks the surface currents that couple them.",
          results="Over 5.0–6.6 GHz the array gives isolation above 34.8 dB, an average gain of 10 dBi and 83 % "
                  "efficiency, and keeps 8.65–10.5 dBi and 77–83 % when bent.",
          relevance="Combines metasurface-inspired radiators with an EBG decoupler; the EBG idea is a candidate for "
                    "Phase II if orthogonal placement alone does not give enough isolation.",
          summary="A flexible 2 × 2 array of slotted (metasurface-inspired) triangular radiators with an EBG decoupler "
                  "for 5.0–6.6 GHz; isolation above 34.8 dB, average gain 10 dBi and efficiency 83 %.",
          src={"all": "abstract and repository records; full text not obtained"}),
    Paper("wu2023", "mimo", "Wu et al. (2023)",
          "R. Wu, J. Dong, and M. Wang, “Wearable polarization conversion metasurface MIMO antenna for biomedical "
          "applications in 5 GHz WBAN,” *Biosensors*, vol. 13, no. 1, Art. no. 73, 2023, doi: 10.3390/bios13010073.",
          ref_checked=True,
          antenna=UNVER,
          substrate=UNVER,
          ports="2",
          size="1.67λ_{0} × 0.81λ_{0} (5.6 GHz)",
          ms="Polarization-conversion metasurface",
          ms_role="circular polarization and gain",
          placement=UNVER,
          band="4.76–6.77 (meas.)",
          isolation="> 19.85 (strip)",
          ecc="< 0.007",
          dg="> 9.98",
          gain="7.95 dBic",
          eff=UNVER,
          measured="Fabricated and measured; SAR simulated",
          problem="Wearable 5 GHz body-area links need broadband, circularly polarized, high-gain antennas that are "
                  "safe for the body.",
          method="A two-element wearable MIMO antenna uses a polarization-conversion metasurface to obtain circular "
                 "polarization and higher gain, and an isolation strip between the elements to reduce coupling; the "
                 "specific absorption rate is checked with a human-tissue model.",
          results="Measured −10 dB band 4.76–6.77 GHz and 3 dB axial-ratio band 4.9–6.17 GHz, isolation above "
                  "19.85 dB, peak gain 7.95 dBic, ECC below 0.007, diversity gain above 9.98 dB and channel capacity "
                  "loss below 0.29 bit/s/Hz.",
          relevance="Uses the metasurface to change the polarization rather than only to reflect, which matters if "
                    "Phase II needs polarization diversity.",
          summary="A two-element wearable antenna with a polarization-conversion metasurface for 5 GHz body-area "
                  "networks: 4.76–6.77 GHz, circular polarization over 4.9–6.17 GHz, isolation above 19.85 dB with an "
                  "isolation strip, 7.95 dBic.",
          src={"all": "abstract (MDPI/PMC); full text not obtained"}),
]

BY_KEY = {p.key: p for p in PAPERS}
SINGLE = [p for p in PAPERS if p.group == "single"]
MIMO = [p for p in PAPERS if p.group == "mimo"]


def ref_text(key: str) -> str:
    return BY_KEY[key].ref if key in BY_KEY else FOUNDATIONAL[key]


# ============================================================================= shared prose
# Citations: [@key] or [@key1, key2]; the builders number them in order of first use.
SCOPE = [
    "Phase I of the project, presented at this mid-semester evaluation, is a single coplanar-waveguide (CPW) fed "
    "ultra-wideband (UWB) monopole backed by a split-ring-resonator (SRR) metasurface placed behind it across an air "
    "gap. Phase II extends the design to a multiple-input multiple-output (MIMO) antenna. The review is split the "
    "same way: (i) single wideband antennas whose gain is raised by a metasurface, artificial magnetic conductor "
    "(AMC) or frequency selective surface (FSS) reflector, which bear directly on the present design, and (ii) MIMO "
    "antennas that use metasurfaces, which inform the next phase.",
    "Papers were located through keyword searches (Google Scholar and the IEEE Xplore, ScienceDirect, Wiley, Nature "
    "and MDPI sites) combining “CPW-fed”, “UWB monopole”, “metasurface reflector”, “split-ring resonator”, “AMC”, "
    "“FSS”, “gain enhancement” and “MIMO isolation”, together with papers already identified by the team. Group (i) "
    "required a printed wideband or UWB antenna, a periodic reflector behind it, and gain reported with and without "
    "the reflector.",
    "Two papers, by Al-Gburi et al. and Hussain et al., were read in full. For the others the full text could not be obtained in "
    "time, so their values come from the abstracts and the publishers’ public pages. Every value in the tables was "
    "checked against at least one of these sources; a value that could not be confirmed is marked “unverified” "
    "rather than estimated.",
]

BACKGROUND_UWB = (
    "The FCC opened 3.1–10.6 GHz for unlicensed UWB communication at a very low power spectral density of "
    "−41.3 dBm/MHz [@fcc]. Printed planar monopoles are the usual UWB radiators: a planar disc or polygon behaves like "
    "a thick cylindrical monopole whose closely spaced resonances overlap into one very wide impedance band "
    "[@agrawall, ray]. A CPW feed keeps the signal strip and both ground planes on the same side of the substrate, so "
    "no vias are needed and the ground can later be shared between MIMO elements [@simons]. The weakness of the "
    "printed monopole is its gain: it radiates almost equally on both sides of the board, so roughly half of the "
    "power leaves through the back and the gain stays at a few dBi [@balanis]."
)

BACKGROUND_SRR = (
    "A metasurface is a two-dimensional array of sub-wavelength scatterers (unit cells) whose geometry sets the "
    "amplitude and phase of the waves it reflects or transmits [@holloway]. The split-ring resonator (SRR) of "
    "Pendry *et al.* [@pendry] is one of the most widely used unit cells. The metal ring behaves as an inductance L "
    "and the split as a capacitance C, so the cell resonates at"
)
BACKGROUND_SRR_AFTER = (
    "Near f_{0} the SRR responds strongly to the incident magnetic field; arrays of SRRs formed the first "
    "negative-index metamaterial [@smith]. Because L and C follow from the ring size, trace width and split width, "
    "the resonance is tuned by geometry alone."
)

BACKGROUND_REFLECTOR = (
    "When a reflector is placed a distance h behind an antenna, the wave radiated backwards returns to the antenna "
    "plane after a round trip of 2h and a reflection phase φ_{R}. It adds constructively to the forward wave when"
)
BACKGROUND_REFLECTOR_AFTER = (
    "where k_{0} = 2π/λ_{0} is the free-space wavenumber and n is an integer. "
    "A metal (PEC) plate reflects with φ_{R} = 180°, so (2) requires h = λ_{0}/4, which is 24.2 mm at 3.1 GHz, and a "
    "fixed gap meets that condition at one frequency only. A high-impedance surface, or artificial magnetic "
    "conductor (AMC), reflects in phase (φ_{R} ≈ 0°) near its resonance [@sievenpiper]; its useful band is usually "
    "taken as the range where φ_{R} stays within ±90° [@yang]. An in-phase reflector can therefore sit much closer to "
    "the antenna, which gives a low-profile, unidirectional antenna with higher gain."
)


def gap_paragraph() -> str:
    """Position of this work: what the 3.9 mm gap implies (computed from (2), not simulated)."""
    lo, hi = 3.1, 10.6
    p_lo, p_hi = round_trip_phase_deg(lo, GAP_MM), round_trip_phase_deg(hi, GAP_MM)
    return (
        f"In this project the metasurface sits h = {GAP_MM} mm behind the antenna, only "
        f"{GAP_MM / wavelength_mm(lo):.3f}λ_{{0}} at {lo} GHz. From (2), the round-trip term 2k_{{0}}h is "
        f"{p_lo:.0f}° at {lo} GHz and {p_hi:.0f}° at {hi} GHz (computed). A PEC plate at this gap would therefore be "
        f"{180 - p_lo:.0f}° out of phase at {lo} GHz and largely cancel the forward radiation, whereas a metasurface "
        f"whose reflection phase stays within ±90° of 2k_{{0}}h adds to it. This simple ray picture ignores near-field "
        f"coupling, which is strong at such a small gap, so the metasurface also loads the antenna and its impedance "
        f"match must be re-checked with the metasurface in place."
    )


# Research gap, from the comparison in Tables A and B.
GAP_POINTS: list[str] = [
    "**Reflector distance.** The single-antenna reflectors reviewed sit 9 mm [@hussain2023], 10 mm (total profile) "
    "[@algburi2022] and 20 mm [@hammache2024] behind the antenna, about 0.07–0.21 of a wavelength at the lowest "
    "operating frequency. The ground-backed AMC of [@aboelhassan2025] sits closer across a small air gap, but its "
    "band (3.5–6.5 GHz) is far narrower than UWB. Phase I places the metasurface only 3.9 mm (0.04λ at 3.1 GHz) "
    "behind an antenna that covers 2.16–15.73 GHz: a lower profile, but a harder in-phase condition and stronger "
    "near-field loading.",
    "**Cell type.** Only [@sen2017] uses split-ring cells behind a UWB monopole, varying the split angle across the "
    "array to widen the in-phase band; the others use ring, loop and patch FSS or AMC cells [@algburi2022, hussain2023, "
    "hammache2024, aboelhassan2025]. A split-ring metasurface also appears in the MIMO design of [@hasan2022], but "
    "over 3.1–7.7 GHz. A single-SRR metasurface behind a CPW-fed antenna covering the whole UWB band is not reported "
    "in the papers reviewed.",
    "**Baselines and reporting.** Neither of the two papers read in full compares its reflector with a plain metal "
    "plate at the same gap, and gain is usually quoted as a single peak value, often without saying whether it is "
    "realized gain. This project compares the antenna alone, a metal plate and the SRR metasurface at the same "
    "3.9 mm gap, reports gain across the band and states which gain is shown.",
    "**MIMO.** The MIMO papers use metasurfaces for gain [@sehrai2021, hasan2022], for decoupling together with other "
    "structures [@sufian2021, althuwayb2023] and for polarization conversion [@wu2023], but all in bands far narrower "
    "than UWB (3.3–3.87, 3.1–7.7, 5.0–6.6, 4.76–6.77 and 23.5–29.4 GHz). A UWB MIMO antenna with an SRR "
    "metasurface reflector is the open target of Phase II.",
]
