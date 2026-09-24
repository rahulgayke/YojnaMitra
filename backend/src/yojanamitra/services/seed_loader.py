"""Import the validated local registry without scraping or overwriting user data."""

from __future__ import annotations

import uuid
from datetime import datetime, time

from sqlalchemy.orm import Session

from yojanamitra.models import Scheme, Source
from yojanamitra.repositories.schemes import get_scheme_by_id
from yojanamitra.services.seed_registry import INDIA_TIMEZONE, SeedManifest

# Stable IDs make retries idempotent without depending on a separate migration.
SEED_NAMESPACE = uuid.UUID("606d7735-9478-42ca-a94c-d7f10bd08c39")


class SeedConflictError(ValueError):
    """Signal that an existing record differs from the curated seed manifest."""


def source_identifier(scheme_id: str, url: str) -> uuid.UUID:
    """Derive the same source UUID for every import of a given scheme and URL."""

    return uuid.uuid5(SEED_NAMESPACE, f"{scheme_id}:{url}")


def seed_registry(session: Session, manifest: SeedManifest) -> dict[str, int]:
    """Insert missing seed schemes/sources, rejecting conflicting existing records.

    The caller owns transaction commit or rollback. All validation is completed
    before invoking this function; it does not perform HTTP downloads.
    """

    counts = {"schemes_created": 0, "sources_created": 0, "unchanged_schemes": 0}
    for entry in manifest.entries:
        payload = entry.scheme
        existing = get_scheme_by_id(session, payload.id)
        if existing is None:
            session.add(
                Scheme(
                    **payload.model_dump(exclude={"metadata"}),
                    extra_metadata=payload.metadata,
                )
            )
            session.flush()
            counts["schemes_created"] += 1
        else:
            # No overwrite: curated seed changes need an explicit version/review workflow.
            if (
                existing.name != payload.name
                or existing.category != payload.category
                or existing.scope != payload.scope
                or existing.status != payload.status
                or existing.extra_metadata != payload.metadata
                or existing.ministry != payload.ministry
                or existing.short_name != payload.short_name
            ):
                raise SeedConflictError(f"Existing scheme differs from reviewed seed: {payload.id}")
            counts["unchanged_schemes"] += 1
        for source_record in entry.sources:
            source_id = source_identifier(payload.id, source_record.url)
            # The verification timestamp has *day* precision, not event precision.
            review_time = datetime.combine(source_record.reviewed_on, time.min, INDIA_TIMEZONE)
            metadata = {
                "reviewed_on": source_record.reviewed_on.isoformat(),
                "verification_method": source_record.verification_method,
                "verification_scope": source_record.verification_scope,
                "content_review_status": source_record.content_review_status,
                "acquisition_policy": source_record.acquisition_policy,
                "timestamp_precision": "calendar_day_ist",
            }
            matching = session.get(Source, source_id)
            if matching is not None:
                if (
                    matching.scheme_id != payload.id
                    or matching.url != source_record.url
                    or matching.title != source_record.title
                    or matching.authority != source_record.authority
                    or matching.source_type != source_record.source_type
                    or matching.tier != source_record.tier
                    or matching.authority_score != source_record.authority_score
                    or matching.is_official != source_record.is_official
                    or matching.extra_metadata != metadata
                ):
                    raise SeedConflictError(
                        f"Existing source differs from reviewed seed: {source_id}"
                    )
                continue
            session.add(
                Source(
                    id=source_id,
                    scheme_id=payload.id,
                    title=source_record.title,
                    url=source_record.url,
                    authority=source_record.authority,
                    source_type=source_record.source_type,
                    tier=source_record.tier,
                    authority_score=source_record.authority_score,
                    is_official=source_record.is_official,
                    last_verified_at=review_time,
                    extra_metadata=metadata,
                )
            )
            counts["sources_created"] += 1
        session.flush()
    return counts
