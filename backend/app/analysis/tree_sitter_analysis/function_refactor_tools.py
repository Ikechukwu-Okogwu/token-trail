"""Refactor methods in Java: rename variables, reorder definitions, etc."""

from tree_sitter import Node

from app.analysis.tree_sitter_analysis.refactor_tools import (
    get_all_functions_in_class,
    node_to_source,
)


def _get_var_name_from_declarator(declarator: Node, source: bytes) -> str | None:
    """Extract variable name from variable_declarator or _variable_declarator_id."""
    name_node = declarator.child_by_field_name("name")
    if name_node:
        return source[name_node.start_byte : name_node.end_byte].decode("utf-8", errors="replace")
    # Fallback: first identifier child
    for child in declarator.children:
        if child.type in ("identifier", "_reserved_identifier"):
            return source[child.start_byte : child.end_byte].decode("utf-8", errors="replace")
    return None


def _get_var_names_from_local_decl(decl_node: Node, source: bytes) -> list[str]:
    """Extract variable names from a local_variable_declaration node."""
    names: list[str] = []

    def collect(node: Node) -> None:
        if node.type == "variable_declarator":
            n = _get_var_name_from_declarator(node, source)
            if n:
                names.append(n)
        for c in node.children:
            collect(c)

    collect(decl_node)
    return names


def get_var_def_order(method_node: Node, source: bytes, var_names: list[str]) -> list[str]:
    """
    Return the order of first definition for vars in var_names, as they appear
    in the method body (top-level statements only).
    Raises ValueError if any var in var_names is not found.
    method_node must be a method_declaration node.
    """
    var_set = set(var_names)
    seen: set[str] = set()
    result: list[str] = []
    block = None
    for child in method_node.children:
        if child.type == "block":
            block = child
            break
    if block is None:
        missing = set(var_names)
        if missing:
            raise ValueError(f"Variables not found: {missing}")
        return []
    for child in block.children:
        if child.type == "local_variable_declaration":
            for name in _get_var_names_from_local_decl(child, source):
                if name in var_set and name not in seen:
                    seen.add(name)
                    result.append(name)
    missing = set(var_names) - seen
    if missing:
        raise ValueError(f"Variables not found: {missing}")
    return result


def get_all_var_def_order(method_node: Node, source: bytes) -> list[str]:
    """
    Return all top-level local variable names in definition order.
    method_node must be a method_declaration node.
    """
    result: list[str] = []
    seen: set[str] = set()
    block = None
    for child in method_node.children:
        if child.type == "block":
            block = child
            break
    if block is None:
        return []
    for child in block.children:
        if child.type == "local_variable_declaration":
            for name in _get_var_names_from_local_decl(child, source):
                if name not in seen:
                    seen.add(name)
                    result.append(name)
    return result


_WRAP_CLASS = "__Wrap"

def _apply_rename_by_defining_order(code_bytes: bytes, method_node: Node) -> bytes:
    """Core logic: rename vars in place. Requires code_bytes and method_node from same parse."""
    var_list = get_all_var_def_order(method_node, code_bytes)
    if not var_list:
        return code_bytes
    all_ranges: list[tuple[int, int, str]] = []
    for i, var in enumerate(var_list):
        ranges: list[tuple[int, int]] = []
        _collect_identifier_ranges(method_node, code_bytes, var, ranges)
        for start, end in ranges:
            all_ranges.append((start, end, f"VAR_{i + 1}"))
    all_ranges.sort(reverse=True, key=lambda x: x[0])
    result = bytearray(code_bytes)
    for start, end, new_name in all_ranges:
        result[start:end] = new_name.encode("utf-8")
    return bytes(result)


def function_rename_variable_by_defining_order(func_source: str) -> str:
    """
    Rename all top-level local variables to VAR_1, VAR_2, ... by definition order.
    Accepts standalone Java method source; returns normalized method source.
    """
    wrapped = f"class {_WRAP_CLASS} {{\n{func_source}\n}}"
    wrapped_bytes = wrapped.encode("utf-8")
    methods = get_all_functions_in_class(wrapped_bytes, _WRAP_CLASS)
    if not methods:
        return func_source
    method_node = methods[0]
    result_bytes = _apply_rename_by_defining_order(wrapped_bytes, method_node)
    result_str = result_bytes.decode("utf-8", errors="replace")
    methods_new = get_all_functions_in_class(result_bytes, _WRAP_CLASS)
    if not methods_new:
        return result_str
    return node_to_source(methods_new[0], result_bytes)


def _collect_identifier_ranges(
    node: Node, source: bytes, name: str, out: list[tuple[int, int]]
) -> None:
    """Collect (start_byte, end_byte) for all identifier nodes matching name."""
    if node.type in ("identifier", "_reserved_identifier"):
        text = source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
        if text == name:
            out.append((node.start_byte, node.end_byte))
    for child in node.children:
        _collect_identifier_ranges(child, source, name, out)


def function_rename_variable_inplace(
    code: str | bytes, method_node: Node, old_name: str, new_name: str
) -> str | bytes:
    """
    Rename all occurrences of old_name to new_name within the given method.
    Returns modified code (str or bytes, matching input type).
    method_node must be a method_declaration node from parsing code.
    """
    if isinstance(code, str):
        was_str = True
        code = code.encode("utf-8")
    else:
        was_str = False
    if old_name == new_name:
        return code.decode("utf-8", errors="replace") if was_str else code
    ranges: list[tuple[int, int]] = []
    _collect_identifier_ranges(method_node, code, old_name, ranges)
    ranges.sort(reverse=True, key=lambda r: r[0])
    new_bytes = new_name.encode("utf-8")
    result = bytearray(code)
    for start, end in ranges:
        result[start:end] = new_bytes
    return result.decode("utf-8", errors="replace") if was_str else bytes(result)
