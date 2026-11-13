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

## After cutover, in this order (Chat, 2026-11-12)

### 1. Seven-day clean period: GitHub Pages stays available as the DNS rollback
- [ ] **A day or more before cutover, and before any merge of `site-astro` into
      `main`:** create branch `pages-frozen` at the last GitHub Pages commit on `main`.
      Otherwise, once `main` holds the Astro project, GitHub Pages would serve the
      source tree instead of the site, and a DNS rollback would land on it.
- [ ] **Immediately protect `pages-frozen`:** block pushes (restrict who can push to
      nobody / lock branch) and block deletion. It stays protected until GitHub Pages
      is turned off (step 2, day 8+).
- [ ] Switch the GitHub Pages source to `pages-frozen` (root), still a day or more
      before cutover.
- [ ] Confirm with `tools/check_live.py`-style byte checks that receiptwhere.com
      serves identical bytes from `pages-frozen` (protected files, `/`, assetlinks
      content type). Only then may `site-astro` be merged into `main`.
- [ ] Spaceship records stay untouched for the whole period.
- [ ] Daily for 7 days: `tools/check_live.py https://receiptwhere.com` passes; mail
      to receipt@ and a sign-in email still arrive. Any failure: decide on rollback.

### 2. Turn off GitHub Pages (day 8 or later, only after a clean period)
- [ ] Settings → Pages: unpublish; remove the custom domain there.
- [ ] Delete the `_github-pages-challenge-*` TXT record in Cloudflare DNS (if no
      longer needed). Remove the protection on `pages-frozen`, then delete the branch.
- [ ] receiptwhere.com still served by Cloudflare (check_live passes).

### 3. Make the repo private
- [ ] Set `dutchdogd/receiptwhere-site` to private. (This also takes the earlier
      commits that held the co-founder's name out of public view.)

### 4. Verify CI and deploys from the private repo
- [ ] Push a branch: the `preview` job deploys and `tools/check_live.py --preview` passes.
- [ ] A `main` deploy after `production` environment approval succeeds and
      `tools/check_live.py https://receiptwhere.com` passes.
- [ ] The required status check `checks` still reports on PRs into `main`.

## Rollback (during the 7-day period only)
Point the nameservers back to Spaceship. Its records are untouched and still point
the apex and `www` at GitHub Pages, which serves the frozen pre-cutover site from
`pages-frozen`. After GitHub Pages is turned off (step 2), rollback means
redeploying a previous Cloudflare Pages deployment instead.
