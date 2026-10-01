-- =============================================
-- SQL DETECTIVE CHALLENGE
-- RecruiterFlow Backend Assignment — Section B, Part 2
-- =============================================
-- Load the assignment-supplied schema and seed data as-is
-- (do not redesign). Then run the five queries below.
--
-- Supplied schema (for reference — do not redesign):
--
-- CREATE TABLE recruiters (
--     id INT PRIMARY KEY,
--     name VARCHAR(100),
--     region VARCHAR(50)
-- );
--
-- CREATE TABLE job_postings (
--     id INT PRIMARY KEY,
--     title VARCHAR(100),
--     recruiter_id INT,
--     department VARCHAR(50),
--     opened_date DATE,
--     status VARCHAR(20)  -- 'open', 'closed', 'on_hold'
-- );
--
-- CREATE TABLE applicants (
--     id INT PRIMARY KEY,
--     full_name VARCHAR(100),
--     email VARCHAR(100),
--     source VARCHAR(50),  -- nullable
--     applied_date DATE
-- );
--
-- CREATE TABLE interviews (
--     id INT PRIMARY KEY,
--     applicant_id INT,
--     job_posting_id INT,
--     stage VARCHAR(20),  -- 'Screen', 'Technical', 'Final'
--     scheduled_date DATE,
--     outcome VARCHAR(20)  -- 'passed', 'failed', 'no_show', NULL (pending)
-- );

-- Question 1
-- List all currently open job postings, along with the name of the
-- recruiter who owns each one.
SELECT
    jp.id AS job_posting_id,
    jp.title AS job_title,
    jp.department,
    jp.opened_date,
    r.id AS recruiter_id,
    r.name AS recruiter_name,
    r.region AS recruiter_region
FROM job_postings jp
JOIN recruiters r ON jp.recruiter_id = r.id
WHERE jp.status = 'open'
ORDER BY jp.opened_date, jp.id;

-- Question 2
-- For each job posting, how many applicants reached the Final
-- interview stage?
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

-- Question 3
-- Find every person who effectively applied to more than one job posting.
-- Careful — the data isn't as clean as it looks (e.g. Ananya Rao appears
-- twice with differently-cased emails).
--
-- Assumption: the supplied dataset has no applicant↔job applications
-- junction table, so an application is inferred from interviews —
-- a person "applied" to a job if they have at least one interview for it.
-- People are de-duplicated by full_name + LOWER(email).
WITH normalized_applicants AS (
    SELECT
        a.full_name,
        LOWER(a.email) AS normalized_email,
        i.job_posting_id
    FROM applicants a
    JOIN interviews i ON a.id = i.applicant_id
),
person_applications AS (
    SELECT
        full_name AS name,
        normalized_email,
        COUNT(DISTINCT job_posting_id) AS job_count,
        STRING_AGG(DISTINCT job_posting_id::text, ', ' ORDER BY job_posting_id::text) AS job_ids
    FROM normalized_applicants
    GROUP BY full_name, normalized_email
    HAVING COUNT(DISTINCT job_posting_id) > 1
)
SELECT
    name,
    normalized_email AS email,
    job_count,
    job_ids
FROM person_applications
ORDER BY job_count DESC, name;

-- Question 4
-- For each recruiter, compute their Final-stage conversion rate
-- (passed ÷ total Final-stage interviews), but only include
-- recruiters with at least 3 Final-stage interviews.
WITH final_interviews AS (
    SELECT
        r.id AS recruiter_id,
        r.name AS recruiter_name,
        r.region,
        i.outcome
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
        COUNT(*) FILTER (WHERE outcome = 'passed') AS passed_final_interviews
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
        (passed_final_interviews::numeric / total_final_interviews) * 100,
        2
    ) AS conversion_rate_percent
FROM recruiter_stats
ORDER BY conversion_rate_percent DESC, recruiter_name;

-- Question 5
-- (Bonus) Using a window function, find the recruiter with the most
-- successful placements (passed at Final stage) per department.
WITH final_placements AS (
    SELECT
        jp.department,
        r.id AS recruiter_id,
        r.name AS recruiter_name,
        COUNT(*) FILTER (WHERE i.outcome = 'passed') AS successful_placements
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
        ROW_NUMBER() OVER (
            PARTITION BY department
            ORDER BY successful_placements DESC, recruiter_id
        ) AS rn
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
