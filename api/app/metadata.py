"""Static dataset and service metadata served by GET /api/v1/meta."""

from datetime import date

SERVICE_NAME = "bioinsight-graph"
API_VERSION = "0.1.0"
DATA_VERSION = "opentargets-sample-demo-v1"
RELEASE_DATE = date(2024, 6, 1)

SOURCES = [
    {
        "name": "Open Targets Platform (representative sample)",
        "url": "https://platform.opentargets.org/",
        "license": "CC0 1.0 (platform data; see Open Targets terms for full releases)",
    },
]

DISCLAIMER = (
    "Demo/sample disease–target associations for exploration and integration testing only. "
    "Associations are correlative scores, not evidence of causation, diagnosis, or treatment. "
    "Not for clinical or regulatory use."
)

ASSOCIATIONS_ARE_CORRELATIVE = True
PROVENANCE_DOC_PATH = "PROVENANCE.md"
