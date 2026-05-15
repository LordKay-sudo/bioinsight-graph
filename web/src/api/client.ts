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
  health: () => fetchJson<{ status: string; neo4j: boolean }>("/api/v1/health"),
};
