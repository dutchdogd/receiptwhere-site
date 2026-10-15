#!/usr/bin/env python3
"""Verbatim check: the text of each published legal page equals its source.

Extracts the visible text of <main> from terms/index.html and privacy/index.html
with the standard library's HTML parser (independent of the renderer), strips the
Markdown syntax from the matching half of source/receiptwhere-terms-privacy.md
(independently, by its own rules), and diffs the two word for word.

Formatting may differ (tags, line breaks, table borders); the words, their order
and their punctuation may not. Prints the diff; exits 1 if it is not empty.

Standard library only.
"""
from __future__ import annotations

import difflib
import html
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "receiptwhere-terms-privacy.md"
BREAK = re.compile(r"^<!--\s*PAGE BREAK.*?-->\s*$", re.M)


class MainText(HTMLParser):
    """Visible text inside <main>, with a break between block elements."""

    BLOCK = {"p", "h1", "h2", "h3", "li", "tr", "td", "th", "ul", "table"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth, self.parts = 0, []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.depth += 1
        elif self.depth and tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "main":
            self.depth -= 1
        elif self.depth and tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)


def html_words(path: pathlib.Path) -> list:
    p = MainText()
    p.feed(path.read_text(encoding="utf-8"))
    # Joined with NOTHING: an inline tag inside a word ("<strong>beta</strong>.")
    # must not split it. Block boundaries already contribute "\n".
    return "".join(p.parts).split()


def md_words(md: str) -> list:
    out = []
    for line in md.splitlines():
        s = line.strip()
        if not s or re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?", s):
            continue                                   # blank, table separator
        s = re.sub(r"^#{1,6}\s+", "", s)               # headings
        s = re.sub(r"^-\s+", "", s)                    # list bullets
        if s.startswith("|"):
            s = " ".join(c.strip() for c in s.strip("|").split("|"))  # table cells
        s = s.replace("**", "")                        # bold
        s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"\1", s)  # italic
        out.extend(html.unescape(s).split())
    return out


def main() -> int:
    terms_md, privacy_md = BREAK.split(SOURCE.read_text(encoding="utf-8"), maxsplit=1)
    failed = False
    for name, md in (("terms", terms_md), ("privacy", privacy_md)):
        src, page = md_words(md), html_words(ROOT / name / "index.html")
        diff = list(difflib.unified_diff(src, page, f"source:{name}", f"{name}/index.html",
                                         lineterm="", n=2))
        print(f"== {name}: {len(src)} words in the source, {len(page)} on the page")
        if diff:
            failed = True
            print("\n".join(diff))
        else:
            print("   diff: EMPTY (identical apart from formatting)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
