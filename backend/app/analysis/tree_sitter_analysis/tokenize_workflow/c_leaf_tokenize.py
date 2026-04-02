"""
Tree-sitter C leaf tokenizer: one syntactic leaf = one token (left-to-right).

Same contract as ``java_leaf_tokenize.tokenize_java`` but for C sources.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tree_sitter import Language, Node, Parser
import tree_sitter_c as tslang

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


def tokenize_c(source: str | bytes) -> list[Token]:
    """
    Return leaf nodes of the C AST in source order.

    Args:
        source: Full C translation unit (UTF-8).
    """
    if isinstance(source, str):
        source = source.encode("utf-8")
    tree = _parser.parse(source)
    out: list[Token] = []
    _leaf_tokens_dfs(tree.root_node, source, out)
    return out


# Minimal sample for smoke / inspecting leaf ``type`` strings vs Java.
_SAMPLE_C = r"""
#include <stdio.h>

int main(void) {
    int x = 42;
    printf("%d\n", x);
    return 0;
}
"""


def _demo() -> None:
    tokens = tokenize_c(_SAMPLE_C)
    print(f"root-level parse OK; {len(tokens)} leaf tokens\n")
    for i, t in enumerate(tokens):
        preview = repr(t.text) if len(t.text) <= 40 else repr(t.text[:37] + "...")
        print(f"{i:4d}  L{t.start_line}-{t.end_line}  {t.type:20s}  {preview}")


if __name__ == "__main__":
    _demo()
