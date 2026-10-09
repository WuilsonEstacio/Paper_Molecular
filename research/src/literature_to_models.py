from __future__ import annotations

from pathlib import Path


def build_model_sources() -> list[dict]:
    return [
        {
            "model_name": "apoptosis_core",
            "paper_source": "MOMP / caspase signaling literature",
            "doi": "NO_VERIFICADO",
            "variables": ["BAX", "BAK", "BCL2", "MOMP", "CytochromeC", "Apaf1", "Caspase9", "Caspase3", "PARP"],
            "parameters": "NO_VERIFICADO",
            "units": "dimensionless / concentration dependent",
            "assumptions": "rule-based apoptosis network simplified for cell-fate transitions",
            "modifications": "prepared for anastasis extension",
            "validation_status": "NOT_YET_VALIDATED",
            "target_path": str(Path(__file__).resolve().parents[1] / "models" / "bionetgen" / "apoptosis_core.bngl"),
        },
        {
            "model_name": "anastasis_extension",
            "paper_source": "anastasis recovery literature",
            "doi": "NO_VERIFICADO",
            "variables": ["ROS", "DNA_damage", "Mitophagy", "Autophagy", "Proteostasis", "Recovery"],
            "parameters": "UNIDENTIFIED_PARAMETER",
            "units": "dimensionless / inferred",
            "assumptions": "recovery pathways can offset stress before irreversible commitment",
            "modifications": "extends apoptosis core with recovery edges",
            "validation_status": "CONCEPTUAL",
            "target_path": str(Path(__file__).resolve().parents[1] / "models" / "bionetgen" / "anastasis_extension.bngl"),
        },
    ]
