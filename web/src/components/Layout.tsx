import { NavLink } from "react-router-dom";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-inner">
          <NavLink to="/" className="brand">
            <div className="brand-icon">BI</div>
            <div>
              <h1>BioInsight Graph</h1>
              <p>Disease–target knowledge explorer</p>
            </div>
          </NavLink>
          <nav className="nav-links">
            <NavLink to="/" end>
              Search
            </NavLink>
            <NavLink to="/about">About</NavLink>
          </nav>
        </div>
      </header>
      <main className="app-main">{children}</main>
      <footer className="app-footer">
        <p>
          Data: Open Targets–style sample · API docs:{" "}
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
            OpenAPI
          </a>
        </p>
      </footer>
    </div>
  );
}
