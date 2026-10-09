from __future__ import annotations

import logging
from dataclasses import dataclass

import requests
from lxml import etree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("metadata")


@dataclass
class MetaResult:
    doi: str = "NO_VERIFICADO"
    pmid: str = "NO_VERIFICADO"
    pmcid: str = "NO_VERIFICADO"
    title: str = "NO_VERIFICADO"
    journal: str = "NO_VERIFICADO"
    year: str = "NO_VERIFICADO"
    url_pdf: str = ""
    open_access: str = "NO"
    source: str = "NO_VERIFICADO"


def europe_pmc_lookup(query: str) -> list[dict]:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {"query": query, "format": "json", "pageSize": 5}
    r = requests.get(url, params=params, timeout=30, headers={"User-Agent": "PaperMolecular/1.0"})
    r.raise_for_status()
    return r.json().get("resultList", {}).get("result", [])


def pmc_pdf_url(pmcid: str) -> str:
    if not pmcid.startswith("PMC"):
        return ""
    num = pmcid.replace("PMC", "")
    return f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/"


def enrich_by_doi(doi: str) -> MetaResult:
    q = f'DOI:"{doi}"'
    try:
        rows = europe_pmc_lookup(q)
        if rows:
            r = rows[0]
            return MetaResult(
                doi=doi,
                pmid=r.get("pmid", "NO_VERIFICADO") or "NO_VERIFICADO",
                pmcid=r.get("pmcid", "NO_VERIFICADO") or "NO_VERIFICADO",
                title=r.get("title", "NO_VERIFICADO") or "NO_VERIFICADO",
                journal=r.get("journalTitle", "NO_VERIFICADO") or "NO_VERIFICADO",
                year=r.get("pubYear", "NO_VERIFICADO") or "NO_VERIFICADO",
                url_pdf=pmc_pdf_url(r.get("pmcid", "")) if r.get("pmcid") else "",
                open_access="YES" if r.get("isOpenAccess") == "Y" else "NO",
                source="EuropePMC",
            )
    except Exception as exc:
        logger.warning("Europe PMC DOI lookup failed for %s: %s", doi, exc)
    return MetaResult(doi=doi)
