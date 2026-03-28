"""
Try three canonical serializations on the same Java source (leaf tokens).

Run from this directory with project .venv:
  python try_token.py
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

from early_access_token import Token, tokenize_java

SEP = "\x1e"  # ASCII record separator


def tokens_as_rows(tokens: list[Token]) -> list[tuple[str, str]]:
    return [(t.type, t.text) for t in tokens]


def canon_delim(rows: list[tuple[str, str]]) -> bytes:
    parts = [f"{t}:{n}" for t, n in rows]
    escaped = [p.replace("\\", "\\\\").replace(SEP, "\\x1e") for p in parts]
    return SEP.join(escaped).encode("utf-8")


def canon_json(rows: list[tuple[str, str]]) -> bytes:
    payload = [{"t": t, "n": n} for t, n in rows]
    s = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return s.encode("utf-8")


def _push_u32_be(buf: bytearray, s: str) -> None:
    b = s.encode("utf-8")
    buf += struct.pack(">I", len(b))
    buf += b


def canon_tlv(rows: list[tuple[str, str]]) -> bytes:
    buf = bytearray()
    buf += struct.pack(">I", len(rows))
    for t, n in rows:
        _push_u32_be(buf, t)
        _push_u32_be(buf, n)
    return bytes(buf)


def main() -> None:
    root = Path(__file__).resolve().parent
    java_path = root / "sample.java"
    source = java_path.read_text(encoding="utf-8")
    tokens = tokenize_java(source)
    rows = tokens_as_rows(tokens)

    print(f"Input: {java_path.name} ({len(source.encode('utf-8'))} bytes UTF-8)")
    print(f"Leaf tokens: {len(tokens)}\n")

    b1 = canon_delim(rows)
    b2 = canon_json(rows)
    b3 = canon_tlv(rows)

    print("--- 1) Delimiter + escape (SEP=\\x1e, field \"type:text\") ---")
    print(f"  length: {len(b1)} bytes")
    print(f"  utf-8 preview (first 200 chars):\n  {b1.decode('utf-8', errors='replace')[:200]!r}\n")

    print("--- 2) JSON (compact, list order = token order) ---")
    print(f"  length: {len(b2)} bytes")
    print(f"  utf-8 preview (first 200 chars):\n  {b2.decode('utf-8', errors='replace')[:200]!r}\n")

    print("--- 3) TLV (big-endian u32 lengths, count then pairs) ---")
    print(f"  length: {len(b3)} bytes")
    print(f"  hex preview (first 64 bytes):\n  {b3[:64].hex()}\n")

    print("--- First 6 tokens (type, text) for reference ---")
    for t, n in rows[:12]:
        print(f"  ({t!r}, {n!r})")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    java_path = root / "sample.java"
    source = java_path.read_text(encoding="utf-8")
    tokens = tokenize_java(source)
    print(tokens)
    # main()
