"""Anonymous, minimal eligibility profile without identity credentials."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, JSON, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from yojanamitra.db.base import Base


class UserProfile(Base):
    """Store voluntarily supplied eligibility attributes for an anonymous session."""

    __tablename__ = "user_profiles"
    __table_args__ = (
        CheckConstraint("age IS NULL OR (age >= 0 AND age <= 120)", name="valid_age"),
        CheckConstraint(
            "beneficiary_age IS NULL OR (beneficiary_age >= 0 AND beneficiary_age <= 120)",
            name="valid_beneficiary_age",
        ),
        CheckConstraint(
            "annual_family_income IS NULL OR annual_family_income >= 0", name="nonnegative_income"
        ),
        CheckConstraint(
            "landholding_acres IS NULL OR landholding_acres >= 0", name="nonnegative_land"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True
    )
    age: Mapped[int | None]
    beneficiary_age: Mapped[int | None]
    beneficiary_relationship: Mapped[str | None] = mapped_column(String(60))
    gender: Mapped[str | None] = mapped_column(String(40))
    state_code: Mapped[str | None] = mapped_column(String(2))
    district: Mapped[str | None] = mapped_column(String(100))
    annual_family_income: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    income_band: Mapped[str | None] = mapped_column(String(60))
    occupation: Mapped[str | None] = mapped_column(String(100))
    employment_status: Mapped[str | None] = mapped_column(String(60))
    is_student: Mapped[bool | None] = mapped_column(Boolean)
    education_level: Mapped[str | None] = mapped_column(String(80))
    is_farmer: Mapped[bool | None] = mapped_column(Boolean)
    landholding_acres: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    residence_type: Mapped[str | None] = mapped_column(String(20))
    disability_status: Mapped[str | None] = mapped_column(String(60))
    scheme_interests: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_fields: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
