"""Design facts of the four-port antenna (Paper 2). EDIT THIS FILE, then re-run build_paper2.py.

Every entry is `value` or `Unknown(guess, why)`. An Unknown is printed in the paper highlighted in yellow, so nothing
that has not been confirmed from the CST model can slip into the text unnoticed. Replace each Unknown with the value
read from the CST parameter list (a plain string or number) to clear the highlight.

Values marked "repo" come from the single-element stage of the project (GAP_STUDY.md, MIDSEM_STUDY_PACK.md).
Values marked "px" were measured on the CST screenshots (3.73 px/mm, about +/-0.3 mm) and are guesses.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Unknown:
    guess: str
    why: str


DESIGN = {
    # --- substrate (repo) ---------------------------------------------------------------------------------------
    "eps_r": "4.3",
    "tan_d": "0.025",
    "h_sub": "1.6",
    # --- element -------------------------------------------------------------------------------------------------
    "R": Unknown("15", "repo value. In the screenshot the lower-row patches measure 15.0 mm but the UPPER-ROW "
                       "patches measure about 14.0 mm: make the four elements identical, then confirm"),
    "W_f": "3",                                  # CPW strip width (repo)
    "g": "0.5",                                  # CPW slot width (repo)
    "L_g": Unknown("18", "repo value; the upper-row grounds look longer in the screenshot (>= 21.7 mm, px)"),
    "W_g": Unknown("23", "repo value; upper-row grounds measure about 21.0 mm (px)"),
    "p": Unknown("0.73", "repo value; lower row measures about 0.5 mm and the upper row about 1.6 mm (px)"),
    # --- four-port layout ----------------------------------------------------------------------------------------
    "board": Unknown("100 mm × 100", "px: bounding box about 105 × 100 mm with a stepped outline (the two halves are "
                                  "shifted sideways by about 4.8 mm). Rebuild the substrate as one rectangle"),
    "pitch": Unknown("50", "px: feed-to-feed spacing within a row"),
    "d_face": Unknown("2.4", "px: flat-edge-to-flat-edge spacing of the two patches that face each other"),
    "ground_statement": Unknown(
        "the coplanar grounds of the two rows are not connected to each other",
        "px: upper-row grounds are 4 mm apart, lower-row grounds touch or are split by a hairline, and the two rows "
        "are not connected. State what the model really has; a common ground is what reviewers expect"),
    "port_map": Unknown("ports 1 and 2 feed the lower row and ports 3 and 4 the upper row",
                        "the screenshots do not show the port numbers"),
    # --- metasurface ---------------------------------------------------------------------------------------------
    "r_out": Unknown("7.5", "repo 'given' value (outer radius of the outer ring); px confirms a 15 mm ring"),
    "r_in": Unknown("5.5", "repo 'given' value (outer radius of the inner ring); px confirms an 11 mm ring"),
    "w_ring": Unknown("0.5", "repo 'given' strip width"),
    "split": Unknown("0.25", "px on the earlier single-element screenshot; not resolvable in the MIMO screenshot. "
                             "If the rings have no split, say 'closed rings' instead of 'split rings'"),
    "pitch_x": Unknown("16.9", "px"),
    "pitch_y": Unknown("18.3", "px"),
    "ms_board": Unknown("105 mm × 100", "px: at least as large as the antenna board"),
    "ms_ground": Unknown(
        "has no copper on its rear face",
        "NOT KNOWN. The single-element metasurface had a full copper ground; the unchanged S11 of the MIMO model "
        "suggests either no ground or a gap of about 30 mm. This decides what the surface physically is"),
    "gap": Unknown("h", "NOT KNOWN: the air gap between the antenna board and the metasurface board (repo mentions "
                        "2, 3.9 and 30 mm at different stages)"),
    # --- simulation ----------------------------------------------------------------------------------------------
    "solver": Unknown("frequency-domain", "repo: the single-element stage used the frequency-domain solver"),
    "cst_version": Unknown("2019", "repo"),
    "port1_position": Unknown("a lower-row element", "its S11 dips track the single-element design, which the "
                                                     "lower row matches"),
    "theta0_side": Unknown("the side of the antenna board away from the metasurface",
                           "the pattern with the metasurface peaks at theta = 6 deg; confirm the axes in CST"),
}


def guess(key: str) -> float:
    """The numeric value of a design fact (confirmed or guessed), for derived quantities."""
    item = DESIGN[key]
    return float(item.guess if isinstance(item, Unknown) else item)


def value(key: str) -> str:
    """The text to print for a design fact; an unconfirmed one is wrapped in [[ ]] (yellow highlight)."""
    item = DESIGN[key]
    return f"[[{item.guess}]]" if isinstance(item, Unknown) else str(item)


def open_items() -> list[tuple[str, Unknown]]:
    return [(key, item) for key, item in DESIGN.items() if isinstance(item, Unknown)]
