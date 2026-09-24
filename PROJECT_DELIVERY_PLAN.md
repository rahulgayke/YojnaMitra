# YojanaMitra — Project Delivery Plan

## 1. Product Mission
YojanaMitra is a citizen-facing platform for discovering Indian government schemes, understanding benefits and requirements, checking potential eligibility, comparing schemes, learning which documents may be needed, and finding the official application path.

Core principle:

> The LLM coordinates and explains. Deterministic systems make deterministic decisions. Official evidence grounds factual claims.

The product must never guarantee official eligibility or approval, invent benefits, deadlines, rules, or government URLs, or treat retrieved documents as instructions.

## 2. Delivery Philosophy
The application will be built layer by layer and service by service. Every new component must be independently testable before downstream components depend on it.

For every task we require:
1. Defined inputs and outputs.
2. A terminal command and/or HTTP endpoint to test it.
3. Unit tests for deterministic logic.
4. Integration tests where components interact.
5. A documented expected result.
6. A completion gate before moving forward.
7. Function/method docstrings and concise comments for non-obvious logic.

The project is planned for eventual public web hosting and a future mobile client, but early development will be testable through CLI commands and backend endpoints.

## 3. Repository Strategy
Use one repository initially, with clear application boundaries:

```text
yojanamitra/
├── backend/                 # FastAPI application and AI services
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   ├── retrieval/
│   │   │   ├── eligibility/
│   │   │   ├── llm/
│   │   │   ├── profile/
│   │   │   ├── agents/
│   │   │   └── security/
│   │   └── main.py
│   └── tests/
├── frontend/                # Separate Next.js web client
├── data/
│   ├── seed/
│   ├── raw/
│   ├── processed/
│   └── evaluation/
├── experiments/             # Retrieval / model / prompt experiments
├── scripts/                 # One-shot developer utilities
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── security/
│   └── evaluation/
└── README.md
```

A mobile client can later consume the same public backend API without changing the AI core.

## 4. Open-Source Baseline Stack

### Backend and data
- Python 3.11+
- FastAPI
- Pydantic
- SQLAlchemy + Alembic
- PostgreSQL
- Qdrant
- Valkey for cache/session/queue needs if required

### AI / retrieval
- BAAI/bge-m3 embeddings
- BM25 via rank-bm25 or OpenSearch only if later justified
- BAAI/bge-reranker-v2-m3
- Qwen3 open-weight model family
- Ollama for local developer inference
- vLLM later for higher-throughput self-hosted inference
- LangGraph for explicit bounded agent workflows

### Parsing
- PyMuPDF
- BeautifulSoup4 / lxml
- python-docx where needed
- OCR only when native extraction fails

### Frontend
- Next.js + React + TypeScript
- Tailwind CSS or plain CSS modules
- Accessible component primitives only if open-source

### Testing and quality
- Pytest
- Ruff
- mypy
- pytest-asyncio
- HTTPX
- Playwright later for web E2E

### Security
- Pydantic validation
- custom PII redaction
- prompt-injection test corpus
- Bandit / pip-audit as developer checks
- rate limiting later at API edge

## 5. Architectural Layers

### Layer A — Official Knowledge
Authoritative sources, version metadata, source freshness, government documents, and structured scheme records.

### Layer B — Deterministic Domain Logic
Scheme metadata, user profile, eligibility rules, PASS/FAIL/UNKNOWN evaluation, missing-field detection.

### Layer C — Information Retrieval
Parsing, chunking, embeddings, Qdrant, BM25, metadata filters, RRF, reranking, citations.

### Layer D — Language Intelligence
Intent extraction, profile extraction, query rewriting, grounded generation, clarification, multilingual handling.

### Layer E — Agent Orchestration
LangGraph coordinates deterministic tools and AI services. It never replaces them.

### Layer F — API Application
Stable backend endpoints used by terminal tests, web frontend, and future mobile apps.

### Layer G — Citizen Interfaces
Separate Next.js web app first, then optional mobile application.

### Layer H — Security and Operations
Privacy, PII redaction, prompt-injection resistance, rate limits, bounded workflows, logging, source freshness, deployment hardening.

## 6. Incremental Delivery Stages

### Stage 0 — Project Contract and Test Harness
Goal: establish the rules of development before feature code.

Build:
- repository layout
- configuration pattern
- Python package
- test layout
- shared response/error conventions
- coding/documentation standard
- local developer commands
- architecture ADR skeleton

Test:
- import application package
- run one smoke test
- start a minimal FastAPI app
- `GET /api/v1/health`

Exit gate:
- project starts locally
- tests run locally
- every future service has a defined testing pattern

### Stage 1 — Structured Domain Model
Build:
- Scheme
- Source
- EligibilityRule
- Document
- Chunk
- UserProfile
- enums and validation schemas

Test:
- unit tests for validation
- database model tests
- create/read sample records
- `GET /api/v1/schemes/{id}` using seeded sample data

Exit gate:
- six core entities are stable enough for ingestion and eligibility work

