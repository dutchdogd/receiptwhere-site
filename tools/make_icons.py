#!/usr/bin/env python3
"""Draw favicon.ico (16/32/48, the simplified mark) and apple-touch-icon.png (180,
the full mark) with Pillow, from the same 100-unit geometry as favicon.svg and the
mark in index.html. Run by hand; the images are committed.
"""
from __future__ import annotations

import pathlib

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAVY, PIN, WHITE = (18, 35, 61, 255), (242, 169, 59, 255), (255, 255, 255, 255)
SS = 8   # supersampling for smooth edges


def mark(px: int, *, lines: bool, rounded: bool) -> Image.Image:
    s = px * SS / 100.0
    img = Image.new("RGBA", (px * SS, px * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle([0, 0, px * SS - 1, px * SS - 1], radius=22 * s, fill=NAVY)
    else:                                   # iOS rounds the corners itself
        d.rectangle([0, 0, px * SS, px * SS], fill=NAVY)
    # the pin: a circle (centre 50,42, r 26) and the point at (50,86)
    d.ellipse([24 * s, 16 * s, 76 * s, 68 * s], fill=PIN)
    d.polygon([(26.5 * s, 52 * s), (73.5 * s, 52 * s), (50 * s, 86 * s)], fill=PIN)
    # the receipt, zigzag bottom edge
    zig = [(39, 27), (61, 27), (61, 53), (57.3, 50.4), (53.7, 53), (50, 50.4),
           (46.3, 53), (42.6, 50.4), (39, 53)]
    d.polygon([(x * s, y * s) for x, y in zig], fill=WHITE)
    if lines:
        for y, w in ((32, 14), (37.5, 14), (43, 9)):
            d.rounded_rectangle([43 * s, y * s, (43 + w) * s, (y + 2.6) * s],
                                radius=1.3 * s, fill=NAVY)
    return img.resize((px, px), Image.LANCZOS)


def main() -> None:
    big = mark(256, lines=False, rounded=True)
    big.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    mark(180, lines=True, rounded=False).convert("RGB").save(ROOT / "apple-touch-icon.png")
    print("wrote favicon.ico, apple-touch-icon.png")


if __name__ == "__main__":
    main()
