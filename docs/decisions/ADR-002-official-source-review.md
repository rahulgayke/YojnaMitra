# ADR-002 — Separate registry verification from substantive scheme verification

**Status:** Accepted in Stage 2.

## Context

Finding a page on a government domain verifies neither current scheme status nor the
completeness of eligibility rules. Source pages can be outdated, withdrawn, region-specific,
or subject to license restrictions.

## Decision

- Record 20 seed scheme identities and 21 source links with a review method and date.
- Keep every `Scheme.status` as `unknown` and `Scheme.last_verified_at` as null.
- `Source.last_verified_at` stores only the *calendar day* when the link/identity was reviewed,
  normalized to midnight IST. Metadata explicitly states `timestamp_precision` and
  `verification_scope=government_source_identity_only`.
- Preserve the distinction between `page_read`, `search_result_review`, and
  `official_portal_reference` (a link established via another official page).
- `content_review_status=not_parsed`, `publish_ready=false`, and
  `eligibility_rule_coverage=not_reviewed` are explicit for every record.
- No `EligibilityRule`, `Document` or `Chunk` rows are fabricated in this stage. Stage 3 must
  review source permissions and provenance before acquisition; Stage 8 must review
  complete, versioned rules before machine evaluation.
- Registry imports are offline, validation-first, transactional, deterministic and
  conflict-rejecting; records are never silently overwritten.

## Trade-offs

Citizen-facing scheme lists can display identities and links but cannot yet establish
eligibility, amount, deadline, active status or application requirements. This is intentional:
an incorrect statement about government benefits is costlier than an explicit unknown.
