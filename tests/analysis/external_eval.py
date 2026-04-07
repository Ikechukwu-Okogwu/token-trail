"""Exploratory engine evaluation for external ZIP bundles (no result.txt / markdown).

Uses the same pipeline as regression fixtures: safe ZIP extract, merge, pairwise
``compare_texts_with_template`` (see ``regression_runner.compute_pairwise_similarity_scores``).

Normalize vendor data
---------------------

1. Create a working folder (not necessarily under ``tests/fixtures``).
2. Put one student submission per file under ``submissions/*.zip`` (or pass ``--submissions-dir``).
3. Optional: place ``template.txt`` or ``template.zip`` next to ``submissions/`` (sibling of
   ``submissions``, i.e. the *assignment* directory) and pass ``--template-exclusion``.

Run::

    python -m tests.analysis.external_eval --assignment-dir <path> --language java

Capture printed scores as a baseline for ``result.txt`` ranges when promoting to CI.

Promote to CI regression
------------------------

1. Copy the folder under ``tests/fixtures/regression/<name>/``.
2. Add ``result.txt`` (metadata + pair lines with ``range=``, ``label=``, ``expected=``).
3. Add ``result_explanation.md`` and ``submission_creation.md`` (required by the fixture runner).
4. Add a test in ``tests/analysis/test_regression_fixtures.py`` that calls
   ``validate_fixture_assignment``.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Print pairwise similarity scores for submission ZIPs using the production-equivalent "
            "extract/merge/compare pipeline (no golden result.txt required)."
        )
    )
    parser.add_argument(
        "--assignment-dir",
        type=Path,
        required=True,
        help=(
            "Directory that may contain template.txt / template.zip (optional). "
            "Default submission location is <assignment-dir>/submissions/."
        ),
    )
    parser.add_argument(
        "--submissions-dir",
        type=Path,
        default=None,
        help="Directory containing *.zip submissions (default: <assignment-dir>/submissions).",
    )
    parser.add_argument(
        "--language",
        required=True,
        choices=["c", "cpp", "java"],
        help="Assignment language (homogeneous; one language per run).",
    )
    parser.add_argument(
        "--template-exclusion",
        action="store_true",
        help="Subtract template hashes (requires template.txt or template.zip under assignment-dir).",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Write CSV to stdout instead of a human-readable table.",
    )
    return parser.parse_args(argv)


def _resolve_submissions_dir(assignment_dir: Path, submissions_dir: Path | None) -> Path:
    assignment_dir = assignment_dir.resolve()
    if submissions_dir is not None:
        return submissions_dir.resolve()
    default = assignment_dir / "submissions"
    if default.is_dir():
        return default
    zips_here = list(assignment_dir.glob("*.zip"))
    if len(zips_here) >= 2:
        return assignment_dir
    raise SystemExit(
        f"No submissions directory {default} and fewer than 2 *.zip in {assignment_dir}. "
        "Create submissions/ with one zip per submission or pass --submissions-dir."
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    assignment_dir = args.assignment_dir.resolve()
    if not assignment_dir.is_dir():
        print(f"assignment-dir is not a directory: {assignment_dir}", file=sys.stderr)
        return 2

    submissions_dir = _resolve_submissions_dir(assignment_dir, args.submissions_dir)
    if not submissions_dir.is_dir():
        print(f"submissions-dir is not a directory: {submissions_dir}", file=sys.stderr)
        return 2

    zips = sorted(submissions_dir.glob("*.zip"))
    if len(zips) < 2:
        print(
            f"Need at least 2 submission *.zip files in {submissions_dir}; found {len(zips)}.",
            file=sys.stderr,
        )
        return 2

    # Import after argparse so --help works without backend on PYTHONPATH in odd setups.
    from tests.analysis.regression_runner import (
        FixtureValidationError,
        compute_pairwise_similarity_scores,
        score_to_label,
    )

    try:
        scores = compute_pairwise_similarity_scores(
            assignment_dir,
            zips,
            language=args.language,
            use_template=args.template_exclusion,
        )
    except FixtureValidationError as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.csv:
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerow(["left", "right", "similarity", "label"])
        for (left, right) in sorted(scores.keys()):
            s = scores[(left, right)]
            writer.writerow([left, right, f"{s:.6f}", score_to_label(s)])
        return 0

    print(f"assignment_dir={assignment_dir}")
    print(f"submissions_dir={submissions_dir}")
    print(f"language={args.language} template_exclusion={args.template_exclusion}")
    print(f"submissions ({len(zips)}): {', '.join(z.name for z in zips)}")
    print()
    for (left, right) in sorted(scores.keys()):
        s = scores[(left, right)]
        print(f"{left},{right}\t{s:.4f}\t{score_to_label(s)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
