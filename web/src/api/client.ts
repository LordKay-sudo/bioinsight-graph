const API_BASE = import.meta.env.VITE_API_URL ?? "";

export interface GeneSummary {
  id: string;
  symbol: string;
  name?: string | null;
}

export interface DiseaseSummary {
  id: string;
  name: string;
}

export interface GeneDetail extends GeneSummary {
  disease_count: number;
  protein_count: number;
}

export interface NeighborNode {
  id: string;
  label: string;
  name?: string | null;
  symbol?: string | null;
}

export interface NeighborEdge {
  source: string;
  target: string;
  type: string;
  score?: number | null;
}

export interface NeighborsResponse {
  gene_id: string;
  nodes: NeighborNode[];
  edges: NeighborEdge[];
}

export interface StatsResponse {
  genes: number;
  diseases: number;
  proteins: number;
  associations: number;
}

export interface MetaResponse {
  service: string;
  api_version: string;
  data_version: string;
  release_date: string;
  disclaimer: string;
  associations_are_correlative: boolean;
}

export interface DiseaseDetail extends DiseaseSummary {
  gene_count: number;
}

export interface ScoredGeneTarget {
  gene_id: string;
  symbol: string;
  name?: string | null;
  score: number;
  source?: string | null;
  evidence: EvidenceItem[];
}

export interface DiseaseGenesResponse {
  disease_id: string;
  disease_name: string;
  min_score: number;
  genes: ScoredGeneTarget[];
}

export interface ScoredDiseaseAssociation {
  disease_id: string;
  name: string;
  score: number;
  source?: string | null;
  evidence: EvidenceItem[];
}

export interface GeneCompareSummary {
  gene_id: string;
  symbol: string;
  name?: string | null;
  disease_count: number;
  top_diseases: ScoredDiseaseAssociation[];
}

export interface CompareGenesResponse {
  symbols: string[];
  genes: GeneCompareSummary[];
  overlapping_disease_names: string[];
}

export interface SubgraphNode {
  id: string;
  label: string;
  name?: string | null;
  symbol?: string | null;
}

export interface SubgraphLink {
  source: string;
  target: string;
  type: string;
  score?: number | null;
}

export interface SubgraphResponse {
  gene_id: string;
  nodes: SubgraphNode[];
  links: SubgraphLink[];
}

export interface EvidenceItem {
  evidence_type: string;
  source: string;
  score: number;
  study_id?: string | null;
}

export interface AssociationEvidenceBundle {
  disease_id: string;
  disease_name: string;
  score: number;
  source: string;
  evidence: EvidenceItem[];
}

export interface GeneEvidenceResponse {
  gene_id: string;
  symbol: string;
  disease_id?: string | null;
  evidence: AssociationEvidenceBundle[];
}

export interface ExternalLink {
  label: string;
  provider: string;
  url: string;
}

export interface GeneExternalLinksResponse {
  gene_id: string;
  symbol: string;
  links: ExternalLink[];
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  searchGenes: (q: string) =>
    fetchJson<GeneSummary[]>(`/api/v1/genes?q=${encodeURIComponent(q)}`),
  searchDiseases: (q: string) =>
    fetchJson<DiseaseSummary[]>(`/api/v1/diseases?q=${encodeURIComponent(q)}`),
  getGene: (id: string) => fetchJson<GeneDetail>(`/api/v1/genes/${encodeURIComponent(id)}`),
  getNeighbors: (id: string) =>
    fetchJson<NeighborsResponse>(`/api/v1/genes/${encodeURIComponent(id)}/neighbors`),
  getStats: () => fetchJson<StatsResponse>("/api/v1/stats"),
  getSubgraph: (geneId: string) =>
    fetchJson<SubgraphResponse>(
      `/api/v1/export/subgraph?gene_id=${encodeURIComponent(geneId)}`
    ),
  health: () => fetchJson<{ status: string; neo4j: boolean }>("/api/v1/health"),
  getMeta: () => fetchJson<MetaResponse>("/api/v1/meta"),
  getGeneEvidence: (id: string, limit = 15) =>
    fetchJson<GeneEvidenceResponse>(
      `/api/v1/genes/${encodeURIComponent(id)}/evidence?limit=${limit}`
    ),
  getGeneExternalLinks: (id: string) =>
    fetchJson<GeneExternalLinksResponse>(
      `/api/v1/genes/${encodeURIComponent(id)}/external-links`
    ),
  getDisease: (id: string) =>
    fetchJson<DiseaseDetail>(`/api/v1/diseases/${encodeURIComponent(id)}`),
  getDiseaseGenes: (id: string, minScore = 0, limit = 25) =>
    fetchJson<DiseaseGenesResponse>(
      `/api/v1/diseases/${encodeURIComponent(id)}/genes?min_score=${minScore}&limit=${limit}`
    ),
  compareGenes: (symbols: string[], topN = 5) =>
    fetchJson<CompareGenesResponse>(
      `/api/v1/genes/compare?symbols=${encodeURIComponent(symbols.join(","))}&top_n=${topN}`
    ),
  geneReportUrl: (id: string, format: "json" | "tsv" = "tsv") =>
    `${API_BASE}/api/v1/export/gene-report?gene_id=${encodeURIComponent(id)}&format=${format}`,
};
