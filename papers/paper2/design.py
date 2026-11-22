"""Design facts of the antenna of Paper 2, as printed in the paper. Edit here, then re-run build_paper2.py.

Source of each value:
  authors  given by the authors from the CST parameter list
  repo     documented single-element design of the project (GAP_STUDY.md, MIDSEM_STUDY_PACK.md)
  derived  follows arithmetically from authors/repo values
  view     measured on the CST top-view screenshots (3.7 px/mm, about +/-0.3 mm); printed with "about"
"""
from __future__ import annotations

DESIGN = {
    # substrate
    "eps_r": "4.3",            # repo
    "tan_d": "0.025",          # repo
    "h_sub": "1.6",            # repo
    # element of the lower row (ports 1 and 2)
    "R": "15",                 # authors: patch radii 14, 14, 15, 15; the lower row is 15
    "R_upper": "14",           # authors
    "W_f": "3",                # repo: CPW strip width
    "g": "0.3",                # authors: CPW slot ("feed gap 0.3 mm")
    "L_g": "18",               # authors: ground from y = -25 to -7 mm
    "W_g": "23.2",             # derived: ground from x = -25 mm to the slot edge at -1.8 mm
    "p": "0.73",               # repo/derived: patch centre 8 mm above the element centre, ground edge at -7 mm
    # layout
    "board_x": "105.5",        # authors: x from -30.5 to 75 mm
    "board_y": "100.5",        # authors: y from -25 to 75.5 mm
    "pitch": "50",             # derived: lower row = two 50 mm tiles from x = -25 to 75 mm
    "d_face": "2.4",           # view
    "board_step": "5",         # derived: outline starts at -30.5 mm, upper-row ground ends at 70 mm
    # metasurface
    "r_out": "7.5",            # authors: outer ring 7.0-7.5 mm
    "r_in": "5.5",             # authors: inner ring 5.0-5.5 mm
    "w_ring": "0.5",           # authors
    "split_out": "0.4",        # authors
    "split_in": "0.3",         # authors
    "pitch_x": "17",           # authors: centre to centre along the rows of six
    "pitch_y": "18.5",         # view, scaled on the 17 mm pitch
    "gap": "4.5",              # authors
    # simulation
    "cst_version": "2019",     # authors
    "solver": "frequency-domain",   # authors
}

# Printed without a highlight, but not read from the CST model by anyone: check them before submission.
VERIFY = {
    "W_g": "lower-row ground width 23.2 mm (assumes the ground edge at x = -1.8 mm, i.e. a 0.3 mm slot)",
    "p": "gap between the patch and the ground edge, 0.73 mm (from the single-element design)",
    "d_face": "spacing of the facing patches of the two rows, about 2.4 mm (measured on the screenshot)",
    "board_step": "sideways displacement of the upper half of the board, about 5 mm",
    "pitch_y": "ring-cell pitch along the columns, about 18.5 mm (measured on the screenshot)",
    "common ground": "that the grounds of elements 1 and 2 touch at x = 25 mm and form one conductor",
}


def value(key: str) -> str:
    return DESIGN[key]


def number(key: str) -> float:
    return float(DESIGN[key])
