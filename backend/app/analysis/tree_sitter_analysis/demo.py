"""
Unified demos for the tokenize similarity pipeline.

- Compare two Java files via :func:`run_tokenize_similarity_pipeline`.
- Run regression fixtures under ``regression/`` (same ``result.txt`` format as before).

Run from ``token-trail/backend``:

  python -m app.analysis.tree_sitter_analysis.demo compare PATH_A PATH_B [--template PATH]
  python -m app.analysis.tree_sitter_analysis.demo regression [--silence]
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TypeAlias

_backend = Path(__file__).resolve().parents[3]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.config import (
    SUPPORTED_TOKENIZE_LANGUAGES,
    TokenizePipelineConfig,
    load_tokenize_pipeline_config_for_language,
)
from app.analysis.tree_sitter_analysis.tokenize_pipeline import (
    TokenizePipelineResult,
    run_tokenize_similarity_pipeline,
)

_SCRIPT_DIR = Path(__file__).resolve().parent

REGRESSION_FIXTURES: list[Path] = [
    Path("regression/assignment_reordered_functions"),
    Path("regression/assignment_renamed_vars"),
    Path("regression/assignment_renamed_vars_c"),
    Path("regression/assignment_reordered_functions_c"),
    Path("regression/assignment_template_heavy"),
    Path("regression/assignment_template_heavy_c"),
    Path("regression/assignment_renamed_vars_cpp"),
    Path("regression/assignment_reordered_functions_cpp"),
    Path("regression/assignment_stage3_rankset"),
]

RegressionRow: TypeAlias = tuple[
    str,
    str,
    float | None,
    bool,
    float,
    tuple[float, float],
]


def _submission_source_candidates(submission_dir: Path, language: str) -> list[Path]:
    """
    Non-recursive: regular files under ``submission_dir`` whose suffix matches the
    tokenize language (excluding dotfiles). Sorted by name for a stable order.
    """
    lang = (language or "").strip().lower()
    if lang not in SUPPORTED_TOKENIZE_LANGUAGES:
        raise ValueError(
            f"submission source resolution: unsupported language {language!r} "
            f"(expected one of {sorted(SUPPORTED_TOKENIZE_LANGUAGES)})"
        )
    if not submission_dir.is_dir():
        return []

    def _suffix_ok(path: Path) -> bool:
        ext = path.suffix.lower()
        if lang == "java":
            return ext == ".java"
        if lang == "c":
            return ext == ".c"
        if lang == "cpp":
            return ext in (".cpp", ".cc", ".cxx")
        return False

    return sorted(
        p
        for p in submission_dir.iterdir()
        if p.is_file() and not p.name.startswith(".") and _suffix_ok(p)
    )


def resolve_unique_submission_source_path(
    submission_dir: Path,
    language: str,
    *,
    context: str,
) -> Path:
    """
    Exactly one language-appropriate source file must exist directly under
    ``submission_dir``; otherwise raise ``ValueError`` with ``context`` in the message.
    """
    lang = (language or "").strip().lower()
    candidates = _submission_source_candidates(submission_dir, language)
    if len(candidates) == 0:
        ext_hint = (
            "*.java"
            if lang == "java"
            else "*.c"
            if lang == "c"
            else "*.cpp / *.cc / *.cxx"
        )
        raise ValueError(
            f"{context}: no {ext_hint} source file under {submission_dir.resolve()} "
            f"(need exactly one)"
        )
    if len(candidates) > 1:
        names = ", ".join(sorted(p.name for p in candidates))
        raise ValueError(
            f"{context}: ambiguous sources for language={language!r} under "
            f"{submission_dir.resolve()}: {names}"
        )
    return candidates[0]


def _is_result_data_row(line: str) -> bool:
    parts = line.split(",")
    return len(parts) >= 3 and ".zip" in parts[0]


def _read_fixture_template_and_pairs(
    base: Path,
) -> tuple[str, list[tuple[str, str, float, float, float]], str]:
    """
    Parse ``result.txt`` for ``template_exclusion`` / ``template_file`` and data rows.

    Submission sources are **not** read from ``result.txt``: each pair resolves the
    single appropriate file under ``submissions/<name>/`` via
    :func:`resolve_unique_submission_source_path` (``language=`` selects extensions).

    Optional ``language=java`` / ``c`` / ``cpp`` selects the tokenizer and default
    bundle (see :func:`run_tokenize_similarity_pipeline`); defaults to ``java``.

    Returns:
        ``(template_text, pairs, language)``
    """
    result_file = base / "result.txt"
    if not result_file.is_file():
        return "", [], "java"
    lines = result_file.read_text(encoding="utf-8").strip().splitlines()
    template_exclusion = False
    template_rel: str | None = None
    language = "java"
    for line in lines:
        s = line.strip()
        if s.startswith("template_exclusion="):
            template_exclusion = s.split("=", 1)[1].strip().lower() == "true"
        elif s.startswith("template_file="):
            template_rel = s.split("=", 1)[1].strip()
        elif s.startswith("language="):
            v = s.split("=", 1)[1].strip().lower()
            if v in SUPPORTED_TOKENIZE_LANGUAGES:
                language = v

    template = ""
    if template_exclusion:
        if template_rel:
            rel = template_rel
        elif language == "c":
            rel = "template/Template.c"
        elif language == "cpp":
            rel = "template/Template.cpp"
        else:
            rel = "template/Template.java"
        tmpl_path = base / rel
        if tmpl_path.is_file():
            template = tmpl_path.read_text(encoding="utf-8")

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

    return template, pairs, language


def compare_two_files(
    path_a: str | Path,
    path_b: str | Path,
    *,
    template: str | None = None,
    template_path: str | Path | None = None,
    config: TokenizePipelineConfig | None = None,
    language: str = "java",
    silence: bool = False,
) -> TokenizePipelineResult:
    """
    Read two source files, run the tokenize pipeline, optionally apply template exclusion.

    ``template_path`` wins over ``template`` when the path exists as a file.
    ``language`` is ``java``, ``c``, or ``cpp`` (tokenizer and default bundle when
    ``config`` is omitted).
    """
    pa = Path(path_a)
    pb = Path(path_b)
    if not pa.is_file():
        raise FileNotFoundError(f"not a file: {pa.resolve()}")
    if not pb.is_file():
        raise FileNotFoundError(f"not a file: {pb.resolve()}")

    tpl = ""
    if template_path is not None:
        tp = Path(template_path)
        if tp.is_file():
            tpl = tp.read_text(encoding="utf-8")
    if not tpl and template is not None:
        tpl = template

    cfg = config or load_tokenize_pipeline_config_for_language(language)
    code_a = pa.read_text(encoding="utf-8")
    code_b = pb.read_text(encoding="utf-8")
    result = run_tokenize_similarity_pipeline(
        code_a, code_b, config=cfg, language=language, template=tpl
    )

    if not silence:
        title = f"{pa.name} vs {pb.name}"
        print(f"--- tokenize similarity: {title} ---\n")
        print(f"  path A: {pa.resolve()}")
        print(f"  path B: {pb.resolve()}")
        print(
            f"  k={result.strategy_k}  tokens: A={len(result.tokens_a)}  "
            f"B={len(result.tokens_b)}"
        )
        print(f"  kept groups (after filter + dedupe): {len(result.groups)}")
        print(
            f"  dye: marked A={result.dye.marked_count_a}  B={result.dye.marked_count_b}  "
            f"similarity={(result.dye.marked_count_a + result.dye.marked_count_b)}/"
            f"{result.dye.n_tokens_a + result.dye.n_tokens_b} = {result.similarity:.6f}"
        )
        regions = result.matching_regions_as_dicts()
        if regions:
            print(f"  matching regions (line spans): {len(regions)}")
            r0 = regions[0]
            print(
                "  first region: "
                f"left L{r0['leftStartLine']}-{r0['leftEndLine']}  "
                f"right L{r0['rightStartLine']}-{r0['rightEndLine']}"
            )
        if result.groups:
            g0 = result.groups[0]
            print(
                f"\n  first kept group: pairs={len(g0.pairs)}  "
                f"pos_a:[{g0.pos_a_start}..{g0.pos_a_end}]  "
                f"pos_b:[{g0.pos_b_start}..{g0.pos_b_end}]"
            )
        print()

    return result


def run_regression_tests(
    *,
    config: TokenizePipelineConfig | None = None,
    silence: bool = False,
    fixtures: Sequence[Path] | None = None,
) -> list[RegressionRow]:
    """
    Run regression pairs using the tokenize pipeline (Java and/or C per fixture headers).

    Returns:
        One tuple per executed pair:
        ``(submission_a, submission_b, result, is_pass, expected, (range_low, range_high))``.
        ``result`` is ``None`` if the pipeline raised or I/O failed. Skipped pairs
        (missing files) are omitted.

        ``config``: when ``None``, each fixture loads ``bundles/<language>_default``
        from its ``result.txt`` ``language=`` line (default ``java``).
    """
    use_fixtures = list(fixtures) if fixtures is not None else REGRESSION_FIXTURES
    rows: list[RegressionRow] = []

    for rel in use_fixtures:
        base = _SCRIPT_DIR / rel
        title = str(rel).replace("\\", "/")
        template, pairs, language = _read_fixture_template_and_pairs(base)
        fixture_cfg = (
            config
            if config is not None
            else load_tokenize_pipeline_config_for_language(language)
        )
        submissions_dir = base / "submissions"
        if not submissions_dir.is_dir():
            if not silence:
                print(f"[skip] {title}: no submissions dir")
            continue

        if not silence:
            print(f"\n--- Regression: {title} ---")
            print(f"  language={language}")
            if template:
                print(f"  template loaded ({len(template)} chars)")
            else:
                print("  template: (none)")

        batch: list[RegressionRow] = []
        for name_a, name_b, expected, low, high in pairs:
            ctx = f"fixture {title!r} pair ({name_a} vs {name_b})"
            path_a = resolve_unique_submission_source_path(
                submissions_dir / name_a, language, context=ctx
            )
            path_b = resolve_unique_submission_source_path(
                submissions_dir / name_b, language, context=ctx
            )
            code_a = path_a.read_text(encoding="utf-8")
            code_b = path_b.read_text(encoding="utf-8")
            score: float | None = None
            try:
                r = run_tokenize_similarity_pipeline(
                    code_a,
                    code_b,
                    config=fixture_cfg,
                    language=language,
                    template=template,
                )
                score = float(r.similarity)
            except (ValueError, OSError) as e:
                if not silence:
                    print(f"  FAIL {name_a} vs {name_b}: {e}")

            is_pass = score is not None and low <= score <= high
            if not silence and score is not None:
                status = "PASS" if is_pass else "FAIL"
                print(
                    f"  {status} {name_a} vs {name_b}: sim={score:.2%} "
                    f"(expected ~{expected:.2%}, range [{low:.2%},{high:.2%}])"
                )

            row: RegressionRow = (name_a, name_b, score, is_pass, expected, (low, high))
            batch.append(row)
            rows.append(row)

        if not silence:
            passed = sum(1 for r in batch if r[3])
            print(f"\n{title}: {passed}/{len(batch)} PASS\n")

    if not silence:
        ok = sum(1 for r in rows if r[3])
        print("=" * 60)
        print(f"All fixtures combined: {ok}/{len(rows)} PASS")
        print(
            "Overall: "
            f"{'All regression rows passed.' if len(rows) > 0 and ok == len(rows) else 'Some rows failed, had errors, or fixtures were empty.'}"
        )

    return rows


def _cli() -> None:
    p = argparse.ArgumentParser(description="Tree-sitter tokenize pipeline demos.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser(
        "compare", help="Compare two source files with the pipeline (Java/C/C++ via --language)."
    )
    pc.add_argument("path_a", type=Path)
    pc.add_argument("path_b", type=Path)
    pc.add_argument("--template", type=Path, default=None, help="Template Java path")
    pc.add_argument(
        "--language",
        choices=sorted(SUPPORTED_TOKENIZE_LANGUAGES),
        default="java",
        help="Tokenizer and default bundle (when not passing custom config).",
    )

    pr = sub.add_parser("regression", help="Run all regression fixtures.")
    pr.add_argument(
        "--silence",
        action="store_true",
        help="No print; use returned list only.",
    )

    args = p.parse_args()
    if args.cmd == "compare":
        compare_two_files(
            args.path_a,
            args.path_b,
            template_path=args.template,
            language=args.language,
            silence=False,
        )
    else:
        run_regression_tests(silence=args.silence)


if __name__ == "__main__":
    _cli()
