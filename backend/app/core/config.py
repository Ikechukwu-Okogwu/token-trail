"""Load environment variables cleanly for Token Trail backend."""
import os
from dotenv import load_dotenv

load_dotenv()


def _get_env(key: str, default: str = "") -> str:
    """Get env var with optional default."""
    return os.getenv(key, default).strip()


# MongoDB
MONGO_URI: str = _get_env("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB: str = _get_env("MONGO_DB", "token_trail")

# CORS - comma-separated origins
CORS_ORIGINS: str = _get_env("CORS_ORIGINS", "http://localhost:5173")

# JWT
JWT_SECRET: str = _get_env("JWT_SECRET", "change-me")
JWT_EXPIRES_MINUTES: int = int(_get_env("JWT_EXPIRES_MINUTES", "60"))

# File uploads
UPLOAD_DIR: str = _get_env("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_MB: int = int(_get_env("MAX_UPLOAD_MB", "50"))

# Assignment lifecycle placeholders
DEFAULT_RETENTION_DAYS: int = int(_get_env("DEFAULT_RETENTION_DAYS", "30"))

# Privacy/anonymization placeholders
ANONYMIZATION_MODE: str = _get_env("ANONYMIZATION_MODE", "none")
ANONYMIZATION_SALT: str = _get_env("ANONYMIZATION_SALT", "")

# Notification/email placeholders
EMAIL_PROVIDER: str = _get_env("EMAIL_PROVIDER", "none")
EMAIL_FROM: str = _get_env("EMAIL_FROM", "")
SMTP_HOST: str = _get_env("SMTP_HOST", "")
SMTP_PORT: int = int(_get_env("SMTP_PORT", "587"))
SMTP_USERNAME: str = _get_env("SMTP_USERNAME", "")
SMTP_PASSWORD: str = _get_env("SMTP_PASSWORD", "")
SMTP_USE_TLS: bool = _get_env("SMTP_USE_TLS", "1") == "1"

# Rate-limit placeholders
RATE_LIMIT_AUTH_ATTEMPTS_PER_HOUR: int = int(
    _get_env("RATE_LIMIT_AUTH_ATTEMPTS_PER_HOUR", "0")
)
RATE_LIMIT_SUBMISSION_ATTEMPTS_PER_HOUR: int = int(
    _get_env("RATE_LIMIT_SUBMISSION_ATTEMPTS_PER_HOUR", "0")
)


def get_cors_origins_list() -> list[str]:
    """Parse CORS_ORIGINS into a list of allowed origins."""
    if not CORS_ORIGINS:
        return []
    return [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
