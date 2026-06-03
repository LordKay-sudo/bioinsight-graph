# BioInsight Graph — implementation roadmap

**Repo:** [bioinsight-graph](https://github.com/LordKay-sudo/bioinsight-graph) (primary product)  
**Ecosystem:** [ECOSYSTEM_CONTEXT.md](./ECOSYSTEM_CONTEXT.md) (compact handoff) · [PORTFOLIO_ROADMAP.md](./PORTFOLIO_ROADMAP.md) (full cross-repo plan)  
**Sibling roadmaps:** [embabel-mcp ROADMAP](https://github.com/LordKay-sudo/embabel-mcp/blob/main/docs/ROADMAP.md) · [kg-rag-demo ROADMAP](https://github.com/LordKay-sudo/kg-rag-demo/blob/main/docs/ROADMAP.md)

No code in this doc — use task IDs when opening issues or PRs.

---

## Positioning

Disease–target **knowledge graph** (Neo4j + FastAPI + React). Credibility = public data + stable IDs + **evidence on edges** + provenance — not “hypergraph RAG” branding. GraphRAG-style structure is the base; next step is **decomposed evidence** and APIs that support **planned multi-hop retrieval** (MCP/agents consume this).

Inspired by (do not reimplement): [PRoH](https://github.com/zaixjun/PRoH) — dynamic planning; [UniAI-GraphRAG](https://arxiv.org/html/2603.25152v3) — ontology-guided structure + dual-channel retrieval. Here = **curated ontology-backed graph** + evidence bundles + API hops.

### Ontology-first main graph (vs LLM-built)

BioInsight’s target–disease graph comes from **bulk public ingest**, not schema-free LLM triple extraction. Ontology = industry IDs + typed relations + evidence constraints — not a separate hypergraph product.

| Do | Don’t |
|----|--------|
| Open Targets–style ETL with evidence fields | Replace ingest with PubMed LLM extraction at scale |
| ENSG / EFO / MONDO validation on load | LangChain GraphRAG community pipeline as core architecture |
| Document schema in `docs/ONTOLOGY_SCHEMA.md` | Claim “production GraphRAG” without citable data underneath |

---

## Shipped (baseline)

| ID | Item |
|----|------|
| ✓ 0.1 | `PROVENANCE.md` |
| ✓ 0.2 | `GET /api/v1/meta` |
| ✓ 0.3 | UI footer: data version + disclaimer |
| ✓ — | Search, gene detail, force graph, compare API, Docker/CI, architecture docs |

---

## P0 — Do next (highest leverage)

| ID | Task | Done when |
|----|------|-----------|
| **1.1** | Document chosen Open Targets (or equivalent) **bulk** ingest source + licence in `PROVENANCE.md` | Source URL + version pinned |
| **1.2** | Neo4j: `evidence_type`, `source`, `score` (and optional study ref) on `ASSOCIATED_WITH` | Schema migration documented |
| **1.3** | ETL v2: defensible slice (≥500 genes, thousands of associations) | `/stats` reflects scale |
| **1.4** | Ranked gene–disease endpoints return **evidence breakdown** per association | API tests + OpenAPI |
| **1.5** | CI fixtures from frozen subset of ingest | Reproducible CI without full download |

---

## P1 — Product + interoperability

| ID | Task | Done when |
|----|------|-----------|
| **2.0** | `docs/ONTOLOGY_SCHEMA.md` — entity types, relation types, ID rules (S=(E,R,Φ) style) | Matches Neo4j model + API |
| **2.1** | Ingest: Ensembl **ENSG** + EFO/MONDO on diseases | Validation on load |
| **2.2** | `GET /genes/{id}/external-links` (Ensembl, Open Targets, UniProt) | All demo genes resolve |
| **2.3** | UI: “Open in Ensembl / Open Targets” on gene page | Links live |
| **3.1** | UI: evidence chart (by type) on gene detail | Matches API breakdown |
| **3.2** | UI: disease page → top targets | Disease-centric workflow |
| **3.3** | UI: compare genes (wire compare API) | Side-by-side diseases |
| **3.4** | `POST /genes/batch-lookup` | Batch in OpenAPI |
| **3.5** | `GET /export/gene-report` (TSV/JSON + provenance columns) | Download works |
| **3.6** | Refresh README screenshots/GIF | Visuals match features |

---

## P2 — Platform story + measurement

| ID | Task | Done when |
|----|------|-----------|
| **4.3** | `docs/PLATFORM.md` — all services, ports, compose order | One doc runs stack |
| **4.4** | Notebook: one gene → graph queries + (optional) literature pointer | ≤15 min clone-to-run |
| **5.2** | Tutorial: public data → Neo4j → API | Linked from README |
| **5.3** | `docs/BENCHMARKS.md` — nodes/edges, ingest time, search p95 | Numbers recorded |
| **0.4** | README: associations ≠ causation (if not already prominent) | Non-goals visible |

---

## API contracts agents will need (coordinate with embabel-mcp)

| Endpoint / field | Why |
|------------------|-----|
| `/meta` | `data_version`, sources, disclaimer (exists) |
| Evidence arrays on ranked associations | Hyperedge-like facts without a hypergraph DB |
| `/genes/{id}/external-links` | Federated identity story |
| Stable `/api/v1` + OpenAPI | MCP and UI share contract |
| Export with provenance columns | Auditable analyst handoff |

---

## Explicit non-goals

- Replacing Ensembl, gnomAD, or Open Targets Platform
- Clinical diagnostics / treatment recommendations
- Causal claims from association scores alone
- Ingest via thousands of per-entity HTTP calls (use bulk)
- Embedding a PRoH-style hypergraph RAG engine in this repo
- LLM-primary graph for target–disease associations (use kg-rag for text-derived facts only)

## References (optional reading)

- [Towards AI — Neo4j + LangChain GraphRAG](https://pub.towardsai.net/graphrag-explained-building-knowledge-grounded-llm-systems-with-neo4j-and-langchain-017a1820763e) — stack patterns only  
- [ML6 — biomedical KG with LLMs](https://blog.ml6.eu/accelerating-biomedical-knowledge-graph-construction-with-llms-db429952f4b2) — applies to **kg-rag**, not main ingest  
- [Production ontologies for GraphRAG (Medium)](https://medium.com/@aiwithakashgoyal/beyond-simple-extraction-how-production-grade-ontologies-transform-graphrag-from-prototype-to-333742fa41a6)  
- [DeepSense — ontology-driven GraphRAG](https://deepsense.ai/resource/ontology-driven-knowledge-graph-for-graphrag/)

---

## Task pick order (4–6 weeks)

1. **1.1 → 1.5** (data + evidence)  
2. **2.1 → 2.3** (IDs + links)  
3. **3.1 → 3.3** (UI depth)  
4. **4.3, 5.3** (ops + benchmarks)

---

*Update ✓ rows as you ship. Phase numbers match [PORTFOLIO_ROADMAP.md](./PORTFOLIO_ROADMAP.md).*
