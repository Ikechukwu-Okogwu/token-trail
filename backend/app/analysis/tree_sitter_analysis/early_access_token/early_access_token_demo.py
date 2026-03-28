"""Run from backend with venv active: ``python app/analysis/tree_sitter_analysis/early_access_token/early_access_token_demo.py``

Loads ``early_access_token.py`` via importlib so this demo does not import
``tree_sitter_analysis``'s package ``__init__`` (which pulls in the full pipeline).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_token_module():
    p = Path(__file__).resolve().parent / "early_access_token.py"
    spec = importlib.util.spec_from_file_location("early_access_token_hw", p)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load early_access_token.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_token = _load_token_module()
tokenize_java = _token.tokenize_java

HELLO_JAVA = """
public class HelloWorld {
  public static void main(String[] args) {
    System.out.println("Hi");
  }
}
"""


def main() -> None:
    tokens = tokenize_java(HELLO_JAVA)
    print(f"tokenize_java(Hello.java): {len(tokens)} leaf tokens\n")
    for t in tokens:
        preview = t.text.replace("\n", "\\n")
        if len(preview) > 40:
            preview = preview[:37] + "..."
        print(f"  [{t.start_byte:3},{t.end_byte:3})  {t.type:22}  {preview!r}")


if __name__ == "__main__":
    main()
