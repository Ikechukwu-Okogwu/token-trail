"""Setup assignment: create course, assignment, submit zips, log assignment key."""
import io
import sys
import zipfile
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent.parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

import requests

from app.analysis.localtest.get_access_token import get_access_token
from app.analysis.localtest.log import test_log

BASE_URL = "http://localhost:8000/api"
TEST_PROJECT = "setup_assignment"

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

def create_assignment(
    course_id: str,
    assignment_config: dict,
    headers: dict,
    base_url: str = BASE_URL,
) -> str:
    """Create an assignment in the specified course. Returns assignment_id."""
    body = {"courseId": course_id, **assignment_config}
    r = requests.post(f"{base_url}/instructor/assignments", json=body, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()["id"]


def submit_to_assignment(
    assignment_id: str,
    zip_bytesio,
    student_identifier: str,
    student_name: str,
    headers: dict,
    base_url: str = BASE_URL,
) -> None:
    """Submit a zip (BytesIO) to the specified assignment. Raises on failure."""
    r = requests.get(f"{base_url}/instructor/assignments/{assignment_id}", headers=headers, timeout=10)
    r.raise_for_status()
    assignment_key = r.json()["assignmentKey"]
    data = {
        "assignmentKey": assignment_key,
        "studentIdentifier": student_identifier,
        "studentName": student_name,
    }
    files = {"zipFile": ("submission.zip", zip_bytesio, "application/zip")}
    r = requests.post(f"{base_url}/public/submissions", data=data, files=files, timeout=30)
    r.raise_for_status()

COURSE_ID = "69ba0363a906062a119e9b6c"
SETUP_DATASET_PROJECT = "setup_dataset"


def setup_dataset(dataset_path: Path) -> str | None:
    """
    dataset_path is absolute path to the dataset zip file
    1. get access token
    2. read the dataset zip file
    3. find all zip files in the dataset, load them into memory as BytesIO
    4. use assignment_config in this file to create assignment(temporarily.)
    5. create assignment under the temporarily hardcoded course id.
    6. submit all zip files to the assignment
    7. log information using log.py
    8. return the assignment key

    course_id: 69ba0363a906062a119e9b6c
    """
    lines = [f"=== {SETUP_DATASET_PROJECT} ===\n"]
    lines.append(f"Dataset: {dataset_path}\n")

    try:
        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        lines.append("Login: OK\n")
    except (RuntimeError, requests.RequestException) as e:
        lines.append(f"Login FAILED: {e}\n")
        test_log(SETUP_DATASET_PROJECT, "".join(lines))
        return None

    # Load dataset zip and find all inner zip files
    try:
        with zipfile.ZipFile(dataset_path, "r") as zf:
            zip_entries = [n for n in zf.namelist() if n.lower().endswith(".zip")]
            zip_entries.sort()
            zip_buffers: list[tuple[str, io.BytesIO]] = []
            for name in zip_entries:
                data = zf.read(name)
                stem = Path(name).stem
                zip_buffers.append((stem, io.BytesIO(data)))
        lines.append(f"Found {len(zip_buffers)} zip files in dataset\n")
    except (zipfile.BadZipFile, OSError) as e:
        lines.append(f"Failed to read dataset zip: {e}\n")
        test_log(SETUP_DATASET_PROJECT, "".join(lines))
        return None

    # Create assignment
    try:
        assignment_id = create_assignment(COURSE_ID, assignment_config, headers)
        r = requests.get(f"{BASE_URL}/instructor/assignments/{assignment_id}", headers=headers, timeout=10)
        r.raise_for_status()
        assignment_key = r.json()["assignmentKey"]
        lines.append(f"Assignment created: {assignment_id}\n")
        lines.append(f"Assignment key: {assignment_key}\n")
    except requests.RequestException as e:
        lines.append(f"Create assignment FAILED: {e}\n")
        if hasattr(e, "response") and e.response is not None:
            lines.append(f"Response: {e.response.text}\n")
        test_log(SETUP_DATASET_PROJECT, "".join(lines))
        return None

    # Submit each zip
    lines.append("\n--- Submissions ---\n")
    for stem, buf in zip_buffers:
        try:
            buf.seek(0)
            submit_to_assignment(assignment_id, buf, stem, stem, headers)
            lines.append(f"  OK {stem}\n")
        except requests.RequestException as e:
            lines.append(f"  FAIL {stem}: {e}\n")

    lines.append(f"\nAssignment key: {assignment_key}\n")
    test_log(SETUP_DATASET_PROJECT, "".join(lines))
    return assignment_key

course_config = {
    "name": "COSC 1P02", 
    "term": "Winter 2026", 
}



# Submissions: POST /api/public/submissions (assignmentKey filled by script)
users_config: list[dict[str, str]] = [
    {
        "name": "John Doe",
        "email": "aa11aa@brocku.ca",
        "password": "admin",
        "submission_path": "submission_files/Alice.zip"
    },
    {
        "name": "Extra Spice",
        "email": "bb22bb@brocku.ca",
        "password": "admin",
        "submission_path": "submission_files/Bob.zip"
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
    try:
        assignment_id = create_assignment(course_id, assignment_config, headers)
        r = requests.get(f"{BASE_URL}/instructor/assignments/{assignment_id}", headers=headers, timeout=10)
        r.raise_for_status()
        assignment_key = r.json()["assignmentKey"]
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
                zip_bytesio = io.BytesIO(f.read())
            submit_to_assignment(assignment_id, zip_bytesio, email, name, headers)
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

def test_setup_and_run_while_loop_vs_for_loop() -> None:
    # path = "D:\work\4P02\Project\token-trail\backend\app\analysis\localtest\datasets\use_while_loop_instead_of_for_loop_JAVA.zip"
    # setup_dataset(path)
    pass

if __name__ == "__main__":
    run()
    # test_setup_and_run_while_loop_vs_for_loop()
