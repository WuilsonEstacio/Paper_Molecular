from __future__ import annotations

import csv
import hashlib
from datetime import datetime
from pathlib import Path

from config import BASE_DIR, DOC_DIR


EXTS = {".pdf", ".docx", ".md", ".txt", ".csv", ".xlsx", ".xls", ".json", ".ipynb", ".py", ".r", ".sbml", ".xml", ".zip"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def category_for(path: Path) -> str:
    s = str(path).lower()
    if "documentacion" in s:
        return "documentation"
    if "articulos_libros" in s:
        return "library"
    if "src" in s:
        return "code"
    return "other"


def main() -> None:
    out = DOC_DIR / "inventario_proyecto.csv"
    rows = []
    for p in BASE_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXTS:
            rows.append({
                "ruta": str(p),
                "archivo": p.name,
                "extension": p.suffix.lower(),
                "tamano_bytes": p.stat().st_size,
                "hash_sha256": sha256_file(p),
                "fecha_modificacion": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                "categoria": category_for(p),
                "estado": "OK",
                "observaciones": "",
            })
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["ruta","archivo","extension","tamano_bytes","hash_sha256","fecha_modificacion","categoria","estado","observaciones"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"inventory_rows={len(rows)}")


if __name__ == "__main__":
    main()
