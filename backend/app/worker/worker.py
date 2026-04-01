"""Token Trail - Analysis worker.

Polls MongoDB for queued AnalysisRun jobs, claims them atomically,
runs the analysis stub, and marks them completed or failed.
"""
import os
import sys
import time
from datetime import datetime, timezone

# Allow running as a standalone script from the backend directory
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from dotenv import load_dotenv

load_dotenv()

from pymongo import MongoClient, ReturnDocument

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "token_trail")

POLL_INTERVAL_SECONDS = 5
PURGE_INTERVAL_SECONDS = 24 * 60 * 60


def main():
    """Connect to MongoDB and process queued AnalysisRun jobs."""
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]

    print("worker started")

    # Lazy import so the worker boots even if analysis code evolves
    from app.services.analysis_service import run_analysis_for_assignment
    from app.services.retention_service import purge_expired_assignment_data

    # Defer first purge window so startup can process queued analysis runs quickly.
    last_purge_at = time.time()

    while True:
        now_epoch = time.time()
        if now_epoch - last_purge_at >= PURGE_INTERVAL_SECONDS:
            try:
                purge_stats = purge_expired_assignment_data(db)
                print(
                    "[worker] retention purge:",
                    f"submissions={purge_stats['deletedSubmissions']}",
                    f"dirs={purge_stats['deletedSubmissionDirs']}",
                )
            except Exception as exc:
                print(f"[worker] retention purge failed: {exc}")
            last_purge_at = now_epoch

        # Atomically claim one queued job (prevents duplicate processing)
        job = db.analysis_runs.find_one_and_update(
            {"status": "queued"},
            {
                "$set": {
                    "status": "running",
                    "startedAt": datetime.now(timezone.utc).isoformat(),
                }
            },
            return_document=ReturnDocument.AFTER,
        )

        if job:
            run_id = str(job["_id"])
            assignment_id = job["assignmentId"]
            print(f"[worker] claimed run {run_id} for assignment {assignment_id}")

            try:
                run_analysis_for_assignment(db, assignment_id, run_id)
                db.analysis_runs.update_one(
                    {"_id": job["_id"]},
                    {
                        "$set": {
                            "status": "completed",
                            "finishedAt": datetime.now(timezone.utc).isoformat(),
                        }
                    },
                )
                print(f"[worker] completed run {run_id}")
            except Exception as exc:
                db.analysis_runs.update_one(
                    {"_id": job["_id"]},
                    {
                        "$set": {
                            "status": "failed",
                            "finishedAt": datetime.now(timezone.utc).isoformat(),
                            "errorMessage": str(exc),
                        }
                    },
                )
                print(f"[worker] failed run {run_id}: {exc}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
