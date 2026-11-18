# S1b: DNS migration plan

Status: plan approved by Chat (relayed by Matthijs, 2026-11-17) with option B: the
website switch publishes a pre-launch build; the full site goes live at launch by
flipping the stage flag. No DNS change without Matthijs relaying Chat's OK for that
step.

Source: the Spaceship DNS screen as exported 2026-11-17 (a copy of the screen, not a
zone file), checked against the authoritative servers (launch1.spaceship.net) and
public resolvers. Names and types only here; values are matched locally, never
written down or posted.

## 1. Inventory (Spaceship, 21 records)

Machine-readable copy for `tools/dns_diff.py`: `tools/dns_records.tsv`.

| # | Name | Type | TTL | Purpose | In Cloudflare |
|---|---|---|---|---|---|
| 1-4 | `@` | A ×4 | 1800 | GitHub Pages | copy, DNS-only; replaced at the web switch |
| 5 | `www` | CNAME | 1800 | GitHub Pages | copy, DNS-only; replaced at the web switch |
| 6-7 | `@` | MX ×2 | 300 | Spacemail (receipt@) | copy |
| 8 | `@` | TXT (SPF) | 300 | Spacemail | copy |
| 9 | `@` | TXT | 300 | Google site verification | copy (keeps Search Console) |
| 10 | `spacemail._domainkey` | TXT (DKIM) | 300 | Spacemail | copy, value byte-exact |
| 11 | `_autodiscover._tcp` | SRV | 300 | Spacemail client setup | copy |
| 12 | `_dmarc` | TXT | 1800 | DMARC (apex) | copy |
| 13 | `api` | CNAME | 1800 | Railway (API) | copy, **DNS-only** |
| 14 | `_railway-verify.api` | TXT | 1800 | Railway domain verification | copy |
| 15-16 | `in` | MX ×2 | 1800 | Mailgun inbound (forwarding) | copy |
| 17 | `in` | TXT (SPF) | 300 | Mailgun | copy |
| 18 | `k1._domainkey.in` | TXT (DKIM) | 300 | Mailgun | copy, value byte-exact |
| 19 | `email.in` | CNAME | 300 | Mailgun tracking | copy, **DNS-only** |
| 20 | `_dmarc.in` | TXT | 300 | DMARC (`in`) | copy |
| 21 | `_github-pages-challenge-dutchdogd` | TXT | 1800 | GitHub Pages verification | copy; delete when GitHub Pages is off |

**Every record is DNS-only (grey cloud) in Cloudflare, including `api` and
`email.in`.** Only A, AAAA and CNAME records can be proxied; the diff checks those
for proxying, and the MX/TXT/SRV rows are DNS-only by type. After switch 2 the apex
and `www` become Pages custom domains, which Cloudflare serves through its proxy by
design; every other record stays DNS-only.

