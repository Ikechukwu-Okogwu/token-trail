"""
Remove ``FingerprintPairGroup`` entries that are redundant under span inclusion.

**Idea**

1. For each group, compute the **inclusive token index span** on side A and B with the
   same rule as :func:`group_analysis.group_token_span_bounds` (matches ``dye_tokens``
   and ``TokenizePipelineResult.matching_regions_as_dicts``).

2. Group *i* is **dropped** if there exists another group *j* such that:

   - *j*'s A-span contains *i*'s A-span and *j*'s B-span contains *i*'s B-span; and
   - either containment is **strict** on at least one side (``i`` lies strictly inside
     ``j``), **or** both spans are **equal** but ``len(i.pairs) < len(j.pairs)`` (keep
     the richer chain), **or** equal spans and equal pair counts and ``i > j`` (stable
     tie-break, single survivor).

3. This yields an antichain-style subset: nested duplicates keep the **outer / longer**
   representative; exact duplicate spans keep one copy.

Transitive chains (e.g. small ⊂ medium ⊂ large) remove all non-maximal groups in one pass.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import (
    group_token_span_bounds,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.grouping_fingerprint_pairs import (
    FingerprintPairGroup,
)


def dedupe_subsumed_groups(
    groups: Sequence[FingerprintPairGroup],
    *,
    k: int,
    n_tokens_a: int,
    n_tokens_b: int,
) -> list[FingerprintPairGroup]:
    """
    Drop groups whose A/B token spans are contained in another group's spans.

    Empty ``groups`` → ``[]``. Uses the same ``k`` and token counts as the pipeline
    that produced the groups.
    """
    seq = list(groups)
    n = len(seq)
    if n == 0:
        return []

    spans: list[tuple[int, int, int, int]] = []
    for g in seq:
        lo_a, hi_a = group_token_span_bounds(g, side="a", k=k, n_tokens=n_tokens_a)
        lo_b, hi_b = group_token_span_bounds(g, side="b", k=k, n_tokens=n_tokens_b)
        spans.append((lo_a, hi_a, lo_b, hi_b))

    remove: set[int] = set()
    for i in range(n):
        lai, hai, lbi, hbi = spans[i]
        if hai < lai or hbi < lbi:
            remove.add(i)
            continue
        for j in range(n):
            if i == j:
                continue
            laj, haj, lbj, hbj = spans[j]
            if haj < laj or hbj < lbj:
                continue
            if not (laj <= lai and haj >= hai and lbj <= lbi and hbj >= hbi):
                continue
            strict_a = (laj < lai) or (haj > hai)
            strict_b = (lbj < lbi) or (hbj > hbi)
            if strict_a or strict_b:
                remove.add(i)
                break
            if (lai, hai, lbi, hbi) == (laj, haj, lbj, hbj):
                ni, nj = len(seq[i].pairs), len(seq[j].pairs)
                if ni < nj:
                    remove.add(i)
                    break
                if ni == nj and i > j:
                    remove.add(i)
                    break

    return [seq[i] for i in range(n) if i not in remove]
