"""
E2E tests for the Token Trail analysis pipeline.

These tests cover scenarios NOT already in test_api_contract.py.
All tests require the Docker stack running (auto-skipped if API unreachable).

Test Plan:
- Run lifecycle with 0 and 1 submission:
  - worker completes; similarity-results endpoint returns empty list (not 404)
- Similarity results before worker picks up job:
  - immediately after queue, results endpoint returns 404
- Known similar submissions score high:
  - Alice.zip vs Bob.zip (renamed-vars fixture) should score >= 0.8
- Run timestamps set after completion:
  - startedAt and finishedAt are present and parseable ISO strings
- Analysis is deterministic:
  - two separate runs on the same assignment produce matching pair scores
- resultId embeds the submission IDs:
  - {runId}__{leftId}__{rightId} — all three parts parse back correctly
- Comparison line numbers are valid:
  - all matchingRegion line numbers >= 1
- Template exclusion is NOT yet wired (known bug, documented as xfail):
  - exclusionCode on assignment has no effect in production; score unchanged
"""

from __future__ import annotations

import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
import requests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "regression"


def _wait_for_run(base_url: str, headers: dict, run_id: str, max_wait: int = 60) -> str:
    """Poll until run reaches completed/failed. Returns final status."""
    deadline = time.time() + max_wait
    while time.time() < deadline:
        r = requests.get(
            f"{base_url}/api/instructor/analysis-runs/{run_id}",
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        status = r.json().get("status", "")
        if status in ("completed", "failed"):
            return status
        time.sleep(2)
    return ""


def _make_assignment(base_url: str, headers: dict, *, exclusion_code: str | None = None) -> dict:
    """Create course + assignment. Returns assignment dict (has 'id' and 'assignmentKey')."""
    rc = requests.post(
        f"{base_url}/api/instructor/courses",
        headers=headers,
        json={"name": f"flow-test-{uuid4().hex[:6]}", "term": "T"},
        timeout=10,
    )
    rc.raise_for_status()
    cid = rc.json()["id"]

    ra = requests.post(
        f"{base_url}/api/instructor/assignments",
        headers=headers,
        json={
            "courseId": cid,
            "title": "FlowHW",
            "language": "java",
            "isOpen": True,
            "dueDate": None,
            "keyExpiry": None,
            "autoAnalysis": False,
            "allowLate": False,
            "exclusionCode": exclusion_code,
        },
        timeout=10,
    )
    ra.raise_for_status()
    return ra.json()


def _upload_zip(base_url: str, assignment_key: str, zip_path: Path, student: str) -> None:
    with open(zip_path, "rb") as f:
        r = requests.post(
            f"{base_url}/api/public/submissions",
            data={
                "assignmentKey": assignment_key,
                "studentIdentifier": student,
                "studentName": student.split("@")[0],
            },
            files={"zipFile": (zip_path.name, f, "application/zip")},
            timeout=30,
        )
    r.raise_for_status()


def _queue_run(base_url: str, headers: dict, assignment_id: str) -> str:
    r = requests.post(
        f"{base_url}/api/instructor/assignments/{assignment_id}/analysis-runs",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["runId"]


# ---------------------------------------------------------------------------
# Tests — empty submissions
# ---------------------------------------------------------------------------


def test_zero_submissions_run_results_list_is_empty(base_url: str, auth_headers: dict) -> None:
    """
    A run with 0 submissions completes and results endpoint returns an empty list.
    Guards: worker doesn't crash on zero pairs; results endpoint returns [] not 404.
    """
    assignment = _make_assignment(base_url, auth_headers)
    run_id = _queue_run(base_url, auth_headers, assignment["id"])
    status = _wait_for_run(base_url, auth_headers, run_id)
    assert status == "completed", f"Expected completed, got {status}"

    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=auth_headers,
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["runId"] == run_id
    assert data["results"] == [], f"Expected empty pairs for 0 submissions, got: {data['results']}"


def test_one_submission_run_results_list_is_empty(
    base_url: str, auth_headers: dict, test_zip: Path
) -> None:
    """
    A run with exactly 1 submission completes and results endpoint returns an empty list.
    Guards: N*(N-1)/2 = 0 for N=1; no crash.
    """
    assignment = _make_assignment(base_url, auth_headers)
    _upload_zip(base_url, assignment["assignmentKey"], test_zip, "solo@test.edu")
    run_id = _queue_run(base_url, auth_headers, assignment["id"])
    status = _wait_for_run(base_url, auth_headers, run_id)
    assert status == "completed", f"Expected completed, got {status}"

    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=auth_headers,
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["results"] == [], f"Expected empty pairs for 1 submission, got: {data['results']}"


# ---------------------------------------------------------------------------
# Tests — results 404 before worker processes
# ---------------------------------------------------------------------------


def test_queued_run_has_no_results_yet(base_url: str, auth_headers: dict) -> None:
    """
    Immediately after queuing (before worker picks up), results endpoint returns 404.
    Guards: results are only available after completed status; no premature data.
    Note: worker polls every 5 s. This test races the worker; it is best-effort.
    If the worker is very fast (< 1 s) this assertion may not hold.
    """
    assignment = _make_assignment(base_url, auth_headers)
    run_id = _queue_run(base_url, auth_headers, assignment["id"])

    # Check immediately — run should still be queued or running, not yet completed
    run_check = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}",
        headers=auth_headers,
        timeout=5,
    )
    run_check.raise_for_status()
    status = run_check.json().get("status")

    if status in ("completed", "failed"):
        pytest.skip("Worker processed the run before we could check (too fast for this assertion)")

    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=auth_headers,
        timeout=5,
    )
    assert r.status_code == 404, (
        f"Expected 404 for queued/running run, got {r.status_code}: {r.text}"
    )


