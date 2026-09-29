from fastapi import FastAPI
from app.config import settings
from app.db.connection import execute_schema, execute_seed


app = FastAPI(
    title="RecruiterBot",
    description="Candidate-Job Matching Backend",
    version="1.0.0"
)


@app.on_event("startup")
async def startup():
    execute_schema()
    execute_seed()


@app.get("/health")
async def health_check():
    return {"status": "ok"}