Not in the list, as expected: NS and SOA (managed by the provider). No AAAA, no CAA
(so Cloudflare's certificate authorities may issue), no wildcard.

DNSSEC: **on**. Two DS records at the .com parent (TTL 86400), signed zone (AD=true).

### Completeness
- The screen's counts (5 + 16) match the 21 records listed.
- Every record the public lookup found is in the export; the export adds one the
  lookup never queried (`_autodiscover._tcp` SRV), confirmed on launch1 (TTL 300).
- Closed (Matthijs, 2026-11-17): no URL redirect, domain forwarding or email
  forwarding is configured at Spaceship. The 21 records are the complete set to
  migrate.
- The export lost the type and TTL columns for the second group; types and TTLs
  above come from the authoritative server.

### Spacemail on Cloudflare nameservers
Spaceship documents this setup: Spacemail works on a domain whose DNS is hosted
elsewhere, Cloudflare included, once its records are added at that DNS host:
- How to set up Spacemail DNS records on Cloudflare:
  https://www.spaceship.com/knowledgebase/set-up-spacemail-dns-records-cloudflare/
- What DNS records do I need to set up for a third-party domain?:
  https://www.spaceship.com/knowledgebase/spacemail-dns-records-third-party-domain/

The records they list are the ones in rows 6-8, 10 and 11: the two apex MX, the
SPF TXT, the DKIM TXT at `spacemail._domainkey`, and the `_autodiscover._tcp` SRV. The DKIM value comes from the Spaceship account (Advanced
DNS → Inactive records → Spacemail DNS records); it is the same value as the live
record, which the diff checks byte for byte. Their verification TXT applies to
domains registered elsewhere; this domain is registered at Spaceship. After switch
1, Matthijs checks that the Spacemail panel shows the domain's DNS as verified
(Spaceship's "Verify DNS changes" step).

(The pages answer automated clients with HTTP 403; their content was read through
search-engine copies on 2026-11-17. Matthijs can open them in a browser to check.)

## 2. Approach: two separate switches

**Switch 1, nameservers (D0):** move DNS hosting only. The Cloudflare zone holds an
exact copy of all 21 records, all DNS-only, so the answers stay identical whichever
provider a resolver asks. The website still comes from GitHub Pages (`pages-frozen`).

**Switch 2, website (D0 + 4 days):** once every resolver sees Cloudflare, add
receiptwhere.com and www as custom domains of the Pages project. Cloudflare replaces
the apex A records and the www CNAME. Rollback is restoring those 5 records in
Cloudflare (TTL 300), with no nameserver change.

What switch 2 publishes is the **pre-launch build** (`site.stage` = `prelaunch`):
exactly the files live today (holding page, Terms, Privacy, Delete account,
`/signin/`, assetlinks, styles, fonts, icons) plus `_headers` and a plain 404 page,
with Privacy carrying the Cloudflare hosting paragraph (effective date = publish
date). The S2 pages and the blog are not in it. At launch, one commit sets
`site.stage` to `launch` together with the launch Terms and Privacy.

This keeps mail, the API and sign-in links independent of the website switch, and
the website switch independent of the launch.

## 3. Timeline (dates per Chat, 2026-11-17)
- **~Mon 30 Nov (D-3):** Matthijs removes the DS records at Spaceship (registrar),
  following the exact clicks I send beforehand. Wait at least 48 h (DS TTL 86400)
  and confirm resolvers no longer return AD for the zone.
- **~Wed 2 Dec (D-1):**
  - Add the zone to Cloudflare (pending, not active). Delete anything Cloudflare
    auto-imports that is not in the inventory; create the 21 records from the
    export, every one DNS-only.
  - Zone settings before activation, all OFF: **Email Routing** (it would replace
    the MX records), Email Address Obfuscation, Rocket Loader, Web Analytics/RUM,
    Bot Fight Mode, Auto Minify, and any other HTML-rewriting feature. Managed
    robots.txt: OFF as soon as the zone exists (the site ships its own robots.txt;
    `tools/check_live.py` checks its bytes).
  - Lower the Spaceship TTLs of 1800 to 300.
  - `pages-frozen` created, protected, GitHub Pages switched to it, bytes verified
    (see the cutover checklist).
  - Run `tools/dns_diff.py` with Spaceship's and the Cloudflare-assigned servers:
    21/21 match and every record DNS-only, no values printed.
- **~Thu 3 Dec (D0, quiet hour):** on my go, Matthijs switches the nameservers at
  Spaceship to Cloudflare's. Rerun the diff against public resolvers through the
  propagation window (up to 48 h, .com NS TTL 172800). Checks of section 4.
- **~Mon 7 Dec, on Chat's OK:** switch 2 (website) with the pre-launch build and
  the Privacy hosting paragraph in the same production deploy (its effective date =
  that day).
- **After it holds:** re-enable DNSSEC in Cloudflare and add the new DS at Spaceship.
- **7–14 Dec:** the 7-day clean period (cutover checklist).
- **15 Dec:** launch flip (`site.stage` = `launch`, launch Terms and Privacy), on
  Chat's OK. GitHub Pages off and repo private follow the clean period per the
  cutover checklist.

## 4. Checks after each switch (yes/no)
- `tools/dns_diff.py`: 21/21 match, every record DNS-only (after switch 1; after
  switch 2 with `--web-switched`).
- Mail to receipt@ arrives (Spacemail); a Mailgun-sent sign-in email arrives and its
  link opens via /signin/; forwarding to the `in` address reaches Mailgun.
- api.receiptwhere.com reachable over TLS.
- After switch 1: the Spacemail panel shows the DNS as verified.
- After switch 2: `tools/check_live.py https://receiptwhere.com` (protected bytes,
  assetlinks content type, CSP, /signin/, no Set-Cookie, pre-launch file set, 404),
  www → apex redirect.

## 5. Rollback
- Switch 1: nameservers back to Spaceship (its records untouched throughout).
- Switch 2: restore the 4 A records and the www CNAME in Cloudflare.
- Any production deploy that removes paths (e.g. launch → pre-launch): purge the
  domain's cache, then `tools/check_live.py` on the deployment URL and on the
  domain (cutover checklist, standing rule).

## 6. `tools/dns_diff.py`
Standard library only. Reads `tools/dns_records.tsv` (names, types, counts; no
values), queries two given nameservers directly, and prints per record set: match
yes/no, the record count on each side, and whether it is DNS-only. Values are
compared in memory and never printed. Proxy check: a proxied A/CNAME answers with
Cloudflare's own addresses instead of the record, so the tool looks for Cloudflare
address ranges and a missing CNAME at the Cloudflare side. With `--cf-export`, it
also reads Cloudflare's zone export locally for the explicit proxied flag of every
record and lists any record in Cloudflare that is not in the inventory (names and
types only).
