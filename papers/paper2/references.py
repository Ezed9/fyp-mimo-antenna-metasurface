"""Reference list of Paper 2 (IEEE style). Keys are cited from the text; numbering follows the order of first use.

Every entry with a DOI was checked against its Crossref record (authors, title, journal, volume, issue, pages, year).
What was read of each paper is noted where it matters: "full text" or "abstract only". Claims made about a paper in
literature_text.py are limited to what was read.
"""

REFS = {
    "fcc": "Federal Communications Commission, “Revision of Part 15 of the Commission’s Rules Regarding "
           "Ultra-Wideband Transmission Systems,” First Report and Order, ET Docket 98-153, FCC 02-48, Apr. 2002.",
    "sharawi_apm": "M. S. Sharawi, “Printed multi-band MIMO antenna systems and their performance metrics,” *IEEE "
                   "Antennas Propag. Mag.*, vol. 55, no. 5, pp. 218–232, Oct. 2013, doi: 10.1109/MAP.2013.6735522.",
    "simons": "R. N. Simons, *Coplanar Waveguide Circuits, Components, and Systems*. New York, NY, USA: Wiley, 2001, "
              "doi: 10.1002/0471224758.",
    "ray": "K. P. Ray, “Design aspects of printed monopole antennas for ultra-wide band applications,” *Int. J. "
           "Antennas Propag.*, vol. 2008, Art. no. 713858, 2008, doi: 10.1155/2008/713858.",
    "pendry": "J. B. Pendry, A. J. Holden, D. J. Robbins, and W. J. Stewart, “Magnetism from conductors and enhanced "
              "nonlinear phenomena,” *IEEE Trans. Microw. Theory Techn.*, vol. 47, no. 11, pp. 2075–2084, Nov. 1999, "
              "doi: 10.1109/22.798002.",
    "sievenpiper": "D. Sievenpiper, L. Zhang, R. F. J. Broas, N. G. Alexópolous, and E. Yablonovitch, “High-impedance "
                   "electromagnetic surfaces with a forbidden frequency band,” *IEEE Trans. Microw. Theory Techn.*, "
                   "vol. 47, no. 11, pp. 2059–2074, Nov. 1999, doi: 10.1109/22.798001.",
    "blanch": "S. Blanch, J. Romeu, and I. Corbella, “Exact representation of antenna system diversity performance "
              "from input parameter description,” *Electron. Lett.*, vol. 39, no. 9, pp. 705–707, May 2003, "
              "doi: 10.1049/el:20030495.",
    "dg": "P.-S. Kildal and K. Rosengren, “Correlation and capacity of MIMO systems and mutual coupling, radiation "
          "efficiency, and diversity gain of their antennas: Simulations and measurements in a reverberation "
          "chamber,” *IEEE Commun. Mag.*, vol. 42, no. 12, pp. 104–112, Dec. 2004, doi: 10.1109/MCOM.2004.1367562.",
    "hallbjorner": "P. Hallbjörner, “The significance of radiation efficiencies when using S-parameters to calculate "
                   "the received signal correlation from two antennas,” *IEEE Antennas Wireless Propag. Lett.*, "
                   "vol. 4, pp. 97–99, 2005, doi: 10.1109/LAWP.2005.845913.",
    "sharawi_misuse": "M. S. Sharawi, “Current misuses and future prospects for printed multiple-input, "
                      "multiple-output antenna systems,” *IEEE Antennas Propag. Mag.*, vol. 59, no. 2, pp. 162–170, "
                      "Apr. 2017, doi: 10.1109/MAP.2017.2658346.",
    "manteghi": "M. Manteghi and Y. Rahmat-Samii, “Multiport characteristics of a wide-band cavity backed annular "
                "patch antenna for multipolarization operations,” *IEEE Trans. Antennas Propag.*, vol. 53, no. 1, "
                "pp. 466–474, Jan. 2005, doi: 10.1109/TAP.2004.838794.",
    "ccl": "H. Shin and J. H. Lee, “Capacity of multiple-antenna fading channels: Spatial fading correlation, double "
           "scattering, and keyhole,” *IEEE Trans. Inf. Theory*, vol. 49, no. 10, pp. 2636–2647, Oct. 2003, "
           "doi: 10.1109/TIT.2003.817439.",
    "vaughan": "R. G. Vaughan and J. B. Andersen, “Antenna diversity in mobile communications,” *IEEE Trans. Veh. "
               "Technol.*, vol. 36, no. 4, pp. 149–172, Nov. 1987, doi: 10.1109/T-VT.1987.24115.",
    # --- four-port UWB MIMO antennas without an added surface ---------------------------------------------------
    # full text
    "yin": "W. Yin, S. Chen, J. Chang, C. Li, and S. K. Khamas, “CPW fed compact UWB 4-element MIMO antenna with high "
           "isolation,” *Sensors*, vol. 21, no. 8, Art. no. 2688, Apr. 2021, doi: 10.3390/s21082688.",
    # full text
    "wu": "A. Wu, M. Zhao, P. Zhang, and Z. Zhang, “A compact four-port MIMO antenna for UWB applications,” "
          "*Sensors*, vol. 22, no. 15, Art. no. 5788, Aug. 2022, doi: 10.3390/s22155788.",
    # full text
    "zhang": "J. Zhang, C. Du, and R. Wang, “Design of a four-port flexible UWB-MIMO antenna with high isolation for "
             "wearable and IoT applications,” *Micromachines*, vol. 13, no. 12, Art. no. 2141, Dec. 2022, "
             "doi: 10.3390/mi13122141.",
    # abstract only
    "ahmad": "S. Ahmad, S. Khan, B. Manzoor, M. Soruri, M. Alibakhshikenari, M. Dalarsson, and F. Falcone, “A compact "
             "CPW-fed ultra-wideband multi-input-multi-output (MIMO) antenna for wireless communication networks,” "
             "*IEEE Access*, vol. 10, pp. 25278–25289, 2022, doi: 10.1109/ACCESS.2022.3155762.",
    # abstract only
    "gomez": "R. Gomez-Villanueva and H. Jardon-Aguilar, “Compact UWB uniplanar four-port MIMO antenna array with "
             "rejecting band,” *IEEE Antennas Wireless Propag. Lett.*, vol. 18, no. 12, pp. 2543–2547, Dec. 2019, "
             "doi: 10.1109/LAWP.2019.2942827.",
    # --- antennas with a metasurface, FSS, AMC or reflector -----------------------------------------------------
    # abstract only
    "sen": "G. Sen, A. Banerjee, M. Kumar, and S. Das, “An ultra-wideband monopole antenna with a gain enhanced "
           "performance using a novel split-ring meta-surface reflector,” *Microw. Opt. Technol. Lett.*, vol. 59, "
           "no. 6, pp. 1296–1300, Jun. 2017, doi: 10.1002/mop.30527.",
    # full text
    "hasan": "M. M. Hasan, M. T. Islam, M. Samsuzzaman, M. H. Baharuddin, M. S. Soliman, A. Alzamil, "
             "I. I. M. Abu Sulayman, and M. S. Islam, “Gain and isolation enhancement of a wideband MIMO antenna "
             "using metasurface for 5G sub-6 GHz communication systems,” *Sci. Rep.*, vol. 12, no. 1, Art. no. 9433, "
             "Jun. 2022, doi: 10.1038/s41598-022-13522-5.",
    # abstract only
    "sufian": "M. A. Sufian, N. Hussain, H. Askari, S. G. Park, K. S. Shin, and N. Kim, “Isolation enhancement of a "
              "metasurface-based MIMO antenna using slots and shorting pins,” *IEEE Access*, vol. 9, "
              "pp. 73533–73543, 2021, doi: 10.1109/ACCESS.2021.3079965.",
    # abstract only
    "din": "I. U. Din, M. Alibakhshikenari, B. S. Virdee, S. Ullah, S. Ullah, M. R. Akram, S. M. Ali, P. Livreri, "
           "and E. Limiti, “High performance antenna system in MIMO configuration for 5G wireless communications "
           "over sub-6 GHz spectrum,” *Radio Sci.*, vol. 58, no. 10, Art. no. e2023RS007726, Oct. 2023, "
           "doi: 10.1029/2023RS007726.",
    # abstract snippet only
    "mohanty": "A. Mohanty and S. Sahu, “4-port UWB MIMO antenna with bluetooth-LTE-WiMax band-rejection and "
               "vias-MCP loaded reflector with improved performance,” *AEU – Int. J. Electron. Commun.*, vol. 144, "
               "Art. no. 154065, Feb. 2022, doi: 10.1016/j.aeue.2021.154065.",
    # abstract only
    "alekya": "B. Alekya, N. A. Murugan, and B. T. P. Madhav, “Artificial magnetic conductor-integrated high-gain "
              "quad-port hexagonal antenna for conformal ultra-wideband applications,” *ETRI J.*, vol. 48, no. 4, "
              "pp. 604–619, Aug. 2026, doi: 10.4218/etrij.2025-0252.",
    # abstract only; check the order of the authors' initials against the PDF
    "nirmala": "M. Nirmala and N. Deepika Rani, “A spatially selective and electromagnetically tailored low-profile "
               "high-gain notched UWB MIMO antenna for 5G and ultra-wideband wireless systems,” *Franklin Open*, "
               "vol. 16, Art. no. 100687, Sep. 2026, doi: 10.1016/j.fraope.2026.100687.",
    # abstract only
    "kumar": "A. Kumar, K. Garg, and P. Sharma, “Performance enhancement of a slotted octagonal MIMO antenna using "
             "frequency selective surface for UWB applications,” *Phys. Scr.*, vol. 101, no. 43, Art. no. 435513, "
             "Oct. 2026, doi: 10.1088/1402-4896/aeb73c.",
}
