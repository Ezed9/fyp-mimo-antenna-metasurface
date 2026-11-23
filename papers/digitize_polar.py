"""Digitise a CST polar far-field cut (red curve on a polar grid) from a screenshot.

    python papers/digitize_polar.py

The centre is where the two axis lines cross, the grid circles are found from the dark pixels, and the radial scale
is fixed by the values printed on the circles (given below for each screenshot). Each curve is checked against the
main-lobe magnitude and direction that CST prints beside the plot. Output: papers/data/*_pattern_*.csv with the angle
in degrees clockwise from the top of the plot (theta on the right half, -theta on the left half) and the directivity.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from scipy.signal import find_peaks

HERE = Path(__file__).resolve().parent

# screenshot, output, value at the centre (dBi), dB between neighbouring circles, value on the innermost circle,
# CST read-out (main lobe magnitude in dBi, direction in degrees) used as the check
JOBS = [
    ("paper2/cst_screenshots/7p4GHz_radiation_pattern_port1_without_metasurface.png", "p2_pattern_noms", 5.0, -15.0,
     (3.62, 156.0)),
    ("paper2/cst_screenshots/7p4GHz_radiation_pattern_port1_with_metasurface.png", "p2_pattern_ms", 5.0, -10.0,
     (4.14, 6.0)),
    ("paper1/cst_screenshots/pattern_5p3GHz_without.png", "p1_pattern_5p3_noms", 5.0, -15.0, (3.56, 176.0)),
    ("paper1/cst_screenshots/pattern_5p3GHz_with.png", "p1_pattern_5p3_ms", 5.0, -15.0, (3.88, 2.0)),
]


def grid(rgb: np.ndarray) -> tuple[int, int, np.ndarray]:
    """Centre (x, y) and the radii of the grid circles, the last one being the solid outer circle."""
    dark = (rgb < 120).all(axis=2)
    cx, cy = int(dark.sum(axis=0).argmax()), int(dark.sum(axis=1).argmax())
    yy, xx = np.where(dark)
    r = np.hypot(xx - cx, yy - cy)
    hist = np.bincount(np.round(r).astype(int), minlength=int(r.max()) + 2).astype(float)
    density = hist / np.maximum(1, 2 * np.pi * np.arange(len(hist)))
    peaks, _ = find_peaks(density[15:], height=0.12, distance=4)
    return cx, cy, peaks + 15


def digitise(path: Path, db_per_circle: float, first_circle: float, step_deg: float) -> tuple[np.ndarray, np.ndarray]:
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(float)
    cx, cy, circles = grid(rgb)
    px_per_db = float(np.mean(np.diff(circles[:-1]))) / db_per_circle if len(circles) > 2 else \
        (circles[-1] - circles[0]) / db_per_circle
    weight = np.clip((rgb[..., 0] - np.maximum(rgb[..., 1], rgb[..., 2])) / 255, 0, 1)
    yy, xx = np.where(weight > 0.25)
    r = np.hypot(xx - cx, yy - cy)
    keep = (r <= circles[-1] * 1.01) & (r > 2)
    xx, yy, r, w = xx[keep], yy[keep], r[keep], weight[yy[keep], xx[keep]]
    angle = np.degrees(np.arctan2(xx - cx, -(yy - cy)))            # 0 at the top, clockwise positive
    bins = np.arange(-180, 180 + step_deg, step_deg)
    which = np.digitize(angle, bins) - 1
    centres, values = [], []
    for k in range(len(bins) - 1):
        m = which == k
        if m.sum() < 2:
            continue
        radius = np.sum(r[m] * w[m]) / np.sum(w[m])
        centres.append(0.5 * (bins[k] + bins[k + 1]))
        values.append(first_circle + (radius - circles[0]) / px_per_db)
    centres, values = np.array(centres), np.array(values)
    # The blue marker lines of CST cross the curve and leave gaps and steps. Fill every bin on a regular grid by
    # circular interpolation, remove single-bin steps with a median of three, then average over three bins.
    full = 0.5 * (bins[:-1] + bins[1:])
    filled = np.interp(full, centres, values, period=360)
    n = len(filled)
    med = np.median(np.stack([np.roll(filled, -1), filled, np.roll(filled, 1)]), axis=0)
    half = max(1, int(round(1.5 / step_deg)))
    smooth = np.mean(np.stack([np.roll(med, k) for k in range(-half, half + 1)]), axis=0)
    assert len(smooth) == n
    return full, smooth


def main() -> None:
    for shot, name, db_per_circle, first_circle, (mag, direction) in JOBS:
        path = HERE / shot
        step = 1.0 if Image.open(path).size[0] > 1500 else 2.0
        angle, value = digitise(path, db_per_circle, first_circle, step)
        k = int(value.argmax())
        print(f"{name}: {len(angle)} points; maximum {value[k]:.2f} dBi at {abs(angle[k]):.0f} deg "
              f"(CST read-out: {mag:.2f} dBi at {direction:.0f} deg)")
        lines = [f"# Directivity pattern, phi = 90 deg cut, digitised from {shot} with papers/digitize_polar.py",
                 "# angle: degrees clockwise from the top of the CST plot (right half = phi 270 deg, left half = "
                 "phi 90 deg; theta = |angle|)",
                 f"# check: maximum {value[k]:.2f} dBi at theta {abs(angle[k]):.0f} deg; CST prints {mag:.2f} dBi at "
                 f"{direction:.0f} deg",
                 "angle_deg,dir_dBi"]
        lines += [f"{a:.1f},{v:.3f}" for a, v in zip(angle, value)]
        (HERE / "data" / f"{name}.csv").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
