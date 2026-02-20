"""ZIP extraction and source-file filtering utilities."""
import zipfile
from pathlib import Path

# Allowed extensions per language
LANGUAGE_EXTENSIONS: dict[str, set[str]] = {
    "java": {".java"},
    "c":    {".c", ".h"},
    "cpp":  {".cpp", ".hpp", ".h"},
}


def safe_extract_zip(zip_path: Path, dest_dir: Path) -> list[str]:
    """Extract a ZIP safely, blocking path-traversal attacks.

    Returns the list of extracted relative paths (strings).
    """
    extracted: list[str] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            name = member.filename
            # Block traversal: reject ".." segments and absolute paths
            if ".." in name or name.startswith("/") or name.startswith("\\"):
                continue
            if member.is_dir():
                continue
            target = dest_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(target, "wb") as dst:
                dst.write(src.read())
            extracted.append(name)
    return extracted


def list_valid_source_files(directory: Path, language: str) -> list[Path]:
    """Return a deterministically sorted list of valid source files.

    Filters by language extensions and skips binary files.
    """
    extensions = LANGUAGE_EXTENSIONS.get(language, set())
    files: list[Path] = []
    for fpath in directory.rglob("*"):
        if fpath.is_file() and fpath.suffix.lower() in extensions:
            if not is_binary_file(fpath):
                files.append(fpath)
    # Sort by POSIX relative path for cross-platform determinism
    return sorted(files, key=lambda p: p.relative_to(directory).as_posix())


def is_binary_file(path: Path) -> bool:
    """Heuristic: a file is binary if the first 8 KB contain a null byte."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except (IOError, OSError):
        return True
