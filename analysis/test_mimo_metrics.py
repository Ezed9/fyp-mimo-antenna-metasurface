import tempfile
from pathlib import Path

import numpy as np
import pytest

import make_figures as mf
import mimo_metrics as mm


def ideal(n: int = 4, f: int = 5, refl: float = 0.0) -> np.ndarray:
    return np.tile(np.eye(n) * refl, (f, 1, 1)).astype(complex)


def test_isolated_matched_ports() -> None:
    S = ideal()
    assert np.allclose(mm.ecc_from_s(S, 0, 1), 0)
    assert np.allclose(mm.diversity_gain(mm.ecc_from_s(S, 0, 1)), 10)
    assert np.allclose(mm.ccl(S), 0)
    assert np.allclose(mm.meg_db(S), 10 * np.log10(0.5))
    assert np.allclose(mm.tarc(S, np.ones(4)), 0)


def test_tarc_equals_reflection_when_isolated() -> None:
    S = ideal(refl=0.1)
    t = mm.tarc(S, mm.random_excitations(4, 10))
    assert t.shape == (10, 5)
    assert np.allclose(t, 0.1)


def test_ecc_from_s_two_port_formula() -> None:
    S = np.array([[[0.2 + 0.1j, 0.15 - 0.05j], [0.15 - 0.05j, 0.1 + 0.2j]]])
    s11, s12, s21, s22 = S[0, 0, 0], S[0, 0, 1], S[0, 1, 0], S[0, 1, 1]
    ref = abs(np.conj(s11) * s12 + np.conj(s21) * s22) ** 2 / (
        (1 - abs(s11) ** 2 - abs(s21) ** 2) * (1 - abs(s22) ** 2 - abs(s12) ** 2)
    )
    assert mm.ecc_from_s(S, 0, 1)[0] == pytest.approx(ref)


def test_ccl_increases_with_coupling() -> None:
    weak, strong = ideal(2, 1), ideal(2, 1)
    weak[0, 0, 1] = weak[0, 1, 0] = 0.05
    strong[0, 0, 1] = strong[0, 1, 0] = 0.3
    assert 0 < mm.ccl(weak)[0] < mm.ccl(strong)[0]


def _grid() -> tuple[np.ndarray, np.ndarray]:
    return np.meshgrid(np.arange(0, 181, 5.0), np.arange(0, 360, 5.0), indexing="ij")


def test_ecc_farfield_identical_and_orthogonal() -> None:
    th, ph = _grid()
    e = np.sin(np.deg2rad(th)) + 0j
    z = np.zeros_like(e)
    assert mm.ecc_from_farfield(e, z, e, z, th) == pytest.approx(1.0)
    assert mm.ecc_from_farfield(e, z, z, e, th) == pytest.approx(0.0, abs=1e-12)


def test_ecc_farfield_orthogonal_dipoles_low() -> None:
    th, ph = np.deg2rad(_grid())
    # x- and y-directed short dipoles at the origin: theta/phi components
    ex_t, ex_p = np.cos(th) * np.cos(ph), -np.sin(ph)
    ey_t, ey_p = np.cos(th) * np.sin(ph), np.cos(ph)
    e = mm.ecc_from_farfield(ex_t + 0j, ex_p + 0j, ey_t + 0j, ey_p + 0j, np.rad2deg(th))
    assert e < 1e-3


def test_impedance_bandwidth_and_score() -> None:
    f = np.linspace(2, 12, 101)
    s = np.where((f >= 3) & (f <= 11), -15.0, -5.0)
    assert mm.impedance_bandwidth(f, s) == [(3.0, 11.0)]
    cov, neg_worst = mm.score_s11(f, s, (3.1, 10.6))
    assert cov == 1.0 and neg_worst == 15.0


def test_ascii_sweep_parser_labels() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "sweep.txt"
        f = np.linspace(2, 12, 11)
        mf._write_ascii(p, [({"Lg": 9, "Wf": 3}, f, -f), ({"Lg": 10, "Wf": 3}, f, -2 * f)], "S1,1")
        curves = mf.read_cst_ascii(p)
    assert [c[0] for c in curves] == ["Lg = 9", "Lg = 10"]
    assert np.allclose(curves[1][2], -2 * f)


def test_demo_pipeline_renders_all_figures() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        exp, out = Path(tmp) / "exp", Path(tmp) / "out"
        exp.mkdir()
        mf.write_demo(exp)
        made = mf.run(exp, out)
        summary = (out / "summary.txt").read_text()
    assert len(made) >= 20
    assert "far-field ECC" in summary and "best R" in summary
