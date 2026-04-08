"""
Tree-sitter C++ leaf tokenizer: one syntactic leaf = one token (left-to-right).

Same contract as ``c_leaf_tokenize.tokenize_c`` but for C++ sources.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tree_sitter import Language, Node, Parser
import tree_sitter_cpp as tslang

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


def tokenize_cpp(source: str | bytes) -> list[Token]:
    """
    Return leaf nodes of the C++ AST in source order.

    Args:
        source: Full C++ translation unit (UTF-8).
    """
    # print("tokenize_cpp")
    if isinstance(source, str):
        source = source.encode("utf-8")
    tree = _parser.parse(source)
    out: list[Token] = []
    _leaf_tokens_dfs(tree.root_node, source, out)
    return out


_SAMPLE_CPP = r"""
#include <iostream>

namespace ns {
class Foo {
 public:
  int x;
};
}  // namespace ns

int main() {
  using namespace std;
  auto v = 42;
  ns::Foo f;
  return 0;
}
"""


def _demo() -> None:
    tokens = tokenize_cpp(_SAMPLE_CPP)
    print(f"root-level parse OK; {len(tokens)} leaf tokens\n")
    for i, t in enumerate(tokens):
        preview = repr(t.text) if len(t.text) <= 40 else repr(t.text[:37] + "...")
        print(f"{i:4d}  L{t.start_line}-{t.end_line}  {t.type:20s}  {preview}")


if __name__ == "__main__":
    _demo()
