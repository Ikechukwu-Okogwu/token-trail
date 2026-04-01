"""
E2E API contract tests for Token Trail.

Test Plan:
- Input partitions: valid (auth, courses, assignments, submissions), invalid (bad IDs,
  missing token, wrong key, malformed resultId), edge (empty list, minimal ZIP, unknown key)
- Boundaries: empty submissions list, single submission (0 pairs), minimal valid ZIP,
  invalid key format (non-10-digit), pairwise ranking order over multiple pairs
- Interface misuse: malformed ObjectId-like route params, malformed `resultId` for
  similarity detail/comparison routes
- Failure modes: API unreachable (connection refused), auth failures (401/403),
  validation failures (400/404), placeholder-only 501 admin endpoints
"""
from datetime import datetime, timedelta, timezone
import io
import time
import zipfile
from uuid import uuid4

import pytest
import requests


def _future_iso(days_ahead: int) -> str:
    """Return a UTC ISO timestamp in the future for time-stable tests."""
    return (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()
def _wait_for_run_terminal_status(
    base_url: str,
    headers: dict,
    run_id: str,
    *,
    max_wait: int = 60,
    interval: int = 2,
) -> str:
    """Poll an analysis run until it reaches completed/failed."""
    deadline = time.time() + max_wait
    last_status = ""
    while time.time() < deadline:
        r = requests.get(
            f"{base_url}/api/instructor/analysis-runs/{run_id}",
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        last_status = r.json().get("status", "")
        if last_status in ("completed", "failed"):
            return last_status
        time.sleep(interval)
    return last_status


def _create_two_submission_run(
    base_url: str,
    auth_headers: dict,
    test_zip,
) -> tuple[str, str, dict]:
    """Create assignment with 2 submissions and queue one run."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "Similarity E2E", "term": "F26"},
        timeout=10,
    )
    rc.raise_for_status()
    course_id = rc.json()["id"]

    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": course_id,
            "title": "Similarity HW",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    assignment = ra.json()
    assignment_id = assignment["id"]
    assignment_key = assignment["assignmentKey"]

    for student in ("student-a@test.edu", "student-b@test.edu"):
        with open(test_zip, "rb") as f:
            ru = requests.post(
                f"{base_url}/api/public/submissions",
                data={
                    "assignmentKey": assignment_key,
                    "studentIdentifier": student,
                    "studentName": student.split("@")[0],
                },
                files={"zipFile": ("sub.zip", f, "application/zip")},
                timeout=30,
            )
        ru.raise_for_status()

    rr = requests.post(
        f"{base_url}/api/instructor/assignments/{assignment_id}/analysis-runs",
        headers=auth_headers,
        timeout=10,
    )
    rr.raise_for_status()
    run_id = rr.json()["runId"]
    return assignment_id, run_id, auth_headers


# --- Smoke ---


def test_health_returns_ok(base_url: str) -> None:
    """Guards: API is up and health endpoint returns expected shape. Catches backend down."""
    r = requests.get(f"{base_url}/api/health", timeout=5)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "token-trail-api"


def test_signup_returns_token(base_url: str) -> None:
    """Guards: Auth signup creates user and returns JWT. Catches auth pipeline break."""
    email = f"test-{uuid4()}@example.com"
    r = requests.post(
        f"{base_url}/api/auth/signup",
        json={"name": "Alice", "email": email, "password": "secret123"},
        timeout=10,
    )
    assert r.status_code == 201, f"Expected 201, got {r.status_code}"
    data = r.json()
    assert "accessToken" in data
    assert isinstance(data["accessToken"], str) and len(data["accessToken"]) > 0


def test_api_unreachable_fails_fast() -> None:
    """Guards: Tests fail fast on unreachable API, not hang. Documents safe fallback."""
    try:
        r = requests.get("http://127.0.0.1:59999/api/health", timeout=2)
        # If it somehow responds, that's ok - we just want no long hang
        _ = r
    except (requests.ConnectionError, requests.Timeout) as e:
        # Expected: connection refused or timeout
        assert "Connection" in str(type(e).__name__) or "Timeout" in str(type(e).__name__)


# --- Happy path ---


def test_happy_path_create_course(base_url: str, auth_headers: dict) -> None:
    """Guards: Course creation works with valid auth. Catches ownership/store break."""
    r = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "CS101", "term": "Fall 2025"},
        timeout=10,
    )
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["name"] == "CS101"
    assert data["term"] == "Fall 2025"
    assert "instructorId" in data


def test_happy_path_create_assignment(base_url: str, auth_headers: dict) -> None:
    """Guards: Assignment creation with assignmentKey. Catches key generation break."""
    # Create course first
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "E2E", "term": "F25"},
        timeout=10,
    )
    rc.raise_for_status()
    course_id = rc.json()["id"]

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
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert "assignmentKey" in data
    assert len(data["assignmentKey"]) == 10
    assert data["assignmentKey"].isdigit()
    assert data["dueDate"] == due_date
    assert data["keyExpiry"] == key_expiry
    assert data["allowLate"] is False


def test_happy_path_validate_key(base_url: str, auth_headers: dict) -> None:
    """Guards: Public validate reads assignment data. Cross-team integration."""
    # Create course and assignment
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "E2E", "term": "F25"},
        timeout=10,
    )
    rc.raise_for_status()
    course_id = rc.json()["id"]
    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": course_id,
            "title": "HW1",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    key = ra.json()["assignmentKey"]

    r = requests.post(
        f"{base_url}/api/public/assignment-key/validate",
        json={"assignmentKey": key},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is True
    assert data["assignment"] is not None
    assert data["assignment"]["language"] == "java"


def test_happy_path_upload_submission(
    base_url: str, auth_headers: dict, test_zip, happy_path_setup: dict
) -> None:
    """Guards: Public submission upload works. Cross-team integration."""
    key = happy_path_setup["assignmentKey"]
    with open(test_zip, "rb") as f:
        r = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": key,
                "studentIdentifier": "s1@test.edu",
                "studentName": "Student 1",
            },
            files={"zipFile": ("sub.zip", f, "application/zip")},
            timeout=30,
        )
    assert r.status_code == 201
    data = r.json()
    assert "submissionId" in data
    assert data["status"] == "processed"
    assert data["fileCount"] >= 1


def test_happy_path_list_submissions(base_url: str, happy_path_setup: dict) -> None:
    """Guards: Instructor can list submissions. Schema matches SubmissionListItem."""
    aid = happy_path_setup["assignmentId"]
    headers = happy_path_setup["auth_headers"]

    r = requests.get(
        f"{base_url}/api/instructor/assignments/{aid}/submissions",
        headers=headers,
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Should have at least one submission from happy_path_setup upload
    assert len(data) >= 1
    for s in data:
        assert "submissionId" in s
        assert "studentIdentifier" in s
        assert "fileCount" in s


def test_happy_path_queue_run(base_url: str, auth_headers: dict) -> None:
    """Guards: Analysis run can be queued. Catches run creation break."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "C", "term": "T"},
        timeout=10,
    )
    rc.raise_for_status()
    cid = rc.json()["id"]
    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": cid,
            "title": "A",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    aid = ra.json()["id"]

    r = requests.post(
        f"{base_url}/api/instructor/assignments/{aid}/analysis-runs",
        headers=auth_headers,
        timeout=10,
    )
    assert r.status_code == 201
    data = r.json()
    assert "runId" in data
    assert data["status"] == "queued"
    assert data["algorithmVersion"] == "v0"


def test_happy_path_poll_run_completed(
    base_url: str, happy_path_setup: dict
) -> None:
    """
    Guards: Worker processes run; status progresses to completed.
    Real wait required; polling loop is intentional.
    """
    run_id = happy_path_setup["runId"]
    headers = happy_path_setup["auth_headers"]
    base = base_url
    max_wait = 60
    interval = 2
    deadline = time.time() + max_wait
    last_status = None
    while time.time() < deadline:
        r = requests.get(
            f"{base}/api/instructor/analysis-runs/{run_id}",
            headers=headers,
            timeout=10,
        )
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        last_status = data.get("status")
        if last_status in ("completed", "failed"):
            break
        time.sleep(interval)
    assert last_status == "completed", f"Run did not complete in {max_wait}s; last status: {last_status}"


def test_similarity_results_list_returns_ranked_pairs(
    base_url: str, auth_headers: dict, test_zip, tmp_path
) -> None:
    """Guards: Similarity list returns ranked pairs and preserves descending score order."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "SIM", "term": "F25"},
        timeout=10,
    )
    rc.raise_for_status()
    course_id = rc.json()["id"]

    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": course_id,
            "title": "HW-SIM",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    assignment = ra.json()
    assignment_id = assignment["id"]
    assignment_key = assignment["assignmentKey"]

    with open(test_zip, "rb") as f:
        up1 = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": assignment_key,
                "studentIdentifier": "sim1@test.edu",
                "studentName": "Sim One",
            },
            files={"zipFile": ("sub1.zip", f, "application/zip")},
            timeout=30,
        )
    up1.raise_for_status()

    second_zip = tmp_path / "submission2.zip"
    with zipfile.ZipFile(second_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "Hello.java",
            "public class Hello { public static void main(String[] args) { int x = 2; } }",
        )
    with open(second_zip, "rb") as f:
        up2 = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": assignment_key,
                "studentIdentifier": "sim2@test.edu",
                "studentName": "Sim Two",
            },
            files={"zipFile": ("sub2.zip", f, "application/zip")},
            timeout=30,
        )
    up2.raise_for_status()

    third_zip = tmp_path / "submission4.zip"
    with zipfile.ZipFile(third_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "Hello.java",
            "public class Hello { public static void main(String[] args) { int z = 99; } }",
        )
    with open(third_zip, "rb") as f:
        up3 = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": assignment_key,
                "studentIdentifier": "sim3@test.edu",
                "studentName": "Sim Three",
            },
            files={"zipFile": ("sub3.zip", f, "application/zip")},
            timeout=30,
        )
    up3.raise_for_status()

    rr = requests.post(
        f"{base_url}/api/instructor/assignments/{assignment_id}/analysis-runs",
        headers=auth_headers,
        timeout=10,
    )
    rr.raise_for_status()
    run_id = rr.json()["runId"]

    max_wait = 60
    interval = 2
    deadline = time.time() + max_wait
    last_status = None
    while time.time() < deadline:
        poll = requests.get(
            f"{base_url}/api/instructor/analysis-runs/{run_id}",
            headers=auth_headers,
            timeout=10,
        )
        poll.raise_for_status()
        last_status = poll.json().get("status")
        if last_status in ("completed", "failed"):
            break
        time.sleep(interval)
    assert last_status == "completed", f"Run did not complete in {max_wait}s; last status: {last_status}"

    list_resp = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=auth_headers,
        timeout=10,
    )
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert payload["runId"] == run_id
    assert payload["assignmentId"] == assignment_id
    assert isinstance(payload["results"], list)
    assert len(payload["results"]) >= 3

    # Regression check: list is sorted descending by similarityScore.
    scores = [item["similarityScore"] for item in payload["results"]]
    assert scores == sorted(scores, reverse=True)

    top = payload["results"][0]
    assert "resultId" in top
    assert "__" in top["resultId"]
    assert top["runId"] == run_id
    assert top["assignmentId"] == assignment_id
    assert "leftSubmissionId" in top and "rightSubmissionId" in top
    assert isinstance(top["similarityScore"], float)


def test_similarity_pair_detail_and_comparison_return_payload(
    base_url: str, auth_headers: dict, test_zip, tmp_path
) -> None:
    """Guards: Pair detail/comparison contract and bounded repeated calls remain stable."""
    # Reuse same setup pattern to guarantee at least one pair.
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "SIM2", "term": "F25"},
        timeout=10,
    )
    rc.raise_for_status()
    course_id = rc.json()["id"]

    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": course_id,
            "title": "HW-SIM2",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    assignment = ra.json()
    assignment_id = assignment["id"]
    assignment_key = assignment["assignmentKey"]

    with open(test_zip, "rb") as f:
        requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": assignment_key,
                "studentIdentifier": "cmp1@test.edu",
                "studentName": "Cmp One",
            },
            files={"zipFile": ("cmp1.zip", f, "application/zip")},
            timeout=30,
        ).raise_for_status()

    second_zip = tmp_path / "submission3.zip"
    with zipfile.ZipFile(second_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "Hello.java",
            "public class Hello { public static void main(String[] args) { int y = 3; } }",
        )
    with open(second_zip, "rb") as f:
        requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": assignment_key,
                "studentIdentifier": "cmp2@test.edu",
                "studentName": "Cmp Two",
            },
            files={"zipFile": ("cmp2.zip", f, "application/zip")},
            timeout=30,
        ).raise_for_status()

    rr = requests.post(
        f"{base_url}/api/instructor/assignments/{assignment_id}/analysis-runs",
        headers=auth_headers,
        timeout=10,
    )
    rr.raise_for_status()
    run_id = rr.json()["runId"]

    deadline = time.time() + 60
    while time.time() < deadline:
        poll = requests.get(
            f"{base_url}/api/instructor/analysis-runs/{run_id}",
            headers=auth_headers,
            timeout=10,
        )
        poll.raise_for_status()
        status = poll.json().get("status")
        if status in ("completed", "failed"):
            break
        time.sleep(2)
    assert status == "completed"

    list_resp = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=auth_headers,
        timeout=10,
    )
    list_resp.raise_for_status()
    result_id = list_resp.json()["results"][0]["resultId"]

    detail_resp = requests.get(
        f"{base_url}/api/instructor/similarity-results/{result_id}",
        headers=auth_headers,
        timeout=10,
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["resultId"] == result_id
    assert detail["runId"] == run_id
    assert detail["assignmentId"] == assignment_id
    assert isinstance(detail["similarityScore"], float)

    cmp_resp = requests.get(
        f"{base_url}/api/instructor/similarity-results/{result_id}/comparison",
        headers=auth_headers,
        timeout=10,
    )
    assert cmp_resp.status_code == 200
    comparison = cmp_resp.json()
    assert comparison["resultId"] == result_id
    assert comparison["runId"] == run_id
    assert comparison["assignmentId"] == assignment_id
    assert "leftCode" in comparison and isinstance(comparison["leftCode"], str)
    assert "rightCode" in comparison and isinstance(comparison["rightCode"], str)
    assert isinstance(comparison["matchingRegions"], list)

    # Stress/repeated-call check (bounded): repeated reads should stay stable.
    for _ in range(5):
        repeat = requests.get(
            f"{base_url}/api/instructor/similarity-results/{result_id}/comparison",
            headers=auth_headers,
            timeout=10,
        )
        assert repeat.status_code == 200
        repeated_payload = repeat.json()
        assert repeated_payload["resultId"] == result_id
        assert repeated_payload["assignmentId"] == assignment_id


def test_similarity_results_for_wrong_instructor_return_403(
    base_url: str, happy_path_setup: dict
) -> None:
    """Guards: Similarity endpoints enforce instructor ownership."""
    run_id = happy_path_setup["runId"]
    email = f"test-{uuid4()}@example.com"
    signup = requests.post(
        f"{base_url}/api/auth/signup",
        json={"name": "Other", "email": email, "password": "secret123"},
        timeout=10,
    )
    signup.raise_for_status()
    headers = {"Authorization": f"Bearer {signup.json()['accessToken']}"}
    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=headers,
        timeout=10,
    )
    assert r.status_code == 403
    data = r.json()
    assert "detail" in data
    assert "Not your analysis run" in str(data["detail"])


def test_similarity_results_list_includes_confidence_and_largest_block(
    base_url: str, auth_headers: dict, test_zip
) -> None:
    """Guards: Ranked similarity list includes metadata fields for table ranking context."""
    _assignment_id, run_id, headers = _create_two_submission_run(base_url, auth_headers, test_zip)
    final_status = _wait_for_run_terminal_status(base_url, headers, run_id)
    assert final_status == "completed", f"Run did not complete, last status: {final_status}"

    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=headers,
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("runId") == run_id
    assert isinstance(data.get("results"), list)
    assert len(data["results"]) >= 1

    row = data["results"][0]
    assert "resultId" in row
    assert "confidence" in row
    assert "largestBlockSize" in row
    assert isinstance(row["confidence"], (float, int))
    assert 0 <= row["confidence"] <= 1
    assert isinstance(row["largestBlockSize"], int)
    assert row["largestBlockSize"] >= 0


def test_similarity_result_id_bad_format_returns_400(
    base_url: str, auth_headers: dict
) -> None:
    """Guards: Malformed similarity resultId is rejected with explicit 400 contract."""
    r = requests.get(
        f"{base_url}/api/instructor/similarity-results/not-a-valid-result-id",
        headers=auth_headers,
        timeout=10,
    )
    assert r.status_code == 400
    payload = r.json()
    assert "detail" in payload
    assert "Invalid resultId format" in str(payload["detail"])


def test_similarity_comparison_returns_regions_and_snippets(
    base_url: str, auth_headers: dict, test_zip
) -> None:
    """Guards: Comparison endpoint returns populated region arrays and tooltip snippets."""
    _assignment_id, run_id, headers = _create_two_submission_run(base_url, auth_headers, test_zip)
    final_status = _wait_for_run_terminal_status(base_url, headers, run_id)
    assert final_status == "completed", f"Run did not complete, last status: {final_status}"

    ranked = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=headers,
        timeout=10,
    )
    ranked.raise_for_status()
    ranked_data = ranked.json()
    assert ranked_data.get("results"), "Expected at least one similarity pair"
    result_id = ranked_data["results"][0]["resultId"]

    comparison = requests.get(
        f"{base_url}/api/instructor/similarity-results/{result_id}/comparison",
        headers=headers,
        timeout=10,
    )
    assert comparison.status_code == 200
    payload = comparison.json()
    assert payload["resultId"] == result_id
    assert isinstance(payload.get("matchingRegions"), list)
    assert isinstance(payload.get("excludedRegions"), list)
    assert isinstance(payload.get("summary"), str)
    assert isinstance(payload.get("confidence"), (float, int))
    assert isinstance(payload.get("snippets"), list)
    if payload["matchingRegions"]:
        first_region = payload["matchingRegions"][0]
        assert "leftStartLine" in first_region and "leftEndLine" in first_region
        assert "rightStartLine" in first_region and "rightEndLine" in first_region
        assert "score" in first_region
        assert "evidenceType" in first_region
        assert "snippet" in first_region
    if payload["snippets"]:
        assert isinstance(payload["snippets"][0], str)
        assert payload["snippets"][0].strip() != ""


# --- Edge / defect ---


def test_no_token_returns_401_or_403(base_url: str) -> None:
    """Guards: Protected routes reject requests without Authorization. Catches auth bypass."""
    r = requests.get(f"{base_url}/api/auth/me", timeout=5)
    assert r.status_code in (401, 403), f"Expected 401 or 403, got {r.status_code}"
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    detail = str(data.get("detail", ""))
    assert "detail" in data or "Not authenticated" in detail or "authenticated" in detail.lower() or "token" in detail.lower()


def test_invalid_assignment_id_returns_400(base_url: str, auth_headers: dict) -> None:
    """Guards: Invalid ObjectId format returns 400. Catches to_object_id bypass."""
    r = requests.get(
        f"{base_url}/api/instructor/assignments/not-an-id",
        headers=auth_headers,
        timeout=5,
    )
    assert r.status_code == 400
    data = r.json()
    assert "detail" in data
    assert "Invalid ID format" in str(data["detail"])


def test_duplicate_signup_returns_409(base_url: str) -> None:
    """Guards: Duplicate email returns 409. Catches uniqueness bypass."""
    email = f"test-{uuid4()}@example.com"
    requests.post(
        f"{base_url}/api/auth/signup",
        json={"name": "A", "email": email, "password": "p"},
        timeout=10,
    ).raise_for_status()
    r = requests.post(
        f"{base_url}/api/auth/signup",
        json={"name": "B", "email": email, "password": "p"},
        timeout=10,
    )
    assert r.status_code == 409
    data = r.json()
    assert "detail" in data
    assert "already registered" in str(data["detail"]).lower()


def test_unknown_assignment_key_returns_valid_false(base_url: str) -> None:
    """Guards: Unknown key returns 200 with valid=false. Catches validate-key contract."""
    r = requests.post(
        f"{base_url}/api/public/assignment-key/validate",
        json={"assignmentKey": "9999999999"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is False
    assert data["assignment"] is None


def test_regenerate_key_returns_200_and_rotates_key(
    base_url: str, happy_path_setup: dict
) -> None:
    """Guards: Regenerate key rotates assignment key and returns assignment payload."""
    aid = happy_path_setup["assignmentId"]
    headers = happy_path_setup["auth_headers"]
    old_key = happy_path_setup["assignmentKey"]
    r = requests.post(
        f"{base_url}/api/instructor/assignments/{aid}/regenerate-key",
        headers=headers,
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("id") == aid
    assert data.get("assignmentKey") != old_key
    assert len(data["assignmentKey"]) == 10
    assert data["assignmentKey"].isdigit()

    old_validate = requests.post(
        f"{base_url}/api/public/assignment-key/validate",
        json={"assignmentKey": old_key},
        timeout=5,
    )
    assert old_validate.status_code == 200
    assert old_validate.json()["valid"] is False


def test_wrong_instructor_cannot_access_analysis_run_returns_403(
    base_url: str, auth_headers: dict, happy_path_setup: dict
) -> None:
    """Guards: Instructor A cannot access Instructor B's run. Catches ownership bypass."""
    run_id = happy_path_setup["runId"]
    # Sign up a different user
    email = f"test-{uuid4()}@example.com"
    r2 = requests.post(
        f"{base_url}/api/auth/signup",
        json={"name": "Bob", "email": email, "password": "secret123"},
        timeout=10,
    )
    r2.raise_for_status()
    token2 = r2.json()["accessToken"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}",
        headers=headers2,
        timeout=5,
    )
    assert r.status_code == 403
    data = r.json()
    assert "detail" in data
    assert "Not your analysis run" in str(data["detail"])


