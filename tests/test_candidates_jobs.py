import sys
sys.path.insert(0, "/app")

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_list_candidates():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/candidates")
        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
        assert len(data["candidates"]) == 15
        
        # Verify structure of first candidate
        candidate = data["candidates"][0]
        assert "id" in candidate
        assert "name" in candidate
        assert "skills" in candidate
        assert "experience_years" in candidate
        assert "availability" in candidate
        assert "traits" in candidate
        assert "quirk" in candidate
        
        # Verify skills structure
        assert len(candidate["skills"]) > 0
        for skill in candidate["skills"]:
            assert "id" in skill
            assert "name" in skill


@pytest.mark.asyncio
async def test_get_candidate_by_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/candidates/1")
        assert response.status_code == 200
        candidate = response.json()
        assert candidate["id"] == 1
        assert candidate["name"] == "Sherlock H."
        assert len(candidate["skills"]) == 3
        skill_names = {s["name"] for s in candidate["skills"]}
        assert skill_names == {"deduction", "pattern-recognition", "forensics"}
        assert candidate["experience_years"] == 8
        assert candidate["availability"] == "Immediate"
        assert set(candidate["traits"]) == {"analytical", "blunt"}


@pytest.mark.asyncio
async def test_get_candidate_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/candidates/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Candidate not found"


@pytest.mark.asyncio
async def test_list_jobs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert len(data["jobs"]) == 6
        
        # Verify structure of first job
        job = data["jobs"][0]
        assert "id" in job
        assert "title" in job
        assert "required_skills" in job
        assert "min_experience" in job
        assert "culture_keywords" in job
        assert "tagline" in job
        
        # Verify skills structure
        assert len(job["required_skills"]) > 0
        for skill in job["required_skills"]:
            assert "id" in skill
            assert "name" in skill


@pytest.mark.asyncio
async def test_get_job_by_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/jobs/1")
        assert response.status_code == 200
        job = response.json()
        assert job["id"] == 1
        assert job["title"] == "Backend Detective"
        assert len(job["required_skills"]) == 3
        skill_names = {s["name"] for s in job["required_skills"]}
        assert skill_names == {"deduction", "pattern-recognition", "forensics"}
        assert job["min_experience"] == 3
        assert set(job["culture_keywords"]) == {"analytical", "autonomous"}
        assert job["tagline"] == "We have a bug. We have no leads. We have you."


@pytest.mark.asyncio
async def test_get_job_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/jobs/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"