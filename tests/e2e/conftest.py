"""E2E test fixtures for Token Trail API contract tests."""
from datetime import datetime, timedelta, timezone
import os
import zipfile
from pathlib import Path
from uuid import uuid4

import pytest
import requests


def _future_iso(days_ahead: int) -> str:
    """Return a UTC ISO timestamp in the future for time-stable tests."""
    return (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()


def _get_base_url() -> str:
    return os.environ.get("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the API (no /api suffix; paths add it)."""
    url = _get_base_url()
    # Fail fast if unreachable
    try:
        r = requests.get(f"{url}/api/health", timeout=5)
        r.raise_for_status()
    except requests.RequestException as e:
        pytest.skip(f"API unreachable at {url}: {e}")
    return url


@pytest.fixture
def auth_headers(base_url: str) -> dict:
    """
    Sign up a new user and return Authorization headers.
    Uses unique email per test for independence.
    """
    email = f"test-{uuid4()}@example.com"
    r = requests.post(
        f"{base_url}/api/auth/signup",
        json={"name": "Test User", "email": email, "password": "secret123"},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    token = data.get("accessToken")
    assert token, "Expected accessToken in signup response"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_zip(tmp_path: Path) -> Path:
    """Create a minimal valid ZIP with one .java file."""
    java_content = 'public class Hello { public static void main(String[] args) {} }'
    zip_path = tmp_path / "submission.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Hello.java", java_content)
    return zip_path


@pytest.fixture
def happy_path_setup(base_url: str, auth_headers: dict, test_zip: Path) -> dict:
    """
    Create course, assignment, validate key, upload submission, queue run.
    Returns dict with courseId, assignmentId, assignmentKey, runId.
    """
    # Create course
    r = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "E2E Test Course", "term": "Fall 2025"},
        timeout=10,
    )
    r.raise_for_status()
    course = r.json()
    course_id = course["id"]

    # Create assignment
    due_date = _future_iso(30)
    key_expiry = _future_iso(31)
    r = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": course_id,
            "title": "HW1",
            "language": "java",
            "isOpen": True,
            "dueDate": due_date,
            "keyExpiry": key_expiry,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    r.raise_for_status()
    assignment = r.json()
    assignment_id = assignment["id"]
    assignment_key = assignment["assignmentKey"]

    # Upload submission
    with open(test_zip, "rb") as f:
        r = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": assignment_key,
                "studentIdentifier": "student1@test.edu",
                "studentName": "Test Student",
            },
            files={"zipFile": ("submission.zip", f, "application/zip")},
            timeout=30,
        )
    r.raise_for_status()

    # Queue analysis run
    r = requests.post(
        f"{base_url}/api/instructor/assignments/{assignment_id}/analysis-runs",
        headers=auth_headers,
        timeout=10,
    )
    r.raise_for_status()
    run = r.json()
    run_id = run["runId"]

    return {
        "courseId": course_id,
        "assignmentId": assignment_id,
        "assignmentKey": assignment_key,
        "runId": run_id,
        "auth_headers": auth_headers,
    }
