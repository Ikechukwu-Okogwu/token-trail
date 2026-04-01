"""Helpers for anonymizing student identifiers."""
import hashlib
import hmac

from app.core.config import ANONYMIZATION_MODE, ANONYMIZATION_SALT


def pseudonymize_student_identifier(student_identifier: str) -> str:
    """Return a stable pseudonym based on configured anonymization mode.

    Modes:
    - none: return the original identifier
    - hash: sha256(salt + identifier)
    - hmac: hmac-sha256(salt, identifier)
    - any other non-none value defaults to hash mode
    """
    if ANONYMIZATION_MODE == "none":
        return student_identifier

    value = (student_identifier or "").strip()
    if not value:
        return value

    salt = ANONYMIZATION_SALT or ""
    if ANONYMIZATION_MODE == "hmac":
        return hmac.new(
            key=salt.encode("utf-8"),
            msg=value.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    # Default hash mode for "hash" and any custom non-none mode.
    digest = hashlib.sha256()
    digest.update((salt + value).encode("utf-8"))
    return digest.hexdigest()
