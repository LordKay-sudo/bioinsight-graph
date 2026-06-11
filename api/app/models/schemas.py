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


class EvidenceItem(BaseModel):
    evidence_type: str
    source: str
    score: float = Field(ge=0.0, le=1.0)
    study_id: str | None = None


class ScoredGeneTarget(BaseModel):
    gene_id: str
    symbol: str
    name: str | None = None
    score: float
    source: str | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)


class ScoredDiseaseAssociation(BaseModel):
    disease_id: str
    name: str
    score: float
    source: str | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)


class AssociationEvidenceBundle(BaseModel):
    disease_id: str
    disease_name: str
    score: float
    source: str
    evidence: list[EvidenceItem] = Field(default_factory=list)


class GeneEvidenceResponse(BaseModel):
    gene_id: str
    symbol: str
    disease_id: str | None = None
    evidence: list[AssociationEvidenceBundle] = Field(default_factory=list)


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


class DataSourceMeta(BaseModel):
    name: str
    url: str
    license: str | None = None


class MetaResponse(BaseModel):
    service: str
    api_version: str
    data_version: str
    release_date: str
    sources: list[DataSourceMeta]
    disclaimer: str
    associations_are_correlative: bool = True
    provenance_doc: str = "PROVENANCE.md"
    web_ui_gene_path: str = "/gene/{gene_id}"


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


class ExternalLink(BaseModel):
    label: str
    provider: str
    url: str


class GeneExternalLinksResponse(BaseModel):
    gene_id: str
    symbol: str
    links: list[ExternalLink] = Field(default_factory=list)


class BatchLookupRequest(BaseModel):
    queries: list[str] = Field(..., min_length=1, max_length=100)


class BatchLookupHit(BaseModel):
    query: str
    gene_id: str
    symbol: str
    name: str | None = None
    disease_count: int = 0


class BatchLookupResponse(BaseModel):
    hits: list[BatchLookupHit] = Field(default_factory=list)
    unresolved: list[str] = Field(default_factory=list)
