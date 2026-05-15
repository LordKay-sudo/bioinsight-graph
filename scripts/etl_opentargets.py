"""Transform raw Open Targets-style JSON into processed CSV for seeding."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "opentargets_sample.json"
OUT_DIR = ROOT / "data" / "processed"


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Run download_sample.py first. Missing: {RAW_PATH}")

    with RAW_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    associations = pd.DataFrame(data["associations"])
    proteins = pd.DataFrame(data["proteins"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    associations.to_csv(OUT_DIR / "associations.csv", index=False)
    proteins.to_csv(OUT_DIR / "proteins.csv", index=False)

    print(f"Processed {len(associations)} associations, {len(proteins)} proteins")


if __name__ == "__main__":
    main()
