"""Submission document creation helper."""
from datetime import datetime, timezone

from bson import ObjectId
from pymongo.database import Database


def create_submission(
    db: Database,
    *,
    submission_id: str,
    assignment_id: str,
    student_identifier: str,
    student_name: str | None,
    file_count: int,
    zip_storage_path: str,
    merged_storage_path: str,
) -> dict:
    """Insert a Submission document into the submissions collection."""
    doc = {
        "_id": ObjectId(submission_id),
        "assignmentId": assignment_id,
        "studentIdentifier": student_identifier,
        "studentName": student_name,
        "submittedAt": datetime.now(timezone.utc).isoformat(),
        "fileCount": file_count,
        "status": "processed",
        "zipStoragePath": zip_storage_path,
        "mergedStoragePath": merged_storage_path,
    }
    db.submissions.insert_one(doc)
    return doc
