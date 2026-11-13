#!/usr/bin/env python3
"""Names check: words that must never appear in the repo or the site.

The words themselves are not stored here (that would publish them); only their
SHA-256 (lowercase). Every word in every tracked text file, and in dist/ when it
exists, is hashed and compared. Prints the file and line of any hit, never the word.
Added on Chat's decision 2026-11-12: the co-founder is not named publicly.

Standard library only.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BLOCKED = {
    "8570b9d31b72a8e1a240eacf0106d538811a33cee0a625f6b0cef82c98c18a9c",
    "63169bea6d7131f931f20d95efdee58635581d400ae651c7750ae434a0af4a5e",
}
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def files() -> list:
    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    out = [ROOT / p for p in tracked.decode("utf-8").split("\0") if p]
    dist = ROOT / "dist"
    if dist.is_dir():
        out += [p for p in dist.rglob("*") if p.is_file()]
    return out


def main() -> int:
    hits, scanned = [], 0
    for f in files():
        try:
            text = f.read_bytes().decode("utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue  # binary (images, fonts) or deleted in the working tree
        scanned += 1
        for n, line in enumerate(text.splitlines(), 1):
            for w in WORD.findall(line.lower()):
                if hashlib.sha256(w.encode("utf-8")).hexdigest() in BLOCKED:
                    hits.append(f"{f.relative_to(ROOT)}:{n}")
                    break
    if hits:
        print("NO   a blocked name appears in:\n     " + "\n     ".join(hits))
        return 1
    print(f"yes  no blocked name in {scanned} text files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
