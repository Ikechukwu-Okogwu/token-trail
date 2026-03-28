"""
Demo: full tokenize pipeline (pair → group → filter → dye similarity).

Also runs ``pipeline_demo`` regression harness with dye coverage as the score, to
compare against fixtures that were authored for ``compute_similarity_javacode`` (file-
class Winnow mean). Expect many FAIL / mismatch: missing values measure different things.

Run from backend root:
  python -m app.analysis.tree_sitter_analysis.tokenize_pipeline_demo
"""

from __future__ import annotations

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parents[3]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.tree_sitter_analysis.pipeline_demo import (
    REGRESSION_FIXTURES,
    JavaSimilarityFn,
    _is_result_data_row,
    demo_test_all,
)
from app.analysis.tree_sitter_analysis.tokenize_pipeline import (
    run_tokenize_similarity_pipeline,
)


def tokenize_dye_similarity_for_regression(
    code_a: str,
    code_b: str,
    template: str,
) -> float:
    """
    Adapter for ``pipeline_demo.demo_test_*``: same signature as
    ``compute_similarity_javacode``.

    ``template`` is ignored — the tokenize pipeline compares full sources as read
    from ``Main.java`` (no class-pairing / template exclusion).
    """
    _ = template
    result = run_tokenize_similarity_pipeline(code_a, code_b)
    return float(result.similarity)


def _alice_bob_snapshot() -> None:
    here = Path(__file__).resolve().parent
    root = here / "regression/assignment_renamed_vars/submissions"
    path_a = root / "Alice/Main.java"
    path_b = root / "Bob/Main.java"

    if not path_a.is_file() or not path_b.is_file():
        print("[skip] Alice/Bob Main.java not found under tree_sitter_analysis/regression.")
        return

    code_a = path_a.read_text(encoding="utf-8")
    code_b = path_b.read_text(encoding="utf-8")

    result = run_tokenize_similarity_pipeline(code_a, code_b)

    print("--- tokenize_pipeline_demo: assignment_renamed_vars Alice vs Bob ---\n")
    print(f"k={result.strategy_k}  tokens: A={len(result.tokens_a)}  B={len(result.tokens_b)}")
    print(f"kept groups (after filter): {len(result.groups)}")
    print(
        f"dye: marked A={result.dye.marked_count_a}  B={result.dye.marked_count_b}  "
        f"similarity={(result.dye.marked_count_a + result.dye.marked_count_b)}/"
        f"{result.dye.n_tokens_a + result.dye.n_tokens_b} = {result.similarity:.6f}"
    )
    if result.groups:
        g0 = result.groups[0]
        print(
            f"\nfirst kept group: pairs={len(g0.pairs)}  "
            f"pos_a:[{g0.pos_a_start}..{g0.pos_a_end}]  "
            f"pos_b:[{g0.pos_b_start}..{g0.pos_b_end}]"
        )


def main() -> None:
    _alice_bob_snapshot()

    print("\n" + "=" * 60)
    print("Regression harness (pipeline_demo) with dye coverage similarity")
    print("=" * 60)
    print(
        "Score = (marked tokens A + marked tokens B) / (|A| + |B|) after group filter.\n"
        "Fixture expected/range targets ``compute_similarity_javacode`` (per-class "
        "function Winnow mean + template exclusion). This run is for calibration / "
        "sanity only — do not expect ranges to PASS unchanged.\n"
    )

    sim_fn: JavaSimilarityFn = tokenize_dye_similarity_for_regression
    demo_test_all(similarity_fn=sim_fn)

    print(
        "\n--- Per-fixture dye stats (pairs with both Main.java) ---\n"
    )
    script_dir = Path(__file__).resolve().parent
    for rel in REGRESSION_FIXTURES:
        base = script_dir / rel
        result_file = base / "result.txt"
        submissions_dir = base / "submissions"
        if not result_file.is_file() or not submissions_dir.is_dir():
            continue
        lines = result_file.read_text(encoding="utf-8").strip().splitlines()
        pair_rows: list[tuple[str, str]] = []
        for line in lines:
            s = line.strip()
            if not s or not _is_result_data_row(s):
                continue
            parts = s.split(",")
            name_a = parts[0].removesuffix(".zip")
            name_b = parts[1].removesuffix(".zip")
            pair_rows.append((name_a, name_b))

        title = str(rel).replace("\\", "/")
        printed = 0
        for name_a, name_b in pair_rows[:5]:
            path_a = submissions_dir / name_a / "Main.java"
            path_b = submissions_dir / name_b / "Main.java"
            if not path_a.is_file() or not path_b.is_file():
                continue
            code_a = path_a.read_text(encoding="utf-8")
            code_b = path_b.read_text(encoding="utf-8")
            try:
                r = run_tokenize_similarity_pipeline(code_a, code_b)
            except (ValueError, FileNotFoundError) as e:
                print(f"  [{title}] {name_a} vs {name_b}: error: {e}")
                continue
            print(
                f"  [{title}] {name_a} vs {name_b}: dye={r.similarity:.4f}  "
                f"kept_groups={len(r.groups)}  tokens {len(r.tokens_a)}+{len(r.tokens_b)}"
            )
            printed += 1
        if printed == 0 and pair_rows:
            print(f"  [{title}] (no sample pairs with both Main.java on disk)")


if __name__ == "__main__":
    main()
