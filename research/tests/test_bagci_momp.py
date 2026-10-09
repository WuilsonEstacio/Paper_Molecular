"""Reproduccion de Bagci et al. 2006 (MODEL1006230056, no curado) y de Albeck et al. 2008 (BIOMD0000000220),
y valores de referencia del modulo MOMP. Ejecutar desde research/:  python -m pytest tests -q
"""
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from simulation import run_momp_simulations as mm  # noqa: E402
from simulation.sbml_ode import load_albeck, load_bagci  # noqa: E402


@pytest.fixture(scope="module")
def bagci():
    m = load_bagci()
    return m, mm._rest(m, m.params)


def test_bagci_structure(bagci):
    m, _ = bagci
    assert len(m.species) == 31


@pytest.mark.parametrize("c8,dies", [(1e-5, False), (1e-4, True)])
def test_bagci_article_stimulus(bagci, c8, dies):
    # Texto del articulo: [casp8]0 = 1e-5 microM -> supervivencia; 1e-4 microM -> apoptosis
    m, x_rest = bagci
    assert mm._bolus(m, m.params, x_rest, c8)["died"] is dies


def test_bagci_partial_momp_is_survivable(bagci):
    m, x_rest = bagci
    r = mm._threshold(m, m.params, x_rest)
    assert r["regime"] == "threshold"
    assert r["c8_threshold_uM"] == pytest.approx(5.28e-5, rel=0.01)
    assert r["survivor_cytc_release_peak_pct"] == pytest.approx(14.5, abs=0.3)
    assert r["survivor_c3_peak_pct_of_death"] < 1.0


def test_albeck_snap_action_momp():
    # Albeck 2008: retraso largo y MOMP rapida; con L = 3000 la MOMP ocurre a ~3.2 h y cPARP 50 % a ~3.65 h
    m = load_albeck()
    I = m.idx
    s = solve_ivp(m.rhs(m.params), [0, 12 * 3600], m.x0, method="LSODA", rtol=1e-6, atol=1e-6, dense_output=True)
    t = np.linspace(0, 12 * 3600, 4321)
    y = s.sol(t)
    rel = 1 - (y[I["CytoCm"]] + y[I["M_hash_CytoCm"]]) / m.x0[I["CytoCm"]]
    t10, t90 = t[np.argmax(rel >= 0.1)], t[np.argmax(rel >= 0.9)]
    assert 2.9 * 3600 < t10 < 3.5 * 3600
    assert (t90 - t10) < 20 * 60
    cp = m.observable("cPARP_frac", y)
    assert 3.4 * 3600 < t[np.argmax(cp >= 0.5)] < 3.9 * 3600
