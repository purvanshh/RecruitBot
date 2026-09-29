from typing import List, Set


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
    matched_skills = candidate_skill_ids & job_required_skill_ids
    matched_count = len(matched_skills)
    total_skills = len(job_required_skill_ids)
    
    parts = []
    
    if total_skills > 0:
        parts.append(f"Matched {matched_count}/{total_skills} required skills")
    else:
        parts.append("No required skills specified")
    
    if candidate_experience >= job_min_experience:
        parts.append("exceeds the minimum experience requirement")
    else:
        parts.append("below the minimum experience requirement")
    
    if job_culture_keywords:
        matched_traits = candidate_traits & job_culture_keywords
        if matched_traits:
            traits_str = ", ".join(sorted(matched_traits))
            parts.append(f"and matches the {traits_str} culture")
        else:
            parts.append("but no culture keyword match")
    
    return ". ".join(parts) + "."