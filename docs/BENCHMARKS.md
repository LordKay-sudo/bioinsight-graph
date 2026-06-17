# Benchmarks

Measured size and performance of the BioInsight Graph (roadmap 5.3).

## Graph size — frozen slice (CI / default Docker)

Default dataset: **frozen slice v2** (`opentargets-24.06-frozen-slice-v2`).

| Metric | Value | How |
|--------|-------|-----|
| Genes (`Gene` nodes) | **500** | distinct `target_id` |
| Diseases (`Disease` nodes) | **20** | distinct `disease_id` |
| Proteins (`Protein` nodes) | **120** | `proteins[]` |
| `ASSOCIATED_WITH` edges | **3,005** | one per gene–disease association |
| Decomposed evidence rows | **8,719** | summed `evidence[]` across associations |
| `ENCODED_BY` edges | **120** | one per protein |

Reproduce:

```bash
py -3 -c "import json,pathlib; d=json.loads(pathlib.Path('api/tests/fixtures/opentargets_slice_v2.json').read_text(encoding='utf-8')); a=d['associations']; print('genes', len({r['target_id'] for r in a}), 'diseases', len({r['disease_id'] for r in a}), 'assocs', len(a))"
```

## Graph size — Open Targets bulk slice (production-scale sample)

Full FTP ingest via `scripts/download_opentargets_bulk.py` (Open Targets **24.06**, CC0 1.0).
Measured **2026-06-17** on Windows 10 after sharded `part-*.json` download fix:

| Metric | Value |
|--------|-------|
| Genes | **500** (`--max-genes 500`) |
| Diseases | **12,252** |
| Associations | **272,726** |

Reproduce:

```bash
py -3 scripts/download_opentargets_bulk.py --release 24.06 --max-genes 500
py -3 -c "import json,pathlib; d=json.loads(pathlib.Path('data/raw/opentargets_bulk.json').read_text(encoding='utf-8')); a=d['associations']; print('genes', len({r['target_id'] for r in a}), 'diseases', len({r['disease_id'] for r in a}), 'assocs', len(a))"
py -3 scripts/etl_opentargets.py --input data/raw/opentargets_bulk.json
py -3 scripts/seed_neo4j.py   # requires Neo4j
```

`data/raw/opentargets_bulk.json` is gitignored — generate locally.

## Ingest time (measured)

| Step | Time | Host |
|------|------|------|
| `build_frozen_slice.py` (generate slice + ETL → CSV) | **~2.1 s** | Windows 10, local Python 3 |
| `etl_opentargets.py` on bulk JSON (500 genes) | **~36 s** | Windows 10, 2026-06-17 |
| `seed_neo4j.py` (load CSV → Neo4j) | *record on your host* | depends on Neo4j + graph size |

Reproduce:

```bash
# Frozen slice ETL only (no DB):
Measure-Command { py -3 scripts/build_frozen_slice.py }   # PowerShell
# Bulk ETL:
Measure-Command { py -3 scripts/etl_opentargets.py --input data/raw/opentargets_bulk.json }
# Seed (requires Neo4j up):
Measure-Command { py -3 scripts/seed_neo4j.py }
```

## API latency (frozen slice)

Run the stack seeded with **frozen slice v2** (see [PLATFORM.md](./PLATFORM.md)), then:

```bash
py -3 scripts/benchmark_api.py --base-url http://localhost:8000 --iterations 200
```

The harness reports p50/p95/p99 per endpoint for `search`, `resolve`, `gene_detail`,
`gene_diseases`, `gene_evidence`, and `stats`. Record the table here with your host spec:

| Endpoint | p50 (ms) | p95 (ms) | p99 (ms) |
|----------|---------:|---------:|---------:|
| `search_genes` | 13.2 | 26.9 | 35.3 |
| `resolve_gene` | *run harness* | *run harness* | *run harness* |
| `gene_detail` | 10.3 | 21.4 | 28.9 |
| `gene_diseases` | 13.3 | 31.8 | 42.7 |
| `gene_evidence` | 12.5 | 22.7 | 32.1 |
| `stats` | 8.3 | 27.8 | 36.3 |

Previous frozen-slice run: **Windows 10**, Docker Compose stack, `benchmark_api.py --iterations 200` against `http://localhost:8001` (2026-06-11). Re-run after seeding to refresh `resolve_gene` and bulk-scale latency.

The frozen slice is small enough that latency is dominated by Neo4j round-trip + serialization rather than query complexity. Bulk seed (272k associations) will increase read latency — re-record after `seed_neo4j.py` on bulk CSV.

## Scaling note

- **CI / quick start:** frozen slice (`scripts/build_frozen_slice.py`).
- **Production-scale sample:** Open Targets bulk via fixed sharded downloader (`scripts/download_opentargets_bulk.py`); licence CC0 1.0 — see [PROVENANCE.md](../PROVENANCE.md).
