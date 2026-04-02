"""
Unit tests for analysis_service helper functions.

These tests run WITHOUT Docker — no network, no MongoDB, no worker.
They call the engine functions directly with synthetic inputs.

Test Plan:
- build_similarity_metrics:
  - identical texts → high score, non-empty regions
  - empty text(s) → score=0.0, no crash
  - completely different texts → low score
  - confidence always in [0.0, 1.0]
  - largestBlockSize always >= 0
  - required keys always present
- Line-mapping helpers (_line_starts, _offset_to_line):
  - single-line text
  - multi-line text
  - offset=0 edge
  - offset at end-of-file edge
- _merge_line_ranges:
  - empty input
  - non-overlapping ranges stay separate
  - overlapping ranges merge
  - adjacent ranges (end+1 == next start) merge
- resolve_pair_result_id:
  - pair with stored resultId returns it unchanged
  - pair missing resultId uses fallback "<run_id>-<index>"
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the backend importable without installing it
_BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.services.analysis_service import (
    _line_starts,
    _merge_line_ranges,
    _offset_to_line,
    build_similarity_metrics,
    resolve_pair_result_id,
)

# ---------------------------------------------------------------------------
# build_similarity_metrics — correctness
# ---------------------------------------------------------------------------

_JAVA_A = """\
public class Hello {
    public static void main(String[] args) {
        int x = 1;
        int y = 2;
        System.out.println(x + y);
    }
}
"""

_JAVA_B_IDENTICAL = _JAVA_A

_JAVA_C_DIFFERENT = """\
public class Goodbye {
    public static void farewell(String[] names) {
        for (String n : names) {
            System.out.println("bye " + n);
        }
    }
}
"""


def test_build_similarity_metrics_identical_texts_score_high() -> None:
    """Identical texts must produce Jaccard similarity = 1.0."""
    result = build_similarity_metrics(_JAVA_A, _JAVA_B_IDENTICAL)
    assert result["similarity"] == pytest.approx(1.0, abs=0.01), (
        f"Identical texts should have similarity ~1.0, got {result['similarity']}"
    )


def test_build_similarity_metrics_identical_texts_has_regions() -> None:
    """Identical texts must produce at least one matching region."""
    result = build_similarity_metrics(_JAVA_A, _JAVA_B_IDENTICAL)
    assert len(result["matchingRegions"]) > 0, "Expected at least one matchingRegion for identical texts"


def test_build_similarity_metrics_empty_text_a_returns_zero() -> None:
    """Empty left text → similarity 0.0, no crash."""
    result = build_similarity_metrics("", _JAVA_A)
    assert result["similarity"] == pytest.approx(0.0, abs=1e-9)
    assert result["matchingRegions"] == []


def test_build_similarity_metrics_empty_text_b_returns_zero() -> None:
    """Empty right text → similarity 0.0, no crash."""
    result = build_similarity_metrics(_JAVA_A, "")
    assert result["similarity"] == pytest.approx(0.0, abs=1e-9)


def test_build_similarity_metrics_both_empty_returns_zero() -> None:
    """Both texts empty → similarity 0.0, no crash."""
    result = build_similarity_metrics("", "")
    assert result["similarity"] == pytest.approx(0.0, abs=1e-9)


def test_build_similarity_metrics_different_texts_score_low() -> None:
    """Structurally different texts should have similarity < 0.5."""
    result = build_similarity_metrics(_JAVA_A, _JAVA_C_DIFFERENT)
    assert result["similarity"] < 0.5, (
        f"Different texts should have similarity < 0.5, got {result['similarity']}"
    )


def test_build_similarity_metrics_confidence_bounded() -> None:
    """confidence must always be in [0.0, 1.0]."""
    for text_a, text_b in [
        (_JAVA_A, _JAVA_B_IDENTICAL),
        (_JAVA_A, _JAVA_C_DIFFERENT),
        ("", _JAVA_A),
        (_JAVA_A, ""),
    ]:
        result = build_similarity_metrics(text_a, text_b)
        c = result["confidence"]
        label = repr(text_a)[:30]
        assert 0.0 <= c <= 1.0, f"confidence={c} out of [0,1] for input starting with {label}"


def test_build_similarity_metrics_largest_block_nonneg() -> None:
    """largestBlockSize must be >= 0 for any inputs."""
    for text_a, text_b in [
        (_JAVA_A, _JAVA_B_IDENTICAL),
        (_JAVA_A, _JAVA_C_DIFFERENT),
        ("", _JAVA_A),
    ]:
        result = build_similarity_metrics(text_a, text_b)
        assert result["largestBlockSize"] >= 0


def test_build_similarity_metrics_required_keys_present() -> None:
    """Result dict must always contain all required keys."""
    required = {
        "similarity",
        "matchingRegions",
        "excludedRegions",
        "summary",
        "confidence",
        "snippets",
        "largestBlockSize",
    }
    result = build_similarity_metrics(_JAVA_A, _JAVA_C_DIFFERENT)
    missing = required - set(result.keys())
    assert not missing, f"Missing keys in result: {missing}"


def test_build_similarity_metrics_matching_regions_schema() -> None:
    """Each matching region must have the required line-number fields."""
    result = build_similarity_metrics(_JAVA_A, _JAVA_B_IDENTICAL)
    for region in result["matchingRegions"]:
        for field in ("leftStartLine", "leftEndLine", "rightStartLine", "rightEndLine", "score", "evidenceType"):
            assert field in region, f"matchingRegion missing field: {field}"
        assert region["leftStartLine"] >= 1
        assert region["leftEndLine"] >= region["leftStartLine"]
        assert region["rightStartLine"] >= 1
        assert region["rightEndLine"] >= region["rightStartLine"]
        assert 0.0 <= region["score"] <= 1.0


def test_build_similarity_metrics_whitespace_only_text() -> None:
    """Whitespace-only text should behave like empty: score 0, no crash."""
    result = build_similarity_metrics("   \n\t  ", _JAVA_A)
    assert result["similarity"] == pytest.approx(0.0, abs=1e-9)


def test_build_similarity_metrics_similarity_is_symmetric() -> None:
    """Similarity of A vs B must equal similarity of B vs A."""
    result_ab = build_similarity_metrics(_JAVA_A, _JAVA_C_DIFFERENT)
    result_ba = build_similarity_metrics(_JAVA_C_DIFFERENT, _JAVA_A)
    assert result_ab["similarity"] == pytest.approx(result_ba["similarity"], abs=1e-6)


def test_build_similarity_metrics_deterministic() -> None:
    """Same inputs must always produce the same score (no randomness)."""
    r1 = build_similarity_metrics(_JAVA_A, _JAVA_C_DIFFERENT)
    r2 = build_similarity_metrics(_JAVA_A, _JAVA_C_DIFFERENT)
    assert r1["similarity"] == r2["similarity"]
    assert r1["confidence"] == r2["confidence"]
    assert r1["largestBlockSize"] == r2["largestBlockSize"]


# ---------------------------------------------------------------------------
# _line_starts
# ---------------------------------------------------------------------------


def test_line_starts_single_line() -> None:
    starts = _line_starts("hello")
    assert starts == [0]


def test_line_starts_two_lines() -> None:
    starts = _line_starts("hello\nworld")
    assert starts == [0, 6]


def test_line_starts_trailing_newline() -> None:
    # "hello\n" → line 1 starts at 0; char at index 5 is '\n', next char would
    # be index 6 but that's len(text), so no second entry
    starts = _line_starts("hello\n")
    assert starts == [0]


def test_line_starts_empty_string() -> None:
    starts = _line_starts("")
    assert starts == [0]


# ---------------------------------------------------------------------------
# _offset_to_line
# ---------------------------------------------------------------------------


def test_offset_to_line_first_char() -> None:
    text = "hello\nworld"
    starts = _line_starts(text)
    assert _offset_to_line(text, starts, 0) == 1


def test_offset_to_line_second_line() -> None:
    text = "hello\nworld"
    starts = _line_starts(text)
    # 'w' is at offset 6
    assert _offset_to_line(text, starts, 6) == 2


def test_offset_to_line_empty_text() -> None:
    result = _offset_to_line("", [0], 0)
    assert result == 1


def test_offset_to_line_clamps_negative() -> None:
    text = "hello\nworld"
    starts = _line_starts(text)
    assert _offset_to_line(text, starts, -5) == 1


# ---------------------------------------------------------------------------
# _merge_line_ranges
# ---------------------------------------------------------------------------


def test_merge_line_ranges_empty() -> None:
    assert _merge_line_ranges([]) == []


def test_merge_line_ranges_single() -> None:
    assert _merge_line_ranges([(3, 7)]) == [(3, 7)]


def test_merge_line_ranges_non_overlapping() -> None:
    result = _merge_line_ranges([(1, 3), (5, 7)])
    assert result == [(1, 3), (5, 7)]


def test_merge_line_ranges_overlapping() -> None:
    result = _merge_line_ranges([(1, 5), (3, 8)])
    assert result == [(1, 8)]


def test_merge_line_ranges_adjacent() -> None:
    # (1,3) and (4,6) are adjacent: 3+1 == 4 → should merge
    result = _merge_line_ranges([(1, 3), (4, 6)])
    assert result == [(1, 6)]


def test_merge_line_ranges_multiple() -> None:
    result = _merge_line_ranges([(1, 2), (2, 4), (10, 12)])
    assert result == [(1, 4), (10, 12)]


# ---------------------------------------------------------------------------
# resolve_pair_result_id
# ---------------------------------------------------------------------------


def test_resolve_pair_result_id_returns_stored() -> None:
    pair = {"resultId": "run123__subA__subB"}
    assert resolve_pair_result_id("run123", pair, 1) == "run123__subA__subB"


def test_resolve_pair_result_id_fallback_when_missing() -> None:
    pair = {}
    result = resolve_pair_result_id("run123", pair, 7)
    assert result == "run123-7"


def test_resolve_pair_result_id_fallback_when_empty_string() -> None:
    pair = {"resultId": ""}
    result = resolve_pair_result_id("run123", pair, 3)
    assert result == "run123-3"


# ---------------------------------------------------------------------------
# Template exclusion via build_similarity_metrics
# ---------------------------------------------------------------------------

_TEMPLATE_JAVA = """\
public class Template {
    public static void boilerplate() {
        int setup = 0;
        System.out.println("setup complete");
        String config = "default";
    }
}
"""

# Student A: template boilerplate + unique logic
_STUDENT_A = _TEMPLATE_JAVA + """\
public class StudentA {
    public void uniqueMethodAlpha() {
        int alpha = 42;
        System.out.println("alpha result: " + alpha);
    }
}
"""

# Student B: same template boilerplate + different unique logic
_STUDENT_B = _TEMPLATE_JAVA + """\
public class StudentB {
    public void uniqueMethodBeta() {
        int beta = 99;
        System.out.println("beta result: " + beta);
    }
}
"""


def test_template_exclusion_reduces_score() -> None:
    """
    Without exclusion, A and B share the template so they score high.
    With exclusion (template_text set), the shared template is subtracted
    and the score should drop significantly.
    """
    score_without = build_similarity_metrics(_STUDENT_A, _STUDENT_B)["similarity"]
    score_with = build_similarity_metrics(
        _STUDENT_A, _STUDENT_B, template_text=_TEMPLATE_JAVA
    )["similarity"]

    assert score_without > score_with, (
        f"Template exclusion should reduce score: "
        f"without={score_without:.3f}, with={score_with:.3f}"
    )
    assert score_with < 0.35, (
        f"After excluding shared template, score should be low (<0.35), got {score_with:.3f}"
    )


def test_template_exclusion_empty_template_is_noop() -> None:
    """Passing template_text='' must produce the same result as no template arg."""
    score_default = build_similarity_metrics(_STUDENT_A, _STUDENT_B)["similarity"]
    score_empty = build_similarity_metrics(
        _STUDENT_A, _STUDENT_B, template_text=""
    )["similarity"]
    assert score_default == pytest.approx(score_empty, abs=1e-9)


def test_template_exclusion_full_template_yields_zero() -> None:
    """If the template IS the entire submission, score after exclusion should be ~0."""
    score = build_similarity_metrics(
        _TEMPLATE_JAVA, _TEMPLATE_JAVA, template_text=_TEMPLATE_JAVA
    )["similarity"]
    assert score == pytest.approx(0.0, abs=0.05), (
        f"Score after excluding the full shared template should be ~0.0, got {score:.3f}"
    )


# ---------------------------------------------------------------------------
# Java-specific: tokenize path vs template-exclusion path
# ---------------------------------------------------------------------------
#
# These tests pass language="java" to exercise the override branch introduced
# by Charlotte in analysis_service.py.  They verify the hotfix: the Java token
# override must be skipped when template_text is present.
# ---------------------------------------------------------------------------

_JAVA_TEMPLATE = """\
public class Assignment {
    public static void setup() {
        System.out.println("setup");
        int boilerplate = 0;
        String config = "default";
    }
}
"""

# Two students: identical template boilerplate + independent unique logic
_JAVA_STUDENT_A = _JAVA_TEMPLATE + """\
public class StudentA {
    public void doWorkAlpha() {
        int alpha = 10;
        System.out.println("alpha: " + alpha);
    }
}
"""

_JAVA_STUDENT_B = _JAVA_TEMPLATE + """\
public class StudentB {
    public void doWorkBeta() {
        int beta = 20;
        System.out.println("beta: " + beta);
    }
}
"""

# Renamed copy of _JAVA_STUDENT_A (all identifiers changed, same structure)
_JAVA_STUDENT_A_RENAMED = """\
public class Assignment {
    public static void initialize() {
        System.out.println("setup");
        int placeholder = 0;
        String setting = "default";
    }
}
public class StudentX {
    public void executeAlpha() {
        int valueX = 10;
        System.out.println("alpha: " + valueX);
    }
}
"""

_CPP_A = """\
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
"""

_CPP_B_IDENTICAL = _CPP_A


def test_java_with_template_score_lower_than_without() -> None:
    """
    Hotfix assertion: when language='java' and template_text is provided,
    the shared template must be excluded from the score.

    Before the fix the Java token override ignored template_text, so both
    calls returned the same value.  After the fix the score with template
    must be strictly lower than without.
    """
    score_without = build_similarity_metrics(
        _JAVA_STUDENT_A, _JAVA_STUDENT_B, language="java"
    )["similarity"]
    score_with = build_similarity_metrics(
        _JAVA_STUDENT_A, _JAVA_STUDENT_B, template_text=_JAVA_TEMPLATE, language="java"
    )["similarity"]

    assert score_with < score_without, (
        f"Java+template score ({score_with:.4f}) must be lower than "
        f"Java-no-template score ({score_without:.4f})"
    )


def test_java_no_template_still_uses_tokenize_path() -> None:
    """
    Regression guard: without a template, Java scoring must still be
    rename-robust (tokenize path).

    A renamed copy of the same code should score >= 0.85 via the tokenize
    pipeline.  The character-based path would score it ~0.4-0.6 due to
    identifier differences.
    """
    score = build_similarity_metrics(
        _JAVA_STUDENT_A, _JAVA_STUDENT_A_RENAMED, language="java"
    )["similarity"]
    assert score >= 0.70, (
        f"Java rename-robustness regression: expected >= 0.70, got {score:.4f}. "
        "This suggests the tokenize path is no longer being used."
    )


def test_non_java_with_template_behavior_unchanged() -> None:
    """
    Non-Java languages must not be affected by the Java hotfix.
    C++ identical texts with no template should still score ~1.0.
    """
    result = build_similarity_metrics(_CPP_A, _CPP_B_IDENTICAL, language="c++")
    assert result["similarity"] == pytest.approx(1.0, abs=0.01), (
        f"Identical C++ texts should score ~1.0, got {result['similarity']:.4f}"
    )


# ---------------------------------------------------------------------------
# Phase B: AST/token adapter contract tests
# ---------------------------------------------------------------------------

def test_java_with_template_uses_ast_exclusion() -> None:
    """
    Phase B guard: Java submissions must go through the AST/token path.

    The AST path stamps evidenceType='tokenize_group' on every matching region.
    The character-winnowing path stamps evidenceType='winnowing_group'.

    We use the renamed-copy pair WITHOUT a template because after template
    exclusion both sides are reduced to small independent student classes that
    produce no matching groups (correct engine behaviour, not a failure).
    The no-template variant retains the full code and produces high-similarity
    matching regions, letting us verify the evidenceType marker unambiguously.
    """
    result = build_similarity_metrics(
        _JAVA_STUDENT_A, _JAVA_STUDENT_A_RENAMED,
        language="java",
    )
    regions = result["matchingRegions"]
    assert len(regions) > 0, (
        "Expected matching regions for a renamed-copy Java pair (no template). "
        "test_java_no_template_still_uses_tokenize_path already guards the score "
        ">= 0.85, so regions must be non-empty."
    )
    for r in regions:
        assert r["evidenceType"] == "tokenize_group", (
            f"Expected evidenceType='tokenize_group' (AST path) but got "
            f"'{r['evidenceType']}'. Java may be falling back to character winnowing."
        )


def test_java_tokenize_adapter_all_fields_present() -> None:
    """
    Phase B contract: build_similarity_metrics with language='java' must return
    all 7 required fields with correct types, whether or not a template is used.
    """
    for label, kwargs in [
        ("no template", {"language": "java"}),
        ("with template", {"language": "java", "template_text": _JAVA_TEMPLATE}),
    ]:
        result = build_similarity_metrics(_JAVA_STUDENT_A, _JAVA_STUDENT_B, **kwargs)

        assert isinstance(result["similarity"], float), f"[{label}] similarity must be float"
        assert 0.0 <= result["similarity"] <= 1.0, f"[{label}] similarity out of range"

        assert isinstance(result["matchingRegions"], list), f"[{label}] matchingRegions must be list"
        for r in result["matchingRegions"]:
            assert "leftStartLine" in r and "leftEndLine" in r, f"[{label}] region missing line keys"
            assert "score" in r, f"[{label}] region missing 'score'"
            assert "evidenceType" in r, f"[{label}] region missing 'evidenceType'"
            assert "snippet" in r, f"[{label}] region missing 'snippet'"
            assert isinstance(r["score"], float), f"[{label}] region score must be float"

        assert isinstance(result["excludedRegions"], list), f"[{label}] excludedRegions must be list"
        assert isinstance(result["confidence"], float), f"[{label}] confidence must be float"
        assert 0.0 <= result["confidence"] <= 1.0, f"[{label}] confidence out of range"
        assert isinstance(result["snippets"], list), f"[{label}] snippets must be list"
        assert isinstance(result["largestBlockSize"], int), f"[{label}] largestBlockSize must be int"
        assert result["largestBlockSize"] >= 0, f"[{label}] largestBlockSize must be >= 0"
        assert isinstance(result["summary"], str), f"[{label}] summary must be str"
        assert result["summary"], f"[{label}] summary must not be empty"


# ---------------------------------------------------------------------------
# Phase D: dependency guard + C/C++ dispatch isolation
# ---------------------------------------------------------------------------

def test_requirements_include_tokenize_runtime_dependencies() -> None:
    """
    Guard: backend/requirements.txt must list pandas and numpy.
    Without them the Java tokenize pipeline fails to import at container
    startup and silently falls back to character winnowing.
    """
    req_path = Path(__file__).resolve().parents[2] / "backend" / "requirements.txt"
    assert req_path.is_file(), f"requirements.txt not found at {req_path}"
    contents = req_path.read_text(encoding="utf-8").lower()
    assert "pandas" in contents, "pandas missing from requirements.txt"
    assert "numpy" in contents, "numpy missing from requirements.txt"


def test_c_cpp_dispatch_uses_tokenize_path() -> None:
    """
    C and C++ now use the AST/token pipeline (PR #35).
    Verify via evidenceType on matching regions.
    """
    for lang, label in [("c", "C"), ("cpp", "C++")]:
        result = build_similarity_metrics(
            _CPP_A, _CPP_B_IDENTICAL, language=lang,
        )
        for r in result["matchingRegions"]:
            assert r["evidenceType"] == "tokenize_group", (
                f"[{label}] Expected evidenceType='tokenize_group' but got "
                f"'{r['evidenceType']}'. {label} should use the tokenize pipeline."
            )


# ---------------------------------------------------------------------------
# Phase 6: Constraint/Validation Audit Regression Tests
# ---------------------------------------------------------------------------

# --- R4: Language enum validation ---


def test_assignment_language_enum_rejects_invalid():
    """Pydantic schema must reject unsupported language values."""
    from pydantic import ValidationError

    from app.schemas.assignment import AssignmentCreateRequest

    # Valid languages must succeed
    for lang in ("java", "c", "cpp"):
        req = AssignmentCreateRequest(courseId="abc", title="Test", language=lang)
        assert req.language == lang

    # Invalid languages must be rejected
    for bad in ("python", "rust", "javascript", "", "JAVA "):
        with pytest.raises(ValidationError):
            AssignmentCreateRequest(courseId="abc", title="Test", language=bad)


# --- R5: Unsupported language raises ValueError ---


def test_normalize_language_rejects_unsupported():
    """_normalize_assignment_language must raise ValueError for bad languages."""
    from app.services.analysis_service import _normalize_assignment_language

    for good in ("java", "c", "cpp", " Java ", "CPP"):
        result = _normalize_assignment_language(good)
        assert result in ("java", "c", "cpp")

    for bad in ("python", "rust", "", None, 42):
        with pytest.raises(ValueError, match="[Uu]nsupported|missing"):
            _normalize_assignment_language(bad)


# --- R7: Parse Quality Score ---


def test_pqs_valid_java_above_threshold():
    """Valid Java code must produce PQS above the low-quality threshold."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.java_leaf_tokenize import (
        tokenize_java,
    )
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        PARSE_QUALITY_THRESHOLD,
        compute_parse_quality_score,
    )

    java_code = (
        "public class Solution {\n"
        "    public static int add(int a, int b) { return a + b; }\n"
        "    public static void main(String[] args) {\n"
        '        System.out.println(add(2, 3));\n'
        "    }\n"
        "}\n"
    )
    tokens = tokenize_java(java_code)
    pqs = compute_parse_quality_score(tokens, language="java")
    assert pqs >= PARSE_QUALITY_THRESHOLD, (
        f"Valid Java should have PQS >= {PARSE_QUALITY_THRESHOLD}, got {pqs:.4f}"
    )


