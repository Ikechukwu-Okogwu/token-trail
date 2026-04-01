"""
Test Plan:
- Partitions: disabled limit, enabled limit
- Boundaries: first request at limit edge, second request exceeding limit
- Failure modes: excessive calls return HTTP 429 with Retry-After
"""
from pathlib import Path
import sys

from fastapi import HTTPException
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
pytest.importorskip("bson")

from app.middleware import rate_limit as rl


def test_rate_limit_disabled_no_exception(monkeypatch):
    """When scope limit is zero, no request should be blocked."""
    monkeypatch.setattr(rl, "_scope_limit", lambda scope: 0)
    rl.enforce_rate_limit(scope="submission", subject="127.0.0.1")


def test_rate_limit_blocks_after_cap(monkeypatch):
    """Second call should fail when artificial cap is set to one."""
    monkeypatch.setattr(rl, "_scope_limit", lambda scope: 1)
    rl._STORE.clear()

    rl.enforce_rate_limit(scope="auth", subject="127.0.0.1:test@example.com")
    try:
        rl.enforce_rate_limit(scope="auth", subject="127.0.0.1:test@example.com")
        assert False, "Expected HTTPException for rate limit"
    except HTTPException as exc:
        assert exc.status_code == 429
        assert exc.headers is not None
        assert "Retry-After" in exc.headers
