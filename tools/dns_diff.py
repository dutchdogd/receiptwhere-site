#!/usr/bin/env python3
"""DNS diff for the S1b nameserver switch: names, types, yes/no. Never values.

Usage:
  python tools/dns_diff.py --a SERVER --b SERVER [--recursive-a] [--recursive-b]
                           [--zone receiptwhere.com] [--cf-export FILE] [--web-switched]

  --a   the reference side (Spaceship's servers, e.g. launch1.spaceship.net)
  --b   the side under test (the Cloudflare-assigned nameservers, or a public
        resolver with --recursive-b during propagation)

For every row of tools/dns_records.tsv (name, type, count; no values) it queries
both servers directly and prints:
  - match yes/no: the two answer sets are equal (values compared in memory only),
    and each side holds the expected number of records;
  - the record count and TTL on each side;
  - dns-only yes/no, for side B: a proxied A or CNAME answers with Cloudflare's own
    addresses (published ranges, below) directly on the name. MX, TXT and SRV
    records cannot be proxied.
With --web-switched (after switch 2), the rows marked `web` (apex A, www) are now
Pages custom domains, proxied by design: they are listed but not compared.

With --cf-export FILE (Cloudflare's DNS export, BIND format, read locally): for
each row, the number of records in the export and whether any is flagged
cf-proxied:true; and every name/type in the export that is not in the inventory.

Exit status 0 only when every compared row matches and every row is DNS-only.
Standard library only.
"""
from __future__ import annotations

import argparse
import ipaddress
import pathlib
import random
import re
import socket
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORDS = ROOT / "tools" / "dns_records.tsv"

TYPES = {"A": 1, "NS": 2, "CNAME": 5, "SOA": 6, "MX": 15, "TXT": 16, "AAAA": 28, "SRV": 33}
TYPE_NAMES = {v: k for k, v in TYPES.items()}
PROXYABLE = {"A", "AAAA", "CNAME"}

# https://www.cloudflare.com/ips/ (as published 2026-11).
CLOUDFLARE_RANGES = [ipaddress.ip_network(n) for n in [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",
    "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20",
    "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22",
    "2400:cb00::/32", "2606:4700::/32", "2803:f800::/32", "2405:b500::/32",
    "2405:8100::/32", "2a06:98c0::/29", "2c0f:f248::/32",
]]


# ── minimal DNS client ───────────────────────────────────────────────────────

def encode_name(name: str) -> bytes:
    out = b""
    for label in name.rstrip(".").split("."):
        raw = label.encode("ascii")
        if not 0 < len(raw) < 64:
            raise ValueError(f"bad label in {name!r}")
        out += bytes([len(raw)]) + raw
    return out + b"\x00"


def read_name(msg: bytes, off: int):
    labels, end, hops = [], None, 0
    while True:
        length = msg[off]
        if length & 0xC0 == 0xC0:
            if end is None:
                end = off + 2
            off = ((length & 0x3F) << 8) | msg[off + 1]
            hops += 1
            if hops > 64:
                raise ValueError("compression loop")
            continue
        off += 1
        if length == 0:
            break
        labels.append(msg[off:off + length].decode("ascii", "replace").lower())
        off += length
    return ".".join(labels), (end if end is not None else off)


def decode_rdata(msg: bytes, rtype: int, off: int, length: int):
    data = msg[off:off + length]
    if rtype == 1:
        return socket.inet_ntop(socket.AF_INET, data)
    if rtype == 28:
        return socket.inet_ntop(socket.AF_INET6, data)
    if rtype in (2, 5):
        return read_name(msg, off)[0]
    if rtype == 15:
        return (struct.unpack(">H", data[:2])[0], read_name(msg, off + 2)[0])
    if rtype == 16:
        # A TXT record is one or more character-strings; providers split long values
        # differently, so compare the concatenation.
        parts, i = [], 0
        while i < len(data):
            n = data[i]
            parts.append(data[i + 1:i + 1 + n])
            i += 1 + n
        return b"".join(parts)
    if rtype == 33:
        prio, weight, port = struct.unpack(">HHH", data[:6])
        return (prio, weight, port, read_name(msg, off + 6)[0])
    return data


