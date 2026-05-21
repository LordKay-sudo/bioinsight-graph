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


class DiseaseDetail(DiseaseSummary):
    gene_count: int = 0


class ScoredGeneTarget(BaseModel):
    gene_id: str
    symbol: str
    name: str | None = None
    score: float


class ScoredDiseaseAssociation(BaseModel):
    disease_id: str
    name: str
    score: float


class DiseaseGenesResponse(BaseModel):
    disease_id: str
    disease_name: str
    min_score: float
    genes: list[ScoredGeneTarget]


class GeneDiseasesResponse(BaseModel):
    gene_id: str
    symbol: str
    min_score: float
    diseases: list[ScoredDiseaseAssociation]


class GeneCompareSummary(BaseModel):
    gene_id: str
    symbol: str
    name: str | None = None
    disease_count: int = 0
    top_diseases: list[ScoredDiseaseAssociation] = Field(default_factory=list)


class CompareGenesResponse(BaseModel):
    symbols: list[str]
    genes: list[GeneCompareSummary]
    overlapping_disease_names: list[str] = Field(default_factory=list)


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


class SubgraphNode(BaseModel):
    id: str
    label: str
    name: str | None = None
    symbol: str | None = None


class SubgraphLink(BaseModel):
    source: str
    target: str
    type: str
    score: float | None = None


class SubgraphResponse(BaseModel):
    gene_id: str
    nodes: list[SubgraphNode]
    links: list[SubgraphLink]