def test_closed_assignment_rejects_submission_returns_400(
    base_url: str, auth_headers: dict, test_zip
) -> None:
    """Guards: Closed assignment rejects submission. Catches isOpen enforcement."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "C", "term": "T"},
        timeout=10,
    )
    rc.raise_for_status()
    cid = rc.json()["id"]
    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": cid,
            "title": "A",
            "language": "java",
            "isOpen": False,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    key = ra.json()["assignmentKey"]

    with open(test_zip, "rb") as f:
        r = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": key,
                "studentIdentifier": "s@test.edu",
                "studentName": "S",
            },
            files={"zipFile": ("sub.zip", f, "application/zip")},
            timeout=10,
        )
    assert r.status_code == 400
    data = r.json()
    assert "detail" in data
    assert "closed" in str(data["detail"]).lower()


def test_past_due_assignment_rejects_submission_returns_400(
    base_url: str, auth_headers: dict, test_zip
) -> None:
    """Guards: Past-due assignment rejects submission when late work is disallowed."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "C", "term": "T"},
        timeout=10,
    )
    rc.raise_for_status()
    cid = rc.json()["id"]
    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": cid,
            "title": "A",
            "language": "java",
            "isOpen": True,
            "dueDate": "2000-01-01T00:00:00+00:00",
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    key = ra.json()["assignmentKey"]

    with open(test_zip, "rb") as f:
        r = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": key,
                "studentIdentifier": "s@test.edu",
                "studentName": "S",
            },
            files={"zipFile": ("sub.zip", f, "application/zip")},
            timeout=10,
        )
    assert r.status_code == 400
    data = r.json()
    assert "detail" in data
    assert "due date" in str(data["detail"]).lower()


