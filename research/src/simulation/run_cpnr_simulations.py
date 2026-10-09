"""Experimentos E1-E5 de punto de no retorno sobre Legewie et al. 2006 (BIOMD0000000102/103).

E1  Reproduccion: histeresis de caspasa-3 frente a la entrada de apoptosoma (WT vs NC).
E2  Mapa CPNR: duracion critica del pulso T* frente a la intensidad del estimulo (WT).
E3  Sensibilidad: que parametros cambian la irreversibilidad y la ventana de anastasis.
    Incluye el escenario tumoral de sobreexpresion de XIAP y la degradacion de caspasa-3 activa.
E4  Poblacion Monte Carlo con variabilidad celula-a-celula (SIMULATED).
E5  ML sobre E4: prediccion del destino a partir del estado molecular en el momento de retirar el estimulo.

Todo lo que produce este script es data_provenance=SIMULATED. No es evidencia experimental.
Uso:  python -m simulation.run_cpnr_simulations   (desde research/src)
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from simulation import cpnr_core as core
from simulation.sbml_ode import load_legewie

SEED = 42
RESEARCH = Path(__file__).resolve().parents[2]
OUT = RESEARCH / "results" / "simulations"
FIG = RESEARCH / "figures"
C3_TOTAL_NM = 200.0  # k22prod / k22 en el modelo

# Paleta de referencia (skill dataviz): categoricos en orden fijo, secuencial azul.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "lines.linewidth": 2, "figure.dpi": 150, "savefig.bbox": "tight", "legend.frameon": False,
})


def _save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)


# --------------------------------------------------------------------------- E1
def e1_hysteresis():
    rows = []
    inputs = np.round(np.linspace(0, 0.03, 31), 5)
    for variant in ["WT", "NC"]:
        m = load_legewie(variant)
        x_low = core.resting_state(m, m.params)
        _, x_high = core.steady_state_c3(m, core.with_params(m, k16prod=0.03), x_low)
        for direction, seq, x in [("up", inputs, x_low), ("down", inputs[::-1], x_high)]:
            for s in seq:
                c3, x = core.steady_state_c3(m, core.with_params(m, k16prod=float(s)), x)
                rows.append(dict(model=variant, direction=direction, apoptosome_input_nM_s=s,
                                 apaf_ss_nM=s / m.params["k16"], c3_star_ss_nM=c3))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "E1_hysteresis.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.2), sharey=True)
    for ax, variant, title in zip(axes, ["WT", "NC"], ["WT: retroalimentacion XIAP (BIOMD102)",
                                                      "NC: sin retroalimentacion (BIOMD103)"]):
        d = df[df.model == variant]
        for direction, color, label in [("up", BLUE, "estimulo creciente"), ("down", ORANGE, "estimulo decreciente")]:
            dd = d[d.direction == direction].sort_values("apaf_ss_nM")
            ax.plot(dd.apaf_ss_nM, dd.c3_star_ss_nM, color=color, label=label,
                    marker="o", markersize=3 if direction == "up" else 0)
        ax.set_title(title, color=INK, fontsize=9, loc="left")
        ax.set_xlabel("Apaf-1 activo en estado estacionario (nM)")
    axes[0].set_ylabel("Caspasa-3 activa estacionaria (nM)")
    axes[0].legend(loc="center right")
    _save(fig, "E1_histeresis_WT_vs_NC")

    wt0 = df[(df.model == "WT") & (df.direction == "down") & (df.apoptosome_input_nM_s == 0)].c3_star_ss_nM.item()
    nc0 = df[(df.model == "NC") & (df.direction == "down") & (df.apoptosome_input_nM_s == 0)].c3_star_ss_nM.item()
    return dict(WT_c3_after_full_withdrawal_nM=wt0, NC_c3_after_full_withdrawal_nM=nc0)


# --------------------------------------------------------------------------- E2
def e2_cpnr_map():
    m = load_legewie("WT")
    p = m.params
    xr = core.resting_state(m, p)
    rows = []
    for s in [0.0025, 0.004, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.04, 0.06, 0.08]:
        t_star = core.critical_duration(m, p, s, x_rest=xr, tol_s=5.0)
        row = dict(stimulus_nM_s=s, apaf_plateau_nM=s / p["k16"], T_star_min=t_star / 60)
        if np.isfinite(t_star):
            below = core.simulate_pulse(m, p, s, t_star - 5.0, xr)
            above = core.simulate_pulse(m, p, s, t_star, xr)
            row.update(
                survivor_c3_at_withdrawal_nM=below.c3_at_withdrawal,
                survivor_c3_peak_nM=below.c3_peak,
                survivor_c3_peak_pct_total=100 * below.c3_peak / C3_TOTAL_NM,
                survivor_exposure_nM_min=below.exposure_nM_s / 60,
                committed_c3_final_nM=above.c3_final,
            )
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "E2_cpnr_map_WT.csv", index=False)

    # Trayectorias justo por debajo / encima de T* para S = 0.02 (estimulo nominal del modelo)
    s = 0.02
    t_star = df.loc[df.stimulus_nM_s == s, "T_star_min"].item() * 60
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.2))
    for dt, color, label in [(-60, BLUE, f"T* - 1 min: se recupera"), (60, ORANGE, f"T* + 1 min: comprometida")]:
        _, t, y = core.simulate_pulse(m, p, s, t_star + dt, xr, keep_traj=True)
        sel = t <= 6 * 3600
        axes[0].plot(t[sel] / 3600, y[m.idx["C3_star"], sel], color=color, label=label)
        axes[0].axvline((t_star + dt) / 3600, color=color, linewidth=0.8, linestyle=":")
    axes[0].set_xlabel("tiempo (h)")
    axes[0].set_ylabel("caspasa-3 activa (nM)")
    axes[0].set_yscale("log")
    axes[0].set_ylim(0.03, 300)
    axes[0].set_title(f"Pulso de apoptosoma S = {s} nM/s, T* = {t_star/60:.1f} min", color=INK, fontsize=9, loc="left")
    axes[0].legend(loc="center right")

    d = df[np.isfinite(df.T_star_min)]
    axes[1].plot(d.apaf_plateau_nM, d.T_star_min, color=BLUE, marker="o", markersize=4)
    axes[1].fill_between(d.apaf_plateau_nM, d.T_star_min, d.T_star_min.max() * 1.15, color=ORANGE, alpha=0.12, linewidth=0)
    axes[1].fill_between(d.apaf_plateau_nM, 0, d.T_star_min, color=BLUE, alpha=0.10, linewidth=0)
    axes[1].text(0.95, 0.9, "compromiso irreversible", transform=axes[1].transAxes, ha="right", color=INK2)
    axes[1].text(0.05, 0.12, "recuperacion", transform=axes[1].transAxes, ha="left", color=INK2)
    axes[1].set_xscale("log")
    axes[1].set_xlabel("intensidad del estimulo: meseta de Apaf-1 activo (nM)")
    axes[1].set_ylabel("duracion critica T* (min)")
    axes[1].set_title("Frontera del punto de no retorno", color=INK, fontsize=9, loc="left")
    _save(fig, "E2_punto_no_retorno_WT")
    return df


# --------------------------------------------------------------------------- E3
REGIME_LABELS = {
    "irreversible_PNR": "PNR",            # existe punto de no retorno alcanzable con el estimulo
    "irreversible_not_reached": "no alc.",  # biestable irreversible, pero S no basta en 6 h
    "reversible_activated": "rev.",        # la caspasa-3 se activa pero siempre se recupera: no hay PNR
    "no_activation": "sin act.",          # el estimulo no llega a activar caspasa-3 (resistencia)
    "spontaneous_death": "espont.",       # la celula en reposo ya esta en el estado de muerte
}


def _window_metrics(m, params, s=0.02):
    """Regimen dinamico + T* + ventana de anastasis para un juego de parametros.

    Ventana de anastasis = caspasa-3 activa maxima (% del total) alcanzada por una celula que aun se
    recupera al retirar el estimulo. Solo tiene sentido como "ventana antes de un PNR" en el regimen
    irreversible_PNR; en reversible_activated cualquier activacion es recuperable (no hay PNR)."""
    c3_total = params["k22prod"] / params["k22"]
    xr = core.resting_state(m, params)
    c3_rest = float(xr[m.idx["C3_star"]])
    if c3_rest > core.FATE_THRESHOLD_NM:
        return dict(regime="spontaneous_death", c3_rest_nM=c3_rest, c3_sustained_stimulus_nM=np.nan,
                    c3_after_withdrawal_nM=np.nan, irreversible=np.nan, T_star_min=0.0,
                    survivor_c3_peak_nM=np.nan, survivor_c3_peak_pct_total=np.nan)
    # Irreversibilidad: desde el estado activado con estimulo sostenido, retirar el estimulo.
    _, x_on = core.steady_state_c3(m, dict(params, k16prod=s), xr)
    c3_on = float(x_on[m.idx["C3_star"]])
    c3_off, _ = core.steady_state_c3(m, dict(params, k16prod=0.0), x_on)
    irreversible = c3_off > core.FATE_THRESHOLD_NM
    t_star = core.critical_duration(m, params, s, x_rest=xr, tol_s=10.0)
    out = dict(c3_rest_nM=c3_rest, c3_sustained_stimulus_nM=c3_on, c3_after_withdrawal_nM=c3_off,
               irreversible=irreversible, T_star_min=t_star / 60)
    if np.isfinite(t_star):
        below = core.simulate_pulse(m, params, s, max(t_star - 10.0, 0.0), xr)
        out.update(regime="irreversible_PNR", survivor_c3_peak_nM=below.c3_peak)
    elif c3_on <= core.FATE_THRESHOLD_NM:
        out.update(regime="no_activation", survivor_c3_peak_nM=c3_on)
    elif irreversible:
        out.update(regime="irreversible_not_reached", survivor_c3_peak_nM=np.nan)
    else:
        out.update(regime="reversible_activated", survivor_c3_peak_nM=c3_on)
    out["survivor_c3_peak_pct_total"] = 100 * out["survivor_c3_peak_nM"] / c3_total
    return out


def e3_sensitivity():
    m = load_legewie("WT")
    base = _window_metrics(m, m.params)
    rows = [dict(parameter="baseline", factor=1.0, **base)]
    for k in m.params:
        if k in ("cytosol", "k16prod"):
            continue
        for f in (0.5, 2.0):
            rows.append(dict(parameter=k, factor=f, **_window_metrics(m, core.with_params(m, **{k: m.params[k] * f}))))
    sens = pd.DataFrame(rows)
    sens.to_csv(OUT / "E3_sensitivity_one_at_a_time_WT.csv", index=False)

    # Escenarios dirigidos: XIAP (produccion) x degradacion de caspasa-3 activa (libre y unida a XIAP).
    grid = []
    xiap_f = [0.5, 1, 1.5, 2, 3, 4]
    deg_f = [1, 2, 4, 8, 16]
    for fx in xiap_f:
        for fd in deg_f:
            p = core.with_params(m, k18prod=m.params["k18prod"] * fx, k23=m.params["k23"] * fd, k24=m.params["k24"] * fd)
            grid.append(dict(xiap_production_factor=fx, active_c3_degradation_factor=fd, **_window_metrics(m, p)))
    g = pd.DataFrame(grid)
    g.to_csv(OUT / "E3_xiap_x_c3degradation_grid_WT.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.3))
    for ax, col, title in [(axes[0], "survivor_c3_peak_pct_total", "Ventana de anastasis:\ncaspasa-3 activa maxima compatible con recuperacion (% del total)"),
                           (axes[1], "T_star_min", "Duracion critica T* (min) con S = 0.02 nM/s")]:
        piv = g.pivot(index="xiap_production_factor", columns="active_c3_degradation_factor", values=col)
        vals = piv.values.astype(float)
        shown = np.where(np.isfinite(vals), vals, np.nan)
        im = ax.imshow(shown, cmap="Blues", origin="lower", aspect="auto")
        for i in range(vals.shape[0]):
            for j in range(vals.shape[1]):
                v = vals[i, j]
                reg = g[(g.xiap_production_factor == piv.index[i]) & (g.active_c3_degradation_factor == piv.columns[j])].regime.item()
                num = "" if np.isnan(v) else ("inf" if not np.isfinite(v) else f"{v:.0f}" if v >= 10 else f"{v:.1f}")
                txt = num + ("" if reg == "irreversible_PNR" else f"\n{REGIME_LABELS[reg]}")
                ax.text(j, i, txt.strip(), ha="center", va="center", fontsize=7,
                        color="white" if np.isfinite(v) and v > np.nanmax(shown[np.isfinite(shown)]) * 0.55 else INK)
        ax.set_xticks(range(len(piv.columns)), [f"x{c:g}" for c in piv.columns])
        ax.set_yticks(range(len(piv.index)), [f"x{r:g}" for r in piv.index])
        ax.set_xlabel("degradacion de caspasa-3 activa (k23, k24)")
        ax.set_ylabel("produccion de XIAP (k18prod)")
        ax.set_title(title, color=INK, fontsize=8, loc="left")
        ax.grid(False)
    fig.text(0.01, -0.12, "rev. = la caspasa-3 se activa pero siempre se recupera (sin PNR); sin act. = el estimulo no activa caspasa-3;\n"
             "espont. = apoptosis espontanea en reposo. Celdas sin etiqueta: existe punto de no retorno.", color=MUTED, fontsize=7)
    _save(fig, "E3_ventana_anastasis_XIAP_degradacion")
    return base, sens, g


def _global_job(args):
    i, factors = args
    p = core.with_params(_M, **{k: _M.params[k] * f for k, f in factors.items()})
    return dict(sample=i, **{f"factor_{k}": v for k, v in factors.items()}, **_window_metrics(_M, p))


def e3b_global_robustness(n_samples=1500, spread=3.0):
    """Muestreo global: todos los parametros cineticos multiplicados por factores log-uniformes en
    [1/spread, spread]. Pregunta: existe algun juego de parametros en esta topologia donde coexistan
    un punto de no retorno y supervivientes con activacion sustancial de caspasa-3?"""
    m = load_legewie("WT")
    keys = [k for k in m.params if k not in ("cytosol", "k16prod")]
    rng = np.random.default_rng(SEED + 1)
    jobs = [(i, {k: float(np.exp(rng.uniform(-np.log(spread), np.log(spread)))) for k in keys}) for i in range(n_samples)]
    with ProcessPoolExecutor(initializer=_init_worker) as ex:
        df = pd.DataFrame(list(ex.map(_global_job, jobs, chunksize=10)))
    df["data_provenance"] = "SIMULATED"
    df.to_csv(OUT / "E3b_global_parameter_sampling_WT.csv", index=False)

    counts = df.regime.value_counts().reindex(list(REGIME_LABELS), fill_value=0)
    pnr = df[df.regime == "irreversible_PNR"].survivor_c3_peak_pct_total
    rev = df[df.regime == "reversible_activated"].survivor_c3_peak_pct_total
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.2), gridspec_kw={"width_ratios": [1, 1.5]})
    names = ["PNR", "irrev. no\nalcanzado", "reversible\nactivada", "sin\nactivacion", "apoptosis\nespontanea"]
    axes[0].barh(names[::-1], counts.values[::-1], color=BLUE, height=0.6)
    for y, v in enumerate(counts.values[::-1]):
        axes[0].text(v, y, f" {v}", va="center", color=INK2, fontsize=8)
    axes[0].set_xlabel(f"juegos de parametros (n = {len(df)})")
    axes[0].set_title("Regimen dinamico", color=INK, fontsize=9, loc="left")
    axes[0].grid(axis="y", visible=False)
    bins = np.linspace(0, 100, 51)
    axes[1].hist(pnr, bins=bins, color=BLUE, histtype="step", linewidth=2, label=f"con PNR (n={len(pnr)})")
    axes[1].hist(rev, bins=bins, color=ORANGE, histtype="step", linewidth=2, label=f"reversible, sin PNR (n={len(rev)})")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("caspasa-3 activa maxima compatible con recuperacion (% del total)")
    axes[1].set_ylabel("juegos de parametros")
    axes[1].set_title("Ventana de anastasis segun regimen", color=INK, fontsize=9, loc="left")
    axes[1].legend()
    _save(fig, "E3b_robustez_global")

    return dict(n=len(df), regime_counts=counts.to_dict(),
                pnr_window_pct_quantiles=pnr.quantile([0.5, 0.9, 0.99, 1.0]).round(2).to_dict() if len(pnr) else {},
                pnr_sets_with_window_over_10pct=int((pnr > 10).sum()),
                reversible_window_pct_median=float(rev.median()) if len(rev) else None)


# --------------------------------------------------------------------------- E4
_M = None
SAMPLED = ["k17prod", "k18prod", "k22prod"]  # produccion de caspasa-9, XIAP, caspasa-3


def _init_worker():
    global _M
    _M = load_legewie("WT")


def _simulate_cell(args):
    cell_id, scenario, factors, s, durations = args
    p = core.with_params(_M, **{k: _M.params[k] * f for k, f in factors.items() if k != "stimulus"})
    xr = core.resting_state(_M, p)
    out = []
    for T in durations:
        r = core.simulate_pulse(_M, p, s * factors["stimulus"], T * 60.0, xr)
        row = dict(cell_id=cell_id, scenario=scenario, pulse_min=T, committed=int(r.committed),
                   c3_final_nM=r.c3_final, c3_peak_nM=r.c3_peak, exposure_nM_min=r.exposure_nM_s / 60,
                   **{f"factor_{k}": v for k, v in factors.items()})
        row.update({f"w_{sp}": float(v) for sp, v in zip(_M.species, r.state_at_withdrawal)})
        out.append(row)
    return out


def e4_population(n_cells=600, cv=0.25):
    """Variabilidad celula-a-celula lognormal (CV=0.25) en produccion de proteinas y en la intensidad
    del estimulo. CV=0.25 es una SUPOSICION del orden de las CV de proteinas medidas en celulas
    individuales (Sigal et al. 2006, Nature 444:643; Spencer et al. 2009, Nature 459:428); no es un
    valor ajustado a un tipo celular concreto."""
    rng = np.random.default_rng(SEED)
    sigma = np.sqrt(np.log(1 + cv ** 2))
    durations = [5, 10, 15, 20, 30, 45, 60, 90]
    scenarios = {"normal": 1.0, "tumor_XIAP_x2": 2.0}
    jobs = []
    for scen, xiap_mean in scenarios.items():
        for i in range(n_cells):
            f = {k: float(rng.lognormal(-sigma ** 2 / 2, sigma)) for k in SAMPLED + ["stimulus"]}
            f["k18prod"] *= xiap_mean
            jobs.append((f"{scen}_{i:04d}", scen, f, 0.02, durations))
    with ProcessPoolExecutor(initializer=_init_worker) as ex:
        rows = [r for chunk in ex.map(_simulate_cell, jobs, chunksize=20) for r in chunk]
    df = pd.DataFrame(rows)
    # Separar supervivencia por anastasis (activo caspasa-3 y se recupero) de resistencia (nunca la activo).
    df["fate_class"] = np.select(
        [df.committed == 1, df.c3_peak_nM >= core.ACTIVATION_THRESHOLD_NM],
        ["committed", "recovered_after_activation"], default="never_activated")

    surv = (df.groupby(["scenario", "pulse_min"]).fate_class.value_counts(normalize=True)
            .unstack(fill_value=0.0).reset_index())
    for c in ["committed", "recovered_after_activation", "never_activated"]:
        if c not in surv:
            surv[c] = 0.0
    surv["fraction_survivors"] = 1 - surv.committed
    surv.to_csv(OUT / "E4_survival_curves.csv", index=False)

    # Determinante de la competencia para anastasis: cociente de produccion XIAP : caspasa-3 de cada celula.
    df["c3_peak_pct_total"] = 100 * df.c3_peak_nM / (C3_TOTAL_NM * df.factor_k22prod)
    df["xiap_c3_ratio"] = df.factor_k18prod / df.factor_k22prod
    longest = df[(df.scenario == "normal") & (df.pulse_min == max(durations))].copy()
    longest["ratio_quintile"] = pd.qcut(longest.xiap_c3_ratio, 5, labels=[f"Q{i}" for i in range(1, 6)])
    quint = longest.groupby("ratio_quintile", observed=True).agg(
        xiap_c3_ratio_median=("xiap_c3_ratio", "median"),
        committed=("committed", "mean"),
        recovered_after_activation=("fate_class", lambda s: (s == "recovered_after_activation").mean()),
        never_activated=("fate_class", lambda s: (s == "never_activated").mean()),
        n=("cell_id", "size")).reset_index()
    quint.to_csv(OUT / "E4_xiap_c3_ratio_quintiles_normal_90min.csv", index=False)
    df["data_provenance"] = "SIMULATED"
    df.to_csv(OUT / "E4_population_SIMULATED.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.3), sharey=True)
    layers = [("never_activated", BLUE, "sobrevive sin activar caspasa-3 (resistencia)"),
              ("recovered_after_activation", AQUA, "activa caspasa-3 y se recupera (tipo anastasis)"),
              ("committed", ORANGE, "comprometida")]
    for ax, scen, title in [(axes[0], "normal", "Celulas normales"), (axes[1], "tumor_XIAP_x2", "Escenario tumoral: XIAP x2")]:
        d = surv[surv.scenario == scen].sort_values("pulse_min")
        x = np.arange(len(d))
        bottom = np.zeros(len(d))
        for col, color, label in layers:
            vals = 100 * d[col].values
            ax.bar(x, vals, bottom=bottom, color=color, width=0.75, edgecolor="#fcfcfb", linewidth=1, label=label)
            bottom += vals
        ax.set_xticks(x, d.pulse_min.astype(int))
        ax.set_xlabel("duracion del pulso apoptotico (min)")
        ax.set_title(title, color=INK, fontsize=9, loc="left")
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("celulas (%)")
    axes[0].legend(loc="upper center", bbox_to_anchor=(1.05, -0.2), ncol=3, fontsize=7.5)
    _save(fig, "E4_poblacion_supervivencia")
    return df, surv


# --------------------------------------------------------------------------- E5
def e5_fate_prediction(df):
    m = load_legewie("WT")
    feats = [f"w_{s}" for s in m.species]
    rows = []
    for scen in df.scenario.unique():
        d = df[df.scenario == scen].reset_index(drop=True)
        # Solo condiciones con ambos destinos; agrupado por duracion de pulso (leave-one-duration-out)
        mixed = d.groupby("pulse_min").committed.agg(lambda c: 0 < c.mean() < 1)
        d = d[d.pulse_min.isin(mixed[mixed].index)].reset_index(drop=True)
        if d.pulse_min.nunique() < 3:
            continue
        X_all, y, groups = d[feats], d.committed.values, d.pulse_min.values
        models = {
            "logreg_C3star_only": (["w_C3_star"], make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))),
            "logreg_all_species": (feats, make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0))),
            "random_forest_all_species": (feats, RandomForestClassifier(n_estimators=300, random_state=SEED, min_samples_leaf=3)),
        }
        gkf = GroupKFold(n_splits=d.pulse_min.nunique())
        for name, (cols, mdl) in models.items():
            prob = np.zeros(len(d))
            for tr, te in gkf.split(X_all, y, groups):
                Xtr = np.log10(X_all.iloc[tr][cols].clip(lower=1e-9))
                Xte = np.log10(X_all.iloc[te][cols].clip(lower=1e-9))
                mdl.fit(Xtr, y[tr])
                prob[te] = mdl.predict_proba(Xte)[:, 1]
            rows.append(dict(scenario=scen, model=name, n=len(d), n_groups=d.pulse_min.nunique(),
                             prevalence_committed=y.mean(), roc_auc=roc_auc_score(y, prob),
                             pr_auc=average_precision_score(y, prob), brier=brier_score_loss(y, prob),
                             validation="GroupKFold leave-one-pulse-duration-out", data_provenance="SIMULATED"))
        rf = RandomForestClassifier(n_estimators=300, random_state=SEED, min_samples_leaf=3)
        rf.fit(np.log10(X_all.clip(lower=1e-9)), y)
        imp = pd.Series(rf.feature_importances_, index=[f.removeprefix("w_") for f in feats]).sort_values(ascending=False)
        imp.rename("rf_importance").to_csv(OUT / f"E5_feature_importance_{scen}.csv")
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "E5_fate_prediction_SIMULATED.csv", index=False)
    return res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    summary = {"data_provenance": "SIMULATED", "model": "Legewie2006 BIOMD0000000102 (WT) / 103 (NC)",
               "fate_threshold_nM": core.FATE_THRESHOLD_NM, "seed": SEED}
    print("E1 histeresis...");     summary["E1"] = e1_hysteresis()
    print("E2 mapa CPNR...");      e2 = e2_cpnr_map(); summary["E2"] = e2.replace({np.inf: None}).to_dict("records")
    print("E3 sensibilidad...");   base, sens, grid = e3_sensitivity(); summary["E3_baseline"] = base
    print("E3b robustez global..."); summary["E3b"] = e3b_global_robustness()
    print("E4 poblacion...");      pop, surv = e4_population(); summary["E4_survival"] = surv.to_dict("records")
    print("E5 prediccion...");     summary["E5"] = e5_fate_prediction(pop).to_dict("records")
    summary["runtime_s"] = round(time.time() - t0, 1)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    print(f"Listo en {summary['runtime_s']} s -> {OUT}")


if __name__ == "__main__":
    main()
