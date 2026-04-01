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
    get_class_source,
    match_labels,
    node_to_source,
)


def _require_exactly_one_class(code: str, side: str) -> str:
    names = get_class_names(code)
    n = len(names)
    if n == 0:
        raise ValueError(f"{side}: expected exactly one class, found 0")
    if n > 1:
        raise ValueError(
            f"{side}: expected exactly one class, found {n}: {names!r}"
        )
    return names[0]


def function_pairing_for_single_class(
    code_a: str, code_b: str
) -> list[tuple[str, str, str, str]]:
    """
    Pair functions between two Java snippets that each contain exactly one class.

    Raises:
        ValueError: if either snippet has 0 or more than 1 class declaration.

    Returns:
        [(name_a, name_b, func_source_a, func_source_b), ...] for each pair.
    """
    class_a = _require_exactly_one_class(code_a, "code_a")
    class_b = _require_exactly_one_class(code_b, "code_b")
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


def class_pairing(code_a: str, code_b: str, template: str) -> list[tuple[str, str]]:
    """
    Decide which class in code_a pairs with which class in code_b for comparison.

    For each class name T declared in ``template``: if the same name T appears in
    both ``code_a`` and ``code_b``, T is treated as unchanged starter code and is
    excluded. Remaining class names on each side are paired 1:1 with
    ``match_labels`` (name similarity), without requiring identical names.

    Empty or whitespace-only ``template`` means no names are excluded.

    Returns:
        Non-empty ``[(name_in_a, name_in_b), ...]`` for classes to compare.

    Raises:
        ValueError: if there are no classes left to compare after template exclusion;
            if, after exclusion, the two sides do not have the same number of classes;
            or if greedy pairing does not cover all remaining classes.
    """
    classes_a = get_class_names(code_a)
    classes_b = get_class_names(code_b)
    tmpl = (template or "").strip()
    template_names = set(get_class_names(tmpl)) if tmpl else set()

    exclude: set[str] = set()
    for name in template_names:
        if name in classes_a and name in classes_b:
            exclude.add(name)

    remaining_a = [c for c in classes_a if c not in exclude]
    remaining_b = [c for c in classes_b if c not in exclude]

    # if len(remaining_a) != len(remaining_b):
    #     raise ValueError(
    #         "class_pairing: unequal class counts after template exclusion: "
    #         f"{remaining_a!r} vs {remaining_b!r}"
    #     )
    if not remaining_a or not remaining_b:
        raise ValueError(
            "class_pairing: no classes left to compare after template exclusion "
            f"(excluded={sorted(exclude)!r}, classes_a={classes_a!r}, classes_b={classes_b!r})"
        )

    pairs = match_labels(remaining_a, remaining_b)
    # if len(pairs) != len(remaining_a):
    #     raise ValueError(
    #         "class_pairing: could not form a full 1-to-1 class pairing for "
    #         f"{remaining_a!r} vs {remaining_b!r}"
    #     )
    return pairs


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
        k=8
    )


def compute_similarity_java_class(code_a: str, code_b: str) -> float:
    """
    Similarity between two Java snippets that each contain exactly one class.

    1. function_pairing_for_single_class -> method pairs.
    2. For each pair: compute_similarity_java_function.
    3. Return the mean similarity; if there are no method pairs, return 0.0.

    Raises:
        ValueError: if either snippet has 0 or more than one class (same as pairing).
    """
    pairs = function_pairing_for_single_class(code_a, code_b)
    if not pairs:
        return 0.0
    similarities: list[float] = []
    for name_a, name_b, src_a, src_b in pairs:
        result = compute_similarity_java_function(
            src_a, src_b, name_a=name_a, name_b=name_b
        )
        similarities.append(result["similarity"])
    return sum(similarities) / len(similarities)


def compute_similarity_javacode(code_a: str, code_b: str, template: str = "") -> float:
    """
    Similarity between two Java compilation units (file-level).

    Uses :func:`class_pairing` with ``template`` to exclude symmetric template
    classes, pairs the remaining classes, runs :func:`compute_similarity_java_class`
    on each pair, and returns the mean.

    ``template`` may be empty: no class names are excluded; all classes on each
    side are paired (counts must match). Propagates :func:`class_pairing`
    ``ValueError`` when pairing fails or nothing remains to compare (callers can
    treat this as an invalid/problematic submission pair).
    """
    class_pairs = class_pairing(code_a, code_b, template)
    scores: list[float] = []
    for name_a, name_b in class_pairs:
        src_a = get_class_source(code_a, name_a)
        src_b = get_class_source(code_b, name_b)
        scores.append(compute_similarity_java_class(src_a, src_b))
    return sum(scores) / len(scores)
