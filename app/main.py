import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.config import settings
from app.db.connection import execute_schema, execute_seed, get_connection_pool, close_connection_pool
from app.api import candidates, jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RecruiterBot application")
    execute_schema()
    execute_seed()
    logger.info("Database initialized successfully")
    yield
    logger.info("Shutting down RecruiterBot application")
    close_connection_pool()


app = FastAPI(
    title="RecruiterBot",
    description="Candidate-Job Matching Backend",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


app.include_router(candidates.router)
app.include_router(jobs.router)


@app.get("/health", summary="Health check", response_description="Service health status")
async def health_check():
    return {"status": "ok"}