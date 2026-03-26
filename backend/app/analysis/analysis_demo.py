"""Demo: call app.analysis.compute_javacode_similarity on Alice vs Bob Main.java."""

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parents[2]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.analysis import compute_javacode_similarity

_SCRIPT_DIR = Path(__file__).resolve().parent
_SUBMISSIONS_DIR = _SCRIPT_DIR / "tree_sitter_analysis/assignment_renamed_vars/submissions"
alice_path = _SUBMISSIONS_DIR / "Alice/Main.java"
bob_path = _SUBMISSIONS_DIR / "Bob/Main.java"


def demo_alice_bob_similarity():
    """Run similarity analysis for Alice and Bob via analysis API."""
    code_a = alice_path.read_text(encoding="utf-8")
    code_b = bob_path.read_text(encoding="utf-8")
    sim = compute_javacode_similarity(code_a, code_b, name_a="Alice", name_b="Bob")
    print(f"compute_javacode_similarity(Alice, Bob) = {sim:.2%}")


if __name__ == "__main__":
    demo_alice_bob_similarity()
