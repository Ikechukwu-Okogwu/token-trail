"""Demo: function_pairing_for_single_class, regression harness, similarity helpers."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

# (code_a, code_b, template) -> similarity in [0, 1]; template may be "".
JavaSimilarityFn = Callable[[str, str, str], float]

_backend = Path(__file__).resolve().parents[3]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.testWinowingCode.render_result import store_compare_result_as_html

from app.analysis.tree_sitter_analysis import (
    compute_similarity_java_function,
    compute_similarity_javacode,
    function_pairing_for_single_class,
    get_class_names,
)

_SCRIPT_DIR = Path(__file__).resolve().parent
_output_dir = _SCRIPT_DIR / "similarity_output"

REGRESSION_FIXTURES: list[Path] = [
    Path("regression/assignment_reordered_functions"),
    Path("regression/assignment_renamed_vars"),
    Path("regression/assignment_template_heavy"),
    Path("regression/assignment_stage3_rankset"),
]


def _is_result_data_row(line: str) -> bool:
    """True for lines like Dev1.zip,Dev2.zip,expected=... (not fixture metadata)."""
    parts = line.split(",")
    return len(parts) >= 3 and ".zip" in parts[0]


def demo_function_pairing(path_a: Path, path_b: Path):
    with open(path_a, encoding="utf-8") as f:
        code_a = f.read()
    with open(path_b, encoding="utf-8") as f:
        code_b = f.read()
    pairs = function_pairing_for_single_class(code_a, code_b)
    classes_a = get_class_names(code_a)
    classes_b = get_class_names(code_b)
    print(f"Class in A: {classes_a[0] if classes_a else None}")
    print(f"Class in B: {classes_b[0] if classes_b else None}")
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
    pairs = function_pairing_for_single_class(code_a, code_b)
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



def demo_test_single_pair(
    path_code_a: Path,
    path_code_b: Path,
    path_template: Path,
) -> float:
    """
    Compare two Java files with an explicit template path.

    ``path_template`` may point to an empty file to use no template text (same as
    ``template=""`` in the pipeline). All paths must exist.

    Prints a one-line summary and returns the similarity in ``[0, 1]``.

    Raises:
        ValueError: propagated from ``compute_similarity_javacode`` / pairing.
        OSError: if a path does not exist or cannot be read.
    """
    if not path_code_a.is_file():
        raise FileNotFoundError(f"code_a not found: {path_code_a}")
    if not path_code_b.is_file():
        raise FileNotFoundError(f"code_b not found: {path_code_b}")
    if not path_template.is_file():
        raise FileNotFoundError(f"template not found: {path_template}")
    code_a = path_code_a.read_text(encoding="utf-8")
    code_b = path_code_b.read_text(encoding="utf-8")
    template = path_template.read_text(encoding="utf-8")
    sim = compute_similarity_javacode(code_a, code_b, template)
    print(
        f"  single pair: {path_code_a.name} vs {path_code_b.name} "
        f"(template {path_template.name}, {len(template)} chars) → {sim:.2%}"
    )
    return sim


def demo_test_on_regression(
    rel_path: Path,
    *,
    similarity_fn: JavaSimilarityFn | None = None,
) -> tuple[int, int]:
    """
    Load a regression fixture under ``_SCRIPT_DIR / rel_path``.

    Reads ``result.txt`` header:
      - ``template_exclusion=true|false`` — if true, loads template Java source from
        ``template_file`` (default ``template/Template.java`` relative to fixture root)
        and passes ``template`` text as the third argument to ``similarity_fn``.
    For each submission pair, runs ``similarity_fn(code_a, code_b, template)`` and
    checks the range. Default ``similarity_fn`` is ``compute_similarity_javacode``.

    ``ValueError`` from pairing / empty class set counts as FAIL (invalid pair).

    Returns:
        ``(pass_count, total)`` where ``total`` is the number of pairs with both
        ``Main.java`` present (SKIPs are excluded). Fixture load failure returns
        ``(0, 0)``.
    """
    sim_fn: JavaSimilarityFn = similarity_fn or compute_similarity_javacode
    base = _SCRIPT_DIR / rel_path
    result_file = base / "result.txt"
    submissions_dir = base / "submissions"
    if not result_file.exists():
        print(f"result.txt not found: {result_file}")
        return (0, 0)
    if not submissions_dir.is_dir():
        print(f"submissions dir not found: {submissions_dir}")
        return (0, 0)

    lines = result_file.read_text(encoding="utf-8").strip().splitlines()
    template_exclusion = False
    template_rel: str | None = None
    for line in lines:
        s = line.strip()
        if s.startswith("template_exclusion="):
            template_exclusion = s.split("=", 1)[1].strip().lower() == "true"
        elif s.startswith("template_file="):
            template_rel = s.split("=", 1)[1].strip()

    template = ""
    if template_exclusion:
        rel = template_rel or "template/Template.java"
        tmpl_path = base / rel
        if not tmpl_path.is_file():
            print(f"template required but not found: {tmpl_path}")
            return (0, 0)
        template = tmpl_path.read_text(encoding="utf-8")
        print(f"  template: {tmpl_path.relative_to(_SCRIPT_DIR)} ({len(template)} chars)")
    else:
        print("  template: (none)")

    pairs: list[tuple[str, str, float, float, float]] = []
    for line in lines:
        s = line.strip()
        if not s or not _is_result_data_row(s):
            continue
        parts = s.split(",")
        name_a = parts[0].removesuffix(".zip")
        name_b = parts[1].removesuffix(".zip")
        expected = 0.0
        low, high = 0.0, 1.0
        for p in parts[2:]:
            if p.startswith("expected="):
                expected = float(p.split("=", 1)[1])
            elif p.startswith("range="):
                rng = p.split("=", 1)[1]
                low_str, high_str = rng.split("-", 1)
                low, high = float(low_str), float(high_str)
        pairs.append((name_a, name_b, expected, low, high))

    pass_count = 0
    total = 0
    for name_a, name_b, expected, low, high in pairs:
        path_a = submissions_dir / name_a / "Main.java"
        path_b = submissions_dir / name_b / "Main.java"
        if not path_a.exists() or not path_b.exists():
            print(f"  SKIP {name_a} vs {name_b}: Main.java not found")
            continue
        total += 1
        code_a = path_a.read_text(encoding="utf-8")
        code_b = path_b.read_text(encoding="utf-8")
        try:
            score = sim_fn(code_a, code_b, template)
        except ValueError as e:
            print(f"  FAIL {name_a} vs {name_b}: ValueError: {e}")
            continue
        ok = low <= score <= high
        status = "PASS" if ok else "FAIL"
        if ok:
            pass_count += 1
        print(
            f"  {status} {name_a} vs {name_b}: sim={score:.2%} "
            f"(expected ~{expected:.2%}, range [{low:.2%},{high:.2%}])"
        )

    return (pass_count, total)

def demo_test_all(*, similarity_fn: JavaSimilarityFn | None = None) -> bool:
    overall_ok = True
    sum_pass = 0
    sum_total = 0

    for rel in REGRESSION_FIXTURES:
        title = str(rel).replace("\\", "/")
        print(f"\n--- Regression: {title} ---\n")
        passed, total = demo_test_on_regression(rel, similarity_fn=similarity_fn)
        sum_pass += passed
        sum_total += total
        fixture_ok = total > 0 and passed == total
        if not fixture_ok:
            overall_ok = False
        print(f"\n{title}: {passed}/{total} PASS\n")

    print("=" * 60)
    print(f"All fixtures combined: {sum_pass}/{sum_total} PASS")
    print(
        "Overall: "
        f"{'All regression fixtures fully passed.' if overall_ok else 'Some fixtures failed or had no tests.'}"
    )
    return overall_ok

if __name__ == "__main__":
    demo_test_all()

    
    #stage3 S09 & S10
    # path_a = _SCRIPT_DIR / "regression/assignment_stage3_rankset/submissions/S09/Main.java"
    # path_b = _SCRIPT_DIR / "regression/assignment_stage3_rankset/submissions/S10/Main.java"
    # # demo_function_pairing(path_a, path_b)
    # path_template = _SCRIPT_DIR / "regression/assignment_stage3_rankset/template/Template.java"
    # demo_test_single_pair(path_a, path_b, path_template)



    # print("\n--- Running similarity + render demo ---\n")
    # demo_similarity_and_render()
