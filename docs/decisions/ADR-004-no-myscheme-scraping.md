# ADR-004 — Do not scrape myScheme

**Status:** Accepted in Stage 2.

## Context

YojanaMitra needs authoritative evidence about government schemes. myScheme is a useful
Government of India discovery portal, but the original implementation specification records
its restrictions on automated scraper/bot access without written authorization.

## Decision

- Do not implement an automated myScheme scraper, crawler, bulk fetcher or bypass.
- Do not use myScheme URLs as input to the automated Stage 2 seed loader.
- Curate metadata from the responsible ministry/department, scheme portals, official APIs,
  downloadable datasets and official government guidelines.
- Review copyright/access conditions and robots/terms **before** Stage 3 downloads;
  a government URL is not automatically permission to copy or republish its contents.
- If written authorization or an approved API is obtained later, document it in a new ADR.

## Trade-offs

Manual source review is slower and restricts initial coverage. It avoids building a data
pipeline whose principal access path may be unauthorized, and improves traceability to the
responsible authority. We preserve source provenance rather than accepting aggregated
summary claims as an independent ground truth.
