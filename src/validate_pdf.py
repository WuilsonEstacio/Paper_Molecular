from __future__ import annotations

from pathlib import Path


def is_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            return fh.read(5) == b"%PDF-"
    except Exception:
        return False


def basic_pdf_quality(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "MISSING"
    if path.stat().st_size < 10_000:
        return False, "TOO_SMALL"
    if not is_pdf(path):
        return False, "NOT_PDF"
    return True, "OK"
