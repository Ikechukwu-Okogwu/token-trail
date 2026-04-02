"""One-off: print ``similarity_results`` for a runId (stdout only, no result_log).

Run from backend root:
  python -m app.analysis.localtest.temp_view_run_similarity <run_id>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent.parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.core.db import get_db


def main() -> None:
    if len(sys.argv) < 2:
        sys.stderr.write(
            "usage: python -m app.analysis.localtest.temp_view_run_similarity <run_id>\n"
        )
        sys.exit(1)
    run_id = sys.argv[1].strip()
    doc = get_db()["similarity_results"].find_one({"runId": run_id})
    if doc is None:
        sys.stderr.write(f"similarity_results not found for runId={run_id!r}\n")
        sys.exit(2)
    doc = dict(doc)
    doc.pop("_id", None)
    print(json.dumps(doc, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
