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
import re
import sys
import urllib.request
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

FTP_BASE = "https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/{release}/output/etl/json"


def _list_part_files(assoc_dir_url: str) -> list[str]:
    with urllib.request.urlopen(assoc_dir_url, timeout=120) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    parts = sorted(set(re.findall(r'href="(part-[^"]+\.json)"', html)))
    if not parts:
        raise RuntimeError(f"No part-*.json files found at {assoc_dir_url}")
    return parts


def _iter_association_rows(assoc_dir_url: str) -> Iterator[dict]:
    for part in _list_part_files(assoc_dir_url):
        part_url = f"{assoc_dir_url}/{part}"
        print(f"  reading {part}...")
        with urllib.request.urlopen(part_url, timeout=300) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                yield json.loads(line)


def _target_id(row: dict) -> str | None:
    return row.get("targetId") or row.get("target_id")


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

    assoc_dir_url = f"{FTP_BASE.format(release=args.release)}/associationByOverallDirect/"
    print(f"Fetching associations from {assoc_dir_url} (sharded JSON parts; may take several minutes)...")

    allowed: set[str] = set()
    associations: list[dict] = []
    try:
        for row in _iter_association_rows(assoc_dir_url):
            target = _target_id(row)
            if not target:
                continue
            if target not in allowed and len(allowed) >= args.max_genes:
                continue
            if target not in allowed:
                allowed.add(target)
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
    except Exception as exc:
        print(
            "Bulk download failed. Use the frozen slice for offline/CI workflows:\n"
            "  py -3 scripts/build_frozen_slice.py\n"
            f"Error: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

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
    print(
        f"Wrote {len(associations)} associations for {len(allowed)} genes -> {args.output}"
    )


if __name__ == "__main__":
    main()
