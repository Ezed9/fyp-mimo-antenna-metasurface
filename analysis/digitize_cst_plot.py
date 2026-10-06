# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "pillow>=10"]
# ///
"""Digitise a CST 1D result plot (red curve, solid frame, dotted grid) from a screenshot.

CST draws a 1D result as a red polyline inside a solid dark frame with dotted gridlines. This finds the frame and the
gridlines, maps pixels to axis values from the axis limits printed at the frame edges (one straight-line fit through
every gridline, so the scale is sub-pixel), and reads the red curve inside the frame (the legend is ignored):

* vertices (--every STEP or --at F1 F2 ...): CST joins its frequency samples with straight lines. When the sample
  frequencies are known (e.g. farfield monitors every 0.1 GHz), every segment between two samples is fitted with a
  line, and each sample value is taken from the fits of the two segments that meet there (their disagreement is
  reported, as a check that the samples really sit there).
* dense (--step STEP, the default): the red pixels of every pixel column are averaged, and the curve is resampled
  every STEP.

Better than any screenshot: export the curve from CST (Post-Processing → Import/Export → Plot Data (ASCII)).

usage (from the repo root):
  uv run analysis/digitize_cst_plot.py figures/cst_single_ms_directivity.jpg --x 1 6 --y -2 9 --every 0.1
  uv run analysis/digitize_cst_plot.py figures/cst_single_final_directivity.png --x 0 18 --y -4 5 --range 1 6 \
      --step 0.05 --check /tmp/check.png
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

RED_MIN = 0.15   # a curve pixel: (R − max(G, B)) / 255 above this
EDGE_PX = 4      # columns this close to a vertex are left out of the segment fits


@dataclass
class Plot:
    """A CST plot screenshot: pixel ↔ value maps and the red curve (column centroids)."""
    path: Path
    frame: tuple[int, int, int, int]   # left, right, top, bottom pixel of the frame lines
    ax: np.ndarray                     # pixel x = ax[0] · value + ax[1]
    ay: np.ndarray                     # pixel y = ay[0] · value + ay[1]
    grid_resid_px: float               # worst gridline misfit of the two scale fits
    cx: np.ndarray                     # curve: x value of each pixel column that holds red
    cy: np.ndarray                     # curve: y value (red-weighted row centroid) of that column

    def px(self, x, y):
        return self.ax[0] * np.asarray(x) + self.ax[1], self.ay[0] * np.asarray(y) + self.ay[1]

    @property
    def y_per_px(self) -> float:
        return 1 / abs(self.ay[0])

    @property
    def x_per_px(self) -> float:
        return 1 / abs(self.ax[0])


def _weights(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(float)
    red = np.clip((rgb[..., 0] - np.maximum(rgb[..., 1], rgb[..., 2])) / 255, 0, 1)
    dark = np.clip((200 - rgb.mean(axis=2)) / 200, 0, 1) * (red < 0.2)
    return red, dark


def _frame(profile: np.ndarray) -> tuple[int, int]:
    """First and last solid line of a darkness profile: the frame (works when JPEG blurs a line over two pixels)."""
    s = np.convolve(profile, np.ones(3), "same")
    strong = np.where(s >= 0.7 * s.max())[0]
    runs = np.split(strong, np.where(np.diff(strong) > 1)[0] + 1)
    return int(runs[0][np.argmax(profile[runs[0]])]), int(runs[-1][np.argmax(profile[runs[-1]])])


def _centroids(profile: np.ndarray, threshold: float) -> list[float]:
    """Weighted centre of every run of profile entries above threshold (one per frame line or gridline)."""
    idx = np.where(profile > threshold)[0]
    out = []
    for run in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):
        if len(run):
            lo, hi = max(run[0] - 1, 0), run[-1] + 2
            w = profile[lo:hi]
            out.append(float((np.arange(lo, hi) * w).sum() / w.sum()))
    return out


def _scale(lines: list[float], v_first: float, v_last: float) -> tuple[np.ndarray, float]:
    """Fit pixel = a·value + b through the frame lines (first/last) and the gridlines between them.

    The gridlines are equally spaced, so each one's value is its position rounded to the grid step, which also
    copes with a gridline hidden behind the curve.
    """
    lines = sorted(lines)
    first, last = lines[0], lines[-1]
    n = max(1, round((last - first) / float(np.median(np.diff(lines)))))
    step = (v_last - v_first) / n
    vals = [v_first + round((p - first) / (last - first) * n) * step for p in lines]
    a = np.polyfit(vals, lines, 1)
    return a, float(np.abs(np.polyval(a, vals) - lines).max())


def read_plot(path: Path, x: tuple[float, float], y: tuple[float, float]) -> Plot:
    """x = (value at the left frame, value at the right frame); y = (value at the bottom, value at the top)."""
    red, dark = _weights(path)
    t, b = _frame(dark.sum(1))
    left, right = _frame(dark[t:b + 1].sum(0))
    row_prof = dark[:, left + 3:right - 2].sum(1)
    col_prof = dark[t + 3:b - 2, :].sum(0)
    ylines = [c for c in _centroids(row_prof, 0.08 * (right - left)) if t - 2 <= c <= b + 2]
    xlines = [c for c in _centroids(col_prof, 0.08 * (b - t)) if left - 2 <= c <= right + 2]
    ay, ry = _scale(ylines, y[1], y[0])     # top line = y max
    ax, rx = _scale(xlines, x[0], x[1])
    # red curve: weighted row centroid of every column inside the frame
    sub = red[t + 1:b, left + 1:right]
    w = np.where(sub > RED_MIN, sub, 0.0)
    have = w.sum(0) > 0.5
    rows_idx = np.arange(t + 1, b)[:, None]
    cy_px = (w * rows_idx).sum(0)[have] / w.sum(0)[have]
    cx_px = np.arange(left + 1, right)[have]
    cx = (cx_px - ax[1]) / ax[0]
    cy = (cy_px - ay[1]) / ay[0]
    return Plot(path, (left, right, t, b), ax, ay, max(rx, ry), cx, cy)


def _line_fit(p: Plot, a: float, b: float) -> np.ndarray | None:
    m = p.x_per_px * EDGE_PX
    sel = (p.cx > a + m) & (p.cx < b - m)
    f, v = p.cx[sel], p.cy[sel]
    if len(f) < 3:
        return None
    keep = np.ones(len(f), bool)
    for _ in range(2):  # drop the odd column spoilt by a gridline crossing or JPEG ringing
        fit = np.polyfit(f[keep], v[keep], 1)
        res = v - np.polyval(fit, f)
        keep = np.abs(res) < 3 * max(np.std(res[keep]), 0.3 * p.y_per_px)
    return np.polyfit(f[keep], v[keep], 1)


def vertices(p: Plot, at: list[float]) -> tuple[np.ndarray, float]:
    """Values at the sample frequencies `at` (the polyline's corners) and the worst two-sided disagreement (px)."""
    ends: list[list[float]] = [[] for _ in at]
    for k, (a, b) in enumerate(zip(at[:-1], at[1:])):
        fit = _line_fit(p, a, b)
        if fit is None:
            raise ValueError(f"too few curve columns between {a} and {b}: is a sample missing there?")
        ends[k].append(float(np.polyval(fit, a)))
        ends[k + 1].append(float(np.polyval(fit, b)))
    worst = max((max(e) - min(e)) / p.y_per_px for e in ends if len(e) > 1)
    return np.array([np.mean(e) for e in ends]), worst


def dense(p: Plot, lo: float, hi: float, step: float) -> tuple[np.ndarray, np.ndarray]:
    """The column-centroid curve resampled every `step` from lo to hi.

    The first/last two columns of the curve hold its anti-aliased line caps; points beyond them are extrapolated
    from the next eight columns.
    """
    cx, cy = p.cx[2:-2], p.cy[2:-2]
    f = np.round(np.arange(lo, hi + step / 2, step), 6)
    v = np.interp(f, cx, cy)
    for out, k in ((f < cx[0], slice(0, 8)), (f > cx[-1], slice(-8, None))):
        if out.any():
            v[out] = np.polyval(np.polyfit(cx[k], cy[k], 1), f[out])
    return f, v


def check_image(p: Plot, f: np.ndarray, v: np.ndarray, out: Path) -> None:
    """The screenshot with the digitised points drawn on it (blue rings), to check the result by eye."""
    im = Image.open(p.path).convert("RGB")
    draw = ImageDraw.Draw(im)
    px, py = p.px(f, v)
    for x, y in zip(px, py):
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], outline=(20, 90, 220), width=1)
    im.save(out)


