export default function About() {
  return (
    <>
      <h2 className="page-title">About BioInsight Graph</h2>
      <p className="page-subtitle">
        A research-oriented prototype for exploring disease–target associations as a knowledge graph.
      </p>

      <section className="about-section">
        <h2>Data source</h2>
        <p>
          MVP uses a representative sample inspired by{" "}
          <a href="https://www.opentargets.org/" target="_blank" rel="noreferrer">
            Open Targets
          </a>{" "}
          disease–target associations (~100+ genes, ~100+ edges). Full-scale production
          ingestion would pull from Open Targets Platform APIs or bulk exports.
        </p>
      </section>

      <section className="about-section">
        <h2>Graph schema</h2>
        <ul>
          <li>
            <strong>Nodes:</strong> Gene, Disease, Protein
          </li>
          <li>
            <strong>Edges:</strong> ASSOCIATED_WITH (Gene→Disease, with score), ENCODED_BY
            (Protein→Gene)
          </li>
        </ul>
      </section>

      <section className="about-section">
        <h2>Limitations (MVP)</h2>
        <ul>
          <li>Sample data only — not clinical-grade</li>
          <li>No authentication or write APIs</li>
          <li>Graph visualization coming in Phase 4</li>
          <li>Disease search lists matches; gene detail is the primary drill-down view</li>
        </ul>
      </section>

      <section className="about-section">
        <h2>Stack</h2>
        <p>
          Neo4j · FastAPI · React + TypeScript + Vite. See the{" "}
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
            OpenAPI docs
          </a>{" "}
          for API reference.
        </p>
      </section>
    </>
  );
}
