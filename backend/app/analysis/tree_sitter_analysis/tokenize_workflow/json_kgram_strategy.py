"""
JavaKgramStrategy: Tree-sitter leaf tokens + compact JSON k-gram blobs + SHA1 (8 hex).

Uses the same truncation style as ``testWinowingCode.winnowingCopy.default_hash``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Sequence
from pathlib import Path

_backend = Path(__file__).resolve().parents[4]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.tree_sitter_analysis.tokenize_workflow.compare_javacode import (
    compare_java_code,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.token_fingerprint import (
    Fingerprint,
    Token,
)

_default_type_mapping_for_kgram: dict[str, frozenset[str]] | None = None


def _get_default_type_mapping() -> dict[str, frozenset[str]]:
    """Load ``type_mapping.csv`` once; ``to_drop`` rows control comment/noise stripping."""
    global _default_type_mapping_for_kgram
    if _default_type_mapping_for_kgram is None:
        from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import (
            load_type_mapping_csv,
        )

        path = Path(__file__).resolve().parent / "type_mapping.csv"
        _default_type_mapping_for_kgram = load_type_mapping_csv(path)
    return _default_type_mapping_for_kgram


def _default_hash_bytes(blob: bytes) -> int:
    hs = hashlib.sha1(blob).hexdigest()[-8:]
    return int(hs, 16)


def _tokens_to_json_bytes(chunk: Sequence[Token]) -> bytes:
    payload = [{"t": t.type, "n": t.text} for t in chunk]
    s = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return s.encode("utf-8")


class JsonLeafKgramStrategy:
    """Leaf tokenize (``java_leaf_tokenize``) + JSON serialization per k-gram window."""

    def __init__(self, k: int = 5) -> None:
        if k < 1:
            raise ValueError("k must be >= 1")
        self.k = k

    def tokens_for_kgram(self, code: str) -> list[Token]:
        """
        Leaf stream after ``to_drop`` mapping (see ``type_mapping.csv``), same as the
        tokenize similarity pipeline.
        """
        if not code.strip():
            return []
        from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
            leaf_tokens_and_truth_for_filter,
        )

        tokens, _, _pqs = leaf_tokens_and_truth_for_filter(
            code,
            _get_default_type_mapping(),
            default_categories=("unmapped",),
        )
        return tokens

    def compute_kgram_fingerprints(self, tokens: Sequence[Token]) -> list[Fingerprint]:
        if not tokens:
            return []
        tokens = list(tokens)
        k = self.k
        n = len(tokens)
        if n < k:
            blob = _tokens_to_json_bytes(tokens)
            hv = _default_hash_bytes(blob)
            first, last = tokens[0], tokens[-1]
            return [
                Fingerprint(
                    hash_value=hv,
                    start_byte=first.start_byte,
                    end_byte=last.end_byte,
                    token_start_index=0,
                    token_end_index=n,
                    start_line=first.start_line,
                    end_line=last.end_line,
                )
            ]

        out: list[Fingerprint] = []
        for i in range(0, n - k + 1):
            chunk = tokens[i : i + k]
            blob = _tokens_to_json_bytes(chunk)
            hv = _default_hash_bytes(blob)
            first, last = chunk[0], chunk[-1]
            out.append(
                Fingerprint(
                    hash_value=hv,
                    start_byte=first.start_byte,
                    end_byte=last.end_byte,
                    token_start_index=i,
                    token_end_index=i + k,
                    start_line=first.start_line,
                    end_line=last.end_line,
                )
            )
        return out

    def compute_kgram_hashes(self, code: str) -> list[int]:
        """Pre-Winnow k-gram hash sequence (convenience / demos)."""
        return [f.hash_value for f in self.compute_kgram_fingerprints(self.tokens_for_kgram(code))]


def _demo_main() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parent
    sample = (root / "sample.java").read_text(encoding="utf-8")
    tweak = sample + "\n// x"

    strategy = JsonLeafKgramStrategy(k=3)
    score_identical = compare_java_code(sample, sample, strategy=strategy)
    score_tweak = compare_java_code(sample, tweak, strategy=strategy)

    kg = strategy.compute_kgram_hashes(sample)
    print(kg[:5])
    print("JsonLeafKgramStrategy end-to-end demo")
    print(f"  sample.java k={strategy.k}: {len(kg)} k-gram hashes (before Winnow)")
    print(f"  compare(sample, sample): {score_identical:.4f}")
    print(f"  compare(sample, sample+comment): {score_tweak:.4f}")


if __name__ == "__main__":
    _demo_main()
