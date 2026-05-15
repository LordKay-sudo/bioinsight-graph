from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import close_driver
from app.routers import diseases, export, genes, health

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_driver()


app = FastAPI(
    title="BioInsight Graph API",
    description="Disease–target knowledge graph API backed by Neo4j",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(genes.router, prefix=API_PREFIX)
app.include_router(diseases.router, prefix=API_PREFIX)
app.include_router(export.router, prefix=API_PREFIX)


@app.get("/")
def root():
    return {"service": "bioinsight-graph", "docs": "/docs", "api": API_PREFIX}