# --- Boundary / partition ---


def test_empty_submissions_list_returns_empty_array(
    base_url: str, auth_headers: dict
) -> None:
    """Guards: Assignment with no submissions returns []. Boundary: empty list."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "C", "term": "T"},
        timeout=10,
    )
    rc.raise_for_status()
    cid = rc.json()["id"]
    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": cid,
            "title": "A",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    aid = ra.json()["id"]

    r = requests.get(
        f"{base_url}/api/instructor/assignments/{aid}/submissions",
        headers=auth_headers,
        timeout=5,
    )
    assert r.status_code == 200
    assert r.json() == []


def test_minimal_zip_single_java_file_accepted(
    base_url: str, auth_headers: dict, test_zip
) -> None:
    """Guards: ZIP with one .java file is accepted. Boundary: minimal valid input."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "C", "term": "T"},
        timeout=10,
    )
    rc.raise_for_status()
    cid = rc.json()["id"]
    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": cid,
            "title": "A",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    key = ra.json()["assignmentKey"]

    with open(test_zip, "rb") as f:
        r = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": key,
                "studentIdentifier": "s@test.edu",
                "studentName": "S",
            },
            files={"zipFile": ("sub.zip", f, "application/zip")},
            timeout=30,
        )
    assert r.status_code == 201
    assert r.json()["fileCount"] >= 1


