from typing import Set


def calculate_skill_score(candidate_skill_ids: Set[int], job_required_skill_ids: Set[int]) -> float:
    if not job_required_skill_ids:
        return 100.0

    matched = len(candidate_skill_ids & job_required_skill_ids)
    total = len(job_required_skill_ids)
    return round((matched / total) * 100, 2)


def calculate_experience_score(candidate_experience: int, job_min_experience: int) -> float:
    if job_min_experience <= 0:
        return 100.0

    score = (candidate_experience / job_min_experience) * 100
    return round(min(score, 100.0), 2)


def calculate_culture_score(candidate_traits: Set[str], job_culture_keywords: Set[str]) -> float:
    if not job_culture_keywords:
        return 100.0

    matched = len(candidate_traits & job_culture_keywords)
    total = len(job_culture_keywords)
    return round((matched / total) * 100, 2)


def calculate_final_score(skill_score: float, experience_score: float, culture_score: float) -> float:
    final = (skill_score * 0.60) + (experience_score * 0.25) + (culture_score * 0.15)
    return round(final, 2)


def generate_match_reason(
    candidate_skill_ids: Set[int],
    job_required_skill_ids: Set[int],
    candidate_experience: int,
    job_min_experience: int,
    candidate_traits: Set[str],
    job_culture_keywords: Set[str]
) -> str:
    matched_count = len(candidate_skill_ids & job_required_skill_ids)
    total_skills = len(job_required_skill_ids)

    if total_skills > 0:
        skill_part = f"Matched {matched_count}/{total_skills} required skills"
    else:
        skill_part = "No required skills specified"

    if candidate_experience >= job_min_experience:
        experience_part = "meets or exceeds the minimum experience requirement"
    else:
        experience_part = "is below the minimum experience requirement"

    parts = [skill_part, experience_part]

    if job_culture_keywords:
        matched_traits = candidate_traits & job_culture_keywords
        if matched_traits:
            traits_str = ", ".join(sorted(matched_traits))
            parts.append(f"aligns with the {traits_str} culture")
        else:
            parts.append("does not match culture keywords")

    if len(parts) == 1:
        return f"{parts[0]}."
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}."
    return f"{parts[0]}, {parts[1]}, and {parts[2]}."
