from fastapi import APIRouter, HTTPException, Path
from app.repositories.candidate_repository import get_all_candidates, get_candidate_by_id
from app.services.matching_service import get_candidate_matches
from app.models.schemas import (
    CandidateListResponse,
    CandidateResponse,
    CandidateMatchesResponse,
    ErrorResponse
)

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get(
    "",
    response_model=CandidateListResponse,
    summary="List all candidates",
    description="Returns a list of all candidates with their skills, experience, availability, traits, and quirk.",
    responses={
        200: {"description": "Successful response"},
    }
)
async def list_candidates():
    candidates = get_all_candidates()
    return CandidateListResponse(candidates=[CandidateResponse(**c) for c in candidates])


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
    summary="Get candidate by ID",
    description="Returns a single candidate with their skills, experience, availability, traits, and quirk.",
    responses={
        200: {"description": "Successful response"},
        404: {"model": ErrorResponse, "description": "Candidate not found"},
    }
)
async def get_candidate(
    candidate_id: int = Path(..., ge=1, description="Candidate ID")
):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return CandidateResponse(**candidate)


@router.get(
    "/{candidate_id}/matches",
    response_model=CandidateMatchesResponse,
    summary="Get ranked job matches for a candidate",
    description="Returns all jobs ranked by match score for the given candidate. "
                "Score is calculated using skill overlap (60%), experience fit (25%), and culture match (15%).",
    responses={
        200: {"description": "Successful response"},
        404: {"model": ErrorResponse, "description": "Candidate not found"},
    }
)
async def get_candidate_matches_endpoint(
    candidate_id: int = Path(..., ge=1, description="Candidate ID")
):
    result = get_candidate_matches(candidate_id)
    if not result:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return result