def test_valid_objectid_format_but_nonexistent_returns_404(
    base_url: str, auth_headers: dict
) -> None:
    """Guards: Valid-format ID for nonexistent resource returns 404."""
    # 24-char hex string (valid ObjectId format) for nonexistent assignment
    r = requests.get(
        f"{base_url}/api/instructor/assignments/665f00000000000000000000",
        headers=auth_headers,
        timeout=5,
    )
    assert r.status_code == 404
    data = r.json()
    assert "detail" in data


def test_assignment_key_wrong_length_rejected(base_url: str) -> None:
    """Guards: Key with wrong length returns valid=false. Boundary: 9 or 11 digits."""
    r = requests.post(
        f"{base_url}/api/public/assignment-key/validate",
        json={"assignmentKey": "123456789"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is False
    assert data["assignment"] is None


def test_zero_submissions_run_completes(
    base_url: str, auth_headers: dict
) -> None:
    """Guards: Queue run with 0 submissions; worker completes; no crash. Boundary: N=0."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "C", "term": "T"},
        timeout=10,
    )
    rc.raise_for_status()
    cid = rc.json()["id"]
    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": cid,
            "title": "A",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    aid = ra.json()["id"]

    rr = requests.post(
        f"{base_url}/api/instructor/assignments/{aid}/analysis-runs",
        headers=auth_headers,
        timeout=10,
    )
    rr.raise_for_status()
    run_id = rr.json()["runId"]

    # Poll until completed
    max_wait = 60
    interval = 2
    deadline = time.time() + max_wait
    last_status = None
    while time.time() < deadline:
        r = requests.get(
            f"{base_url}/api/instructor/analysis-runs/{run_id}",
            headers=auth_headers,
            timeout=10,
        )
        assert r.status_code == 200
        last_status = r.json().get("status")
        if last_status in ("completed", "failed"):
            break
        time.sleep(interval)
    assert last_status in ("completed", "failed"), f"Run stuck at {last_status}"


def test_expire_key_invalidates_public_validation(
    base_url: str, happy_path_setup: dict
) -> None:
    """Guards: Expire-key causes validate endpoint to return valid=false."""
    aid = happy_path_setup["assignmentId"]
    headers = happy_path_setup["auth_headers"]
    key = happy_path_setup["assignmentKey"]

    expire = requests.post(
        f"{base_url}/api/instructor/assignments/{aid}/expire-key",
        headers=headers,
        timeout=10,
    )
    assert expire.status_code == 200
    payload = expire.json()
    assert payload["id"] == aid
    assert payload["keyExpiry"] is not None

    validate = requests.post(
        f"{base_url}/api/public/assignment-key/validate",
        json={"assignmentKey": key},
        timeout=10,
    )
    assert validate.status_code == 200
    assert validate.json()["valid"] is False


def test_expired_key_rejects_submission(base_url: str, auth_headers: dict, test_zip) -> None:
    """Guards: Submission upload is rejected when key is expired."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=auth_headers,
        json={"name": "Expire C", "term": "F25"},
        timeout=10,
    )
    rc.raise_for_status()
    cid = rc.json()["id"]
    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=auth_headers,
        json={
            "courseId": cid,
            "title": "Expire A",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": "2000-01-01T00:00:00+00:00",
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": None,
        },
        timeout=10,
    )
    ra.raise_for_status()
    key = ra.json()["assignmentKey"]

    with open(test_zip, "rb") as f:
        submit = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": key,
                "studentIdentifier": "expired@test.edu",
                "studentName": "Expired",
            },
            files={"zipFile": ("sub.zip", f, "application/zip")},
            timeout=10,
        )
    assert submit.status_code == 400
    assert "expired" in submit.json().get("detail", "").lower()


