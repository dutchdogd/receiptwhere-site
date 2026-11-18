# Launch checklist (site)

Release order (Matthijs, 2026-11-17):

1. **Site launch with Android v1.0, ~15–17 December 2026.** The S2 pages (Home,
   Features, Pricing, About) and the blog go public together with the launch Terms
   and Privacy. Production deploys only after Matthijs relays Chat's OK.
2. **Web app release, early January 2027.** The web-app wording and the Sign in link
   switch then, in a separate site release.

## A. Site launch with Android v1.0 (mid-December)
- [ ] Rerun the copy conflict check of every page against the **launch** version of
      the Terms and Privacy; report each line that conflicts (do not change copy
      without a decision).
- [ ] **Verify before launch:** Pricing FAQ "Deleting your account also stops the
      renewal." Keep it only if billing cancels the Google Play subscription on
      account deletion; otherwise remove it (needs Chat's OK on the wording).
- [ ] Launch facts kept from S2 (#1, #5, #8): paid plan and prices, Google Play
      billing, CSV export on the paid plan, 50 / 300 receipts a month: confirm each
      matches the launch Terms and the app.
- [ ] **CSV export vs the API's CSV contract (§7f), as released:** confirm the column
      names and the status wording the site shows (Home "From receipt to record"
      table: date, merchant, total, tax, payment, business/personal, status; status
      values "checked" / "confirmed"; Features "Accounting-ready export"; Pricing
      "Accounting-ready CSV export"). List every mismatch; do not change copy
      without a decision.
- [ ] Home "Coming next" line under the table (QuickBooks and Xero formats, journal
      entries posted for you): still accurate as a "coming next" statement at launch.
- [ ] Business / Personal (v1.0, Features → Organise and use): confirm the app ships
      it as described (one-tap mark, set before scanning, totals and exports split).
- [ ] Google Play: replace "Coming soon to Google Play" with the real Play link.
- [ ] Web app stays "coming": Features "On your computer — coming in January"; no
      Sign in link in the nav.
- [ ] About: founder photo per Matthijs (src/data/about.ts). The co-founder is not
      named publicly anywhere (pages, meta, structured data; CI: tools/check_names.py).
- [ ] No draft posts in the production build (CI: tools/check_drafts.py).
- [ ] S4 SEO basics done (robots.txt, sitemap, 404).
- [ ] S1b cutover done (docs/ops/s1b-cutover-checklist.md).

## B. Web app release (early January)
- [ ] app.receiptwhere.com is live (DNS record exists, TLS OK).
- [ ] Add "Sign in" to the nav, linking to https://app.receiptwhere.com
      (src/layouts/Base.astro; the S2 design's placement).
- [ ] Features "Coming next": move "On your computer" out of "coming" (drop
      "— coming in January"; wording per Chat), and recheck every page for
      web-app wording.
- [ ] Recheck the copy against the Terms and Privacy in force at that date.
