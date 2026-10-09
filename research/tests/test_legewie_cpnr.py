"""Verifica que la implementacion reproduce el comportamiento publicado de Legewie et al. 2006
(PLoS Comput Biol 2:e120) y que las metricas CPNR no cambian sin que nadie lo note.

Ejecutar desde research/:  python -m pytest tests -q
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from simulation import cpnr_core as core  # noqa: E402
from simulation.sbml_ode import load_legewie  # noqa: E402


@pytest.fixture(scope="module")
def wt():
    return load_legewie("WT")


@pytest.fixture(scope="module")
def nc():
    return load_legewie("NC")


def test_sbml_structure(wt, nc):
    assert len(wt.species) == 13 and len(wt.reaction_ids) == 28
    assert len(nc.species) == 17 and len(nc.reaction_ids) == 42


def test_wt_activates_with_nominal_apaf(wt):
    # Fig. 2A del articulo: con Apaf-1 total = 20 nM la caspasa-3 se activa por completo.
    c3, _ = core.steady_state_c3(wt, wt.params, wt.x0)
    assert c3 > 100


def test_wt_bistability_is_irreversible(wt):
    # Retirar por completo la entrada de apoptosoma no devuelve la celula al estado vivo.
    _, x_on = core.steady_state_c3(wt, wt.params, wt.x0)
    c3_off, _ = core.steady_state_c3(wt, core.with_params(wt, k16prod=0.0), x_on)
    assert c3_off > 40


def test_nc_bistability_is_reversible(nc):
    # Sin la retroalimentacion implicita de XIAP la activacion es reversible (notas del SBML, Fig. 4C).
    _, x_on = core.steady_state_c3(nc, nc.params, nc.x0)
    c3_off, _ = core.steady_state_c3(nc, core.with_params(nc, k16prod=0.0), x_on)
    assert c3_off < 1


def test_wt_point_of_no_return(wt):
    xr = core.resting_state(wt, wt.params)
    t_star = core.critical_duration(wt, wt.params, 0.02, x_rest=xr, tol_s=5.0)
    assert t_star / 60 == pytest.approx(13.4, abs=0.2)
    survivor = core.simulate_pulse(wt, wt.params, 0.02, t_star - 5.0, xr)
    committed = core.simulate_pulse(wt, wt.params, 0.02, t_star, xr)
    assert not survivor.committed and committed.committed
    # El PNR se cruza con menos del 1 % de la caspasa-3 total activa.
    assert committed.c3_at_withdrawal < 2.0


def test_fate_monotonic_in_duration(wt):
    xr = core.resting_state(wt, wt.params)
    fates = [core.simulate_pulse(wt, wt.params, 0.01, T, xr).committed for T in np.arange(0, 7200, 300)]
    assert fates == sorted(fates)