def parse(msg: bytes, qid: int):
    rid, flags, qd, an, _ns, _ar = struct.unpack(">HHHHHH", msg[:12])
    if rid != qid:
        raise ValueError("response id mismatch")
    off = 12
    for _ in range(qd):
        _, off = read_name(msg, off)
        off += 4
    answers = []
    for _ in range(an):
        owner, off = read_name(msg, off)
        rtype, _rclass, ttl, rdlen = struct.unpack(">HHIH", msg[off:off + 10])
        off += 10
        answers.append((owner, rtype, ttl, decode_rdata(msg, rtype, off, rdlen)))
        off += rdlen
    return {"rcode": flags & 0xF, "aa": bool(flags & 0x400), "tc": bool(flags & 0x200),
            "answers": answers}


def query(server_ip: str, name: str, qtype: str, recursive: bool):
    qid = random.randrange(65536)
    header = struct.pack(">HHHHHH", qid, 0x0100 if recursive else 0, 1, 0, 0, 1)
    question = encode_name(name) + struct.pack(">HH", TYPES[qtype], 1)
    opt = b"\x00" + struct.pack(">HHIH", 41, 4096, 0, 0)   # EDNS0, 4096-byte UDP
    packet = header + question + opt
    family = socket.AF_INET6 if ":" in server_ip else socket.AF_INET
    last_error = None
    for _ in range(3):
        try:
            with socket.socket(family, socket.SOCK_DGRAM) as s:
                s.settimeout(4)
                s.sendto(packet, (server_ip, 53))
                result = parse(s.recv(65535), qid)
            if result["tc"]:
                with socket.create_connection((server_ip, 53), timeout=8) as s:
                    s.sendall(struct.pack(">H", len(packet)) + packet)
                    size = struct.unpack(">H", recv_exact(s, 2))[0]
                    result = parse(recv_exact(s, size), qid)
            return result
        except (OSError, ValueError) as e:
            last_error = e
    raise SystemExit(f"no answer from {server_ip} for {name} {qtype}: {last_error}")


