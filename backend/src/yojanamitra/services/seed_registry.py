"""Validate a human-curated official-source manifest without network access.

This service validates *source identity*, not live scheme status, eligibility,
benefit amounts, document copyrights, or the suitability of pages for ingestion.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from yojanamitra.models.enums import SchemeScope, SchemeStatus, SourceTier, SourceType
from yojanamitra.schemas.domain import SchemeCreate, SourceCreate

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SEED_PATH = PROJECT_ROOT / "data" / "seed" / "central_schemes.json"
INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")
# This non-gov.in authority hosts its own official regulator information.
EXPLICIT_OFFICIAL_HOSTS = frozenset({"pfrda.org.in", "www.pfrda.org.in"})
VerificationMethod = Literal["page_read", "search_result_review", "official_portal_reference"]
AcquisitionPolicy = Literal[
    "manual_review_required_before_download",
    "do_not_copy_or_ingest_without_permission_review",
]


class SeedSource(BaseModel):
    """Represent a reviewed registry link and its narrow verification claim."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=2, max_length=250)
    url: str = Field(min_length=12, max_length=2048)
    authority: str = Field(min_length=2, max_length=200)
    source_type: SourceType
    tier: SourceTier
    authority_score: int = Field(ge=0, le=100)
    is_official: bool
    reviewed_on: date
    verification_method: VerificationMethod
    verification_scope: Literal["government_source_identity_only"]
    content_review_status: Literal["not_parsed"]
    acquisition_policy: AcquisitionPolicy

    @model_validator(mode="after")
    def validate_official_url(self) -> SeedSource:
        """Reject unsafe and unapproved source URLs before the database is touched."""

        parts = urlsplit(self.url)
        host = (parts.hostname or "").lower()
        sanctioned = (
            host.endswith(".gov.in")
            or host.endswith(".nic.in")
            or host in EXPLICIT_OFFICIAL_HOSTS
        )
        if (
            parts.scheme != "https"
            or not sanctioned
            or parts.username is not None
            or parts.password is not None
            or parts.port is not None
            or parts.fragment
        ):
            raise ValueError("Source must be a plain HTTPS URL on an approved official host")
        if host == "myscheme.gov.in" or host.endswith(".myscheme.gov.in"):
            raise ValueError("myScheme is excluded from automated seed ingestion")
        if self.reviewed_on > datetime.now(INDIA_TIMEZONE).date():
            raise ValueError("Source registry review date must not be in the future")
        if not self.is_official:
            raise ValueError("Stage 2 seed must use identified official sources")
        # SourceCreate provides the identical typed constraints used by the API layer.
        SourceCreate.model_validate(
            {
                "scheme_id": "validation-only",
                "title": self.title,
                "url": self.url,
                "authority": self.authority,
                "source_type": self.source_type,
                "tier": self.tier,
                "authority_score": self.authority_score,
                "is_official": self.is_official,
            }
        )
        return self


class SeedEntry(BaseModel):
    """Represent one scheme, at least one official source, and no trusted rules."""

    model_config = ConfigDict(extra="forbid")

    scheme: SchemeCreate
    sources: list[SeedSource] = Field(min_length=1)
    eligibility_rules: list[dict[str, object]] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_incomplete_registry_scope(self) -> SeedEntry:
        """Prevent partially reviewed records being presented as operationally verified."""

        if self.scheme.scope != SchemeScope.CENTRAL or self.scheme.status != SchemeStatus.UNKNOWN:
            raise ValueError("Seed records must be central with unknown operating status")
        if self.scheme.last_verified_at is not None:
            raise ValueError("Scheme-wide verification is not completed in Stage 2")
        if self.scheme.metadata.get("publish_ready") is not False:
            raise ValueError("Unreviewed records cannot be marked publish-ready")
        if self.scheme.metadata.get("eligibility_rule_coverage") != "not_reviewed":
            raise ValueError("Eligibility rule coverage must be explicitly unreviewed")
        if (
            self.scheme.metadata.get("verification_scope")
            != "scheme_identity_and_source_registry_only"
        ):
            raise ValueError("Review scope must be stated explicitly")
        if self.eligibility_rules:
            raise ValueError("Do not seed incomplete eligibility rules as machine-verifiable")
        if not any(source.tier == SourceTier.PRIMARY for source in self.sources):
            raise ValueError("Every scheme requires a primary government source")
        return self


class SeedManifest(BaseModel):
    """Represent the entire checked manifest for atomic import."""

    model_config = ConfigDict(extra="forbid")
    entries: list[SeedEntry]

    @model_validator(mode="after")
    def check_unique_identity(self) -> SeedManifest:
        """Reject duplicate scheme IDs and repeated source URLs across the manifest."""

        identifiers = [entry.scheme.id for entry in self.entries]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Duplicate scheme ID in seed manifest")
        urls = [source.url for entry in self.entries for source in entry.sources]
        if len(set(urls)) != len(urls):
            raise ValueError("Duplicate official source URL in seed manifest")
        return self


def load_manifest(path: Path = DEFAULT_SEED_PATH) -> SeedManifest:
    """Load and validate local JSON completely before permitting database writes."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to load seed manifest: {path}") from exc
    try:
        return SeedManifest.model_validate({"entries": raw})
    except ValidationError as exc:
        raise ValueError(f"Invalid seed manifest: {exc}") from exc


def manifest_summary(manifest: SeedManifest) -> dict[str, object]:
    """Report manifest size and incomplete verification coverage without inference."""

    return {
        "schemes": len(manifest.entries),
        "sources": sum(len(entry.sources) for entry in manifest.entries),
        "primary_source_schemes": sum(
            any(source.tier == SourceTier.PRIMARY for source in entry.sources)
            for entry in manifest.entries
        ),
        "rules": sum(len(entry.eligibility_rules) for entry in manifest.entries),
        "publish_ready": sum(
            bool(entry.scheme.metadata.get("publish_ready")) for entry in manifest.entries
        ),
    }
