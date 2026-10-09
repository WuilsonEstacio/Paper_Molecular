import hashlib
import re
from pathlib import Path


INVALID_WIN_CHARS = r'\\/:*?"<>|'


def normalize_text(value: str) -> str:
    value = value or ""
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def normalize_title(value: str) -> str:
    value = normalize_text(value)
    value = re.sub(r"[^\w\s-]", "", value)
    return value


def safe_filename(value: str, max_len: int = 90) -> str:
    value = value.strip()
    for ch in INVALID_WIN_CHARS:
        value = value.replace(ch, "_")
    value = re.sub(r"\s+", "_", value)
    return value[:max_len].strip("._")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