def test_pqs_python_as_java_below_threshold():
    """Python code parsed as Java must produce PQS below the low-quality threshold."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.java_leaf_tokenize import (
        tokenize_java,
    )
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        PARSE_QUALITY_THRESHOLD,
        compute_parse_quality_score,
    )

    python_code = (
        "def add(a, b):\n"
        "    return a + b\n"
        "\n"
        "def main():\n"
        "    print(add(2, 3))\n"
        "\n"
        "main()\n"
    )
    tokens = tokenize_java(python_code)
    pqs = compute_parse_quality_score(tokens, language="java")
    assert pqs < PARSE_QUALITY_THRESHOLD, (
        f"Python-as-Java should have PQS < {PARSE_QUALITY_THRESHOLD}, got {pqs:.4f}"
    )


def test_pqs_valid_c_above_threshold():
    """Valid C code must produce PQS above the low-quality threshold."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.c_leaf_tokenize import (
        tokenize_c,
    )
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        PARSE_QUALITY_THRESHOLD,
        compute_parse_quality_score,
    )

    c_code = (
        "#include <stdio.h>\n"
        "int add(int a, int b) { return a + b; }\n"
        "int main() {\n"
        '    printf("%d\\n", add(2, 3));\n'
        "    return 0;\n"
        "}\n"
    )
    tokens = tokenize_c(c_code)
    pqs = compute_parse_quality_score(tokens, language="c")
    assert pqs >= PARSE_QUALITY_THRESHOLD, (
        f"Valid C should have PQS >= {PARSE_QUALITY_THRESHOLD}, got {pqs:.4f}"
    )