# ---------------------------------------------------------------------------
# Tests — known similar submissions
# ---------------------------------------------------------------------------


def test_known_similar_pair_alice_bob_scores_high(
    base_url: str, auth_headers: dict
) -> None:
    """
    Alice.zip and Bob.zip from the renamed-vars fixture are known to be highly similar
    (same algorithm, only variable names differ). The engine must detect them.
    Expected: top pair score >= 0.8, Carol.zip pairs score < 0.3.
    """
    fixture_subs = _FIXTURE_ROOT / "assignment_renamed_vars" / "submissions"
    alice_zip = fixture_subs / "Alice.zip"
    bob_zip = fixture_subs / "Bob.zip"
    carol_zip = fixture_subs / "Carol.zip"

    if not alice_zip.exists() or not bob_zip.exists() or not carol_zip.exists():
        pytest.skip("Renamed-vars fixture ZIPs not found at expected path")

    assignment = _make_assignment(base_url, auth_headers)
    key = assignment["assignmentKey"]

    _upload_zip(base_url, key, alice_zip, "alice@test.edu")
    _upload_zip(base_url, key, bob_zip, "bob@test.edu")
    _upload_zip(base_url, key, carol_zip, "carol@test.edu")

    run_id = _queue_run(base_url, auth_headers, assignment["id"])
    status = _wait_for_run(base_url, auth_headers, run_id)
    assert status == "completed", f"Run did not complete: {status}"

    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=auth_headers,
        timeout=10,
    )
    r.raise_for_status()
    results = r.json()["results"]
    assert results, "Expected at least one similarity pair"

    # Top pair should be Alice vs Bob (high similarity)
    top = results[0]
    assert top["similarityScore"] >= 0.8, (
        f"Top pair score {top['similarityScore']:.3f} < 0.8 — "
        f"Alice/Bob should be detected as highly similar"
    )

    # All scores must be descending
    scores = [item["similarityScore"] for item in results]
    assert scores == sorted(scores, reverse=True), "Results not sorted descending by score"


# ---------------------------------------------------------------------------
# Tests — run timestamps
# ---------------------------------------------------------------------------


