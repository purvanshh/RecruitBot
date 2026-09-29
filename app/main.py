from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.db.connection import execute_schema, execute_seed
from app.api import candidates, jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    execute_schema()
    execute_seed()
    yield


app = FastAPI(
    title="RecruiterBot",
    description="Candidate-Job Matching Backend",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(candidates.router)
app.include_router(jobs.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}