# YojanaMitra

YojanaMitra is an open-source government-scheme discovery and guidance platform for Indian citizens. The system will eventually combine verified government information, deterministic eligibility evaluation, retrieval-augmented generation (RAG), and a citizen-facing web application.

This repository is being built incrementally. **Stage 0 intentionally contains no scheme database, vector database, LLM, RAG pipeline, eligibility engine, or production deployment infrastructure.**

## Stage 0 scope

Stage 0 establishes the development contract and the smallest runnable backend slice:

- Python backend package
- environment-based configuration
- minimal FastAPI application
- `GET /api/v1/health`
- shared API response/error schemas
- Pytest smoke tests
- documentation and ADR structure
- separate frontend application boundary
- repeatable local commands for every test gate

See [`TASK_TRACKER.md`](TASK_TRACKER.md) for stage-by-stage delivery status.

## Repository layout

```text
yojanamitra/
├── backend/                 # FastAPI + future AI/domain services
│   ├── src/yojanamitra/
│   └── tests/
├── frontend/                # Separate citizen-facing web application
├── docs/
│   ├── architecture/
│   ├── decisions/
│   └── standards/
├── PROJECT_DELIVERY_PLAN.md
├── TASK_TRACKER.md
└── OPEN_SOURCE_STACK.md
```

## Prerequisites

- Python 3.11 or newer
- Git

No Docker, database, model server, or frontend runtime is required for Stage 0.

## Backend setup

Run the installation and API commands from the `backend` directory. Tests also work
from the repository root using its `pytest.ini`; both paths explicitly load this checkout.

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install the backend and developer dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 3. Run tests

```bash
python -m pytest
```

Expected Stage 0 result: all tests pass. You can also return to the repository
root and run `python -m pytest` there. The root `pytest.ini` ensures the
current `backend/src` package is used even if an older YojanaMitra stage was
previously installed.

If imports seem wrong, use this diagnostic from `backend/`:

```powershell
python -c "import yojanamitra; print(yojanamitra.__file__)"
```

It should point to this checkout's `backend/src/yojanamitra/__init__.py`.
Do not mix Stage 0 and the older Stage 1/2 repositories in one virtual environment.
Create/activate `backend/.venv` before installing this project.

### 4. Start the API

```bash
python -m uvicorn yojanamitra.main:app --reload
```

Then test it from another terminal:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "yojanamitra-api",
  "environment": "local",
  "api_version": "v1"
}
```

Interactive OpenAPI docs are available locally at:

```text
http://127.0.0.1:8000/docs
```

## Local quality checks

Use module-style commands so they work reliably across Windows, macOS, and Linux:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

Ruff formatting fixes can be applied with:

```bash
python -m ruff format .
python -m ruff check . --fix
```

## Development rule

Every stage follows the same sequence:

1. Define the service/layer contract.
2. Implement the smallest working unit.
3. Add unit tests.
4. Add an integration/endpoint/CLI check where appropriate.
5. Run the complete test gate.
6. Update `TASK_TRACKER.md`.
7. Only then integrate the next service.

Every Python function and method must have a useful docstring. Comments should explain non-obvious decisions rather than restating the code.
