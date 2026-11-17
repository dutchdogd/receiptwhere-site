#!/usr/bin/env python3
"""Stage check: dist/ matches site.stage.

site.stage holds "prelaunch" or "launch" (see src/integrations/stage.mjs).

prelaunch: dist/ holds exactly the files live today, nothing more and nothing less:
  the protected files (protected.sha256), public/fonts/*, _headers, and index.html,
  404.html and robots.txt, which equal prelaunch/ byte for byte.
launch: the full site is built (the home page is not the holding page; the S2
  pages, blog and sitemap exist).

Prints yes/no lines; exits 1 on any failure. Standard library only.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PRELAUNCH = ROOT / "prelaunch"
STAGES = ("prelaunch", "launch")
# Files a pre-launch build takes from prelaunch/ (same list as src/integrations/stage.mjs).
PRELAUNCH_OWN = ("index.html", "404.html", "robots.txt")


def stage() -> str:
    value = (ROOT / "site.stage").read_text(encoding="utf-8").strip()
    if value not in STAGES:
        raise SystemExit(f"site.stage must be one of {', '.join(STAGES)}; found {value!r}")
    return value


def prelaunch_files() -> set:
    rows = (ROOT / "protected.sha256").read_text(encoding="utf-8").splitlines()
    files = {line.split(maxsplit=1)[1].strip() for line in rows if line.strip()}
    files |= {f"fonts/{p.name}" for p in (ROOT / "public" / "fonts").iterdir() if p.is_file()}
    return files | {"_headers"} | set(PRELAUNCH_OWN)


def main() -> int:
    failed = False

    def check(ok: bool, what: str):
        nonlocal failed
        failed |= not ok
        print(f"{'yes' if ok else 'NO '}  {what}")

    current = stage()
    print(f"site.stage: {current}")
    if not DIST.is_dir():
        print("NO   dist/ not built")
        return 1
    built = {p.relative_to(DIST).as_posix() for p in DIST.rglob("*") if p.is_file()}
    home = (DIST / "index.html").read_bytes()
    holding = (PRELAUNCH / "index.html").read_bytes()

    if current == "prelaunch":
        want = prelaunch_files()
        extra, missing = sorted(built - want), sorted(want - built)
        check(not extra, f"dist/ holds nothing beyond the pre-launch set ({len(want)} files)"
              + "".join(f"\n       extra: {p}" for p in extra))
        check(not missing, "dist/ holds the whole pre-launch set"
              + "".join(f"\n       missing: {p}" for p in missing))
        check(home == holding, "dist/index.html is the holding page (prelaunch/index.html)")
        for name in PRELAUNCH_OWN[1:]:
            check((DIST / name).is_file()
                  and (DIST / name).read_bytes() == (PRELAUNCH / name).read_bytes(),
                  f"dist/{name} is prelaunch/{name}")
    else:
        check(home != holding, "dist/index.html is the full home page, not the holding page")
        for rel in ["features/index.html", "pricing/index.html", "about/index.html",
                    "blog/index.html", "sitemap.xml", "robots.txt", "404.html"]:
            check(rel in built, f"dist/{rel} built")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
