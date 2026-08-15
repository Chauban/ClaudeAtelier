from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw
import math

W, H = 1000, 1800
sf = Surface(W, H, scale=2, bg=(7, 8, 26))

# Background gradient
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
lay[..., 0] = (6 + 2 * xx).astype(np.uint8)
lay[..., 1] = (7 + 8 * yy).astype(np.uint8)
lay[..., 2] = (24 + 28 * yy).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# Pixel art layer
art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(art)
rng = np.random.RandomState(18)

# Pixel stars
star_colors = [(255, 255, 255), (180, 210, 255),
               (255, 240, 190), (140, 220, 255)]
for _ in range(200):
    x = int(rng.randint(0, W - 8))
    y = int(rng.randint(0, 1150))
    s = int(rng.choice([2, 3, 4, 5]))
    c = star_colors[rng.randint(0, len(star_colors) - 1)]
    d.rectangle([x, y, x + s, y + s], fill=c + (255,))

# Pixelated Neptune
cx, cy, pr, block = 500, 320, 152, 8
for py in range(cy - pr, cy + pr + 1, block):
    for px in range(cx - pr, cx + pr + 1, block):
        dx = px + block / 2 - cx
        dy = py + block / 2 - cy
        if dx * dx + dy * dy <= pr * pr:
            band = math.sin((py - cy + pr) / 38 * math.pi)
            if band > 0.55:
                base = (74, 124, 208)
            elif band < -0.55:
                base = (13, 32, 94)
            else:
                base = (26, 55, 136)
            if abs(py - (cy + 34)) < 26 and abs(px - cx) < 60:
                base = (92, 140, 218)
            if abs(py - (cy - 48)) < 18 and abs(px - cx) < 90:
                base = (150, 190, 240)
            if dx > 40 and dy < -50:
                base = tuple(min(255, int(c * 1.45)) for c in base)
            d.rectangle([px, py, px + block - 1, py + block - 1], fill=base + (255,))

# Faint pixel ring
for i in range(60):
    x = cx - 160 + i * 5
    y = cy + 90 + int(20 * math.sin(i / 9))
    d.rectangle([x, y, x + 5, y + 3], fill=(90, 110, 190, 220))

# HUD panels for serial/date
d.rectangle([68, 68, 282, 132], fill=(0, 0, 0, 180))
d.rectangle([68, 68, 282, 132], outline=(120, 210, 255, 255), width=3)
d.rectangle([718, 68, 932, 130], fill=(0, 0, 0, 180))
d.rectangle([718, 68, 932, 130], outline=(120, 210, 255, 255), width=3)

# Game dialog panel
panel_x, panel_y, panel_w, panel_h = 88, 1050, 824, 650
d.rectangle([panel_x + 14, panel_y + 14, panel_x + panel_w + 14, panel_y + panel_h + 14], fill=(0, 0, 0, 180))
d.rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h], fill=(16, 22, 52, 255))
d.rectangle([panel_x - 8, panel_y - 8, panel_x + panel_w + 8, panel_y + panel_h + 8], outline=(150, 195, 255, 255), width=5)
d.rectangle([panel_x + 5, panel_y + 5, panel_x + panel_w - 5, panel_y + panel_h - 5], outline=(70, 120, 225, 255), width=2)

# Blocky corner accents
for cx0, cy0 in [
    (panel_x - 8, panel_y - 8),
    (panel_x + panel_w + 8, panel_y - 8),
    (panel_x - 8, panel_y + panel_h + 8),
    (panel_x + panel_w + 8, panel_y + panel_h + 8),
]:
    d.rectangle([cx0 - 12, cy0 - 12, cx0 + 20, cy0 + 20], outline=(255, 255, 255, 255), width=4)

# Composite pixel art
art = art.resize((sf.W, sf.H), Image.NEAREST)
sf.composite(art, mode="normal", opacity=1.0)

# Text safe area
sf.frame(70, 70, 860, 1660)

# Serial and date in HUD
sf.serial(90, 82, SERIAL, family="mono", size=30, fill=(255, 255, 255),
          anchor="lt", role="meta", bold=True, allow_overlap=False)
sf.datestamp(912, 82, DATE, family="mono", size=27, fill=(255, 244, 180),
             anchor="rt", role="meta", bold=True, allow_overlap=False)

# Main text in dialog window
quote_box = sf.text(130, 1140, QUOTE, family="cjk-sc", size=34,
                     fill=(236, 244, 255), anchor="lt", role="quote",
                     bold=True, max_w=740, line_gap=0.45, allow_overlap=False)

fact_box = sf.text(130, quote_box.bottom + 48, FACT, family="cjk-sc", size=28,
                   fill=(205, 222, 255), anchor="lt", role="body",
                   bold=False, max_w=740, line_gap=0.45, allow_overlap=False)

sf.save(OUT_PATH)
