from fastapi import APIRouter, HTTPException
from app.repositories.candidate_repository import get_all_candidates, get_candidate_by_id
from app.models.schemas import CandidateListResponse, CandidateResponse


router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=CandidateListResponse)
async def list_candidates():
    candidates = get_all_candidates()
    return CandidateListResponse(candidates=[CandidateResponse(**c) for c in candidates])


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return CandidateResponse(**candidate)