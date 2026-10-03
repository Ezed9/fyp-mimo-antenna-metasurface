"""MIMO diversity metrics computed from S-parameters and far-field patterns.

Conventions: S has shape (F, N, N) complex (F frequency points, N ports).
Port indices are 0-based in code; figures label them 1-based.
"""

import numpy as np


def _col_power(S: np.ndarray, i: int) -> np.ndarray:
    return np.sum(np.abs(S[:, :, i]) ** 2, axis=1)


def ecc_from_s(S: np.ndarray, i: int, j: int) -> np.ndarray:
    """ECC between ports i, j from S-params (valid for lossless, high-efficiency antennas)."""
    num = np.abs(np.sum(np.conj(S[:, :, i]) * S[:, :, j], axis=1)) ** 2
    den = (1 - _col_power(S, i)) * (1 - _col_power(S, j))
    return num / np.clip(den, 1e-12, None)


def ecc_from_farfield(
    Ei_theta: np.ndarray,
    Ei_phi: np.ndarray,
    Ej_theta: np.ndarray,
    Ej_phi: np.ndarray,
    theta_deg: np.ndarray,
) -> float:
    """ECC from complex 3D patterns on a uniform (theta, phi) grid, uniform environment (XPR = 1).

    All field arrays share the same shape; theta_deg broadcasts against them.
    """
    w = np.sin(np.deg2rad(theta_deg))
    cross = np.sum((Ei_theta * np.conj(Ej_theta) + Ei_phi * np.conj(Ej_phi)) * w)
    pi = np.sum((np.abs(Ei_theta) ** 2 + np.abs(Ei_phi) ** 2) * w)
    pj = np.sum((np.abs(Ej_theta) ** 2 + np.abs(Ej_phi) ** 2) * w)
    return float(np.abs(cross) ** 2 / (pi * pj))


def diversity_gain(ecc: np.ndarray) -> np.ndarray:
    return 10 * np.sqrt(1 - np.clip(ecc, 0, 1) ** 2)


def tarc(S: np.ndarray, a: np.ndarray) -> np.ndarray:
    """TARC (linear) for excitation vector(s) a of shape (N,) or (K, N). Returns (F,) or (K, F)."""
    a2 = np.atleast_2d(a)
    b = np.einsum("fmn,kn->kfm", S, a2)
    out = np.sqrt(np.sum(np.abs(b) ** 2, axis=2)) / np.sqrt(np.sum(np.abs(a2) ** 2, axis=1))[:, None]
    return out[0] if a.ndim == 1 else out


def random_excitations(n_ports: int, count: int, seed: int = 0) -> np.ndarray:
    """Unit-amplitude excitations with random phases; port 1 is the phase reference."""
    rng = np.random.default_rng(seed)
    phases = rng.uniform(0, 2 * np.pi, size=(count, n_ports))
    phases[:, 0] = 0
    return np.exp(1j * phases)


def ccl(S: np.ndarray) -> np.ndarray:
    """Channel capacity loss in bit/s/Hz: -log2 det(I - S^H S)."""
    n = S.shape[1]
    psi = np.eye(n)[None] - np.conj(np.transpose(S, (0, 2, 1))) @ S
    det = np.real(np.linalg.det(psi))
    return -np.log2(np.clip(det, 1e-12, None))


def meg_db(S: np.ndarray) -> np.ndarray:
    """Mean effective gain per port in dB, shape (F, N): 0.5 * (1 - sum_j |S_ij|^2)."""
    lin = 0.5 * (1 - np.sum(np.abs(S) ** 2, axis=2))
    return 10 * np.log10(np.clip(lin, 1e-12, None))


def to_db(x: np.ndarray) -> np.ndarray:
    return 20 * np.log10(np.clip(np.abs(x), 1e-12, None))


def band_mask(f_ghz: np.ndarray, band: tuple[float, float]) -> np.ndarray:
    return (f_ghz >= band[0]) & (f_ghz <= band[1])


def impedance_bandwidth(f_ghz: np.ndarray, s11_db: np.ndarray, level: float = -10.0) -> list[tuple[float, float]]:
    """Contiguous frequency ranges where S11 <= level."""
    below = s11_db <= level
    edges = np.flatnonzero(np.diff(below.astype(int)))
    starts = [0] if below[0] else []
    starts += [e + 1 for e in edges if not below[e]]
    stops = [e for e in edges if below[e]]
    if below[-1]:
        stops.append(len(f_ghz) - 1)
    return [(float(f_ghz[a]), float(f_ghz[b])) for a, b in zip(starts, stops)]


def score_s11(f_ghz: np.ndarray, s11_db: np.ndarray, band: tuple[float, float]) -> tuple[float, float]:
    """Ranking key for parametric sweeps: (fraction of band with S11 <= -10 dB, -worst in-band S11).

    Higher is better on both; compare tuples directly.
    """
    m = band_mask(f_ghz, band)
    coverage = float(np.mean(s11_db[m] <= -10))
    return coverage, -float(np.max(s11_db[m]))