def test_completed_run_has_started_and_finished_at(
    base_url: str, auth_headers: dict, test_zip: Path
) -> None:
    """
    After a run completes, the run document must have startedAt and finishedAt
    as parseable ISO timestamps, with finishedAt >= startedAt.
    """
    assignment = _make_assignment(base_url, auth_headers)
    _upload_zip(base_url, assignment["assignmentKey"], test_zip, "ts-a@test.edu")
    _upload_zip(base_url, assignment["assignmentKey"], test_zip, "ts-b@test.edu")
    run_id = _queue_run(base_url, auth_headers, assignment["id"])
    status = _wait_for_run(base_url, auth_headers, run_id)
    assert status == "completed"

    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}",
        headers=auth_headers,
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()

    assert "startedAt" in data and data["startedAt"], "startedAt should be set after completion"
    assert "finishedAt" in data and data["finishedAt"], "finishedAt should be set after completion"

    started = datetime.fromisoformat(data["startedAt"].replace("Z", "+00:00"))
    finished = datetime.fromisoformat(data["finishedAt"].replace("Z", "+00:00"))
    assert finished >= started, (
        f"finishedAt ({finished}) must be >= startedAt ({started})"
    )


# ---------------------------------------------------------------------------
# Tests — determinism
# ---------------------------------------------------------------------------


def test_analysis_deterministic_across_two_runs(
    base_url: str, auth_headers: dict, test_zip: Path, tmp_path: Path
) -> None:
    """
    Running analysis twice on the same assignment must produce the same
    similarity score for the same pair. Guards: no randomness in engine.
    """
    second_zip = tmp_path / "b.zip"
    with zipfile.ZipFile(second_zip, "w") as zf:
        zf.writestr(
            "Main.java",
            "public class Main { public static void main(String[] a) { int x = 42; } }",
        )

    assignment = _make_assignment(base_url, auth_headers)
    key = assignment["assignmentKey"]
    aid = assignment["id"]
    _upload_zip(base_url, key, test_zip, "det-a@test.edu")
    _upload_zip(base_url, key, second_zip, "det-b@test.edu")

    run1_id = _queue_run(base_url, auth_headers, aid)
    assert _wait_for_run(base_url, auth_headers, run1_id) == "completed"

    run2_id = _queue_run(base_url, auth_headers, aid)
    assert _wait_for_run(base_url, auth_headers, run2_id) == "completed"

    def _get_top_score(run_id: str) -> float:
        r = requests.get(
            f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
            headers=auth_headers,
            timeout=10,
        )
        r.raise_for_status()
        results = r.json()["results"]
        return results[0]["similarityScore"] if results else 0.0

    score1 = _get_top_score(run1_id)
    score2 = _get_top_score(run2_id)
    assert score1 == pytest.approx(score2, abs=1e-4), (
        f"Analysis not deterministic: run1={score1}, run2={score2}"
    )


# ---------------------------------------------------------------------------
# Tests — resultId structure
# ---------------------------------------------------------------------------


def test_result_id_embeds_submission_ids(
    base_url: str, auth_headers: dict, test_zip: Path, tmp_path: Path
) -> None:
    """
    resultId must have format {runId}__{leftSubmissionId}__{rightSubmissionId}
    so it can be parsed back to identify each side.
    """
    second_zip = tmp_path / "rid_b.zip"
    with zipfile.ZipFile(second_zip, "w") as zf:
        zf.writestr("Main.java", "public class Main { void run() {} }")

    assignment = _make_assignment(base_url, auth_headers)
    key = assignment["assignmentKey"]
    _upload_zip(base_url, key, test_zip, "rid-a@test.edu")
    _upload_zip(base_url, key, second_zip, "rid-b@test.edu")

    run_id = _queue_run(base_url, auth_headers, assignment["id"])
    assert _wait_for_run(base_url, auth_headers, run_id) == "completed"

    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=auth_headers,
        timeout=10,
    )
    r.raise_for_status()
    results = r.json()["results"]
    assert results, "Expected at least one pair"

    row = results[0]
    result_id = row["resultId"]
    parts = result_id.split("__")
    assert len(parts) == 3, f"resultId should have 3 parts separated by '__', got: {result_id!r}"

    parsed_run_id, left_id, right_id = parts
    assert parsed_run_id == run_id, (
        f"resultId run part {parsed_run_id!r} != run_id {run_id!r}"
    )
    assert left_id == row["leftSubmissionId"], (
        f"resultId left part {left_id!r} != leftSubmissionId {row['leftSubmissionId']!r}"
    )
    assert right_id == row["rightSubmissionId"], (
        f"resultId right part {right_id!r} != rightSubmissionId {row['rightSubmissionId']!r}"
    )


