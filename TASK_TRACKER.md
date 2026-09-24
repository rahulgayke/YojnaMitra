# YojanaMitra — Task Tracker

Status legend: `[ ] Not started` · `[-] In progress` · `[x] Complete` · `[!] Blocked`

## Stage 0 — Project Contract and Test Harness
- [x] Create clean repository structure
- [x] Create backend Python project
- [x] Create separate frontend directory placeholder
- [x] Add environment/config pattern
- [x] Add minimal FastAPI application
- [x] Add `/api/v1/health`
- [x] Add Pytest smoke test
- [x] Add coding/docstring standard
- [x] Add local test commands to README
- [x] Create ADR directory
- [x] Verify local startup and test command
- [x] Verify both root and backend Pytest entry points
- [x] Add package source-resolution regression test

**Stage 0 gate:** ✅ app imports, health endpoint responds, and the Stage 0 test suite passes.

## Stage 1 — Structured Domain Model
- [x] Implement Scheme model/schema
- [x] Implement Source model/schema
- [x] Implement EligibilityRule model/schema
- [x] Implement Document model/schema
- [x] Implement Chunk model/schema
- [x] Implement UserProfile model/schema
- [x] Define enums and validation constraints
- [x] Add explicit Alembic database migration
- [x] Add model validation tests
- [x] Add SQLite create/read integration test
- [x] Add sample scheme detail endpoint
- [x] Add safe, idempotent synthetic demo seeder
- [x] Preserve Stage 0 regression tests and enforce function/method docstrings
- [ ] Run optional live PostgreSQL migration test (server unavailable in this workspace)
- [ ] Run Ruff and mypy in developer environment (not downloadable in this workspace)

**Stage 1 functional gate:** ✅ all local SQLite, schema, CLI and API tests pass.
PostgreSQL and static-analysis gates remain explicitly pending; run the documented quality
commands before committing and report any failures rather than assuming they passed.

## Stage 2 — Official Source Registry and Seed Dataset
- [x] Select 20 Central Government scheme identities
- [x] Review 21 source identities on official government/authority sites
- [x] Record ministry/category/beneficiary metadata (identity scope only)
- [x] Record registry review calendar date and method per source
- [x] Record source authority/type/tier and provenance scope
- [x] Add no partial rules that could be mistaken for full verified eligibility
- [x] Add conflict-rejecting and idempotent seed loader (explicit `--apply`)
- [x] Add offline dataset and URL validator
- [x] Add ADR-004 no myScheme scraping
- [x] Review every seed record's identity/source and document review method
- [x] Add list/filter and source lookup endpoints
- [x] Add endpoint, CLI and rollback regression tests
- [ ] Stage 3: verify document permissions, current content, rules, deadlines and status
- [ ] Local gate: run Ruff, mypy and live PostgreSQL before merging if required

**Stage 2 gate:** all 20 records have at least one identified primary official source,
explicit verification scope/date, status=unknown and publish_ready=false. The offline
validator, idempotent/atomic importer and read-only endpoints are tested. This does
**not** certify that complete scheme facts or public eligibility advice are ready.

## Stage 3 — Document Acquisition and Parsing
- [ ] Implement source download/fetch function
- [ ] Add MIME validation
- [ ] Add SHA-256 checksum
- [ ] Add duplicate detection
- [ ] Implement PDF parser
- [ ] Implement HTML parser
- [ ] Implement text cleaning
- [ ] Preserve pages/headings/sections
- [ ] Add ingestion report
- [ ] Add parser fixtures/tests
- [ ] Add CLI parse/inspect command

**Stage 3 gate:** official documents parse reproducibly into clean structured text.

## Stage 4 — Chunking
- [ ] Implement fixed chunking
- [ ] Implement recursive chunking
- [ ] Implement structure-aware chunking
- [ ] Preserve heading hierarchy
- [ ] Preserve source/page metadata
- [ ] Add deterministic chunking tests
- [ ] Add chunk inspection CLI
- [ ] Record baseline chunk statistics

