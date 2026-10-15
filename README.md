# receiptwhere.com

The ReceiptWhere holding page, Terms of Service and Privacy Policy, served by GitHub
Pages from `main` (root). Plain HTML and CSS, no framework, no build step: Pages
serves the files as they are.

| path | content |
|---|---|
| `/` | `index.html`: the holding page |
| `/terms/` | `terms/index.html`: the Terms of Service |
| `/privacy/` | `privacy/index.html`: the Privacy Policy |

## The legal pages are generated from one source, verbatim

`source/receiptwhere-terms-privacy.md` is the text of record, split at its
PAGE BREAK comment. To change a policy:

1. Edit the source file.
2. Run `python tools/render_legal.py`. It rewrites `terms/index.html` and
   `privacy/index.html`.
3. Run `python tools/verbatim_check.py`. It must print `diff: EMPTY` for both
   pages.
4. Commit all of them together.

Never edit the generated HTML by hand: the verbatim check would fail.

`tools/make_icons.py` redraws `favicon.ico` and `apple-touch-icon.png` (needs
Pillow). `favicon.svg` is the simplified mark, concept A.
