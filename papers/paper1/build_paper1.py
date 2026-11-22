"""Build the revised Paper 1 (.docx, IEEE conference format).

    python papers/make_figures.py && python papers/paper1/build_paper1.py

Every number in the text comes from the two CST runs of the original manuscript (antenna alone; antenna with the
patch board); papers/data/p1_*.csv hold the curves and papers/check_numbers.py recomputes the numbers from them.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from ieee_docx import Paper  # noqa: E402

FIG = HERE / "figures"
OUT = HERE / "Paper1_TriBand_Octagonal_Monopole_revised.docx"

AFFIL = ("Department of Electronics and Communication Engineering", "National Institute of Technology Silchar",
         "Silchar, Assam 788010, India")
AUTHORS = [[("Chanswarang Boro", *AFFIL), ("Nishit Baishya", *AFFIL), ("Anushka Dam", *AFFIL)],
           [("Sanjana", *AFFIL), ("Sovan Bhattacharya", *AFFIL), ("Ujjal Chakraborty", *AFFIL)]]

REFS = [
    "C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed. Hoboken, NJ, USA: Wiley, 2016.",
    "3rd Generation Partnership Project, “NR; Base Station (BS) radio transmission and reception,” 3GPP TS 38.104.",
    "*IEEE Standard for Information Technology—Telecommunications and Information Exchange Between Systems—Local "
    "and Metropolitan Area Networks—Specific Requirements—Part 11: Wireless LAN Medium Access Control (MAC) and "
    "Physical Layer (PHY) Specifications*, IEEE Std 802.11-2020 (Revision of IEEE Std 802.11-2016), Feb. 2021, "
    "doi: 10.1109/IEEESTD.2021.9363693.",
    "*IEEE Standard Letter Designations for Radar-Frequency Bands*, IEEE Std 521-2019 (Revision of IEEE Std "
    "521-2002), Feb. 2020, doi: 10.1109/IEEESTD.2020.8999849.",
    "R. N. Simons, *Coplanar Waveguide Circuits, Components, and Systems*. New York, NY, USA: Wiley, 2001, "
    "doi: 10.1002/0471224758.",
    "Y. Song, Y.-C. Jiao, G. Zhao, and F.-S. Zhang, “Multiband CPW-fed triangle-shaped monopole antenna for "
    "wireless applications,” *Prog. Electromagn. Res.*, vol. 70, pp. 329–336, 2007, "
    "doi: 10.2528/PIER07020201.",
    "S. Ahmad, U. Ijaz, S. Naseer, A. Ghaffar, M. A. Qasim, F. Abrar, N. O. Parchin, C. H. See, and "
    "R. Abd-Alhameed, “A jug-shaped CPW-fed ultra-wideband printed monopole antenna for wireless communications "
    "networks,” *Appl. Sci.*, vol. 12, no. 2, Art. no. 821, Jan. 2022, doi: 10.3390/app12020821.",
    "O. P. Kumar, T. Ali, P. Kumar, P. Kumar, and J. Anguera, “An elliptical-shaped dual-band UWB notch antenna "
    "for wireless applications,” *Appl. Sci.*, vol. 13, no. 3, Art. no. 1310, Jan. 2023, doi: 10.3390/app13031310.",
    "S. Bhattacharya, A. Chatterjee, P. P. Sarkar, and A. Swarnakar, “A javelin shaped UWB antenna with notch "
    "band for remote sensing applications,” *Amer. J. Electron. Commun.*, vol. 5, no. 1, pp. 58–61, Jan. 2025.",
    "D. Sievenpiper, L. Zhang, R. F. J. Broas, N. G. Alexópolous, and E. Yablonovitch, “High-impedance "
    "electromagnetic surfaces with a forbidden frequency band,” *IEEE Trans. Microw. Theory Techn.*, vol. 47, "
    "no. 11, pp. 2059–2074, Nov. 1999, doi: 10.1109/22.798001.",
    "G. Sen, A. Banerjee, M. Kumar, and S. Das, “An ultra-wideband monopole antenna with a gain enhanced "
    "performance using a novel split-ring meta-surface reflector,” *Microw. Opt. Technol. Lett.*, vol. 59, no. 6, "
    "pp. 1296–1300, Jun. 2017, doi: 10.1002/mop.30527.",
    "A. J. A. Al-Gburi, I. B. M. Ibrahim, Z. Zakaria, B. H. Ahmad, N. A. B. Shairi, and M. Y. Zeain, “High gain "
    "of UWB planar antenna utilising FSS reflector for UWB applications,” *Comput. Mater. Contin.*, vol. 70, "
    "no. 1, pp. 1419–1436, 2022, doi: 10.32604/cmc.2022.019741.",
    "M. Hussain, M. A. Sufian, M. S. Alzaidi, S. I. Naqvi, N. Hussain, D. H. Elkamchouchi, M. F. A. Sree, and "
    "S. Y. A. Fatah, “Bandwidth and gain enhancement of a CPW antenna using frequency selective surface for UWB "
    "applications,” *Micromachines*, vol. 14, no. 3, Art. no. 591, Feb. 2023, doi: 10.3390/mi14030591.",
    "B. Hammache, I. Messaoudene, M. Belazzoug, S. Titouni, A. Messai, and T. A. Denidni, “Gain enhancement of "
    "compact CPW-fed ultra-wideband antenna using an FSS reflector,” *Microw. Opt. Technol. Lett.*, vol. 66, "
    "no. 10, Art. no. e34344, Oct. 2024, doi: 10.1002/mop.34344.",
    "M. AboEl-Hassan, A. E. Farahat, and K. F. A. Hussein, “Gain enhancement wideband CPW antenna based on "
    "artificial magnetic conductor,” *Sci. Rep.*, vol. 15, no. 1, Art. no. 7108, Feb. 2025, "
    "doi: 10.1038/s41598-025-89622-9.",
    "S. Kundu and A. Chatterjee, “Sharp triple-notched ultra wideband antenna with gain augmentation using FSS "
    "for ground penetrating radar,” *Wireless Pers. Commun.*, vol. 117, no. 2, pp. 1399–1418, Mar. 2021, "
    "doi: 10.1007/s11277-020-07928-5.",
    "S. Kundu, A. Chatterjee, S. K. Jana, and S. K. Parui, “Gain enhancement of a printed leaf shaped UWB antenna "
    "using dual FSS layers and experimental study for ground coupling GPR applications,” *Microw. Opt. Technol. "
    "Lett.*, vol. 60, no. 6, pp. 1417–1423, Jun. 2018, doi: 10.1002/mop.31171.",
    "A. Chatterjee and S. K. Parui, “Frequency-dependent directive radiation of monopole-dielectric resonator "
    "antenna using a conformal frequency selective surface,” *IEEE Trans. Antennas Propag.*, vol. 65, no. 5, "
    "pp. 2233–2239, May 2017, doi: 10.1109/TAP.2017.2677914.",
    "P. Rajalakshmi and N. Gunavathi, “Gain enhancement of cross shaped patch antenna for IEEE 802.11ax Wi-Fi "
    "applications,” *Prog. Electromagn. Res. Lett.*, vol. 80, pp. 91–99, 2018, doi: 10.2528/PIERL18091401.",
    "H. L. Zhu, X. H. Liu, S. W. Cheung, and T. I. Yuk, “Frequency-reconfigurable antenna using metasurface,” *IEEE "
    "Trans. Antennas Propag.*, vol. 62, no. 1, pp. 80–85, Jan. 2014, doi: 10.1109/TAP.2013.2288112.",
    "H. L. Zhu, S. W. Cheung, K. L. Chung, and T. I. Yuk, “Linear-to-circular polarization conversion using "
    "metasurface,” *IEEE Trans. Antennas Propag.*, vol. 61, no. 9, pp. 4615–4623, Sep. 2013, "
    "doi: 10.1109/TAP.2013.2267712.",
    "N. Alexopoulos and D. Jackson, “Fundamental superstrate (cover) effects on printed circuit antennas,” *IEEE "
    "Trans. Antennas Propag.*, vol. 32, no. 8, pp. 807–816, Aug. 1984, doi: 10.1109/TAP.1984.1143433.",
    "K. P. Ray, “Design aspects of printed monopole antennas for ultra-wide band applications,” *Int. J. Antennas "
    "Propag.*, vol. 2008, Art. no. 713858, 2008, doi: 10.1155/2008/713858.",
    "G. Kumar and K. P. Ray, *Broadband Microstrip Antennas*. Norwood, MA, USA: Artech House, 2003.",
    "O. Luukkonen, C. Simovski, G. Granet, G. Goussetis, D. Lioubtchenko, A. V. Räisänen, and S. A. Tretyakov, "
    "“Simple and accurate analytical model of planar grids and high-impedance surfaces comprising metal strips or "
    "patches,” *IEEE Trans. Antennas Propag.*, vol. 56, no. 6, pp. 1624–1632, Jun. 2008, "
    "doi: 10.1109/TAP.2008.923327.",
    "D. F. Sievenpiper, “High-impedance electromagnetic surfaces,” Ph.D. dissertation, Dept. Elect. Eng., Univ. "
    "California, Los Angeles, CA, USA, 1999.",
]


# The authors' title. A reviewer may object to "tri-band" (the antenna alone is matched over more spectrum) and to
# "metasurface" (4 x 4 ungrounded cells); the alternative below claims only what the data show.
TITLE = "A Compact Tri-Band CPW-Fed Octagonal Monopole Antenna Loaded with a 4 × 4 Square-Patch Metasurface"
ALT_TITLE = ("Effect of a Zero-Gap 4 × 4 Patch-Array Cover Board on a CPW-Fed Octagonal Wideband Monopole Antenna: "
             "A Simulation Study")


def build() -> Path:
    p = Paper()
    p.title(TITLE)
    p.authors(AUTHORS)
    # -- abstract ------------------------------------------------------------------------------------------------
    p.abstract(
        "A compact coplanar-waveguide (CPW)-fed octagonal monopole antenna loaded with a 4 × 4 square-patch "
        "metasurface is studied by full-wave simulation. The radiator is printed on a 27 mm × 30 mm × 1.6 mm FR-4 "
        "substrate. A second FR-4 board of the same footprint lies directly on the radiator, with no air gap, and "
        "carries the patches on its outer face; neither board has a backing conductor, and the total thickness is "
        "3.2 mm. Alone, the antenna is matched (|*S*_{11}| ≤ −10 dB) from 3.52 GHz to beyond the 15 GHz limit of "
        "the simulation, except for 5.21–5.79 GHz, where |*S*_{11}| reaches −9.8 dB. With the board, the match near "
        "5.3 GHz improves to −27.8 dB, but two mismatched regions appear (−6.5 dB at 6.96 GHz and −8.4 dB at "
        "13.54 GHz). Three bands result: 3.42–6.13 GHz (56.7%), 7.63–13.23 GHz (53.7%) and a marginal band from "
        "13.95 GHz to beyond 15 GHz. The maximum directivity in the *φ* = 0° plane rises by 0.6 dB on average in "
        "the first band and by 2.1 dB in the third, and reaches 7.0 dBi at 13.9 GHz, at the lower edge of the third "
        "band, against 4.5 dBi for the antenna alone; it falls by 1.4 dB on average in the second band. The first "
        "band contains the 5G New Radio (NR) band n79 and the 5 GHz wireless LAN (WLAN) band, and the second "
        "contains the X band. The board acts as a dielectric and "
        "capacitive loading of the monopole and not as a reflector. Gain and efficiency are not evaluated.")
    p.keywords("5G, CPW-fed antenna, metasurface, octagonal monopole, parasitic patch array, tri-band antenna, "
               "WLAN, X band")
    # -- I --------------------------------------------------------------------------------------------------------
    p.heading("I. Introduction")
    p.body(
        "Compact, low-cost antennas that serve several standards at once are in steady demand, since the antenna is "
        "a basic block of every RF front end [1]. A present-day terminal may have to reach sub-6 GHz 5G new radio "
        "and 5 GHz WLAN, while sensing and satellite equipment works in the X and Ku bands [2]–[4]. Planar "
        "monopoles fed by a coplanar waveguide (CPW) suit such needs: the feed line and the ground planes lie on the "
        "same side of the substrate, no via is required, and the impedance bandwidth is large [5], [6]. Printed "
        "monopoles of triangular, jug, elliptical and javelin shape have been reported for multiband and "
        "ultra-wideband (UWB) "
        "operation, some with notches that avoid interference with neighbouring services [6]–[9].")
    p.body(
        "A printed monopole radiates on both sides of the board, so its gain remains modest. A metal reflector "
        "raises the gain only when it is about a quarter wavelength away, which makes the antenna bulky. Artificial "
        "magnetic conductors (AMC), frequency selective surfaces (FSS) and metasurfaces reflect the backward wave "
        "with an engineered phase and can be placed closer [10]. Sen *et al.* backed a UWB monopole with a split-ring "
        "metasurface and reported a gain rise of about 5.5 dB [11]. Al-Gburi *et al.* raised the simulated peak "
        "gain of a CPW-fed ring monopole from 6.7 to 11.5 dB with a 19 × 19 FSS and a total profile of 10 mm [12]. "
        "Hussain "
        "*et al.* reached 10.5 dBi with a 5 × 5 FSS 9 mm behind a CPW hexagonal patch [13], and Hammache *et al.* "
        "obtained 8.4 dBi with a 7 × 7 FSS at 20 mm [14]. A CPW-fed octagonal monopole over a 5 × 5 AMC achieved up "
        "to 11.5 dBi over 3.5–6.5 GHz [15]. Kundu and co-workers loaded printed UWB antennas with FSS layers for "
        "ground penetrating radar [16], [17], and a conformal FSS was used to obtain frequency-dependent directive "
        "radiation [18]. Rajalakshmi and Gunavathi placed a 2 × 2 array of hexagonal metamaterial cells behind the "
        "substrate of a cross-shaped patch and reported gains of about 6 and 10 dBi at 2.4 and 5 GHz [19].")
    p.body(
        "Most of these surfaces sit 9–20 mm from the antenna and are larger than the radiator, so the gain is paid "
        "for in volume. In the opposite limit, the surface is laid directly on the antenna. Zhu *et al.* placed a "
        "metasurface directly on a source antenna, with a total thickness of 0.05 wavelength, and found that it "
        "behaves like a dielectric substrate that tunes the antenna [20]; the same arrangement converts the "
        "polarisation [21]. The effect of a plain dielectric cover on a printed antenna is itself well "
        "established [22]. This paper examines that limit for a CPW monopole: a small patch array of the same "
        "footprint as the antenna is laid directly on it, where it lies in the reactive near field and cannot act "
        "as a reflector, and what it does to the match and to the radiation is evaluated.")
    p.body(
        "A compact CPW-fed octagonal monopole on FR-4 is designed, and a second FR-4 board carrying a 4 × 4 "
        "square-patch array on its outer face is placed on it without an air gap or a backing conductor. The antenna is "
        "simulated with and without the board, and the two cases are compared over 1–15 GHz. Section II describes "
        "the design and the analytical estimates, Section III discusses the simulated results and their "
        "limitations, and Section IV concludes the paper.")
    # -- II -------------------------------------------------------------------------------------------------------
    p.heading("II. Antenna Design and Analysis")
    p.subheading("A. Antenna Geometry")
    p.body(
        "The geometry of the antenna is shown in Fig. 1(a), and its dimensions are listed in Table I. The radiator "
        "is a regular octagon of circumradius *R* = 9 mm standing on one vertex. It is printed on an FR-4 substrate "
        "(*ε*_{r} = 4.3, tan *δ* = 0.025) of width *W*_{s} = 27 mm, length *L*_{s} = 30 mm and thickness "
        "*h*_{s} = 1.6 mm. The octagon is fed by a CPW line of width *W*_{f} = 3 mm, separated from the two coplanar "
        "ground planes by slots of *g* = 0.3 mm, which gives a 50 Ω line on this substrate [5]. The ground planes "
        "are *L*_{g} = 11 mm long; the left one is *W*_{g1} = 11.2 mm wide and the right one *W*_{g2} = 12.2 mm, so "
        "the feed line and the octagon are offset by 0.5 mm from the centre line of the board. The lower vertex of "
        "the octagon lies *p* = [[0.22]] mm above the ground edge. The back of the substrate carries no copper. Since "
        "the CPW grounds carry current and take part in the radiation, their length and the patch-to-ground gap "
        "mainly control the matching at the lower end of the band [23].")
    p.figure([FIG / "fig_geometry_antenna.png", FIG / "fig_geometry_metasurface.png"],
             "Top views of the proposed structure (CST Studio Suite model): (a) CPW-fed octagonal monopole, "
             "(b) 4 × 4 square-patch metasurface. The dimensions are listed in Table I.",
             width_in=1.62, sublabels=True, side_by_side=True)
    p.table("Dimensions of the Proposed Antenna and Metasurface (mm)", [
        ["Parameter", "*W*_{s}", "*L*_{s}", "*h*_{s}", "*R*", "*W*_{f}", "*g*"],
        ["Value", "27", "30", "1.6", "9", "3", "0.3"],
        ["Parameter", "*L*_{g}", "*W*_{g1}", "*W*_{g2}", "*p*", "*W*_{m}", "*L*_{m}"],
        ["Value", "11", "11.2", "12.2", "0.22", "27", "30"],
        ["Parameter", "*t*", "*W*_{p}", "*s*", "*a*", "", ""],
        ["Value", "1.6", "5", "0.5", "5.5", "", ""],
    ], [0.74, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44], header_rows=0, bold_first_col=True)
    p.body(
        "The lower edge of the operating band is estimated by replacing the octagon with a cylindrical monopole of "
        "the same height and the same surface area [23], [24]:")
    p.equation(r"f_L = \frac{7.2}{(l + r + p)\,k}\ \text{GHz}")
    p.equation(r"r = \frac{A}{2\pi l}")
    p.body(
        "where *l* = 2*R* = 18.0 mm is the height of the octagon, *A* = 2√2*R*^{2} = 229.1 mm^{2} its area, "
        "*r* = 2.03 mm the radius of the equivalent cylinder and *p* = 0.22 mm the gap to the ground, all taken in "
        "centimetres in (1); *k* = 1.15 is the empirical factor for an FR-4 substrate [23]. Equation (1) gives "
        "*f*_{L} ≈ 3.09 GHz, about 12% below the simulated lower edge of the antenna alone, 3.52 GHz "
        "(Section III). Equation (1) is used here only as a first check of the size of the radiator: it is an "
        "empirical estimate for a monopole above a large ground, whereas the CPW ground here is only 11 mm long.", cont=True)
    p.subheading("B. Metasurface Design")
    p.body(
        "The metasurface of Fig. 1(b) is a 4 × 4 array of square copper patches of side *W*_{p} = 5 mm and period "
        "*a* = 5.5 mm, so that adjacent patches are separated by *s* = 0.5 mm and the array is 21.5 mm across. It is "
        "printed on a 1.6 mm FR-4 board of width *W*_{m} and length *L*_{m}, the same footprint as the antenna, and "
        "has no backing conductor. The board is placed directly on the copper side of the antenna, with no air gap, "
        "as shown in "
        "Fig. 2. From top to bottom, the structure consists of the patches on the outer face, the metasurface "
        "substrate of thickness *t*, the octagon and the CPW feed at the interface between the two substrates, and "
        "the antenna substrate of thickness *h*_{s}. The radiator is thus enclosed between the two FR-4 layers, the "
        "patches lie *t* = 1.6 mm from it, and the total thickness is *h*_{s} + *t* = 3.2 mm.")
    p.figure(HERE / "cst_screenshots" / "stackup_schematic.png",
             "Side view of the proposed structure (schematic, not to scale).", width_in=3.4)
    p.body(
        "The added board loads the antenna in two ways. First, the octagon and the CPW line, which lie on an "
        "air–FR-4 boundary in the antenna alone, now have FR-4 on both sides. From the conformal-mapping "
        "expressions for a CPW between two dielectric layers of finite thickness [5], the effective permittivity of "
        "the feed line rises from 2.4 to 3.8, and its characteristic impedance falls from 50 Ω to 40 Ω; a slot of "
        "about 0.65 mm would be needed to restore 50 Ω under the cover. The cover therefore lowers the resonance "
        "frequencies of the radiator and, at the same time, changes the impedance of the line that feeds it.")
    p.body(
        "Second, the patch array adds a capacitive surface close to the radiator. Since it has no backing "
        "conductor, the array does not form the resonant circuit of a high-impedance surface [10]. At frequencies "
        "at which the patches are small compared with the wavelength, it behaves as a capacitive sheet [25], in "
        "which the narrow gaps between neighbouring patches provide the capacitance [26]")
    p.equation(r"C = \frac{W_p\,\varepsilon_0\,(\varepsilon_1 + \varepsilon_2)}{\pi}\cosh^{-1}\!\left(\frac{a}{s}\right)")
    p.body(
        "where *ε*_{1} and *ε*_{2} are the relative permittivities of the media on the two sides of the patches. The "
        "patches have FR-4 on one side and air on the other (*ε*_{1} = 4.3, *ε*_{2} = 1), so with the dimensions of "
        "Table I, (3) gives *C* ≈ 0.23 pF, a sheet reactance of 1/(*ωC*) ≈ 200 Ω at 3.42 GHz and 70 Ω at 10 GHz. "
        "This sheet is not a reflector for the antenna. The array has only 4 × 4 cells and is 0.25 free-space "
        "wavelength across at 3.42 GHz, and it lies 1.6 mm from the radiator, in its reactive near field. The "
        "patches therefore couple to the radiator through the metasurface substrate and act as a capacitive "
        "loading that changes the current distribution and the input impedance. Equation (3) is, moreover, a "
        "quasi-static estimate: it loses accuracy towards the upper end of the range, where the 5 mm patches are no "
        "longer small compared with the wavelength. The combined effect of the two loadings is therefore evaluated "
        "by full-wave simulation in Section III.", cont=True)
    p.subheading("C. Simulation Setup")
    p.body(
        "The structure is simulated in two stages with the frequency-domain solver of CST Studio Suite from 1 to "
        "15 GHz, with a waveguide port at the CPW feed. In stage 1 the octagonal antenna is simulated alone, and "
        "its ground and patch are tuned for impedance matching. In stage 2 the metasurface board is placed on the "
        "copper side of the antenna, with the patches on its outer face, and the complete structure is simulated "
        "again without retuning. In stage 2 the feed line, and therefore the port, lies at the interface between "
        "the two substrates. The board lies in the *xy* plane with the feed line along *y*, so that *θ* = 0° is "
        "the normal to the board on [[the patch side]]. The far-field quantity "
        "evaluated is the directivity, which does not include the dielectric and conductor losses or the "
        "mismatch.")
    # -- III ------------------------------------------------------------------------------------------------------
    p.heading("III. Results and Discussion")
    p.subheading("A. Reflection Coefficient")
    p.body(
        "The simulated reflection coefficients of the two stages are compared in Fig. 3 and summarised in Table II. "
        "Without the metasurface board, |*S*_{11}| falls below −10 dB at 3.52 GHz and remains below it up to "
        "15 GHz, the upper limit of the simulation, except from 5.21 to 5.79 GHz, where it rises to −9.8 dB, only "
        "0.2 dB above the limit. The lowest reflection coefficient is −36.6 dB at 12.44 GHz, and further "
        "resonances appear at 4.08 and 7.42 GHz.")
    p.figure(FIG / "fig_s11.png",
             "Simulated reflection coefficient of the antenna alone and with the metasurface board. The shaded "
             "regions are the −10 dB bands with the board.", width_in=3.4)
    p.body(
        "With the board, the structure has three −10 dB bands: band I from 3.42 to 6.13 GHz, band II from 7.63 to "
        "13.23 GHz and band III from 13.95 GHz to beyond 15 GHz. The fractional bandwidths (FBW) of bands I and II are "
        "56.7% and 53.7%. The lowest reflection coefficient is −27.8 dB at 5.26 GHz, and further resonances "
        "appear at 3.94, 9.04, 9.90 and 12.84 GHz. Between the bands, |*S*_{11}| rises to −6.5 dB at 6.96 GHz and "
        "to −8.4 dB at 13.54 GHz. These regions are not designed notches; they are the frequencies at which the "
        "loaded antenna is mismatched. In band III, |*S*_{11}| stays between −10 and −11.5 dB up to the simulation "
        "limit, so this band is marginal and its upper edge is not known.")
    p.body(
        "A comparison of the two curves shows what the board changes. Both the FR-4 layer over the radiator and "
        "the patches on it are added in stage 2, so the changes are the sum of the two effects of Section II-B and "
        "cannot be assigned to the patches alone. The lower band edge moves only from 3.52 to 3.42 GHz. Near "
        "5.3 GHz the match improves from −9.8 dB to −27.8 dB, which closes the gap of the antenna alone at "
        "5.21–5.79 GHz, and resonances appear at 9.04 and 9.90 GHz. The resonances of the antenna alone at 7.42 and "
        "12.44 GHz are not retained: with the board, |*S*_{11}| is −8.3 dB and −13.0 dB at these frequencies. "
        "Whether the resonances at 9.04 and 9.90 GHz are new, or are those of the antenna alone moved down by the "
        "dielectric cover, cannot be decided without the cover-only simulation.")
    p.body(
        "In total, the antenna alone is matched over 10.9 GHz of the 3.42–15 GHz range and the antenna with the "
        "board over 9.4 GHz. The board thus trades the almost continuous match of the antenna alone for three "
        "separate bands, of which the first is wider and better matched than the corresponding band of the antenna "
        "alone (3.52–5.21 GHz, 38.7%).")
    p.table("Simulated Performance of the Two Stages", [
        ["Stage", "−10 dB band (GHz)", "FBW (%)", "Lowest |*S*_{11}| (dB)", "Peak directivity (dBi)"],
        ["1: antenna alone", "3.52–5.21\n5.79 to >15", "38.7\n≥ 88.6", "−36.6 at 12.44 GHz", "5.2 at 13.1 GHz"],
        ["2: with metasurface board", "3.42–6.13\n7.63–13.23\n13.95 to >15", "56.7\n53.7\n≥ 7.2",
         "−27.8 at 5.26 GHz", "7.0 at 13.9 GHz"],
    ], [0.78, 0.82, 0.5, 0.68, 0.62], bold_first_col=True)
    p.subheading("B. Directivity")
    p.body(
        "The simulated directivity against frequency is shown in Fig. 4. The quantity plotted is the highest "
        "directivity found in the *φ* = 0° plane at each frequency. It is not the directivity in a fixed direction, "
        "and where it is low the main radiation lies outside this plane. Without the board, it varies smoothly and "
        "reaches its peak of 5.2 dBi at 13.1 GHz. With the board, the peak is 7.0 dBi at 13.9 GHz, at the lower "
        "edge of band III, where the antenna alone gives 4.5 dBi; at 13.1 GHz, on the other hand, the value with "
        "the board is 3.6 dBi.")
    p.figure(FIG / "fig_directivity.png",
             "Simulated directivity (maximum in the *φ* = 0° plane) of the antenna alone and with the metasurface "
             "board.", width_in=3.4)
    p.body(
        "The effect of the board differs from band to band. Averaged over band I, the directivity rises from 3.22 "
        "to 3.82 dBi, and over band III from 3.25 to 5.34 dBi. Over band II, however, it falls from 3.22 to "
        "1.85 dBi, and "
        "the directivity with the board is the lower one over 70% of this band. With the board the curve has sharp "
        "dips to −2.8 dBi at 7.5 GHz, −1.0 dBi at 9.6 GHz and −0.3 dBi at 12.0 GHz, where the antenna alone gives "
        "4.4, 2.5 and 3.5 dBi. The first dip lies between bands I and II, but the other two lie inside band II. "
        "Averaged over 3.42–15 GHz, the directivity is 3.46 dBi without the board and 2.95 dBi with it. Since the "
        "patches are in the near field of the radiator (Section II-B), they redistribute the current with "
        "frequency, and the result is not a uniform increase of directivity.")
    p.subheading("C. Radiation Pattern")
    p.body(
        "The simulated directivity patterns in the *φ* = 90° plane at 5.3 GHz, close to the best-matched frequency "
        "of band I, are shown in Fig. 5. Both patterns have two broad lobes, one around *θ* = 0° and one around "
        "*θ* = 180°, as expected of a planar monopole without a backing conductor. Without the board, the two "
        "lobes are almost equal; the larger one points to *θ* = 176° with a directivity of 3.56 dBi and a "
        "half-power beamwidth of 71.7°. With the board, the larger lobe points to *θ* = 2° with a directivity of "
        "3.88 dBi and a half-power beamwidth of 76.8°, and the opposite lobe is 1.3 dB lower. In this plane the "
        "board therefore makes the lobe on one side 1.3 dB stronger than the other and raises the directivity by "
        "0.32 dB, but the radiation remains two-sided. The maximum of Fig. 4 at this frequency, 4.3 dBi with the "
        "board, is higher than that of this cut, so the direction of maximum radiation is not in the plane of "
        "Fig. 5.")
    p.figure([FIG / "fig_pattern_without.png", FIG / "fig_pattern_with.png"],
             "Simulated directivity pattern in the *φ* = 90° plane at 5.3 GHz: (a) antenna alone, (b) with the "
             "metasurface board. The circle and the straight lines are the CST Studio Suite markers of the main "
             "lobe and its half-power width.", width_in=1.66, sublabels=True, side_by_side=True)
    p.subheading("D. Limitations")
    p.body(
        "Four limits of the present results should be kept in mind. First, only the directivity has been evaluated, "
        "in one plane. FR-4 is lossy (tan *δ* = 0.025), and with the board the radiator and its feed are embedded "
        "in it, so the realised gain will be lower than the directivity, increasingly so towards the upper end of "
        "the range. Second, the dielectric cover and the patches were added together; a simulation with a bare "
        "FR-4 cover is required to separate the two effects. Third, the feed line was not retuned for the cover, "
        "and band III is marginal and reaches the upper limit of the simulated range. Fourth, in a prototype the "
        "cover board must leave the end of the CPW line free for the connector, and any air or adhesive layer "
        "between the two boards will change the loading.")
    p.subheading("E. Comparison with Reported Works")
    p.body(
        "Table III compares the proposed antenna with reported printed antennas that use a reflector or a "
        "metamaterial layer. The total profile of the proposed structure is 3.2 mm (0.037*λ*_{0} at 3.42 GHz), "
        "lower than that of the FSS-backed designs [12]–[14], which place a reflector behind the antenna across a "
        "gap, and its metasurface is no larger than the antenna itself, whereas the FSS of [12] and [13] and the "
        "AMC of [15] are larger than their antennas. The design of [19] serves two narrow WLAN bands. This "
        "compactness has a "
        "price: the reflector-backed designs reach 8–11.5 dBi of gain, whereas the proposed surface is too small and "
        "too close to act as a reflector. For the proposed antenna the table gives the peak simulated directivity, "
        "which does not include the losses, whereas the other works report gain; the last column is therefore not "
        "a like-for-like comparison.")
    p.table("Comparison with Reported Antennas", [
        ["Ref.", "Antenna; added surface", "Size (mm)", "Gap (mm)", "Band (GHz)", "Peak gain or\ndirectivity\n(dBi)"],
        ["[12]", "CPW ring monopole; 19 × 19 FSS", "50 × 50; FSS 100 × 100", "10 (total)", "2.2–11.9", "11.3 (meas.)"],
        ["[13]", "CPW hexagon; 5 × 5 FSS", "32 × 25; FSS 50 × 50", "9", "3–18", "10.5"],
        ["[14]", "CPW hexagon; 7 × 7 FSS", "30 × 30", "20", "UWB", "8.4"],
        ["[15]", "CPW octagon; 5 × 5 AMC", "27 × 37; AMC 70 × 70", "–", "3.5–6.5", "11.5"],
        ["[19]", "Cross patch; 2 × 2 hexagonal metamaterial array", "20 × 25 (patch)", "–", "2.4, 5", "6, 10 (meas.)"],
        ["This work", "CPW octagon; 4 × 4 patch metasurface", "27 × 30", "0", "3.42–6.13\n7.63–13.23\n13.95 to >15",
         "7.0^{†}"],
    ], [0.4, 0.8, 0.62, 0.42, 0.62, 0.64],
        note="–: not available.  ^{†}Simulated directivity in the *φ* = 0° plane; gain not evaluated.")
    # -- IV -------------------------------------------------------------------------------------------------------
    p.heading("IV. Conclusion")
    p.body(
        "A compact CPW-fed octagonal monopole antenna loaded with a 4 × 4 square-patch metasurface has been "
        "studied by simulation. The structure has a footprint of 27 mm × 30 mm and a total thickness of 3.2 mm; the "
        "radiator lies between two FR-4 substrates and the patches are on the outer face, with no air gap and no "
        "backing conductor. It provides three bands with |*S*_{11}| ≤ −10 dB, 3.42–6.13 GHz, 7.63–13.23 GHz and a "
        "marginal band above 13.95 GHz, whereas the antenna alone is matched from 3.52 GHz upwards except for "
        "5.21–5.79 GHz. The metasurface board acts as a dielectric and capacitive loading of the radiator and not "
        "as a reflector: it improves the match near 5.3 GHz to −27.8 dB and raises the maximum directivity in the "
        "*φ* = 0° plane in the first and third bands, to 7.0 dBi at the lower edge of the third, but it introduces "
        "two mismatched "
        "regions and lowers the directivity over most of the second band. A control simulation with a bare FR-4 "
        "cover, a retuned feed line, the evaluation of the realised gain and efficiency, and the fabrication and "
        "measurement of a prototype are the next steps of this work.")
    p.references(REFS)
    p.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
