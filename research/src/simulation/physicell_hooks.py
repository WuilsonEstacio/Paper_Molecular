from __future__ import annotations

from pathlib import Path


def ensure_physicell_scaffold() -> Path:
    base = Path(__file__).resolve().parents[2] / "models" / "physicell"
    base.mkdir(parents=True, exist_ok=True)
    readme = base / "README.md"
    if not readme.exists():
        readme.write_text(
            "# PhysiCell scaffold\n\nThis folder will host simplified multicellular simulations for the digital twin.\n",
            encoding="utf-8",
        )
    return readme
