"""Tests for exploratory external ZIP evaluation and shared score computation.

Test Plan:
- Partitions: valid multi-zip directory vs too few zips vs bad language.
- Boundaries: two zips minimum; scores in [0, 1].
- Failure modes: FixtureValidationError on invalid input; CLI exit codes.
- Regression: compute_pairwise_similarity_scores matches run_fixture_assignment scores.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from tests.analysis.regression_runner import (
    FixtureValidationError,
    canonical_pair_key,
    compute_pairwise_similarity_scores,
    parse_result_file,
    run_fixture_assignment,
)


FIXTURES_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "regression"


def test_compute_pairwise_scores_matches_fixture_runner() -> None:
    """Regression: shared helper must match full fixture run (same numeric pipeline)."""
    fixture = FIXTURES_ROOT / "assignment_renamed_vars"
    metadata, _ = parse_result_file(fixture / "result.txt")
    zips = sorted((fixture / "submissions").glob("*.zip"))
    use_template = metadata.get("template_exclusion", "false").lower() in {"true", "1", "yes"}

    direct = compute_pairwise_similarity_scores(
        fixture,
        zips,
        language=metadata["language"],
        use_template=use_template,
    )
    full_scores, _, _ = run_fixture_assignment(fixture)
    assert direct == full_scores


def test_compute_pairwise_scores_rejects_fewer_than_two_zips(tmp_path: Path) -> None:
    """Defect: fewer than two submission zips must fail fast."""
    subs = tmp_path / "submissions"
    subs.mkdir()
    with zipfile.ZipFile(subs / "only.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Main.java", "class Main { int x = 1; }")

    with pytest.raises(FixtureValidationError, match="at least two"):
        compute_pairwise_similarity_scores(tmp_path, [subs / "only.zip"], language="java")


def test_compute_pairwise_java_with_template_still_invokes_tokenizer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression: template_exclusion must not skip compute_javacode_similarity when imports work."""
    import tests.analysis.regression_runner as rr

    monkeypatch.setattr(rr, "_JAVA_TOKENIZE_AVAILABLE", True)
    templates_seen: list[str] = []

    def fake_compute(left: str, right: str, template: str = "") -> float:
        templates_seen.append(template)
        return 0.42

    monkeypatch.setattr(rr, "_compute_java", fake_compute)

    subs = tmp_path / "submissions"
    subs.mkdir()
    boiler = "class Boiler { void x() { int z = 0; } }\n"
    for name, extra in (
        ("A.zip", "class AOnly { int a = 1; }"),
        ("B.zip", "class BOnly { int b = 2; }"),
    ):
        with zipfile.ZipFile(subs / name, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Main.java", boiler + extra)

    (tmp_path / "template.txt").write_text(boiler, encoding="utf-8")
    zips = sorted(subs.glob("*.zip"))
    scores = compute_pairwise_similarity_scores(
        tmp_path, zips, language="java", use_template=True
    )
    key = canonical_pair_key("A.zip", "B.zip")
    assert scores[key] == pytest.approx(0.42)
    assert templates_seen == [boiler]


def test_compute_pairwise_scores_returns_unit_interval(tmp_path: Path) -> None:
    """Validation: pairwise scores must lie in [0, 1]."""
    subs = tmp_path / "submissions"
    subs.mkdir()
    for name, body in (("A.zip", "class A { int x = 1; }"), ("B.zip", "class B { int y = 2; }")):
        with zipfile.ZipFile(subs / name, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Main.java", body)

    zips = sorted(subs.glob("*.zip"))
    scores = compute_pairwise_similarity_scores(tmp_path, zips, language="java")
    assert len(scores) == 1
    for s in scores.values():
        assert 0.0 <= s <= 1.0


def test_external_eval_cli_csv_smoke(tmp_path: Path) -> None:
    """Validation: CLI prints CSV rows for a minimal assignment."""
    subs = tmp_path / "submissions"
    subs.mkdir()
    for name, body in (("A.zip", "class A { int x = 1; }"), ("B.zip", "class B { int y = 2; }")):
        with zipfile.ZipFile(subs / name, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Main.java", body)

    repo_root = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tests.analysis.external_eval",
            "--assignment-dir",
            str(tmp_path),
            "--language",
            "java",
            "--csv",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    lines = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
    assert lines[0] == "left,right,similarity,label"
    assert len(lines) == 2
