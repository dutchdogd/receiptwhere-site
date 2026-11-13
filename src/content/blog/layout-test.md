---
title: "Layout test: what a receipt has to prove"
description: "A placeholder post with synthetic content, to check the blog layout. It is a draft and is never published."
date: 2026-11-12
author: "Matthijs van Leeuwen"
tags: ["Layout test", "Receipts"]
draft: true
---

This is a **placeholder post** with synthetic content. It exists only to exercise the blog layout on previews: headings, paragraphs, lists, a table, a quote and a code block. The first real post comes later.

## What a receipt shows

A typical store receipt, like the synthetic one below, carries a handful of details that matter for records:

- the store name and location
- the date and time of the purchase
- the items, a subtotal, the tax and the total
- how it was paid, with only the last four digits of a card

| Line | Amount |
|---|---|
| Wood screws | 8.97 |
| Paint roller | 12.49 |
| Drop cloth | 6.99 |
| **Subtotal** | **28.45** |
| Tax | 2.96 |
| **Total** | **31.41** |

## Checking the numbers

The total should equal the subtotal plus the tax, and the card payment should equal the total. In this example: 28.45 + 2.96 = 31.41, and the card paid 31.41.

> A receipt is evidence when its numbers agree with each other. When they don't, the honest answer is to ask.

### A longer list, numbered

1. Capture the receipt.
2. Read the details.
3. Check them against each other.
4. Ask when something doesn't add up.

Inline code such as `31.41` and a block:

```
SUBTOTAL   28.45
TAX         2.96
TOTAL      31.41
VISA ••4242 31.41
```

That's the end of the layout test. [Back to the blog](/blog/).
