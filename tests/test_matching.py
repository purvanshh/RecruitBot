import sys
sys.path.insert(0, "/app")

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.utils.scoring import (
    calculate_skill_score,
    calculate_experience_score,
    calculate_culture_score,
    calculate_final_score,
    generate_match_reason
)


class TestScoringFunctions:
    
    def test_exact_skill_match(self):
        candidate_skills = {1, 2, 3}
        job_skills = {1, 2, 3}
        assert calculate_skill_score(candidate_skills, job_skills) == 100.0
    
    def test_partial_skill_match(self):
        candidate_skills = {1, 2}
        job_skills = {1, 2, 3}
        assert calculate_skill_score(candidate_skills, job_skills) == 66.67
    
    def test_zero_skill_match(self):
        candidate_skills = {4, 5}
        job_skills = {1, 2, 3}
        assert calculate_skill_score(candidate_skills, job_skills) == 0.0
    
    def test_no_required_skills(self):
        candidate_skills = {1, 2}
        job_skills = set()
        assert calculate_skill_score(candidate_skills, job_skills) == 100.0
    
    def test_candidate_exceeds_experience(self):
        assert calculate_experience_score(8, 3) == 100.0
    
    def test_candidate_meets_experience(self):
        assert calculate_experience_score(3, 3) == 100.0
    
    def test_candidate_below_experience(self):
        assert calculate_experience_score(2, 4) == 50.0
    
    def test_experience_capped_at_100(self):
        assert calculate_experience_score(15, 3) == 100.0
    
    def test_zero_min_experience(self):
        assert calculate_experience_score(0, 0) == 100.0
    
    def test_culture_match(self):
        candidate_traits = {"analytical", "autonomous"}
        job_keywords = {"analytical", "autonomous"}
        assert calculate_culture_score(candidate_traits, job_keywords) == 100.0
    
    def test_partial_culture_match(self):
        candidate_traits = {"analytical"}
        job_keywords = {"analytical", "autonomous"}
        assert calculate_culture_score(candidate_traits, job_keywords) == 50.0
    
    def test_no_culture_match(self):
        candidate_traits = {"creative"}
        job_keywords = {"analytical", "autonomous"}
        assert calculate_culture_score(candidate_traits, job_keywords) == 0.0
    
    def test_no_culture_keywords(self):
        candidate_traits = {"analytical"}
        job_keywords = set()
        assert calculate_culture_score(candidate_traits, job_keywords) == 100.0
    
    def test_final_weighted_score(self):
        final = calculate_final_score(100.0, 100.0, 100.0)
        assert final == 100.0
    
    def test_final_weighted_score_mixed(self):
        final = calculate_final_score(66.67, 75.0, 50.0)
        expected = round(66.67 * 0.60 + 75.0 * 0.25 + 50.0 * 0.15, 2)
        assert final == expected
    
    def test_explanation_exact_match(self):
        reason = generate_match_reason(
            {1, 2, 3}, {1, 2, 3},
            8, 3,
            {"analytical", "autonomous"}, {"analytical", "autonomous"}
        )
        assert "3/3 required skills" in reason
        assert "exceeds the minimum experience requirement" in reason
        assert "analytical" in reason and "autonomous" in reason
    
    def test_explanation_partial_match(self):
        reason = generate_match_reason(
            {1, 2}, {1, 2, 3},
            2, 4,
            {"creative"}, {"analytical", "autonomous"}
        )
        assert "2/3 required skills" in reason
        assert "below the minimum experience requirement" in reason
        assert "no culture keyword match" in reason
    
    def test_explanation_no_culture_keywords(self):
        reason = generate_match_reason(
            {1, 2}, {1, 2, 3},
            5, 3,
            {"analytical"}, set()
        )
        assert "2/3 required skills" in reason
        assert "exceeds the minimum experience requirement" in reason


