# YojanaMitra

YojanaMitra is an open-source AI engineering project for helping Indian citizens discover and understand government schemes using structured eligibility logic and official evidence.

This repository snapshot implements **Stage 1 — Repository Foundation only**.

## Stage 1 included

- Python 3.11 project using a `src/` layout
- FastAPI application
- PostgreSQL connectivity
- Redis connectivity
- Qdrant connectivity
- Docker Compose local stack
- Liveness and readiness health endpoints
- Pytest unit and integration test foundations
- Ruff, mypy, Bandit and pip-audit checks
- GitHub Actions CI
- Docker image build

## Deliberately not implemented yet

The following belong to later stages and are intentionally absent:

- Scheme / Source / EligibilityRule / Document / Chunk / UserProfile models
- Government scheme dataset
- Eligibility engine
- Parsing, chunking, embeddings and RAG
- Retrieval evaluation
- Hybrid retrieval and reranking
- LangGraph agents
- Frontend
- Multilingual and voice features

## Repository layout

```text
.
├── .github/workflows/ci.yml
├── docs/decisions/
├── scripts/wait_for_services.py
├── src/yojanamitra/
│   ├── api/routes/health.py
│   ├── core/config.py
│   ├── core/logging.py
│   ├── infrastructure/cache.py
│   ├── infrastructure/database.py
│   ├── infrastructure/vector_store.py
│   └── main.py
├── tests/
│   ├── integration/
│   └── unit/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── pyproject.toml
```

## Local setup

### Option A — Docker Compose

```bash
docker compose up --build
```

The Compose file has safe local-development defaults. Copy `.env.example` to `.env` only when you want to override them.

Then open:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Liveness: `http://localhost:8000/api/v1/health/live`
- Readiness: `http://localhost:8000/api/v1/health/ready`

### Option B — Run API locally, infrastructure in Docker

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"

docker compose up -d postgres redis qdrant
```

If running the API on the host instead of inside Docker, override service hosts:

```bash
export POSTGRES_HOST=localhost
export REDIS_URL=redis://localhost:6379/0
export QDRANT_URL=http://localhost:6333
uvicorn yojanamitra.main:app --reload
```

On PowerShell:

```powershell
$env:POSTGRES_HOST="localhost"
$env:REDIS_URL="redis://localhost:6379/0"
$env:QDRANT_URL="http://localhost:6333"
uvicorn yojanamitra.main:app --reload
```

## Tests and quality checks

```bash
pytest tests/unit -q
RUN_INTEGRATION=1 pytest tests/integration -q
ruff check .
mypy src
bandit -q -r src
pip-audit
```

## Health contract

`GET /api/v1/health/live` only verifies that the API process is alive.

`GET /api/v1/health/ready` verifies dependencies and returns HTTP 200 only when PostgreSQL, Redis and Qdrant are reachable. It returns HTTP 503 if one or more dependencies are unavailable.

## Next stage

**Stage 2 — Data Model** should add `Scheme`, `Source`, `EligibilityRule`, `Document`, `Chunk`, and `UserProfile`, with database migrations and model-level tests.
