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
    "phase1": "Phase I: CPW-fed UWB Antenna with a Split-Ring-Resonator Metasurface Reflector",
    # From the existing deck (presentation/build_deck.py); to be confirmed by the team.
    "students": [("Chanswarang Boro", "2314143"), ("Nishit Baishya", "2314088"),
                 ("Anushka Dam", "2314115"), ("Sanjana", "2314060")],
    "supervisors": [("Dr. Ujjal Chakraborty", "Associate Professor, ECE"),
                    ("Mr. Sovan Bhattacharya", "PhD Scholar, ECE (Co-guide)")],
}

# ============================================================================= this work (from the team's CST results)
GAP_MM = 3.9  # air gap between the antenna substrate and the metasurface (team, 2026-10-05)

THIS_WORK = {
    "antenna": "CPW-fed planar monopole (R = 15 mm, ground edge L_{g} = −7 mm)",
    "band_ghz": (2.1615, 15.734),         # −10 dB markers, figures/cst_single_final_s11_bandwidth.png
    "resonances": [(2.7275, -32.65), (4.7824, -21.182), (9.2265, -22.556), (14.32, -27.068)],  # markers, cst_single_final_s11_markers.png
    # Read off figures/cst_single_final_gain_ieee.png (CST "Gain", i.e. IEEE gain); ±0.1 dB reading accuracy.
    "gain_ieee_uwb": "≈ 2.9–4.9",         # dBi over 3.1–10.6 GHz (min ≈ 2.9 near 6.3 GHz, max ≈ 4.9 near 8.5 GHz)
    "gain_ieee_peak": "≈ 5.1 dBi at ≈ 13.5 GHz",
    "weak_match": "S11 only ≈ −10.3 dB near 6.5 GHz and ≈ −10.5 dB near 12.2 GHz",
    "metasurface": "Single split-ring resonator (SRR) array",
    "gap_mm": GAP_MM,
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
}


@dataclass
class Paper:
    key: str
    group: str                      # "single" (single antenna + metasurface) or "mimo" (MIMO + metasurface)
    short: str                      # e.g. "Sen et al. (2017)"
    ref: str                        # IEEE reference; completed from the PDF's first page
    ref_checked: bool = False       # True once authors/volume/pages/DOI are checked against the PDF
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
    src: dict[str, str] = field(default_factory=dict)


PAPERS: list[Paper] = [
    # ---------------------------------------------------------------- (i) single antenna + metasurface reflector
    Paper("sen2017", "single", "Sen et al. (2017)",
          "Sen, Banerjee, Kumar, and Das, “An ultra-wideband monopole antenna with a gain enhanced performance using "
          "a novel split-ring meta-surface reflector,” *Microw. Opt. Technol. Lett.*, vol. 59, pp. 1296–1300, 2017, "
          "doi: 10.1002/mop.30527."),
    Paper("aboelhassan2025", "single", "AboEl-Hassan et al. (2025)",
          "M. AboEl-Hassan, A. E. Farahat, and K. F. A. Hussein, “Gain enhancement wideband CPW antenna based on "
          "artificial magnetic conductor,” *Sci. Rep.*, 2025, doi: 10.1038/s41598-025-89622-9."),
    Paper("hussain2023", "single", "Hussain et al. (2023)",
          "M. Hussain *et al.*, “Bandwidth and gain enhancement of a CPW antenna using frequency selective surface for "
          "UWB applications,” *Micromachines*, vol. 14, no. 3, Art. no. 591, 2023, doi: 10.3390/mi14030591."),
    Paper("algburi2022", "single", "Al-Gburi et al. (2022)",
          "A. J. A. Al-Gburi, I. Ibrahim, Z. Zakaria, B. H. Ahmad, N. A. Shairi, and M. Y. Zeain, “High gain of UWB "
          "planar antenna utilising FSS reflector for UWB applications,” *Comput. Mater. Contin.*, vol. 70, no. 1, "
          "pp. 1425–1436, 2022."),
    Paper("hammache2024", "single", "Hammache et al. (2024)",
          "Hammache *et al.*, “Gain enhancement of compact CPW-fed ultra-wideband antenna using an FSS reflector,” "
          "*Microw. Opt. Technol. Lett.*, 2024, doi: 10.1002/mop.34344."),
    # ---------------------------------------------------------------- (ii) MIMO + metasurface (team's papers)
    Paper("sufian2021", "mimo", "Sufian et al. (2021)",
          "M. A. Sufian, N. Hussain, H. Askari, S. G. Park, K. S. Shin, and N. Kim, “Isolation enhancement of a "
          "metasurface-based MIMO antenna using slots and shorting pins,” *IEEE Access*, vol. 9, pp. 73533–73543, "
          "2021."),
    Paper("hasan2022", "mimo", "Hasan et al. (2022)",
          "M. M. Hasan, M. T. Islam, M. Samsuzzaman, M. H. Baharuddin, M. S. Soliman, A. Alzamil, I. I. M. Abu "
          "Sulayman, and M. S. Islam, “Gain and isolation enhancement of a wideband MIMO antenna using metasurface "
          "for 5G sub-6 GHz communication systems,” *Sci. Rep.*, vol. 12, 2022, doi: 10.1038/s41598-022-13522-5."),
    Paper("althuwayb2023", "mimo", "Althuwayb et al. (2023)",
          "A. A. Althuwayb *et al.*, “Metasurface-inspired flexible wearable MIMO antenna array for wireless body "
          "area network applications and biomedical telemetry devices,” *IEEE Access*, 2023."),
    Paper("wu2023", "mimo", "Wu et al. (2023)",
          "R. Wu, J. Dong, and M. Wang, “Wearable polarization conversion metasurface MIMO antenna for biomedical "
          "applications in 5 GHz WBAN,” *Biosensors*, vol. 13, no. 1, Art. no. 73, 2023, doi: 10.3390/bios13010073."),
    Paper("mmwave2021", "mimo", "Metasurface mmWave MIMO (2021)",
          "“Metasurface-based wideband MIMO antenna for 5G millimeter-wave systems,” *IEEE Access*, 2021."),
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
    "the reflector. Only papers whose full text could be read were included, and every value in the comparison "
    "tables was checked against the paper itself.",
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


# Written after the full texts are read (Step 1): research gap, slide cards, report-chapter summary.
GAP_POINTS: list[str] = []
