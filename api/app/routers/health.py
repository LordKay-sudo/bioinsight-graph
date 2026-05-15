from fastapi import APIRouter

from app.db import check_connectivity
from app.models.schemas import HealthResponse, StatsResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    neo4j_ok = check_connectivity()
    return HealthResponse(status="ok" if neo4j_ok else "degraded", neo4j=neo4j_ok)


@router.get("/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    from app.db import get_session

    with get_session() as session:
        row = session.run(
            """
            RETURN
              count { (g:Gene) } AS genes,
              count { (d:Disease) } AS diseases,
              count { (p:Protein) } AS proteins,
              count { ()-[:ASSOCIATED_WITH]->() } AS associations
            """
        ).single()
    return StatsResponse(
        genes=row["genes"],
        diseases=row["diseases"],
        proteins=row["proteins"],
        associations=row["associations"],
    )
