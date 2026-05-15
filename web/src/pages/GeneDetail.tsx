import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  api,
  type GeneDetail as GeneDetailType,
  type NeighborEdge,
  type NeighborNode,
} from "../api/client";

function nodeLabel(n: NeighborNode): string {
  if (n.label === "Gene") return n.symbol ?? n.id;
  return n.name ?? n.id;
}

function neighborRows(
  geneId: string,
  nodes: NeighborNode[],
  edges: NeighborEdge[]
): { type: string; name: string; id: string; relation: string; score: string }[] {
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));
  const rows: { type: string; name: string; id: string; relation: string; score: string }[] = [];

  for (const e of edges) {
    const otherId = e.source === geneId ? e.target : e.source;
    const node = nodeMap.get(otherId);
    if (!node || node.id === geneId) continue;
    rows.push({
      type: node.label,
      name: nodeLabel(node),
      id: node.id,
      relation: e.type.replace(/_/g, " "),
      score: e.score != null ? e.score.toFixed(2) : "—",
    });
  }

  return rows.sort((a, b) => a.type.localeCompare(b.type));
}

export default function GeneDetail() {
  const { geneId } = useParams<{ geneId: string }>();
  const [gene, setGene] = useState<GeneDetailType | null>(null);
  const [neighbors, setNeighbors] = useState<{ nodes: NeighborNode[]; edges: NeighborEdge[] } | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!geneId) return;
    setLoading(true);
    setError(null);

    Promise.all([api.getGene(geneId), api.getNeighbors(geneId)])
      .then(([g, n]) => {
        setGene(g);
        setNeighbors({ nodes: n.nodes, edges: n.edges });
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [geneId]);

  if (loading) {
    return <div className="state-box">Loading gene details…</div>;
  }

  if (error || !gene) {
    return (
      <>
        <Link to="/" className="back-link">
          ← Back to search
        </Link>
        <div className="state-box error">{error ?? "Gene not found"}</div>
      </>
    );
  }

  const rows = neighbors ? neighborRows(gene.id, neighbors.nodes, neighbors.edges) : [];

  return (
    <>
      <Link to="/" className="back-link">
        ← Back to search
      </Link>

      <div className="detail-header">
        <span className="badge badge-gene">Gene</span>
        <h2 className="page-title" style={{ marginTop: "0.5rem" }}>
          {gene.symbol}
        </h2>
        {gene.name && <p className="page-subtitle" style={{ marginBottom: 0 }}>{gene.name}</p>}
        <p className="mono" style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
          {gene.id}
        </p>

        <div className="detail-meta">
          <div className="meta-chip">
            <strong>{gene.disease_count}</strong>
            Linked diseases
          </div>
          <div className="meta-chip">
            <strong>{gene.protein_count}</strong>
            Encoded proteins
          </div>
          <div className="meta-chip">
            <strong>{rows.length}</strong>
            Neighbor edges
          </div>
        </div>
      </div>

      <h3 style={{ marginBottom: "1rem" }}>1-hop neighbors</h3>

      {rows.length === 0 ? (
        <div className="state-box">No neighbors found for this gene.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Name</th>
                <th>ID</th>
                <th>Relationship</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={`${r.id}-${r.relation}`}>
                  <td>
                    <span
                      className={`badge badge-${r.type.toLowerCase()}`}
                      style={
                        r.type === "Protein"
                          ? { background: "rgba(167,139,250,0.15)", color: "var(--protein)" }
                          : undefined
                      }
                    >
                      {r.type}
                    </span>
                  </td>
                  <td>{r.name}</td>
                  <td className="mono">{r.id}</td>
                  <td>{r.relation}</td>
                  <td>{r.score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
