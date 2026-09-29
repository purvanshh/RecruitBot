-- =============================================
-- SQL DETECTIVE CHALLENGE
-- =============================================
-- This file contains the analytical queries for the second part of the assignment.
-- The schema and seed data are provided by the assignment and must not be redesigned.

-- =============================================
-- SCHEMA (provided by assignment)
-- =============================================

-- CREATE TABLE recruiters (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     region VARCHAR(50) NOT NULL
-- );

-- CREATE TABLE job_postings (
--     id SERIAL PRIMARY KEY,
--     title VARCHAR(255) NOT NULL,
--     recruiter_id INTEGER REFERENCES recruiters(id),
--     department VARCHAR(100) NOT NULL,
--     posted_date DATE NOT NULL,
--     status VARCHAR(50) NOT NULL
-- );

-- CREATE TABLE applicants (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     email VARCHAR(255) NOT NULL,
--     source VARCHAR(100),
--     applied_date DATE NOT NULL
-- );

-- CREATE TABLE interviews (
--     id SERIAL PRIMARY KEY,
--     applicant_id INTEGER REFERENCES applicants(id),
--     job_posting_id INTEGER REFERENCES job_postings(id),
--     stage VARCHAR(50) NOT NULL,
--     scheduled_date DATE NOT NULL,
--     result VARCHAR(50)
-- );

-- =============================================
-- QUESTION 1
-- List all currently open job postings along with the recruiter who owns each.
-- =============================================
-- Question 1
SELECT 
    jp.id AS job_posting_id,
    jp.title AS job_title,
    jp.department,
    jp.posted_date,
    r.id AS recruiter_id,
    r.name AS recruiter_name,
    r.region AS recruiter_region
FROM job_postings jp
JOIN recruiters r ON jp.recruiter_id = r.id
WHERE jp.status = 'open'
ORDER BY jp.posted_date, jp.id;

-- =============================================
-- QUESTION 2
-- For each job posting, count how many applicants reached the Final interview stage.
-- =============================================
-- Question 2
SELECT 
    jp.id AS job_posting_id,
    jp.title AS job_title,
    COUNT(DISTINCT i.applicant_id) AS final_stage_applicant_count
FROM job_postings jp
LEFT JOIN interviews i 
    ON jp.id = i.job_posting_id 
    AND i.stage = 'Final'
GROUP BY jp.id, jp.title
ORDER BY jp.id;

-- =============================================
-- QUESTION 3
-- Find every person who effectively applied to more than one job posting.
-- IMPORTANT: The dataset contains duplicate-looking applicants such as:
-- Ananya Rao / ananya.rao@mail.com
-- Ananya Rao / Ananya.Rao@mail.com
-- Handle the data carefully rather than assuming applicant ID represents a unique person.
-- =============================================
-- Question 3
WITH normalized_applicants AS (
    SELECT 
        id,
        name,
        LOWER(email) AS normalized_email,
        applied_date,
        job_posting_id
    FROM applicants a
    JOIN interviews i ON a.id = i.applicant_id
),
person_applications AS (
    SELECT 
        name,
        normalized_email,
        COUNT(DISTINCT job_posting_id) AS job_count,
        STRING_AGG(DISTINCT job_posting_id::text, ', ' ORDER BY job_posting_id) AS job_ids
    FROM normalized_applicants
    GROUP BY name, normalized_email
    HAVING COUNT(DISTINCT job_posting_id) > 1
)
SELECT 
    name,
    normalized_email AS email,
    job_count,
    job_ids
FROM person_applications
ORDER BY job_count DESC, name;

-- =============================================
-- QUESTION 4
-- For each recruiter, calculate:
-- Final-stage conversion rate = passed Final interviews / total Final interviews
-- Only include recruiters with at least 3 Final-stage interviews.
-- =============================================
-- Question 4
WITH final_interviews AS (
    SELECT 
        r.id AS recruiter_id,
        r.name AS recruiter_name,
        r.region,
        i.result
    FROM recruiters r
    JOIN job_postings jp ON r.id = jp.recruiter_id
    JOIN interviews i ON jp.id = i.job_posting_id
    WHERE i.stage = 'Final'
),
recruiter_stats AS (
    SELECT 
        recruiter_id,
        recruiter_name,
        region,
        COUNT(*) AS total_final_interviews,
        COUNT(CASE WHEN result = 'passed' THEN 1 END) AS passed_final_interviews
    FROM final_interviews
    GROUP BY recruiter_id, recruiter_name, region
    HAVING COUNT(*) >= 3
)
SELECT 
    recruiter_id,
    recruiter_name,
    region,
    total_final_interviews,
    passed_final_interviews,
    ROUND(
        (passed_final_interviews::numeric / total_final_interviews) * 100, 2
    ) AS conversion_rate_percent
FROM recruiter_stats
ORDER BY conversion_rate_percent DESC, recruiter_name;

-- =============================================
-- QUESTION 5 (BONUS)
-- Using a window function, find the recruiter with the most successful 
-- Final-stage placements per department.
-- =============================================
-- Question 5
WITH final_placements AS (
    SELECT 
        jp.department,
        r.id AS recruiter_id,
        r.name AS recruiter_name,
        COUNT(CASE WHEN i.result = 'passed' THEN 1 END) AS successful_placements
    FROM recruiters r
    JOIN job_postings jp ON r.id = jp.recruiter_id
    JOIN interviews i ON jp.id = i.job_posting_id
    WHERE i.stage = 'Final'
    GROUP BY jp.department, r.id, r.name
),
ranked_recruiters AS (
    SELECT 
        department,
        recruiter_id,
        recruiter_name,
        successful_placements,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY successful_placements DESC, recruiter_id) AS rn
    FROM final_placements
)
SELECT 
    department,
    recruiter_id,
    recruiter_name,
    successful_placements
FROM ranked_recruiters
WHERE rn = 1
ORDER BY department;