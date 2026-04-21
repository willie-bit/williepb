from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables (MVP convenience; use Alembic for prod migrations)."""
    from app.db.base import Base
    from app.models import (  # noqa: F401 — ensure all models are registered
        household,
        member,
        account,
        asset,
        liability,
        price_quote,
        snapshot,
        transaction,
        user,
    )

    Base.metadata.create_all(bind=engine)
