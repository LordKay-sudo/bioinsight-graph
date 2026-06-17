"""Attach Open Targets evidence shards to an existing bulk associations JSON.

Skips re-downloading association parts — use after download_opentargets_bulk.py.

Usage:
    py -3 scripts/attach_opentargets_evidence.py \\
        --input data/raw/opentargets_bulk.json \\
        --output data/raw/opentargets_bulk_evidence.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from opentargets_ftp import DEFAULT_EVIDENCE_SOURCES, attach_evidence


def main() -> None:
    parser = argparse.ArgumentParser(description="Attach OT evidence to bulk JSON")
    parser.add_argument("--input", type=Path, required=True, help="Existing bulk JSON")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path")
    parser.add_argument("--release", default="24.06", help="Open Targets release")
    parser.add_argument(
        "--sources",
        nargs="*",
        default=None,
        help=f"Evidence source ids (default: {', '.join(DEFAULT_EVIDENCE_SOURCES)})",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")

    data = json.loads(args.input.read_text(encoding="utf-8"))
    associations: list[dict] = data.get("associations") or []
    if not associations:
        raise SystemExit("No associations in input JSON")

    allowed_genes = {a["target_id"] for a in associations}
    release = data.get("meta", {}).get("release") or args.release

    print(f"Attaching evidence for {len(associations)} associations ({len(allowed_genes)} genes)...")
    attached = attach_evidence(
        associations,
        release=release,
        allowed_genes=allowed_genes,
        sources=args.sources,
    )
    print(f"Attached {attached} evidence row(s)")

    meta = dict(data.get("meta") or {})
    meta["data_version"] = str(meta.get("data_version", f"opentargets-{release}-bulk")) + "-evidence"

    payload = {**data, "meta": meta, "associations": associations}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote -> {args.output}")


if __name__ == "__main__":
    main()
