"""Regression harness wired to JsonLeafKgramStrategy + compare_java_code.

Run from ``token-trail/backend`` with venv:
  python -m app.analysis.tree_sitter_analysis.tokenize_demo

Template text is passed through the callback but not applied yet (token path).
"""

from __future__ import annotations

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parents[3]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.tree_sitter_analysis.early_access_token.compare_javacode import (
    compare_java_code,
)
from app.analysis.tree_sitter_analysis.early_access_token.json_kgram_strategy import (
    JsonLeafKgramStrategy,
)
from app.analysis.tree_sitter_analysis.pipeline_demo import (
    JavaSimilarityFn,
    demo_test_all,
)


def make_json_leaf_similarity_fn(
    *, k: int = 5, winnow_window: int = 4
) -> JavaSimilarityFn:
    strategy = JsonLeafKgramStrategy(k=k)

    def fn(code_a: str, code_b: str, template: str) -> float:
        _ = template
        return compare_java_code(
            code_a, code_b, strategy=strategy, winnow_window=winnow_window
        )

    return fn


def main() -> None:
    print("Regression: JsonLeafKgramStrategy + compare_java_code\n")
    demo_test_all(similarity_fn=make_json_leaf_similarity_fn(k=5, winnow_window=4))


if __name__ == "__main__":
    main()
