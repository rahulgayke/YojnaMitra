# YojanaMitra — Stage 1 (Structured Domain Model)

An open-source, incrementally tested Indian government-scheme advisor. The core product rule
is: **the LLM coordinates and explains; deterministic systems decide; official evidence
grounds claims.** Stage 1 introduces structure only; no verified schemes or eligibility
results are provided yet.

The corrected Stage 0 health API and source-resolution safeguard are preserved. See
[`PROJECT_DELIVERY_PLAN.md`](PROJECT_DELIVERY_PLAN.md),
[`TASK_TRACKER.md`](TASK_TRACKER.md) and
[`docs/architecture/STAGE-1-DATA-MODEL.md`](docs/architecture/STAGE-1-DATA-MODEL.md).

## What you get

- Six typed ORM entities and strict Pydantic input/output contracts.
- Migration-managed local persistence using SQLAlchemy and Alembic.
- SQLite by default so Stage 1 can be tested without Docker; an optional PostgreSQL driver
  and database URL for the planned production data layer.
- `GET /api/v1/schemes/{scheme_id}` returning stored metadata and sources.
- Synthetic-only, idempotent CLI test fixture; it cannot seed production settings.
- Isolated model/schema/migration/API tests and mandatory function/method docstrings.
- `frontend/` remains a separate future Next.js application boundary.

## Install (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Use this checkout's virtual environment rather than one from an earlier YojanaMitra version.
For future local PostgreSQL support, install `python -m pip install -e ".[dev,postgres]"`
and set `YOJANAMITRA_DATABASE_URL` to a `postgresql+psycopg://...` URL. That path is **not**
needed for Stage 1's SQLite acceptance gate.

## Test each layer

Run from `backend/`:

```powershell
python -m pytest tests/test_domain_schemas.py
python -m pytest tests/test_database.py
python -m pytest tests/test_demo_cli.py
python -m pytest tests/test_schemes_api.py
python -m pytest
```

Or from repository root:

```powershell
python -m pytest
```

Both paths are configured to import this checkout, not a stale editable install.

## Run the API and sample data

From `backend/` in the active virtual environment:

```powershell
python -m alembic upgrade head
python -m yojanamitra.cli seed-demo
python -m uvicorn yojanamitra.main:app --reload
```

In another PowerShell terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/schemes/stage1-demo-scheme
```

The sample is labeled **NOT A GOVERNMENT SCHEME** and its source is **NOT OFFICIAL**. It is
only for testing the data flow. The scheme response has `status: "unknown"`. Try a missing ID
(`nonexistent`) and check that it returns HTTP 404. API docs: <http://127.0.0.1:8000/docs>.

Do not call `Base.metadata.create_all()` against your application DB: use `alembic upgrade
head` so schema history is retained. Tests use isolated temporary databases.

## Quality gate before committing

```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

All Python functions and methods need meaningful docstrings. Test output and limitations are
recorded in [`STAGE-1-ACCEPTANCE.md`](docs/architecture/STAGE-1-ACCEPTANCE.md).

No LLM, eligibility evaluation, real scheme records, document ingestion, Qdrant, or frontend
features have been added. Stage 2 is the **official source registry and ~20 manually verified
Central Government seed schemes**.