def test_pqs_empty_tokens_returns_zero():
    """Empty token list produces PQS = 0.0."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        compute_parse_quality_score,
    )

    assert compute_parse_quality_score([], language="java") == 0.0


# --- R9: analysisMethod distinguishes tokenize from error fallback ---


def test_build_similarity_metrics_includes_evidence_type():
    """build_similarity_metrics must include evidenceType in matching regions."""
    result = build_similarity_metrics(
        _JAVA_STUDENT_A, _JAVA_STUDENT_A_RENAMED, language="java"
    )
    for r in result["matchingRegions"]:
        assert "evidenceType" in r
        assert r["evidenceType"] in ("tokenize_group", "winnowing_group")


# --- R11: warnings field in schemas ---


def test_run_status_schema_has_warnings():
    """RunStatusResponse must have warnings, pairsAnalyzed, pairsFailed fields."""
    from app.schemas.analysis import RunStatusResponse

    resp = RunStatusResponse(
        runId="r1",
        assignmentId="a1",
        courseId="c1",
        status="completed",
        algorithmVersion="v1",
        createdAt="2026-01-01",
        warnings=["test warning"],
        pairsAnalyzed=3,
        pairsFailed=1,
    )
    assert resp.warnings == ["test warning"]
    assert resp.pairsAnalyzed == 3
    assert resp.pairsFailed == 1


def test_similarity_list_item_has_analysis_method():
    """SimilarityResultListItem must have analysisMethod and warnings fields."""
    from app.schemas.similarity import SimilarityResultListItem

    item = SimilarityResultListItem(
        resultId="r1",
        runId="run1",
        assignmentId="a1",
        leftSubmissionId="s1",
        leftStudentIdentifier="alice",
        rightSubmissionId="s2",
        rightStudentIdentifier="bob",
        similarityScore=0.5,
        analysisMethod="error_fallback",
        warnings=["Pipeline error"],
    )
    assert item.analysisMethod == "error_fallback"
    assert item.warnings == ["Pipeline error"]


def test_comparison_response_has_warnings():
    """SimilarityComparisonResponse must have analysisMethod and warnings fields."""
    from app.schemas.similarity import SimilarityComparisonResponse

    resp = SimilarityComparisonResponse(
        resultId="r1",
        runId="run1",
        assignmentId="a1",
        leftSubmissionId="s1",
        leftStudentIdentifier="alice",
        rightSubmissionId="s2",
        rightStudentIdentifier="bob",
        similarityScore=0.5,
        leftFilePath="/a",
        rightFilePath="/b",
        leftCode="code",
        rightCode="code",
        matchingRegions=[],
        excludedRegions=[],
        summary="test",
        confidence=0.5,
        snippets=[],
        analysisMethod="tokenize",
        warnings=["Low parse quality"],
    )
    assert resp.analysisMethod == "tokenize"
    assert resp.warnings == ["Low parse quality"]


# --- R7 warning propagation: leaf_tokens_and_truth returns 3-tuple ---


def test_leaf_tokens_returns_3_tuple_with_pqs():
    """leaf_tokens_and_truth_for_filter must return (tokens, df, pqs) 3-tuple."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        leaf_tokens_and_truth_for_filter,
    )
    from app.analysis.config import load_active_tokenize_pipeline_config

    cfg = load_active_tokenize_pipeline_config()

    java_code = (
        "public class Foo {\n"
        "    public static void main(String[] args) {}\n"
        "}\n"
    )
    result = leaf_tokens_and_truth_for_filter(
        java_code,
        cfg.type_mapping,
        default_categories=cfg.default_categories,
        language="java",
    )
    assert len(result) == 3, f"Expected 3-tuple, got {len(result)}-tuple"
    tokens, df, pqs = result
    assert isinstance(pqs, float)
    assert 0.0 <= pqs <= 1.0


