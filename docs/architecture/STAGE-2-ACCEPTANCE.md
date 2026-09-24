# Stage 2 acceptance — official source registry

## Boundary

Adds a read-only official-source registry and an offline validation/import path to the
existing Stage 1 domain model. **No** new ORM entities, database migrations, scraping,
download/parsing, RAG, active-status claims, benefit amounts or eligibility evaluation.

## Tests / commands

Run from `backend/` in the project's virtual environment:

```powershell
python -m pytest tests/test_seed_registry.py -q
python -m pytest -q
python -m yojanamitra.cli validate-seed
python -m alembic upgrade head
python -m yojanamitra.cli seed-registry
python -m yojanamitra.cli seed-registry --apply
python -m yojanamitra.cli seed-registry --apply
python -m uvicorn yojanamitra.main:app --reload
```

For HTTP checks, use `/api/v1/health`, `/api/v1/schemes`, `/api/v1/schemes/pm-kisan`, and
`/api/v1/sources/{source_uuid}`. Filtering: `?category=education`; active-only returns none.

## Implementation gate

- Manifest validation requires one government primary source per scheme.
- Official HTTPS host allowlisting; rejects deceptive hostnames and myScheme in seed input.
- 20 identities / 21 sources; primary source for all; duplicate IDs and URLs rejected.
- Reproducible UUIDs and transaction-scoped import; reruns do not create duplicate rows.
- Conflicting existing records stop import and rollback rather than overwrite.
- Source review *scope* and *method* are retained; unparsed content is labeled unparsed.
- Every scheme remains `status=unknown`, `publish_ready=false` and has no rules.
- The original synthetic test record is excluded from default scheme listing.
- Stage 0 and Stage 1 tests remain in the suite.
- All added functions and methods have docstrings.

## Environment limitations

The workspace validates SQLite functionality and HTTP contracts. A live PostgreSQL service
is not provided here. Ruff and mypy may need to be run in your own project virtual
environment if unavailable in the artifact-build environment. Do not mark those checks
successful until they actually run.

## Publication gate — **not** passed

This stage does **not** approve public-facing eligibility advice. Full content and license
reviews, freshness monitoring, detailed rules and evidence retrieval remain future stages.

## Observed results in the artifact workspace

- `python -m pytest -q` from root and backend: **43 tests passed** each.
- AST documentation audit: **88 functions checked, 0 missing docstrings**.
- Manual line-length audit on the new/changed Python files: no lines over 100 characters.
- Local SQLite Alembic upgrade completed; CLI dry run reported 20/21 and no write.
- First explicit import created 20 schemes and 21 sources; second created 0/0.
- Live Uvicorn HTTP checks: health 200, scheme list 200 (20 records),
  education filter 200 (3 records), scheme detail 200 (unknown/not publish-ready),
  source detail 200 (identity-only), active filter 200 (empty).
- Ruff, mypy and real PostgreSQL were **not executed** in this environment.

## Cross-platform timezone dependency fix

`tzdata` is declared in `backend/pyproject.toml`, rather than relying on the host OS
to provide IANA timezone records. `tests/test_timezones.py` exercises the
`Asia/Kolkata` lookup with `PYTHONTZPATH` empty, matching the behavior of a machine
without a system timezone database (including many Windows installations).
Install the updated project dependencies before running the test gate.
