"""Strict typed contracts for the six Stage 1 domain entities."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    JsonValue,
    StringConstraints,
    model_validator,
)

from yojanamitra.models.enums import (
    ComparisonOperator,
    DocumentStatus,
    GroupOperator,
    ProfileField,
    RuleKind,
    SchemeScope,
    SchemeStatus,
    SourceTier,
    SourceType,
)

Slug = Annotated[
    str, StringConstraints(min_length=2, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
]
StateCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]
Hash256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class DomainSchema(BaseModel):
    """Reject unexpected fields, including identity and credential fields."""

    model_config = ConfigDict(extra="forbid", from_attributes=True, str_strip_whitespace=True)


class SchemeCreate(DomainSchema):
    """Validate the structured metadata used to register a scheme."""

    id: Slug
    name: str = Field(min_length=2, max_length=250)
    short_name: str | None = Field(default=None, max_length=80)
    category: str = Field(min_length=2, max_length=80)
    ministry: str | None = Field(default=None, max_length=180)
    scope: SchemeScope = SchemeScope.CENTRAL
    state_code: StateCode | None = None
    status: SchemeStatus = SchemeStatus.UNKNOWN
    last_verified_at: datetime | None = None
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_scope(self) -> "SchemeCreate":
        """Require a state code for state/UT schemes and forbid it for central schemes."""

        if self.scope == SchemeScope.CENTRAL and self.state_code is not None:
            raise ValueError("Central schemes cannot specify a state_code")
        if self.scope != SchemeScope.CENTRAL and self.state_code is None:
            raise ValueError("State and UT schemes require a state_code")
        return self


class SourceCreate(DomainSchema):
    """Validate source identity, URL and evidence-authority metadata."""

    scheme_id: Slug
    title: str = Field(min_length=2, max_length=250)
    url: HttpUrl
    authority: str = Field(min_length=2, max_length=200)
    source_type: SourceType
    tier: SourceTier
    authority_score: int = Field(default=0, ge=0, le=100)
    is_official: bool = False
    last_verified_at: datetime | None = None
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class SourceRead(SourceCreate):
    """Expose source metadata with its assigned immutable ID."""

    id: UUID
    # SQLAlchemy reserves `.metadata`; map the ORM alias back to the public name.
    metadata: dict[str, JsonValue] = Field(
        default_factory=dict, validation_alias="extra_metadata", serialization_alias="metadata"
    )


class SchemeRead(SchemeCreate):
    """Return scheme metadata and registered sources without unsupported claims."""

    metadata: dict[str, JsonValue] = Field(
        default_factory=dict, validation_alias="extra_metadata", serialization_alias="metadata"
    )
    sources: list[SourceRead] = Field(default_factory=list)


class EligibilityRuleCreate(DomainSchema):
    """Validate a nested ALL/ANY group or one leaf comparison."""

    scheme_id: Slug
    parent_rule_id: UUID | None = None
    source_id: UUID | None = None
    kind: RuleKind
    group_operator: GroupOperator | None = None
    profile_field: ProfileField | None = None
    comparison_operator: ComparisonOperator | None = None
    expected_value: JsonValue | None = None
    priority: int = Field(default=0, ge=0)
    rule_version: str | None = Field(default=None, max_length=80)
    machine_verified: bool = False

    @model_validator(mode="after")
    def validate_rule_shape(self) -> "EligibilityRuleCreate":
        """Prevent mixing group-only and condition-only fields in one node."""

        if self.kind == RuleKind.GROUP:
            if self.group_operator is None:
                raise ValueError("A group requires group_operator")
            if any(
                value is not None
                for value in (self.profile_field, self.comparison_operator, self.expected_value)
            ):
                raise ValueError("A group cannot contain condition fields")
        elif (
            self.group_operator is not None
            or self.profile_field is None
            or self.comparison_operator is None
        ):
            raise ValueError("A condition needs profile_field and comparison_operator only")
        if (
            self.kind == RuleKind.CONDITION
            and self.comparison_operator != ComparisonOperator.EXISTS
        ):
            if self.expected_value is None:
                raise ValueError("Non-EXISTS conditions require expected_value")
        return self


class DocumentCreate(DomainSchema):
    """Validate source-bound version metadata before document ingestion."""

    source_id: UUID
    title: str = Field(min_length=2, max_length=250)
    source_url: HttpUrl
    content_hash: Hash256
    mime_type: str = Field(min_length=3, max_length=120)
    storage_uri: str | None = Field(default=None, max_length=2048)
    version_label: str = Field(min_length=1, max_length=80)
    status: DocumentStatus = DocumentStatus.UNVERIFIED
    downloaded_at: datetime | None = None
    published_at: date | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    page_count: int | None = Field(default=None, ge=0)
    language: str = Field(default="en", min_length=2, max_length=10)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_effective_window(self) -> "DocumentCreate":
        """Reject document versions whose end precedes their effective start."""

        if self.effective_from and self.effective_to and self.effective_from > self.effective_to:
            raise ValueError("effective_to must not precede effective_from")
        return self


class ChunkCreate(DomainSchema):
    """Validate retrievable text and section/page citation coordinates."""

    document_id: UUID
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)
    heading: str | None = Field(default=None, max_length=250)
    section: str | None = Field(default=None, max_length=100)
    heading_path: list[str] = Field(default_factory=list)
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    token_count: int | None = Field(default=None, ge=0)
    content_hash: Hash256 | None = None
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_pages(self) -> "ChunkCreate":
        """Keep page citations ordered whenever both bounds are present."""

        if self.page_start and self.page_end and self.page_start > self.page_end:
            raise ValueError("page_end must not precede page_start")
        return self


class UserProfileCreate(DomainSchema):
    """Accept a minimal anonymous eligibility profile, never credentials."""

    age: int | None = Field(default=None, ge=0, le=120)
    beneficiary_age: int | None = Field(default=None, ge=0, le=120)
    beneficiary_relationship: str | None = Field(default=None, max_length=60)
    gender: str | None = Field(default=None, max_length=40)
    state_code: StateCode | None = None
    district: str | None = Field(default=None, max_length=100)
    annual_family_income: Decimal | None = Field(
        default=None, ge=0, max_digits=14, decimal_places=2
    )
    income_band: str | None = Field(default=None, max_length=60)
    occupation: str | None = Field(default=None, max_length=100)
    employment_status: str | None = Field(default=None, max_length=60)
    is_student: bool | None = None
    education_level: str | None = Field(default=None, max_length=80)
    is_farmer: bool | None = None
    landholding_acres: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    residence_type: str | None = Field(default=None, max_length=20)
    disability_status: str | None = Field(default=None, max_length=60)
    scheme_interests: list[str] = Field(default_factory=list, max_length=20)
    missing_fields: list[ProfileField] = Field(default_factory=list)
