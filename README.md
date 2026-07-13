# BioInsight Graph

**Disease–target knowledge graph** — ingest public association data into Neo4j, query via FastAPI, explore with a React/TypeScript UI.

[![CI](https://github.com/LordKay-sudo/bioinsight-graph/actions/workflows/ci.yml/badge.svg)](https://github.com/LordKay-sudo/bioinsight-graph/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776ab)](api/requirements.txt)
[![Neo4j 5](https://img.shields.io/badge/neo4j-5.x-008CC1)](docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)](api/app/main.py)
[![React 18](https://img.shields.io/badge/react-18-61dafb)](web/package.json)

---

## Overview

BioInsight Graph models how research datasets can become **queryable knowledge graphs**: structured ETL from open biomedical associations → Neo4j storage → documented REST API → researcher-facing explorer.

| Capability | Status |
|------------|--------|
| Neo4j via Docker + schema constraints | ✅ |
| Open Targets frozen slice (500 genes, 3k+ associations) | ✅ |
| Evidence on associations + `/genes/{id}/evidence` | ✅ |
| FastAPI search, compare, batch-lookup, gene-report export | ✅ |
| React search, gene/disease detail, compare pages | ✅ |
| Force-directed graph + evidence chart | ✅ |
| Jupyter notebook: one gene → API + Cypher + literature links | ✅ |
| Full Docker Compose stack | ✅ |
| GitHub Actions CI | ✅ |

**Data:** Open Targets **24.06** frozen slice — **500** genes, **20** diseases, **3,005** associations with typed evidence metadata. Demo/research use only — **not clinical-grade**. See [PROVENANCE.md](PROVENANCE.md).

![BioInsight Graph search UI](docs/screenshot-search.png)

### UI gallery

| Search | Force-directed graph | Gene detail | Compare | Disease |
|--------|----------------------|-------------|---------|---------|
| ![Search](docs/screenshot-search.png) | ![Graph](docs/screenshot-graph.png) | [Detail](docs/screenshot-gene-detail.png) | ![Compare](docs/screenshot-compare.png) | ![Disease](docs/screenshot-disease.png) |

Open the app: **http://localhost:8080** (Docker) or **http://localhost:5173** (dev). Docs: [GETTING_STARTED.md](docs/GETTING_STARTED.md) · [Notebook (4.4)](notebooks/one_gene_exploration.ipynb) · [PLATFORM.md](docs/PLATFORM.md) · [BENCHMARKS.md](docs/BENCHMARKS.md) · [ARCHITECTURE.md](docs/ARCHITECTURE.md) · Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md) · Ecosystem: [docs/PORTFOLIO_ROADMAP.md](docs/PORTFOLIO_ROADMAP.md)

### Demo walkthrough

![Demo walkthrough — search BRCA1 and open graph view](docs/demo-walkthrough.gif)

### Human-in-the-loop

Before trusting agent or MCP output, review associations in the web UI. See [docs/HUMAN_IN_THE_LOOP.md](docs/HUMAN_IN_THE_LOOP.md).

### GapForge (translational gap hunter)

Educational stalled-program analysis — **not** molecule design.

**Product home:** [github.com/LordKay-sudo/gapforge](https://github.com/LordKay-sudo/gapforge)

| Surface | URL / path |
|---------|------------|
| Design | [docs/GAPFORGE.md](docs/GAPFORGE.md) |
| Programs UI | `/programs` (Flurizan AD case study) |
| HITL review | `/gaps/review` |
| Seed | `data/gapforge/flurizan_case.json` → `scripts/seed_gapforge.py` |

Risk tiers: L0–L1 explore/summarize; **L2 hypotheses require human approve/reject**; L3 chemistry/dosing blocked.

### Non-goals

- **Not for clinical diagnosis or treatment decisions**
- Association scores are **correlative**, not causal — see `/api/v1/meta` disclaimer
- Does not replace Ensembl, Open Targets Platform, or regulatory-grade evidence pipelines

---

## Quick start

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/), Python 3.11+ (`py -3`), Node.js 20+.

```bash
git clone https://github.com/LordKay-sudo/bioinsight-graph.git
cd bioinsight-graph
cp .env.example .env

# 1 — Graph database
docker compose up -d neo4j

# 2 — Seed (from repo root, using api venv)
cd api && py -3 -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt   # Windows
cd ..\scripts
..\api\.venv\Scripts\python download_sample.py
..\api\.venv\Scripts\python etl_opentargets.py
..\api\.venv\Scripts\python seed_neo4j.py

# 3 — API
cd ..\api
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000

# 4 — Web (new terminal)
cd web && npm install && npm run dev
```

| Service | URL |
|---------|-----|
| Web UI | http://localhost:5173 |
| API docs | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 (`neo4j` / `changeme`) |

Try searching **BRCA1** in the UI, then open the gene detail view for associated diseases and proteins.

### Docker (all-in-one)

Runs Neo4j, seeds sample data, API, and nginx-served web UI:

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| **Web UI** | http://localhost:8080 |
| API docs | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |

#### MCP server (optional)

With [embabel-mcp](https://github.com/LordKay-sudo/embabel-mcp) cloned as a sibling directory (`../embabel-mcp`), set `OPENAI_API_KEY` in `.env`, then:

```bash
docker compose -f docker-compose.yml -f docker-compose.mcp.yml up --build
```

| Service | URL |
|---------|-----|
| MCP (SSE) | http://localhost:1337/sse |

Human review workflow: [docs/HUMAN_IN_THE_LOOP.md](docs/HUMAN_IN_THE_LOOP.md).

The `seed` service runs once per `compose up` (loads Open Targets–style sample data). To re-seed:

```bash
docker compose run --rm seed
```

---

## Architecture

```mermaid
flowchart LR
  subgraph ingest [Ingestion]
    OT[Open Targets sample]
    ETL[scripts/ ETL]
  end
  subgraph store [Storage]
    N4j[(Neo4j 5)]
  end
  subgraph serve [Application]
    API[FastAPI /api/v1]
    WEB[React + Vite]
  end
  OT --> ETL --> N4j
  N4j --> API
  API --> WEB
```

### Integrations (MCP + RAG)

BioInsight Graph is the full application (ETL → Neo4j → API → UI). Separate repos add agent or document layers via the same APIs — they do not replace this codebase:

```mermaid
flowchart TB
  UI[BioInsight Web UI :8080]
  API[BioInsight API :8000]
  N4j[(Neo4j)]
  MCP[embabel-mcp :1337]
  RAG[kg-rag-demo :8001]
  UI --> API --> N4j
  MCP --> API
  MCP -. optional .-> RAG
```

| Integration | Repository |
|-------------|------------|
| MCP tools + `research_gene` agent | [embabel-mcp](https://github.com/LordKay-sudo/embabel-mcp) |
| Citation-grounded document Q&A | [kg-rag-demo](https://github.com/LordKay-sudo/kg-rag-demo) |

---

## Graph model

```cypher
(:Gene {id, symbol, name})
(:Disease {id, name})
(:Protein {id, name})

(:Gene)-[:ASSOCIATED_WITH {score, source}]->(:Disease)
(:Protein)-[:ENCODED_BY]->(:Gene)
```

Unique constraints on `Gene.id`, `Disease.id`, and `Protein.id` — see `scripts/neo4j/init.cypher`.

### Entity–relationship diagram

```mermaid
erDiagram
  GENE ||--o{ ASSOCIATED_WITH : scores
  DISEASE ||--o{ ASSOCIATED_WITH : scores
  PROTEIN }o--|| GENE : encodes
  GENE {
    string id PK
    string symbol
    string name
  }
  DISEASE {
    string id PK
    string name
  }
  PROTEIN {
    string id PK
    string name
  }
  ASSOCIATED_WITH {
    float score
    string source
  }
```

---

## API

Base path: **`/api/v1`** · Interactive docs at **`/docs`** when the API is running.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Liveness + Neo4j connectivity |
| `GET` | `/meta` | Data version, sources, disclaimer ([PROVENANCE.md](PROVENANCE.md)) |
| `GET` | `/stats` | Node and relationship counts |
| `GET` | `/genes?q=` | Search genes by symbol or name |
| `GET` | `/resolve?query=&entity_type=` | Resolve symbol or disease name to canonical id (ambiguity notes) |
| `GET` | `/diseases?q=` | Search diseases |
| `GET` | `/genes/{id}` | Gene metadata + degree counts |
| `GET` | `/genes/{id}/diseases` | Diseases for a gene, ranked by `score` (`min_score`, `limit`) |
| `GET` | `/genes/{id}/neighbors` | 1-hop subgraph (JSON nodes + edges) |
| `GET` | `/genes/compare?symbols=` | Compare 2–5 genes; top diseases + overlap |
| `GET` | `/diseases/{id}` | Disease metadata + linked gene count |
| `GET` | `/diseases/{id}/genes` | Gene targets for a disease, ranked by `score` |
| `GET` | `/genes/{id}/evidence` | Evidence breakdown per disease association |
| `GET` | `/genes/{id}/external-links` | Ensembl, Open Targets, UniProt links |
| `POST` | `/genes/batch-lookup` | Resolve many symbols/ids at once |
| `GET` | `/export/gene-report?gene_id=` | Analyst export (JSON or TSV + provenance columns) |
| `GET` | `/export/subgraph?gene_id=` | Subgraph for force-directed visualization |

---

## Web application

| Route | Page |
|-------|------|
| `/` | Search genes and diseases (debounced, tabbed) |
| `/gene/:id` | Gene detail — evidence chart, external links, graph + neighbors |
| `/disease/:id` | Disease detail — ranked gene targets with score filter |
| `/compare` | Compare 2–5 genes — overlapping diseases highlighted |
| `/about` | Data provenance, schema, limitations |

![BRCA1 subgraph — force-directed 1-hop neighborhood](docs/screenshot-graph.png)

Full gene detail page (stats + graph + legend): [screenshot-gene-detail.png](docs/screenshot-gene-detail.png)

Stack: React 18, TypeScript, Vite. Dev server proxies `/api` → `localhost:8000`.

---

## Repository layout

```
bioinsight-graph/
├── .github/workflows/ci.yml
├── api/              # FastAPI + Dockerfile
├── web/              # React + nginx Dockerfile
├── scripts/          # download → ETL → seed_neo4j
├── docs/             # README screenshots
├── docker-compose.yml
├── Dockerfile.seed   # one-shot graph seed job
└── .env.example
```

---

## Development

```bash
# API tests (mocked Neo4j)
cd api && .\.venv\Scripts\python -m pytest -q

# Lint/typecheck web (Node 20+)
cd web && npm run build
```

### Roadmap

| Phase | Focus |
|-------|--------|
| 0–2 | Neo4j, ETL, FastAPI ✅ |
| 3 | React search + gene detail ✅ |
| 4 | Graph visualization + `/export/subgraph` ✅ |
| 5 | Docker Compose (api + web + neo4j + seed) ✅ |
| 6 | GitHub Actions CI ✅ |
| 7+ | Ranked API endpoints (gene/disease compare) ✅ |
| MCP | [embabel-mcp](https://github.com/LordKay-sudo/embabel-mcp) tools, resources, `research_gene` agent ✅ |

**Related project:** [kg-rag-demo](https://github.com/LordKay-sudo/kg-rag-demo) — unstructured documents → knowledge graph → RAG Q&A (optional MCP bridge).

---

## License

[MIT](LICENSE) © 2026 LordKay-sudo
