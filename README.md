# RecruiterBot — Candidate ↔ Job Matching Backend

Backend service for the RecruiterFlow Backend Developer internship assignment (Section B): ingest fictional candidates and jobs, then rank matches in both directions using raw SQL.

## Tech Stack

- **Python 3.12**
- **FastAPI** — HTTP API
- **PostgreSQL 16** — relational store
- **psycopg3** — raw SQL only (no ORM / query builder)
- **psycopg-pool** — connection pooling
- **Pydantic** — response models
- **pytest** — tests
- **Docker Compose** — local run

## Project Structure

```
RecruitBot/
├── app/
│   ├── main.py                      # FastAPI entry, lifespan, exception handlers
│   ├── config.py                    # DATABASE_URL / APP_ENV settings
│   ├── db/
│   │   ├── connection.py            # Pool + schema/seed execution
│   │   ├── schema.sql               # Handwritten DDL
│   │   └── seed.sql                 # Assignment candidate/job seed data
│   ├── models/schemas.py            # Pydantic response models
│   ├── repositories/                # Handwritten SQL data access
│   ├── services/matching_service.py # Ranking + explanations
│   ├── api/                         # /candidates and /jobs routers
│   └── utils/scoring.py             # Pure scoring functions
├── tests/
├── sql_detective.sql                # Part 2 analytical queries
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

There is **no persisted `matches` table**. Matches are computed on each request from candidate/job data.

## Prerequisites

- Docker and Docker Compose, **or**
- Python 3.12+ and PostgreSQL 16+

## Setup

### Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000
- Health: http://localhost:8000/health
- Swagger: http://localhost:8000/docs

Schema and seed run automatically on API startup.

### Local (without Docker)

```bash
# Create DB
createdb recruiterbot   # or equivalent

pip install -r requirements.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recruiterbot
export APP_ENV=development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/recruiterbot` |
| `APP_ENV` | Application environment | `development` |

## Database Schema

Normalized handwritten SQL in `app/db/schema.sql`:

| Table | Purpose |
|-------|---------|
| `candidates` | Profile fields (name, experience, availability, quirk) |
| `skills` | Shared skill catalog |
| `candidate_skills` | Candidate ↔ skill |
| `candidate_traits` | Candidate traits |
| `jobs` | Job openings |
| `job_required_skills` | Job ↔ required skill |
| `job_culture_keywords` | Job culture keywords |

Foreign keys and indexes are defined in the schema file. Seed data in `app/db/seed.sql` matches the Section B PDF (15 candidates, 6 jobs).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/candidates` | List candidates |
| GET | `/candidates/{id}` | Get candidate |
| GET | `/jobs` | List jobs |
| GET | `/jobs/{id}` | Get job |
| GET | `/jobs/{id}/matches` | Ranked candidates for a job |
| GET | `/candidates/{id}/matches` | Ranked jobs for a candidate |

Required assignment endpoints are the two `/matches` routes. The list/detail routes are supporting APIs.

### curl examples

```bash
curl http://localhost:8000/health
curl http://localhost:8000/candidates
curl http://localhost:8000/candidates/1
curl http://localhost:8000/jobs
curl http://localhost:8000/jobs/1
curl http://localhost:8000/jobs/1/matches
curl http://localhost:8000/candidates/1/matches
```

### Example match response

```json
{
  "job_id": 1,
  "job_title": "Backend Detective",
  "matches": [
    {
      "candidate_id": 1,
      "candidate_name": "Sherlock H.",
      "score": 92.5,
      "reason": "Matched 3/3 required skills, meets or exceeds the minimum experience requirement, and aligns with the analytical culture."
    }
  ]
}
```

Unknown IDs return HTTP 404.

## Matching Algorithm

Matches are calculated in application code (`app/utils/scoring.py` + `app/services/matching_service.py`) after loading related rows with handwritten SQL. No LLM, embeddings, or external ranking APIs.

### Weights

| Component | Weight |
|-----------|--------|
| Skill overlap | 60% |
| Experience fit | 25% |
| Culture / traits | 15% |

```
final_score =
    skill_score * 0.60
  + experience_score * 0.25
  + culture_score * 0.15
```

Rounded to 2 decimal places.

### Component formulas

**Skill**

```
matched_required_skills / total_required_skills × 100
```

**Experience** (capped at 100)

```
min(candidate_experience / job_min_experience × 100, 100)
```

**Culture**

```
matching_traits / culture_keywords × 100
```

If a job has no culture keywords, culture score is 100 (neutral).

**Availability** is stored and returned on candidate profiles but is **not** used as a hard filter or score component.

### Ranking / tie-breaking

- Job → candidates: score DESC, experience_years DESC, candidate_id ASC
- Candidate → jobs: score DESC, job_id ASC

### Why culture/traits

The assignment requires skill overlap and experience fit, and leaves extra factors to us. Traits vs culture keywords are a small, deterministic third signal so near-ties on skills/experience still rank in a explainable way without overcomplicating the model.

### Match reasons

Each match includes a short deterministic sentence describing skills, experience, and culture contribution. Reasons are generated in code, not by an LLM.

## Design Decisions & Trade-offs

1. **Raw SQL only** — assignment constraint; all DDL/DML is handwritten.
2. **Normalized schema** — skills/traits/culture as separate tables instead of CSV strings.
3. **Dynamic matching** — no `matches` table; ranking stays consistent with live seed data and is easier to reason about for this dataset size.
4. **Weighted scoring** — explicit 60/25/15 mix; defended as skill-first with experience and culture as secondary signals.
5. **Idempotent seed** — junction tables are cleared and reloaded so corrected PDF traits/skills replace stale rows on restart.
6. **No auth / frontend / queues** — out of assignment scope.

## Testing

```bash
# Docker
docker compose run --rm api pytest -v

# Local (Postgres must be reachable via DATABASE_URL)
pytest -v
```

Coverage includes health, candidate/job reads, scoring units, bidirectional match APIs, ranking/tie-breaks, reason text, and PDF seed-data checks for traits/skills.

## SQL Detective (Part 2)

`sql_detective.sql` answers the five Part 2 questions against the **supplied** hiring-ops schema (`recruiters`, `job_postings`, `applicants`, `interviews`). That schema is separate from RecruiterBot’s own tables and is not redesigned.

1. Open job postings with owning recruiter
2. Final-stage applicant count per job posting
3. People who effectively applied to more than one job (normalize `LOWER(email)`; applications inferred via `interviews` because no application junction table is supplied)
4. Final-stage conversion rate per recruiter (≥ 3 Final interviews)
5. Bonus: top Final-stage placer per department (`ROW_NUMBER`)

Load the assignment’s detective schema/seed into a Postgres database, then:

```bash
psql "$DATABASE_URL" -f sql_detective.sql
```

## AI Tool Usage

AI assistants were used for boilerplate (Docker/config layout), formatting, and documentation polish. Matching weights, SQL design, detective query logic, and seed-data fidelity to the PDF were reviewed and owned as project decisions. Anything submitted should be explainable in a walkthrough.

## License / Submission

Built for the RecruiterFlow Backend Developer Intern take-home (Section B).
