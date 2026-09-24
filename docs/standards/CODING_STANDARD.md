# Coding and Testing Standard

## Documentation

- Every Python function and method must contain a useful docstring explaining its responsibility.
- Public classes and modules should have concise docstrings.
- Comments should explain non-obvious reasoning, constraints, security choices, or trade-offs.
- Avoid comments that merely translate the next line of code into English.

## Service boundaries

- Prefer small services with one clear responsibility.
- Do not place AI, persistence, retrieval, eligibility, and HTTP concerns in one module.
- Define typed input/output contracts before integration.

## Testing rule

Every code addition must provide the cheapest useful test at the same time:

- pure function -> unit test
- parser/chunker -> fixture + deterministic output test
- service integration -> integration test
- HTTP contract -> endpoint test
- end-to-end workflow -> scenario test
- retrieval/model change -> evaluation benchmark where relevant

A later layer must not be integrated until the current layer's acceptance gate passes.

## Security rule

Security is incremental rather than postponed. Each stage must consider:

- input validation
- sensitive-data minimization
- untrusted retrieved/document content
- safe logging
- bounded external/model calls
- authoritative-source grounding
- failure/abstention behavior

Dedicated hardening and adversarial testing will still occur in the security stage.
