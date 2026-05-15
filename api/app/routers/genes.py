from fastapi import APIRouter, HTTPException, Query

from app.db import get_session
from app.models.schemas import GeneDetail, GeneSummary, NeighborEdge, NeighborNode, NeighborsResponse

router = APIRouter(prefix="/genes", tags=["genes"])


@router.get("", response_model=list[GeneSummary])
def search_genes(q: str = Query("", min_length=0)) -> list[GeneSummary]:
    with get_session() as session:
        result = session.run(
            """
            MATCH (g:Gene)
            WHERE $q = '' OR toLower(g.symbol) CONTAINS toLower($q)
               OR toLower(coalesce(g.name, '')) CONTAINS toLower($q)
            RETURN g.id AS id, g.symbol AS symbol, g.name AS name
            ORDER BY g.symbol
            LIMIT 25
            """,
            q=q,
        )
        return [GeneSummary(id=r["id"], symbol=r["symbol"], name=r["name"]) for r in result]


@router.get("/{gene_id}", response_model=GeneDetail)
def get_gene(gene_id: str) -> GeneDetail:
    with get_session() as session:
        row = session.run(
            """
            MATCH (g:Gene {id: $id})
            OPTIONAL MATCH (g)-[:ASSOCIATED_WITH]->(d:Disease)
            OPTIONAL MATCH (p:Protein)-[:ENCODED_BY]->(g)
            RETURN g.id AS id, g.symbol AS symbol, g.name AS name,
                   count(DISTINCT d) AS disease_count,
                   count(DISTINCT p) AS protein_count
            """,
            id=gene_id,
        ).single()
    if not row:
        raise HTTPException(status_code=404, detail="Gene not found")
    return GeneDetail(
        id=row["id"],
        symbol=row["symbol"],
        name=row["name"],
        disease_count=row["disease_count"],
        protein_count=row["protein_count"],
    )


@router.get("/{gene_id}/neighbors", response_model=NeighborsResponse)
def get_neighbors(gene_id: str) -> NeighborsResponse:
    with get_session() as session:
        exists = session.run("MATCH (g:Gene {id: $id}) RETURN g", id=gene_id).single()
        if not exists:
            raise HTTPException(status_code=404, detail="Gene not found")

        nodes_result = session.run(
            """
            MATCH (g:Gene {id: $id})
            OPTIONAL MATCH (g)-[r:ASSOCIATED_WITH]->(d:Disease)
            OPTIONAL MATCH (p:Protein)-[:ENCODED_BY]->(g)
            WITH collect(DISTINCT g) + collect(DISTINCT d) + collect(DISTINCT p) AS raw
            UNWIND raw AS n
            WITH DISTINCT n
            RETURN
              labels(n)[0] AS label,
              n.id AS id,
              n.name AS name,
              n.symbol AS symbol
            """,
            id=gene_id,
        )
        edges_result = session.run(
            """
            MATCH (g:Gene {id: $id})
            OPTIONAL MATCH (g)-[r:ASSOCIATED_WITH]->(d:Disease)
            RETURN g.id AS source, d.id AS target, type(r) AS type, r.score AS score
            UNION
            MATCH (g:Gene {id: $id})
            OPTIONAL MATCH (p:Protein)-[r:ENCODED_BY]->(g)
            RETURN p.id AS source, g.id AS target, type(r) AS type, null AS score
            """,
            id=gene_id,
        )

    nodes = [
        NeighborNode(id=r["id"], label=r["label"], name=r.get("name"), symbol=r.get("symbol"))
        for r in nodes_result
        if r["id"]
    ]
    edges = [
        NeighborEdge(source=r["source"], target=r["target"], type=r["type"], score=r["score"])
        for r in edges_result
        if r["source"] and r["target"] and r["type"]
    ]
    return NeighborsResponse(gene_id=gene_id, nodes=nodes, edges=edges)
