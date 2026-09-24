# Stage 0 Acceptance Report

Stage 0 establishes the project contract and local test harness. It deliberately does not implement any domain, persistence, retrieval, LLM, or agent behavior.

## Acceptance checks

- [x] Backend package imports after editable installation.
- [x] FastAPI application factory creates an application.
- [x] `GET /api/v1/health` returns HTTP 200.
- [x] Health response matches the documented contract.
- [x] Environment-driven settings have safe local defaults.
- [x] Python function/method docstring policy is enforced by a test.
- [x] Uvicorn starts with the documented command.
- [x] Health endpoint succeeds over a real local HTTP socket.
- [x] Python sources compile successfully.
- [x] `pyproject.toml` parses successfully.
- [x] Tests pass from both the repository root and `backend/`.
- [x] Source-resolution regression test detects an older imported checkout.

## Verified result

The corrected Stage 0 Pytest suite contains six tests. It must pass both from
the repository root and `backend/`, including with an older package on `PYTHONPATH`.

Manual runtime response:

```json
{
  "status": "ok",
  "service": "yojanamitra-api",
  "environment": "local",
  "api_version": "v1"
}
```

## Local commands

From `backend/`:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m uvicorn yojanamitra.main:app --reload
```

Then, from another terminal:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## Exit gate

**PASS.** Stage 1 may begin only after the same commands pass in the developer's local environment.
