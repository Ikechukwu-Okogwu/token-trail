"""Tree-sitter based refactor tools for Java (and future C/C++)."""

from difflib import SequenceMatcher
from tree_sitter import Parser, Node, Language
import tree_sitter_java as tslang
import warnings

_lang = Language(tslang.language())
_parser = Parser()
_parser.language = _lang


def _get_class_name(node: Node, source: bytes) -> str | None:
    if node.type != "class_declaration":
        return None
    for child in node.children:
        if child.type == "identifier":
            return source[child.start_byte : child.end_byte].decode("utf-8", errors="replace")
    return None


def _find_all_class_declarations(root: Node, out: list[Node]) -> None:
    if root.type == "class_declaration":
        out.append(root)
    for child in root.children:
        _find_all_class_declarations(child, out)


def get_class_names(code: str | bytes) -> list[str]:
    if isinstance(code, str):
        code = code.encode("utf-8")
    tree = _parser.parse(code)
    root = tree.root_node
    classes: list[Node] = []
    _find_all_class_declarations(root, classes)
    return [_get_class_name(c, code) or "" for c in classes]


def _find_class_declaration(root: Node, class_name: str, source: bytes) -> Node | None:
    classes: list[Node] = []
    _find_all_class_declarations(root, classes)
    for c in classes:
        if _get_class_name(c, source) == class_name:
            return c
    return None


def _collect_method_declarations(node: Node, out: list[Node]) -> None:
    if node.type == "method_declaration":
        out.append(node)
    for child in node.children:
        _collect_method_declarations(child, out)


def get_all_functions_in_class(code: str | bytes, class_name: str) -> list[Node]:
    if isinstance(code, str):
        code = code.encode("utf-8")
    tree = _parser.parse(code)
    root = tree.root_node
    class_node = _find_class_declaration(root, class_name, code)
    if class_node is None:
        return []
    methods: list[Node] = []
    for child in class_node.children:
        if child.type == "class_body":
            _collect_method_declarations(child, methods)
            break
    return methods


def _get_function_name(node: Node, source: bytes) -> str | None:
    if node.type != "method_declaration":
        return None
    for child in node.children:
        if child.type == "_method_header":
            for sub in child.children:
                if sub.type == "_method_declarator":
                    name_node = sub.child_by_field_name("name")
                    if name_node:
                        return source[name_node.start_byte : name_node.end_byte].decode("utf-8", errors="replace")
    children = node.children
    for i, child in enumerate(children):
        if child.type == "formal_parameters" and i > 0:
            prev = children[i - 1]
            if prev.type in ("identifier", "_reserved_identifier"):
                return source[prev.start_byte : prev.end_byte].decode("utf-8", errors="replace")
    return None


def get_all_function_names_in_class(code: str | bytes, class_name: str) -> list[str]:
    if isinstance(code, str):
        code = code.encode("utf-8")
    methods = get_all_functions_in_class(code, class_name)
    return [_get_function_name(m, code) or "" for m in methods]


def node_to_source(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def get_class_source(code: str | bytes, class_name: str) -> str:
    """
    Return the source text of the top-level class_declaration named ``class_name``.

    Raises:
        ValueError: if no such class exists in ``code``.
    """
    if isinstance(code, str):
        code_bytes = code.encode("utf-8")
    else:
        code_bytes = code
    tree = _parser.parse(code_bytes)
    class_node = _find_class_declaration(tree.root_node, class_name, code_bytes)
    if class_node is None:
        raise ValueError(f"get_class_source: class {class_name!r} not found in source")
    return node_to_source(class_node, code_bytes)


def label_literal_similarity(label_a: str, label_b: str) -> float:
    if not label_a and not label_b:
        return 1.0
    if not label_a or not label_b:
        return 0.0
    return SequenceMatcher(None, label_a, label_b).ratio()


def match_labels(labels_a: list[str], labels_b: list[str]) -> list[tuple[str, str]]:
    if len(labels_a) != len(labels_b):
        warnings.warn(f"match_labels: unequal label counts: {len(labels_a)} vs {len(labels_b)}")
    if not labels_a or not labels_b:
        return []
    candidates: list[tuple[float, str, str]] = []
    for a in labels_a:
        for b in labels_b:
            sim = label_literal_similarity(a, b)
            candidates.append((sim, a, b))
    candidates.sort(key=lambda x: (-x[0], x[1], x[2]))
    used_a: set[str] = set()
    used_b: set[str] = set()
    result: list[tuple[str, str]] = []
    for _, a, b in candidates:
        if a not in used_a and b not in used_b:
            result.append((a, b))
            used_a.add(a)
            used_b.add(b)
    return result
