# v1.0 launch checklist (site)

Release rule (Chat, S2): the S2 pages (Home, Features, Pricing, About) and the blog go
public only together with the v1.0 launch Terms and Privacy. Production deploys only
after Matthijs relays Chat's OK.

## Before launch
- [ ] Rerun the copy conflict check of every page against the **launch** version of
      the Terms and Privacy; report each line that conflicts (do not change copy
      without a decision).
- [ ] **Verify before launch:** Pricing FAQ "Deleting your account also stops the
      renewal." Keep it only if billing cancels the Google Play subscription on
      account deletion; otherwise remove it (needs Chat's OK on the wording).
- [ ] Launch facts kept from S2 (#1, #5, #8): paid plan and prices, Google Play
      billing, CSV export on the paid plan, 50 / 300 receipts a month: confirm each
      matches the launch Terms and the app.
- [ ] Google Play: replace "Coming soon to Google Play" with the real Play link.
- [ ] "Sign in" in the nav only once app.receiptwhere.com exists.
- [ ] About: founder photo and co-founder name per Matthijs (src/data/about.ts).
- [ ] No draft posts in the production build (CI: tools/check_drafts.py).
- [ ] S4 SEO basics done (robots.txt, sitemap, 404).
- [ ] S1b cutover done (docs/ops/s1b-cutover-checklist.md).
