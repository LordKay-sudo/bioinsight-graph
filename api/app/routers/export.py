from fastapi import APIRouter, HTTPException, Query

from app.db import get_session
from app.models.schemas import SubgraphLink, SubgraphNode, SubgraphResponse

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/subgraph", response_model=SubgraphResponse)
def export_subgraph(gene_id: str = Query(..., description="Center gene Ensembl ID")) -> SubgraphResponse:
    with get_session() as session:
        exists = session.run("MATCH (g:Gene {id: $id}) RETURN g", id=gene_id).single()
        if not exists:
            raise HTTPException(status_code=404, detail="Gene not found")

        nodes_result = session.run(
            """
            MATCH (g:Gene {id: $id})
            OPTIONAL MATCH (g)-[:ASSOCIATED_WITH]->(d:Disease)
            OPTIONAL MATCH (p:Protein)-[:ENCODED_BY]->(g)
            WITH collect(DISTINCT g) + collect(DISTINCT d) + collect(DISTINCT p) AS raw
            UNWIND raw AS n
            WITH DISTINCT n
            RETURN labels(n)[0] AS label, n.id AS id, n.name AS name, n.symbol AS symbol
            """,
            id=gene_id,
        )
        links_result = session.run(
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
        SubgraphNode(id=r["id"], label=r["label"], name=r.get("name"), symbol=r.get("symbol"))
        for r in nodes_result
        if r["id"]
    ]
    links = [
        SubgraphLink(source=r["source"], target=r["target"], type=r["type"], score=r["score"])
        for r in links_result
        if r["source"] and r["target"] and r["type"]
    ]
    return SubgraphResponse(gene_id=gene_id, nodes=nodes, links=links)
