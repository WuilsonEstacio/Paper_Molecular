from __future__ import annotations

import pandas as pd

from config import CATALOG_CSV
from metadata import enrich_by_doi


def main(limit: int | None = None) -> None:
    df = pd.read_csv(CATALOG_CSV)
    rows = df.head(limit) if limit else df
    for idx, row in rows.iterrows():
        doi = str(row.get("doi", "")).strip()
        if not doi or doi.upper() == "NO_VERIFICADO":
            continue
        meta = enrich_by_doi(doi)
        if meta.pmid != "NO_VERIFICADO":
            df.at[idx, "pmid"] = meta.pmid
        if meta.pmcid != "NO_VERIFICADO":
            df.at[idx, "observations"] = f"PMCID={meta.pmcid}"
        if meta.url_pdf and not str(df.at[idx, "url_pdf"]).strip():
            df.at[idx, "url_pdf"] = meta.url_pdf
        if meta.open_access == "YES":
            df.at[idx, "open_access"] = "YES"
    df.to_csv(CATALOG_CSV, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
