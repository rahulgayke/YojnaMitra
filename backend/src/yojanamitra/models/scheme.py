"""Structured scheme metadata independent of government source documents."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from yojanamitra.db.base import Base
from yojanamitra.models.enums import SchemeScope, SchemeStatus, enum_values

if TYPE_CHECKING:
    from yojanamitra.models.eligibility_rule import EligibilityRule
    from yojanamitra.models.source import Source


class Scheme(Base):
    """Store a scheme's identity, jurisdiction, provenance and status."""

    __tablename__ = "schemes"
    __table_args__ = (
        CheckConstraint(
            "(scope = 'central' AND state_code IS NULL) OR "
            "(scope IN ('state', 'ut') AND state_code IS NOT NULL)",
            name="scope_matches_state_code",
        ),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    ministry: Mapped[str | None] = mapped_column(String(180))
    scope: Mapped[SchemeScope] = mapped_column(
        SAEnum(SchemeScope, values_callable=enum_values, native_enum=False, create_constraint=True),
        default=SchemeScope.CENTRAL,
        nullable=False,
    )
    state_code: Mapped[str | None] = mapped_column(String(2))
    status: Mapped[SchemeStatus] = mapped_column(
        SAEnum(
            SchemeStatus, values_callable=enum_values, native_enum=False, create_constraint=True
        ),
        default=SchemeStatus.UNKNOWN,
        nullable=False,
    )
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # 'metadata' is a reserved SQLAlchemy attribute; the DB column retains the domain name.
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    sources: Mapped[list[Source]] = relationship(
        back_populates="scheme", cascade="all, delete-orphan"
    )
    eligibility_rules: Mapped[list[EligibilityRule]] = relationship(
        back_populates="scheme", cascade="all, delete-orphan"
    )
