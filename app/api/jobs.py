from fastapi import APIRouter, HTTPException, Path
from app.repositories.job_repository import get_all_jobs, get_job_by_id
from app.services.matching_service import get_job_matches
from app.models.schemas import (
    JobListResponse,
    JobResponse,
    JobMatchesResponse,
    ErrorResponse
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get(
    "",
    response_model=JobListResponse,
    summary="List all jobs",
    description="Returns a list of all job postings with their required skills, minimum experience, culture keywords, and tagline.",
    responses={
        200: {"description": "Successful response"},
    }
)
async def list_jobs():
    jobs = get_all_jobs()
    return JobListResponse(jobs=[JobResponse(**j) for j in jobs])


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job by ID",
    description="Returns a single job posting with its required skills, minimum experience, culture keywords, and tagline.",
    responses={
        200: {"description": "Successful response"},
        404: {"model": ErrorResponse, "description": "Job not found"},
    }
)
async def get_job(
    job_id: int = Path(..., ge=1, description="Job ID")
):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**job)


@router.get(
    "/{job_id}/matches",
    response_model=JobMatchesResponse,
    summary="Get ranked candidate matches for a job",
    description="Returns all candidates ranked by match score for the given job. "
                "Score is calculated using skill overlap (60%), experience fit (25%), and culture match (15%).",
    responses={
        200: {"description": "Successful response"},
        404: {"model": ErrorResponse, "description": "Job not found"},
    }
)
async def get_job_matches_endpoint(
    job_id: int = Path(..., ge=1, description="Job ID")
):
    result = get_job_matches(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result