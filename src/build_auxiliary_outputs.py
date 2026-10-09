from __future__ import annotations

import pandas as pd

from config import DOC_DIR

CATALOG = DOC_DIR / "catalogo_biomedico_depurado.csv"

# Temas obligatorios de las secciones 9-10 del documento maestro, con los patrones de texto
# (case-insensitive, sobre "title") que se consideran evidencia de que un registro toca el tema.
# Esto reemplaza las filas fabricadas a mano: cada conteo sale de una búsqueda real y reproducible
# sobre el catálogo depurado.
REQUIRED_THEMES: dict[str, list[str]] = {
    "Anastasis": ["anastasis"],
    "Minority MOMP / limited mitochondrial permeabilization": ["minority momp", "limited mitochondrial permeabili"],
    "Cytochrome-c": ["cytochrome c", "cytochrome-c", "cytochrome-c"],
    "BAX/BAK/BCL2": ["bax", "bak", "bcl-2", "bcl2"],
    "Mitochondrial membrane potential": ["membrane potential", "ΔΨm", "delta psi"],
    "Mitochondrial fragmentation": ["mitochondrial fragmentation"],
    "Mitophagy": ["mitophagy"],
    "ROS / oxidative stress": ["reactive oxygen", "oxidative stress", "oxidative damage"],
    "ATP / bioenergetics": [" atp ", "atp depletion", "bioenerget"],
    "Calcium homeostasis": ["calcium"],
    "DNA damage": ["dna damage"],
    "DNA repair": ["dna repair"],
    "Membrane repair / integrity": ["membrane repair", "membrane integrity"],
    "Ferroptosis (incl. reversal)": ["ferroptosis"],
    "Necroptosis": ["necroptosis"],
    "Pyroptosis": ["pyroptosis"],
    "Cellular senescence": ["senescence"],
    "Partial reprogramming / OSKM": ["reprogramming", "oskm", "yamanaka"],
    "Ischemia/reperfusion": ["ischemia", "ischaemia", "reperfusion"],
    "BrainEx/OrganEx": ["brainex", "organex", "restoration of brain"],
    "Cancer anastasis": ["anastasis"],  # se cruza con cancer_context abajo
    "Tumor recurrence": ["recurrence"],
    "Drug resistance / chemoresistance": ["chemoresistan", "drug resistan", "treatment resistan", "therapy resistan"],
    "Cell fate modeling": ["cell fate"],
    "Single-cell transcriptomics": ["single-cell", "single cell", "scrna"],
    "AI virtual cells / cellular digital twins": ["virtual cell", "digital twin"],
    "Computational/mathematical modeling of apoptosis": ["computational model", "mathematical model", "in silico"],
}

CANCER_CONTEXT = ["cancer", "tumor", "tumour", "malignan", "carcinoma", "oncogenic", "metastas"]


def real_gap_analysis(df: pd.DataFrame) -> pd.DataFrame:
    usable = df[df["Estado_inclusion"] != "EXCLUIR_NO_BIOMEDICO"].copy()
    titles = usable["title"].astype(str).str.lower()
    core_mask_all = usable["Estado_inclusion"] == "INCLUIR_CORE"

    rows = []
    for tema, patterns in REQUIRED_THEMES.items():
        hit = titles.apply(lambda t: any(p in t for p in patterns))
        if tema == "Cancer anastasis":
            cancer_hit = titles.apply(lambda t: any(c in t for c in CANCER_CONTEXT))
            hit = hit & cancer_hit
        existentes = int(hit.sum())
        core = int((hit & core_mask_all).sum())
        if core == 0:
            nivel = "ninguna"
        elif core <= 2:
            nivel = "baja"
        elif core <= 5:
            nivel = "parcial"
        else:
            nivel = "buena"
        rows.append({
            "Tema": tema,
            "Papers_existentes": existentes,
            "Papers_core": core,
            "Nivel_cobertura": nivel,
            "Necesita_busqueda": "yes" if core < 3 else "no",
        })
    return pd.DataFrame(rows)


def real_prisma_flow(df: pd.DataFrame) -> pd.DataFrame:
    identificados = len(df)
    duplicados_registrados = 0
    dup_path = DOC_DIR / "duplicados.csv"
    if dup_path.exists():
        try:
            duplicados_registrados = len(pd.read_csv(dup_path))
        except Exception:
            duplicados_registrados = 0
    excluidos_no_biomedico = int((df["Estado_inclusion"] == "EXCLUIR_NO_BIOMEDICO").sum())
    pendiente = int((df["Estado_inclusion"] == "PENDIENTE_VERIFICACION").sum())
    incluidos_core = int((df["Estado_inclusion"] == "INCLUIR_CORE").sum())
    incluidos_secundario = int((df["Estado_inclusion"] == "INCLUIR_SECUNDARIO").sum())

    return pd.DataFrame([
        {"fase": "identificados", "n": identificados},
        {"fase": "duplicados_detectados_openalex", "n": duplicados_registrados},
        {"fase": "excluidos_no_biomedico", "n": excluidos_no_biomedico},
        {"fase": "pendiente_verificacion", "n": pendiente},
        {"fase": "incluidos_core", "n": incluidos_core},
        {"fase": "incluidos_secundario", "n": incluidos_secundario},
    ])


def main() -> None:
    df = pd.read_csv(CATALOG)

    gap = real_gap_analysis(df)
    gap.to_csv(DOC_DIR / "gap_analysis.csv", index=False, encoding="utf-8-sig")

    prisma = real_prisma_flow(df)
    prisma.to_csv(DOC_DIR / "prisma_flow.csv", index=False, encoding="utf-8-sig")

    print("gap_analysis (temas con Papers_core < 3, necesitan busqueda):")
    print(gap[gap["Necesita_busqueda"] == "yes"].to_string(index=False))
    print()
    print("prisma_flow:")
    print(prisma.to_string(index=False))
    print()
    print(
        "NOTA: evidencia_cuantitativa.csv, matriz_cpnr.xlsx, datasets_catalog.csv y "
        "novelty_matrix.xlsx ya NO se generan aqui -- este script los llenaba con filas "
        "de ejemplo escritas a mano (ver plan Documentacion, Fase 3/6/7). Se completan con "
        "lectura real de articulos y busqueda real en APIs externas en scripts dedicados."
    )


if __name__ == "__main__":
    main()
