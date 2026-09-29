-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    experience_years INTEGER NOT NULL,
    availability VARCHAR(50) NOT NULL,
    quirk TEXT
);

-- Skills table (shared between candidates and jobs)
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Candidate skills junction table
CREATE TABLE IF NOT EXISTS candidate_skills (
    candidate_id INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (candidate_id, skill_id)
);

-- Candidate traits
CREATE TABLE IF NOT EXISTS candidate_traits (
    candidate_id INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    trait VARCHAR(100) NOT NULL,
    PRIMARY KEY (candidate_id, trait)
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    min_experience INTEGER NOT NULL,
    tagline TEXT
);

-- Job required skills junction table
CREATE TABLE IF NOT EXISTS job_required_skills (
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

-- Job culture keywords
CREATE TABLE IF NOT EXISTS job_culture_keywords (
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    keyword VARCHAR(100) NOT NULL,
    PRIMARY KEY (job_id, keyword)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_candidate_skills_candidate_id ON candidate_skills(candidate_id);
CREATE INDEX IF NOT EXISTS idx_candidate_skills_skill_id ON candidate_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_candidate_traits_candidate_id ON candidate_traits(candidate_id);
CREATE INDEX IF NOT EXISTS idx_job_required_skills_job_id ON job_required_skills(job_id);
CREATE INDEX IF NOT EXISTS idx_job_required_skills_skill_id ON job_required_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_job_culture_keywords_job_id ON job_culture_keywords(job_id);