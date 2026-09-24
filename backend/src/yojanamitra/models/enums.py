"""Stable domain vocabularies shared by persistence and API validation."""

from enum import Enum


class SchemeScope(str, Enum):
    """Identify the jurisdiction responsible for a scheme."""

    CENTRAL = "central"
    STATE = "state"
    UT = "ut"


class SchemeStatus(str, Enum):
    """Represent a scheme's evidence-backed operational status."""

    UNKNOWN = "unknown"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class SourceTier(str, Enum):
    """Distinguish primary authorities from discovery and contextual sources."""

    PRIMARY = "tier_1"
    GOVERNMENT_AGGREGATOR = "tier_2"
    CONTEXT_ONLY = "tier_3"


class SourceType(str, Enum):
    """Describe the kind of government source or related reference."""

    GUIDELINE = "guideline"
    NOTIFICATION = "notification"
    GAZETTE = "gazette"
    MINISTRY_PAGE = "ministry_page"
    OFFICIAL_API = "official_api"
    GOVERNMENT_AGGREGATOR = "government_aggregator"
    PRESS_RELEASE = "press_release"
    OTHER = "other"


class RuleKind(str, Enum):
    """Distinguish a Boolean rule group from a leaf condition."""

    GROUP = "group"
    CONDITION = "condition"


class GroupOperator(str, Enum):
    """Describe how a nested group combines child rule results."""

    ALL = "all"
    ANY = "any"


class ComparisonOperator(str, Enum):
    """Declare the operators Stage 8's deterministic engine will implement."""

    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    CONTAINS = "contains"
    EXISTS = "exists"


class ProfileField(str, Enum):
    """Limit rule field references to known, consent-appropriate profile data."""

    AGE = "age"
    BENEFICIARY_AGE = "beneficiary_age"
    BENEFICIARY_RELATIONSHIP = "beneficiary_relationship"
    GENDER = "gender"
    STATE_CODE = "state_code"
    DISTRICT = "district"
    ANNUAL_FAMILY_INCOME = "annual_family_income"
    INCOME_BAND = "income_band"
    OCCUPATION = "occupation"
    EMPLOYMENT_STATUS = "employment_status"
    IS_STUDENT = "is_student"
    EDUCATION_LEVEL = "education_level"
    IS_FARMER = "is_farmer"
    LANDHOLDING_ACRES = "landholding_acres"
    RESIDENCE_TYPE = "residence_type"
    DISABILITY_STATUS = "disability_status"


class DocumentStatus(str, Enum):
    """Differentiate draft/current source versions from historical copies."""

    UNVERIFIED = "unverified"
    CURRENT = "current"
    SUPERSEDED = "superseded"


def enum_values(enum_type: type[Enum]) -> list[str]:
    """Return enum values so database storage matches public JSON contracts."""

    return [str(member.value) for member in enum_type]
