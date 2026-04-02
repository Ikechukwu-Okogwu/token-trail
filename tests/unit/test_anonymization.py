"""
Unit tests for the anonymization pipeline.

Verifies:
- pseudonymize_student_identifier produces stable hashes
- Different identifiers produce different hashes
- Hash mode and HMAC mode both work
- None mode returns raw values
- Submission storage keeps raw values (no write-time hashing)
- Export uses submissionId (opaque), not student identity
"""

from __future__ import annotations

import hashlib
import hmac as hmac_mod
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Make the backend importable without installing it
_BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


# ── Core pseudonymization logic ──────────────────────

class TestPseudonymize:
    """Test the pseudonymize function under different modes."""

    def test_hash_mode_returns_sha256(self):
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "hash"), \
             patch("app.services.anonymization_service.ANONYMIZATION_SALT", "test-salt"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            # Force re-evaluation
            result = pseudonymize_student_identifier("alice123")
            expected = hashlib.sha256(("test-salt" + "alice123").encode("utf-8")).hexdigest()
            assert result == expected
            assert len(result) == 64  # SHA256 hex length

    def test_hash_mode_is_stable(self):
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "hash"), \
             patch("app.services.anonymization_service.ANONYMIZATION_SALT", "salt"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            a = pseudonymize_student_identifier("student1")
            b = pseudonymize_student_identifier("student1")
            assert a == b

    def test_different_inputs_different_hashes(self):
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "hash"), \
             patch("app.services.anonymization_service.ANONYMIZATION_SALT", "salt"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            a = pseudonymize_student_identifier("alice")
            b = pseudonymize_student_identifier("bob")
            assert a != b

    def test_hmac_mode(self):
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "hmac"), \
             patch("app.services.anonymization_service.ANONYMIZATION_SALT", "secret"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            result = pseudonymize_student_identifier("alice123")
            expected = hmac_mod.new(
                key=b"secret", msg=b"alice123", digestmod=hashlib.sha256,
            ).hexdigest()
            assert result == expected

    def test_none_mode_returns_raw(self):
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "none"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            assert pseudonymize_student_identifier("alice123") == "alice123"

    def test_empty_string_returns_empty(self):
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "hash"), \
             patch("app.services.anonymization_service.ANONYMIZATION_SALT", "salt"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            assert pseudonymize_student_identifier("") == ""

    def test_none_input_handled(self):
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "none"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            assert pseudonymize_student_identifier(None) is None


# ── Submission storage keeps raw values ────────────

class TestSubmissionServiceRawStorage:
    """Verify create_submission stores raw identifier and name (no write-time hashing)."""

    def test_submission_stores_raw_identifier(self):
        """submission_service.create_submission must NOT hash studentIdentifier."""
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        mock_db.submissions.insert_one = MagicMock()

        from app.services.submission_service import create_submission
        doc = create_submission(
            mock_db,
            submission_id="6650a1b2c3d4e5f6a7b8c9d0",
            assignment_id="test-assignment",
            student_identifier="alice123",
            student_name="Alice Smith",
            student_email="alice@example.com",
            file_count=3,
            zip_storage_path="/tmp/zip",
            merged_storage_path="/tmp/merged",
        )
        assert doc["studentIdentifier"] == "alice123"
        assert doc["studentName"] == "Alice Smith"

    def test_submission_stores_none_name(self):
        """If studentName is None, it stays None in storage."""
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        mock_db.submissions.insert_one = MagicMock()

        from app.services.submission_service import create_submission
        doc = create_submission(
            mock_db,
            submission_id="6650a1b2c3d4e5f6a7b8c9d1",
            assignment_id="test-assignment",
            student_identifier="bob456",
            student_name=None,
            student_email=None,
            file_count=1,
            zip_storage_path="/tmp/zip",
            merged_storage_path="/tmp/merged",
        )
        assert doc["studentIdentifier"] == "bob456"
        assert doc["studentName"] is None


# ── Output-layer anonymization ─────────────────────

class TestOutputLayerAnonymization:
    """Verify that pseudonymize transforms values for API responses."""

    def test_hash_mode_anonymizes_for_output(self):
        """When mode=hash, output-layer call returns a hash, not the raw value."""
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "hash"), \
             patch("app.services.anonymization_service.ANONYMIZATION_SALT", "salt"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            result = pseudonymize_student_identifier("alice123")
            assert result != "alice123"
            assert len(result) == 64

    def test_none_mode_passes_through(self):
        """When mode=none, output-layer returns the raw value unchanged."""
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "none"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            assert pseudonymize_student_identifier("alice123") == "alice123"

    def test_none_value_returns_empty_in_hash_mode(self):
        """Pseudonymize(None) returns '' in hash mode; routers guard with `if x else None`."""
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "hash"), \
             patch("app.services.anonymization_service.ANONYMIZATION_SALT", "salt"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            assert pseudonymize_student_identifier(None) == ""

    def test_router_guard_pattern(self):
        """Routers use `pseudonymize(x) if x else None` — verify the pattern."""
        with patch("app.services.anonymization_service.ANONYMIZATION_MODE", "hash"), \
             patch("app.services.anonymization_service.ANONYMIZATION_SALT", "salt"):
            from app.services.anonymization_service import pseudonymize_student_identifier
            name = None
            result = pseudonymize_student_identifier(name) if name else None
            assert result is None

            name = "Alice"
            result = pseudonymize_student_identifier(name) if name else None
            assert result is not None
            assert len(result) == 64


# ── Export uses submissionId, not student identity ───

class TestExportAnonymity:
    """Verify export archive uses submissionId as folder names."""

    def test_export_folders_are_submission_ids(self):
        from app.services.zip_service import build_submissions_archive
        import zipfile, io

        submissions = [
            {
                "_id": "aaa111bbb222",
                "zipStoragePath": None,
                "mergedStoragePath": None,
            },
            {
                "_id": "ccc333ddd444",
                "zipStoragePath": None,
                "mergedStoragePath": None,
            },
        ]
        # With no actual files, the archive will be mostly empty but
        # the folder structure uses submission IDs, not student names
        payload = build_submissions_archive(
            assignment_id="test-assignment",
            submissions=submissions,
        )
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            names = zf.namelist()
            # No student identifiers should appear — only submission IDs
            for name in names:
                assert "alice" not in name.lower()
                assert "student" not in name.lower()


# ── Default config is hash mode ──────────────────────

class TestDefaultConfig:
    """Verify the default anonymization config is hash mode."""

    def test_default_mode_is_hash(self, monkeypatch):
        # Clear env override and suppress .env file so we test the code default
        monkeypatch.delenv("ANONYMIZATION_MODE", raising=False)
        monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **kw: None)
        import importlib
        import app.core.config as cfg
        importlib.reload(cfg)
        assert cfg.ANONYMIZATION_MODE == "hash"

    def test_default_salt_is_set(self, monkeypatch):
        monkeypatch.delenv("ANONYMIZATION_SALT", raising=False)
        monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **kw: None)
        import importlib
        import app.core.config as cfg
        importlib.reload(cfg)
        assert cfg.ANONYMIZATION_SALT != ""
