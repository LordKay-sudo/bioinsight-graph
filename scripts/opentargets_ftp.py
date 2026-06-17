"""Shared Open Targets FTP helpers (sharded JSON listings and streaming)."""
from __future__ import annotations

import json
import re
import urllib.request
from collections.abc import Iterator
from pathlib import Path

FTP_BASE = "https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/{release}/output/etl/json"

DEFAULT_EVIDENCE_SOURCES = (
    "chembl",
    "europepmc",
    "ot_genetics_portal",
    "expression_atlas",
    "impc",
    "eva",
    "gene_burden",
    "cancer_gene_census",
)


def ftp_dir_url(release: str, *parts: str) -> str:
    base = FTP_BASE.format(release=release).rstrip("/")
    suffix = "/".join(p.strip("/") for p in parts if p)
    return f"{base}/{suffix}/" if suffix else f"{base}/"


def list_part_files(dir_url: str) -> list[str]:
    with urllib.request.urlopen(dir_url, timeout=120) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    parts = sorted(set(re.findall(r'href="(part-[^"]+\.json)"', html)))
    if not parts:
        raise RuntimeError(f"No part-*.json files found at {dir_url}")
    return parts


def list_evidence_sources(release: str) -> list[str]:
    index_url = ftp_dir_url(release, "evidence")
    with urllib.request.urlopen(index_url, timeout=120) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    return sorted(
        m.replace("/", "")
        for m in re.findall(r'href="(sourceId=[^"/]+)/?"', html)
    )


def iter_json_lines(dir_url: str, *, label: str | None = None) -> Iterator[dict]:
    for part in list_part_files(dir_url):
        if label:
            print(f"  {label}: {part}...")
        part_url = f"{dir_url.rstrip('/')}/{part}"
        with urllib.request.urlopen(part_url, timeout=300) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if line:
                    yield json.loads(line)


def evidence_item_from_row(row: dict) -> dict:
    item = {
        "evidence_type": row.get("datatypeId") or row.get("evidence_type") or "unknown",
        "source": row.get("datasourceId") or row.get("source") or "opentargets",
        "score": float(row.get("score") or 0.0),
    }
    study_id = row.get("studyId") or row.get("study_id") or row.get("id")
    if study_id:
        item["study_id"] = str(study_id)
    return item


def attach_evidence(
    associations: list[dict],
    *,
    release: str,
    allowed_genes: set[str],
    sources: list[str] | None = None,
    max_per_pair: int = 25,
) -> int:
    """Merge Open Targets evidence shards into association dicts. Returns rows attached."""
    pair_index = {(a["target_id"], a["disease_id"]): a for a in associations}
    allowed_pairs = set(pair_index.keys())
    sources = sources or list(DEFAULT_EVIDENCE_SOURCES)
    attached = 0

    for source_dir in sources:
        dir_url = ftp_dir_url(release, "evidence", source_dir)
        try:
            rows = iter_json_lines(dir_url, label=source_dir)
        except Exception as exc:
            print(f"  skip {source_dir}: {exc}")
            continue

        for row in rows:
            target = row.get("targetId") or row.get("target_id")
            disease = row.get("diseaseId") or row.get("disease_id")
            if not target or not disease:
                continue
            if target not in allowed_genes:
                continue
            key = (target, disease)
            if key not in allowed_pairs:
                continue
            assoc = pair_index[key]
            evidence = assoc.setdefault("evidence", [])
            if len(evidence) >= max_per_pair:
                continue
            evidence.append(evidence_item_from_row(row))
            attached += 1

    for assoc in associations:
        evidence = assoc.get("evidence") or []
        if not evidence:
            continue
        primary = max(evidence, key=lambda e: e.get("score", 0))
        assoc["evidence_type"] = primary.get("evidence_type", "genetic_association")
        study_id = primary.get("study_id")
        if study_id:
            assoc["study_id"] = study_id

    return attached
