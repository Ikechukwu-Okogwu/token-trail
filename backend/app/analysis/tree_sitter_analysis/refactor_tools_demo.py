"""Demo: get_all_functions_in_class on Alice's Main.java."""

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parents[3]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.tree_sitter_analysis.refactor_tools import (
    get_all_function_names_in_class,
    get_all_functions_in_class,
    match_labels,
    node_to_source,
)

_SCRIPT_DIR = Path(__file__).resolve().parent
original_file_path = _SCRIPT_DIR / "assignment_renamed_vars/submissions/Alice/Main.java"
copied_file_path = _SCRIPT_DIR / "assignment_renamed_vars/submissions/Bob/Main.java"


def demo_get_all_functions():
    with open(original_file_path, encoding="utf-8") as f:
        code = f.read()
    methods = get_all_functions_in_class(code, "RenamedBase")
    print(f"Found {len(methods)} methods in RenamedBase:\n")
    code_bytes = code.encode("utf-8")
    for i, method in enumerate(methods, 1):
        text = node_to_source(method, code_bytes)
        print(f"--- Method {i} ---")
        print(text)
        print()


def demo_match_labels():
    with open(original_file_path, encoding="utf-8") as f:
        code_a = f.read()
    with open(copied_file_path, encoding="utf-8") as f:
        code_b = f.read()
    names_a = get_all_function_names_in_class(code_a, "RenamedBase")
    names_b = get_all_function_names_in_class(code_b, "RenamedBase")
    pairs = match_labels(names_a, names_b)
    print("Method name pairs (Alice vs Bob):")
    for a, b in pairs:
        print(f"  {a!r} <-> {b!r}")


def demo_get_all_function_names():
    with open(original_file_path, encoding="utf-8") as f:
        code = f.read()
    names = get_all_function_names_in_class(code, "RenamedBase")
    print(f"Method names in {original_file_path}:")
    for name in names:
        print(f"  {name}")


if __name__ == "__main__":
    # demo_get_all_functions()
    print()
    # demo_get_all_function_names()
    demo_match_labels()
