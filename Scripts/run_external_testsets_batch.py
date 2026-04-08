#!/usr/bin/env python3
"""Batch-evaluate ExternalTestSets/ with the same engine path as regression fixtures.

One command (from repository root):

    python scripts/run_external_testsets_batch.py

Optional:

    python scripts/run_external_testsets_batch.py --output report.txt

See docs/EXTERNAL_ENGINE_EVAL.md for layout details. This script applies the same
homogeneous-language rules as production; mixed bundles use filtered subsets where noted.

For Java, pairwise scores use the leaf-token (Tree-sitter) pipeline when the backend
imports succeed, including runs with ``--template-exclusion`` (see
``tests.analysis.regression_runner.compute_pairwise_similarity_scores``), and fall
back to character winnowing only if tokenization fails for a pair.
"""

from __future__ import annotations

import argparse
import statistics
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

CONFIG: list[tuple[str, Path, str, bool]] = [
    ("TestSet2", REPO / "ExternalTestSets/TestSet2", "java", False),
    ("TestSet9", REPO / "ExternalTestSets/TestSet9", "java", False),
    ("TestSet10", REPO / "ExternalTestSets/TestSet10", "java", False),
    ("TestSet17", REPO / "ExternalTestSets/TestSet17", "java", False),
    ("TestSet18", REPO / "ExternalTestSets/TestSet18", "java", False),
    ("TestSet20", REPO / "ExternalTestSets/TestSet20", "java", False),
]


def run_eval(assignment_dir: Path, language: str, *, template_exclusion: bool) -> tuple[int, str, str]:
    cmd = [
        sys.executable,
        "-m",
        "tests.analysis.external_eval",
        "--assignment-dir",
        str(assignment_dir),
        "--language",
        language,
        "--csv",
    ]
    if template_exclusion:
        cmd.append("--template-exclusion")
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def parse_scores(csv_text: str) -> list[float]:
    """Parse external_eval --csv lines; ignore [CUT] debug lines on stdout."""
    scores: list[float] = []
    for line in csv_text.splitlines():
        line = line.strip()
        if ".zip," not in line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        if not parts[0].endswith(".zip") or not parts[1].endswith(".zip"):
            continue
        try:
            scores.append(float(parts[2]))
        except ValueError:
            continue
    return scores


def _stats(scores: list[float], n_zip: int) -> dict:
    return {
        "submissions": n_zip,
        "pairs": len(scores),
        "min": min(scores),
        "max": max(scores),
        "mean": statistics.mean(scores),
        "median": statistics.median(scores),
    }


def _zip_has_suffixes(z: Path, suffixes: set[str]) -> bool:
    with zipfile.ZipFile(z) as zf:
        for n in zf.namelist():
            suf = Path(n).suffix.lower()
            if suf in suffixes:
                return True
    return False


def run_c_problem1_nested() -> tuple[str, dict | None, str]:
    outer = REPO / "ExternalTestSets/c_problem1/c_problem1/C_class_submissions.zip"
    if not outer.is_file():
        return "c_problem1", None, "missing C_class_submissions.zip"
    with tempfile.TemporaryDirectory() as tmp:
        sub = Path(tmp) / "submissions"
        sub.mkdir()
        with zipfile.ZipFile(outer) as zf:
            zf.extractall(sub)
        inner = sorted(sub.rglob("*.zip"))
        if len(inner) < 2:
            return "c_problem1", None, "fewer than 2 inner zips"
        work = Path(tmp) / "work"
        work.mkdir()
        dest_sub = work / "submissions"
        dest_sub.mkdir()
        for p in inner:
            (dest_sub / p.name).write_bytes(p.read_bytes())
        code, out, err = run_eval(work, "c", template_exclusion=False)
    if code != 0:
        return "c_problem1", None, (err or out).strip()[:500]
    scores = parse_scores(out)
    if not scores:
        return "c_problem1", None, "no scores"
    return "c_problem1", _stats(scores, len(inner)), ""


