"""Generate VoidTorrent brand icons (PNG + multi-resolution ICO).

Draws a polished "void" mark: a black rounded tile, a crisp purple
ring + smooth spiral sweeping into a central void dot, with a soft top
gloss. Mirrors assets/logo.svg so the app/installer icon matches the
vector logo used on the website.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

OUT_DIR = Path(__file__).resolve().parent.parent / "assets"

PURPLE = (124, 77, 214, 255)
PURPLE_SOFT = (154, 111, 230, 255)
TILE_TOP = (22, 22, 28, 255)
TILE_BOT = (10, 10, 12, 255)
BORDER = (42, 42, 48, 255)


def _tile(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = max(1, int(size * 0.045))
    d.rounded_rectangle(
        [pad, pad, size - 1 - pad, size - 1 - pad],
        radius=int(size * 0.22),
        fill=(15, 15, 20, 255), outline=BORDER,
    )
    return img


def _ring_and_spiral(size: int) -> Image.Image:
    """Render ring + spiral on a transparent layer at high res, downscale."""
    cx = cy = size / 2
    scale = max(1, size // 16)
    big = size * scale
    tcx = tcy = big / 2

    R = size * 0.30 * scale
    steps = 2600
    pts = []
    # sweeping spiral easing into the centre (no central dot)
    for i in range(steps):
        t = i / steps
        ang = -math.pi / 2 + t * 3.05 * 2 * math.pi
        r = R * (1 - t) ** 1.18
        x = tcx + r * math.cos(ang)
        y = tcy + r * math.sin(ang)
        pts.append((x, y))

    layer = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    lw = max(2, int(0.052 * size * scale))
    # outer ring (nearly full circle)
    ld.arc([tcx - R, tcy - R, tcx + R, tcy + R],
            start=-92, end=268, fill=PURPLE_SOFT, width=lw)
    # spiral (tapers toward centre)
    ld.line(pts, fill=PURPLE, width=lw, joint="curve")
    ld.point(pts[0], fill=PURPLE_SOFT)
    layer = layer.resize((size, size), Image.LANCZOS)
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    return layer


def rounded_tile(size: int) -> Image.Image:
    return _ring_and_spiral(size)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sizes = [16, 32, 48, 64, 128, 256]
    pngs = [rounded_tile(s) for s in sizes]
    big = rounded_tile(512)
    big.save(OUT_DIR / "icon-512.png")

    ico = OUT_DIR / "voidtorrent.ico"
    pngs[0].save(
        ico, sizes=[(s, s) for s in sizes], append_images=pngs[1:],
    )
    print(f"Wrote icons to {OUT_DIR}")
    print(f"  ICO: {ico}")
    print(f"  PNG: {OUT_DIR / 'icon-512.png'}")


if __name__ == "__main__":
    main()
