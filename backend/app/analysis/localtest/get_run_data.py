"""Local test: JWT login, fetch analysis run + similarity-results from API, write result_log.

Uses :mod:`get_access_token` and :mod:`log` (same pattern as ``run_analysis_on_specified_assignment``).

Available endpoints (no Mongo):
  GET /api/instructor/analysis-runs/{run_id}
  GET /api/instructor/analysis-runs/{run_id}/similarity-results

Note: ranked list does not include per-pair ``matchingRegions``; pair detail/comparison
routes exist but comparison currently returns empty ``matchingRegions`` in code.

Run from backend root:
  python -m app.analysis.localtest.get_run_data <run_id>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent.parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

import requests

from app.analysis.localtest.get_access_token import BASE_URL, get_access_token
from app.analysis.localtest.log import test_log

TEST_PROJECT = "get_run_data"
RUN_ID = "69c94ede416228f190bb8596"


def _fmt_response(label: str, r: requests.Response) -> str:
    body_preview = r.text
    try:
        body_pretty = json.dumps(r.json(), indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, ValueError):
        body_pretty = body_preview
    return (
        f"--- {label} ---\n"
        f"URL: {r.url}\n"
        f"HTTP {r.status_code}\n"
        f"{body_pretty}\n\n"
    )


def run(run_id: str) -> None:
    lines: list[str] = []
    lines.append(f"=== {TEST_PROJECT} ===\n")
    lines.append(f"run_id: {run_id}\n\n")

    try:
        token = get_access_token(base_url=BASE_URL)
        headers = {"Authorization": f"Bearer {token}"}
        lines.append("Login: OK\n\n")
    except (RuntimeError, requests.RequestException) as e:
        lines.append(f"Login FAILED: {e}\n")
        log_path = test_log(TEST_PROJECT, "".join(lines))
        print(f"Test log saved to: {log_path}")
        return

    for path, label in (
        (f"{BASE_URL}/instructor/analysis-runs/{run_id}", "run status"),
        (
            f"{BASE_URL}/instructor/analysis-runs/{run_id}/similarity-results",
            "similarity-results (ranked list)",
        ),
    ):
        try:
            r = requests.get(path, headers=headers, timeout=30)
            lines.append(_fmt_response(label, r))
        except requests.RequestException as e:
            lines.append(f"--- {label} ---\nREQUEST FAILED: {e}\n\n")

    log_path = test_log(TEST_PROJECT, "".join(lines))
    print(f"Test log saved to: {log_path}")


def main() -> None:
    if len(sys.argv) < 2:
        run(RUN_ID)
    else:
        run(sys.argv[1].strip())


if __name__ == "__main__":
    main()
