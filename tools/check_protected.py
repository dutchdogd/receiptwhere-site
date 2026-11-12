#!/usr/bin/env python3
"""Protected-file check: the carried-over files are byte-identical to protected.sha256.

protected.sha256 (sha256sum format, paths relative to the site root) holds the
SHA-256 of each file as served today. This checks, for every entry:
  - public/<path>  (the committed file; on Linux CI this is the git blob), and
  - dist/<path>    (the build output Astro copied), when dist/ exists.
It also checks that:
  - dist/ contains nothing from docs/ (no docs/ directory, no *.dc.html, no support.js);
  - the /signin/ inline-script hash in public/_headers matches the script in
    public/signin/index.html, so the CSP cannot silently block the forwarder.

Prints one yes/no line per file and location; exits 1 on any failure.
Changing protected.sha256 needs Chat's approval, named in the commit message.

Standard library only.
"""
from __future__ import annotations

import base64
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "protected.sha256"
PUBLIC, DIST = ROOT / "public", ROOT / "dist"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest() -> list:
    rows = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, rel = line.split(maxsplit=1)
            rows.append((digest, rel.strip()))
    return rows


def signin_script_hash() -> str:
    page = (PUBLIC / "signin" / "index.html").read_text(encoding="utf-8")
    scripts = re.findall(r"<script>(.*?)</script>", page, re.S)
    if len(scripts) != 1:
        raise SystemExit(f"expected one inline script in signin/index.html, found {len(scripts)}")
    digest = hashlib.sha256(scripts[0].encode("utf-8")).digest()
    return "sha256-" + base64.b64encode(digest).decode("ascii")


def main() -> int:
    failed = False
    locations = [("public", PUBLIC)] + ([("dist", DIST)] if DIST.is_dir() else [])
    for digest, rel in manifest():
        for label, base in locations:
            f = base / rel
            ok = f.is_file() and sha256(f) == digest
            failed |= not ok
            print(f"{'yes' if ok else 'NO '}  {label}/{rel}")

    if DIST.is_dir():
        leaks = [p for p in DIST.rglob("*")
                 if p.relative_to(DIST).parts[0] == "docs"
                 or p.name.endswith(".dc.html") or p.name == "support.js"]
        failed |= bool(leaks)
        print(f"{'yes' if not leaks else 'NO '}  dist/ holds nothing from docs/"
              + "".join(f"\n       {p.relative_to(DIST)}" for p in leaks))
        third = [p for p in DIST.rglob("*") if p.suffix in (".html", ".css")
                 and re.search(r"fonts\.(googleapis|gstatic)\.com", p.read_text("utf-8"))]
        failed |= bool(third)
        print(f"{'yes' if not third else 'NO '}  dist/ makes no Google Fonts request"
              + "".join(f"\n       {p.relative_to(DIST)}" for p in third))
    else:
        print("note: dist/ not built; checked public/ only")

    want = signin_script_hash()
    headers = (PUBLIC / "_headers").read_text(encoding="utf-8")
    ok = f"'{want}'" in headers
    failed |= not ok
    print(f"{'yes' if ok else 'NO '}  public/_headers allows the /signin/ script ({want})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
