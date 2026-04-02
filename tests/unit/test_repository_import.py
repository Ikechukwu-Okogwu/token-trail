"""
Unit tests for the repository import endpoint.

Tests both import formats:
  Format A — flat zip-of-zips: StudentA.zip, StudentB.zip at top level
  Format B — folder/raw.zip:  StudentA/raw.zip (Token Trail export)

Also tests: malformed ZIPs, wrong-language content, duplicate handling,
partial failure summaries, format detection logic.

These tests run WITHOUT Docker — no network, no MongoDB.
"""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest

# Make the backend importable without installing it
_BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.services.zip_service import list_valid_source_files, safe_extract_zip
from app.services.merge_service import merge_source_files


# ── Helpers ──────────────────────────────────────────

def _make_inner_zip(files: dict[str, str]) -> bytes:
    """Build an in-memory ZIP from {filename: content} pairs."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _make_repo_format_a(submissions: dict[str, bytes]) -> bytes:
    """Build a Format A repo: top-level .zip entries."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, inner_bytes in submissions.items():
            zf.writestr(f"{name}.zip", inner_bytes)
    return buf.getvalue()


def _make_repo_format_b(submissions: dict[str, bytes]) -> bytes:
    """Build a Format B repo: folder/raw.zip entries."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, inner_bytes in submissions.items():
            zf.writestr(f"{name}/raw.zip", inner_bytes)
    return buf.getvalue()


def _detect_entries(repo_bytes: bytes) -> list[tuple[str, bytes]]:
    """Replicate the endpoint's format detection logic for testing."""
    entries = []
    with zipfile.ZipFile(io.BytesIO(repo_bytes)) as zf:
        # Format A: top-level .zip files
        for info in zf.infolist():
            name = info.filename
            if "/" not in name and name.lower().endswith(".zip"):
                entries.append((name[:-4], zf.read(info)))

        # Fallback to Format B if no top-level zips
        if not entries:
            folders: dict[str, list] = {}
            for info in zf.infolist():
                parts = info.filename.split("/")
                if len(parts) < 2 or not parts[0]:
                    continue
                folders.setdefault(parts[0], []).append(info)

            for folder_name, members in sorted(folders.items()):
                for m in members:
                    if m.filename == f"{folder_name}/raw.zip":
                        entries.append((folder_name, zf.read(m)))
                        break
    return entries


def _process_entry(inner_bytes: bytes, language: str, tmp_path: Path) -> list[Path]:
    """Extract an inner zip and return valid source files."""
    zip_path = tmp_path / "raw.zip"
    zip_path.write_bytes(inner_bytes)
    extracted = tmp_path / "extracted"
    extracted.mkdir(exist_ok=True)
    safe_extract_zip(zip_path, extracted)
    return list_valid_source_files(extracted, language)


_JAVA_HELLO = """\
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""

_JAVA_WORLD = """\
public class World {
    public static void main(String[] args) {
        System.out.println("World");
    }
}
"""

_C_HELLO = """\
#include <stdio.h>
int main(void) {
    printf("Hello\\n");
    return 0;
}
"""

_PYTHON_CODE = """\
def hello():
    print("Hello")

if __name__ == "__main__":
    hello()
"""


# ── Format detection ─────────────────────────────────

def test_format_a_detected():
    """Top-level .zip files are detected as Format A entries."""
    inner = _make_inner_zip({"Hello.java": _JAVA_HELLO})
    repo = _make_repo_format_a({"Alice": inner, "Bob": inner})
    entries = _detect_entries(repo)
    names = [e[0] for e in entries]
    assert "Alice" in names
    assert "Bob" in names
    assert len(entries) == 2


def test_format_b_detected():
    """folder/raw.zip layout is detected as Format B entries."""
    inner = _make_inner_zip({"Hello.java": _JAVA_HELLO})
    repo = _make_repo_format_b({"Alice": inner, "Bob": inner})
    entries = _detect_entries(repo)
    names = [e[0] for e in entries]
    assert "Alice" in names
    assert "Bob" in names
    assert len(entries) == 2


def test_format_a_takes_priority_over_folders():
    """If both top-level .zips and folders exist, Format A wins."""
    inner = _make_inner_zip({"Hello.java": _JAVA_HELLO})
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("TopLevel.zip", inner)
        zf.writestr("SomeFolder/raw.zip", inner)
    entries = _detect_entries(buf.getvalue())
    names = [e[0] for e in entries]
    assert names == ["TopLevel"]


def test_empty_zip_no_entries():
    """A ZIP with no .zips and no folders yields no entries."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("README.txt", "nothing useful")
    entries = _detect_entries(buf.getvalue())
    assert len(entries) == 0


# ── Format A: full pipeline ──────────────────────────

def test_format_a_extract_and_merge(tmp_path):
    """Format A: inner .zip extracted, filtered, merged correctly."""
    inner = _make_inner_zip({"Hello.java": _JAVA_HELLO, "notes.txt": "ignore"})
    repo = _make_repo_format_a({"StudentA": inner})
    entries = _detect_entries(repo)
    assert len(entries) == 1

    identifier, inner_bytes = entries[0]
    assert identifier == "StudentA"

    sources = _process_entry(inner_bytes, "java", tmp_path)
    assert len(sources) == 1
    assert sources[0].name == "Hello.java"

    merged = tmp_path / "merged.txt"
    merge_source_files(sources, tmp_path / "extracted", merged)
    assert "Hello" in merged.read_text()


