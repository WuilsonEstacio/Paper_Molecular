from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from config import ARTICLES_DIR, DOC_DIR, THEME_DIRS

CATALOG = DOC_DIR / "catalogo_biomedico_depurado.csv"

TOPIC_TO_DIR = {
    "Apoptosis_Anastasis": "01_Apoptosis_Anastasis",
    "Mitocondria": "02_Mitocondria",
    "DNA_Repair": "03_DNA_Repair",
    "Membrane_Repair": "04_Membrane_Repair",
    "ROS_Oxidative_Stress": "05_ROS_Oxidative_Stress",
    "Reprogramming_Rejuvenation": "07_Reprogramming_Rejuvenation",
    "Senescence": "08_Senescence",
    "Other_Cell_Death": "09_Necroptosis_Ferroptosis_Pyroptosis",
    "Computational_Modeling": "10_Computational_Modeling",
    "Cell_Regeneration": "11_Cell_Regeneration",
}


def main() -> None:
    df = pd.read_csv(CATALOG)
    have_pdf = df[df["download_status"] == "DESCARGADO"].copy()

    moved = []
    not_found = []
    for idx, row in have_pdf.iterrows():
        src = Path(str(row["pdf_path"]))
        if not src.exists():
            candidates = list(ARTICLES_DIR.rglob(src.name))
            if not candidates:
                not_found.append((row["id"], row["pdf_path"]))
                continue
            src = candidates[0]
        folder_name = TOPIC_TO_DIR.get(str(row["topic"]), "99_Other")
        dest_dir = ARTICLES_DIR / folder_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        if dest.resolve() == src.resolve():
            continue
        if dest.exists():
            dest = dest_dir / f"{src.stem}__{row['id']}{src.suffix}"
        shutil.move(str(src), str(dest))
        df.at[idx, "pdf_path"] = str(dest)
        moved.append((row["id"], src.name, folder_name))

    df.to_csv(CATALOG, index=False, encoding="utf-8-sig")
    df.to_excel(DOC_DIR / "catalogo_biomedico_depurado.xlsx", index=False)

    rep = pd.DataFrame(moved, columns=["id", "archivo", "carpeta_destino"])
    rep.to_csv(DOC_DIR / "reorganizacion_biblioteca.csv", index=False, encoding="utf-8-sig")
    print(f"movidos={len(moved)} no_encontrados={len(not_found)}")
    for nf in not_found:
        print("NO_ENCONTRADO:", nf)


if __name__ == "__main__":
    main()
