"""
Heuristic veto for “does this look like Java?” based on ``type_identifier`` casing.

Not wired into upload or tokenize pipeline until reviewed. Callers
pass leaf tokens from ``tokenize_java``.

Veto rule: among tokens with ``type == "type_identifier"``, if the fraction whose
``text`` does **not** start with an ASCII uppercase letter (``A``–``Z``) is
**strictly greater** than :data:`NON_CAPITAL_TYPE_IDENTIFIER_RATIO_THRESHOLD`, return
``True`` (treat as failing the heuristic / recommend veto). Otherwise ``False``.

If there are zero ``type_identifier`` tokens, returns ``False`` (no signal).
"""

from __future__ import annotations

from collections.abc import Sequence

from app.analysis.tree_sitter_analysis.tokenize_workflow.token_fingerprint import Token

# Fraction of type_identifiers that must be "non–uppercase-start" to trigger veto.
NON_CAPITAL_TYPE_IDENTIFIER_RATIO_THRESHOLD = 0.30


def _type_identifier_starts_ascii_uppercase(text: str) -> bool:
    if not text:
        return False
    c0 = text[0]
    return "A" <= c0 <= "Z"


def lowercase_type_identifier_veto(tokens: Sequence[Token]) -> bool:
    """
    Return ``True`` if the lowercase-leading ``type_identifier`` share exceeds the
    threshold (veto / likely not Java type naming), else ``False``.

    ``True`` means: more than :data:`NON_CAPITAL_TYPE_IDENTIFIER_RATIO_THRESHOLD`
    of ``type_identifier`` rows have ``text`` whose first character is not ``A``–``Z``.
    """
    type_id_tokens = [t for t in tokens if t.type == "type_identifier"]
    n = len(type_id_tokens)
    if n == 0:
        return False

    non_capital = sum(
        1 for t in type_id_tokens if not _type_identifier_starts_ascii_uppercase(t.text)
    )
    ratio = non_capital / n
    return ratio > NON_CAPITAL_TYPE_IDENTIFIER_RATIO_THRESHOLD
