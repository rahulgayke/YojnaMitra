"""Versioned downloaded-document metadata for future ingestion."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    JSON,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from yojanamitra.db.base import Base
from yojanamitra.models.enums import DocumentStatus, enum_values

if TYPE_CHECKING:
    from yojanamitra.models.chunk import Chunk
    from yojanamitra.models.source import Source


class Document(Base):
    """Describe one immutable content version associated with a source."""

    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("page_count IS NULL OR page_count >= 0", name="page_count_nonnegative"),
        CheckConstraint(
            "effective_from IS NULL OR effective_to IS NULL OR effective_from <= effective_to",
            name="valid_effective_window",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(String(2048))
    version_label: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(
            DocumentStatus, values_callable=enum_values, native_enum=False, create_constraint=True
        ),
        default=DocumentStatus.UNVERIFIED,
        nullable=False,
    )
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[date | None] = mapped_column(Date)
    effective_from: Mapped[date | None] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    page_count: Mapped[int | None]
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    source: Mapped[Source] = relationship(back_populates="documents")
    chunks: Mapped[list[Chunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
