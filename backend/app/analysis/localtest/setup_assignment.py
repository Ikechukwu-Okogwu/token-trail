"""Setup assignment: create course, assignment, submit zips, log assignment key."""
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent.parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

import requests

from app.analysis.localtest.get_access_token import get_access_token
from app.analysis.localtest.log import test_log

BASE_URL = "http://localhost:8000/api"
TEST_PROJECT = "setup_assignment"

course_config = {
    "name": "COSC 1P02", 
    "term": "Winter 2026", 
}

assignment_config = {
    "title": "Assignment 1", 
    "language": "java",
    "isOpen": True,
    "dueDate": None,
    "keyExpiry": None,
    "autoAnalysis": False,
    "allowLate": False,
    "exclusionCode": None,  # boilerplate code to exclude
}

# Submissions: POST /api/public/submissions (assignmentKey filled by script)
users_config: list[dict[str, str]] = [
    {
        "name": "John Doe",
        "email": "aa11aa@brocku.ca",
        "password": "admin",
        "submission_path": "submission_files/original.zip"
    },
    {
        "name": "Extra Spice",
        "email": "bb22bb@brocku.ca",
        "password": "admin",
        "submission_path": "submission_files/copied.zip"
    },
    {
        "name": "Coke Zero",
        "email": "cc33cc@brocku.ca",
        "password": "admin",
        "submission_path": "submission_files/changed.zip"
    },
]


def run() -> str | None:
    """Create course, assignment, submit each user's zip, log assignment key. Returns key or None on failure."""
    script_dir = Path(__file__).resolve().parent
    lines = [f"=== {TEST_PROJECT} ===\n"]

    try:
        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        lines.append("Login: OK\n")
    except (RuntimeError, requests.RequestException) as e:
        lines.append(f"Login FAILED: {e}\n")
        test_log(TEST_PROJECT, "".join(lines))
        return None

    # Create course
    try:
        r = requests.post(f"{BASE_URL}/instructor/courses", json=course_config, headers=headers, timeout=10)
        r.raise_for_status()
        course = r.json()
        course_id = course["id"]
        lines.append(f"Course created: {course_id}\n")
    except requests.RequestException as e:
        lines.append(f"Create course FAILED: {e}\n")
        if hasattr(e, "response") and e.response is not None:
            lines.append(f"Response: {e.response.text}\n")
        test_log(TEST_PROJECT, "".join(lines))
        return None

    # Create assignment
    body = {"courseId": course_id, **assignment_config}
    try:
        r = requests.post(f"{BASE_URL}/instructor/assignments", json=body, headers=headers, timeout=10)
        r.raise_for_status()
        assignment = r.json()
        assignment_id = assignment["id"]
        assignment_key = assignment["assignmentKey"]
        lines.append(f"Assignment created: {assignment_id}\n")
        lines.append(f"Assignment key: {assignment_key}\n")
    except requests.RequestException as e:
        lines.append(f"Create assignment FAILED: {e}\n")
        if hasattr(e, "response") and e.response is not None:
            lines.append(f"Response: {e.response.text}\n")
        test_log(TEST_PROJECT, "".join(lines))
        return None

    # Submit each user's zip
    lines.append("\n--- Submissions ---\n")
    for u in users_config:
        name = u.get("name", "")
        email = u.get("email", "")
        submission_path = u.get("submission_path", "")
        path = (script_dir / submission_path).resolve()
        if not path.exists():
            lines.append(f"  SKIP {email}: file not found {path}\n")
            continue
        try:
            with open(path, "rb") as f:
                files = {"zipFile": (path.name, f, "application/zip")}
                data = {"assignmentKey": assignment_key, "studentIdentifier": email, "studentName": name}
                r = requests.post(f"{BASE_URL}/public/submissions", data=data, files=files, timeout=30)
            r.raise_for_status()
            lines.append(f"  OK {email}\n")
        except requests.RequestException as e:
            lines.append(f"  FAIL {email}: {e}\n")

    lines.append(f"\nAssignment key: {assignment_key}\n")
    log_path = test_log(TEST_PROJECT, "".join(lines))
    print(f"Test log saved to: {log_path}")
    print(f"Assignment key: {assignment_key}")
    return assignment_key


"""
create new assignment
user user config to submit files
crete log file using log.py, log the obtained assignment key
return assignment key
"""

if __name__ == "__main__":
    run()
