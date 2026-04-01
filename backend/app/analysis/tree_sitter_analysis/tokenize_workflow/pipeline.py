"""
Demonstrates how compare_javacode pieces are wired.

Run from this directory:
  python pipeline.py
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

try:
    from app.analysis.tree_sitter_analysis.tokenize_workflow.compare_javacode import (
        UnimplementedJavaKgramStrategy,
        compare_java_code,
    )
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_fingerprint import (
        Fingerprint,
        Token,
    )
except ImportError:
    from compare_javacode import (  # type: ignore[no-redef]
        UnimplementedJavaKgramStrategy,
        compare_java_code,
    )
    from token_fingerprint import Fingerprint, Token  # type: ignore[no-redef]


_DEMO_CONSTANT_HASHES = [1, 2, 3, 42, 7, 8]


class _DemoConstantKgrams:
    """Demo: fixed k-gram fingerprint sequence for any non-empty source."""

    def tokens_for_kgram(self, code: str) -> list[Token]:
        if not code.strip():
            return []
        return [
            Token(
                type="demo",
                text="x",
                start_byte=i,
                end_byte=i + 1,
                start_line=1,
                end_line=1,
            )
            for i in range(len(_DEMO_CONSTANT_HASHES))
        ]

    def compute_kgram_fingerprints(self, tokens: Sequence[Token]) -> list[Fingerprint]:
        if not tokens:
            return []
        return [
            Fingerprint(
                hash_value=h,
                start_byte=0,
                end_byte=0,
                token_start_index=i,
                token_end_index=i + 1,
                start_line=1,
                end_line=1,
            )
            for i, h in enumerate(_DEMO_CONSTANT_HASHES)
        ]


class _DemoPerSourceKgrams:
    """Demo: one k-gram fingerprint per source string; Winnow reduces to one hash."""

    def tokens_for_kgram(self, code: str) -> list[Token]:
        if not code.strip():
            return []
        s = code.strip()
        b = s.encode("utf-8")
        return [
            Token(
                type="demo",
                text=s,
                start_byte=0,
                end_byte=len(b),
                start_line=1,
                end_line=1,
            )
        ]

    def compute_kgram_fingerprints(self, tokens: Sequence[Token]) -> list[Fingerprint]:
        if not tokens:
            return []
        h = hash(tokens[0].text) & 0x7FFF_FFFF
        return [
            Fingerprint(
                hash_value=h,
                start_byte=0,
                end_byte=0,
                token_start_index=0,
                token_end_index=1,
                start_line=1,
                end_line=1,
            )
        ]


def run_pipeline_demo(code_a: str, code_b: str) -> None:
    print("--- constant k-gram demo (same strategy, same code -> expect 1.0) ---")
    s1 = compare_java_code(code_a, code_b, strategy=_DemoConstantKgrams())
    print(f"  similarity: {s1:.4f}")

    print("--- per-string single k-gram demo (different sources -> often low) ---")
    s2 = compare_java_code(code_a, code_b, strategy=_DemoPerSourceKgrams())
    print(f"  similarity: {s2:.4f}")

    print("--- UnimplementedJavaKgramStrategy (expect NotImplementedError) ---")
    try:
        compare_java_code(code_a, code_b, strategy=UnimplementedJavaKgramStrategy())
    except NotImplementedError as e:
        print(f"  {e}")


def main() -> None:
    root = Path(__file__).resolve().parent
    p = root / "sample.java"
    text = p.read_text(encoding="utf-8") if p.is_file() else "class X {}"
    print(f"Using sample: {p.name if p.is_file() else 'inline fallback'}\n")
    run_pipeline_demo(text, text)
    print()
    run_pipeline_demo(text, text + "\n// tail comment")


if __name__ == "__main__":
    main()