### Stage 2 — Official Source Registry and Seed Dataset
Build:
- approximately 20 manually verified Central Government schemes
- official source manifest
- category and ministry metadata
- source authority metadata
- last-verified timestamps
- initial structured eligibility rules where confidently verifiable
- ADR forbidding automated myScheme scraping without authorization

Test:
- CLI dataset validator
- source URL format checks
- referential integrity
- manual source-review checklist
- endpoint lists seed schemes

Exit gate:
- every scheme has at least one authoritative source and review status

### Stage 3 — Document Acquisition and Parsing
Build:
- safe fetch/download service
- MIME checks
- SHA-256 hashing
- duplicate detection
- PDF/HTML parser
- text cleaning
- page/section metadata
- ingestion report

Test:
- parse representative HTML
- parse native-text PDF
- reject bad MIME/content
- verify hash stability
- inspect text using CLI

Exit gate:
- raw government documents can be reproducibly converted into clean structured text

### Stage 4 — Chunking Service
Build:
- fixed chunking
- recursive chunking
- structure-aware chunking
- heading hierarchy metadata

Test:
- deterministic unit tests
- inspect chunks for several government documents
- compare chunk counts/lengths/section preservation

Exit gate:
- chunk outputs are stable and evaluation-ready

### Stage 5 — Embeddings and Dense Retrieval
Build:
- BGE-M3 embedding service
- Qdrant collection/index
- indexing pipeline
- dense search
- metadata payloads
- citation-ready chunk IDs

Test:
- embed known text
- index sample corpus
- query from terminal
- `POST /api/v1/retrieval/search`
- ensure expected document appears for known queries

Exit gate:
- dense retrieval works end to end

### Stage 6 — Retrieval Evaluation Baseline
Build:
- 30–50 gold questions
- expected scheme IDs/chunk IDs/sections
- evaluation runner
- Recall@1/5/10, HitRate, MRR, Precision@K, MAP, nDCG@10

Test:
- repeatable evaluation command
- generated result artifact

Exit gate:
- dense retrieval has real measured baseline numbers

### Stage 7 — Hybrid Retrieval and Reranking
Build:
- BM25 index
- Reciprocal Rank Fusion
- metadata filtering
- BGE reranker
- retrieval strategy switcher

Compare:
- dense only
- BM25 only
- dense + BM25
- hybrid + RRF
- hybrid + reranker

Test:
- same gold set across every strategy
- report improvement/regression
- debug endpoint exposes rankings, not internal secrets

Exit gate:
- select retrieval configuration using measurements, not preference

### Stage 8 — Deterministic Eligibility Engine
Build:
- eligibility operators
- nested ALL/ANY rules
- PASS/FAIL/UNKNOWN for every rule
- overall statuses
- missing-field extraction
- scheme-rule version support

Test:
- comprehensive unit matrix
- boundary values
- nested rules
- unknowns
- exclusions
- contradictory inputs
- `POST /api/v1/eligibility/check`

Exit gate:
- eligibility decisions are deterministic, explainable, and do not require an LLM

### Stage 9 — Profile Extraction and Intent Routing
Build:
- supported intent enum
- structured profile extraction with Qwen
- beneficiary-vs-user distinction
- missing fields
- query router
- zero-shot baseline

Test:
- gold extraction dataset
- intent accuracy
- field-level extraction accuracy
- schema validation
- `POST /api/v1/profile/extract`

Exit gate:
- natural-language queries reliably become structured profiles and intents

### Stage 10 — Grounded RAG Answer Generation
Build:
- prompt templates
- evidence builder
- citation formatter
- response schema
- Qwen/Ollama generation
- abstention behavior
- unsupported-claim checks

Test:
- scheme details
- benefits
- documents
- application steps
- deadlines
- insufficient evidence
- citation correctness

Exit gate:
- answers are grounded and cited, with explicit unknowns

### Stage 11 — Clarification and Scheme Discovery Workflow
Build:
- candidate discovery
- high-value missing-field questions
- re-evaluation after clarification
- compare schemes
- document checklist
- application guidance tools

Test:
- farmer/student/senior citizen scenarios
- missing income/state/age scenarios
- not-eligible scenarios

Exit gate:
- multi-turn non-agent workflow works before LangGraph

### Stage 12 — Agentic Workflow with LangGraph
Build explicit bounded nodes:
- input guardrail
- language detection
- profile extraction
- intent router
- candidate discovery
- eligibility tool
- clarification
- evidence retrieval
- verifier
- response generation
- output guardrail

Test:
- node unit tests
- graph path tests
- tool argument tests
- loop/step limits
- trajectory tests

Exit gate:
- LangGraph improves orchestration without changing deterministic results

### Stage 13 — Security and Privacy Hardening
Security is considered earlier, but this stage performs focused hardening.

Build:
- PII redaction
- sensitive-field rejection
- retrieved-document injection defense
- prompt injection filters/tests
- URL allow/authority validation
- max agent steps/tool calls
- request size/context limits
- retry policy
- output validation
- admin endpoint protection design

