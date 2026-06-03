# BioInsight ecosystem — compact context

**Use this file** at the start of new agent sessions instead of long chat history.  
**Roadmaps:** [bioinsight ROADMAP](./ROADMAP.md) · [embabel ROADMAP](https://github.com/LordKay-sudo/embabel-mcp/blob/main/docs/ROADMAP.md) · [kg-rag ROADMAP](https://github.com/LordKay-sudo/kg-rag-demo/blob/main/docs/ROADMAP.md) · [PORTFOLIO_ROADMAP](./PORTFOLIO_ROADMAP.md)

---

## Repos

| Repo | Role | Port (typical) |
|------|------|----------------|
| **bioinsight-graph** | Product: Neo4j + FastAPI + React | API 8000, UI 8080 |
| **embabel-mcp** | MCP tools → BioInsight HTTP only | 1337 SSE |
| **kg-rag-demo** | Optional doc RAG + citations | API 8001 |

**Coupling:** embabel → BioInsight API. kg-rag optional. No monorepo.

---

## Shipped

- BioInsight: `/api/v1/meta`, `PROVENANCE.md`, UI footer version, search/gene/graph/compare, CI/Docker
- embabel: tool profiles (minimal/standard/full), `build_target_dossier`, provenance footers, `compact-mode: off`, workflow never truncated, `docs/RESPONSE_POLICY.md`, `bioinsight://context-policy`
- kg-rag: seed corpus, ask + graph UI, optional MCP via `KG_RAG_ENABLED`

---

## Strategic direction

GraphRAG ≠ enough (PRoH: planned multi-hop). Production biodata also needs **ontology-guided** structure (schema-constrained types/IDs — not schema-free LLM triple mining on the main graph).

| Layer | Approach |
|-------|----------|
| **BioInsight** | Curated ingest (Open Targets–style) + ENSG/EFO/MONDO + evidence on edges |
| **kg-rag** | Ontology-guided extract → **normalize** → cite (ML6-style); does not replace BioInsight |
| **embabel** | **Dual-channel**: channel A = graph dossier/API; channel B = kg-rag chunks only when needed (M8) |

---

## Priority next (all repos)

1. **BioInsight 1.x** — bulk ingest, evidence on relationships, API breakdown  
2. **BioInsight 2.x** — ENSG/EFO, `docs/ONTOLOGY_SCHEMA.md`, external-links  
3. **BioInsight 3.x** — evidence UI, disease page, compare, export  
4. **embabel M1–M6, M8** — plan/route; dual-channel graph→literature  
5. **kg-rag R1–R4** — citations; **R16–R17** extraction schema + normalization; **R5–R8** shared IDs  

---

## MCP defaults

- `BIOINSIGHT_MCP_TOOL_PROFILE=minimal` (long chats)
- `BIOINSIGHT_MCP_COMPACT_MODE=off`
- Prefer **`build_target_dossier`** over many `get_*` calls
- HITL: agent report vs BioInsight UI (`docs/HUMAN_IN_THE_LOOP.md` in embabel)

---

## Non-goals

Clinical advice; causal claims from scores; replacing Ensembl/OT Platform; PRoH/UniAI codebase import; LLM-built target–disease graph replacing OT ingest; LangChain/MS GraphRAG community pipeline as core architecture.

## Reading (optional)

Ontology GraphRAG: [Akash Medium](https://medium.com/@aiwithakashgoyal/beyond-simple-extraction-how-production-grade-ontologies-transform-graphrag-from-prototype-to-333742fa41a6) · [UniAI-GraphRAG arXiv:2603.25152](https://arxiv.org/html/2603.25152v3) · Biomedical LLM KG: [ML6 blog](https://blog.ml6.eu/accelerating-biomedical-knowledge-graph-construction-with-llms-db429952f4b2)

---

## Key paths

```
bioinsight-graph/docs/ROADMAP.md          # P0–P2 tasks 1.x–5.3
bioinsight-graph/docs/PORTFOLIO_ROADMAP.md
embabel-mcp/docs/ROADMAP.md               # M1–M13
embabel-mcp/docs/RESPONSE_POLICY.md
kg-rag-demo/docs/ROADMAP.md               # R1–R15
```

---

## Local paths (dev machine)

`C:\Users\Lordwill\Documents\projects\{bioinsight-graph,embabel-mcp,kg-rag-demo}`

---

*Last updated: 2026-05-21 — refresh when phases ship.*
