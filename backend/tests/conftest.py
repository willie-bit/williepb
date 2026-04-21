from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Point the app to an in-memory SQLite BEFORE the models import.
import os

os.environ["WILLIEPB_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.db.base import Base  # noqa: E402
from app.models import (  # noqa: E402,F401 — register metadata
    account,
    asset,
    household,
    liability,
    member,
    price_quote,
    snapshot,
    transaction,
)


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session(engine) -> Iterator[Session]:
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with SessionLocal() as s:
        yield s
