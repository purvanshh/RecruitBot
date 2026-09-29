from pydantic import BaseModel
from typing import List, Optional


class SkillResponse(BaseModel):
    id: int
    name: str


class CandidateResponse(BaseModel):
    id: int
    name: str
    skills: List[SkillResponse]
    experience_years: int
    availability: str
    traits: List[str]
    quirk: Optional[str] = None


class CandidateListResponse(BaseModel):
    candidates: List[CandidateResponse]


class JobResponse(BaseModel):
    id: int
    title: str
    required_skills: List[SkillResponse]
    min_experience: int
    culture_keywords: List[str]
    tagline: Optional[str] = None


class JobListResponse(BaseModel):
    jobs: List[JobResponse]


class MatchCandidateResponse(BaseModel):
    candidate_id: int
    candidate_name: str
    score: float
    reason: str


class JobMatchesResponse(BaseModel):
    job_id: int
    job_title: str
    matches: List[MatchCandidateResponse]


class MatchJobResponse(BaseModel):
    job_id: int
    job_title: str
    score: float
    reason: str


class CandidateMatchesResponse(BaseModel):
    candidate_id: int
    candidate_name: str
    matches: List[MatchJobResponse]


class ErrorResponse(BaseModel):
    detail: str