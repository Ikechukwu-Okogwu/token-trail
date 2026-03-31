"""Retention-policy cleanup service."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil

from bson import ObjectId
from pymongo.database import Database

from app.core.config import DEFAULT_RETENTION_DAYS
from app.core.db import get_db


def purge_expired_assignment_data(db: Database | None = None) -> dict[str, int]:
    """Delete submissions older than retention window and remove disk files.

    Returns counts for observability.
    """
    database = db if db is not None else get_db()
    retention_days = DEFAULT_RETENTION_DAYS if DEFAULT_RETENTION_DAYS > 0 else 30
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    deleted_submissions = 0
    deleted_files = 0

    for submission in database.submissions.find(
        {}, {"_id": 1, "submittedAt": 1, "zipStoragePath": 1, "mergedStoragePath": 1}
    ):
        submitted_at_raw = submission.get("submittedAt")
        if not submitted_at_raw:
            continue
        try:
            submitted_at = datetime.fromisoformat(str(submitted_at_raw).replace("Z", "+00:00"))
            if submitted_at.tzinfo is None:
                submitted_at = submitted_at.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

        if submitted_at >= cutoff:
            continue

        submission_id = submission.get("_id")
        if isinstance(submission_id, ObjectId):
            database.submissions.delete_one({"_id": submission_id})
            deleted_submissions += 1

        # Remove submission directory inferred from known storage paths.
        submission_root: Path | None = None
        for path_key in ("zipStoragePath", "mergedStoragePath"):
            raw = submission.get(path_key)
            if not raw:
                continue
            p = Path(raw)
            # .../<submissionId>/raw.zip or .../<submissionId>/merged/merged.txt
            if p.name == "raw.zip":
                submission_root = p.parent
            elif p.name == "merged.txt":
                submission_root = p.parent.parent
            if submission_root:
                break

        if submission_root and submission_root.exists() and submission_root.is_dir():
            shutil.rmtree(submission_root, ignore_errors=True)
            deleted_files += 1

    return {"deletedSubmissions": deleted_submissions, "deletedSubmissionDirs": deleted_files}
