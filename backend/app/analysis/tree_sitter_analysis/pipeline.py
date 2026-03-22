"""
Java code similarity analysis pipeline.

Simplified model: single class per file, function pairing by name, variable
normalization, then Winnowing-based similarity per pair.
"""

from app.analysis.testWinowingCode.testWinowingLib import compare_texts_with_template

from app.analysis.tree_sitter_analysis.function_refactor_tools import (
    function_rename_variable_by_defining_order,
)
from app.analysis.tree_sitter_analysis.refactor_tools import (
    get_all_function_names_in_class,
    get_all_functions_in_class,
    get_class_names,
    match_labels,
    node_to_source,
)


def function_pairing(code_a: str, code_b: str) -> list[tuple[str, str, str, str]]:
    """
    Pair functions between two Java code snippets by name similarity.

    Assumes each snippet has exactly one class; extracts method names from the
    first class in each, uses match_labels to get 1-to-1 pairs.

    Returns: [(name_a, name_b, func_source_a, func_source_b), ...] for each pair.
    """
    classes_a = get_class_names(code_a)
    classes_b = get_class_names(code_b)
    if not classes_a or not classes_b:
        return []
    class_a = classes_a[0]
    class_b = classes_b[0]
    code_a_bytes = code_a.encode("utf-8")
    code_b_bytes = code_b.encode("utf-8")
    methods_a = get_all_functions_in_class(code_a_bytes, class_a)
    methods_b = get_all_functions_in_class(code_b_bytes, class_b)
    names_a = get_all_function_names_in_class(code_a_bytes, class_a)
    names_b = get_all_function_names_in_class(code_b_bytes, class_b)
    pairs = match_labels(names_a, names_b)
    result: list[tuple[str, str, str, str]] = []
    for name_a, name_b in pairs:
        i = names_a.index(name_a)
        j = names_b.index(name_b)
        src_a = node_to_source(methods_a[i], code_a_bytes)
        src_b = node_to_source(methods_b[j], code_b_bytes)
        result.append((name_a, name_b, src_a, src_b))
    return result


def compute_similarity_java_function(
    func_a: str,
    func_b: str,
    *,
    name_a: str = "",
    name_b: str = "",
) -> dict:
    """
    Compute similarity of two Java function fragments.

    1. Normalize each via function_rename_variable_by_defining_order (VAR_1, VAR_2, ...).
    2. Run Winnowing on the two normalized strings via compare_texts_with_template.

    Returns: same structure as testWinowingLib.compare_files:
        base_dir, name_a, name_b, text_a, text_b, similarity, overlap, groups, points
    """
    norm_a = function_rename_variable_by_defining_order(func_a)
    norm_b = function_rename_variable_by_defining_order(func_b)
    display_a = name_a or "func_a"
    display_b = name_b or "func_b"
    return compare_texts_with_template(
        norm_a,
        norm_b,
        template="",
        name_a=display_a,
        name_b=display_b,
        auto_store=False,
    )


def compute_similarity_javacode(code_a: str, code_b: str) -> float:
    """
    Main entry: similarity between two Java code strings.

    1. function_pairing(code_a, code_b) -> list of (name_a, name_b, func_a, func_b) pairs.
    2. For each pair: compute_similarity_java_function(func_a, func_b).
    3. Return mean of pairwise similarities.
    4. If no pairs: return 0.0.
    """
    pairs = function_pairing(code_a, code_b)
    if not pairs:
        return 0.0
    similarities: list[float] = []
    for name_a, name_b, src_a, src_b in pairs:
        result = compute_similarity_java_function(
            src_a, src_b, name_a=name_a, name_b=name_b
        )
        similarities.append(result["similarity"])
    return sum(similarities) / len(similarities)
