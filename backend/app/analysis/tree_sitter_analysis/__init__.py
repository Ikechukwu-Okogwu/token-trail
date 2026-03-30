"""Tree-sitter based Java code analysis: parsing, refactoring, similarity."""

from __future__ import annotations

from typing import Any

from app.analysis.tree_sitter_analysis.pipeline import (
    class_pairing,
    compute_similarity_java_class,
    compute_similarity_javacode,
    compute_similarity_java_function,
    function_pairing_for_single_class,
)
from app.analysis.tree_sitter_analysis.refactor_tools import (
    get_all_function_names_in_class,
    get_all_functions_in_class,
    get_class_names,
    get_class_source,
    match_labels,
    node_to_source,
)


def __getattr__(name: str) -> Any:
    """Lazy import so ``app.analysis.config`` can load before ``tokenize_pipeline``."""
    if name == "TokenizePipelineResult":
        from app.analysis.tree_sitter_analysis.tokenize_pipeline import TokenizePipelineResult

        return TokenizePipelineResult
    if name == "run_tokenize_similarity_pipeline":
        from app.analysis.tree_sitter_analysis.tokenize_pipeline import (
            run_tokenize_similarity_pipeline,
        )

        return run_tokenize_similarity_pipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "TokenizePipelineResult",
    "class_pairing",
    "compute_similarity_java_class",
    "compute_similarity_javacode",
    "compute_similarity_java_function",
    "function_pairing_for_single_class",
    "run_tokenize_similarity_pipeline",
    "get_all_function_names_in_class",
    "get_all_functions_in_class",
    "get_class_names",
    "get_class_source",
    "match_labels",
    "node_to_source",
]