# ---------------------------------------------------------------------------
# Upload-time PQS validation (quick_parse_quality + thresholds)
# ---------------------------------------------------------------------------


def test_quick_parse_quality_valid_java():
    """Valid Java merged source should have PQS well above the reject threshold."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        UPLOAD_REJECT_PQS_THRESHOLD,
        quick_parse_quality,
    )

    merged = (
        "//// FILE: Solution.java\n"
        "public class Solution {\n"
        "    public static int add(int a, int b) { return a + b; }\n"
        "    public static void main(String[] args) {\n"
        '        System.out.println(add(2, 3));\n'
        "    }\n"
        "}\n"
    )
    pqs, count = quick_parse_quality(merged, language="java")
    assert count > 0
    assert pqs >= UPLOAD_REJECT_PQS_THRESHOLD, (
        f"Valid Java should pass upload PQS check: {pqs:.4f} >= {UPLOAD_REJECT_PQS_THRESHOLD}"
    )


def test_quick_parse_quality_valid_c():
    """Valid C merged source should have PQS well above the reject threshold."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        UPLOAD_REJECT_PQS_THRESHOLD,
        quick_parse_quality,
    )

    merged = (
        "//// FILE: main.c\n"
        "#include <stdio.h>\n"
        "int add(int a, int b) { return a + b; }\n"
        "int main() {\n"
        '    printf(\"%d\\n\", add(2, 3));\n'
        "    return 0;\n"
        "}\n"
    )
    pqs, count = quick_parse_quality(merged, language="c")
    assert count > 0
    assert pqs >= UPLOAD_REJECT_PQS_THRESHOLD, (
        f"Valid C should pass upload PQS check: {pqs:.4f} >= {UPLOAD_REJECT_PQS_THRESHOLD}"
    )


