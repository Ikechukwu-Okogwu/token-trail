"""
Test Plan:
- Partitions: ANONYMIZATION_MODE none/hash/hmac
- Boundaries: empty identifier input
- Failure modes: deterministic output drift due to salt/mode mismatch
"""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
pytest.importorskip("bson")

from app.services import anonymization_service as svc


def test_none_mode_returns_raw_identifier(monkeypatch):
    """Mode none must preserve existing behavior for backwards compatibility."""
    monkeypatch.setattr(svc, "ANONYMIZATION_MODE", "none")
    monkeypatch.setattr(svc, "ANONYMIZATION_SALT", "salt")
    assert svc.pseudonymize_student_identifier("student-1") == "student-1"


def test_hash_mode_is_deterministic_and_salt_sensitive(monkeypatch):
    """Hash mode should be stable and change when salt changes."""
    monkeypatch.setattr(svc, "ANONYMIZATION_MODE", "hash")
    monkeypatch.setattr(svc, "ANONYMIZATION_SALT", "salt-a")
    first = svc.pseudonymize_student_identifier("student-1")
    second = svc.pseudonymize_student_identifier("student-1")
    assert first == second

    monkeypatch.setattr(svc, "ANONYMIZATION_SALT", "salt-b")
    third = svc.pseudonymize_student_identifier("student-1")
    assert third != first


def test_hmac_mode_handles_empty_identifier(monkeypatch):
    """Empty identifiers should not raise and should return empty string."""
    monkeypatch.setattr(svc, "ANONYMIZATION_MODE", "hmac")
    monkeypatch.setattr(svc, "ANONYMIZATION_SALT", "salt-a")
    assert svc.pseudonymize_student_identifier("") == ""
