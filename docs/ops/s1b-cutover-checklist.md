# S1b cutover checklist (draft, on hold)

Status: ON HOLD until the Spaceship zone export is reviewed and the migration plan
is approved. No DNS change without Matthijs relaying Chat's OK.

## Requirement
Cloudflare Pages serves an apex custom domain only from a full-setup Cloudflare zone
(Cloudflare nameservers): https://developers.cloudflare.com/pages/configuration/custom-domains/

## Before (days ahead)
- [ ] Zone export from Spaceship received; every record listed by name/type/TTL.
- [ ] Zone added to Cloudflare (not yet active); every record copied; diff
      Spaceship vs Cloudflare = empty (names, types, values matched yes/no; key
      values never posted in chat).
- [ ] Mail records DNS-only (grey cloud): apex MX/SPF/DKIM (Spacemail),
      `in` MX/SPF, `k1._domainkey.in`, `email.in`, `_dmarc`, `_dmarc.in`.
- [ ] `api` (Railway) DNS-only; keep `_railway-verify.api`, Google site verification,
      decide on `_github-pages-challenge-*`.
- [ ] TTLs lowered (300 s) at Spaceship at least one old-TTL period ahead.
- [ ] **DNSSEC: remove the DS record at Spaceship ≥ 24 h before the nameserver switch**
      (DS TTL 86400 s); confirm resolvers no longer return AD for the zone.
- [ ] Cloudflare zone settings, before activation:
  - [ ] Email Address Obfuscation: OFF (would rewrite mailto links and inject a script)
  - [ ] Rocket Loader: OFF
  - [ ] Web Analytics / RUM auto-injection: OFF
  - [ ] Bot Fight Mode: OFF (sets a cookie / injects a challenge script)
  - [ ] No other HTML-rewriting feature on (Auto Minify, Mirage, Zaraz, etc.)
- [ ] Privacy edit (branch `legal-fonts-privacy`, b477c9b) ready; effective date set
      to the publish date in a final commit; merged together with the cutover.
- [ ] `GITHUB_PAGES_SERVES_MAIN` set to `false` in the same change that merges
      `site-astro` into `main`; then add `checks` as a required status check.

## Window (quiet hour)
- [ ] Switch nameservers at Spaceship to Cloudflare's.
- [ ] Add `receiptwhere.com` (and `www` → apex redirect) as Pages custom domains.

## Checks after (yes/no each)
- [ ] `python tools/check_live.py https://receiptwhere.com`: protected bytes,
      assetlinks content type, one CSP per page, `/signin/` hash + no-referrer,
      **no Set-Cookie on any page**.
- [ ] No Cloudflare-injected script or rewritten mailto in any page (bytes check covers it).
- [ ] Mail to receipt@receiptwhere.com delivered (Spacemail).
- [ ] A Mailgun-sent sign-in email arrives, and its link opens via /signin/.
- [ ] Forwarding to the `in` address reaches Mailgun.
- [ ] api.receiptwhere.com reachable (TLS OK).
- [ ] www redirects to the apex.
- [ ] Re-enable DNSSEC in Cloudflare; add the new DS at Spaceship.

## Right after cutover: make the repo private (Chat, 2026-11-12)
- [ ] Set `dutchdogd/receiptwhere-site` to private.
      Note: on GitHub Free, a private repo cannot serve GitHub Pages, so this also
      ends the GitHub Pages rollback path. Do it only once the cutover has held, or
      after confirming GitHub Pro (Pages from private repos).
- [ ] Cloudflare deploys still work from the private repo: push a branch, the
      `preview` job deploys and `tools/check_live.py` passes; then a `main` deploy
      after environment approval. (Deploys use the API token from Actions secrets,
      so repo visibility should not matter; this proves it.)
- [ ] Required status check `checks` still reports on PRs.

## Rollback
Point the nameservers back to Spaceship (records there untouched until the switch has
held). GitHub Pages stays configured until a clean period has passed.
