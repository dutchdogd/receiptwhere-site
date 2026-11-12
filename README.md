# receiptwhere.com

The ReceiptWhere website: marketing pages and blog built with Astro (static output,
no client JavaScript), plus the Terms of Service, Privacy Policy and Delete account
pages, which are carried over byte for byte. Hosted on Cloudflare Pages.

> **Branch `site-astro` (S1a).** Until the S1b cutover, production is still GitHub
> Pages serving the root of `main` as it is. Do not merge this branch into `main`
> before then: CI refuses a PR into `main` that carries `docs/` or the Astro sources
> while `GITHUB_PAGES_SERVES_MAIN` is `true` in `.github/workflows/site.yml`.

| path | content |
|---|---|
| `/` | `src/pages/index.astro` (S1a: the holding page; S2: Home) |
| `/terms/`, `/privacy/` | `public/terms/index.html`, `public/privacy/index.html`: generated, protected |
| `/delete-account/` | `public/delete-account/index.html`: written by hand, protected |
| `/signin/` | `public/signin/index.html`: forwards sign-in links to the API |
| `/.well-known/assetlinks.json` | Android app links, protected |

## Layout

- `src/`: Astro pages, layouts, components, `styles/site.css` (design tokens).
- `public/`: copied into `dist/` unchanged. The protected files live here, plus
  `_headers` (CSP and security headers) and `fonts/` (self-hosted, OFL).
- `source/receiptwhere-terms-privacy.md`: the legal text of record.
- `tools/`: the legal renderer and every check (standard library Python).
- `docs/design/`: the design handoff. Reference only, never built or deployed.
- `protected.sha256`: SHA-256 of each carried-over file as served.

## Protected files

The files in `protected.sha256` must stay byte-identical unless Chat approves an
edit. A commit that changes the manifest names that approval in its message.
`python tools/check_protected.py` checks `public/` and `dist/` against it;
`python tools/check_live.py <url>` checks what a deployment actually serves.

## Changing the legal pages

`source/receiptwhere-terms-privacy.md` is split at its PAGE BREAK comment.

1. Edit the source file.
2. Run `python tools/render_legal.py`. It rewrites `public/terms/index.html` and
   `public/privacy/index.html`.
3. Run `python tools/verbatim_check.py`. It must print `diff: EMPTY` for both pages.
4. Update `protected.sha256` (with the approval named in the commit message).
5. Commit all of them together.

Never edit the generated HTML by hand: the verbatim check would fail.

## Building

```
npm ci
npm run build                 # dist/
python tools/check_protected.py
```

`npm run fonts` re-copies the fonts from the pinned `@fontsource` packages into
`public/fonts/`. `tools/make_icons.py` redraws the favicons (needs Pillow; they are in
the manifest, so redrawing needs approval).

On Windows with Smart App Control, the native bundler binary is blocked. For a
local build only, `npm install --no-save --force @rolldown/binding-wasm32-wasi@<rolldown
version>` (the lockfile does not change). CI builds on Linux.

## CI and deploys (`.github/workflows/site.yml`)

- `checks` (every push and PR): legal pages reproducible, verbatim check, fonts
  reproducible, build, protected-file check.
- `preview` (every branch except `main`): deploy to
  `<branch>.receiptwhere-site.pages.dev`, then fetch it back and check bytes,
  content type, CSP and `X-Robots-Tag: noindex`.
- `production` (`main` only): waits for approval on the `production` environment.

The Cloudflare API token and account ID are GitHub Actions secrets, never in the repo.
No trackers, ads, cookies or analytics.