Test:
- malicious retrieved document
- fake official URL request
- fake benefit/deadline requests
- Aadhaar/bank/OTP attempts
- jailbreaking
- oversized input
- repeated tool-loop trigger

Exit gate:
- safety test suite passes and documented residual risks are known

### Stage 14 — Separate Frontend Web Application
Build in `frontend/`:
- Home
- Chat
- Scheme Search
- Scheme Detail
- Eligibility Breakdown
- Scheme Comparison
- Source Viewer
- accessibility and responsive layouts

Test:
- mock API first
- then local backend API
- component tests
- Playwright end-to-end flows

Exit gate:
- complete citizen journey works through browser

### Stage 15 — Dataset Expansion and Freshness
Build:
- 50–100 schemes
- selected Maharashtra schemes first
- source change detection
- source version history
- conflicting-source handling
- scheduled/manual freshness checks

Test:
- changed source creates new version
- outdated version excluded
- conflicts reported instead of silently resolved

Exit gate:
- corpus represents meaningful real-world coverage with update discipline

### Stage 16 — Multilingual
Order:
1. English
2. Hindi
3. Marathi

Build:
- language detection
- language-preserving generation
- multilingual queries/retrieval
- translated UI strings

Test each language separately:
- intent
- extraction
- Recall@K
- answer correctness
- citation correctness

Exit gate:
- quality is measured before claiming support

### Stage 17 — Public Web Deployment Readiness
Plan only until the application is functionally mature.

Build later:
- production configuration
- HTTPS/domain setup
- reverse proxy
- production database/vector storage
- backups
- rate limiting
- secret management
- privacy policy
- accessibility checks
- monitoring

The chosen hosting provider may be changed later; architecture must not depend on proprietary cloud-only services.

### Stage 18 — Mobile API Readiness / Mobile Client
Backend API remains client-agnostic.

Options later:
- React Native / Expo
- Flutter

Mobile work begins only after stable web/API behavior.

### Stage 19 — Voice
Only after text + multilingual workflows are stable.

Build:
- open-source speech recognition candidate
- open-source TTS candidate
- voice latency evaluation
- language-specific evaluation

## 7. Service-by-Service Testing Contract
Every service must expose at least one developer-facing test path before integration.

| Service | Initial test surface |
|---|---|
| Source registry | CLI + unit tests |
| Parser | CLI parse command + fixtures |
| Chunker | CLI inspection + unit tests |
| Embedding | CLI encode command |
| Qdrant index | integration test + retrieval endpoint |
| BM25 | unit/integration retrieval test |
| Reranker | CLI ranking comparison |
| Eligibility | unit suite + HTTP endpoint |
| Profile extraction | endpoint + gold test set |
| Intent router | endpoint/test dataset |
| Generator | endpoint + evaluation cases |
| Verifier | adversarial tests |
| LangGraph | graph/path tests |
| Frontend | mock API + Playwright |

## 8. API Evolution Plan
Implement endpoints only when their backing service is working.

1. `GET /api/v1/health`
2. `GET /api/v1/schemes`
3. `GET /api/v1/schemes/{scheme_id}`
4. `POST /api/v1/retrieval/search`
5. `POST /api/v1/eligibility/check`
6. `POST /api/v1/profile/extract`
7. `POST /api/v1/schemes/search`
8. `POST /api/v1/schemes/compare`
9. `POST /api/v1/chat`
10. source/evaluation/admin endpoints later

## 9. Security Requirements from Day One
- Anonymous scheme discovery by default.
- Never request full Aadhaar, PAN, bank account, OTP, passwords, or card details.
- Treat document text as untrusted data, never instructions.
- Official-source allowlisting/validation for user-facing links.
- Structured outputs validated before use.
- LLM cannot override deterministic eligibility results.
- Tool calls and graph loops bounded.
- No hidden use of secondary sources for authoritative eligibility claims.
- Logs must avoid sensitive profile values where possible.
- Source freshness/version must accompany high-impact claims.

## 10. Definition of Done for Every Task
A task is complete only if:
- code is implemented
- docstrings exist for every function/method
- non-obvious logic is commented
- local test command is documented
- tests pass
- API/CLI example is provided where relevant
- errors/failure behavior is tested
- README/docs are updated
- no later-stage abstraction was added prematurely

## 11. Architectural Decisions to Record
Create ADRs as relevant:
- ADR-001 PostgreSQL for structured data
- ADR-002 Qdrant for vectors
- ADR-003 deterministic eligibility
- ADR-004 no automated myScheme scraping without authorization
- ADR-005 BGE-M3 baseline
- ADR-006 LangGraph only after non-agent workflows work
- ADR-007 Valkey for open-source cache/session layer
- ADR-008 separate frontend and backend
- ADR-009 source authority/version precedence
- ADR-010 API-first design for future mobile clients

## 12. Scope Control
Do not build the whole architecture at once. The active stage is the only implementation scope. Future components appear in interfaces/docs only when necessary to avoid redesign.