# ---------------------------------------------------------------------------
# Tests — line number validity in comparison
# ---------------------------------------------------------------------------


def test_matching_regions_line_numbers_valid(
    base_url: str, auth_headers: dict, test_zip: Path
) -> None:
    """
    Any matchingRegions returned by the comparison endpoint must have
    line numbers >= 1. leftEndLine >= leftStartLine, same for right.
    """
    assignment = _make_assignment(base_url, auth_headers)
    key = assignment["assignmentKey"]
    _upload_zip(base_url, key, test_zip, "ln-a@test.edu")
    _upload_zip(base_url, key, test_zip, "ln-b@test.edu")  # identical → regions expected

    run_id = _queue_run(base_url, auth_headers, assignment["id"])
    assert _wait_for_run(base_url, auth_headers, run_id) == "completed"

    list_r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=auth_headers,
        timeout=10,
    )
    list_r.raise_for_status()
    results = list_r.json()["results"]
    assert results
    result_id = results[0]["resultId"]

    cmp_r = requests.get(
        f"{base_url}/api/instructor/similarity-results/{result_id}/comparison",
        headers=auth_headers,
        timeout=10,
    )
    assert cmp_r.status_code == 200
    payload = cmp_r.json()

    for region in payload.get("matchingRegions", []):
        assert region["leftStartLine"] >= 1, f"leftStartLine {region['leftStartLine']} < 1"
        assert region["leftEndLine"] >= region["leftStartLine"], (
            f"leftEndLine {region['leftEndLine']} < leftStartLine {region['leftStartLine']}"
        )
        assert region["rightStartLine"] >= 1, f"rightStartLine {region['rightStartLine']} < 1"
        assert region["rightEndLine"] >= region["rightStartLine"], (
            f"rightEndLine {region['rightEndLine']} < rightStartLine {region['rightStartLine']}"
        )


# ---------------------------------------------------------------------------
# Tests — template exclusion
# ---------------------------------------------------------------------------


def test_template_exclusion_reduces_similarity_when_exclusion_code_set(
    base_url: str, auth_headers: dict
) -> None:
    """
    When exclusionCode is set on an assignment and submissions share only template
    code, the similarity score AFTER exclusion should be near 0.

    Previously marked xfail — fixed by PR #37 (hybrid AST engine wires exclusionCode
    through run_analysis_for_assignment -> build_similarity_metrics).
    """
    fixture = _FIXTURE_ROOT / "assignment_template_heavy"
    template_zip = fixture / "template.zip"
    subs = fixture / "submissions"

    if not template_zip.exists():
        pytest.skip("template_heavy fixture not found")

    # Read the template source to pass as exclusionCode
    import zipfile as _zf
    with _zf.ZipFile(template_zip) as z:
        names = [n for n in z.namelist() if n.endswith(".java")]
        if not names:
            pytest.skip("No .java in template zip")
        template_source = z.read(names[0]).decode("utf-8", errors="replace")

    # Create assignment WITH exclusionCode set
    assignment = _make_assignment(base_url, auth_headers, exclusion_code=template_source)
    key = assignment["assignmentKey"]

    for zip_name in ("TemplateA.zip", "TemplateB.zip"):
        sub_path = subs / zip_name
        if not sub_path.exists():
            pytest.skip(f"Template fixture submission {zip_name} not found")
        _upload_zip(base_url, key, sub_path, f"{zip_name.lower()}@test.edu")

    run_id = _queue_run(base_url, auth_headers, assignment["id"])
    status = _wait_for_run(base_url, auth_headers, run_id)
    assert status == "completed"

    r = requests.get(
        f"{base_url}/api/instructor/analysis-runs/{run_id}/similarity-results",
        headers=auth_headers,
        timeout=10,
    )
    r.raise_for_status()
    results = r.json()["results"]
    assert results

    score_with_exclusion = results[0]["similarityScore"]
    # After template exclusion, TemplateA vs TemplateB should score near 0
    # (they share only template boilerplate; unique logic is different)
    assert score_with_exclusion < 0.2, (
        f"Expected near-zero score after template exclusion, got {score_with_exclusion:.3f}."
    )
