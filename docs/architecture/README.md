# Architecture

YojanaMitra is delivered layer by layer. Every new service must have a stable contract and its own test path before another service depends on it.

## Planned logical layers

1. **Domain/data layer** — schemes, sources, documents, chunks, profiles, eligibility rules.
2. **Acquisition layer** — official source download, parsing, validation, versioning.
3. **Retrieval layer** — chunking, BGE embeddings, Qdrant, BM25, RRF, reranking.
4. **Decision layer** — deterministic eligibility evaluation.
5. **AI reasoning layer** — profile extraction, intent routing, grounded generation, verification.
6. **Orchestration layer** — bounded LangGraph workflows.
7. **API layer** — versioned FastAPI contracts for web/mobile/terminal clients.
8. **Interface layer** — separate Next.js web application and possible future mobile client.
9. **Security layer** — privacy, validation, prompt-injection resistance, output grounding, abuse controls.

## Stage 0 boundary

Only the API skeleton, configuration, shared response conventions, tests, and documentation exist. The absence of later services is deliberate.
