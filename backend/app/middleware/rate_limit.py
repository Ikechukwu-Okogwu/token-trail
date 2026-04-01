"""In-memory rate-limiting utilities."""
from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import HTTPException

from app.core.config import (
    RATE_LIMIT_AUTH_ATTEMPTS_PER_HOUR,
    RATE_LIMIT_SUBMISSION_ATTEMPTS_PER_HOUR,
)

_LOCK = Lock()
_WINDOW = timedelta(hours=1)
_STORE: dict[tuple[str, str], list[datetime]] = {}


def _scope_limit(scope: str) -> int:
    if scope == "auth":
        return RATE_LIMIT_AUTH_ATTEMPTS_PER_HOUR
    if scope == "submission":
        return RATE_LIMIT_SUBMISSION_ATTEMPTS_PER_HOUR
    return 0


def enforce_rate_limit(*, scope: str, subject: str) -> None:
    """Enforce per-hour limit for a scope/subject pair.

    `subject` is caller-defined (e.g. IP, IP+email).
    """
    limit = _scope_limit(scope)
    if limit <= 0:
        return

    key = (scope, subject)
    now = datetime.now(timezone.utc)
    cutoff = now - _WINDOW

    with _LOCK:
        attempts = _STORE.get(key, [])
        attempts = [ts for ts in attempts if ts >= cutoff]
        if len(attempts) >= limit:
            retry_after = int((_WINDOW - (now - attempts[0])).total_seconds())
            retry_after = max(retry_after, 1)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for {scope}. Please retry later.",
                headers={"Retry-After": str(retry_after)},
            )
        attempts.append(now)
        _STORE[key] = attempts