**Stage 4 gate:** three chunking strategies produce stable inspectable outputs.

## Stage 5 — BGE-M3 Dense Retrieval
- [ ] Add embedding model wrapper
- [ ] Add batch embedding
- [ ] Add Qdrant collection setup
- [ ] Add chunk indexing
- [ ] Add metadata payloads
- [ ] Add dense search service
- [ ] Add retrieval endpoint
- [ ] Add integration test
- [ ] Run known-query smoke tests

**Stage 5 gate:** user query returns relevant cited chunks from Qdrant.

## Stage 6 — Retrieval Evaluation Baseline
- [ ] Create 30–50 gold questions
- [ ] Map expected scheme IDs
- [ ] Map expected chunk IDs/sections
- [ ] Implement Recall@K
- [ ] Implement Precision@K
- [ ] Implement HitRate@K
- [ ] Implement MRR
- [ ] Implement MAP
- [ ] Implement nDCG@10
- [ ] Add repeatable evaluation runner
- [ ] Save baseline result artifact

**Stage 6 gate:** dense baseline measured and reproducible.

## Stage 7 — Hybrid Retrieval and Reranking
- [ ] Add BM25 index
- [ ] Add sparse retrieval
- [ ] Add RRF
- [ ] Add metadata filtering
- [ ] Add BGE reranker
- [ ] Add retrieval strategy selector
- [ ] Compare dense-only
- [ ] Compare BM25-only
- [ ] Compare hybrid
- [ ] Compare RRF
- [ ] Compare hybrid + reranker
- [ ] Publish actual metrics

**Stage 7 gate:** best retrieval stack chosen from measured evidence.

## Stage 8 — Deterministic Eligibility
- [ ] Define rule operators
- [ ] Implement PASS/FAIL/UNKNOWN
- [ ] Implement nested ALL/ANY
- [ ] Implement missing-field detection
- [ ] Implement overall statuses
- [ ] Implement exclusions
- [ ] Add rule-version awareness
- [ ] Add exhaustive unit tests
- [ ] Add eligibility endpoint

**Stage 8 gate:** deterministic rules work independently of LLMs.

## Stage 9 — Profile Extraction and Intent
- [ ] Define supported intents
- [ ] Implement Qwen model adapter
- [ ] Implement structured profile extraction
- [ ] Distinguish user vs beneficiary
- [ ] Extract missing fields
- [ ] Implement intent router
- [ ] Build extraction gold set
- [ ] Measure zero-shot accuracy
- [ ] Add profile extraction endpoint

**Stage 9 gate:** queries reliably become validated profiles and intents.

## Stage 10 — Grounded RAG Generation
- [ ] Create prompt/version directory
- [ ] Implement evidence builder
- [ ] Implement citation formatter
- [ ] Implement response schema
- [ ] Implement Qwen/Ollama generator
- [ ] Add abstention behavior
- [ ] Add unsupported-claim checks
- [ ] Test benefits/documents/application/deadline queries
- [ ] Measure citation correctness

**Stage 10 gate:** grounded responses contain correct citations and explicit uncertainty.

## Stage 11 — Discovery and Clarification Workflow
- [ ] Implement candidate scheme discovery
- [ ] Implement missing eligibility field ranking
- [ ] Implement clarification question generation
- [ ] Re-evaluate after clarification
- [ ] Implement scheme comparison
- [ ] Implement document checklist
- [ ] Implement application guidance
- [ ] Add scenario tests

**Stage 11 gate:** multi-turn workflow works without agents.

## Stage 12 — LangGraph Agentic Workflow
- [ ] Create graph state
- [ ] Add input guardrail node
- [ ] Add language node
- [ ] Add profile node
- [ ] Add intent router node
- [ ] Add discovery node
- [ ] Add eligibility node
- [ ] Add clarification node
- [ ] Add retrieval/evidence node
- [ ] Add verifier node
- [ ] Add final response node
- [ ] Add output guardrail node
- [ ] Add max-step/loop limits
- [ ] Add graph path tests
- [ ] Add tool selection/argument tests