def test_quick_parse_quality_valid_cpp():
    """Valid C++ merged source should have PQS well above the reject threshold."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        UPLOAD_REJECT_PQS_THRESHOLD,
        quick_parse_quality,
    )

    merged = (
        "//// FILE: solution.cpp\n"
        "#include <iostream>\n"
        "int add(int a, int b) { return a + b; }\n"
        "int main() {\n"
        "    std::cout << add(2, 3) << std::endl;\n"
        "    return 0;\n"
        "}\n"
    )
    pqs, count = quick_parse_quality(merged, language="cpp")
    assert count > 0
    assert pqs >= UPLOAD_REJECT_PQS_THRESHOLD, (
        f"Valid C++ should pass upload PQS check: {pqs:.4f} >= {UPLOAD_REJECT_PQS_THRESHOLD}"
    )


def test_quick_parse_quality_python_in_java_rejected():
    """Python code in a .java merged source should score below the reject threshold."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        UPLOAD_MIN_TOKENS_FOR_PQS,
        UPLOAD_REJECT_PQS_THRESHOLD,
        quick_parse_quality,
    )

    merged = (
        "//// FILE: Solution.java\n"
        "def add(a, b):\n"
        "    return a + b\n"
        "\n"
        "def multiply(x, y):\n"
        "    return x * y\n"
        "\n"
        "print(add(2, 3))\n"
        "print(multiply(4, 5))\n"
    )
    pqs, count = quick_parse_quality(merged, language="java")
    assert count >= UPLOAD_MIN_TOKENS_FOR_PQS, (
        f"Test expects enough tokens to trigger check: got {count}"
    )
    assert pqs < UPLOAD_REJECT_PQS_THRESHOLD, (
        f"Python-in-Java should be rejected: {pqs:.4f} < {UPLOAD_REJECT_PQS_THRESHOLD}"
    )


