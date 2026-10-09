from __future__ import annotations

from pathlib import Path


def ensure_pysb_models() -> list[Path]:
    base = Path(__file__).resolve().parents[2] / "models" / "pysb"
    base.mkdir(parents=True, exist_ok=True)
    files = [
        base / "cell_injury_model.py",
        base / "apoptosis_model.py",
        base / "recovery_model.py",
        base / "cell_fate_model.py",
    ]
    for f in files:
        if not f.exists():
            f.write_text("# Placeholder for future PySB model\n", encoding="utf-8")
    return files
