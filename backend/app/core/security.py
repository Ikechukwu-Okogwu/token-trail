"""Password hashing (bcrypt) and JWT helpers for Token Trail."""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import JWT_EXPIRES_MINUTES, JWT_SECRET

ALGORITHM = "HS256"


# ── Password helpers ───────────────────────────────

def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Check a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ── JWT helpers ────────────────────────────────────

def create_access_token(subject: str) -> str:
    """Create a JWT with the given subject (instructor ID)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRES_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Decode a JWT and return the subject, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
