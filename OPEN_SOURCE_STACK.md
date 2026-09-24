# YojanaMitra — Open-Source Stack Policy

The project should not depend on a paid proprietary model or managed service for core functionality during development.

## Baseline choices

| Capability | Default |
|---|---|
| Backend API | FastAPI |
| Validation | Pydantic |
| Structured DB | PostgreSQL |
| ORM/migrations | SQLAlchemy + Alembic |
| Vector DB | Qdrant |
| Cache/session/queue if required | Valkey |
| Embeddings | BAAI/bge-m3 |
| Reranker | BAAI/bge-reranker-v2-m3 |
| LLM | Qwen3-8B initially; larger Qwen variant if hardware permits |
| Local serving | Ollama |
| Advanced serving | vLLM |
| Agent orchestration | LangGraph Python library |
| PDF parsing | PyMuPDF |
| HTML parsing | BeautifulSoup4 + lxml |
| Frontend | Next.js + React + TypeScript |
| Unit/integration tests | Pytest |
| Browser E2E | Playwright |
| Lint/type checking | Ruff + mypy |

## Important policy
Do not adopt a package/model because it is popular. Before adding a core dependency:
1. verify license,
2. verify maintenance status,
3. verify it can run without a paid hosted service,
4. record the reason in an ADR if architectural.

LangGraph refers to the open-source Python library, not paid LangGraph Platform features.
