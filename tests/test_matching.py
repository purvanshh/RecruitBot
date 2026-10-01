import sys
sys.path.insert(0, "/app")

import pytest
from app.utils.scoring import (
    calculate_skill_score,
    calculate_experience_score,
    calculate_culture_score,
    calculate_final_score,
    generate_match_reason
)


class TestScoringFunctions:

    def test_exact_skill_match(self):
        assert calculate_skill_score({1, 2, 3}, {1, 2, 3}) == 100.0

    def test_partial_skill_match(self):
        assert calculate_skill_score({1, 2}, {1, 2, 3}) == 66.67

    def test_zero_skill_match(self):
        assert calculate_skill_score({4, 5}, {1, 2, 3}) == 0.0

    def test_no_required_skills(self):
        assert calculate_skill_score({1, 2}, set()) == 100.0

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
        assert calculate_culture_score({"analytical", "autonomous"}, {"analytical", "autonomous"}) == 100.0

    def test_partial_culture_match(self):
        assert calculate_culture_score({"analytical"}, {"analytical", "autonomous"}) == 50.0

    def test_no_culture_match(self):
        assert calculate_culture_score({"creative"}, {"analytical", "autonomous"}) == 0.0

    def test_no_culture_keywords(self):
        assert calculate_culture_score({"analytical"}, set()) == 100.0

    def test_final_weighted_score(self):
        assert calculate_final_score(100.0, 100.0, 100.0) == 100.0

    def test_final_weighted_score_mixed(self):
        expected = round(66.67 * 0.60 + 75.0 * 0.25 + 50.0 * 0.15, 2)
        assert calculate_final_score(66.67, 75.0, 50.0) == expected

    def test_explanation_exact_match(self):
        reason = generate_match_reason(
            {1, 2, 3}, {1, 2, 3},
            8, 3,
            {"analytical", "autonomous"}, {"analytical", "autonomous"}
        )
        assert reason == (
            "Matched 3/3 required skills, meets or exceeds the minimum experience requirement, "
            "and aligns with the analytical, autonomous culture."
        )

    def test_explanation_partial_match(self):
        reason = generate_match_reason(
            {1, 2}, {1, 2, 3},
            2, 4,
            {"creative"}, {"analytical", "autonomous"}
        )
        assert reason == (
            "Matched 2/3 required skills, is below the minimum experience requirement, "
            "and does not match culture keywords."
        )

    def test_explanation_no_culture_keywords(self):
        reason = generate_match_reason(
            {1, 2}, {1, 2, 3},
            5, 3,
            {"analytical"}, set()
        )
        assert reason == (
            "Matched 2/3 required skills and meets or exceeds the minimum experience requirement."
        )


class TestMatchingAPI:

    @pytest.mark.asyncio
    async def test_job_matches_endpoint(self, client):
        response = await client.get("/jobs/1/matches")
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == 1
        assert data["job_title"] == "Backend Detective"
        assert len(data["matches"]) == 15

        scores = [m["score"] for m in data["matches"]]
        assert scores == sorted(scores, reverse=True)

        top_match = data["matches"][0]
        assert top_match["candidate_name"] == "Sherlock H."
        # 3/3 skills, 8 yrs vs min 3, 1/2 culture (analytical) => 92.5
        assert top_match["score"] == 92.5
        assert "Matched 3/3 required skills" in top_match["reason"]
        assert "analytical" in top_match["reason"]

    @pytest.mark.asyncio
    async def test_job_matches_not_found(self, client):
        response = await client.get("/jobs/999/matches")
        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"

    @pytest.mark.asyncio
    async def test_candidate_matches_endpoint(self, client):
        response = await client.get("/candidates/1/matches")
        assert response.status_code == 200
        data = response.json()
        assert data["candidate_id"] == 1
        assert data["candidate_name"] == "Sherlock H."
        assert len(data["matches"]) == 6

        scores = [m["score"] for m in data["matches"]]
        assert scores == sorted(scores, reverse=True)

        top_match = data["matches"][0]
        assert top_match["job_title"] == "Backend Detective"
        assert top_match["score"] == 92.5

    @pytest.mark.asyncio
    async def test_candidate_matches_not_found(self, client):
        response = await client.get("/candidates/999/matches")
        assert response.status_code == 404
        assert response.json()["detail"] == "Candidate not found"

    @pytest.mark.asyncio
    async def test_deterministic_tie_breaking_job_to_candidate(self, client):
        response = await client.get("/jobs/1/matches")
        data = response.json()

        same_score_groups = {}
        for m in data["matches"]:
            same_score_groups.setdefault(m["score"], []).append(m["candidate_id"])

        for candidate_ids in same_score_groups.values():
            if len(candidate_ids) > 1:
                experiences = []
                for cid in candidate_ids:
                    c_resp = await client.get(f"/candidates/{cid}")
                    experiences.append(c_resp.json()["experience_years"])
                assert experiences == sorted(experiences, reverse=True)

    @pytest.mark.asyncio
    async def test_deterministic_tie_breaking_candidate_to_job(self, client):
        response = await client.get("/candidates/1/matches")
        data = response.json()

        same_score_groups = {}
        for m in data["matches"]:
            same_score_groups.setdefault(m["score"], []).append(m["job_id"])

        for job_ids in same_score_groups.values():
            if len(job_ids) > 1:
                assert job_ids == sorted(job_ids)

    @pytest.mark.asyncio
    async def test_all_matches_have_reasons(self, client):
        resp = await client.get("/jobs/1/matches")
        for m in resp.json()["matches"]:
            assert m["reason"]
            assert m["reason"].endswith(".")
            assert " requiredskills" not in m["reason"].replace(" ", "")
            assert "theminimum" not in m["reason"]

        resp = await client.get("/candidates/1/matches")
        for m in resp.json()["matches"]:
            assert m["reason"]
            assert m["reason"].endswith(".")

    @pytest.mark.asyncio
    async def test_pdf_seed_traits_and_ted_optimism(self, client):
        """Guard assignment PDF seed fidelity for traits and Ted's optimism skill."""
        expected_traits = {
            1: {"analytical", "blunt"},
            2: {"detail-oriented", "overachiever"},
            3: {"confident", "innovative"},
            4: {"tenacious", "organized"},
            5: {"stubborn", "principled"},
            6: {"genius", "reckless"},
            7: {"optimistic", "sharp"},
            8: {"calm", "improviser"},
            9: {"rigid", "brilliant"},
            10: {"resilient", "decisive"},
            11: {"enthusiastic", "chaotic"},
            12: {"decisive", "intense"},
            13: {"empathetic", "persistent"},
            14: {"demanding", "decisive"},
            15: {"intense", "loyal"},
        }

        for candidate_id, traits in expected_traits.items():
            resp = await client.get(f"/candidates/{candidate_id}")
            assert resp.status_code == 200
            body = resp.json()
            assert set(body["traits"]) == traits

        ted = (await client.get("/candidates/13")).json()
        skill_names = {s["name"] for s in ted["skills"]}
        assert skill_names == {
            "team-building",
            "optimism",
            "mentorship",
            "public-speaking",
        }
