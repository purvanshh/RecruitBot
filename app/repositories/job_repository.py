from app.db.connection import get_db_connection


def get_all_jobs():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT j.id, j.title, j.min_experience, j.tagline
                FROM jobs j
                ORDER BY j.id
            """)
            jobs = cur.fetchall()
            
            for job in jobs:
                job['required_skills'] = get_job_required_skills(cur, job['id'])
                job['culture_keywords'] = get_job_culture_keywords(cur, job['id'])
            
            return jobs


def get_job_by_id(job_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT j.id, j.title, j.min_experience, j.tagline
                FROM jobs j
                WHERE j.id = %s
            """, (job_id,))
            job = cur.fetchone()
            
            if job:
                job['required_skills'] = get_job_required_skills(cur, job['id'])
                job['culture_keywords'] = get_job_culture_keywords(cur, job['id'])
            
            return job


def get_job_required_skills(cur, job_id: int):
    cur.execute("""
        SELECT s.id, s.name
        FROM skills s
        JOIN job_required_skills jrs ON s.id = jrs.skill_id
        WHERE jrs.job_id = %s
        ORDER BY s.name
    """, (job_id,))
    return cur.fetchall()


def get_job_culture_keywords(cur, job_id: int):
    cur.execute("""
        SELECT keyword
        FROM job_culture_keywords
        WHERE job_id = %s
        ORDER BY keyword
    """, (job_id,))
    return [row['keyword'] for row in cur.fetchall()]