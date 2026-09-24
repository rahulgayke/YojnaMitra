# YojanaMitra — Stage 2: Official Source Registry

A layered, open-source government-scheme advisor for Indian citizens. The key product
principle remains: **the LLM coordinates and explains; deterministic systems make
deterministic decisions; official evidence grounds factual claims.**

Stage 2 extends the **corrected Stage 0 + Stage 1 repository**. It does not begin the RAG,
LLM, eligibility engine or frontend. The frontend remains a separate future Next.js app.

## What Stage 2 adds

- 20 curated Central Government scheme identities spanning agriculture, energy, housing,
  healthcare, women's welfare, artisans, livelihoods, finance, education and social security.
- 21 linked official-source records, including a secondary government announcement for
  PM SVANidhi. Source authority, URL, tier, identity-review method and calendar date retained.
- Offline strict JSON validation, host-safety controls, duplicate detection, and provenance
  labels; no automatic source fetching or myScheme scraping.
- Atomic/idempotent import with stable source IDs and conflict rejection.
- `GET /api/v1/schemes` (pagination/category/status filtering), existing scheme detail,
  and `GET /api/v1/sources/{source_id}`.
- Pytest tests for validation, import, rollback, CLI safety and API contracts.
- Source review ledger, no-scraping ADR and acceptance report.

**Important:** these are registry records, **not** a complete, citizen-ready scheme
knowledge base. Every scheme status is `unknown`, `Scheme.last_verified_at` is null,
`publish_ready=false`, and there are **zero machine-verified eligibility rules**. A source's
reviewed date means the official *link identity* was checked—not that benefits, deadlines,
operational status or complete eligibility were verified. Read
[`data/seed/README.md`](data/seed/README.md) and
[`STAGE-2-SOURCE-LEDGER.md`](docs/architecture/STAGE-2-SOURCE-LEDGER.md).

## Install (Windows PowerShell)

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

If you already have the Stage 1 virtual environment, reinstall the editable package from
the current checkout: `python -m pip install -e ".[dev]"`. Use `python -m ruff` to avoid
Windows PATH issues. The core dependencies include `tzdata` so `Asia/Kolkata` works
on Windows and other environments without an OS timezone database. If you already installed
Stage 2 before this fix, rerun `python -m pip install -e ".[dev]"`. Optional PostgreSQL driver:
`python -m pip install -e ".[dev,postgres]"`.

## Test each layer before combining them

From `backend/`:

```powershell
python -m pytest tests/test_seed_registry.py -q  # Stage 2 registry/service/API
python -m pytest -q                            # Stage 0–2 regression suite
python -m yojanamitra.cli validate-seed         # Offline schema + provenance checks
python -m alembic upgrade head                 # Reuse Stage 1 migration
python -m yojanamitra.cli seed-registry         # DRY RUN, no database write
python -m yojanamitra.cli seed-registry --apply # Explicit local import
python -m yojanamitra.cli seed-registry --apply # Idempotency: zero inserts
python -m uvicorn yojanamitra.main:app --reload
```

`validate-seed` returns the following counts for the supplied corpus:

```json
{
  "schemes": 20,
  "sources": 21,
  "primary_source_schemes": 20,
  "rules": 0,
  "publish_ready": 0
}
```

From another PowerShell terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/schemes
Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/schemes?category=education'
Invoke-RestMethod http://127.0.0.1:8000/api/v1/schemes/pm-kisan
```

Fetch a source's UUID from the scheme detail response and query
`/api/v1/sources/{source_id}`. The active-only filter returns an empty list because this
stage has not verified operational status. Swagger UI: <http://127.0.0.1:8000/docs>.

The old synthetic sample remains available only by explicit ID for Stage 1 testing, and
is excluded from the scheme listing.

### Reset an existing Stage 1 local database?

**No reset is necessary.** `alembic upgrade head` will reuse Stage 1's existing schema.
The importer does not delete or overwrite your records. If there is a conflicting real
scheme ID/source, it rejects the operation and rolls back; reconcile it manually. There
is no Stage 2 schema migration.

## Quality gate

```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

All methods/functions need docstrings and non-obvious logic needs concise comments. Do
not mark Ruff/mypy or PostgreSQL as passed without running those tools locally.
The acceptance report records the known limitations:
[`docs/architecture/STAGE-2-ACCEPTANCE.md`](docs/architecture/STAGE-2-ACCEPTANCE.md).

## Next stages

Stage 3 reviews access rights then implements authorized downloads, MIME/hash validation,
PDF/HTML parsing and source-version metadata; Stage 4 adds chunking. Neither has been
implemented here. See [the delivery plan](PROJECT_DELIVERY_PLAN.md) and
[the task tracker](TASK_TRACKER.md).