def recv_exact(s: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = s.recv(n - len(buf))
        if not chunk:
            raise OSError("connection closed")
        buf += chunk
    return buf


def resolve_server(server: str) -> str:
    try:
        ipaddress.ip_address(server)
        return server
    except ValueError:
        return socket.getaddrinfo(server, 53, socket.AF_INET, socket.SOCK_DGRAM)[0][4][0]


def rrset(server_ip: str, fqdn: str, qtype: str, recursive: bool):
    """Records of exactly this owner and type (CNAME chains are ignored)."""
    result = query(server_ip, fqdn, qtype, recursive)
    rows = [(ttl, value) for owner, rtype, ttl, value in result["answers"]
            if owner == fqdn and TYPE_NAMES.get(rtype) == qtype]
    return {v for _, v in rows}, sorted({t for t, _ in rows}), result["aa"]


def on_cloudflare(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    return any(ip in net for net in CLOUDFLARE_RANGES if net.version == ip.version)


# ── inventory and Cloudflare export ──────────────────────────────────────────

def inventory():
    rows = []
    for line in RECORDS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        rows.append({"name": cols[0], "type": cols[1], "count": int(cols[2]),
                     "web": len(cols) > 3 and cols[3].strip() == "web"})
    return rows


def fqdn(name: str, zone: str) -> str:
    return zone if name == "@" else f"{name}.{zone}"


def read_cf_export(path: pathlib.Path, zone: str):
    """{(relative name, type): [proxied flags]} from a Cloudflare BIND export."""
    found = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith((";", "$")):
            continue
        tokens = line.split()
        if len(tokens) < 4:
            continue
        # name [ttl] [class] type rdata...
        idx = 1
        if idx < len(tokens) and tokens[idx].isdigit():
            idx += 1
        if idx < len(tokens) and tokens[idx].upper() in ("IN", "CH", "HS"):
            idx += 1
        rtype = tokens[idx].upper() if idx < len(tokens) else ""
        if rtype in ("SOA", "NS") or rtype not in TYPES:
            continue
        owner = tokens[0].rstrip(".").lower()
        rel = "@" if owner == zone else owner[: -len(zone) - 1] if owner.endswith("." + zone) else owner
        proxied = bool(re.search(r"cf-proxied:true", line))
        found.setdefault((rel, rtype), []).append(proxied)
    return found


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--a", required=True, help="reference server (Spaceship)")
    ap.add_argument("--b", required=True, help="server under test (Cloudflare or a resolver)")
    ap.add_argument("--recursive-a", action="store_true")
    ap.add_argument("--recursive-b", action="store_true")
    ap.add_argument("--zone", default="receiptwhere.com")
    ap.add_argument("--cf-export", type=pathlib.Path)
    ap.add_argument("--web-switched", action="store_true")
    args = ap.parse_args()
    zone = args.zone.rstrip(".").lower()
    a_ip, b_ip = resolve_server(args.a), resolve_server(args.b)
    rows = inventory()
    total = sum(r["count"] for r in rows)

    print(f"== {zone}: {len(rows)} record sets, {total} records")
    print(f"   A: {args.a} ({'recursive' if args.recursive_a else 'authoritative'})")
    print(f"   B: {args.b} ({'recursive' if args.recursive_b else 'authoritative'})")

    matched = dns_only = compared = 0
    aa_a = aa_b = True
    for row in rows:
        name, rtype, want = row["name"], row["type"], row["count"]
        label = f"{name} {rtype}".ljust(44)
        if args.web_switched and row["web"]:
            print(f"{label} web: Pages custom domain since switch 2 (not compared)")
            continue
        compared += want
        owner = fqdn(name, zone)
        va, ta, aa1 = rrset(a_ip, owner, rtype, args.recursive_a)
        vb, tb, aa2 = rrset(b_ip, owner, rtype, args.recursive_b)
        aa_a &= aa1 or args.recursive_a
        aa_b &= aa2 or args.recursive_b
        ok = va == vb and len(va) == want and len(vb) == want
        matched += want if ok else 0

        if rtype in PROXYABLE:
            direct = set()
            for qt in ("A", "AAAA"):
                direct |= rrset(b_ip, owner, qt, args.recursive_b)[0]
            plain = not any(on_cloudflare(ip) for ip in direct)
        else:
            plain = True
        dns_only += want if plain else 0

        ttl = f"ttl {'/'.join(map(str, ta)) or '-'} | {'/'.join(map(str, tb)) or '-'}"
        print(f"{label} match {'yes' if ok else 'NO '}  count {len(va)}|{len(vb)} (want {want})"
              f"  {ttl.ljust(18)}  dns-only {'yes' if plain else 'NO'}"
              + ("" if rtype in PROXYABLE else " (type is never proxied)"))

    if not aa_a:
        print("note: A did not answer authoritatively for every query")
    if not aa_b:
        print("note: B did not answer authoritatively for every query (zone not on that server yet?)")
    print(f"records matched: {matched}/{compared}")
    print(f"records dns-only: {dns_only}/{compared}")
    failed = matched != compared or dns_only != compared

    if args.cf_export:
        print(f"-- Cloudflare export ({args.cf_export.name}), names and types only")
        found = read_cf_export(args.cf_export, zone)
        for row in rows:
            flags = found.get((row["name"], row["type"]), [])
            if args.web_switched and row["web"]:
                print(f"{row['name']} {row['type']}".ljust(44) + f" in export {len(flags)} (web, not checked)")
                continue
            ok = len(flags) == row["count"] and not any(flags)
            failed |= not ok
            print(f"{row['name']} {row['type']}".ljust(44)
                  + f" in export {len(flags)} (want {row['count']})"
                  + f"  proxied {'NO, all DNS-only' if not any(flags) else 'YES'}  {'yes' if ok else 'NO'}")
        known = {(r["name"], r["type"]) for r in rows}
        web_names = {r["name"] for r in rows if r["web"]} if args.web_switched else set()
        extra = sorted(k for k in found if k not in known and k[0] not in web_names)
        failed |= bool(extra)
        print(f"{'yes' if not extra else 'NO '}  nothing in the export beyond the inventory"
              + "".join(f"\n       extra: {n} {t} x{len(found[(n, t)])}" for n, t in extra))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
