from fastapi import APIRouter, Query

from app.db import get_session
from app.models.schemas import DiseaseSummary

router = APIRouter(prefix="/diseases", tags=["diseases"])


@router.get("", response_model=list[DiseaseSummary])
def search_diseases(q: str = Query("", min_length=0)) -> list[DiseaseSummary]:
    with get_session() as session:
        result = session.run(
            """
            MATCH (d:Disease)
            WHERE $q = '' OR toLower(d.name) CONTAINS toLower($q)
               OR toLower(d.id) CONTAINS toLower($q)
            RETURN d.id AS id, d.name AS name
            ORDER BY d.name
            LIMIT 25
            """,
            q=q,
        )
        return [DiseaseSummary(id=r["id"], name=r["name"]) for r in result]
