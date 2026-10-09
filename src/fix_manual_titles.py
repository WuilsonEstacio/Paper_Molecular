from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import DOC_DIR
from verify_ids import crossref_lookup

CATALOG = DOC_DIR / "catalogo_biomedico_depurado.csv"

JUNK_MARKERS = ["loading", "skip to main content", "javascript", "please wait", "checking your browser", "verifying you"]


def filename_title(pdf_path: str) -> str:
    name = Path(pdf_path).stem
    return name.replace("_", " ").replace("  ", " ").strip()


def main() -> None:
    df = pd.read_csv(CATALOG)
    manual = df["id"].astype(str).str.startswith("MANUAL")

    fixed = []
    for idx in df[manual].index:
        row = df.loc[idx]
        title = str(row["title"])
        doi = str(row["doi"])
        old_title = title

        if doi and doi.upper() != "NO_VERIFICADO":
            cr = crossref_lookup(doi)
            if cr and cr.get("crossref_title"):
                df.at[idx, "title"] = cr["crossref_title"]
                fixed.append((row["id"], "crossref", old_title, cr["crossref_title"]))
                continue

        if any(j in title.lower() for j in JUNK_MARKERS) or len(title) < 12:
            new_title = filename_title(row["pdf_path"])
            df.at[idx, "title"] = new_title
            fixed.append((row["id"], "filename_fallback", old_title, new_title))

    df.to_csv(CATALOG, index=False, encoding="utf-8-sig")
    df.to_excel(DOC_DIR / "catalogo_biomedico_depurado.xlsx", index=False)

    rep = pd.DataFrame(fixed, columns=["id", "metodo", "titulo_anterior", "titulo_nuevo"])
    rep.to_csv(DOC_DIR / "biblioteca_manual_titulos_corregidos.csv", index=False, encoding="utf-8-sig")
    print(f"corregidos={len(fixed)}")
    for r in fixed:
        print(r)


if __name__ == "__main__":
    main()
