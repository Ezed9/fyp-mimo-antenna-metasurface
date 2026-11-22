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
    "R_lower": "15",                             # CST parameter list (authors): patch radii 14, 14, 15, 15.
    "R_upper": "14",                             # Kept as it is, without a stated reason (authors' decision).
    "W_f": "3",                                  # CPW strip width (repo)
    "g": "0.3",                                  # CPW slot width (authors: "feed gap 0.3 mm" is the slot)
    "L_g": "18",                                 # CST: ground from y = -25 to -7 mm
    "W_g": Unknown("23", "repo value; upper-row grounds measure about 21 mm on the screenshot"),
    "p_lower": Unknown("0.73", "follows from R = 15 mm with the patch centre 8 mm above the element centre and the "
                               "ground edge at -7 mm (repo); about 0.5 mm on the screenshot"),
    "p_upper": Unknown("1.69", "follows from R = 14 mm on the same patch centre; about 1.6 mm on the screenshot"),
    # --- four-port layout ----------------------------------------------------------------------------------------
    "board": "105.5 mm × 100.5",                 # CST: x from -30.5 to 75 mm, y from -25 to 75.5 mm
    "board_step": Unknown("5.5", "the lower half starts at x = -25 mm (the single-element board) and the outline at "
                                 "-30.5 mm, so the upper half is displaced by 5.5 mm; 4.8 mm on the screenshot"),
    "pitch": Unknown("50", "px: feed-to-feed spacing within a row (the single-element board is 50 mm wide)"),
    "d_face": Unknown("2.4", "px: flat-edge-to-flat-edge spacing of the two patches that face each other"),
    "ground_statement": Unknown(
        "the coplanar grounds of the two rows are not connected to each other",
        "px: upper-row grounds are 4 mm apart, lower-row grounds touch or are split by a hairline, and the two rows "
        "are not connected. State what the model really has; a common ground is what reviewers expect"),
    # authors: port 1 bottom left, port 2 bottom right, port 3 top left, port 4 top right
    "port_map": "ports 1 and 2 feed the left and right elements of the lower row and ports 3 and 4 those of the "
                "upper row",
    # --- metasurface (CST parameter list, authors) -----------------------------------------------------------------
    "r_out": "7.5",                              # outer ring 7.0-7.5 mm
    "r_in": "5.5",                               # inner ring 5.0-5.5 mm
    "w_ring": "0.5",
    "split_out": "0.4",
    "split_in": "0.3",
    "pitch_x": "17",                             # centre to centre along the rows of six
    "pitch_y": Unknown("18.5", "px, scaled on the confirmed 17 mm: 18.2-18.5 mm along the columns of five"),
    "ms_board": Unknown("105.5 mm × 100.5", "px: at least as large as the antenna board"),
    "ms_ground": "has no copper on its rear face",   # authors
    "gap": "4.5",                                # authors
    # --- simulation ----------------------------------------------------------------------------------------------
    "solver": "frequency-domain",                # authors
    "cst_version": Unknown("2019", "repo"),
    "port1_position": "the lower-left element",
    "theta0_side": Unknown("the copper side of the antenna board, away from the metasurface",
                           "the pattern with the metasurface peaks at theta = 6 deg; confirm the axes in CST"),
}


MS_GROUNDED = False        # the metasurface board has no backing conductor (authors); set True if that changes


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