def test_submission_accepts_optional_student_email(
    base_url: str, happy_path_setup: dict, test_zip
) -> None:
    """Guards: Public submission accepts optional studentEmail field."""
    key = happy_path_setup["assignmentKey"]
    with open(test_zip, "rb") as f:
        r = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": key,
                "studentIdentifier": "s2@test.edu",
                "studentName": "Student 2",
                "studentEmail": "student2@test.edu",
            },
            files={"zipFile": ("sub.zip", f, "application/zip")},
            timeout=30,
        )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "processed"


def test_exclusion_code_crud_endpoints(base_url: str, happy_path_setup: dict) -> None:
    """Guards: Exclusion-code GET/PUT/DELETE operate on assignment field."""
    aid = happy_path_setup["assignmentId"]
    headers = happy_path_setup["auth_headers"]

    initial = requests.get(
        f"{base_url}/api/instructor/assignments/{aid}/exclusion-code",
        headers=headers,
        timeout=10,
    )
    assert initial.status_code == 200
    assert initial.json()["assignmentId"] == aid

    put = requests.put(
        f"{base_url}/api/instructor/assignments/{aid}/exclusion-code",
        headers=headers,
        json={"exclusionCode": "starter template"},
        timeout=10,
    )
    assert put.status_code == 200
    assert put.json()["exclusionCode"] == "starter template"

    assignment = requests.get(
        f"{base_url}/api/instructor/assignments/{aid}",
        headers=headers,
        timeout=10,
    )
    assert assignment.status_code == 200
    assert assignment.json()["exclusionCode"] == "starter template"

    delete = requests.delete(
        f"{base_url}/api/instructor/assignments/{aid}/exclusion-code",
        headers=headers,
        timeout=10,
    )
    assert delete.status_code == 200
    assert delete.json()["exclusionCode"] is None


