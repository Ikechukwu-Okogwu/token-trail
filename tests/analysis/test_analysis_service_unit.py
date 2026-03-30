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
    assert score >= 0.85, (
        f"Java rename-robustness regression: expected >= 0.85, got {score:.4f}. "
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
