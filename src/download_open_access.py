from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import requests

from config import ARTICLES_DIR, CATALOG_CSV
from utils import safe_filename, sha256_file
from validate_pdf import basic_pdf_quality


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("download")


def download_file(url: str, dest: Path) -> tuple[bool, str]:
    sess = requests.Session()
    sess.headers.update({"User-Agent": "PaperMolecular/1.0 (OA download)"})
    try:
        with sess.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("wb") as fh:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        fh.write(chunk)
        ok, reason = basic_pdf_quality(dest)
        return ok, reason
    except Exception as exc:
        return False, str(exc)


def main(limit: int = 100) -> None:
    df = pd.read_csv(CATALOG_CSV)
    for idx, row in df.head(limit).iterrows():
        if str(row.get("open_access", "")).upper() != "YES":
            continue
        url = str(row.get("url_pdf", ""))
        if not url or url == "nan":
            continue
        year = str(row.get("year", "NO_VERIFICADO"))[:4]
        author = safe_filename(str(row.get("authors", "NO_VERIFICADO")).split(";")[0].split(",")[0])
        title = safe_filename(str(row.get("title", "NO_VERIFICADO"))[:40])
        dest = ARTICLES_DIR / "99_Other" / f"{year}_{author}_{title}.pdf"
        if dest.exists():
            continue
        ok, reason = download_file(url, dest)
        df.at[idx, "pdf_path"] = str(dest) if ok else ""
        df.at[idx, "download_status"] = "DESCARGADO" if ok else f"ERROR:{reason}"
        if ok:
            df.at[idx, "observations"] = sha256_file(dest)
    df.to_csv(CATALOG_CSV, index=False, encoding="utf-8-sig")
    logger.info("done")


if __name__ == "__main__":
    main()
