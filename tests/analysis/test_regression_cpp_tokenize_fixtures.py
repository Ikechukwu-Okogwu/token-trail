"""C++ regression fixtures scored with :func:`run_tokenize_similarity_pipeline`.

``config`` is omitted so the pipeline loads the per-language default bundle from
``backend/app/analysis/config/default_metas.json``.

Expectations come only from each fixture's ``result.txt`` (same rules as
:func:`tests.analysis.regression_runner.validate_fixture_assignment`).
ZIP merge / template loading matches :mod:`tests.analysis.regression_runner`.
"""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.analysis.tree_sitter_analysis.tokenize_pipeline import run_tokenize_similarity_pipeline

from tests.analysis.regression_runner import (
    FixtureValidationError,
    canonical_pair_key,
    parse_result_file,
    score_to_label,
    _build_merged_text_for_zip,
    _load_template_text,
    _parse_bool,
    _validate_fixture_documentation,
)

FIXTURES_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "regression"


def _validate_cpp_tokenize_assignment(assignment_dir: Path, *, expected_tolerance: float = 0.06) -> list[str]:
    """Same checks as ``validate_fixture_assignment``, but scores via tokenize pipeline."""
    if expected_tolerance < 0:
        raise FixtureValidationError("expected_tolerance must be >= 0")

    result_path = assignment_dir / "result.txt"
    metadata, expectations = parse_result_file(result_path)
    language = metadata["language"]
    if language != "cpp":
        raise FixtureValidationError(
            f"This test module only supports language=cpp, got {language!r} in {result_path}"
        )

    submissions_dir = assignment_dir / "submissions"
    if not submissions_dir.exists():
        raise FixtureValidationError(f"Missing submissions directory: {submissions_dir}")

    submission_zips = sorted(submissions_dir.glob("*.zip"))
    if len(submission_zips) < 2:
        raise FixtureValidationError(f"Expected at least 2 submission zips in {submissions_dir}")
    _validate_fixture_documentation(assignment_dir, expectations, [path.name for path in submission_zips])

    scores: dict[tuple[str, str], float] = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        template_text = _load_template_text(assignment_dir, language, tmp_dir)
        use_template = _parse_bool(metadata.get("template_exclusion", "false"))

        merged_text_by_zip: dict[str, str] = {}
        for zip_path in submission_zips:
            merged_text_by_zip[zip_path.name] = _build_merged_text_for_zip(
                zip_path=zip_path,
                language=language,
                work_dir=tmp_dir / "submissions",
            )

        template = template_text if use_template else ""
        for left_name, right_name in combinations(sorted(merged_text_by_zip.keys()), 2):
            key = canonical_pair_key(left_name, right_name)
            left_text = merged_text_by_zip[left_name]
            right_text = merged_text_by_zip[right_name]
            result = run_tokenize_similarity_pipeline(
                left_text,
                right_text,
                language="cpp",
                template=template,
            )
            scores[key] = float(result.similarity)

    require_all_pairs = _parse_bool(metadata.get("require_all_pairs", "true"))
    errors: list[str] = []

    if require_all_pairs and set(scores.keys()) != set(expectations.keys()):
        missing = sorted(set(scores.keys()) - set(expectations.keys()))
        extra = sorted(set(expectations.keys()) - set(scores.keys()))
        if missing:
            errors.append(f"Missing expectations for pairs: {missing}")
        if extra:
            errors.append(f"Unexpected expectations for nonexistent pairs: {extra}")
        return errors

    pairs_to_check = set(expectations.keys()) & set(scores.keys())
    for key in sorted(pairs_to_check):
        actual = scores[key]
        expected = expectations[key]
        if not (expected.range_min <= actual <= expected.range_max):
            errors.append(
                f"{key}: score {actual:.4f} outside range [{expected.range_min:.4f}, {expected.range_max:.4f}]"
            )
        if abs(actual - expected.expected) > expected_tolerance:
            errors.append(
                f"{key}: score {actual:.4f} too far from expected {expected.expected:.4f} (tol={expected_tolerance:.4f})"
            )
        actual_label = score_to_label(actual)
        if actual_label != expected.label:
            errors.append(f"{key}: label {actual_label!r} != expected {expected.label!r}")
    return errors


def test_cpp_renamed_vars_tokenize_matches_result_txt() -> None:
    fixture = FIXTURES_ROOT / "assignment_renamed_vars_cpp"
    errors = _validate_cpp_tokenize_assignment(fixture)
    assert not errors, errors


def test_cpp_reordered_functions_tokenize_matches_result_txt() -> None:
    fixture = FIXTURES_ROOT / "assignment_reordered_functions_cpp"
    errors = _validate_cpp_tokenize_assignment(fixture)
    assert not errors, errors
