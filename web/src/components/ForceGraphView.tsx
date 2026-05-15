import { useEffect, useMemo, useRef } from "react";
import ForceGraph2D, { type ForceGraphMethods } from "react-force-graph-2d";
import type { SubgraphLink, SubgraphNode } from "../api/client";

const LABEL_COLORS: Record<string, string> = {
  Gene: "#34d399",
  Disease: "#f472b6",
  Protein: "#a78bfa",
};

function displayName(n: SubgraphNode): string {
  if (n.label === "Gene") return n.symbol ?? n.id;
  return n.name ?? n.id;
}

interface GraphData {
  nodes: { id: string; label: string; name: string }[];
  links: { source: string; target: string; type: string; score?: number | null }[];
}

interface Props {
  centerGeneId: string;
  nodes: SubgraphNode[];
  links: SubgraphLink[];
}

export default function ForceGraphView({ centerGeneId, nodes, links }: Props) {
  const ref = useRef<ForceGraphMethods | undefined>(undefined);

  const data: GraphData = useMemo(
    () => ({
      nodes: nodes.map((n) => ({
        id: n.id,
        label: n.label,
        name: displayName(n),
      })),
      links: links.map((l) => ({
        source: l.source,
        target: l.target,
        type: l.type,
        score: l.score,
      })),
    }),
    [nodes, links]
  );

  useEffect(() => {
    const t = setTimeout(() => ref.current?.zoomToFit(400, 40), 400);
    return () => clearTimeout(t);
  }, [data]);

  if (data.nodes.length === 0) {
    return <div className="state-box">No graph data to display.</div>;
  }

  return (
    <div className="graph-panel">
      <ForceGraph2D
        ref={ref}
        graphData={data}
        nodeLabel={(n) => `${(n as GraphData["nodes"][0]).label}: ${(n as GraphData["nodes"][0]).name}`}
        nodeColor={(n) => LABEL_COLORS[(n as GraphData["nodes"][0]).label] ?? "#94a3b8"}
        nodeRelSize={6}
        linkLabel={(l) => {
          const link = l as GraphData["links"][0] & { source: { id: string }; target: { id: string } };
          const score = link.score != null ? ` (${link.score.toFixed(2)})` : "";
          return `${link.type}${score}`;
        }}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        linkColor={() => "rgba(148, 163, 184, 0.45)"}
        backgroundColor="#121c2e"
        nodeCanvasObject={(node, ctx, globalScale) => {
          const n = node as GraphData["nodes"][0] & { x?: number; y?: number };
          const label = n.name;
          const fontSize = 12 / globalScale;
          const isCenter = n.id === centerGeneId;
          const r = isCenter ? 8 : 6;

          ctx.beginPath();
          ctx.arc(n.x ?? 0, n.y ?? 0, r, 0, 2 * Math.PI);
          ctx.fillStyle = LABEL_COLORS[n.label] ?? "#94a3b8";
          ctx.fill();
          if (isCenter) {
            ctx.strokeStyle = "#38bdf8";
            ctx.lineWidth = 2 / globalScale;
            ctx.stroke();
          }

          ctx.font = `${fontSize}px DM Sans, sans-serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "top";
          ctx.fillStyle = "#e8edf5";
          ctx.fillText(label, n.x ?? 0, (n.y ?? 0) + r + 2);
        }}
        cooldownTicks={80}
      />
    </div>
  );
}
