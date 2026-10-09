from __future__ import annotations

import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import requests

from config import ARTICLES_DIR, CATALOG_CSV, CATALOG_XLSX, LOG_DIR
from utils import normalize_title


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bibliografia")


QUERIES = [
    '"anastasis" OR "apoptosis reversal"',
    '"cell recovery" AND apoptosis',
    '"mitochondrial repair" OR "mitochondrial biogenesis"',
    '"DNA repair" AND "cell recovery"',
    '"partial reprogramming" AND rejuvenation',
    '"cell death" AND reversible',
    '"membrane repair" AND cell injury',
    '"ferroptosis" AND recovery',
    '"necroptosis" AND recovery',
    '"pyroptosis" AND recovery',
]


@dataclass
class Record:
    id: str
    year: str
    authors: str
    title: str
    journal: str
    doi: str
    pmid: str
    country: str
    topic: str
    type: str
    open_access: str
    url_source: str
    url_pdf: str
    pdf_path: str
    download_status: str
    relevance: int
    evidence: str
    observations: str


def openalex_search(query: str, per_page: int = 25, pages: int = 2) -> Iterable[dict]:
    base = "https://api.openalex.org/works"
    sess = requests.Session()
    sess.headers.update({"User-Agent": "PaperMolecular/1.0 (bibliographic research)"})
    for page in range(1, pages + 1):
        params = {"search": query, "per-page": per_page, "page": page}
        try:
            r = sess.get(base, params=params, timeout=40)
            r.raise_for_status()
            yield from r.json().get("results", [])
        except Exception as exc:
            logger.warning("OpenAlex query failed for %s page %s: %s", query, page, exc)
            continue


def build_records() -> list[Record]:
    seen = set()
    out: list[Record] = []
    for q in QUERIES:
        for w in openalex_search(q):
            title = w.get("title") or ""
            norm = normalize_title(title)
            doi = (w.get("doi") or "").lower().replace("https://doi.org/", "")
            key = doi or norm
            if not title or key in seen:
                continue
            seen.add(key)
            authors = "; ".join(a["author"]["display_name"] for a in w.get("authorships", [])[:5] if a.get("author"))
            primary_location = w.get("primary_location") or {}
            source = primary_location.get("source") or {}
            best_oa = w.get("best_oa_location") or {}
            pdf_url = best_oa.get("pdf_url") or primary_location.get("pdf_url") or ""
            rec = Record(
                id=f"OA{len(out)+1:04d}",
                year=str(w.get("publication_year") or "NO_VERIFICADO"),
                authors=authors or "NO_VERIFICADO",
                title=title,
                journal=source.get("display_name", "NO_VERIFICADO"),
                doi=doi or "NO_VERIFICADO",
                pmid="NO_VERIFICADO",
                country="NO_VERIFICADO",
                topic=guess_topic(title),
                type=w.get("type", "article"),
                open_access="YES" if w.get("open_access", {}).get("is_oa") else "NO",
                url_source=w.get("id", "NO_VERIFICADO"),
                url_pdf=pdf_url,
                pdf_path="",
                download_status="NO_DESCARGADO",
                relevance=score_relevance(title),
                evidence=guess_evidence(title),
                observations="",
            )
            out.append(rec)
    return out


def guess_topic(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["anastasis", "apoptosis"]):
        return "Apoptosis_Anastasis"
    if any(k in t for k in ["mitochond", "mitophagy", "biogenesis"]):
        return "Mitocondria"
    if any(k in t for k in ["dna repair", "genome"]):
        return "DNA_Repair"
    if any(k in t for k in ["membrane repair"]):
        return "Membrane_Repair"
    if any(k in t for k in ["ros", "oxidative stress"]):
        return "ROS_Oxidative_Stress"
    if any(k in t for k in ["reprogramming", "yamanaka", "oskm", "rejuven"]):
        return "Reprogramming_Rejuvenation"
    if any(k in t for k in ["senescence"]):
        return "Senescence"
    if any(k in t for k in ["ferroptosis", "necroptosis", "pyroptosis"]):
        return "Other_Cell_Death"
    if any(k in t for k in ["model", "computational", "systems biology"]):
        return "Computational_Modeling"
    return "Cell_Regeneration"


def guess_evidence(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["review", "meta-analysis", "systematic review"]):
        return "E"
    if any(k in t for k in ["model", "simulation", "computational"]):
        return "D"
    return "C"


def score_relevance(title: str) -> int:
    t = title.lower()
    if any(k in t for k in ["anastasis", "apoptosis reversal", "partial reprogramming", "cellular rejuvenation"]):
        return 5
    if any(k in t for k in ["mitochondrial", "dna repair", "membrane repair", "senescence", "reprogramming"]):
        return 4
    return 3


def main() -> None:
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    recs = build_records()
    import pandas as pd
    df = pd.DataFrame([asdict(r) for r in recs])
    df.to_csv(CATALOG_CSV, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(CATALOG_XLSX, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="catalogo")
    print(f"records={len(df)}")


if __name__ == "__main__":
    main()
