from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class DataSourceRecord:
    dataset_id: str
    accession: str
    source: str
    paper: str
    doi: str
    organism: str
    cell_type: str
    cancer_type: str
    experimental_condition: str
    treatment: str
    timepoints: str
    n_samples: str
    n_cells: str
    technology: str
    data_type: str
    labels_available: str
    features_available: str
    raw_available: str
    processed_available: str
    license: str
    url: str
    paper1_relevance: str
    paper2_relevance: str
    priority: str
    download_status: str


def load_catalog(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def standardize_origin(col: pd.Series) -> pd.Series:
    return col.fillna("DERIVED").replace({"": "DERIVED"})


def real_master_schema() -> list[str]:
    return [
        "global_sample_id", "study_id", "dataset_id", "sample_id", "patient_id", "cell_id", "cell_line",
        "species", "cell_type", "cancer_type", "condition", "treatment", "timepoint", "label",
        "label_type", "data_origin", "ATP", "ROS", "Ca2", "DeltaPsiM", "MOMP", "CytochromeC",
        "Caspase3", "Caspase8", "Caspase9", "DNA_damage", "MembraneIntegrity", "Mitophagy",
        "Autophagy", "Proteostasis", "transcription_state", "morphology"
    ]