def write_csv(out: Path, f: np.ndarray, v: np.ndarray, column: str, notes: list[str]) -> None:
    lines = [f"# {n}" for n in notes] + [f"f_GHz,{column}"] + [f"{a:.3f},{b:.3f}" for a, b in zip(f, v)]
    out.write_text("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("image", type=Path)
    ap.add_argument("--x", nargs=2, type=float, required=True, metavar=("LEFT", "RIGHT"),
                    help="axis values at the left and right frame lines")
    ap.add_argument("--y", nargs=2, type=float, required=True, metavar=("BOTTOM", "TOP"),
                    help="axis values at the bottom and top frame lines")
    ap.add_argument("--range", nargs=2, type=float, metavar=("LO", "HI"), help="x range to read (default: all)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--every", type=float, help="polyline corners every EVERY from LO to HI (segment fits)")
    g.add_argument("--at", nargs="+", type=float, help="polyline corners at these x values (segment fits)")
    g.add_argument("--step", type=float, default=0.05, help="dense resampling step (default 0.05)")
    ap.add_argument("--column", default="value", help="CSV column name for the y values")
    ap.add_argument("--out", type=Path, help="CSV to write (default: print)")
    ap.add_argument("--check", type=Path, help="write the screenshot with the digitised points on it")
    a = ap.parse_args()

    p = read_plot(a.image, tuple(a.x), tuple(a.y))
    lo, hi = a.range or (round(p.cx[0], 2), round(p.cx[-1], 2))
    notes = [f"Digitised from {a.image.as_posix()} with analysis/digitize_cst_plot.py",
             f"axes: x {a.x[0]:g}..{a.x[1]:g}, y {a.y[0]:g}..{a.y[1]:g} at the frame; gridline misfit "
             f"{p.grid_resid_px:.2f} px; 1 px = {p.x_per_px:.4f} in x, {p.y_per_px:.4f} in y"]
    if a.every or a.at:
        at = list(np.round(np.arange(lo, hi + a.every / 2, a.every), 6)) if a.every else a.at
        v, worst = vertices(p, at)
        f = np.array(at)
        notes.append(f"polyline corners from segment fits; worst two-sided disagreement {worst:.2f} px "
                     f"({worst * p.y_per_px:.3f})")
    else:
        f, v = dense(p, lo, hi, a.step)
        notes.append(f"red-pixel column centroids, resampled every {a.step:g}")
    if a.out:
        write_csv(a.out, f, v, a.column, notes)
    else:
        print("\n".join(f"# {n}" for n in notes))
        for x, y in zip(f, v):
            print(f"{x:.3f},{y:.3f}")
    if a.check:
        check_image(p, f, v, a.check)


if __name__ == "__main__":
    main()
