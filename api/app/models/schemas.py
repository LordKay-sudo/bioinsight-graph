from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    neo4j: bool


class GeneSummary(BaseModel):
    id: str
    symbol: str
    name: str | None = None


class DiseaseSummary(BaseModel):
    id: str
    name: str


class GeneDetail(GeneSummary):
    disease_count: int = 0
    protein_count: int = 0


class NeighborNode(BaseModel):
    id: str
    label: str
    name: str | None = None
    symbol: str | None = None


class NeighborEdge(BaseModel):
    source: str
    target: str
    type: str
    score: float | None = None


class NeighborsResponse(BaseModel):
    gene_id: str
    nodes: list[NeighborNode]
    edges: list[NeighborEdge]


class StatsResponse(BaseModel):
    genes: int
    diseases: int
    proteins: int
    associations: int
