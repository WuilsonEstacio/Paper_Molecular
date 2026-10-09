from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import requests


@dataclass
class DatasetHit:
    dataset_id: str
    accession: str
    source: str
    query: str
    title: str
    url: str
    download_status: str
    notes: str


def search_europe_pmc(query: str, page_size: int = 10) -> list[dict]:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {"query": query, "format": "json", "pageSize": page_size}
    r = requests.get(url, params=params, timeout=40, headers={"User-Agent": "PaperMolecular/1.0"})
    r.raise_for_status()
    return r.json().get("resultList", {}).get("result", [])


def build_hits() -> list[DatasetHit]:
    queries = [
        "anastasis",
        "apoptosis time series",
        "caspase single cell",
        "mitochondrial depolarization",
        "ischemia reperfusion",
        "cancer apoptosis resistance",
        "senescence",
        "reprogramming",
    ]
    hits: list[DatasetHit] = []
    seen = set()
    for q in queries:
        for item in search_europe_pmc(q, page_size=5):
            accession = item.get("accession", "NO_VERIFICADO")
            title = item.get("title", "NO_VERIFICADO")
            key = (accession, title)
            if key in seen:
                continue
            seen.add(key)
            hits.append(
                DatasetHit(
                    dataset_id=accession if accession != "NO_VERIFICADO" else f"PMC_{len(hits)+1:04d}",
                    accession=accession,
                    source="EuropePMC",
                    query=q,
                    title=title,
                    url=f"https://europepmc.org/article/{item.get('source','')}/{accession}" if accession != "NO_VERIFICADO" else "NO_VERIFICADO",
                    download_status="NOT_DOWNLOADED",
                    notes=item.get("authorString", ""),
                )
            )
    return hits


def write_catalog(out_csv: Path) -> None:
    hits = build_hits()
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(asdict(hits[0]).keys()) if hits else ["dataset_id", "accession", "source", "query", "title", "url", "download_status", "notes"])
        writer.writeheader()
        for h in hits:
            writer.writerow(asdict(h))


if __name__ == "__main__":
    write_catalog(Path(__file__).resolve().parents[2] / "data" / "raw" / "dataset_hits_europepmc.csv")
