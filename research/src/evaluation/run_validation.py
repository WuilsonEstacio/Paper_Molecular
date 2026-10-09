from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupKFold, train_test_split

from models.baseline_ml import train_baselines
from preprocessing.prepare_dataset import UnverifiedDatasetError, load_and_prepare


def main(dataset_path: Path | None = None) -> None:
    base = Path(__file__).resolve().parents[2]
    target = "label"
    features = ["ATP", "DeltaPsiM", "ROS", "Calcium", "MOMP", "CytochromeC", "Caspase3", "Caspase9", "DNA_damage", "Membrane_integrity", "Mitophagy", "Proteostasis", "Transcription"]
    group_col = "study_id"

    if dataset_path is None:
        dataset_path = base / "data" / "processed" / "cpnr_dataset.csv"

    if not dataset_path.exists():
        print("NOT_EXECUTED: no existe un dataset real en research/data/processed/.")
        print("El unico dataset disponible hoy es research/data/external/SYNTHETIC_EXAMPLE_cpnr_dataset.csv, ")
        print("marcado data_provenance=SIMULATED, y load_and_prepare() lo rechaza deliberadamente.")
        print("Ver Fase 7 del plan (busqueda de datasets publicos reales) antes de reintentar esto.")
        return

    try:
        df = load_and_prepare(dataset_path, target, features, group_col)
    except UnverifiedDatasetError as exc:
        print(f"NOT_EXECUTED: {exc}")
        return
    X = df[[c for c in features if c in df.columns]]
    y = df[target].astype(int)
    groups = df[group_col] if group_col in df.columns else None
    if groups is not None and len(groups.unique()) >= 3:
        gkf = GroupKFold(n_splits=min(3, len(groups.unique())))
        train_idx, test_idx = next(gkf.split(X, y, groups))
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    results = train_baselines(X_train, y_train, X_test, y_test)
    out = pd.DataFrame([r.__dict__ for r in results])
    out = out.fillna("NOT_DEFINED")
    out_dir = base / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_dir / "baseline_validation.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
