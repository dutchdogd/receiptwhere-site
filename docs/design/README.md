# ReceiptWhere website: design handoff

Source: the "ReceiptWhere website" design canvas (draft layout and copy), exported 2026-11-12.

## What this is
Five reference pages: Home (Main), Features, Pricing, About, Sign in. They are **design references, not production code**:
- `{{accent}}` is a template placeholder: use `#F2A93B`.
- `support.js`, `<x-dc>`, `<helmet>` and the `text/x-dc` script are canvas runtime: drop them.
- Inline styles are canvas convenience: move them into the site's stylesheet as tokens and components.
- Links (`Main.dc.html` etc.) map to `/`, `/features/`, `/pricing/`, `/about/`. "Sign in" goes to `https://app.receiptwhere.com` (the web app), not a site page; SignIn.dc.html only shows the intended look.

## Design tokens
- Navy `#12233D`, footer navy `#0C1A2E`, amber accent `#F2A93B`
- Link `#8A5200` (hover `#5E3800`), body grey `#4A5568`, muted `#C5CEDB`, panel `#F4F6F9`
- Highlight `#FCEBCF`, success bg `#E7F4EC` / text `#1E5B36`, info bg `#E7F1FB` / text `#1F4E79`
- Type: DM Sans (400/500/700) for text, IBM Plex Mono (400/500) for receipt and step labels
- Content width 1160px; side padding `max(16px, 5vw)`; radius 10–18px

## Open items before going public
- Founder photo (About), and Matthijs's OK to name Kalpesh Desai publicly.
- "Get it on Google Play" links: add the Play URL at launch.
- Copy must stay in line with the published Terms and Privacy (e.g. CSV export is paid-plan, v1.0).
