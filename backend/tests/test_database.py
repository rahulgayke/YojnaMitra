"""Stage 1 SQLite integration tests for the real migration and six entities."""

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, configure_mappers

from yojanamitra.db.base import Base
from yojanamitra.db.session import create_database_engine
from yojanamitra.models import Chunk, Document, EligibilityRule, Scheme, Source, UserProfile
from yojanamitra.models.enums import (
    ComparisonOperator,
    GroupOperator,
    ProfileField,
    RuleKind,
    SchemeScope,
    SourceTier,
    SourceType,
)
from yojanamitra.repositories.schemes import add_scheme, add_source, get_scheme_by_id

BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture
def sqlite_engine(tmp_path: Path) -> Iterator[Engine]:
    """Create a migrated temporary database with foreign keys enforced."""

    engine = create_database_engine(f"sqlite:///{tmp_path / 'stage1.db'}")
    config = Config(str(BACKEND / "alembic.ini"))
    with engine.connect() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
    yield engine
    engine.dispose()


def test_six_models_and_relationships_register() -> None:
    """Check that all models are connected before database interactions begin."""

    configure_mappers()
    assert set(Base.metadata.tables) == {
        "schemes", "sources", "eligibility_rules", "documents", "chunks", "user_profiles"
    }


def test_migration_upgrade_and_downgrade(sqlite_engine: Engine) -> None:
    """Ensure Alembic creates all six entities and can reverse the initial version."""

    assert set(inspect(sqlite_engine).get_table_names()) >= set(Base.metadata.tables)
    config = Config(str(BACKEND / "alembic.ini"))
    with sqlite_engine.connect() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
    assert not (set(inspect(sqlite_engine).get_table_names()) & set(Base.metadata.tables))


def test_all_entities_persist_and_read(sqlite_engine: Engine) -> None:
    """Round-trip metadata, nested rules, versions, chunks and an anonymous profile."""

    with Session(sqlite_engine) as session, session.begin():
        scheme = add_scheme(session, Scheme(id="test-scheme", name="Synthetic", category="test"))
        source = add_source(session, Source(
            scheme_id=scheme.id, title="Synthetic source", url="https://example.org/test",
            authority="Test authority", source_type=SourceType.OTHER, tier=SourceTier.CONTEXT_ONLY
        ))
        rule = EligibilityRule(
            scheme_id=scheme.id, kind=RuleKind.GROUP, group_operator=GroupOperator.ALL
        )
        session.add(rule)
        session.flush()
        session.add(EligibilityRule(
            scheme_id=scheme.id, parent_rule_id=rule.id, kind=RuleKind.CONDITION,
            profile_field=ProfileField.AGE, comparison_operator=ComparisonOperator.GTE,
            expected_value=18, source_id=source.id
        ))
        document = Document(
            source_id=source.id, title="Synthetic PDF metadata",
            source_url="https://example.org/test.pdf", content_hash="a" * 64,
            mime_type="application/pdf", version_label="v1"
        )
        session.add(document)
        session.flush()
        session.add(Chunk(
            document_id=document.id, chunk_index=0, text="Test-only text",
            heading_path=["Overview"], page_start=1, page_end=1
        ))
        profile = UserProfile(age=28, beneficiary_age=68, annual_family_income=Decimal("250000.00"))
        session.add(profile)

    with Session(sqlite_engine) as session:
        scheme = get_scheme_by_id(session, "test-scheme")
        assert scheme is not None
        assert scheme.status.value == "unknown"
        assert len(scheme.sources) == 1
        assert scheme.sources[0].is_official is False
        assert (
            session.scalar(
                select(EligibilityRule).where(EligibilityRule.parent_rule_id.is_not(None))
            )
            is not None
        )
        assert session.scalar(select(Document)).version_label == "v1"
        assert session.scalar(select(Chunk)).heading_path == ["Overview"]
        saved_profile = session.scalar(select(UserProfile))
        assert saved_profile is not None
        assert saved_profile.beneficiary_age == 68
        assert saved_profile.annual_family_income == Decimal("250000.00")
        assert saved_profile.session_id is not None


def test_foreign_keys_and_database_constraints(sqlite_engine: Engine) -> None:
    """Reject orphan records and inconsistent jurisdiction even outside Pydantic."""

    with Session(sqlite_engine) as session:
        session.add(Source(
            scheme_id="missing", title="Orphan", url="https://example.org",
            authority="Unknown", source_type=SourceType.OTHER, tier=SourceTier.CONTEXT_ONLY
        ))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        session.add(Scheme(
            id="bad-state", name="Bad", category="test", scope=SchemeScope.CENTRAL,
            state_code="MH"
        ))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_duplicate_chunk_position_is_rejected(sqlite_engine: Engine) -> None:
    """Ensure two chunks cannot claim the same index within one document version."""

    with Session(sqlite_engine) as session:
        scheme = Scheme(id="test", name="Synthetic", category="test")
        session.add(scheme)
        source = Source(
            scheme_id="test", title="Synthetic", url="https://example.org",
            authority="Test", source_type=SourceType.OTHER, tier=SourceTier.CONTEXT_ONLY
        )
        session.add(source)
        session.flush()
        doc = Document(
            source_id=source.id, title="Test", source_url="https://example.org/test.pdf",
            content_hash="0" * 64, mime_type="application/pdf", version_label="v1"
        )
        session.add(doc)
        session.flush()
        session.add_all([
            Chunk(id=uuid4(), document_id=doc.id, chunk_index=0, text="One"),
            Chunk(id=uuid4(), document_id=doc.id, chunk_index=0, text="Two"),
        ])
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_sqlite_foreign_keys_enabled(sqlite_engine: Engine) -> None:
    """Detect accidental changes that leave SQLite integrity disabled by default."""

    with sqlite_engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
