"""Small, explicit local demo-data command for Stage 1 verification."""

import argparse
import uuid

from sqlalchemy.orm import Session

from yojanamitra.core.config import get_settings
from yojanamitra.db.session import get_engine
from yojanamitra.models import Scheme, Source
from yojanamitra.models.enums import SchemeScope, SourceTier, SourceType
from yojanamitra.repositories.schemes import add_scheme, add_source, get_scheme_by_id
from yojanamitra.schemas.domain import SchemeCreate, SourceCreate

DEMO_SCHEME_ID = "stage1-demo-scheme"
DEMO_SOURCE_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")


def seed_demo() -> None:
    """Insert one unmistakably synthetic scheme for local read-only API testing."""

    settings = get_settings()
    # A synthetic record must never accidentally be added to a public government dataset.
    if settings.environment != "local" or not settings.database_url.startswith("sqlite"):
        raise RuntimeError("Demo seeding is allowed only with local SQLite configuration")

    scheme_data = SchemeCreate(
        id=DEMO_SCHEME_ID,
        name="Stage 1 Synthetic Test Scheme — NOT A GOVERNMENT SCHEME",
        category="test_only",
        scope=SchemeScope.CENTRAL,
        metadata={"demo_only": True},
    )
    source_data = SourceCreate(
        scheme_id=DEMO_SCHEME_ID,
        title="Synthetic Stage 1 test reference — NOT AN OFFICIAL SOURCE",
        url="https://example.org/yojanamitra/stage1-demo",
        authority="YojanaMitra local tests",
        source_type=SourceType.OTHER,
        tier=SourceTier.CONTEXT_ONLY,
    )
    with Session(get_engine()) as session, session.begin():
        if get_scheme_by_id(session, DEMO_SCHEME_ID) is not None:
            print("Demo already exists; no changes made.")
            return
        add_scheme(
            session,
            Scheme(
                **scheme_data.model_dump(exclude={"metadata"}),
                extra_metadata=scheme_data.metadata,
            ),
        )
        add_source(
            session,
            Source(
                id=DEMO_SOURCE_ID,
                **source_data.model_dump(exclude={"metadata", "url"}),
                url=str(source_data.url),
                extra_metadata=source_data.metadata,
            ),
        )
    print(f"Seeded synthetic demo only: {DEMO_SCHEME_ID}")


def main() -> None:
    """Parse the narrow Stage 1 demo command and execute it."""

    parser = argparse.ArgumentParser(description="Stage 1 local data helper")
    parser.add_argument("action", choices=["seed-demo"])
    args = parser.parse_args()
    if args.action == "seed-demo":
        seed_demo()


if __name__ == "__main__":
    main()
