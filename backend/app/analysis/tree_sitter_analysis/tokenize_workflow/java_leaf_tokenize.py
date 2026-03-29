"""
Tree-sitter Java leaf tokenizer: one syntactic leaf = one token (left-to-right).

We treat each AST leaf node (no children) as one token before any Winnowing.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tree_sitter import Language, Node, Parser
import tree_sitter_java as tslang

try:
    from app.analysis.tree_sitter_analysis.tokenize_workflow.token_fingerprint import (
        Token,
        byte_span_to_one_based_lines,
    )
except ImportError:
    _pkg = Path(__file__).resolve().parent
    if str(_pkg) not in sys.path:
        sys.path.insert(0, str(_pkg))
    from token_fingerprint import (  # type: ignore[no-redef]
        Token,
        byte_span_to_one_based_lines,
    )

_lang = Language(tslang.language())
_parser = Parser()
_parser.language = _lang


def _leaf_tokens_dfs(node: Node, source: bytes, out: list[Token]) -> None:
    if len(node.children) == 0:
        text = source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
        start_line, end_line = byte_span_to_one_based_lines(
            source, node.start_byte, node.end_byte
        )
        out.append(
            Token(
                type=node.type,
                text=text,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                start_line=start_line,
                end_line=end_line,
            )
        )
        return
    for child in node.children:
        _leaf_tokens_dfs(child, source, out)


def tokenize_java(source: str | bytes) -> list[Token]:
    """
    Return leaf nodes of the Java AST in source order.

    Args:
        source: Full Java compilation unit (UTF-8).
    """
    if isinstance(source, str):
        source = source.encode("utf-8")
    tree = _parser.parse(source)
    out: list[Token] = []
    _leaf_tokens_dfs(tree.root_node, source, out)
    return out
