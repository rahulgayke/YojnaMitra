# Stage 1 — Acceptance gate

## Independently testable layers

| Layer | Test |
| --- | --- |
| Pydantic contracts | `python -m pytest tests/test_domain_schemas.py` |
| ORM relationships and constraints | `python -m pytest tests/test_database.py` |
| Alembic migration upgrade/downgrade | `python -m pytest tests/test_database.py -k migration` |
| Local test data safety | `python -m pytest tests/test_demo_cli.py` |
| FastAPI read contract | `python -m pytest tests/test_schemes_api.py` |
| Stage 0 regression and documentation | `python -m pytest` |

All commands run from `backend/`. From repository root, `python -m pytest` loads the same
checkout because of the root `pytest.ini`.

## Manual smoke gate (PowerShell, from `backend/`)

```powershell
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m yojanamitra.cli seed-demo
python -m uvicorn yojanamitra.main:app --reload
```

In a second terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/schemes/stage1-demo-scheme
```

Expected scheme ID: `stage1-demo-scheme`; status `unknown`, one source with `is_official=false`.
The record is explicitly synthetic. `GET /api/v1/schemes/nonexistent` must return HTTP 404.

## Not covered by this gate

This workspace did not have a PostgreSQL server or downloadable Ruff/mypy packages. Run
`python -m ruff check .`, `python -m ruff format --check .`, and `python -m mypy src`
on your developer machine. A live PostgreSQL migration is planned as a separate integration
gate. Do not treat the Stage 1 synthetic record as verified government information.
