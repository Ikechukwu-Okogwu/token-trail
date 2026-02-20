"""Deterministic source-file merging for analysis input."""
from pathlib import Path


def merge_source_files(
    source_files: list[Path],
    base_dir: Path,
    output_path: Path,
) -> None:
    """Merge source files into a single text file with separator headers.

    Files must already be sorted by relative path (see zip_service).
    Each section starts with:  //// FILE: <relativePath>
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as out:
        for i, fpath in enumerate(source_files):
            rel = fpath.relative_to(base_dir).as_posix()
            if i > 0:
                out.write("\n")
            out.write(f"//// FILE: {rel}\n")
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                content = ""
            out.write(content)
            # Ensure every section ends with a newline
            if not content.endswith("\n"):
                out.write("\n")
