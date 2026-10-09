"""Contraste con datos reales: GSE90959 (anastasis en hepatocitos primarios de raton).

Implementa literalmente Documentacion/preregistro_GSE90959.md. data_provenance = REAL (datos) / DERIVED (estadisticos).
Uso: python -m evaluation.gse90959_brake_driver   (desde research/src)
"""
from __future__ import annotations

import gzip
import io
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

RESEARCH = Path(__file__).resolve().parents[2]
RAW = RESEARCH / "data" / "raw" / "GSE90959"
OUT = RESEARCH / "results" / "real_data"
FIG = RESEARCH / "figures"

BRAKES = ["Xiap", "Bcl2", "Cflar", "Bfar"]
DRIVERS = ["Casp3", "Casp9", "Apaf1", "Casp8", "Bid", "Bax", "Cycs", "Diablo", "Casp6"]
EXPLORATORY = ["Birc2", "Birc3", "Bcl2l1", "Mcl1", "Bak1", "Bbc3", "Pmaip1"]
EXPRESSED_MIN = 7.0
N_NULL = 10_000
SEED = 2026
RECOVERY = ["R3", "R6", "R24", "R48"]
GROUP_FROM_TREATMENT = {
    "treatment: Untreated": "Ctrl",
    "treatment: 4.5% EtOH, 5Hr": "R0",
    "treatment: 4.5% EtOH, 5Hr, fresh medium 3Hr": "R3",
    "treatment: 4.5% EtOH, 5Hr, fresh medium 6Hr": "R6",
    "treatment: 4.5% EtOH, 5Hr, fresh medium 24Hr": "R24",
    "treatment: 4.5% EtOH, 5Hr, fresh medium 48Hr": "R48",
}


