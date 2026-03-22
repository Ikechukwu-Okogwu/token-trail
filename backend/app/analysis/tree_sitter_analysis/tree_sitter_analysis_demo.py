"""Demo: function_pairing on Alice vs Bob Main.java."""

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parents[3]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.testWinowingCode.render_result import store_compare_result_as_html

from app.analysis.tree_sitter_analysis import (
    compute_similarity_java_function,
    compute_similarity_javacode,
    function_pairing,
    get_class_names,
)

_SCRIPT_DIR = Path(__file__).resolve().parent
_SUBMISSIONS_DIR = _SCRIPT_DIR / "assignment_renamed_vars/submissions"
alice_path = _SUBMISSIONS_DIR / "Alice/Main.java"
bob_path = _SUBMISSIONS_DIR / "Bob/Main.java"
carol_path = _SUBMISSIONS_DIR / "Carol/Main.java"
_output_dir = _SCRIPT_DIR / "similarity_output"


def demo_function_pairing():
    with open(alice_path, encoding="utf-8") as f:
        code_a = f.read()
    with open(bob_path, encoding="utf-8") as f:
        code_b = f.read()
    pairs = function_pairing(code_a, code_b)
    classes_a = get_class_names(code_a)
    classes_b = get_class_names(code_b)
    print(f"First class in Alice: {classes_a[0] if classes_a else None}")
    print(f"First class in Bob: {classes_b[0] if classes_b else None}")
    print(f"\nPaired functions ({len(pairs)} pairs):\n")
    for i, (name_a, name_b, src_a, src_b) in enumerate(pairs, 1):
        first_line_a = src_a.strip().split("\n")[0]
        first_line_b = src_b.strip().split("\n")[0]
        print(f"  Pair {i}: {name_a} <-> {name_b}")
        print(f"    A: {first_line_a}...")
        print(f"    B: {first_line_b}...")
        print()


def demo_similarity_and_render():
    """Take first 3 function pairs, compute similarity, render result.html."""
    with open(alice_path, encoding="utf-8") as f:
        code_a = f.read()
    with open(bob_path, encoding="utf-8") as f:
        code_b = f.read()
    pairs = function_pairing(code_a, code_b)
    top3 = pairs[:3]
    _output_dir.mkdir(parents=True, exist_ok=True)
    base_dir_str = str(_output_dir)

    for name_a, name_b, src_a, src_b in top3:
        result = compute_similarity_java_function(
            src_a, src_b, name_a=name_a, name_b=name_b
        )
        store_compare_result_as_html(
            base_dir=base_dir_str,
            name_a=result["name_a"],
            name_b=result["name_b"],
            text_a=result["text_a"],
            text_b=result["text_b"],
            similarity=result["similarity"],
            overlap=result["overlap"],
            groups=result["groups"],
        )
    print(f"Rendered {len(top3)} pairs to {_output_dir / 'result.html'}")


def demo_compute_similarity_javacode():
    """Compute overall similarity between all three submission pairs: Alice-Bob, Alice-Carol, Bob-Carol."""
    paths = {"Alice": alice_path, "Bob": bob_path, "Carol": carol_path}
    codes = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}

    pairs = [("Alice", "Bob"), ("Alice", "Carol"), ("Bob", "Carol")]
    for name_a, name_b in pairs:
        sim = compute_similarity_javacode(codes[name_a], codes[name_b])
        print(f"compute_similarity_javacode({name_a}, {name_b}) = {sim:.2%}")


if __name__ == "__main__":
    # demo_function_pairing()
    # print("\n--- Running similarity + render demo ---\n")
    # demo_similarity_and_render()
    print("\n--- Running compute_similarity_javacode demo ---\n")
    demo_compute_similarity_javacode()