**Stage 12 gate:** bounded graph reproduces or improves non-agent workflow behavior.

## Stage 13 — Security and Privacy Hardening
- [ ] PII pattern redaction
- [ ] Reject sensitive profile fields
- [ ] Retrieved-document prompt injection defense
- [ ] Prompt injection test corpus
- [ ] Official URL validation
- [ ] Request/context size limits
- [ ] Tool call limits
- [ ] Retry limits
- [ ] Output schema validation
- [ ] Admin protection design
- [ ] Add malicious-document test
- [ ] Add fake-benefit/deadline/URL tests
- [ ] Add sensitive-data tests

**Stage 13 gate:** safety suite passes with documented residual risk.

## Stage 14 — Separate Web Frontend
- [ ] Initialize Next.js + TypeScript app
- [ ] Build API client layer
- [ ] Home page
- [ ] Chat page
- [ ] Scheme search
- [ ] Scheme detail
- [ ] Eligibility breakdown
- [ ] Compare schemes
- [ ] Source viewer
- [ ] Responsive design
- [ ] Accessibility checks
- [ ] Mock API tests
- [ ] Backend integration
- [ ] Playwright E2E tests

**Stage 14 gate:** complete citizen workflow works in browser.

## Stage 15 — Dataset Expansion and Freshness
- [ ] Expand to 50 schemes
- [ ] Expand toward 100 schemes
- [ ] Add Maharashtra state schemes
- [ ] Implement source hash comparison
- [ ] Implement source/document versioning
- [ ] Add effective-date filters
- [ ] Add conflict detection
- [ ] Add stale-source handling
- [ ] Add refresh workflow

**Stage 15 gate:** data changes are tracked and stale rules cannot masquerade as current.

## Stage 16 — Multilingual
- [ ] English baseline complete
- [ ] Hindi profile/intent test set
- [ ] Hindi retrieval evaluation
- [ ] Hindi answer evaluation
- [ ] Marathi profile/intent test set
- [ ] Marathi retrieval evaluation
- [ ] Marathi answer evaluation
- [ ] UI translation framework
- [ ] Language preservation tests

**Stage 16 gate:** each claimed language independently meets documented metrics.

## Stage 17 — Web Deployment Readiness
- [ ] Domain/HTTPS architecture
- [ ] Reverse proxy plan
- [ ] production configuration
- [ ] secrets management
- [ ] rate limits
- [ ] backups
- [ ] privacy policy
- [ ] accessibility review
- [ ] monitoring plan
- [ ] deployment runbook

**Stage 17 gate:** public deployment can happen without changing application architecture.

## Stage 18 — Mobile Readiness
- [ ] Stabilize public API contracts
- [ ] Define mobile auth/session needs
- [ ] Select React Native/Expo or Flutter
- [ ] Build first mobile client only after web/API stability

## Stage 19 — Voice
- [ ] Select open-source STT candidate
- [ ] Select open-source TTS candidate
- [ ] English voice evaluation
- [ ] Hindi voice evaluation
- [ ] Marathi voice evaluation
- [ ] latency/usability evaluation

---

## Permanent Development Rules
- [ ] Every function/method has a docstring.
- [ ] Non-obvious logic has a concise comment.
- [ ] Each new service has unit tests before integration.
- [ ] Each new service has a CLI or endpoint test path.
- [ ] No LLM decides deterministic eligibility.
- [ ] No invented government data, URL, benefit, deadline, or rule.
- [ ] No automated myScheme scraping without authorization.
- [ ] No benchmark number is published unless measured.
- [ ] Current-source version/effective date is part of authoritative decisions.
- [ ] Security tests grow alongside features, not only at the end.
