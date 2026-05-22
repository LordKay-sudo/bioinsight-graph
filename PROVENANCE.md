# Data provenance

## Dataset

| Field | Value |
|-------|--------|
| **Data version** | `opentargets-sample-demo-v1` |
| **Release date** | 2024-06-01 |
| **Scope** | Representative sample (~30 genes, ~12 diseases, ~105 associations) |
| **Inspiration** | [Open Targets Platform](https://platform.opentargets.org/) association model |

## Sources

- **Open Targets Platform (representative sample)** — [platform.opentargets.org](https://platform.opentargets.org/)  
  Licence: CC0 1.0 for platform data; use [official releases](https://platform-docs.opentargets.org/) for production analyses.

## Scientific scope

- Graph edges are **disease–target associations** with a single **score** (0–1).
- Scores indicate **correlative strength** in this demo slice, not causation, mechanism, or clinical actionability.
- This system does **not** provide diagnosis, treatment recommendations, or regulatory-grade evidence.

## API

Live metadata: `GET /api/v1/meta` (also exposed as MCP resource `bioinsight://meta` when using [embabel-mcp](https://github.com/LordKay-sudo/embabel-mcp)).

## Citations

If you reference this demo in a write-up, cite Open Targets and note the sample nature of the graph:

> Open Targets Platform, EMBL-EBI & Wellcome Sanger Institute. Representative sample used in BioInsight Graph demo.

## Updates

When ingesting a new data release, update `api/app/metadata.py` (`DATA_VERSION`, `RELEASE_DATE`, `SOURCES`) and re-seed Neo4j.