def test_quick_parse_quality_javascript_in_java_rejected():
    """JavaScript code in a .java merged source should score below the reject threshold."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        UPLOAD_MIN_TOKENS_FOR_PQS,
        UPLOAD_REJECT_PQS_THRESHOLD,
        quick_parse_quality,
    )

    merged = (
        "//// FILE: Solution.java\n"
        "const add = (a, b) => a + b;\n"
        "console.log(add(2, 3));\n"
        "function multiply(x, y) { return x * y; }\n"
        "console.log(multiply(4, 5));\n"
    )
    pqs, count = quick_parse_quality(merged, language="java")
    assert count >= UPLOAD_MIN_TOKENS_FOR_PQS
    assert pqs < UPLOAD_REJECT_PQS_THRESHOLD, (
        f"JavaScript-in-Java should be rejected: {pqs:.4f} < {UPLOAD_REJECT_PQS_THRESHOLD}"
    )


def test_quick_parse_quality_python_in_c_rejected():
    """Python code in a .c merged source should score below the reject threshold.

    Regression: before removing type_identifier from C expected leaf types,
    Python-in-C scored PQS ~0.07 (above 0.05) because tree-sitter mapped
    Python keywords like 'def' and 'import' to type_identifier.
    """
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        UPLOAD_MIN_TOKENS_FOR_PQS,
        UPLOAD_REJECT_PQS_THRESHOLD,
        quick_parse_quality,
    )

    merged = (
        "//// FILE: sorter.c\n"
        "def bubble_sort(arr):\n"
        "    n = len(arr)\n"
        "    for i in range(n):\n"
        "        for j in range(0, n - i - 1):\n"
        "            if arr[j] > arr[j + 1]:\n"
        "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
        "    return arr\n"
        "\n"
        "class Sorter:\n"
        "    def __init__(self, data):\n"
        "        self.data = list(data)\n"
        "    def sort(self):\n"
        "        return bubble_sort(self.data)\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    s = Sorter([64, 34, 25, 12, 22, 11, 90])\n"
    )
    pqs, count = quick_parse_quality(merged, language="c")
    assert count >= UPLOAD_MIN_TOKENS_FOR_PQS, (
        f"Test expects enough tokens to trigger check: got {count}"
    )
    assert pqs < UPLOAD_REJECT_PQS_THRESHOLD, (
        f"Python-in-C should be rejected: {pqs:.4f} < {UPLOAD_REJECT_PQS_THRESHOLD}"
    )


def test_quick_parse_quality_python_in_cpp_rejected():
    """Python code in a .cpp merged source should score below the reject threshold."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        UPLOAD_MIN_TOKENS_FOR_PQS,
        UPLOAD_REJECT_PQS_THRESHOLD,
        quick_parse_quality,
    )

    merged = (
        "//// FILE: solution.cpp\n"
        "import os\n"
        "import sys\n"
        "from collections import defaultdict\n"
        "\n"
        "def count_words(filename):\n"
        "    counts = defaultdict(int)\n"
        "    with open(filename) as f:\n"
        "        for line in f:\n"
        "            for word in line.strip().split():\n"
        "                counts[word] += 1\n"
        "    return dict(counts)\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    result = count_words(sys.argv[1])\n"
    )
    pqs, count = quick_parse_quality(merged, language="cpp")
    assert count >= UPLOAD_MIN_TOKENS_FOR_PQS, (
        f"Test expects enough tokens to trigger check: got {count}"
    )
    assert pqs < UPLOAD_REJECT_PQS_THRESHOLD, (
        f"Python-in-C++ should be rejected: {pqs:.4f} < {UPLOAD_REJECT_PQS_THRESHOLD}"
    )


