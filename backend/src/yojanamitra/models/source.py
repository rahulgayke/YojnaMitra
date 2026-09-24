"""Source authority and verification records for scheme facts."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    JSON,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from yojanamitra.db.base import Base
from yojanamitra.models.enums import SourceTier, SourceType, enum_values

if TYPE_CHECKING:
    from yojanamitra.models.document import Document
    from yojanamitra.models.eligibility_rule import EligibilityRule
    from yojanamitra.models.scheme import Scheme


class Source(Base):
    """Track where scheme information originated and who verified it."""

    __tablename__ = "sources"
    __table_args__ = (
        CheckConstraint(
            "authority_score >= 0 AND authority_score <= 100", name="authority_score_range"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_id: Mapped[str] = mapped_column(
        ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    authority: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        SAEnum(SourceType, values_callable=enum_values, native_enum=False, create_constraint=True),
        nullable=False,
    )
    tier: Mapped[SourceTier] = mapped_column(
        SAEnum(SourceTier, values_callable=enum_values, native_enum=False, create_constraint=True),
        nullable=False,
    )
    authority_score: Mapped[int] = mapped_column(default=0, nullable=False)
    # Unknown sources must not be presented as official without an explicit review.
    is_official: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    scheme: Mapped[Scheme] = relationship(back_populates="sources")
    documents: Mapped[list[Document]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )
    eligibility_rules: Mapped[list[EligibilityRule]] = relationship(back_populates="source")
