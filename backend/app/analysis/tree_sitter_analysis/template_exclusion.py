"""
Remove top-level template classes from Java sources before leaf tokenization.

Uses the same Tree-sitter Java grammar as the rest of tree_sitter_analysis.
Template supplies top-level ``class_declaration`` simple names; any matching
top-level class in the submission is deleted as a whole byte span before
tokenization, so the token pipeline never sees shared boilerplate.

This module is Java-only. C/C++ take a different path.
"""

from __future__ import annotations

from tree_sitter import Language, Node, Parser
import tree_sitter_java as tslang

_lang = Language(tslang.language())
_parser = Parser()
_parser.language = _lang


def _class_declaration_name(node: Node, source: bytes) -> str | None:
    if node.type != "class_declaration":
        return None
    for child in node.children:
        if child.type == "identifier":
            return source[child.start_byte : child.end_byte].decode(
                "utf-8", errors="replace"
            )
    return None


def _top_level_class_declarations(program: Node) -> list[Node]:
    """``class_declaration`` nodes that are direct children of ``program``."""
    if program.type != "program":
        return []
    return [c for c in program.children if c.type == "class_declaration"]


def template_top_level_class_names(template: str) -> frozenset[str]:
    """Return the set of top-level Java class simple names declared in ``template``."""
    if not (template or "").strip():
        return frozenset()
    source = template.encode("utf-8")
    tree = _parser.parse(source)
    names: list[str] = []
    for node in _top_level_class_declarations(tree.root_node):
        n = _class_declaration_name(node, source)
        if n:
            names.append(n)
    return frozenset(names)


def strip_template_classes(code: str, template: str) -> str:
    """
    Drop every top-level ``class_declaration`` in ``code`` whose simple name
    appears among the top-level class names of ``template``.

    If ``template`` is blank/whitespace-only, returns ``code`` unchanged.
    Classes not present in ``code`` are silently skipped.
    Does not reformat or trim the result.
    """
    if not (template or "").strip():
        return code
    to_remove = template_top_level_class_names(template)
    if not to_remove:
        return code

    raw = code.encode("utf-8")
    tree = _parser.parse(raw)
    spans: list[tuple[int, int]] = []
    for node in _top_level_class_declarations(tree.root_node):
        cn = _class_declaration_name(node, raw)
        if cn and cn in to_remove:
            spans.append((node.start_byte, node.end_byte))

    if not spans:
        return code

    # Remove in reverse order so earlier offsets stay valid
    spans.sort(key=lambda t: t[0], reverse=True)
    buf = bytearray(raw)
    for lo, hi in spans:
        del buf[lo:hi]
    return bytes(buf).decode("utf-8", errors="replace")
