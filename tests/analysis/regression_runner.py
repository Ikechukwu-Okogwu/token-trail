"""Regression fixture runner for direct engine evaluation.

This module loads assignment-style fixture folders, applies the same ZIP/source
selection and merge pipeline used by the backend, computes pairwise similarity
directly from the engine, and validates results against fixture expectations.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.analysis.testWinowingCode.testWinowingLib import compare_texts_with_template
from app.services.merge_service import merge_source_files
from app.services.zip_service import LANGUAGE_EXTENSIONS, list_valid_source_files, safe_extract_zip


LABEL_BOUNDS = {
    "high": (0.80, 1.00),
    "medium": (0.40, 0.80),
    "low": (0.00, 0.40),
}
SUPPORTED_LANGUAGES = tuple(sorted(LANGUAGE_EXTENSIONS.keys()))
SUPPORTED_SOURCE_EXTENSIONS = set().union(*LANGUAGE_EXTENSIONS.values())


class FixtureValidationError(ValueError):
    """Raised when a fixture is malformed or violates runner constraints."""


@dataclass(frozen=True)
class PairExpectation:
    """Expected score metadata for one pair."""

    left: str
    right: str
    expected: float
    range_min: float
    range_max: float
    label: str


def canonical_pair_key(left: str, right: str) -> tuple[str, str]:
    """Return a deterministic pair key that is order-independent."""
    if left == right:
        raise FixtureValidationError(f"Pair must contain two distinct submissions: {left}")
    return tuple(sorted((left, right)))


def score_to_label(score: float) -> str:
    """Map a normalized similarity score to the expected label bucket."""
    if score >= LABEL_BOUNDS["high"][0]:
        return "high"
    if score >= LABEL_BOUNDS["medium"][0]:
        return "medium"
    return "low"


def _parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes"}:
        return True
    if lowered in {"false", "0", "no"}:
        return False
    raise FixtureValidationError(f"Invalid boolean value: {value!r}")


def _parse_float(value: str, name: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise FixtureValidationError(f"Invalid float for {name}: {value!r}") from exc
    if not (0.0 <= parsed <= 1.0):
        raise FixtureValidationError(f"{name} must be in [0,1], got {parsed}")
    return parsed


def parse_result_file(result_path: Path) -> tuple[dict[str, str], dict[tuple[str, str], PairExpectation]]:
    """Parse fixture metadata and pair expectations from result.txt."""
    if not result_path.exists():
        raise FixtureValidationError(f"Missing fixture result file: {result_path}")

    metadata: dict[str, str] = {}
    expectations: dict[tuple[str, str], PairExpectation] = {}

    for raw_line in result_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "," not in line:
            if "=" not in line:
                raise FixtureValidationError(f"Invalid metadata line: {line!r}")
            key, value = line.split("=", 1)
            metadata[key.strip()] = value.strip()
            continue

        fields = [x.strip() for x in line.split(",") if x.strip()]
        if len(fields) < 5:
            raise FixtureValidationError(f"Invalid pair line (expected 5+ fields): {line!r}")

        left = fields[0]
        right = fields[1]
        kv_map: dict[str, str] = {}
        for field in fields[2:]:
            if "=" not in field:
                raise FixtureValidationError(f"Invalid key=value field in pair line: {field!r}")
            key, value = field.split("=", 1)
            kv_map[key.strip()] = value.strip()

        if "range" not in kv_map:
            raise FixtureValidationError(f"Pair line missing range=...: {line!r}")
        if "label" not in kv_map:
            raise FixtureValidationError(f"Pair line missing label=...: {line!r}")

        range_parts = kv_map["range"].split("-", 1)
        if len(range_parts) != 2:
            raise FixtureValidationError(f"Invalid range format (min-max): {kv_map['range']!r}")
        range_min = _parse_float(range_parts[0], "range_min")
        range_max = _parse_float(range_parts[1], "range_max")
        if range_min > range_max:
            raise FixtureValidationError(f"Range min cannot exceed max: {kv_map['range']!r}")

        expected = _parse_float(kv_map.get("expected", str((range_min + range_max) / 2.0)), "expected")

        label = kv_map["label"].lower()
        if label not in LABEL_BOUNDS:
            raise FixtureValidationError(f"Unknown label {label!r}; expected one of {sorted(LABEL_BOUNDS)}")

        key = canonical_pair_key(left, right)
        if key in expectations:
            raise FixtureValidationError(f"Duplicate expectation entry for pair {key}")

        expectations[key] = PairExpectation(
            left=left,
            right=right,
            expected=expected,
            range_min=range_min,
            range_max=range_max,
            label=label,
        )

    if "language" not in metadata:
        raise FixtureValidationError(f"Missing required metadata key language in {result_path}")
    if metadata["language"] not in SUPPORTED_LANGUAGES:
        raise FixtureValidationError(
            f"Unsupported language {metadata['language']!r}; expected one of {SUPPORTED_LANGUAGES}"
        )
    if "homogeneous" in metadata and not _parse_bool(metadata["homogeneous"]):
        raise FixtureValidationError("Fixture metadata homogeneous must be true")

    return metadata, expectations


def _validate_no_mixed_supported_languages(extracted_dir: Path, language: str, zip_name: str) -> None:
    allowed = LANGUAGE_EXTENSIONS[language]
    for path in extracted_dir.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in SUPPORTED_SOURCE_EXTENSIONS and suffix not in allowed:
            rel = path.relative_to(extracted_dir).as_posix()
            raise FixtureValidationError(
                f"Mixed-language submission in {zip_name}: {rel} ({suffix}) is not valid for {language}"
            )


def _build_merged_text_for_zip(zip_path: Path, language: str, work_dir: Path) -> str:
    extracted_dir = work_dir / zip_path.stem
    extracted_dir.mkdir(parents=True, exist_ok=True)
    safe_extract_zip(zip_path=zip_path, dest_dir=extracted_dir)
    _validate_no_mixed_supported_languages(extracted_dir, language, zip_path.name)

    source_files = list_valid_source_files(extracted_dir, language)
    if not source_files:
        raise FixtureValidationError(
            f"{zip_path.name} has no valid source files for language {language}. "
            "Every submission fixture must contain at least one valid source file."
        )

    merged_path = extracted_dir / "_merged.txt"
    merge_source_files(source_files=source_files, base_dir=extracted_dir, output_path=merged_path)
    return merged_path.read_text(encoding="utf-8", errors="replace")


def _load_template_text(assignment_dir: Path, language: str, work_dir: Path) -> str:
    template_txt = assignment_dir / "template.txt"
    if template_txt.exists():
        return template_txt.read_text(encoding="utf-8", errors="replace")

    template_zip = assignment_dir / "template.zip"
    if template_zip.exists():
        return _build_merged_text_for_zip(template_zip, language, work_dir / "_template")

    return ""


def run_fixture_assignment(assignment_dir: Path) -> tuple[dict[tuple[str, str], float], dict[str, str], dict[tuple[str, str], PairExpectation]]:
    """Compute all pairwise scores for one assignment fixture directory."""
    result_path = assignment_dir / "result.txt"
    metadata, expectations = parse_result_file(result_path)
    language = metadata["language"]

    submissions_dir = assignment_dir / "submissions"
    if not submissions_dir.exists():
        raise FixtureValidationError(f"Missing submissions directory: {submissions_dir}")

    submission_zips = sorted(submissions_dir.glob("*.zip"))
    if len(submission_zips) < 2:
        raise FixtureValidationError(f"Expected at least 2 submission zips in {submissions_dir}")

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

        scores: dict[tuple[str, str], float] = {}
        for left_name, right_name in combinations(sorted(merged_text_by_zip.keys()), 2):
            key = canonical_pair_key(left_name, right_name)
            left_text = merged_text_by_zip[left_name]
            right_text = merged_text_by_zip[right_name]
            template = template_text if use_template else ""
            result = compare_texts_with_template(left_text, right_text, template, k=5, name_a=left_name, name_b=right_name)
            scores[key] = float(result["similarity"])

    return scores, metadata, expectations


def validate_fixture_assignment(assignment_dir: Path, *, expected_tolerance: float = 0.06) -> list[str]:
    """Return a list of mismatch messages; empty list means success."""
    if expected_tolerance < 0:
        raise FixtureValidationError("expected_tolerance must be >= 0")

    scores, metadata, expectations = run_fixture_assignment(assignment_dir)
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
