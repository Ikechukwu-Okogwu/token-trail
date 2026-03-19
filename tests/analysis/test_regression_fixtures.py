"""Regression tests for offline fixture-based similarity evaluation.

Test Plan:
- Input partitions:
  - Valid fixture folders with homogeneous language and complete pair expectations.
  - Invalid fixture specs (malformed lines, missing metadata/pair expectations).
- Boundary values:
  - Label boundaries (low/medium/high) and tolerance checks around expected score.
  - Minimal valid submission set (2 zips) vs larger stage3 rank fixture.
- Interface misuse cases:
  - Mixed-language submissions in one assignment.
  - Missing expected pair rows when full matrix is required.
- Failure modes:
  - Parser rejects malformed result.txt quickly with explicit errors.
  - Validation emits actionable mismatch details instead of vague assertion failures.
"""

from __future__ import annotations

from pathlib import Path
import zipfile

import pytest

from tests.analysis.regression_runner import (
    FixtureValidationError,
    parse_result_file,
    score_to_label,
    validate_fixture_assignment,
)


FIXTURES_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "regression"


def test_regression_fixture_renamed_variables_passes() -> None:
    """Validation test: renamed identifiers should still score as high similarity."""
    fixture = FIXTURES_ROOT / "assignment_renamed_vars"
    errors = validate_fixture_assignment(fixture)
    assert not errors, f"Renamed-vars fixture mismatches: {errors}"


def test_regression_fixture_reordered_functions_passes() -> None:
    """Validation test: function order changes should remain detectable."""
    fixture = FIXTURES_ROOT / "assignment_reordered_functions"
    errors = validate_fixture_assignment(fixture)
    assert not errors, f"Reordered-functions fixture mismatches: {errors}"


def test_regression_fixture_template_heavy_passes() -> None:
    """Validation test: template-heavy pairs should trend lower after exclusion."""
    fixture = FIXTURES_ROOT / "assignment_template_heavy"
    errors = validate_fixture_assignment(fixture)
    assert not errors, f"Template-heavy fixture mismatches: {errors}"


def test_regression_fixture_stage3_rankset_passes() -> None:
    """Regression test: larger stage3-style set remains stable and fully scorable."""
    fixture = FIXTURES_ROOT / "assignment_stage3_rankset"
    errors = validate_fixture_assignment(fixture)
    assert not errors, f"Stage3 fixture mismatches: {errors}"


def test_score_to_label_boundaries() -> None:
    """Boundary test: verify exact bucket transitions for score labels."""
    assert score_to_label(0.0) == "low"
    assert score_to_label(0.3999) == "low"
    assert score_to_label(0.4) == "medium"
    assert score_to_label(0.7999) == "medium"
    assert score_to_label(0.8) == "high"
    assert score_to_label(1.0) == "high"


def test_result_parser_rejects_malformed_line(tmp_path: Path) -> None:
    """Defect test: malformed expectation rows must fail with explicit parser error."""
    fixture = tmp_path / "bad_fixture"
    fixture.mkdir(parents=True, exist_ok=True)
    (fixture / "result.txt").write_text(
        "\n".join(
            [
                "fixture=bad",
                "language=java",
                "homogeneous=true",
                "template_exclusion=false",
                "StudentA.zip,StudentB.zip,expected=0.93,label=high",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(FixtureValidationError):
        parse_result_file(fixture / "result.txt")


def test_runner_rejects_mixed_language_submission(tmp_path: Path) -> None:
    """Defect test: mixed-language files inside one assignment must be rejected."""
    fixture = tmp_path / "mixed"
    submissions = fixture / "submissions"
    submissions.mkdir(parents=True, exist_ok=True)
    (fixture / "result.txt").write_text(
        "\n".join(
            [
                "fixture=mixed",
                "language=java",
                "homogeneous=true",
                "template_exclusion=false",
                "A.zip,B.zip,expected=0.90,range=0.80-1.00,label=high",
            ]
        ),
        encoding="utf-8",
    )

    with zipfile.ZipFile(submissions / "A.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Main.java", "class Main { int x = 1; }")
    with zipfile.ZipFile(submissions / "B.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Main.java", "class Main { int y = 2; }")
        zf.writestr("extra.cpp", "int main(){return 0;}")

    with pytest.raises(FixtureValidationError):
        validate_fixture_assignment(fixture)


def test_runner_reports_missing_expected_pair_when_full_matrix_required(tmp_path: Path) -> None:
    """Defect test: missing pair expectation should fail when require_all_pairs=true."""
    fixture = tmp_path / "missing_pair"
    submissions = fixture / "submissions"
    submissions.mkdir(parents=True, exist_ok=True)
    (fixture / "result.txt").write_text(
        "\n".join(
            [
                "fixture=missing_pair",
                "language=java",
                "homogeneous=true",
                "template_exclusion=false",
                "require_all_pairs=true",
                "A.zip,B.zip,expected=0.90,range=0.80-1.00,label=high",
            ]
        ),
        encoding="utf-8",
    )

    for name in ("A.zip", "B.zip", "C.zip"):
        with zipfile.ZipFile(submissions / name, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Main.java", f"class Main{name[0]} {{ int v = {ord(name[0])}; }}")

    errors = validate_fixture_assignment(fixture)
    assert errors, "Expected missing-pair validation errors but got none"
    assert "Missing expectations for pairs" in errors[0]


def test_runner_repeatability_is_stable() -> None:
    """Stress test: repeated runs should produce consistent pass/fail outcomes."""
    fixture = FIXTURES_ROOT / "assignment_renamed_vars"
    for _ in range(50):
        errors = validate_fixture_assignment(fixture)
        assert not errors, f"Repeatability failure: {errors}"
