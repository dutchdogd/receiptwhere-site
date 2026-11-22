# Writing a blog post

1. Create `src/content/blog/<slug>.md`. The file name becomes the URL:
   `receiptwhere.com/blog/<slug>/`. Use lowercase words and hyphens.
2. Put the cover image in `src/content/blog/images/<slug>.jpg` (or `.png`).
3. Start the file with:

```md
---
title: "What a receipt has to prove for taxes"
description: "One or two sentences. Shown in search results, social cards and the blog list."
date: 2026-12-15
tags: ["Taxes", "Receipts"]
cover: ./images/<slug>.jpg
coverAlt: "What the image shows, in one sentence, for people who can't see it."
draft: true
---
```

4. Push to a branch: the preview shows the post, including drafts. Set `draft: false`
   (or remove the line) when it is ready to publish.

## The cover image
Every published post needs one; the build stops without it.

- **Size:** at least 1200 × 675 px. Best: 1600 × 1200 px or larger, landscape, with
  the subject in the centre. The site makes the crops itself: 16:9 for the post and
  the blog list, 1200 × 630 for link previews (social media, chat apps), and
  16:9, 4:3 and 1:1 for search engines.
- **Content:** your own photo or illustration, or one you have the rights to.
  Never a real receipt or real customer data: use synthetic examples only.
- **coverAlt:** describe what is in the image, not the post. Example: "A stack of
  paper receipts next to a phone showing a checked total." Up to 200 characters.
- **File:** JPEG for photos, PNG for illustrations. The site converts and resizes it;
  upload the original (up to a few MB).
- **An SVG illustration** (2026-11-21): keep the `.svg` next to the post if the body
  shows it (`![alt](./<slug>.svg)`), and give the cover as a PNG rendered from it at 2x
  (`images/<slug>.png`, at least 1200 × 675 px). When the body opens with that same
  picture, add `coverInBody: true`: the post page then shows it once, from the body;
  lists, link previews and search engines still use the cover.
