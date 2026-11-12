#!/usr/bin/env python3
"""Fetch a deployment back and check what it actually serves.

Usage: python tools/check_live.py <base-url> [--preview]

For every entry in protected.sha256: the served bytes equal the manifest
(index.html entries are fetched at their directory URL, as visitors see them).
Also: assetlinks.json is served as application/json; every page checked carries
exactly one CSP (no comma-joined duplicates); / and /terms/ forbid all scripts;
/signin/ allows only its own script hash and sends Referrer-Policy: no-referrer.
With --preview: X-Robots-Tag contains noindex.

Prints the security headers as served; exits 1 on any failure.
Standard library only.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_protected import manifest, signin_script_hash  # noqa: E402

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
    failed = False

    def check(ok: bool, what: str):
        nonlocal failed
        failed |= not ok
        print(f"{'yes' if ok else 'NO '}  {what}")

    print(f"== {base}")
    for digest, rel in manifest():
        path = "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)
        body, headers = fetch(base + path)
        check(hashlib.sha256(body).hexdigest() == digest, f"bytes  {path}")
        if rel == ".well-known/assetlinks.json":
            ctype = headers.get("Content-Type", "")
            check(ctype.split(";")[0].strip() == "application/json",
                  f"content-type {path}: {ctype}")

    want = f"'{signin_script_hash()}'"
    for path in ["/", "/terms/", "/privacy/", "/delete-account/", "/signin/"]:
        _, headers = fetch(base + path)
        print(f"-- {path}")
        for name in SHOW:
            for value in headers.get_all(name) or ["(absent)"]:
                print(f"   {name}: {value}")
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
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
