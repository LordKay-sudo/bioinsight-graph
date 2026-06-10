"""Download Open Targets Platform bulk association + evidence files (full ingest).

Documented source: https://platform-docs.opentargets.org/data-access/datasets
Default release: 24.06 (June 2024) from FTP.

Usage (requires network + disk; not run in CI):

    py -3 scripts/download_opentargets_bulk.py --release 24.06 --max-genes 500
    py -3 scripts/etl_opentargets.py --input data/raw/opentargets_bulk.json
    py -3 scripts/seed_neo4j.py

For CI and quick local dev, use the frozen slice instead:

    py -3 scripts/build_frozen_slice.py
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

# Open Targets FTP layout (associationByOverallDirect + evidence parquet as JSON export path)
FTP_BASE = "https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/{release}/output/etl/json"


def _fetch_json(url: str) -> list[dict]:
    with urllib.request.urlopen(url, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Open Targets bulk slice")
    parser.add_argument("--release", default="24.06", help="Open Targets release folder, e.g. 24.06")
    parser.add_argument("--max-genes", type=int, default=500, help="Cap unique targets in output JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=RAW_DIR / "opentargets_bulk.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    base = FTP_BASE.format(release=args.release)
    assoc_url = f"{base}/associationByOverallDirect"
    print(f"Fetching associations from {assoc_url} (this may take several minutes)...")
    try:
        rows = _fetch_json(assoc_url)
    except Exception as exc:
        print(
            "Bulk download failed. Use the frozen slice for offline/CI workflows:\n"
            "  py -3 scripts/build_frozen_slice.py\n"
            f"Error: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    gene_ids: list[str] = []
    seen_genes: set[str] = set()
    associations: list[dict] = []
    for row in rows:
        target = row.get("targetId") or row.get("target_id")
        if not target or target in seen_genes:
            continue
        seen_genes.add(target)
        gene_ids.append(target)
        if len(gene_ids) >= args.max_genes:
            break

    allowed = set(gene_ids)
    for row in rows:
        target = row.get("targetId") or row.get("target_id")
        if target not in allowed:
            continue
        disease = row.get("diseaseId") or row.get("disease_id")
        score = row.get("score") or row.get("associationScore") or 0.0
        associations.append(
            {
                "target_id": target,
                "symbol": row.get("targetSymbol", target),
                "name": row.get("targetName", target),
                "disease_id": disease,
                "disease_name": row.get("diseaseName", disease),
                "score": float(score),
                "source": "opentargets",
                "evidence_type": "genetic_association",
                "evidence": [
                    {
                        "evidence_type": "genetic_association",
                        "source": "opentargets",
                        "score": float(score),
                    }
                ],
            }
        )

    payload = {
        "meta": {
            "data_version": f"opentargets-{args.release}-bulk",
            "source": "opentargets-ftp",
            "release": args.release,
        },
        "associations": associations,
        "proteins": [],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(associations)} associations for {len(gene_ids)} genes -> {args.output}")


if __name__ == "__main__":
    main()
