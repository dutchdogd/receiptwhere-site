#!/usr/bin/env python3
"""Render source/receiptwhere-terms-privacy.md into terms/index.html and
privacy/index.html. Run by hand when the source changes; the output is committed.

NOT A BUILD STEP: GitHub Pages serves the committed HTML as it is. This only keeps
the HTML reproducible from the one source of record.

The source is split at its PAGE BREAK comment. The text is copied VERBATIM: only
Markdown syntax becomes HTML (headings, paragraphs, lists, **bold**, *italic*,
tables), and email addresses become mailto links with the same visible text.
tools/verbatim_check.py proves it by comparing the text back to the source.

Standard library only.
"""
from __future__ import annotations

import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "receiptwhere-terms-privacy.md"
BREAK = re.compile(r"^<!--\s*PAGE BREAK.*?-->\s*$", re.M)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def inline(text: str) -> str:
    """Escape, then **bold**, *italic*, and mailto links (visible text unchanged)."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", out)
    out = EMAIL.sub(lambda m: f'<a href="mailto:{m.group(0)}">{m.group(0)}</a>', out)
    return out


def _cells(row: str) -> list:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def to_html(md: str) -> str:
    lines = md.strip("\n").splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
            i += 1
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
            i += 1
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"  <li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>\n" + "\n".join(items) + "\n</ul>")
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            head, body = _cells(rows[0]), [_cells(r) for r in rows[2:]]
            t = ['<div class="table-wrap"><table>', "  <thead><tr>"
                 + "".join(f"<th scope=\"col\">{inline(c)}</th>" for c in head)
                 + "</tr></thead>", "  <tbody>"]
            for r in body:
                t.append("    <tr>" + "".join(f"<td>{inline(c)}</td>" for c in r)
                         + "</tr>")
            t += ["  </tbody>", "</table></div>"]
            out.append("\n".join(t))
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^(#{1,2} |- |\|)", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<header class="site-header">
  <a class="brand" href="/"><img src="/favicon.svg" alt="" width="32" height="32"><span class="wordmark">Receipt<span class="where">Where</span></span></a>
  <nav aria-label="Legal"><a href="/terms/"{terms_current}>Terms</a> <a href="/privacy/"{privacy_current}>Privacy</a></nav>
</header>
<main class="legal">
{body}
</main>
<footer class="site-footer">
  <a href="/terms/">Terms</a> <a href="/privacy/">Privacy</a> <a href="mailto:receipt@receiptwhere.com">receipt@receiptwhere.com</a>
</footer>
</body>
</html>
"""


def page(md: str, which: str) -> str:
    title = md.strip().splitlines()[0].lstrip("# ").strip()
    cur = ' aria-current="page"'
    return PAGE.format(
        title=html.escape(title), body=to_html(md),
        description=html.escape(f"{title}. ReceiptWhere is provided by DuoNex AI LLC."),
        terms_current=cur if which == "terms" else "",
        privacy_current=cur if which == "privacy" else "")


def split_source() -> tuple:
    terms, privacy = BREAK.split(SOURCE.read_text(encoding="utf-8"), maxsplit=1)
    return terms, privacy


def main() -> None:
    terms, privacy = split_source()
    for which, md in (("terms", terms), ("privacy", privacy)):
        d = ROOT / which
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page(md, which), encoding="utf-8", newline="\n")
        print(f"wrote {which}/index.html")


if __name__ == "__main__":
    main()
