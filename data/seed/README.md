# Stage 2 — reviewed registry, **not** a verified eligibility corpus

`central_schemes.json` contains 20 Central Government scheme identities and 21 source
references, reviewed on the date in each `sources[].reviewed_on` field.

The date means that the *identity of the linked government source* was checked; it does not
mean that complete content, live availability, current benefits, eligibility, application
links or deadlines were verified. Read the per-source `verification_method`:

- `page_read`: a relevant official landing page was opened and read.
- `search_result_review`: an official result/heading was inspected, but direct source
  acquisition and document parsing were **not** performed.
- `official_portal_reference`: an official portal link was established through an official
  reference but content was not read.

The database stores the review day on the source record as *midnight IST* with
`timestamp_precision=calendar_day_ist`; it is **not** the exact time of review.

Every scheme has `status=unknown`, `last_verified_at=null`, `publish_ready=false`,
`eligibility_rule_coverage=not_reviewed`, and no machine-verified rule. This seed dataset is
for discovery engineering, not for public eligibility decisions.

An identified official source is not necessarily licensed for bulk copying. The
PM SVANidhi portal is marked `do_not_copy_or_ingest_without_permission_review` because its
published disclaimer restricts reproduction. Stage 3 must review access and licensing for
**all** sources before downloading or indexing content. Do not scrape myScheme.

Review this manifest before every public release; never update review dates automatically
without a real review. See `docs/decisions/ADR-004-no-myscheme-scraping.md`.
