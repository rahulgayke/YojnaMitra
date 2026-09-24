# Stage 1 — Domain model contract

This stage introduces the **structure**, not verified government-scheme facts. Stage 2 will
populate official records. The Stage 8 deterministic eligibility engine will interpret
rules; it is **not** implemented here.

## Entity boundaries

```text
Scheme [slug, jurisdiction, unknown/active/paused/closed status]
├── Source [UUID, type/tier/authority, is_official=false by default]
│   └── Document [UUID, version, hash, effective dates, unverified by default]
│       └── Chunk [UUID, text, heading path, source pages]
└── EligibilityRule [UUID, group ALL/ANY or typed condition; optional parent/source]

UserProfile [anonymous UUID session; only eligibility attributes]
```

`scheme_id` is a stable slug; the other entity IDs are UUIDs. `metadata` is stored as a JSON
column using `extra_metadata` in the ORM, since SQLAlchemy reserves `metadata`.

### Safeguards already enforced

- Pydantic rejects extra fields in every domain payload, especially unrequested sensitive
  fields in `UserProfileCreate`; a user and a separate beneficiary can have different ages.
- Central schemes cannot specify a state code; State/UT schemes require one.
- Schemes default to `unknown`, sources to nonofficial, rules to not machine verified,
  documents to unverified. These states require later source evidence to change.
- Rule group/condition shapes, page/effective-date ranges, hashes and authority score are
  validated. Foreign keys and key constraints are also enforced by the database.
- `Scheme → Source → Document → Chunk` and `Scheme → EligibilityRule` are separate from the
  anonymous `UserProfile` table. A chunk retains document/section/page linkage for citations.

### Intentional Stage 1 limits

No API accepts new government-scheme facts yet. Future ingestion must check scheme/source
ownership, parent-rule consistency, source authority, history/version validity, and official
URLs before setting trusted states. No source or rule is treated as verified merely because
it was stored. No full Aadhaar number, PAN, bank credential, OTP or password is modeled.

The local default is SQLite for a test gate without a service dependency. The same SQLAlchemy
model/migration supports PostgreSQL via `postgresql+psycopg://...`; an actual PostgreSQL
integration gate remains pending until a server is available. SQLite tests are not claimed
to prove PostgreSQL migration behavior.
