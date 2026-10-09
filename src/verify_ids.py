from __future__ import annotations

import difflib
import re
import time
from pathlib import Path

import pandas as pd
import requests

from config import DOC_DIR

CATALOG = DOC_DIR / "catalogo_biomedico_depurado.csv"
PARTIAL_CSV = DOC_DIR / "verificacion_pmid_doi_partial.csv"
OUT_CSV = DOC_DIR / "verificacion_pmid_doi.csv"
OUT_SUMMARY = DOC_DIR / "verificacion_pmid_doi_resumen.md"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
IDCONV = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
CROSSREF = "https://api.crossref.org/works/"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "PaperMolecular/1.0 (academic bibliographic verification; mailto:none)"})

_last_ncbi_call = 0.0
_last_crossref_call = 0.0


def _throttle(kind: str) -> None:
    global _last_ncbi_call, _last_crossref_call
    min_interval = 0.34 if kind == "ncbi" else 0.15
    last = _last_ncbi_call if kind == "ncbi" else _last_crossref_call
    now = time.monotonic()
    wait = min_interval - (now - last)
    if wait > 0:
        time.sleep(wait)
    if kind == "ncbi":
        _last_ncbi_call = time.monotonic()
    else:
        _last_crossref_call = time.monotonic()


def normalize_title(t: str) -> str:
    t = (t or "").lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def title_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def crossref_lookup(doi: str) -> dict | None:
    _throttle("crossref")
    try:
        r = SESSION.get(CROSSREF + requests.utils.quote(doi, safe=""), timeout=20)
        if r.status_code != 200:
            return None
        msg = r.json().get("message", {})
        title = (msg.get("title") or [""])[0]
        return {"crossref_title": title}
    except Exception:
        return None