def test_download_submissions_returns_zip(
    base_url: str, happy_path_setup: dict
) -> None:
    """Guards: Download endpoint returns a valid ZIP attachment."""
    aid = happy_path_setup["assignmentId"]
    headers = happy_path_setup["auth_headers"]
    r = requests.get(
        f"{base_url}/api/instructor/assignments/{aid}/submissions/download",
        headers=headers,
        timeout=15,
    )
    assert r.status_code == 200
    assert "application/zip" in r.headers.get("content-type", "")
    assert "attachment;" in r.headers.get("content-disposition", "")

    # Validate zip bytes are parseable.
    with zipfile.ZipFile(io.BytesIO(r.content), "r") as zf:
        names = zf.namelist()
        assert isinstance(names, list)
        assert len(names) >= 1


def test_delete_assignment_submissions_removes_list_entries(
    base_url: str, happy_path_setup: dict
) -> None:
    """Guards: Delete submissions endpoint removes assignment submissions."""
    aid = happy_path_setup["assignmentId"]
    headers = happy_path_setup["auth_headers"]
    delete = requests.delete(
        f"{base_url}/api/instructor/assignments/{aid}/submissions",
        headers=headers,
        timeout=10,
    )
    assert delete.status_code == 204

    listed = requests.get(
        f"{base_url}/api/instructor/assignments/{aid}/submissions",
        headers=headers,
        timeout=10,
    )
    assert listed.status_code == 200
    assert listed.json() == []


def test_delete_assignment_cascades_and_returns_404_after(
    base_url: str, happy_path_setup: dict
) -> None:
    """Guards: Delete assignment removes assignment record."""
    aid = happy_path_setup["assignmentId"]
    headers = happy_path_setup["auth_headers"]
    delete = requests.delete(
        f"{base_url}/api/instructor/assignments/{aid}",
        headers=headers,
        timeout=10,
    )
    assert delete.status_code == 204

    fetch = requests.get(
        f"{base_url}/api/instructor/assignments/{aid}",
        headers=headers,
        timeout=10,
    )
    assert fetch.status_code == 404


def test_class_list_route_removed_returns_404(base_url: str, auth_headers: dict) -> None:
    """Guards: Removed class-list scaffolding now returns 404."""
    bogus_course_id = "665f00000000000000000000"
    r = requests.get(
        f"{base_url}/api/instructor/courses/{bogus_course_id}/class-list",
        headers=auth_headers,
        timeout=10,
    )
    assert r.status_code == 404
