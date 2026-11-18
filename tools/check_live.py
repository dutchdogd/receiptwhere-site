#!/usr/bin/env python3
"""Fetch a deployment back and check what it actually serves.

Usage: python tools/check_live.py <base-url> [--preview]

For every entry in protected.sha256: the served bytes equal the manifest
(index.html entries are fetched at their directory URL, as visitors see them).
Also: assetlinks.json is served as application/json; every page checked carries
exactly one CSP (no comma-joined duplicates); / and /terms/ forbid all scripts;
/signin/ allows only its own script hash and sends Referrer-Policy: no-referrer.
No page sets a cookie (no Set-Cookie header, e.g. from Bot Fight Mode).
With --preview: X-Robots-Tag contains noindex.
Reports (without failing) whether Cloudflare's NEL / Report-To headers are present.

The rest depends on the stage (site.stage, or --stage=prelaunch|launch to check a
deployment built from another commit). launch: robots.txt, sitemap, manifest,
icons, the styled 404, trailing-slash redirects. prelaunch: / and /robots.txt are
prelaunch/ byte for byte, the full-site paths (S2 pages, blog, sitemap) answer 404,
and a missing page answers 404 with the pre-launch 404 page.

Prints the security headers as served; exits 1 on any failure.
Standard library only.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_protected import manifest, signin_script_hash  # noqa: E402
from check_stage import PRELAUNCH, STAGES, stage  # noqa: E402

SHOW = ["Content-Type", "Content-Security-Policy", "Strict-Transport-Security",
        "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy",
        "X-Frame-Options", "X-Robots-Tag"]
UA = {"User-Agent": "site-deploy-check/1.0"}


def fetch(url: str):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read(), r.headers


def main() -> int:
    base = sys.argv[1].rstrip("/")
    preview = "--preview" in sys.argv[2:]
    current = stage()
    for arg in sys.argv[2:]:
        if arg.startswith("--stage="):
            current = arg.split("=", 1)[1]
            if current not in STAGES:
                raise SystemExit(f"--stage must be one of {', '.join(STAGES)}")
    failed = False

    def check(ok: bool, what: str):
        nonlocal failed
        failed |= not ok
        print(f"{'yes' if ok else 'NO '}  {what}")

    print(f"== {base}  (stage: {current})")
    for digest, rel in manifest():
        path = "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)
        body, headers = fetch(base + path)
        check(hashlib.sha256(body).hexdigest() == digest, f"bytes  {path}")
        if rel == ".well-known/assetlinks.json":
            ctype = headers.get("Content-Type", "")
            check(ctype.split(";")[0].strip() == "application/json",
                  f"content-type {path}: {ctype}")

    want = f"'{signin_script_hash()}'"
    nel_paths = []
    for path in ["/", "/terms/", "/privacy/", "/delete-account/", "/signin/"]:
        _, headers = fetch(base + path)
        if headers.get("NEL") or headers.get("Report-To"):
            nel_paths.append(path)
        print(f"-- {path}")
        for name in SHOW:
            for value in headers.get_all(name) or ["(absent)"]:
                print(f"   {name}: {value}")
        check(not headers.get_all("Set-Cookie"), f"{path} sets no cookie")
        csps = headers.get_all("Content-Security-Policy") or []
        check(len(csps) == 1 and "," not in csps[0], f"{path} one CSP, not merged")
        csp = csps[0] if csps else ""
        if path == "/signin/":
            check(f"script-src {want}" in csp, f"{path} script-src is only its own hash")
            check(headers.get("Referrer-Policy") == "no-referrer", f"{path} Referrer-Policy no-referrer")
        else:
            check("script-src 'none'" in csp, f"{path} script-src 'none'")
        if preview:
            check("noindex" in (headers.get("X-Robots-Tag") or ""), f"{path} X-Robots-Tag noindex")

    # Cloudflare's Network Error Logging headers. Reported, not failed: whether the
    # zone can turn them off is recorded in docs/ops/s1b-dns-plan.md.
    print(f"info NEL / Report-To headers present: {'yes on ' + ' '.join(nel_paths) if nel_paths else 'no'}")

    if current == "prelaunch":
        print("-- pre-launch build")
        body, _ = fetch(base + "/")
        check(body == (PRELAUNCH / "index.html").read_bytes(), "/ is the holding page, byte for byte")
        body, _ = fetch(base + "/robots.txt")
        check(body == (PRELAUNCH / "robots.txt").read_bytes(),
              "/robots.txt is prelaunch/robots.txt (not a Cloudflare-managed one)")
        for path in ["/features/", "/pricing/", "/about/", "/blog/", "/blog/rss.xml",
                     "/sitemap.xml", "/site.webmanifest", "/og/default.png",
                     "/this-page-does-not-exist/"]:
            try:
                fetch(base + path)
                check(False, f"{path} answers 404")
            except urllib.error.HTTPError as e:
                page = e.read()
                check(e.code == 404 and page == (PRELAUNCH / "404.html").read_bytes(),
                      f"{path} answers {e.code} with the pre-launch 404 page")
        return 1 if failed else 0

    # S4: crawl files, manifest, 404, canonical trailing slash.
    print("-- SEO basics")
    body, headers = fetch(base + "/robots.txt")
    text = body.decode("utf-8")
    check("Allow: /" in text and "Sitemap: https://receiptwhere.com/sitemap.xml" in text,
          "/robots.txt allows all and points to the sitemap")
    body, headers = fetch(base + "/sitemap.xml")
    check(body.startswith(b"<?xml") and b"<urlset" in body and b"https://receiptwhere.com/</loc>" in body,
          f"/sitemap.xml served ({headers.get('Content-Type')}), canonical apex URLs")
    _, headers = fetch(base + "/site.webmanifest")
    check("manifest+json" in (headers.get("Content-Type") or "") or "json" in (headers.get("Content-Type") or ""),
          f"/site.webmanifest served ({headers.get('Content-Type')})")
    for icon in ["/icons/icon-192.png", "/icons/icon-512.png", "/favicon.svg", "/favicon.ico", "/apple-touch-icon.png"]:
        _, headers = fetch(base + icon)
        check(True, f"{icon} 200 ({headers.get('Content-Type')})")
    try:
        fetch(base + "/this-page-does-not-exist/")
        check(False, "missing page answers 404")
    except urllib.error.HTTPError as e:
        page = e.read().decode("utf-8", "replace")
        check(e.code == 404 and "isn't in the shoebox" in page, f"missing page answers {e.code} with the styled 404")
    for path in ["/features", "/blog"]:
        with urllib.request.urlopen(urllib.request.Request(base + path, headers=UA), timeout=30) as r:
            check(r.geturl().endswith(path + "/"), f"{path} redirects to {path}/")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
