"""Password hashing + JWT encoding/decoding.

bcrypt is used directly (not via passlib) to avoid a long-standing compatibility
wart between passlib's bcrypt backend detection and recent bcrypt releases.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings

_ALGO = "HS256"
_ACCESS_TOKEN_TTL = timedelta(days=7)


def hash_password(password: str) -> str:
    # bcrypt max input is 72 bytes; we enforce it explicitly so long passwords
    # don't silently get truncated in a way that changes verify semantics.
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8")[:72], password_hash.encode("utf-8"))
    except ValueError:
        return False


def _signing_key() -> str:
    key = get_settings().jwt_secret
    if not key:
        # Deliberately unsafe default for dev. Prod must set WILLIEPB_JWT_SECRET.
        return "dev-only-not-secret-change-me-please-xxxxxxxxxx"
    return key


def create_access_token(user_id: int, ttl: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + (ttl or _ACCESS_TOKEN_TTL)).timestamp()),
    }
    return jwt.encode(payload, _signing_key(), algorithm=_ALGO)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, _signing_key(), algorithms=[_ALGO])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None
