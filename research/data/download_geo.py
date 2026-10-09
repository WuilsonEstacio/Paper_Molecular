"""Descarga los datos publicos de GEO usados en el proyecto y verifica que son los mismos que se analizaron.

Los archivos no se incluyen en el repositorio; se obtienen de su fuente original (NCBI GEO).
Los SHA-256 esperados son los registrados el 2026-10-08 en Documentacion/simulacion_cpnr_resultados.md (seccion 7.1).

Uso (desde la raiz del repositorio):  python research/data/download_geo.py
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"
GEO = "https://ftp.ncbi.nlm.nih.gov/geo"
FILES = {
    "GSE90959/GSE90959_series_matrix.txt.gz": (
        f"{GEO}/series/GSE90nnn/GSE90959/matrix/GSE90959_series_matrix.txt.gz",
        "9f810806add13672a813fca4f1d2a73c1b50d23e5a3ccb10b53362db80b7c718"),
    "GSE90959/GPL6887.annot.gz": (
        f"{GEO}/platforms/GPL6nnn/GPL6887/annot/GPL6887.annot.gz",
        "b70966cc44a991c6cff3309eb2523b0a094694160698a723c98b7bba1816964f"),
    # GSE86480 se descargo pero se excluyo del analisis (sus columnas no tienen correspondencia publicada con las muestras).
    "GSE86480/GSE86480_genes.rpkm.gz": (
        f"{GEO}/series/GSE86nnn/GSE86480/suppl/GSE86480_genes.rpkm.gz",
        "505ec0b5f604b66a05ce1e25c91d36cd1dc1ed188b130d0af6bd57993d8ebff2"),
    "GSE86480/GSE86480_series_matrix.txt.gz": (
        f"{GEO}/series/GSE86nnn/GSE86480/matrix/GSE86480_series_matrix.txt.gz",
        "b3a01be839d691949ecdc4ebc5c3b094e2e7af17ad68deb394d01b25d1907bfc"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    mismatches = 0
    for rel, (url, expected) in FILES.items():
        dest = RAW / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            print(f"descargando {url}")
            urllib.request.urlretrieve(url, dest)
        got = sha256(dest)
        status = "OK" if got == expected else "DIFERENTE (GEO pudo actualizar el archivo; revisar antes de usar)"
        mismatches += got != expected
        print(f"{rel}: {status}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