def run_testset1_cpp_homogeneous() -> tuple[str, dict | None, str]:
    """C++-only zips (no .java / .c inside). TestSet1 is mostly Java/C; often <2 qualify."""
    src = REPO / "ExternalTestSets/TestSet1/TestSet1"
    if not src.is_dir():
        return "TestSet1_cpp_only", None, "missing dir"
    zips = sorted(z for z in src.glob("*.zip") if not _zip_has_suffixes(z, {".java", ".c"}))
    if len(zips) < 2:
        return (
            "TestSet1_cpp_only",
            None,
            f"skip: only {len(zips)} zip(s) without .java/.c (need 2+ for pairwise)",
        )
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        for z in zips:
            (tdir / z.name).write_bytes(z.read_bytes())
        code, out, err = run_eval(tdir, "cpp", template_exclusion=False)
    if code != 0:
        return "TestSet1_cpp_only", None, (err or out).strip()[:400]
    scores = parse_scores(out)
    if not scores:
        return "TestSet1_cpp_only", None, "no scores"
    return "TestSet1_cpp_only", _stats(scores, len(zips)), ""


def run_testset3_java_subset() -> tuple[str, dict | None, str]:
    src = REPO / "ExternalTestSets/TestSet3/TestSet3"
    if not src.is_dir():
        return "TestSet3_java_only", None, "missing dir"
    keep: list[Path] = []
    for z in sorted(src.glob("*.zip")):
        with zipfile.ZipFile(z) as zf:
            names = zf.namelist()
        if any(n.lower().endswith(".java") for n in names):
            keep.append(z)
    if len(keep) < 2:
        return "TestSet3_java_only", None, "fewer than 2 java zips"
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        for z in keep:
            (tdir / z.name).write_bytes(z.read_bytes())
        code, out, err = run_eval(tdir, "java", template_exclusion=False)
    if code != 0:
        return "TestSet3_java_only", None, (err or out).strip()[:400]
    scores = parse_scores(out)
    if not scores:
        return "TestSet3_java_only", None, "no scores"
    return "TestSet3_java_only", _stats(scores, len(keep)), ""


def run_testset7() -> tuple[str, dict | None, str]:
    base = REPO / "ExternalTestSets/TestSet7(1)"
    zips = sorted(base.glob("Submission*/*.zip"))
    if len(zips) < 2:
        return "TestSet7(1)", None, "fewer than 2 zips"
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        for z in zips:
            (tdir / z.name).write_bytes(z.read_bytes())
        code, out, err = run_eval(tdir, "java", template_exclusion=False)
    if code != 0:
        return "TestSet7(1)", None, (err or out).strip()
    scores = parse_scores(out)
    if not scores:
        return "TestSet7(1)", None, "no scores"
    return "TestSet7(1)", _stats(scores, len(zips)), ""


