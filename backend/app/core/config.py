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


def get_cors_origins_list() -> list[str]:
    """Parse CORS_ORIGINS into a list of allowed origins."""
    if not CORS_ORIGINS:
        return []
    return [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
