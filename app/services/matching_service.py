from typing import List, Dict, Any
from app.db.connection import get_db_connection
from app.utils.scoring import (
    calculate_skill_score,
    calculate_experience_score,
    calculate_culture_score,
    calculate_final_score,
    generate_match_reason
)


def get_candidate_data(candidate_id: int) -> Dict[str, Any]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.experience_years, c.availability, c.quirk
                FROM candidates c
                WHERE c.id = %s
            """, (candidate_id,))
            candidate = cur.fetchone()
            
            if not candidate:
                return None
            
            cur.execute("""
                SELECT s.id FROM skills s
                JOIN candidate_skills cs ON s.id = cs.skill_id
                WHERE cs.candidate_id = %s
            """, (candidate_id,))
            candidate['skill_ids'] = {row['id'] for row in cur.fetchall()}
            
            cur.execute("""
                SELECT trait FROM candidate_traits WHERE candidate_id = %s
            """, (candidate_id,))
            candidate['traits'] = {row['trait'] for row in cur.fetchall()}
            
            return candidate


def get_job_data(job_id: int) -> Dict[str, Any]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT j.id, j.title, j.min_experience, j.tagline
                FROM jobs j
                WHERE j.id = %s
            """, (job_id,))
            job = cur.fetchone()
            
            if not job:
                return None
            
            cur.execute("""
                SELECT s.id FROM skills s
                JOIN job_required_skills jrs ON s.id = jrs.skill_id
                WHERE jrs.job_id = %s
            """, (job_id,))
            job['required_skill_ids'] = {row['id'] for row in cur.fetchall()}
            
            cur.execute("""
                SELECT keyword FROM job_culture_keywords WHERE job_id = %s
            """, (job_id,))
            job['culture_keywords'] = {row['keyword'] for row in cur.fetchall()}
            
            return job


def get_all_candidates_for_matching() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.experience_years, c.availability, c.quirk
                FROM candidates c
                ORDER BY c.id
            """)
            candidates = cur.fetchall()
            
            for candidate in candidates:
                cur.execute("""
                    SELECT s.id FROM skills s
                    JOIN candidate_skills cs ON s.id = cs.skill_id
                    WHERE cs.candidate_id = %s
                """, (candidate['id'],))
                candidate['skill_ids'] = {row['id'] for row in cur.fetchall()}
                
                cur.execute("""
                    SELECT trait FROM candidate_traits WHERE candidate_id = %s
                """, (candidate['id'],))
                candidate['traits'] = {row['trait'] for row in cur.fetchall()}
            
            return candidates


def get_all_jobs_for_matching() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT j.id, j.title, j.min_experience, j.tagline
                FROM jobs j
                ORDER BY j.id
            """)
            jobs = cur.fetchall()
            
            for job in jobs:
                cur.execute("""
                    SELECT s.id FROM skills s
                    JOIN job_required_skills jrs ON s.id = jrs.skill_id
                    WHERE jrs.job_id = %s
                """, (job['id'],))
                job['required_skill_ids'] = {row['id'] for row in cur.fetchall()}
                
                cur.execute("""
                    SELECT keyword FROM job_culture_keywords WHERE job_id = %s
                """, (job['id'],))
                job['culture_keywords'] = {row['keyword'] for row in cur.fetchall()}
            
            return jobs


def calculate_match(candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    skill_score = calculate_skill_score(candidate['skill_ids'], job['required_skill_ids'])
    experience_score = calculate_experience_score(candidate['experience_years'], job['min_experience'])
    culture_score = calculate_culture_score(candidate['traits'], job['culture_keywords'])
    final_score = calculate_final_score(skill_score, experience_score, culture_score)
    
    reason = generate_match_reason(
        candidate['skill_ids'],
        job['required_skill_ids'],
        candidate['experience_years'],
        job['min_experience'],
        candidate['traits'],
        job['culture_keywords']
    )
    
    return {
        'candidate_id': candidate['id'],
        'candidate_name': candidate['name'],
        'job_id': job['id'],
        'job_title': job['title'],
        'score': final_score,
        'skill_score': skill_score,
        'experience_score': experience_score,
        'culture_score': culture_score,
        'reason': reason
    }


def get_job_matches(job_id: int) -> Dict[str, Any]:
    job = get_job_data(job_id)
    if not job:
        return None
    
    candidates = get_all_candidates_for_matching()
    
    matches = []
    for candidate in candidates:
        match = calculate_match(candidate, job)
        matches.append({
            'candidate_id': match['candidate_id'],
            'candidate_name': match['candidate_name'],
            'score': match['score'],
            'reason': match['reason']
        })
    
    matches.sort(key=lambda m: (-m['score'], -next(c['experience_years'] for c in candidates if c['id'] == m['candidate_id']), m['candidate_id']))
    
    return {
        'job_id': job['id'],
        'job_title': job['title'],
        'matches': matches
    }


def get_candidate_matches(candidate_id: int) -> Dict[str, Any]:
    candidate = get_candidate_data(candidate_id)
    if not candidate:
        return None
    
    jobs = get_all_jobs_for_matching()
    
    matches = []
    for job in jobs:
        match = calculate_match(candidate, job)
        matches.append({
            'job_id': match['job_id'],
            'job_title': match['job_title'],
            'score': match['score'],
            'reason': match['reason']
        })
    
    matches.sort(key=lambda m: (-m['score'], m['job_id']))
    
    return {
        'candidate_id': candidate['id'],
        'candidate_name': candidate['name'],
        'matches': matches
    }