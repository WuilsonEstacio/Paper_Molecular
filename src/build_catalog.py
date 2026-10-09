from pathlib import Path

import pandas as pd

from config import CATALOG_CSV, CATALOG_XLSX, TOP50_XLSX, README_MD, ARTICLES_DIR


def main() -> None:
    df = pd.read_csv(CATALOG_CSV)
    df = df.drop_duplicates(subset=[c for c in ["doi", "title"] if c in df.columns])
    df = df.sort_values(by=["relevance", "year"], ascending=[False, False])
    with pd.ExcelWriter(CATALOG_XLSX, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="catalogo")
    df.head(50).to_excel(TOP50_XLSX, index=False)
    README_MD.write_text(
        "# Bibliografía\n\n"
        f"Fecha de ejecución: {pd.Timestamp.now():%Y-%m-%d %H:%M:%S}\n"
        f"Publicaciones encontradas: {len(df)}\n"
        f"Carpeta: {ARTICLES_DIR}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
