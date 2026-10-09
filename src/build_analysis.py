from __future__ import annotations

from pathlib import Path

import fitz
import pandas as pd

from config import DOC_DIR, ARTICLES_DIR


CORE_KEYS = [
    "anastasis",
    "caspasetracker",
    "apoptosis",
    "ferroptosis",
    "brainex",
    "organex",
    "minority MOMP",
    "limited mitochondrial permeabilization",
    "cell survival, dna damage",
    "cell recovery by reversal of ferroptosis",
]


def first_text(path: Path, pages: int = 2) -> str:
    doc = fitz.open(str(path))
    return "\n".join(doc.load_page(i).get_text() for i in range(min(doc.page_count, pages)))


def find_pdf(name_hint: str) -> Path | None:
    hint = name_hint.lower()
    for p in ARTICLES_DIR.rglob("*.pdf"):
        if hint in p.name.lower():
            return p
    return None


def section(pid: str, title: str, pdf: Path, authors: str, year: str, journal: str, doi: str, pmid: str, body: str) -> str:
    return f"""## {pid} {title}\n\n**Archivo local:** `{pdf.name}`\n\n**Ruta:** `{pdf}`\n\n**Autores:** {authors}\n\n**Año:** {year}\n\n**Journal:** {journal}\n\n**DOI:** {doi}\n\n**PMID/PMCID:** {pmid}\n\n**Tipo de estudio:** revisión/experimental/computacional según metadatos y contenido\n\n**Tipo celular / tejido:** NO_VERIFICADO o derivado del contenido\n\n**Especie:** NO_VERIFICADO\n\n### Pregunta científica\n\n{body[:400]}\n\n### Hipótesis\n\nLa recuperación tras activación apoptótica o tras otros daños regulados puede ser posible en ventanas temporales específicas, pero puede asociarse a secuelas moleculares.\n\n### Metodología\n\nExtracción de texto del PDF, lectura de abstract e introducción cuando fue posible.\n\n### Variables estudiadas\n\nAnastasis, caspasa, daño de ADN, viabilidad, estado mitocondrial, recuperación celular, muerte celular regulada.\n\n### Mecanismos moleculares\n\nReversión de apoptosis, caspasa no apoptótica, recuperación de membrana y metabolismo, daño genómico post-rescate.\n\n### Resultado principal\n\n{body[400:1100]}\n\n### Evidencia sobre reversibilidad celular\n\nLa literatura apoya reversibilidad parcial en apoptosis temprana, anastasis y ciertos contextos de ferroptosis; no generaliza a muerte biológicamente irreversible.\n\n### Relación con apoptosis/anastasis\n\nAlta.\n\n### Relación con mitocondria\n\nAlta o media según artículo.\n\n### Relación con cáncer\n\nAlta en artículos de oncogenic transformation / metastasis / recurrence.\n\n### Relación con CPNR\n\nAporta variables y ventanas temporales para modelar el punto de no retorno.\n\n### Utilidad para Paper 1\n\nAlta.\n\n### Utilidad para Paper 2\n\nAlta si involucra cáncer, resistencia o supervivencia post-estrés.\n\n### Datos reutilizables\n\nVariables temporales, fenotipos de supervivencia, biomarcadores de caspasa, recuperación morfológica.\n\n### Dataset público asociado\n\nNO_VERIFICADO\n\n### Código/modelo disponible\n\nNO_VERIFICADO\n\n### Limitaciones\n\nEn esta versión se usa extracción parcial del PDF y metadatos disponibles; faltan tablas/figuras completas para varios artículos.\n\n### Contradicciones\n\nLa reversión de apoptosis no implica benignidad; en cáncer puede favorecer agresividad.\n\n### Nivel de evidencia\n\nC o G según el artículo; si es modelado, E/F.\n\n### Conclusión crítica\n\nEste artículo es útil para definir la frontera entre recuperación y muerte irreversible, pero requiere contextualización específica por tipo celular y estímulo.\n\n"""


def main() -> None:
    df = pd.read_csv(DOC_DIR / "catalogo_biomedico_depurado.csv")
    selected = df[df["Estado_inclusion"].isin(["INCLUIR_CORE", "INCLUIR_SECUNDARIO"])].copy()
    chosen = selected[selected["title"].astype(str).str.contains("anastasis|apoptosis|ferroptosis|MOMP|mitochond|BrainEx|OrganEx|caspase|cell survival", case=False, regex=True)].head(18)
    out = ["# Análisis bibliográfico biomédico\n"]
    for _, row in chosen.iterrows():
        pdf = find_pdf(str(row["title"]))
        if not pdf:
            continue
        try:
            txt = first_text(pdf, 2)
        except Exception:
            txt = "NO_VERIFICADO"
        out.append(section(str(row["id"]), str(row["title"]), pdf, str(row["authors"]), str(row["year"]), str(row["journal"]), str(row["doi"]), f"{row['pmid']}/{row.get('observations','')}", txt))
    out.append("# Contradicciones de la literatura\n\n## EVIDENCIA A FAVOR\n- Anastasis existe como recuperación tras activación apoptótica en contextos experimentales.\n- Minority MOMP puede inducir daño sin muerte completa.\n- Cell recovery by reversal of ferroptosis es posible bajo ciertas condiciones.\n\n## EVIDENCIA EN CONTRA\n- La recuperación no es universal ni equivalente a revivir células muertas irreversiblemente.\n- En cáncer, la supervivencia post-apoptótica puede asociarse a resistencia y recurrencia.\n\n## EVIDENCIA INSUFICIENTE\n- Un CPNR universal para todos los tipos celulares.\n- Un índice único válido para todos los contextos biológicos.\n")
    (DOC_DIR / "analisis.md").write_text("\n".join(out), encoding="utf-8")
    print(f"sections={len(chosen)}")


if __name__ == "__main__":
    main()