class TestMatchingAPI:
    
    @pytest.mark.asyncio
    async def test_job_matches_endpoint(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/jobs/1/matches")
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == 1
            assert data["job_title"] == "Backend Detective"
            assert "matches" in data
            assert len(data["matches"]) == 15
            
            # Check sorting: score DESC, then experience DESC
            scores = [m["score"] for m in data["matches"]]
            assert scores == sorted(scores, reverse=True)
            
            # Verify Sherlock H. is top match for Backend Detective
            top_match = data["matches"][0]
            assert top_match["candidate_name"] == "Sherlock H."
            # Sherlock has 3/3 skills, 8/3 exp, but only 1/2 culture (analytical vs autonomous)
            # Score = 100*0.60 + 100*0.25 + 50*0.15 = 92.5
            assert top_match["score"] == 92.5
    
    @pytest.mark.asyncio
    async def test_job_matches_not_found(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/jobs/999/matches")
            assert response.status_code == 404
            assert response.json()["detail"] == "Job not found"
    
    @pytest.mark.asyncio
    async def test_candidate_matches_endpoint(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/candidates/1/matches")
            assert response.status_code == 200
            data = response.json()
            assert data["candidate_id"] == 1
            assert data["candidate_name"] == "Sherlock H."
            assert "matches" in data
            assert len(data["matches"]) == 6
            
            # Check sorting: score DESC, then job_id ASC
            scores = [m["score"] for m in data["matches"]]
            assert scores == sorted(scores, reverse=True)
            
            # Verify Backend Detective is top match for Sherlock
            top_match = data["matches"][0]
            assert top_match["job_title"] == "Backend Detective"
            # Same calculation: 3/3 skills, 8/3 exp, 1/2 culture = 92.5
            assert top_match["score"] == 92.5
    
    @pytest.mark.asyncio
    async def test_candidate_matches_not_found(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/candidates/999/matches")
            assert response.status_code == 404
            assert response.json()["detail"] == "Candidate not found"
    
    @pytest.mark.asyncio
    async def test_deterministic_tie_breaking_job_to_candidate(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/jobs/1/matches")
            data = response.json()
            
            # Find candidates with same score, verify experience tie-breaker
            same_score_groups = {}
            for m in data["matches"]:
                score = m["score"]
                if score not in same_score_groups:
                    same_score_groups[score] = []
                same_score_groups[score].append(m["candidate_id"])
            
            # For each score group with multiple candidates, verify experience DESC
            for score, candidate_ids in same_score_groups.items():
                if len(candidate_ids) > 1:
                    # Get their experience years
                    experiences = []
                    for cid in candidate_ids:
                        c_resp = await client.get(f"/candidates/{cid}")
                        experiences.append(c_resp.json()["experience_years"])
                    
                    # Should be sorted by experience DESC
                    assert experiences == sorted(experiences, reverse=True)
    
    @pytest.mark.asyncio
    async def test_deterministic_tie_breaking_candidate_to_job(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/candidates/1/matches")
            data = response.json()
            
            # Check that jobs with same score are sorted by job_id ASC
            same_score_groups = {}
            for m in data["matches"]:
                score = m["score"]
                if score not in same_score_groups:
                    same_score_groups[score] = []
                same_score_groups[score].append(m["job_id"])
            
            for score, job_ids in same_score_groups.items():
                if len(job_ids) > 1:
                    assert job_ids == sorted(job_ids)
    
    @pytest.mark.asyncio
    async def test_all_matches_have_reasons(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Test job matches
            resp = await client.get("/jobs/1/matches")
            for m in resp.json()["matches"]:
                assert "reason" in m
                assert len(m["reason"]) > 0
                assert m["reason"].endswith(".")
            
            # Test candidate matches
            resp = await client.get("/candidates/1/matches")
            for m in resp.json()["matches"]:
                assert "reason" in m
                assert len(m["reason"]) > 0
                assert m["reason"].endswith(".")