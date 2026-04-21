"""Auth business logic.

Registration creates User + Household + Member in a single transaction so that
every authenticated request immediately has a household to operate on.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import Household, Member, Role, User


def register_user(
    db: Session,
    email: str,
    password: str,
    display_name: str,
    household_name: str,
) -> User:
    email = email.lower().strip()
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise ValueError("email already registered")

    hh = Household(name=household_name, base_currency="KRW")
    db.add(hh)
    db.flush()

    member = Member(
        household_id=hh.id,
        name=display_name,
        email=email,
        role=Role.OWNER,
    )
    db.add(member)
    db.flush()

    user = User(email=email, password_hash=hash_password(password), member_id=member.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    email = email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
