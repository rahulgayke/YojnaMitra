"""Version-aware nested eligibility definitions; no evaluation logic yet."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Enum as SAEnum, ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from yojanamitra.db.base import Base
from yojanamitra.models.enums import (
    ComparisonOperator,
    GroupOperator,
    ProfileField,
    RuleKind,
    enum_values,
)

if TYPE_CHECKING:
    from yojanamitra.models.scheme import Scheme
    from yojanamitra.models.source import Source


class EligibilityRule(Base):
    """Store a group or condition in a scheme-specific eligibility tree."""

    __tablename__ = "eligibility_rules"
    __table_args__ = (
        CheckConstraint(
            "(kind = 'group' AND group_operator IS NOT NULL AND profile_field IS NULL "
            "AND comparison_operator IS NULL AND expected_value IS NULL) OR "
            "(kind = 'condition' AND group_operator IS NULL AND profile_field IS NOT NULL "
            "AND comparison_operator IS NOT NULL)",
            name="valid_rule_shape",
        ),
        CheckConstraint("priority >= 0", name="nonnegative_priority"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_id: Mapped[str] = mapped_column(
        ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("eligibility_rules.id", ondelete="CASCADE"), index=True
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL")
    )
    kind: Mapped[RuleKind] = mapped_column(
        SAEnum(RuleKind, values_callable=enum_values, native_enum=False, create_constraint=True),
        nullable=False,
    )
    group_operator: Mapped[GroupOperator | None] = mapped_column(
        SAEnum(
            GroupOperator, values_callable=enum_values, native_enum=False, create_constraint=True
        )
    )
    profile_field: Mapped[ProfileField | None] = mapped_column(
        SAEnum(ProfileField, values_callable=enum_values, native_enum=False, create_constraint=True)
    )
    comparison_operator: Mapped[ComparisonOperator | None] = mapped_column(
        SAEnum(
            ComparisonOperator,
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True
        )
    )
    expected_value: Mapped[object | None] = mapped_column(JSON(none_as_null=True))
    priority: Mapped[int] = mapped_column(default=0, nullable=False)
    rule_version: Mapped[str | None] = mapped_column(String(80))
    # Machine-verification is a human-reviewed claim, never inferred from creating a rule.
    machine_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    scheme: Mapped[Scheme] = relationship(back_populates="eligibility_rules")
    source: Mapped[Source | None] = relationship(back_populates="eligibility_rules")
    parent: Mapped[EligibilityRule | None] = relationship(
        back_populates="children", remote_side="EligibilityRule.id"
    )
    children: Mapped[list[EligibilityRule]] = relationship(back_populates="parent")
