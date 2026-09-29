from fastapi import APIRouter, HTTPException
from app.repositories.job_repository import get_all_jobs, get_job_by_id
from app.models.schemas import JobListResponse, JobResponse


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
async def list_jobs():
    jobs = get_all_jobs()
    return JobListResponse(jobs=[JobResponse(**j) for j in jobs])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**job)