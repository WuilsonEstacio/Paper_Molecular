from __future__ import annotations

import re
from pathlib import Path

import fitz
import pandas as pd

from config import ARTICLES_DIR, DOC_DIR
from classify_biomedical import classify
from search_articles import guess_topic, guess_evidence, score_relevance

CATALOG = DOC_DIR / "catalogo_biomedico_depurado.csv"
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>)]+")


def extract_first_page(path: Path) -> str:
    doc = fitz.open(str(path))
    try:
        return doc.load_page(0).get_text()
    finally:
        doc.close()


def guess_title(pdf_name: str, first_page_text: str) -> str:
    lines = [l.strip() for l in first_page_text.splitlines() if l.strip()]
    if lines:
        candidate = lines[0]
        if 8 < len(candidate) < 220 and not candidate.lower().startswith(("doi", "http")):
            return candidate
    return pdf_name.rsplit(".", 1)[0].replace("_", " ").strip()


def find_doi(text: str) -> str:
    m = DOI_RE.search(text)
    return m.group(0).rstrip(".,;") if m else "NO_VERIFICADO"


def main() -> None:
    df = pd.read_csv(CATALOG)
    tracked_names = {Path(str(p)).name.lower() for p in df["pdf_path"].dropna()}

    all_pdfs = sorted(ARTICLES_DIR.glob("*.pdf"))
    untracked = [p for p in all_pdfs if p.name.lower() not in tracked_names]

    print(f"PDFs totales: {len(all_pdfs)}  |  ya en catalogo: {len(all_pdfs) - len(untracked)}  |  sin catalogar: {len(untracked)}")

    existing_ids = df["id"].astype(str).tolist()
    n = 1
    new_rows = []
    for pdf in untracked:
        try:
            first_page = extract_first_page(pdf)
        except Exception as exc:
            first_page = ""
            print(f"AVISO: no se pudo leer {pdf.name}: {exc}")

        title = guess_title(pdf.name, first_page)
        doi = find_doi(first_page)
        topic = guess_topic(title)

        while f"MANUAL{n:04d}" in existing_ids:
            n += 1
        rec_id = f"MANUAL{n:04d}"
        n += 1

        estado, motivo, score = classify(title, "", "article")

        new_rows.append({
            "id": rec_id,
            "year": "NO_VERIFICADO",
            "authors": "NO_VERIFICADO",
            "title": title,
            "journal": "NO_VERIFICADO",
            "doi": doi,
            "pmid": "NO_VERIFICADO",
            "country": "NO_VERIFICADO",
            "topic": topic,
            "type": "article",
            "open_access": "YES",
            "url_source": "NO_VERIFICADO",
            "url_pdf": "",
            "pdf_path": str(pdf),
            "download_status": "DESCARGADO",
            "relevance": score_relevance(title),
            "evidence": guess_evidence(title),
            "observations": "Incorporado desde biblioteca manual preexistente (no via OpenAlex); titulo extraido de la primera pagina del PDF, requiere verificacion.",
            "Estado_inclusion": estado,
            "Motivo_inclusion_exclusion": motivo + " (fuente: biblioteca manual, titulo sin verificar por API)",
            "Relevancia_Paper1": score,
            "Relevancia_Paper2": score,
        })

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        combined = pd.concat([df, new_df], ignore_index=True)
    else:
        combined = df

    combined.to_csv(CATALOG, index=False, encoding="utf-8-sig")
    combined.to_excel(DOC_DIR / "catalogo_biomedico_depurado.xlsx", index=False)

    report = pd.DataFrame(new_rows)[["id", "title", "topic", "Estado_inclusion", "doi"]] if new_rows else pd.DataFrame()
    report.to_csv(DOC_DIR / "biblioteca_manual_incorporada.csv", index=False, encoding="utf-8-sig")
    print(f"agregados={len(new_rows)}")


if __name__ == "__main__":
    main()
