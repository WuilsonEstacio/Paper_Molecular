"""Experimentos de punto de no retorno (CPNR) sobre el modelo de Legewie et al. 2006.

Protocolo (analogo in silico al de anastasis de Tang et al. 2012, MBoC 23:2240):
  1. Celula en reposo: estado estacionario sin entrada de apoptosoma (k16prod = 0).
  2. Estimulo transitorio: formacion de apoptosoma activo (k16prod = S, nM/s) durante T segundos.
     En el modelo, S representa la tasa de formacion de Apaf-1 activo tras la liberacion de
     citocromo c; un pulso finito corresponde a una permeabilizacion mitocondrial limitada.
  3. Retirada del estimulo (k16prod = 0) y seguimiento hasta el estado final.

Definicion operativa de destino: la celula queda comprometida si la caspasa-3 activa libre
(C3_star) permanece por encima de FATE_THRESHOLD_NM tras la retirada. El modelo no contiene
una ejecucion de muerte explicita; "comprometida" significa actividad caspasa-3 sostenida sin
estimulo, que en el WT es un estado estable autosostenido (biestabilidad irreversible).

Unidades del modelo: nM y segundos.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from simulation.sbml_ode import SBMLModel

FATE_THRESHOLD_NM = 5.0
# Umbral operativo para decir que una celula superviviente "llego a activar" caspasa-3:
# 1 nM = 0.5 % de la caspasa-3 total y ~17 veces el nivel basal del WT (0.058 nM).
ACTIVATION_THRESHOLD_NM = 1.0
HORIZON_S = 1.0e5
RTOL, ATOL = 1e-7, 1e-9


def with_params(model: SBMLModel, **overrides) -> dict:
    p = dict(model.params)
    for k, v in overrides.items():
        if k not in p:
            raise KeyError(k)
        p[k] = v
    return p


def _augmented_rhs(model: SBMLModel, params: dict):
    """ODEs del SBML + exposicion acumulada a caspasa-3 activa, E(t) = integral de C3_star dt."""
    base = model.rhs(params)
    i3 = model.idx["C3_star"]

    def f(t, y):
        return np.append(base(t, y[:-1]), y[i3])

    return f


def resting_state(model: SBMLModel, params: dict) -> np.ndarray:
    p = dict(params, k16prod=0.0)
    x0 = model.x0.copy()
    x0[model.idx["A"]] = 0.0
    sol = solve_ivp(model.rhs(p), [0, 2e5], x0, method="LSODA", rtol=RTOL, atol=ATOL)
    return sol.y[:, -1]


@dataclass
class PulseResult:
    stimulus: float
    duration_s: float
    state_at_withdrawal: np.ndarray
    c3_at_withdrawal: float
    c3_peak: float
    c3_final: float
    exposure_nM_s: float
    committed: bool


def simulate_pulse(model: SBMLModel, params: dict, stimulus: float, duration_s: float,
                   x_rest: np.ndarray | None = None, keep_traj: bool = False):
    if x_rest is None:
        x_rest = resting_state(model, params)
    i3 = model.idx["C3_star"]
    y0 = np.append(x_rest, 0.0)
    ts, ys = [], []

    p_on = dict(params, k16prod=stimulus)
    if duration_s > 0:
        s1 = solve_ivp(_augmented_rhs(model, p_on), [0, duration_s], y0, method="LSODA",
                       rtol=RTOL, atol=ATOL, dense_output=keep_traj)
        y_w = s1.y[:, -1]
        peak1 = s1.y[i3].max()
        if keep_traj:
            ts.append(s1.t); ys.append(s1.y)
    else:
        y_w, peak1 = y0, y0[i3]

    p_off = dict(params, k16prod=0.0)
    s2 = solve_ivp(_augmented_rhs(model, p_off), [duration_s, duration_s + HORIZON_S], y_w,
                   method="LSODA", rtol=RTOL, atol=ATOL)
    if keep_traj:
        ts.append(s2.t); ys.append(s2.y)
    c3_final = float(s2.y[i3, -1])
    res = PulseResult(
        stimulus=stimulus,
        duration_s=duration_s,
        state_at_withdrawal=y_w[:-1],
        c3_at_withdrawal=float(y_w[i3]),
        c3_peak=float(max(peak1, s2.y[i3].max())),
        c3_final=c3_final,
        exposure_nM_s=float(s2.y[-1, -1]),
        committed=c3_final > FATE_THRESHOLD_NM,
    )
    if keep_traj:
        return res, np.concatenate(ts), np.concatenate(ys, axis=1)
    return res


def critical_duration(model: SBMLModel, params: dict, stimulus: float,
                      t_max_s: float = 6 * 3600, tol_s: float = 10.0,
                      x_rest: np.ndarray | None = None) -> float:
    """Duracion minima del pulso que compromete a la celula (T*). np.inf si no ocurre antes de t_max_s.

    Asume monotonia del destino en T (verificado empiricamente en los barridos de duracion).
    Devuelve 0.0 si la celula ya esta comprometida en reposo (apoptosis espontanea)."""
    if x_rest is None:
        x_rest = resting_state(model, params)
    if x_rest[model.idx["C3_star"]] > FATE_THRESHOLD_NM:
        return 0.0
    if not simulate_pulse(model, params, stimulus, t_max_s, x_rest).committed:
        return np.inf
    lo, hi = 0.0, t_max_s
    while hi - lo > tol_s:
        mid = 0.5 * (lo + hi)
        if simulate_pulse(model, params, stimulus, mid, x_rest).committed:
            hi = mid
        else:
            lo = mid
    return hi


def steady_state_c3(model: SBMLModel, params: dict, x_start: np.ndarray) -> tuple[float, np.ndarray]:
    sol = solve_ivp(model.rhs(params), [0, 2e5], x_start, method="LSODA", rtol=RTOL, atol=ATOL)
    return float(sol.y[model.idx["C3_star"], -1]), sol.y[:, -1]