def test_type_identifier_not_in_c_cpp_expected_types():
    """type_identifier must NOT be in C/C++ expected leaf types.

    It inflates PQS for wrong-language code because tree-sitter maps
    unrecognized identifiers (like Python's 'def') to type_identifier.
    """
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        _EXPECTED_LEAF_TYPES,
    )

    assert "type_identifier" not in _EXPECTED_LEAF_TYPES["c"], (
        "type_identifier should not be in C expected leaf types"
    )
    assert "type_identifier" not in _EXPECTED_LEAF_TYPES["cpp"], (
        "type_identifier should not be in C++ expected leaf types"
    )


def test_quick_parse_quality_too_few_tokens_skips_check():
    """If token count is below minimum, PQS check should not be used for rejection."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        UPLOAD_MIN_TOKENS_FOR_PQS,
        quick_parse_quality,
    )

    # Very short file — too few tokens to be meaningful
    merged = "//// FILE: A.java\n// just a comment\n"
    pqs, count = quick_parse_quality(merged, language="java")
    assert count < UPLOAD_MIN_TOKENS_FOR_PQS, (
        f"This short file should produce fewer than {UPLOAD_MIN_TOKENS_FOR_PQS} tokens, got {count}"
    )


def test_quick_parse_quality_empty_code():
    """Empty code should return (0.0, 0)."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        quick_parse_quality,
    )

    pqs, count = quick_parse_quality("", language="java")
    assert pqs == 0.0
    assert count == 0


def test_quick_parse_quality_unsupported_language():
    """Unsupported language should return (0.0, 0) without error."""
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
        quick_parse_quality,
    )

    pqs, count = quick_parse_quality("some code", language="python")
    assert pqs == 0.0
    assert count == 0
