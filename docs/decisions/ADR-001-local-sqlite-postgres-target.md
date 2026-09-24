# ADR-001 — Local SQLite gate with PostgreSQL target

**Status:** Accepted for Stage 1.

**Decision:** Use SQLAlchemy models and an explicit Alembic migration. Make local SQLite the
default so the first domain gate runs without Docker or database administration. Keep a
PostgreSQL URL/driver option for the planned structured-data service.

**Rationale:** Every entity and endpoint can be tested today. SQLite tests enable foreign-key
checks and use a real migration rather than mock repositories.

**Trade-off:** SQLite success does not establish PostgreSQL type/index/migration correctness.
A real PostgreSQL integration test must be run before relying on its deployment path.
No eligibility/RAG/agent functionality is introduced by this decision.