def run_testset20_with_boilerplate() -> tuple[str, dict | None, str]:
    src_sub = REPO / "ExternalTestSets/TestSet20"
    tpl_src = REPO / "ExternalTestSets/TestSet20BoilerPlate"
    zips = sorted(src_sub.glob("*.zip"))
    if len(zips) < 2:
        return "TestSet20+boilerplate", None, "fewer than 2 submission zips"
    if not tpl_src.is_dir():
        return "TestSet20+boilerplate", None, "missing TestSet20BoilerPlate"
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        subs = tdir / "submissions"
        subs.mkdir()
        for z in zips:
            (subs / z.name).write_bytes(z.read_bytes())
        with zipfile.ZipFile(tdir / "template.zip", "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(tpl_src.glob("*.java")):
                zf.write(f, f.name)
        code, out, err = run_eval(tdir, "java", template_exclusion=True)
    if code != 0:
        return "TestSet20+boilerplate", None, (err or out).strip()[:500]
    scores = parse_scores(out)
    if not scores:
        return "TestSet20+boilerplate", None, "no scores"
    return "TestSet20+boilerplate", _stats(scores, len(zips)), ""


def run_cosc_java() -> tuple[str, dict | None, str]:
    cosc = (
        REPO
        / "ExternalTestSets/COSC 4P02 - Group 11 - Phase 3 Contents"
        / "COSC 4P02 - Group 11 - Phase 3 Contents"
    )
    bundle = cosc / "Java Test Set.zip"
    boiler = cosc / "Java Boilerplate.zip"
    if not bundle.is_file():
        return "COSC_Java_50", None, "missing Java Test Set.zip"
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        sub = tdir / "submissions"
        sub.mkdir()
        with zipfile.ZipFile(bundle) as zf:
            zf.extractall(sub)
        inner = sorted(sub.glob("*.zip"))
        if len(inner) < 2:
            return "COSC_Java_50", None, f"expected inner zips, got {len(inner)}"
        if boiler.is_file():
            (tdir / "template.zip").write_bytes(boiler.read_bytes())
            code, out, err = run_eval(tdir, "java", template_exclusion=True)
        else:
            code, out, err = run_eval(tdir, "java", template_exclusion=False)
    if code != 0:
        return "COSC_Java_50", None, (err or out).strip()[:500]
    scores = parse_scores(out)
    if not scores:
        return "COSC_Java_50", None, "no scores"
    return "COSC_Java_50", _stats(scores, len(inner)), ""


def run_java_folder_skip_mixed(label: str, src: Path) -> tuple[str, dict | None, str]:
    if not src.is_dir():
        return label, None, "missing dir"
    non_java = {".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hh"}
    keep = sorted(z for z in src.glob("*.zip") if not _zip_has_suffixes(z, non_java))
    if len(keep) < 2:
        return label, None, "fewer than 2 java-only zips after excluding C/C++ sources"
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        for z in keep:
            (tdir / z.name).write_bytes(z.read_bytes())
        code, out, err = run_eval(tdir, "java", template_exclusion=False)
    if code != 0:
        return label, None, (err or out).strip()[:400]
    scores = parse_scores(out)
    if not scores:
        return label, None, "no scores"
    return label, _stats(scores, len(keep)), ""


def _format_line(label: str, stats: dict | None, err: str) -> str:
    if stats:
        st = stats
        return (
            f"{label}: submissions={st['submissions']} pairs={st['pairs']} "
            f"min={st['min']:.4f} max={st['max']:.4f} mean={st['mean']:.4f} median={st['median']:.4f}"
        )
    return f"{label}: {err}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch pairwise similarity report for ExternalTestSets/.")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Write the same text that is printed to stdout to this file (UTF-8).",
    )
    args = parser.parse_args()

    lines_out: list[str] = []

    for label, adir, lang, tmpl in CONFIG:
        if not adir.is_dir():
            lines_out.append(f"{label}: SKIP (missing dir)")
            continue
        code, out, err = run_eval(adir, lang, template_exclusion=tmpl)
        if code != 0:
            lines_out.append(_format_line(label, None, f"ERROR — {(err or out).strip()[:300]}"))
            continue
        scores = parse_scores(out)
        if not scores:
            lines_out.append(_format_line(label, None, "ERROR — no scores"))
            continue
        zips_here = sorted(adir.glob("*.zip"))
        lines_out.append(_format_line(label, _stats(scores, len(zips_here)), ""))

    for label, rel in (
        ("TestSet12_java_only", "ExternalTestSets/TestSet12"),
        ("TestSet13_java_only", "ExternalTestSets/TestSet13/TestSet13"),
        ("TestSet15_java_only", "ExternalTestSets/TestSet15"),
        ("testset5_java_only", "ExternalTestSets/testset5"),
    ):
        ll, stats, err = run_java_folder_skip_mixed(label, REPO / rel)
        lines_out.append(_format_line(ll, stats, err))

    for fn in (
        run_c_problem1_nested,
        run_testset1_cpp_homogeneous,
        run_testset3_java_subset,
        run_testset7,
        run_testset20_with_boilerplate,
        run_cosc_java,
    ):
        label, stats, err = fn()
        lines_out.append(_format_line(label, stats, err))

    text = "\n".join(lines_out) + "\n"
    sys.stdout.write(text)
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
