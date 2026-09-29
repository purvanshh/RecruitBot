from app.db.connection import get_db_connection


def get_all_candidates():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.experience_years, c.availability, c.quirk
                FROM candidates c
                ORDER BY c.id
            """)
            candidates = cur.fetchall()
            
            for candidate in candidates:
                candidate['skills'] = get_candidate_skills(cur, candidate['id'])
                candidate['traits'] = get_candidate_traits(cur, candidate['id'])
            
            return candidates


def get_candidate_by_id(candidate_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.experience_years, c.availability, c.quirk
                FROM candidates c
                WHERE c.id = %s
            """, (candidate_id,))
            candidate = cur.fetchone()
            
            if candidate:
                candidate['skills'] = get_candidate_skills(cur, candidate['id'])
                candidate['traits'] = get_candidate_traits(cur, candidate['id'])
            
            return candidate


def get_candidate_skills(cur, candidate_id: int):
    cur.execute("""
        SELECT s.id, s.name
        FROM skills s
        JOIN candidate_skills cs ON s.id = cs.skill_id
        WHERE cs.candidate_id = %s
        ORDER BY s.name
    """, (candidate_id,))
    return cur.fetchall()


def get_candidate_traits(cur, candidate_id: int):
    cur.execute("""
        SELECT trait
        FROM candidate_traits
        WHERE candidate_id = %s
        ORDER BY trait
    """, (candidate_id,))
    return [row['trait'] for row in cur.fetchall()]