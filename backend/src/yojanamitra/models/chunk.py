"""Text spans and citation coordinates for future retrieval."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, JSON, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from yojanamitra.db.base import Base

if TYPE_CHECKING:
    from yojanamitra.models.document import Document


class Chunk(Base):
    """Store a document segment with its section and page provenance."""

    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),
        CheckConstraint("chunk_index >= 0", name="chunk_index_nonnegative"),
        CheckConstraint("token_count IS NULL OR token_count >= 0", name="token_count_nonnegative"),
        CheckConstraint(
            "page_start IS NULL OR page_end IS NULL OR page_start <= page_end",
            name="valid_page_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int]
    text: Mapped[str] = mapped_column(Text, nullable=False)
    heading: Mapped[str | None] = mapped_column(String(250))
    section: Mapped[str | None] = mapped_column(String(100))
    heading_path: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    page_start: Mapped[int | None]
    page_end: Mapped[int | None]
    token_count: Mapped[int | None]
    content_hash: Mapped[str | None] = mapped_column(String(64))
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    document: Mapped[Document] = relationship(back_populates="chunks")