def load_expression() -> tuple[pd.DataFrame, pd.Series]:
    with gzip.open(RAW / "GSE90959_series_matrix.txt.gz", "rt", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    gsm = next(l for l in lines if l.startswith("!Sample_geo_accession")).split("\t")[1:]
    treat = next(l for l in lines if l.startswith("!Sample_characteristics_ch1")).split("\t")[1:]
    groups = pd.Series([GROUP_FROM_TREATMENT[t.strip('"')] for t in treat], index=[g.strip('"') for g in gsm])
    start = lines.index("!series_matrix_table_begin") + 1
    end = lines.index("!series_matrix_table_end")
    expr = pd.read_csv(io.StringIO("\n".join(lines[start:end])), sep="\t", index_col=0)
    expr.columns = [c.strip('"') for c in expr.columns]
    return expr[groups.index], groups


def probe_to_gene(expr: pd.DataFrame) -> pd.DataFrame:
    with gzip.open(RAW / "GPL6887.annot.gz", "rt", encoding="utf-8") as fh:
        rows = [l for l in fh if not l.startswith(("!", "#", "^"))]
    ann = pd.read_csv(io.StringIO("".join(rows)), sep="\t", usecols=["ID", "Gene symbol"]).dropna()
    ann = ann[~ann["Gene symbol"].str.contains("///")].set_index("ID")["Gene symbol"]
    e = expr.loc[expr.index.intersection(ann.index)].copy()
    e["gene"] = ann.loc[e.index].values
    e["mean"] = e.drop(columns="gene").mean(axis=1)
    best = e.sort_values("mean", ascending=False).drop_duplicates("gene")  # sonda de mayor expresion media
    return best.set_index("gene").drop(columns="mean")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    expr, groups = load_expression()
    genes = probe_to_gene(expr)
    expressed = genes[genes.mean(axis=1) >= EXPRESSED_MIN]
    order = ["Ctrl", "R0"] + RECOVERY
    means = pd.DataFrame({g: expressed.loc[:, groups[groups == g].index].mean(axis=1) for g in order})
    lfc = means.sub(means["Ctrl"], axis=0).drop(columns="Ctrl")

    # Genes de los conjuntos: presencia y expresion
    status = []
    for name, members in (("brake", BRAKES), ("driver", DRIVERS), ("exploratory", EXPLORATORY)):
        for gname in members:
            status.append(dict(gene=gname, set=name, on_array=gname in genes.index,
                               mean_log2=float(genes.loc[gname].mean()) if gname in genes.index else np.nan,
                               expressed=gname in expressed.index))
    status = pd.DataFrame(status)
    brakes = [g for g in BRAKES if g in expressed.index]
    drivers = [g for g in DRIVERS if g in expressed.index]

    # Por gen: Welch frente a Ctrl, BH por tiempo
    ctrl = expressed.loc[:, groups[groups == "Ctrl"].index]
    per_gene = []
    for t in ["R0"] + RECOVERY:
        x = expressed.loc[:, groups[groups == t].index]
        tt, p = stats.ttest_ind(x, ctrl, axis=1, equal_var=False)
        q = stats.false_discovery_control(np.nan_to_num(p, nan=1.0), method="bh")
        per_gene.append(pd.DataFrame({"gene": expressed.index, "timepoint": t, "log2FC": lfc[t].values, "t": tt, "p": p, "q_BH": q}))
    per_gene = pd.concat(per_gene)
    model_genes = per_gene[per_gene.gene.isin(BRAKES + DRIVERS + EXPLORATORY)].copy()
    model_genes["set"] = model_genes.gene.map({**{g: "brake" for g in BRAKES}, **{g: "driver" for g in DRIVERS},
                                               **{g: "exploratory" for g in EXPLORATORY}})

    # Indice frenos-impulsores y nulo empirico
    rng = np.random.default_rng(SEED)
    pool = lfc.values
    n_b, n_d = len(brakes), len(drivers)
    idx_rows = []
    for t in ["R0"] + RECOVERY:
        col = lfc.columns.get_loc(t)
        obs = lfc.loc[brakes, t].mean() - lfc.loc[drivers, t].mean()
        null = np.empty(N_NULL)
        for i in range(N_NULL):
            pick = rng.choice(len(pool), n_b + n_d, replace=False)
            null[i] = pool[pick[:n_b], col].mean() - pool[pick[n_b:], col].mean()
        p_emp = (1 + np.sum(np.abs(null) >= abs(obs))) / (N_NULL + 1)
        idx_rows.append(dict(timepoint=t, index_brake_minus_driver=obs, null_sd=null.std(), p_empirical=p_emp,
                             mean_lfc_brakes=lfc.loc[brakes, t].mean(), mean_lfc_drivers=lfc.loc[drivers, t].mean()))
    idx = pd.DataFrame(idx_rows)
    rec = idx.timepoint.isin(RECOVERY)
    # Holm sobre los 4 tiempos de recuperacion
    pr = idx.loc[rec, "p_empirical"].values
    order_p = np.argsort(pr)
    holm = np.empty_like(pr)
    running = 0.0
    for rank, j in enumerate(order_p):
        running = max(running, min(1.0, (len(pr) - rank) * pr[j]))
        holm[j] = running
    idx["p_holm_recovery"] = np.nan
    idx.loc[rec, "p_holm_recovery"] = holm

    sig_pos = ((idx.index_brake_minus_driver > 0) & (idx.p_holm_recovery < 0.05)).any()
    sig_neg = ((idx.index_brake_minus_driver < 0) & (idx.p_holm_recovery < 0.05)).any()
    verdict = "APOYO" if sig_pos and not sig_neg else "CONTRADICCION" if sig_neg else "NO_CONCLUYENTE"

    status.to_csv(OUT / "GSE90959_gene_set_status.csv", index=False)
    model_genes.to_csv(OUT / "GSE90959_model_genes_per_timepoint.csv", index=False)
    idx.to_csv(OUT / "GSE90959_brake_driver_index.csv", index=False)
    summary = dict(dataset="GSE90959", data_provenance="REAL (expression) / DERIVED (statistics)",
                   n_samples=int(len(groups)), group_sizes=groups.value_counts().to_dict(),
                   n_genes_on_array=int(len(genes)), n_genes_expressed=int(len(expressed)),
                   brakes_used=brakes, drivers_used=drivers, verdict=verdict,
                   index=idx.replace({np.nan: None}).to_dict("records"))
    (OUT / "GSE90959_summary.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")

    # Figura: log2FC de cada gen de los conjuntos principales + indice
    from simulation.run_cpnr_simulations import BLUE, INK, MUTED, ORANGE, _save
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.4), gridspec_kw={"width_ratios": [1.5, 1]})
    hours = {"R0": 0, "R3": 3, "R6": 6, "R24": 24, "R48": 48}
    xs = list(hours.values())
    labels = []
    for g in brakes:
        axes[0].plot(xs, [lfc.loc[g, t] for t in hours], color=BLUE, linewidth=1.5, alpha=0.9)
        labels.append([lfc.loc[g, "R48"], g, BLUE])
    for g in drivers:
        axes[0].plot(xs, [lfc.loc[g, t] for t in hours], color=ORANGE, linewidth=1.2, alpha=0.75)
        labels.append([lfc.loc[g, "R48"], g, ORANGE])
    labels.sort()
    for i in range(1, len(labels)):  # separar etiquetas superpuestas
        labels[i][0] = max(labels[i][0], labels[i - 1][0] + 0.075)
    for y, g, c in labels:
        axes[0].text(49.5, y, g, color=c, fontsize=7, va="center")
    axes[0].axhline(0, color=MUTED, linewidth=0.8)
    axes[0].set_xticks(xs, ["R0", "R3", "R6", "R24", "R48"])
    axes[0].set_xlabel("tiempo de recuperacion tras retirar el etanol (h)")
    axes[0].set_ylabel("log2FC frente a control")
    axes[0].set_title("Frenos (azul) e impulsores (naranja) del interruptor", color=INK, fontsize=9, loc="left")
    axes[1].bar(range(len(idx)), idx.index_brake_minus_driver, color=[BLUE if v > 0 else ORANGE for v in idx.index_brake_minus_driver], width=0.6)
    axes[1].errorbar(range(len(idx)), np.zeros(len(idx)), yerr=1.96 * idx.null_sd, fmt="none", ecolor=MUTED, capsize=3, linewidth=1)
    ticks = [f"{r.timepoint}\np={r.p_empirical:.2f}" if pd.isna(r.p_holm_recovery) else f"{r.timepoint}\np={r.p_holm_recovery:.2f}"
             for _, r in idx.iterrows()]
    axes[1].set_xticks(range(len(idx)), ticks, fontsize=7)
    axes[1].set_ylabel("indice frenos − impulsores (log2)")
    axes[1].set_title("Indice y nulo aleatorio (±1.96 DE)\np de Holm en R3-R48", color=INK, fontsize=9, loc="left")
    fig.subplots_adjust(wspace=0.5)
    axes[1].grid(axis="x", visible=False)
    _save(fig, "D1_GSE90959_frenos_impulsores")
    print(json.dumps({k: summary[k] for k in ("n_genes_expressed", "brakes_used", "drivers_used", "verdict")}, indent=1))
    print(idx.round(4).to_string())
    print(status.to_string())


if __name__ == "__main__":
    main()
