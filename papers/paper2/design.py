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
    "W_g_lower": Unknown("23.2", "authors: lower-row ground from x = -25 to -1.5 mm. With the 3 mm strip and the "
                                 "0.3 mm slot the ground edge is at -1.8 mm, i.e. 23.2 mm wide; if the copper really "
                                 "ends at -1.5 mm there is no slot. Read the exact x of the ground edge"),
    "W_g_upper": "21.5",                         # authors: upper-row ground from x = 48.5 to 70 mm
    "p_lower": Unknown("0.73", "follows from R = 15 mm with the patch centre 8 mm above the element centre and the "
                               "ground edge at -7 mm (repo); about 0.5 mm on the screenshot"),
    "p_upper": Unknown("1.69", "follows from R = 14 mm on the same patch centre; about 1.6 mm on the screenshot"),
    # --- four-port layout ----------------------------------------------------------------------------------------
    "board": "105.5 mm × 100.5",                 # CST: x from -30.5 to 75 mm, y from -25 to 75.5 mm
    "board_step": Unknown("about 5", "lower half x = -25 to 75 mm (two 50 mm tiles); the outline starts at -30.5 mm "
                                     "and the upper-row ground ends at 70 mm, so the upper half is displaced by "
                                     "5-5.5 mm; 4.8 mm on the screenshot"),
    "feed_offset": Unknown("3.3", "upper-right feed axis at x = 48.5 - 0.3 - 1.5 = 46.7 mm against 50 mm in the "
                                  "lower row; 2.9 mm on the screenshot"),
    "pitch": "50",                               # lower row: two 50 mm tiles from x = -25 to 75 mm (authors)
    "d_face": Unknown("2.4", "px: flat-edge-to-flat-edge spacing of the two patches that face each other"),
    "ground_statement": Unknown(
        "the adjacent grounds of the two lower-row elements meet and form one conductor, those of the upper row are "
        "about 3.4 mm apart, and the grounds of the two rows are not connected to each other",
        "derived: lower-row grounds both reach the tile edge at x = 25 mm (on the screenshot they touch or are split "
        "by a hairline); upper-row grounds are 21.5 mm wide, which leaves 3.4 mm between neighbours (4 mm on the "
        "screenshot). A common ground for all four ports is what reviewers expect"),
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
    "ms_board": "105.5 mm × 100.5",              # authors: same as the antenna board
    "ms_ground": "has no copper on its rear face",   # authors
    "gap": "4.5",                                # authors
    # --- simulation ----------------------------------------------------------------------------------------------
    "solver": "frequency-domain",                # authors
    "cst_version": "2019",                       # authors
    "port1_position": "the lower-left element",
    "theta0_side": Unknown("the copper side of the antenna board, away from the metasurface",
                           "guessed from the pattern with the metasurface, which peaks at theta = 6 deg. To confirm: "
                           "read the z-coordinates of the metasurface board in CST. If they are lower (more "
                           "negative) than those of the antenna board, this text is right"),
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
