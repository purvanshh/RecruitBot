# RecruiterBot — Candidate ↔ Job Matching Backend

A backend service for matching candidates to jobs and vice versa, built for the RecruiterFlow Backend Developer Internship assignment.

## Tech Stack

- **Python 3.12**
- **FastAPI** — Web framework
- **PostgreSQL 16** — Database
- **psycopg3** — Database driver (raw SQL, no ORM)
- **Pydantic** — Data validation
- **pytest** — Testing
- **Docker** — Containerization

## Project Structure

```
recruiterbot/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration via environment variables
│   ├── db/
│   │   ├── connection.py       # Database connection & initialization
│   │   ├── schema.sql          # Database schema (handwritten SQL)
│   │   └── seed.sql            # Seed data (15 candidates, 6 jobs)
│   ├── models/
│   │   └── schemas.py          # Pydantic response models
│   ├── repositories/
│   │   ├── candidate_repository.py  # Candidate data access
│   │   └── job_repository.py        # Job data access
│   └── api/
│       ├── candidates.py       # Candidate endpoints
│       └── jobs.py             # Job endpoints
├── tests/
│   ├── test_health.py          # Health & database tests
│   └── test_candidates_jobs.py # Candidate & job API tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # API container
├── docker-compose.yml          # Multi-container orchestration
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Or: Python 3.12+ and PostgreSQL 16+ installed locally

### Using Docker (Recommended)

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Start services:**
   ```bash
   docker compose up --build
   ```

3. **Verify:**
   - API: http://localhost:8000
   - Health check: http://localhost:8000/health
   - Swagger docs: http://localhost:8000/docs

### Local Development (Without Docker)

1. **Start PostgreSQL** (ensure it's running on port 5432)

2. **Create database:**
   ```sql
   CREATE DATABASE recruiterbot;
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recruiterbot
   export APP_ENV=development
   ```

5. **Run the API:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/recruiterbot` |
| `APP_ENV` | Application environment | `development` |

## Database Schema

The schema uses normalized tables with proper foreign keys:

- **candidates** — Candidate profiles
- **skills** — Shared skill catalog
- **candidate_skills** — Many-to-many: candidates ↔ skills
- **candidate_traits** — Candidate personality traits
- **jobs** — Job openings
- **job_required_skills** — Many-to-many: jobs ↔ skills
- **job_culture_keywords** — Job culture keywords

All tables have appropriate indexes for query performance.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/candidates` | List all candidates |
| GET | `/candidates/{id}` | Get candidate by ID |
| GET | `/jobs` | List all jobs |
| GET | `/jobs/{id}` | Get job by ID |
| GET | `/jobs/{id}/matches` | Rank candidates for a job |
| GET | `/candidates/{id}/matches` | Rank jobs for a candidate |

### Example Requests

```bash
# Health check
curl http://localhost:8000/health

# List candidates
curl http://localhost:8000/candidates

# Get candidate
curl http://localhost:8000/candidates/1

# List jobs
curl http://localhost:8000/jobs

# Get job
curl http://localhost:8000/jobs/1
```

### Example Responses

**GET /candidates/1**
```json
{
  "id": 1,
  "name": "Sherlock H.",
  "skills": [
    {"id": 1, "name": "deduction"},
    {"id": 2, "name": "pattern-recognition"},
    {"id": 3, "name": "forensics"}
  ],
  "experience_years": 8,
  "availability": "Immediate",
  "traits": ["analytical", "blunt"],
  "quirk": "Solves problems by eliminating the impossible; occasionally insufferable in standups."
}
```

**GET /jobs/1**
```json
{
  "id": 1,
  "title": "Backend Detective",
  "required_skills": [
    {"id": 1, "name": "deduction"},
    {"id": 2, "name": "pattern-recognition"},
    {"id": 3, "name": "forensics"}
  ],
  "min_experience": 3,
  "culture_keywords": ["analytical", "autonomous"],
  "tagline": "We have a bug. We have no leads. We have you."
}
```

## Matching Algorithm

The matching engine calculates a **final score** based on three weighted components:

### Scoring Formula

```
Final Score = (Skill Score × 0.60) + (Experience Score × 0.25) + (Culture Score × 0.15)
```

### Component Scores

**Skill Score** (60% weight):
```
matched_required_skills / total_required_skills × 100
```

**Experience Score** (25% weight):
```
min(candidate_experience / job_min_experience × 100, 100)
```
Capped at 100.

**Culture Score** (15% weight):
```
matching_candidate_traits / total_culture_keywords × 100
```
If a job has no culture keywords, culture score defaults to 100 (neutral, doesn't penalize).

### Ranking

- **Job → Candidates**: Score DESC, then Experience DESC, then Candidate ID ASC
- **Candidate → Jobs**: Score DESC, then Job ID ASC

### Match Explanation

Each match includes a human-readable reason generated deterministically (no LLMs):
- "Matched 3/3 required skills and exceeds the minimum experience requirement."
- "Matched 2/3 required skills, meets experience requirement, and matches the analytical culture."

## Design Decisions & Trade-offs

1. **Raw SQL only** — No ORM/query builder as required by assignment. All queries are handwritten in repository modules.

2. **Normalized schema** — Skills, traits, and culture keywords are in separate tables with junction tables. This avoids data duplication and enables efficient set-based matching queries.

3. **Synchronous psycopg3** — Used with connection pooling via context managers. For a small assignment scope, async wasn't necessary but could be added for scale.

4. **Deterministic scoring** — All scoring logic is pure Python functions, making it easily testable and auditable.

5. **Seed data integrity** — Used `ON CONFLICT DO NOTHING` for idempotent seeding.

6. **No authentication/authorization** — Out of scope for this assignment.

## Running Tests

```bash
# With Docker
docker compose run --rm api pytest -v

# Locally
pytest -v
```

## SQL Detective Challenge

The `sql_detective.sql` file (to be added in Phase 4) contains the five analytical queries for the second part of the assignment, using the supplied recruiters/job_postings/applicants/interviews schema.

## AI Tool Usage

This project was built with assistance from AI coding tools for:
- Boilerplate generation (Docker, config, project structure)
- SQL schema and seed data formatting
- Test scaffolding

All core logic (matching algorithm, scoring, database queries) was designed and implemented manually.