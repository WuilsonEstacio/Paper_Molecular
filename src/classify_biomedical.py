from __future__ import annotations

import pandas as pd

from config import CATALOG_CSV, DOC_DIR


CORE = ["anastasis", "apoptosis", "mitochond", "dna repair", "membrane repair", "reprogramming", "senescence", "ferroptosis", "necroptosis", "pyroptosis", "organex", "brainex", "cell fate", "cell death", "momp", "cytochrome c"]
EXCLUDE = ["psychological", "measurement", "education", "survey", "testing", "entomology"]

# "anastasis" también es un término de historia del arte (icono bizantino de la Resurrección)
# y de teología ("Anastasis" = doctrina de la resurrección del cuerpo). Cuando el único gatillo
# de CORE es esta palabra y el título trae señales claras de arte/teología, se excluye en vez
# de incluirse por coincidencia léxica. Confirmado manualmente: OA0002, OA0016 (auditoría 2026-08-27).
ANASTASIS_NON_BIOMEDICAL_CONTEXT = [
    "icon", "iconography", "fresco", "byzantine", "painting", "image",
    "doctrine of the resurrection", "resurrection of the body", "scripturally",
]


def classify(title: str, journal: str, typ: str) -> tuple[str, str, int]:
    t = f"{title} {journal} {typ}".lower()
    if any(k in t for k in EXCLUDE):
        return "EXCLUIR_NO_BIOMEDICO", "No biomédico según título/journal", 1
    if "anastasis" in t and not any(k in t for k in [c for c in CORE if c != "anastasis"]):
        if any(ctx in t for ctx in ANASTASIS_NON_BIOMEDICAL_CONTEXT):
            return "EXCLUIR_NO_BIOMEDICO", "Uso de 'anastasis' en sentido artístico/teológico, no biológico", 1
    if any(k in t for k in CORE):
        return "INCLUIR_CORE", "Relacionado directamente con hipótesis", 5
    if any(k in t for k in ["review", "systematic review", "meta-analysis", "perspective"]):
        return "INCLUIR_SECUNDARIO", "Contexto/revisión útil", 3
    return "PENDIENTE_VERIFICACION", "Insuficiente para decidir solo por metadatos", 2


def main() -> None:
    depurado = DOC_DIR / "catalogo_biomedico_depurado.csv"
    verified = DOC_DIR / "catalogo_biomedico_depurado_verificado.csv"
    if depurado.exists():
        source = depurado
    elif verified.exists():
        source = verified
    else:
        source = CATALOG_CSV
    df = pd.read_csv(source)

    before = df["Estado_inclusion"].copy() if "Estado_inclusion" in df.columns else None

    states = []
    motives = []
    rel = []
    for _, row in df.iterrows():
        st, mot, score = classify(str(row.get("title", "")), str(row.get("journal", "")), str(row.get("type", "")))
        states.append(st)
        motives.append(mot)
        rel.append(score)
    df["Estado_inclusion"] = states
    df["Motivo_inclusion_exclusion"] = motives
    df["Relevancia_Paper1"] = rel
    df["Relevancia_Paper2"] = rel

    if before is not None:
        changed = df[before.values != df["Estado_inclusion"].values][["id", "title", "Estado_inclusion", "Motivo_inclusion_exclusion"]].copy()
        changed.insert(2, "Estado_anterior", before[before.values != df["Estado_inclusion"].values].values)
        changed.to_csv(DOC_DIR / "clasificacion_cambios.csv", index=False, encoding="utf-8-sig")
        print(f"fuente={source.name} cambios={len(changed)}")
        if len(changed):
            print(changed.to_string(index=False))

    out = DOC_DIR / "catalogo_biomedico_depurado.csv"
    out_xlsx = DOC_DIR / "catalogo_biomedico_depurado.xlsx"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    df.to_excel(out_xlsx, index=False)
    print(df["Estado_inclusion"].value_counts().to_dict())


if __name__ == "__main__":
    main()
