from __future__ import annotations

import time

import pandas as pd
import requests

from config import DOC_DIR
from verify_ids import SESSION, _throttle

CATALOG = DOC_DIR / "catalogo_biomedico_depurado.csv"
OUT_CSV = DOC_DIR / "retractaciones.csv"

RETRACTION_TYPES = {"retraction", "removal"}
CONCERN_TYPES = {"expression_of_concern"}
CORRECTION_TYPES = {"correction", "erratum", "addendum", "corrigendum"}


def crossref_updates(doi: str) -> list[dict]:
    _throttle("crossref")
    try:
        r = SESSION.get(f"https://api.crossref.org/works/{requests.utils.quote(doi, safe='')}", timeout=20)
        if r.status_code != 200:
            return []
        return r.json().get("message", {}).get("update-to", []) or []
    except Exception:
        return []


def classify_updates(updates: list[dict]) -> str:
    types = {u.get("type", "").lower() for u in updates}
    if types & RETRACTION_TYPES:
        return "RETRACTADO"
    if types & CONCERN_TYPES:
        return "EXPRESION_DE_PREOCUPACION"
    if types & CORRECTION_TYPES:
        return "CORREGIDO"
    if updates:
        return "OTRA_ACTUALIZACION:" + ",".join(sorted(types))
    return "SIN_ALERTAS_ENCONTRADAS"


def main(limit: int | None = None) -> None:
    df = pd.read_csv(CATALOG)
    target = df[df["Estado_inclusion"].isin(["INCLUIR_CORE", "INCLUIR_SECUNDARIO"])].copy()
    target = target[target["doi"].astype(str).str.upper() != "NO_VERIFICADO"]
    if limit:
        target = target.head(limit)

    rows = []
    for i, (_, row) in enumerate(target.iterrows(), start=1):
        doi = str(row["doi"]).strip()
        updates = crossref_updates(doi)
        status = classify_updates(updates)
        rows.append({
            "id": row["id"],
            "title": row["title"],
            "doi": doi,
            "estado_retractacion": status,
            "detalle": "; ".join(f"{u.get('type')}@{u.get('updated', {}).get('date-time', '')}" for u in updates) if updates else "",
        })
        if i % 50 == 0:
            print(f"progreso {i}/{len(target)}")
            pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    counts = out["estado_retractacion"].value_counts().to_dict()
    print(f"total={len(out)}")
    print(counts)

    flagged = out[out["estado_retractacion"] != "SIN_ALERTAS_ENCONTRADAS"]
    if len(flagged):
        print("--- registros con alerta ---")
        print(flagged.to_string(index=False))

    df = df.merge(out[["id", "estado_retractacion"]], on="id", how="left")
    df["Estado_retractacion"] = df["estado_retractacion"].fillna("NO_VERIFICADO")
    df = df.drop(columns=["estado_retractacion"])
    df.to_csv(CATALOG, index=False, encoding="utf-8-sig")
    df.to_excel(DOC_DIR / "catalogo_biomedico_depurado.xlsx", index=False)


if __name__ == "__main__":
    main()
