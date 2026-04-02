"""
Template handling for the tokenize pipeline.

**Line-based exclusion (language-agnostic):** ``submission_lines_matching_template``
marks 1-based source lines in a submission that match a non-blank line from the
template string exactly (``splitlines`` equality). Used to OR into per-token ``to_drop``
in :func:`leaf_tokens_and_truth_for_filter`.

**Legacy Java:** ``strip_template_classes`` removes entire top-level classes by name —
still available for callers that splice source before parsing; the main pipeline uses
line-based dropping instead.
"""

from __future__ import annotations

from tree_sitter import Language, Node, Parser
import tree_sitter_java as tslang

_lang = Language(tslang.language())
_parser = Parser()
_parser.language = _lang


def non_blank_template_line_set(template: str) -> frozenset[str]:
    """
    Distinct lines from ``template`` that contain at least one non-whitespace character.

    Empty / whitespace-only template lines are ignored (not used for matching).
    """
    if not (template or "").strip():
        return frozenset()
    return frozenset(line for line in template.splitlines() if line.strip())


def submission_lines_matching_template(code: str, template: str) -> frozenset[int]:
    """
    1-based line numbers in ``code`` whose full text equals some entry of
    :func:`non_blank_template_line_set` (literal ``str`` match per ``splitlines()`` row).
    """
    needles = non_blank_template_line_set(template)
    if not needles:
        return frozenset()
    hits: set[int] = set()
    for line_no, line in enumerate(code.splitlines(), start=1):
        if line in needles:
            hits.add(line_no)
    return frozenset(hits)


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
    """Top-level Java class simple names declared in ``template``."""
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
    Drop every top-level ``class_declaration`` in ``code`` whose simple name is among
    the top-level class names of ``template``.

    If ``template`` is blank/whitespace-only, returns ``code`` unchanged.
    Missing names in ``code`` are skipped. Does not trim or reformat the result.
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

    spans.sort(key=lambda t: t[0], reverse=True)
    buf = bytearray(raw)
    for lo, hi in spans:
        del buf[lo:hi]
    return bytes(buf).decode("utf-8", errors="replace")
