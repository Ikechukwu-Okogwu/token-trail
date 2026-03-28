"""
JavaKgramStrategy: Tree-sitter leaf tokens + compact JSON k-gram blobs + SHA1 (8 hex).

Uses the same truncation style as ``testWinowingCode.winnowingCopy.default_hash``.
"""

from __future__ import annotations

import hashlib
import json
import sys
import warnings
from collections.abc import Sequence
from pathlib import Path

_backend = Path(__file__).resolve().parents[4]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.tree_sitter_analysis.early_access_token.compare_javacode import (
    compare_java_code,
)
from app.analysis.tree_sitter_analysis.early_access_token.early_access_token import (
    tokenize_java,
)
from app.analysis.tree_sitter_analysis.early_access_token.token_fingerprint import (
    Fingerprint,
    Token,
)

# Tree-sitter Java leaf types to omit from k-grams (noise / non-behavioral).
_TOKEN_TYPES_DROP: frozenset[str] = frozenset({"line_comment", "block_comment"})


def _default_hash_bytes(blob: bytes) -> int:
    hs = hashlib.sha1(blob).hexdigest()[-8:]
    return int(hs, 16)


def _filter_tokens_for_kgram(tokens: list[Token]) -> list[Token]:
    """Drop comments; warn once if ERROR leaves appear (parse-quality signal)."""
    if any(t.type == "ERROR" for t in tokens):
        n_err = sum(1 for t in tokens if t.type == "ERROR")
        warnings.warn(
            f"Java parse produced {n_err} ERROR leaf token(s); "
            "k-gram fingerprint may be unreliable until handled.",
            UserWarning,
            stacklevel=2,
        )
    return [t for t in tokens if t.type not in _TOKEN_TYPES_DROP]


def _tokens_to_json_bytes(chunk: Sequence[Token]) -> bytes:
    payload = [{"t": t.type, "n": t.text} for t in chunk]
    s = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return s.encode("utf-8")


class JsonLeafKgramStrategy:
    """Leaf tokenize (early_access_token) + JSON serialization per k-gram window."""

    def __init__(self, k: int = 5) -> None:
        if k < 1:
            raise ValueError("k must be >= 1")
        self.k = k

    def tokens_for_kgram(self, code: str) -> list[Token]:
        """Same filtered leaf stream used by ``compute_kgram_fingerprints``."""
        if not code.strip():
            return []
        return _filter_tokens_for_kgram(tokenize_java(code))

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
