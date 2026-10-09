from __future__ import annotations

from pathlib import Path

from literature_to_models import build_model_sources


def ensure_bionetgen_models() -> list[Path]:
    records = build_model_sources()
    paths = []
    for rec in records:
        path = Path(rec["target_path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(
                f"# {rec['model_name']}\n# paper_source: {rec['paper_source']}\n# doi: {rec['doi']}\n# status: {rec['validation_status']}\n",
                encoding="utf-8",
            )
        paths.append(path)
    return paths
