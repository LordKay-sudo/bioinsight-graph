# BioInsight Graph

Research-oriented prototype that ingests public biological association data, loads it into **Neo4j**, and exposes it through a **Python FastAPI** API and **React + TypeScript** explorer UI.

Built as portfolio work aligned with data-intensive research platforms (e.g. knowledge extraction from datasets, graph storage, researcher-facing APIs and UIs).

---

## Goals

- Demonstrate **ETL → knowledge graph → API → UI** for structured biological data
- Show production-minded habits: seed data, tests, Docker, clear schema, OpenAPI docs
- Stay small enough to ship in ~4 weeks part-time

**Non-goals (MVP):** ML model training, full UniProt scale, auth beyond basic API key (optional later)

---

## Tech stack

| Layer | Choice |
|-------|--------|
| Graph DB | Neo4j 5.x (Community via Docker) |
| API | Python 3.11+, FastAPI, Pydantic, httpx |
| ETL | pandas, optional `neo4j` official driver |
| Frontend | React 18, TypeScript, Vite |
| Graph viz | `react-force-graph` or `vis-network` (pick one) |
| Infra | Docker Compose; optional K8s manifests in `/deploy` |
| CI | GitHub Actions: lint, test, build |

---

## Architecture

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Public     │     │  ETL / seed  │     │   Neo4j     │
│  datasets   │ ──► │  (scripts/)  │ ──► │  (Cypher)   │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                     ┌──────────────┐           │
                     │   FastAPI    │ ◄─────────┘
                     │   (api/)     │
                     └──────┬───────┘
                            │ REST / OpenAPI
                     ┌──────▼───────┐
                     │ React + TS   │
                     │  (web/)      │
                     └──────────────┘
```

---

## Data sources (start small)

Pick **one** for MVP; document which you used in this README.

| Source | What to extract | Notes |
|--------|-----------------|-------|
| [Open Targets](https://www.opentargets.org/) | Disease–target associations | Good for Gene/Disease edges |
| [Reactome](https://reactome.org/) | Pathway membership (subset) | Pathway nodes |
| UniProt (subset) | Protein ↔ gene mapping | Keep to &lt;500 rows for demo |

**MVP seed size:** 100–500 nodes, 500–2000 relationships.

Store raw files in `data/raw/` (gitignored if large); processed CSV/JSON in `data/processed/`.

---

## Graph schema (MVP)

```cypher
// Nodes
(:Gene {id, symbol, name})
(:Disease {id, name})
(:Protein {id, name})
(:Pathway {id, name})          // optional in v1

// Relationships
(:Gene)-[:ASSOCIATED_WITH {score, source}]->(:Disease)
(:Protein)-[:ENCODED_BY]->(:Gene)
(:Gene)-[:IN_PATHWAY]->(:Pathway)   // optional
```

**Constraints (create in `scripts/neo4j/init.cypher`):**

```cypher
CREATE CONSTRAINT gene_id IF NOT EXISTS FOR (g:Gene) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT disease_id IF NOT EXISTS FOR (d:Disease) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT protein_id IF NOT EXISTS FOR (p:Protein) REQUIRE p.id IS UNIQUE;
```

---

## API endpoints (MVP)

Base path: `/api/v1`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness + Neo4j connectivity |
| GET | `/genes?q=` | Search genes by symbol/name |
| GET | `/diseases?q=` | Search diseases |
| GET | `/genes/{id}` | Gene detail + degree counts |
| GET | `/genes/{id}/neighbors` | 1-hop subgraph (genes, diseases, proteins) |
| GET | `/path?from_gene=&to_disease=` | Shortest path (if exists) |
| GET | `/stats` | Node/rel counts by label |
| GET | `/export/subgraph?gene_id=` | JSON nodes + edges for UI |

OpenAPI at `/docs` when running locally.

---

## Frontend (MVP)

**Pages:**

1. **Search** — autocomplete genes/diseases
2. **Gene detail** — metadata + neighbor table
3. **Graph view** — force-directed subgraph from `/export/subgraph`
4. **About** — data source, schema, limitations

**UX notes:**

- Loading and empty states for slow Cypher queries
- Link to OpenAPI `/docs` from footer
- Cite data license/source on About page

---

## Repository structure

```text
bioinsight-graph/
├── README.md
├── LICENSE
├── docker-compose.yml
├── .env.example
├── api/
│   ├── pyproject.toml          # or requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py               # Neo4j driver/session
│   │   ├── routers/
│   │   └── models/             # Pydantic schemas
│   └── tests/
├── scripts/
│   ├── download_sample.py
│   ├── etl_opentargets.py
│   ├── seed_neo4j.py
│   └── neo4j/init.cypher
├── web/
│   ├── package.json
│   ├── src/
│   │   ├── api/client.ts
│   │   ├── pages/
│   │   └── components/
│   └── vite.config.ts
├── data/
│   ├── raw/.gitkeep
│   └── processed/.gitkeep
└── deploy/                     # optional
    └── k8s/
```

---

## Getting started

### Prerequisites

- Docker Desktop
- Python 3.11+
- Node.js 20+

### 1. Environment

```bash
cp .env.example .env
```

Example `.env`:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=changeme
API_PORT=8000
CORS_ORIGINS=http://localhost:5173
```

### 2. Start Neo4j

```bash
docker compose up -d neo4j
```

Neo4j Browser: http://localhost:7474

### 3. Seed data

```bash
cd scripts
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r ../api/requirements.txt
python download_sample.py
python etl_opentargets.py
python seed_neo4j.py
```

### 4. Run API

```bash
cd api
uvicorn app.main:app --reload --port 8000
```

### 5. Run web

Requires **Node.js 20+**.

```bash
cd web
npm install
npm run dev
```

Open http://localhost:5173

The UI proxies API calls to `http://localhost:8000` (see `web/vite.config.ts`).

---

## Docker Compose (target)

Services: `neo4j`, `api`, `web` (nginx or Vite preview for demo).

```bash
docker compose up --build
```

Document ports in README after implementation.

---

## Testing

**API:**

- `pytest` with mocked Neo4j or Testcontainers
- At minimum: health, search, neighbors return expected shape

**Web:**

- Vitest + React Testing Library for Search page
- Optional Playwright smoke: load home, run search

---

## Development roadmap

| Phase | Deliverable |
|-------|-------------|
| **0** | Repo scaffold, Docker Neo4j, init constraints |
| **1** | ETL + seed script + sample data committed or scripted |
| **2** | FastAPI read endpoints + OpenAPI + tests |
| **3** | React search + gene detail ✅ |
| **4** | Graph visualization + export endpoint |
| **5** | Docker Compose all-in-one + README screenshots |
| **6** | GitHub Actions CI + optional minikube manifests |

---

## MVP checklist

- [ ] Neo4j runs via Docker with persisted volume
- [ ] Seed script loads ≥100 genes and ≥100 associations
- [ ] 5+ API endpoints documented in OpenAPI
- [ ] React UI: search + graph view
- [ ] README with architecture diagram and screenshots
- [ ] License file (MIT recommended)
- [ ] `.gitignore` for `data/raw/`, `.env`, `node_modules`, `__pycache__`

---

## Portfolio blurb (for CV / cover letter)

> Open-source pipeline: ingests public disease–target association data into Neo4j, exposes a FastAPI graph API, and provides a React/TypeScript explorer for search and subgraph visualization — modeling how research datasets can be structured as queryable knowledge graphs.

---

## References

- [Neo4j Python driver](https://neo4j.com/docs/python-manual/current/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Open Targets documentation](https://platform-docs.opentargets.org/)

---

## License

MIT (update if you choose otherwise)
