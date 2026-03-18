"""Local test: login, queue analysis run, poll until done, fetch results, log to result_log."""
import sys
import time
from pathlib import Path

# Ensure backend is in path when run as script (e.g. python run_analysis_on_specified_assignment.py)
_backend = Path(__file__).resolve().parent.parent.parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

import requests

from app.analysis.localtest.get_access_token import get_access_token
from app.analysis.localtest.log import test_log

BASE_URL = "http://localhost:8000/api"
TEST_PROJECT = "run_analysis_on_specified_assignment"

assignment_id = "69ba0363a906062a119e9b6d"


def run():
    """Execute the test and log results."""
    lines = []
    lines.append(f"=== {TEST_PROJECT} ===\n")
    lines.append(f"Assignment ID: {assignment_id}\n")

    # 1. Login (via get_access_token: try login, signup on fail, retry)
    try:
        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        lines.append("Login: OK\n")
    except (RuntimeError, requests.RequestException) as e:
        lines.append(f"Login FAILED: {e}\n")
        test_log(TEST_PROJECT, "".join(lines))
        return

    # 2. Queue analysis run
    try:
        r = requests.post(
            f"{BASE_URL}/instructor/assignments/{assignment_id}/analysis-runs",
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        run_id = data["runId"]
        lines.append(f"Queue analysis run: OK\n")
        lines.append(f"  runId: {run_id}\n")
        lines.append(f"  status: {data.get('status')}\n")
    except requests.RequestException as e:
        lines.append(f"Queue analysis run FAILED: {e}\n")
        if hasattr(e, "response") and e.response is not None:
            lines.append(f"Response: {e.response.text}\n")
        test_log(TEST_PROJECT, "".join(lines))
        return

    # 3. Poll until completed or failed
    lines.append("\n--- Polling run status ---\n")
    max_wait = 120
    poll_interval = 5
    elapsed = 0
    run_status = None
    while elapsed < max_wait:
        try:
            r = requests.get(
                f"{BASE_URL}/instructor/analysis-runs/{run_id}",
                headers=headers,
                timeout=10,
            )
            r.raise_for_status()
            run_status = r.json()
            status = run_status["status"]
            lines.append(f"  [{elapsed}s] status={status}\n")
            if status in ("completed", "failed"):
                break
        except requests.RequestException as e:
            lines.append(f"  Poll FAILED: {e}\n")
            break
        time.sleep(poll_interval)
        elapsed += poll_interval

    if run_status:
        lines.append(f"\nRun final status:\n")
        for k, v in run_status.items():
            lines.append(f"  {k}: {v}\n")

    # 4. Get analysis results (similarity-results)
    lines.append("\n--- Similarity results ---\n")
    try:
        r = requests.get(
            f"{BASE_URL}/instructor/analysis-runs/{run_id}/similarity-results",
            headers=headers,
            timeout=10,
        )
        lines.append(f"  Status: {r.status_code}\n")
        lines.append(f"  Body: {r.text}\n")
    except requests.RequestException as e:
        lines.append(f"  FAILED: {e}\n")

    # 5. Save to result_log
    log_path = test_log(TEST_PROJECT, "".join(lines))
    print(f"Test log saved to: {log_path}")


if __name__ == "__main__":
    run()
