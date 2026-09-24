# Backend — Stage 2

Run the backend from this directory after `python -m pip install -e ".[dev]"`.

The Stage 2 registry is in `../data/seed/central_schemes.json` and imports **offline**.

```powershell
python -m pytest tests/test_seed_registry.py -q
python -m pytest -q
python -m alembic upgrade head
python -m yojanamitra.cli validate-seed
python -m yojanamitra.cli seed-registry        # dry run
python -m yojanamitra.cli seed-registry --apply # explicit local insert
python -m uvicorn yojanamitra.main:app --reload
```

`/api/v1/schemes` lists reviewed identities, not confirmed active schemes. Source records
expose review method/date and do not assert substantive scheme facts. Do not scrape myScheme.
