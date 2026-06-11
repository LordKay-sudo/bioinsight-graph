# Benchmarks

Measured size and performance of the BioInsight Graph (roadmap 5.3). Numbers below are
for the **frozen slice v2** (`opentargets-24.06-frozen-slice-v2`), the default CI/demo
dataset. Latency is environment-dependent — reproduce with `scripts/benchmark_api.py`.

## Graph size (measured)

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

## Ingest time (measured)

| Step | Time | Host |
|------|------|------|
| `build_frozen_slice.py` (generate slice + ETL → CSV) | **~2.1 s** | Windows 10, local Python 3 |
| `seed_neo4j.py` (load CSV → Neo4j) | *record on your host* | depends on Neo4j |

Reproduce:

```bash
# ETL only (no DB):
Measure-Command { py -3 scripts/build_frozen_slice.py }   # PowerShell
# Seed (requires Neo4j up):
Measure-Command { py -3 scripts/seed_neo4j.py }
```

## API latency

Run the stack (see [PLATFORM.md](./PLATFORM.md)), then:

```bash
py -3 scripts/benchmark_api.py --base-url http://localhost:8000 --iterations 200
```

The harness reports p50/p95/p99 per endpoint for `search`, `gene_detail`,
`gene_diseases`, `gene_evidence`, and `stats`. Record the table here with your host spec:

| Endpoint | p50 (ms) | p95 (ms) | p99 (ms) |
|----------|---------:|---------:|---------:|
| `search_genes` | 13.2 | 26.9 | 35.3 |
| `gene_detail` | 10.3 | 21.4 | 28.9 |
| `gene_diseases` | 13.3 | 31.8 | 42.7 |
| `gene_evidence` | 12.5 | 22.7 | 32.1 |
| `stats` | 8.3 | 27.8 | 36.3 |

Measured on **Windows 10**, Docker Compose stack, frozen slice v2, `benchmark_api.py --iterations 200` against `http://localhost:8001` (2026-06-11).

The frozen slice is small enough that latency is dominated by Neo4j round-trip + serialization rather than query complexity.

## Scaling note

The frozen slice is intentionally small for reproducible CI. For production-scale
numbers, run the full Open Targets bulk ingest (`scripts/download_opentargets_bulk.py`,
see [PROVENANCE.md](../PROVENANCE.md)) and re-record this table.
