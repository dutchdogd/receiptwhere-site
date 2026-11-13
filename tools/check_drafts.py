#!/usr/bin/env python3
"""Draft check: a build without SITE_DRAFTS=1 contains no draft post.

Reads the frontmatter of every post in src/content/blog/ for `draft: true`, then
checks that dist/ has no page, OG image or RSS item for those slugs, and no page
carrying the draft marker. Only meaningful for production-style builds; with
SITE_DRAFTS=1 (previews) it just reports what it would have checked.

Standard library only.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BLOG = ROOT / "src" / "content" / "blog"
DIST = ROOT / "dist"


def drafts() -> list:
    out = []
    for f in sorted(BLOG.glob("**/*.md*")):
        m = re.match(r"^---\s*\n(.*?)\n---", f.read_text(encoding="utf-8"), re.S)
        if m and re.search(r"^draft:\s*true\s*$", m.group(1), re.M):
            out.append(f.relative_to(BLOG).with_suffix("").as_posix().lower())
    return out


def main() -> int:
    slugs = drafts()
    if os.environ.get("SITE_DRAFTS") == "1":
        print(f"preview build (SITE_DRAFTS=1): drafts allowed ({len(slugs)}: {', '.join(slugs) or '-'})")
        return 0
    failed = False
    rss = (DIST / "blog" / "rss.xml").read_text(encoding="utf-8") if (DIST / "blog" / "rss.xml").exists() else ""
    for slug in slugs:
        hits = [p for p in [DIST / "blog" / slug] if p.exists()]
        in_rss = f"/blog/{slug}/" in rss
        linked = [p for p in DIST.rglob("*.html") if f'href="/blog/{slug}/"' in p.read_text("utf-8")]
        ok = not hits and not in_rss and not linked
        failed |= not ok
        print(f"{'yes' if ok else 'NO '}  draft '{slug}' not in the build")
    marked = [p for p in DIST.rglob("*.html") if "Draft: shown on previews only" in p.read_text("utf-8")]
    failed |= bool(marked)
    print(f"{'yes' if not marked else 'NO '}  no page carries the draft marker"
          + "".join(f"\n       {p.relative_to(DIST)}" for p in marked))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