def test_format_a_c_sources(tmp_path):
    """Format A: C source files detected correctly."""
    inner = _make_inner_zip({"main.c": _C_HELLO})
    repo = _make_repo_format_a({"CStudent": inner})
    entries = _detect_entries(repo)
    sources = _process_entry(entries[0][1], "c", tmp_path)
    assert len(sources) == 1
    assert sources[0].name == "main.c"


# ── Format B: full pipeline ──────────────────────────

def test_format_b_extract_and_merge(tmp_path):
    """Format B: folder/raw.zip extracted, filtered, merged correctly."""
    inner = _make_inner_zip({"Hello.java": _JAVA_HELLO})
    repo = _make_repo_format_b({"StudentA": inner})
    entries = _detect_entries(repo)
    assert len(entries) == 1

    sources = _process_entry(entries[0][1], "java", tmp_path)
    assert len(sources) == 1


# ── Export round-trip (Format B) ─────────────────────

def test_export_format_round_trips():
    """Token Trail export (submissionId/raw.zip + merged/) is importable via Format B."""
    inner = _make_inner_zip({"Main.java": _JAVA_HELLO})
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("abc123def456/raw.zip", inner)
        zf.writestr("abc123def456/merged/merged.txt", "merged content")
    entries = _detect_entries(buf.getvalue())
    assert len(entries) == 1
    assert entries[0][0] == "abc123def456"


# ── Malformed ZIPs ───────────────────────────────────

def test_malformed_outer_zip():
    """Opening garbage as a ZIP raises BadZipFile."""
    with pytest.raises(zipfile.BadZipFile):
        zipfile.ZipFile(io.BytesIO(b"this is not a zip file"))


def test_malformed_inner_zip_in_format_a(tmp_path):
    """Format A: a corrupt inner .zip fails on extract."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("Bad.zip", b"not a real zip")
    entries = _detect_entries(buf.getvalue())
    assert len(entries) == 1

    zip_path = tmp_path / "raw.zip"
    zip_path.write_bytes(entries[0][1])
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    with pytest.raises(zipfile.BadZipFile):
        safe_extract_zip(zip_path, extracted)


def test_malformed_inner_zip_in_format_b(tmp_path):
    """Format B: a corrupt raw.zip fails on extract."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("StudentA/raw.zip", b"corrupted data")
    entries = _detect_entries(buf.getvalue())
    assert len(entries) == 1

    zip_path = tmp_path / "raw.zip"
    zip_path.write_bytes(entries[0][1])
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    with pytest.raises(zipfile.BadZipFile):
        safe_extract_zip(zip_path, extracted)


# ── Wrong language ───────────────────────────────────

def test_wrong_language_format_a(tmp_path):
    """Format A: Python files in a Java assignment yield zero sources."""
    inner = _make_inner_zip({"script.py": _PYTHON_CODE})
    repo = _make_repo_format_a({"PythonStudent": inner})
    entries = _detect_entries(repo)
    sources = _process_entry(entries[0][1], "java", tmp_path)
    assert len(sources) == 0


def test_java_in_c_assignment(tmp_path):
    """Java files submitted to a C assignment yield zero sources."""
    inner = _make_inner_zip({"Hello.java": _JAVA_HELLO})
    repo = _make_repo_format_a({"WrongLang": inner})
    entries = _detect_entries(repo)
    sources = _process_entry(entries[0][1], "c", tmp_path)
    assert len(sources) == 0


# ── Partial failure summary ──────────────────────────

def test_partial_failure_format_a(tmp_path):
    """Format A: 2 valid Java + 1 Python → 2 imported, 1 skipped."""
    java_a = _make_inner_zip({"Hello.java": _JAVA_HELLO})
    java_b = _make_inner_zip({"World.java": _JAVA_WORLD})
    python = _make_inner_zip({"script.py": _PYTHON_CODE})

    repo = _make_repo_format_a({"Alice": java_a, "Bob": java_b, "Charlie": python})
    entries = _detect_entries(repo)
    assert len(entries) == 3

    imported, skipped = [], []
    for i, (name, inner_bytes) in enumerate(sorted(entries)):
        entry_dir = tmp_path / f"entry_{i}"
        entry_dir.mkdir()
        try:
            sources = _process_entry(inner_bytes, "java", entry_dir)
        except zipfile.BadZipFile:
            skipped.append(name)
            continue
        if sources:
            imported.append(name)
        else:
            skipped.append(name)

    assert len(imported) == 2
    assert "Alice" in imported
    assert "Bob" in imported
    assert len(skipped) == 1
    assert "Charlie" in skipped


def test_partial_failure_format_b(tmp_path):
    """Format B: same partial failure logic works with folder/raw.zip."""
    java_a = _make_inner_zip({"Hello.java": _JAVA_HELLO})
    python = _make_inner_zip({"script.py": _PYTHON_CODE})

    repo = _make_repo_format_b({"Good": java_a, "Bad": python})
    entries = _detect_entries(repo)
    assert len(entries) == 2

    imported, skipped = [], []
    for i, (name, inner_bytes) in enumerate(sorted(entries)):
        entry_dir = tmp_path / f"entry_{i}"
        entry_dir.mkdir()
        sources = _process_entry(inner_bytes, "java", entry_dir)
        (imported if sources else skipped).append(name)

    assert imported == ["Good"]
    assert skipped == ["Bad"]


# ── Folder without raw.zip in Format B ───────────────

def test_format_b_folder_without_raw_zip():
    """Format B: folder with files but no raw.zip yields no entry."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("StudentA/notes.txt", "no raw.zip here")
    entries = _detect_entries(buf.getvalue())
    assert len(entries) == 0
