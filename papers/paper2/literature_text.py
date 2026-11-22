"""Literature review and comparison table of Paper 2.

Every number attributed to a cited paper below was read in that paper's abstract or full text (which of the two is
noted in references.py). Do not add a number from memory: check it in the source first.
"""


def review_mimo(c) -> str:
    return (
        "Four-port UWB antennas have been obtained on boards of 38–65 mm side, mostly by placing neighbouring "
        "elements at right angles, so that polarisation diversity supplies much of the isolation. Yin *et al.* "
        "placed CPW-fed elements perpendicularly on a 38 mm × 38 mm board and reported more than 17 dB of isolation "
        f"over 3–20 GHz {c('yin')}. Wu *et al.* reached more than 17 dB over 3.1–13.1 GHz on a 45 mm × 45 mm board "
        f"with a connected ground {c('wu')}, Zhang *et al.* added cross-shaped decoupling branches to a flexible CPW-fed "
        f"design and obtained more than 22 dB over 2.9–10.86 GHz {c('zhang')}, and Ahmad *et al.* reported more than "
        f"20 dB over 3–11 GHz with CPW-fed elements {c('ahmad')}. A uniplanar four-port array with a rejection band "
        f"has also been described {c('gomez')}. In all of these the envelope correlation coefficient is below 0.1.")


def review_metasurface(c) -> str:
    return (
        "A printed monopole radiates on both sides of its board, and a reflecting surface behind it can turn part "
        "of the backward radiation forwards. A plain conductor has to be about a quarter wavelength away, whereas "
        f"a surface with an engineered reflection phase can be closer {c('sievenpiper')}. Sen *et al.* placed a "
        f"split-ring surface behind a UWB monopole and reported a gain rise of about 5.5 dB {c('sen')}. For four-port "
        "antennas, Hasan *et al.* placed a copper-backed array of 10 × 10 split-ring cells 12 mm behind an "
        "80 mm × 80 mm antenna and raised the simulated realised gain from 5.4 to 8.3 dBi over 3.08–7.75 GHz, with "
        f"more than 15.5 dB of isolation {c('hasan')}; Sufian *et al.* combined a metasurface with slots and "
        f"shorting pins and reached more than 32 dB of isolation over 3.3–3.87 GHz {c('sufian')}; and Din *et al.* "
        f"placed a frequency selective surface (FSS) over a four-port antenna for 3.8–6 GHz {c('din')}. Over wider "
        f"bands, a reflector under a four-port antenna covering 2.08–10.4 GHz {c('mohanty')}, a split-ring "
        "artificial magnetic conductor (AMC) under a four-port antenna covering 2–12 GHz with a gain of up to "
        f"9.6 dBi {c('alekya')}, and FSS-backed four-port UWB antennas {c('nirmala', 'kumar')} have been reported. "
        "A wideband MIMO antenna with a reflecting surface is therefore not new. What is less often reported is "
        "how much a given surface contributes when it is compared, on the same model, with the antenna alone.")


def reflector_note(c) -> str:
    return (
        "The surfaces that raise the gain in the reported designs are backed by a conductor and spaced from the "
        f"antenna; in {c('hasan')}, for example, the surface is copper-backed and 12 mm behind the antenna.")


def comparison_text(c, table: str) -> str:
    return (
        f"Table {table} compares the antenna with reported four-port designs. The antennas without an added surface "
        f"occupy boards of 38–65 mm side and isolate their ports by more than 17 dB {c('yin', 'wu', 'zhang', 'ahmad')}; "
        f"those with a conductor-backed surface or an FSS reach gains of about 8–10 dBi "
        f"{c('hasan', 'alekya', 'kumar')}. The present antenna is larger, because its element was sized for a lower "
        "band edge below 2 GHz, and its elements are parallel and not orthogonal. Its entry gives the simulated "
        "directivity, which is not comparable with the gains of the other works.")


# (key, [ports; element | size (mm) | added surface; gap (mm) | band (GHz) | isolation (dB) | ECC | peak gain (dBi)])
# "–": not available (not stated in the abstract or full text that was read; see references.py).
COMPARISON_ROWS = [
    ("yin", ["4; CPW-fed monopoles, orthogonal", "38 × 38", "none", "3–20", "> 17", "< 0.08", "6.2"]),
    ("wu", ["4; microstrip-fed monopoles, orthogonal", "45 × 45", "none", "3.1–13.1", "> 17", "< 0.02",
            "7.3 (meas.)"]),
    ("zhang", ["4; CPW-fed monopoles, orthogonal", "65 × 65", "none", "2.9–10.86", "> 22", "< 0.01",
               "6.49 (meas.)"]),
    ("ahmad", ["4; CPW-fed monopoles, orthogonal", "60 × 60", "none", "3–11", "> 20", "< 0.02", "–"]),
    ("hasan", ["4; microstrip patches, orthogonal", "80 × 80", "10 × 10 split rings, copper-backed; 12",
               "3.08–7.75", "> 15.5", "< 0.004", "8.5 (meas.)"]),
    ("alekya", ["4; hexagonal monopoles", "60 × 60", "split-ring AMC, 80 × 80; –", "2–12", "> 25", "–", "9.6"]),
    ("kumar", ["4; slotted octagonal monopoles", "45 × 45", "FSS; –", "3.6–19.2", "–", "–", "≈ 9"]),
]
