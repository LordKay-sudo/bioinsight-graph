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

## Strategic direction (PRoH / GraphRAG lesson)

GraphRAG ≠ enough. Target: **decomposed evidence on graph edges** + **planned/adaptive MCP retrieval** + **conditional graph→literature** — not rebranding as “hypergraph RAG.”

---

## Priority next (all repos)

1. **BioInsight 1.x** — real OT-style bulk ingest, evidence on relationships, API breakdown  
2. **BioInsight 2.x** — ENSG/EFO, external-links  
3. **BioInsight 3.x** — evidence UI, disease page, compare UI, export  
4. **embabel M1–M6** — plan/route prompts, meta in dossiers, then `resolve_identifier` / `get_target_evidence` when API ready  
5. **kg-rag R1–R4** — PMIDs/DOIs, citation blocks; then R5–R8 shared IDs + notebook  

---

## MCP defaults

- `BIOINSIGHT_MCP_TOOL_PROFILE=minimal` (long chats)
- `BIOINSIGHT_MCP_COMPACT_MODE=off`
- Prefer **`build_target_dossier`** over many `get_*` calls
- HITL: agent report vs BioInsight UI (`docs/HUMAN_IN_THE_LOOP.md` in embabel)

---

## Non-goals

Clinical advice; causal claims from scores; replacing Ensembl/OT Platform; PRoH codebase import; unbounded external API MCP wrappers.

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

*Last updated: 2026-05 — refresh when phases ship.*
