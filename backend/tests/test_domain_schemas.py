"""Stage 1 validation tests that do not need a running database."""

from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from yojanamitra.models.enums import ComparisonOperator, GroupOperator, RuleKind, SchemeScope
from yojanamitra.schemas.domain import (
    ChunkCreate,
    DocumentCreate,
    EligibilityRuleCreate,
    SchemeCreate,
    SourceCreate,
    UserProfileCreate,
)


def test_scheme_status_defaults_to_unknown() -> None:
    """Prevent an unreviewed scheme from being shown as active."""

    scheme = SchemeCreate(id="demo-scheme", name="Synthetic scheme", category="test")
    assert scheme.status.value == "unknown"
    assert scheme.state_code is None


@pytest.mark.parametrize(
    ("scope", "state", "is_valid"),
    [
        (SchemeScope.CENTRAL, None, True),
        (SchemeScope.CENTRAL, "MH", False),
        (SchemeScope.STATE, "MH", True),
        (SchemeScope.STATE, None, False),
        (SchemeScope.UT, "DL", True),
        (SchemeScope.UT, "mH", False),
    ],
)
def test_scope_state_validation(scope: SchemeScope, state: str | None, is_valid: bool) -> None:
    """Require jurisdiction and state information to remain consistent."""

    fields = dict(
        id="demo-scheme", name="Synthetic scheme", category="test", scope=scope, state_code=state
    )
    if is_valid:
        assert SchemeCreate.model_validate(fields).scope == scope
    else:
        with pytest.raises(ValidationError):
            SchemeCreate.model_validate(fields)


def test_source_defaults_to_unverified_and_requires_url() -> None:
    """Do not mark an arbitrary source official or accept a malformed URL."""

    payload = dict(
        scheme_id="demo-scheme", title="Synthetic source", url="https://example.org/test",
        authority="Demo authority", source_type="other", tier="tier_3"
    )
    assert SourceCreate.model_validate(payload).is_official is False
    with pytest.raises(ValidationError):
        SourceCreate.model_validate({**payload, "url": "not a web URL"})
    with pytest.raises(ValidationError):
        SourceCreate.model_validate({**payload, "authority_score": 101})


def test_nested_group_and_leaf_condition_are_separate() -> None:
    """Allow nested-rule shape definitions without evaluating them in Stage 1."""

    group = EligibilityRuleCreate(
        scheme_id="demo-scheme", kind=RuleKind.GROUP, group_operator=GroupOperator.ALL
    )
    condition = EligibilityRuleCreate(
        scheme_id="demo-scheme", parent_rule_id=uuid4(), kind=RuleKind.CONDITION,
        profile_field="age", comparison_operator=ComparisonOperator.GTE, expected_value=18
    )
    assert group.machine_verified is False
    assert condition.expected_value == 18
    with pytest.raises(ValidationError):
        EligibilityRuleCreate(
            scheme_id="demo-scheme", kind=RuleKind.GROUP,
            group_operator=GroupOperator.ANY, profile_field="age"
        )
    with pytest.raises(ValidationError):
        EligibilityRuleCreate(
            scheme_id="demo-scheme", kind=RuleKind.CONDITION,
            profile_field="age", comparison_operator=ComparisonOperator.GTE
        )


def test_document_version_dates_and_hash_are_validated() -> None:
    """Reject invalid digest text and backwards effective dates."""

    fields = dict(
        source_id=uuid4(), title="Synthetic document", source_url="https://example.org/test.pdf",
        content_hash="a" * 64, mime_type="application/pdf", version_label="v1",
        effective_from=date(2026, 1, 2), effective_to=date(2026, 1, 1)
    )
    with pytest.raises(ValidationError):
        DocumentCreate.model_validate(fields)
    with pytest.raises(ValidationError):
        DocumentCreate.model_validate({**fields, "effective_to": None, "content_hash": "abc"})
    assert (
        DocumentCreate.model_validate({**fields, "effective_to": None}).status.value
        == "unverified"
    )


def test_chunk_metadata_preserves_ordered_citations() -> None:
    """Require valid source page coordinates and a nonempty chunk body."""

    fields = dict(
        document_id=uuid4(), chunk_index=0, text="Synthetic paragraph", page_start=2, page_end=1
    )
    with pytest.raises(ValidationError):
        ChunkCreate.model_validate(fields)
    with pytest.raises(ValidationError):
        ChunkCreate.model_validate({**fields, "page_end": 2, "text": ""})
    assert ChunkCreate.model_validate({**fields, "page_end": 3}).page_end == 3


def test_anonymous_profile_rejects_sensitive_or_unknown_fields() -> None:
    """Keep discovery anonymous and retain distinct user/beneficiary ages."""

    profile = UserProfileCreate(age=28, beneficiary_age=68, beneficiary_relationship="father")
    assert profile.age == 28
    assert profile.beneficiary_age == 68
    for secret in ("aadhaar_number", "pan", "otp", "bank_account", "password"):
        with pytest.raises(ValidationError):
            UserProfileCreate.model_validate({secret: "must not be stored"})
    with pytest.raises(ValidationError):
        UserProfileCreate(age=121)
