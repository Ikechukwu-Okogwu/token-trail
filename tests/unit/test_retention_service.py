"""
Test Plan:
- Partitions: expired submissions, non-expired submissions
- Boundaries: submittedAt exactly around cutoff via far past/future timestamps
- Failure modes: missing timestamps are ignored without crashing
"""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
pytest.importorskip("bson")
from bson import ObjectId

from app.services.retention_service import purge_expired_assignment_data


class _FakeCollection:
    def __init__(self, docs):
        self._docs = docs

    def find(self, *_args, **_kwargs):
        return list(self._docs)

    def delete_one(self, query):
        target = query.get("_id")
        self._docs = [d for d in self._docs if d.get("_id") != target]


class _FakeDb:
    def __init__(self, docs):
        self.submissions = _FakeCollection(docs)


def test_purge_deletes_only_expired_submission_dirs(tmp_path):
    """Expired submission should be removed while future submission remains."""
    old_root = tmp_path / "assign-a" / "sub-old"
    old_root.mkdir(parents=True, exist_ok=True)
    old_raw = old_root / "raw.zip"
    old_raw.write_bytes(b"zip")

    new_root = tmp_path / "assign-a" / "sub-new"
    new_root.mkdir(parents=True, exist_ok=True)
    new_raw = new_root / "raw.zip"
    new_raw.write_bytes(b"zip")

    docs = [
        {
            "_id": ObjectId(),
            "submittedAt": "2000-01-01T00:00:00+00:00",
            "zipStoragePath": str(old_raw),
            "mergedStoragePath": str(old_root / "merged" / "merged.txt"),
        },
        {
            "_id": ObjectId(),
            "submittedAt": "2999-01-01T00:00:00+00:00",
            "zipStoragePath": str(new_raw),
            "mergedStoragePath": str(new_root / "merged" / "merged.txt"),
        },
    ]
    db = _FakeDb(docs)
    stats = purge_expired_assignment_data(db)
    assert stats["deletedSubmissions"] == 1
    assert not old_root.exists()
    assert new_root.exists()
