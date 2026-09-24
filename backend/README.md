# YojanaMitra Backend

FastAPI backend package for YojanaMitra. See the repository-level `README.md`
for setup, testing, and the staged delivery process.

Install with `python -m pip install -e ".[dev]"` from this directory. Run
`python -m pytest` here, or from the repository root; both invocations load
this checkout instead of an older installed `yojanamitra` package.


Stage 1 adds typed domain contracts and Alembic-managed persistence. From `backend/`:

```bash
python -m alembic upgrade head
python -m yojanamitra.cli seed-demo
python -m uvicorn yojanamitra.main:app --reload
```

Test `GET http://127.0.0.1:8000/api/v1/schemes/stage1-demo-scheme`.
The fixture is **synthetic**, not a government scheme. Schema and migration tests use
isolated SQLite databases; no PostgreSQL server is required at this stage.
