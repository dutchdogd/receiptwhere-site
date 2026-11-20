#!/usr/bin/env python3
"""URL check on the build: no preview hostnames, internal URLs root-relative.

For every HTML, XML, CSS and web-manifest file in dist/:
  - no *.pages.dev hostname anywhere in it (a preview URL baked into the site);
and for every HTML page outside the protected files (protected.sha256):
  - href / src / srcset / poster / action values are root-relative ("/..."),
    fragments, mailto:/tel:, or (links only, <a href>) external sites. An absolute
    https://receiptwhere.com URL in a link or an asset is a failure: it must be
    root-relative so previews and production serve the same page;
  - assets (src, srcset, poster, <link href> other than canonical/alternate) are
    never on another host: no third-party requests;
  - the canonical link, og:url, og:image and twitter:image are absolute URLs on
    https://receiptwhere.com/.

Prints one yes/no line per check; exits 1 on any failure. Standard library only.
"""
from __future__ import annotations

import html.parser
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITE = "https://receiptwhere.com/"
PREVIEW_HOST = re.compile(r"[a-z0-9.-]*\.pages\.dev", re.I)
TEXT_SUFFIXES = {".html", ".xml", ".css", ".webmanifest"}


def protected() -> set:
    rows = (ROOT / "protected.sha256").read_text(encoding="utf-8").splitlines()
    return {line.split(maxsplit=1)[1].strip() for line in rows if line.strip()}


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.problems: list = []
        self.canonical = None
        self.meta: dict = {}

    def bad(self, what: str):
        self.problems.append(what)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        rel = (a.get("rel") or "").lower().split()
        if tag == "link" and "canonical" in rel:
            self.canonical = a.get("href")
            return
        if tag == "meta":
            key = a.get("property") or a.get("name")
            if key in ("og:url", "og:image", "twitter:image"):
                self.meta[key] = a.get("content")
            return
        for attr in ("href", "src", "srcset", "poster", "action"):
            value = a.get(attr)
            if value is None:
                continue
            urls = [u.strip().split()[0] for u in value.split(",") if u.strip()] if attr == "srcset" else [value.strip()]
            for url in urls:
                self.check_url(tag, attr, url, rel)

    def check_url(self, tag, attr, url, rel):
        low = url.lower()
        if not url or low.startswith(("#", "mailto:", "tel:")):
            return
        if url.startswith("/") and not url.startswith("//"):
            return
        if low.startswith(("http://", "https://", "//")):
            if low.startswith((SITE, "https://www.receiptwhere.com/")):
                self.bad(f"<{tag} {attr}> absolute site URL, should be root-relative: {url}")
            elif tag == "a" and attr == "href":
                return  # a link to another site
            elif tag == "link" and "alternate" in rel:
                return
            else:
                self.bad(f"<{tag} {attr}> asset on another host: {url}")
            return
        self.bad(f"<{tag} {attr}> relative URL (use a root-relative one): {url}")


def main() -> int:
    failed = False

    def check(ok: bool, what: str, details=()):
        nonlocal failed
        failed |= not ok
        print(f"{'yes' if ok else 'NO '}  {what}" + "".join(f"\n       {d}" for d in details))

    if not DIST.is_dir():
        print("NO   dist/ not built")
        return 1
    files = [p for p in DIST.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES]
    hits = [f"{p.relative_to(DIST).as_posix()}: {m.group(0)}" for p in files
            for m in PREVIEW_HOST.finditer(p.read_text(encoding="utf-8", errors="replace"))]
    check(not hits, f"no *.pages.dev hostname in {len(files)} built HTML/XML/CSS/manifest files", hits)

    skip = protected()
    pages = [p for p in DIST.rglob("*.html") if p.relative_to(DIST).as_posix() not in skip]
    url_problems, head_problems = [], []
    for p in sorted(pages):
        rel = p.relative_to(DIST).as_posix()
        parser = Page()
        parser.feed(p.read_text(encoding="utf-8"))
        url_problems += [f"{rel}: {x}" for x in parser.problems]
        is_404 = rel == "404.html"
        if not is_404 and parser.canonical is not None and not parser.canonical.startswith(SITE):
            head_problems.append(f"{rel}: canonical {parser.canonical}")
        for key, value in parser.meta.items():
            if value is not None and not value.startswith(SITE):
                head_problems.append(f"{rel}: {key} {value}")
    check(not url_problems, f"internal links and assets root-relative, no third-party assets ({len(pages)} pages)",
          url_problems)
    check(not head_problems, "canonical, og:url, og:image, twitter:image on https://receiptwhere.com/",
          head_problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
