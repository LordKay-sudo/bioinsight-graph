"""Load processed CSV data into Neo4j."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))

from app.config import settings  # noqa: E402

INIT_CYPHER = (ROOT / "scripts" / "neo4j" / "init.cypher").read_text(encoding="utf-8")


def run_constraints(session) -> None:
    for stmt in INIT_CYPHER.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            session.run(stmt)


def seed(driver) -> None:
    assoc = pd.read_csv(ROOT / "data" / "processed" / "associations.csv")
    proteins = pd.read_csv(ROOT / "data" / "processed" / "proteins.csv")

    with driver.session() as session:
        run_constraints(session)
        session.run("MATCH (n) DETACH DELETE n")

        for _, row in assoc.drop_duplicates(subset=["target_id"]).iterrows():
            session.run(
                """
                MERGE (g:Gene {id: $id})
                SET g.symbol = $symbol, g.name = $name
                """,
                id=row["target_id"],
                symbol=row["symbol"],
                name=row["name"],
            )

        for _, row in assoc.drop_duplicates(subset=["disease_id"]).iterrows():
            session.run(
                """
                MERGE (d:Disease {id: $id})
                SET d.name = $name
                """,
                id=row["disease_id"],
                name=row["disease_name"],
            )

        for _, row in assoc.iterrows():
            session.run(
                """
                MATCH (g:Gene {id: $gene_id})
                MATCH (d:Disease {id: $disease_id})
                MERGE (g)-[r:ASSOCIATED_WITH]->(d)
                SET r.score = $score, r.source = 'opentargets_sample'
                """,
                gene_id=row["target_id"],
                disease_id=row["disease_id"],
                score=float(row["score"]),
            )

        for _, row in proteins.iterrows():
            session.run(
                """
                MERGE (p:Protein {id: $id})
                SET p.name = $name
                WITH p
                MATCH (g:Gene {id: $gene_id})
                MERGE (p)-[:ENCODED_BY]->(g)
                """,
                id=row["id"],
                name=row["name"],
                gene_id=row["gene_id"],
            )

        counts = session.run(
            """
            RETURN
              count { (g:Gene) } AS genes,
              count { (d:Disease) } AS diseases,
              count { ()-[:ASSOCIATED_WITH]->() } AS associations
            """
        ).single()
        print(f"Seeded: {counts['genes']} genes, {counts['diseases']} diseases, {counts['associations']} associations")


def main() -> None:
    uri = os.getenv("NEO4J_URI", settings.neo4j_uri)
    user = os.getenv("NEO4J_USER", settings.neo4j_user)
    password = os.getenv("NEO4J_PASSWORD", settings.neo4j_password)

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        driver.verify_connectivity()
        seed(driver)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
