from __future__ import annotations

import pandas as pd

from config import DOC_DIR, CATALOG_CSV
from utils import normalize_title


def main() -> None:
    df = pd.read_csv(CATALOG_CSV)
    df["title_norm"] = df["title"].astype(str).map(normalize_title)
    df["doi_norm"] = df["doi"].astype(str).str.lower().str.replace("https://doi.org/", "", regex=False)
    df["pmid_norm"] = df["pmid"].astype(str)
    dup = df[df.duplicated(subset=["doi_norm"], keep=False) | df.duplicated(subset=["title_norm"], keep=False)].copy()
    dup.to_csv(DOC_DIR / "duplicados.csv", index=False, encoding="utf-8-sig")
    print(f"dup_rows={len(dup)}")


if __name__ == "__main__":
    main()
