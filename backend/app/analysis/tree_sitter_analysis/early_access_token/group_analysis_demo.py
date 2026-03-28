"""
Demo: Alice/Bob first five FingerprintPairGroups — token-type shares, filter config, keep.

Run from backend root with:
  python -m app.analysis.tree_sitter_analysis.early_access_token.group_analysis_demo
"""

from __future__ import annotations

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parents[4]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.tree_sitter_analysis.early_access_token.group_analysis import (
    evaluate_group_filter,
    filter_groups,
    group_tokentype_analysis,
    load_group_filter_config,
    load_type_mapping_csv,
)
from app.analysis.tree_sitter_analysis.early_access_token.token_fingerprint import (
    align_mapped_type_truth_tables,
    mapped_type_truth_table,
)
from app.analysis.tree_sitter_analysis.early_access_token.grouping_fingerprint_pairs import (
    grouping_fingerprint_pairs,
)
from app.analysis.tree_sitter_analysis.early_access_token.json_kgram_strategy import (
    JsonLeafKgramStrategy,
)
from app.analysis.tree_sitter_analysis.pipeline_demo import _fingerprint_pairs_for_two_java_codes


def main() -> None:
    here = Path(__file__).resolve().parent
    tree_sitter_root = here.parent
    path_a = tree_sitter_root / "regression/assignment_renamed_vars/submissions/Alice/Main.java"
    path_b = tree_sitter_root / "regression/assignment_renamed_vars/submissions/Bob/Main.java"
    mapping_path = here / "type_mapping.csv"
    filter_path = here / "group_filtering_config.json"

    if not path_a.is_file() or not path_b.is_file():
        print("[skip] Alice/Bob Main.java not found under tree_sitter_analysis/regression.")
        return
    if not mapping_path.is_file():
        print(f"[skip] {mapping_path} missing.")
        return
    if not filter_path.is_file():
        print(f"[skip] {filter_path} missing.")
        return

    code_a = path_a.read_text(encoding="utf-8")
    code_b = path_b.read_text(encoding="utf-8")
    strategy = JsonLeafKgramStrategy(k=5)
    pairs = _fingerprint_pairs_for_two_java_codes(
        code_a,
        code_b,
        strategy=strategy,
        winnow_window=4,
        max_pos_each=100,
    )
    groups = grouping_fingerprint_pairs(
        pairs,
        min_group_size=4,
        delta_tol=5,
        max_gap=120,
    )
    if not groups:
        print("No groups produced.")
        return

    tokens_a = list(strategy.tokens_for_kgram(code_a))
    tokens_b = list(strategy.tokens_for_kgram(code_b))
    k = strategy.k
    mapping = load_type_mapping_csv(mapping_path)
    filt = load_group_filter_config(filter_path)

    truth_a = mapped_type_truth_table(tokens_a, mapping)
    truth_b = mapped_type_truth_table(tokens_b, mapping)
    truth_a, truth_b = align_mapped_type_truth_tables(truth_a, truth_b)
    kept = filter_groups(
        groups,
        tokens_a=tokens_a,
        tokens_b=tokens_b,
        k=k,
        type_mapping=mapping,
        config=filt,
        truth_a=truth_a,
        truth_b=truth_b,
    )

    print("--- group_analysis_demo: Alice/Bob, first 5 groups ---\n")
    print(
        f"filter: keep_threshold={filt.keep_threshold} "
        f"default_similarity_no_match={filt.default_similarity_no_match}"
    )
    print(f"groups total={len(groups)}  kept by config filter={len(kept)}\n")

    n_show = min(20, len(groups))
    for idx in range(n_show):
        g = groups[idx]
        stats = group_tokentype_analysis(
            g, tokens_a, tokens_b, k, mapping, truth_a=truth_a, truth_b=truth_b
        )
        ev = evaluate_group_filter(
            g,
            tokens_a,
            tokens_b,
            k,
            mapping,
            filt,
            truth_a=truth_a,
            truth_b=truth_b,
        )

        print(f"========== group[{idx}] ==========")
        print(
            f"pairs={len(g.pairs)}  pos_a:[{g.pos_a_start}..{g.pos_a_end}]  "
            f"pos_b:[{g.pos_b_start}..{g.pos_b_end}]"
        )
        print(f"token span: A={stats.token_count_a}  B={stats.token_count_b}  mass A={stats.mass_a} B={stats.mass_b}")

        def top_shares_line(title: str, d: dict[str, float], n: int = 5) -> str:
            items = sorted(d.items(), key=lambda x: (-x[1], x[0]))[:n]
            inner = ", ".join(f"{k}={v:.3f}" for k, v in items)
            return f"{title} {inner}"

        print(top_shares_line("top shares A:", stats.side_a))
        print(top_shares_line("top shares B:", stats.side_b))

        if ev.matched_feature_names:
            print("matched features:", ", ".join(ev.matched_feature_names))
        else:
            print("matched features: (none — using default_similarity_no_match)")

        print(f"group similarity (weighted mean of matched contributions): {ev.similarity:.6f}")
        print(f"keep (similarity >= {filt.keep_threshold}): {ev.keep}")
        print()


if __name__ == "__main__":
    main()
