"""Modulo mitocondrial (MOMP / BCL-2): ¿es la permeabilizacion mitocondrial completa el punto de no retorno?

M0  Albeck et al. 2008 (EARM, BIOMD0000000220, curado): rescate por inhibicion de caspasa-8 a tiempo t.
    Muestra que el modelo no tiene estado de supervivencia al que volver (solo retrasa la muerte).
M1  Bagci et al. 2006 (MODEL1006230056, NO curado): verificacion frente a cifras del articulo.
M2  Bagci: umbral de estimulo y liberacion maxima de citocromo c compatible con supervivencia.
M3  Bagci: efecto de BCL-2, IAP y Bax (escenarios tumorales) sobre el umbral y la MOMP sobrevivible.
M4  Bagci: muestreo global de parametros (robustez).

Todo es data_provenance=SIMULATED.  Uso: python -m simulation.run_momp_simulations  (desde research/src)
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from simulation.run_cpnr_simulations import BLUE, INK, ORANGE, OUT, _save
from simulation.sbml_ode import load_albeck, load_bagci

SEED = 44
DEATH_C3_UM = 1e-4       # Bagci: caspasa-3 estacionaria > 0.1 nM = estado apoptotico (muerte ~5.7e-3 microM)
HORIZON_S = 1.0e6        # ~11.6 dias: los destinos cercanos al umbral tardan >80 h en decidirse
RTOL, ATOL = 1e-8, 1e-16
C8_MIN, C8_MAX = 1e-9, 1e-1
MAX_RHS_CALLS = 2_000_000  # ~100 veces lo que necesita una simulacion tipica (~5e3-2e4 evaluaciones)


class IntegrationBudgetExceeded(RuntimeError):
    """La integracion supero el presupuesto de calculo; el juego de parametros se marca integration_failed."""


# --------------------------------------------------------------------------- M0 Albeck
def m0_albeck_rescue():
    m = load_albeck()
    p, I = m.params, m.idx
    cyt_total = m.x0[I["CytoCm"]]
    inhibited = dict(p, k5=0.0, kc5=0.0, k10=0.0, kc10=0.0)  # caspasa-8 sin actividad catalitica (tipo z-IETD)
    rows = []
    for L in (100.0, 3000.0):
        x0 = m.x0.copy()
        x0[I["L"]] = L
        base = solve_ivp(m.rhs(p), [0, 24 * 3600], x0, method="LSODA", rtol=1e-6, atol=1e-6, dense_output=True)
        tt = np.linspace(0, 24 * 3600, 2881)
        cp = m.observable("cPARP_frac", base.sol(tt))
        t_death_untreated = tt[np.argmax(cp >= 0.5)] / 3600
        for t_inh_h in (0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.25):
            if t_inh_h * 3600 >= t_death_untreated * 3600:
                continue
            xi = base.sol(t_inh_h * 3600)
            s2 = solve_ivp(m.rhs(inhibited), [t_inh_h * 3600, 96 * 3600], xi, method="LSODA", rtol=1e-6, atol=1e-6, dense_output=True)
            t2 = np.linspace(t_inh_h * 3600, 96 * 3600, 4000)
            y2 = s2.sol(t2)
            cp2 = m.observable("cPARP_frac", y2)
            died = cp2.max() >= 0.5
            rows.append(dict(model="Albeck2008_BIOMD0000000220", ligand_molecules=L, untreated_death_h=t_death_untreated,
                             inhibitor_time_h=t_inh_h, tBid_at_inhibition=float(xi[I["tBid"]]),
                             cytc_released_at_inhibition_pct=100 * (1 - (xi[I["CytoCm"]] + xi[I["M_hash_CytoCm"]]) / cyt_total),
                             death_time_h=float(t2[np.argmax(cp2 >= 0.5)] / 3600) if died else np.nan,
                             cPARP_frac_at_96h=float(cp2[-1])))
    df = pd.DataFrame(rows)
    df["data_provenance"] = "SIMULATED"
    df.to_csv(OUT / "M0_albeck_caspase8_inhibitor_rescue.csv", index=False)
    return df


# --------------------------------------------------------------------------- Bagci helpers
_B = None


def _bagci():
    global _B
    if _B is None:
        _B = load_bagci()
    return _B


def _budgeted(f):
    calls = [0]

    def rhs(t, y):  # presupuesto de calculo: evita trayectorias patologicas de millones de pasos
        calls[0] += 1
        if calls[0] > MAX_RHS_CALLS:
            raise IntegrationBudgetExceeded
        return f(t, y)

    return rhs


def _rest(m, params):
    return solve_ivp(_budgeted(m.rhs(params)), [0, 5e5], m.x0, method="LSODA", rtol=RTOL, atol=ATOL).y[:, -1]


def _bolus(m, params, x_rest, c8, keep=False):
    """Estimulo del articulo: bolo inicial de caspasa-8 activa (decae con u)."""
    I = m.idx
    x = x_rest.copy()
    x[I["Casp8"]] = c8
    t = np.unique(np.concatenate([np.linspace(0, 4 * 3600, 4801), np.geomspace(4 * 3600, HORIZON_S, 3000)]))
    s = solve_ivp(_budgeted(m.rhs(params)), [0, HORIZON_S], x, method="LSODA", rtol=RTOL, atol=ATOL, t_eval=t)
    if s.status != 0:
        raise IntegrationBudgetExceeded
    y = s.y
    cyt0 = x_rest[I["Cytc_mito"]]
    rel = 1 - y[I["Cytc_mito"]] / cyt0
    out = dict(c8=c8, c3_final=float(y[I["Casp3"], -1]), died=bool(y[I["Casp3"], -1] > DEATH_C3_UM),
               cytc_release_peak_pct=float(100 * rel.max()), c3_peak=float(y[I["Casp3"]].max()),
               cytc_release_final_pct=float(100 * rel[-1]))
    if keep:
        return out, t, y
    return out


def _threshold(m, params, x_rest):
    """Bolo minimo de caspasa-8 que compromete (biseccion logaritmica) + metricas justo por debajo/encima."""
    if _bolus(m, params, x_rest, 0.0)["died"] or x_rest[m.idx["Casp3"]] > DEATH_C3_UM:
        return dict(regime="spontaneous_death")
    if not _bolus(m, params, x_rest, C8_MAX)["died"]:
        return dict(regime="no_death_reachable")
    lo, hi = C8_MIN, C8_MAX
    if _bolus(m, params, x_rest, lo)["died"]:
        return dict(regime="hypersensitive")
    while hi / lo > 1 + 1e-7:
        mid = np.sqrt(lo * hi)
        if _bolus(m, params, x_rest, mid)["died"]:
            hi = mid
        else:
            lo = mid
    below, above = _bolus(m, params, x_rest, lo), _bolus(m, params, x_rest, hi)
    return dict(regime="threshold", c8_threshold_uM=hi,
                survivor_cytc_release_peak_pct=below["cytc_release_peak_pct"],
                survivor_c3_peak_uM=below["c3_peak"], death_c3_steady_uM=above["c3_final"],
                survivor_c3_peak_pct_of_death=100 * below["c3_peak"] / above["c3_final"],
                death_cytc_release_final_pct=above["cytc_release_final_pct"])


def _metrics(factors):
    m = _bagci()
    params = dict(m.params, **{k: m.params[k] * f for k, f in factors.items()})
    try:
        x_rest = _rest(m, params)
        res = _threshold(m, params, x_rest)
    except IntegrationBudgetExceeded:
        res = dict(regime="integration_failed")  # se informa, no se descarta en silencio
    return dict(**{f"factor_{k}": v for k, v in factors.items()}, **res)


# --------------------------------------------------------------------------- M1
def m1_reproduction():
    """Cifras del articulo (Bagci et al. 2006, Biophys J 90:1546; texto en PMC1367306)."""
    m = _bagci()
    p, I = m.params, m.idx
    x_rest = _rest(m, p)
    rows = []
    for c8, expected in ((1e-5, "survival"), (1e-4, "apoptosis")):
        r = _bolus(m, p, x_rest, c8)
        rows.append(dict(check=f"[casp8]0 = {c8:g} microM", article_value=expected,
                         simulated=("apoptosis" if r["died"] else "survival") + f" (Casp3 final {r['c3_final']:.2e} microM)",
                         match=(r["died"] == (expected == "apoptosis"))))
    x_start = x_rest.copy()
    x_start[I["Casp8"]] = 1e-4
    x_dead = solve_ivp(m.rhs(p), [0, 5e5], x_start, method="LSODA", rtol=RTOL, atol=ATOL).y[:, -1]

    def loss_point(par, values):
        x = x_dead.copy()
        last_alive = None
        for v in values:
            x = solve_ivp(m.rhs(dict(p, **{par: v})), [0, 5e5], x, method="LSODA", rtol=RTOL, atol=ATOL).y[:, -1]
            if x[I["Casp3"]] < DEATH_C3_UM:
                return last_alive, v
            last_alive = v
        return last_alive, None

    # Continuacion cuasi-estacionaria: aproxima el punto silla-nodo desde el lado biestable. Se acepta
    # concordancia si la diferencia relativa con la cifra del articulo es <= 3 % (se informa el valor exacto).
    a, b = loss_point("u_Bax", np.round(np.arange(0.006, 0.2, 0.001), 4))
    mid = (a + b) / 2
    rows.append(dict(check="u_Bax at which apoptotic state disappears (saddle-node)", article_value="0.11 s^-1",
                     simulated=f"between {a} and {b} s^-1", rel_diff_pct=100 * abs(mid - 0.11) / 0.11,
                     match=abs(mid - 0.11) / 0.11 <= 0.03))
    a, b = loss_point("P_oBax", np.round(np.arange(3e-5, 1e-6, -1e-7), 9))
    mid = (a + b) / 2
    rows.append(dict(check="Bax production at which apoptotic state disappears", article_value="6.03e-6 microM/s",
                     simulated=f"between {b} and {a} microM/s", rel_diff_pct=100 * abs(mid - 6.03e-6) / 6.03e-6,
                     match=abs(mid - 6.03e-6) / 6.03e-6 <= 0.03))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "M1_bagci_reproduction_checks.csv", index=False)
    return df


# --------------------------------------------------------------------------- M2
def m2_threshold():
    m = _bagci()
    p, I = m.params, m.idx
    x_rest = _rest(m, p)
    res = _threshold(m, p, x_rest)
    pd.DataFrame([res]).assign(data_provenance="SIMULATED").to_csv(OUT / "M2_bagci_threshold_default.csv", index=False)

    c8s = res["c8_threshold_uM"]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.2))
    for f, color, label in [(1 - 1e-6, BLUE, "justo bajo el umbral: sobrevive"), (1 + 1e-6, ORANGE, "justo sobre el umbral: muere")]:
        _, t, y = _bolus(m, p, x_rest, c8s * f, keep=True)
        sel = (t > 0) & (t <= 100 * 3600)
        axes[0].plot(t[sel] / 3600, 100 * (1 - y[I["Cytc_mito"], sel] / x_rest[I["Cytc_mito"]]), color=color, label=label)
        axes[1].plot(t[sel] / 3600, np.maximum(y[I["Casp3"], sel], 1e-12) * 1e3, color=color, label=label)
    axes[0].set_xscale("log")
    axes[0].set_xlabel("tiempo (h)")
    axes[0].set_ylabel("citocromo c liberado (% del mitocondrial)")
    axes[0].set_title("Liberacion de citocromo c (MOMP)", color=INK, fontsize=9, loc="left")
    axes[0].legend(loc="upper left", fontsize=7.5)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_ylim(1e-6, 20)
    axes[1].set_xlabel("tiempo (h)")
    axes[1].set_ylabel("caspasa-3 activa (nM)")
    axes[1].set_title("Caspasa-3 activa", color=INK, fontsize=9, loc="left")
    _save(fig, "M2_bagci_MOMP_parcial_umbral")
    return res


# --------------------------------------------------------------------------- M3
def m3_scenarios():
    jobs = []
    for par, label in (("P_oBcl_2", "Bcl-2 production"), ("P_IAP", "IAP production"), ("P_oBax", "Bax production")):
        for f in (0.25, 0.5, 1, 2, 4, 8):
            jobs.append({par: f})
    with ProcessPoolExecutor() as ex:
        rows = list(ex.map(_metrics, jobs))
    df = pd.DataFrame(rows)
    df["data_provenance"] = "SIMULATED"
    df.to_csv(OUT / "M3_bagci_bcl2_iap_bax_scenarios.csv", index=False)
    return df


# --------------------------------------------------------------------------- M4
SAMPLED_EXCLUDED = {"p", "p53", "p53_thresh", "COMpartment"}


def plot_m4(df):
    """Figura M4 a partir del CSV (se puede regenerar sin volver a simular)."""
    thr = df[df.regime == "threshold"]
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.3))
    axes[0].hist(thr.survivor_cytc_release_peak_pct, bins=np.linspace(0, 100, 41), color=BLUE, histtype="step", linewidth=2)
    axes[0].set_xlabel("citocromo c liberado maximo\nen una celula que sobrevive (%)")
    axes[0].set_ylabel("juegos de parametros")
    axes[0].set_title(f"MOMP sobrevivible (n = {len(thr)} con umbral)", color=INK, fontsize=9, loc="left")
    axes[1].hist(np.log10(thr.survivor_c3_peak_pct_of_death.clip(lower=1e-6)), bins=40, color=ORANGE, histtype="step", linewidth=2)
    axes[1].set_xlabel("log10 caspasa-3 maxima en superviviente\n(% del estado apoptotico; <1e-6 agrupado en -6)")
    axes[1].set_ylabel("juegos de parametros")
    axes[1].set_title("Caspasa-3 sobrevivible", color=INK, fontsize=9, loc="left")
    fig.subplots_adjust(wspace=0.3)
    _save(fig, "M4_bagci_robustez_global")


def m4_global(n=1000, spread=3.0):
    m = _bagci()
    keys = [k for k in m.params if k not in SAMPLED_EXCLUDED]
    rng = np.random.default_rng(SEED)
    jobs = [{k: float(np.exp(rng.uniform(-np.log(spread), np.log(spread)))) for k in keys} for _ in range(n)]
    rows = []
    with ProcessPoolExecutor() as ex:
        for i, r in enumerate(ex.map(_metrics, jobs, chunksize=4), 1):
            rows.append(r)
            if i % 50 == 0:
                print(f"  M4 {i}/{n}", flush=True)
    df = pd.DataFrame(rows)
    df["data_provenance"] = "SIMULATED"
    df.to_csv(OUT / "M4_bagci_global_sampling.csv", index=False)

    thr = df[df.regime == "threshold"]
    plot_m4(df)
    q = thr[["survivor_cytc_release_peak_pct", "survivor_c3_peak_pct_of_death"]].quantile([0.01, 0.5, 0.9, 0.99, 1.0])
    return dict(n=len(df), regime_counts=df.regime.value_counts().to_dict(), quantiles=q.round(4).to_dict(),
                sets_with_survivable_release_over_50pct=int((thr.survivor_cytc_release_peak_pct > 50).sum()),
                sets_with_survivable_c3_over_10pct_of_death=int((thr.survivor_c3_peak_pct_of_death > 10).sum()))


def main():
    import sys
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    summary = {"data_provenance": "SIMULATED", "death_c3_threshold_uM": DEATH_C3_UM, "horizon_s": HORIZON_S, "seed": SEED}
    print("M0 Albeck rescate...", flush=True);  summary["M0"] = m0_albeck_rescue().replace({np.nan: None}).to_dict("records")
    print("M1 Bagci reproduccion...", flush=True); summary["M1"] = m1_reproduction().to_dict("records")
    print("M2 Bagci umbral...", flush=True);     summary["M2"] = m2_threshold()
    print("M3 Bagci escenarios...", flush=True); summary["M3"] = m3_scenarios().replace({np.nan: None}).to_dict("records")
    print("M4 Bagci global...", flush=True);     summary["M4"] = m4_global(n=int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
    summary["runtime_s"] = round(time.time() - t0, 1)
    (OUT / "summary_momp.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    print(f"Listo en {summary['runtime_s']} s")


if __name__ == "__main__":
    main()
