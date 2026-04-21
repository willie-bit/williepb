"""FastAPI dependencies — auth context for protected routes."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import Household, User


@dataclass(slots=True)
class AuthContext:
    user: User
    household_id: int


def _extract_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    # Cookie fallback — Next.js server components prefer HttpOnly cookies.
    return request.cookies.get("williepb_token")


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_auth_context(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AuthContext:
    if user.member is None or user.member.household_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not linked to a household",
        )
    # Verify household still exists (member might have been reparented).
    hh = db.get(Household, user.member.household_id)
    if hh is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Household missing")
    return AuthContext(user=user, household_id=hh.id)


def require_household(household_id: int, ctx: AuthContext = Depends(get_auth_context)) -> int:
    """Guard route — ensures the authenticated user belongs to the requested household."""
    if ctx.household_id != household_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this household",
        )
    return household_id
