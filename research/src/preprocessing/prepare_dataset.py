from __future__ import annotations

from pathlib import Path

import pandas as pd

ALLOWED_PROVENANCE = {"REAL", "SIMULATED", "DERIVED"}
MIN_ROWS = 30
MIN_GROUPS = 5


class UnverifiedDatasetError(Exception):
    """Raised when a dataset lacks explicit data provenance or is too small to support any metric."""


def load_and_prepare(path: Path, target_column: str, feature_columns: list[str], group_column: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)

    if "data_provenance" not in df.columns:
        raise UnverifiedDatasetError(
            f"{path} no tiene columna 'data_provenance'. Toda fila debe declarar "
            f"{sorted(ALLOWED_PROVENANCE)} (regla 36 del documento maestro). Abortando."
        )
    bad = set(df["data_provenance"].astype(str).unique()) - ALLOWED_PROVENANCE
    if bad:
        raise UnverifiedDatasetError(f"{path} tiene valores de data_provenance no permitidos: {bad}")
    if (df["data_provenance"] == "SIMULATED").any() or (df["data_provenance"] == "DERIVED").any():
        raise UnverifiedDatasetError(
            f"{path} contiene filas SIMULATED/DERIVED. No se calculan métricas de validación "
            "sobre datos no REAL. Usa este archivo solo para probar el esquema/código, nunca para reportar resultados."
        )

    cols = [c for c in feature_columns if c in df.columns]
    keep = cols + [target_column]
    if group_column and group_column in df.columns:
        keep.append(group_column)
    out = df[keep].dropna(subset=[target_column]).copy()

    if len(out) < MIN_ROWS:
        raise UnverifiedDatasetError(
            f"{path} tiene solo {len(out)} filas (mínimo {MIN_ROWS}). Insuficiente para cualquier "
            "métrica con significado estadístico; no se procede."
        )
    if group_column and group_column in df.columns:
        n_groups = df[group_column].nunique()
        if n_groups < MIN_GROUPS:
            raise UnverifiedDatasetError(
                f"{path} tiene solo {n_groups} grupos distintos en '{group_column}' (mínimo {MIN_GROUPS}). "
                "GroupKFold/leave-one-study-out no es significativo con tan pocos grupos; no se procede."
            )
    return out
