# Launch checklist (site)

Release order (Matthijs, 2026-11-17):

1. **Site launch with Android v1.0, ~15–17 December 2026.** The S2 pages (Home,
   Features, Pricing, About) and the blog go public together with the launch Terms
   and Privacy. Production deploys only after Matthijs relays Chat's OK.
2. **Web app release, early January 2027.** The web-app wording and the Sign in link
   switch then, in a separate site release.

## A. Site launch with Android v1.0 (mid-December)
- [ ] **BLOCKING before the Fri 11 Dec submission: launch Terms published.** Chat
      drafts the §6 paid-plan edits as an edit table (week of 23 Nov); no Terms
      edits on the site until that table arrives. Publication planned **Mon 7 Dec**,
      together with the Cloudflare hosting paragraph (branch `legal-fonts-privacy`),
      in one release with **one effective date** (the publish date) for both Terms
      and Privacy. Through the protected-file process: verbatim check against the
      approved table, `protected.sha256` updated with Chat's approval named in the
      commit, `tools/check_live.py` on receiptwhere.com after deploy.
- [ ] Rerun the copy conflict check of every page against the **launch** version of
      the Terms and Privacy; report each line that conflicts (do not change copy
      without a decision).
- [ ] **Verify before launch:** Pricing FAQ "Deleting your account also stops the
      renewal." Keep it only if billing cancels the Google Play subscription on
      account deletion; otherwise remove it (needs Chat's OK on the wording).
- [ ] Launch facts kept from S2 (#1, #5, #8): paid plan and prices, Google Play
      billing, 50 / 300 receipts a month: confirm each matches the launch Terms and
      the app. **#5, CSV export: paid plan, January (not at launch)** (decision
      2026-11-25): the site says "coming in January" everywhere and the paid card
      lists no export bullet; confirm the launch Terms and the in-app plan
      description don't offer export at launch either.
- [ ] **CSV export vs the API's CSV contract (§7f), as released:** confirm the column
      names and the status wording the site shows (Home "From receipt to record"
      table: date, merchant, total, tax, payment, business/personal, status; status
      values "checked" / "confirmed"; Features "Accounting-ready export"; Pricing
      note "accounting-ready CSV export"). List every mismatch; do not change copy
      without a decision.
- [ ] Home "Coming next" line under the table (QuickBooks and Xero formats, journal
      entries posted for you): still accurate as a "coming next" statement at launch.
- [ ] **Document types vs the release replay:** the five categories the site names
      (Home hero line; Features → Capture → "What it reads"; Home step 1): store
      receipts, online orders, bills (utilities), subscriptions and apps, invoices.
      For each, confirm the release replay has documents of that type reading
      correctly; list any category that doesn't (do not change copy without a
      decision). No bill due dates or reminders anywhere on the site (v1.1).
- [ ] Business / Personal (v1.0, Features → Organise and use): confirm the app ships
      it as described (one-tap mark, set before scanning, totals split).
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

## C. CSV export ships (paid plan, January)
Only once export is live in the app for paid users (wording per Chat):
- [ ] Drop the "coming in January" export wording: Home step 3 ("Find and total";
      "…is coming in January"), Home "From receipt to record" ("From January you
      can export…"), Features "Accounting-ready export — coming in January",
      Pricing note under the paid card ("Coming to the paid plan in January: …").
- [ ] Pricing: put "Accounting-ready CSV export" back as a paid-plan bullet and
      remove the note.
- [ ] Recheck the columns and status wording against the CSV contract (§7f) as
      shipped, and the Terms and Privacy in force at that date.