def idconv_batch(dois: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for i in range(0, len(dois), 200):
        chunk = dois[i : i + 200]
        _throttle("ncbi")
        try:
            r = SESSION.get(
                IDCONV,
                params={"ids": ",".join(chunk), "format": "json", "tool": "PaperMolecularVerification"},
                timeout=40,
            )
            r.raise_for_status()
            for rec in r.json().get("records", []):
                key = (rec.get("doi") or "").lower()
                if key:
                    out[key] = rec
        except Exception:
            continue
    return out


def esearch_pubmed_by_doi(doi: str) -> str | None:
    _throttle("ncbi")
    try:
        r = SESSION.get(
            f"{EUTILS}/esearch.fcgi",
            params={"db": "pubmed", "term": f"{doi}[AID]", "retmode": "json"},
            timeout=20,
        )
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except Exception:
        return None


def esearch_pubmed_by_title(title: str) -> str | None:
    term = normalize_title(title)[:200]
    if not term:
        return None
    _throttle("ncbi")
    try:
        r = SESSION.get(
            f"{EUTILS}/esearch.fcgi",
            params={"db": "pubmed", "term": f"{term}[Title]", "retmode": "json", "retmax": 3},
            timeout=20,
        )
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except Exception:
        return None


def esummary_pubmed_title(pmid: str) -> str | None:
    _throttle("ncbi")
    try:
        r = SESSION.get(
            f"{EUTILS}/esummary.fcgi",
            params={"db": "pubmed", "id": pmid, "retmode": "json"},
            timeout=20,
        )
        r.raise_for_status()
        res = r.json().get("result", {})
        rec = res.get(pmid) or res.get(str(pmid))
        return (rec or {}).get("title")
    except Exception:
        return None


def load_partial() -> pd.DataFrame:
    if PARTIAL_CSV.exists():
        return pd.read_csv(PARTIAL_CSV)
    return pd.DataFrame()


def verify_row(row: pd.Series, idconv_map: dict[str, dict]) -> dict:
    cat_id = row["id"]
    title = str(row.get("title", ""))
    doi = str(row.get("doi", "")).strip()
    has_doi = bool(doi) and doi.upper() != "NO_VERIFICADO"
    old_pmid_raw = str(row.get("pmid", "")).strip()
    old_pmid = "" if old_pmid_raw.upper() in ("", "NAN", "NO_VERIFICADO") else old_pmid_raw

    def label(new_pmid: str, suffix: str = "") -> str:
        if not old_pmid:
            return f"ENCONTRADO_NUEVO{suffix}"
        return f"CONFIRMADO{suffix}" if old_pmid == new_pmid else f"CORREGIDO{suffix}"

    result = {
        "id": cat_id,
        "title": title,
        "doi": doi if has_doi else "NO_VERIFICADO",
        "pmid_original_europepmc": old_pmid if old_pmid.upper() != "NO_VERIFICADO" else "",
        "doi_status": "NO_DOI",
        "crossref_title": "",
        "doi_title_similarity": 0.0,
        "pmid_verificado": "",
        "pmcid_verificado": "",
        "pmid_fuente": "",
        "pmid_title_similarity": 0.0,
        "estado_verificacion": "NOT_FOUND",
        "notas": "",
    }

    if has_doi:
        cr = crossref_lookup(doi)
        if cr and cr.get("crossref_title"):
            sim = title_similarity(title, cr["crossref_title"])
            result["crossref_title"] = cr["crossref_title"]
            result["doi_title_similarity"] = round(sim, 3)
            result["doi_status"] = "VALID" if sim >= 0.55 else "MISMATCH_REVISAR"
        else:
            result["doi_status"] = "INVALID_O_NO_RESUELVE"

        idc = idconv_map.get(doi.lower())
        if idc and idc.get("status", "ok") != "error" and idc.get("pmid"):
            idc_pmid = str(idc.get("pmid", "")).strip()
            result["pmid_verificado"] = idc_pmid
            result["pmcid_verificado"] = str(idc.get("pmcid", "") or "")
            result["pmid_fuente"] = "NCBI_IDCONV_PMC"
            result["estado_verificacion"] = label(idc_pmid)
        else:
            pmid = esearch_pubmed_by_doi(doi)
            if pmid:
                pm_title = esummary_pubmed_title(pmid)
                sim2 = title_similarity(title, pm_title or "")
                result["pmid_title_similarity"] = round(sim2, 3)
                if sim2 >= 0.55:
                    result["pmid_verificado"] = pmid
                    result["pmid_fuente"] = "PUBMED_ESEARCH_DOI"
                    result["estado_verificacion"] = label(pmid)
                else:
                    result["estado_verificacion"] = "PMID_ENCONTRADO_BAJA_CONFIANZA"
                    result["notas"] = f"PubMed PMID {pmid} title similarity {sim2:.2f} bajo umbral"
            else:
                result["estado_verificacion"] = "SIN_PMID_EN_PUBMED"

    if not result["pmid_verificado"] and (not has_doi or result["estado_verificacion"] == "SIN_PMID_EN_PUBMED"):
        pmid = esearch_pubmed_by_title(title)
        if pmid:
            pm_title = esummary_pubmed_title(pmid)
            sim3 = title_similarity(title, pm_title or "")
            if sim3 >= 0.75:
                result["pmid_verificado"] = pmid
                result["pmid_fuente"] = "PUBMED_ESEARCH_TITLE"
                result["pmid_title_similarity"] = round(sim3, 3)
                result["estado_verificacion"] = label(pmid, "_POR_TITULO")
            else:
                result["notas"] = (result["notas"] + f"; title-search match {sim3:.2f} bajo umbral").strip("; ")

    return result


def main(limit: int | None = None) -> None:
    df = pd.read_csv(CATALOG)
    if limit:
        df = df.head(limit)

    done = load_partial()
    done_ids = set(done["id"]) if not done.empty else set()

    dois_all = [
        str(d).strip()
        for d in df["doi"].tolist()
        if str(d).strip() and str(d).strip().upper() != "NO_VERIFICADO"
    ]
    print(f"precargando ID Converter para {len(dois_all)} DOIs...")
    idconv_map = idconv_batch(dois_all)
    print(f"idconv resolvio {len(idconv_map)} registros")

    rows_out = [] if done.empty else done.to_dict("records")
    total = len(df)
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        if row["id"] in done_ids:
            continue
        res = verify_row(row, idconv_map)
        rows_out.append(res)
        if i % 20 == 0 or i == total:
            pd.DataFrame(rows_out).to_csv(PARTIAL_CSV, index=False, encoding="utf-8-sig")
            print(f"progreso {i}/{total}")

    out = pd.DataFrame(rows_out)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    counts = out["estado_verificacion"].value_counts().to_dict()
    doi_counts = out["doi_status"].value_counts().to_dict()
    mismatches = out[out["doi_status"] == "MISMATCH_REVISAR"]
    not_found = out[out["estado_verificacion"].isin(["NOT_FOUND", "SIN_PMID_EN_PUBMED"])]

    lines = [
        "# Verificacion PMID/DOI\n",
        f"Total registros: {len(out)}\n",
        "## Estado PMID\n",
        *(f"- {k}: {v}" for k, v in counts.items()),
        "\n## Estado DOI\n",
        *(f"- {k}: {v}" for k, v in doi_counts.items()),
        f"\n## DOIs con posible mismatch (similitud < 0.55) — revisar manualmente: {len(mismatches)}\n",
        *(f"- {r['id']}: {r['title'][:90]} (doi={r['doi']}, similitud={r['doi_title_similarity']})" for _, r in mismatches.iterrows()),
        f"\n## Sin PMID verificable tras todos los metodos: {len(not_found)}\n",
        *(f"- {r['id']}: {r['title'][:90]}" for _, r in not_found.head(60).iterrows()),
    ]
    OUT_SUMMARY.write_text("\n".join(lines), encoding="utf-8")

    if PARTIAL_CSV.exists():
        PARTIAL_CSV.unlink()
    print(f"verification_rows={len(out)}")
    print(counts)


if __name__ == "__main__":
    main()
