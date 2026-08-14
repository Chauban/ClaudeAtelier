from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math
import random

def split_translation(text):
    marker = "（译："
    if marker in text:
        parts = text.split(marker, 1)
        original = parts[0].strip()
        translation = parts[1].rstrip("）").strip()
        return original, translation
    return text, ""

quote_jp, quote_zh = split_translation(QUOTE)
fact_jp, fact_zh = split_translation(FACT)

sf = Surface(960, 1340, scale=2, bg=(228, 214, 184))
W, H = sf.W, sf.H

# ---- aged paper ----
rng = np.random.default_rng(20260815)
base = np.array([228, 214, 184], dtype=np.float32)
noise = rng.normal(0, 4, (H, W, 1)).astype(np.float32)
arr = base[None, None, :] + noise
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cy, cx = (H - 1) / 2, (W - 1) / 2
rr = np.sqrt(((xx - cx) / (W / 2)) ** 2 + ((yy - cy) / (H / 2)) ** 2)
vig = 1.0 - 0.14 * np.clip(rr - 0.55, 0, 1)
arr *= vig[..., None]
arr = np.clip(arr, 0, 255).astype(np.uint8)
alpha = np.full((H, W, 1), 255, np.uint8)
paper = np.concatenate([arr, alpha], axis=2)
sf.composite(paper, mode="normal", opacity=1.0)

# ---- stains ----
stain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(stain)
for blob_cx, blob_cy, r, op in [
    (340, 560, 130, 22),
    (1560, 900, 150, 18),
    (880, 2320, 180, 20),
    (1760, 2100, 100, 16),
    (500, 1900, 110, 18),
]:
    sd.ellipse([blob_cx - r, blob_cy - r, blob_cx + r, blob_cy + r], fill=(110, 82, 46, op))
stain = stain.filter(ImageFilter.GaussianBlur(90))
sf.composite(stain, mode="normal", opacity=0.6)

# ---- ticket decoration ----
deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)
INK = (58, 40, 28, 255)
INK2 = (115, 88, 62, 255)
RED = (150, 42, 42, 255)
PAPER_HOLE = (216, 202, 172, 255)

# stub shading
d.rectangle([88, 72, 540, 2600], fill=(120, 92, 52, 16))

# double frame
d.rectangle([88, 72, 1744, 2600], outline=INK, width=3)
d.rectangle([100, 84, 1732, 2588], outline=INK2, width=1)

# vertical perforation
for py in range(160, 2570, 30):
    d.ellipse([537, py, 543, py + 7], fill=(72, 54, 36, 255))

# punch hole
d.ellipse([240, 300, 320, 380], outline=INK, width=3, fill=PAPER_HOLE)
d.arc([246, 306, 314, 374], 200, 340, fill=(150, 135, 110, 255), width=3)

# date stamp frame
d.rounded_rectangle([1220, 156, 1700, 312], radius=18, outline=RED, width=3)
d.rounded_rectangle([1232, 166, 1688, 302], radius=12, outline=RED, width=1)

# barcode (bars only, no digits)
rand = random.Random(7)
bx0, bx1, by0, by1 = 640, 1780, 2110, 2270
x = bx0
while x < bx1:
    bw = rand.choice([4, 6, 8, 10, 12])
    gap = rand.choice([4, 6, 8])
    if rand.random() > 0.32:
        d.rectangle([x, by0, min(x + bw - 2, bx1), by1], fill=(42, 31, 21, 255))
    x += bw + gap

# horizontal tear perforation
for tx in range(650, 1780, 34):
    d.line([tx, 2290, tx + 14, 2290], fill=(95, 72, 48, 255), width=2)

# abstract red stamp circle, no characters
seal_cx, seal_cy, seal_r = 1540, 2400, 88
d.ellipse([seal_cx - seal_r, seal_cy - seal_r, seal_cx + seal_r, seal_cy + seal_r], outline=RED, width=4)
d.ellipse([seal_cx - seal_r + 14, seal_cy - seal_r + 14, seal_cx + seal_r - 14, seal_cy + seal_r - 14], outline=RED, width=1)
for k in range(10):
    a = k * math.pi / 5 + 0.3
    d.line([
        seal_cx + (seal_r - 34) * math.cos(a),
        seal_cy + (seal_r - 34) * math.sin(a),
        seal_cx + (seal_r - 12) * math.cos(a),
        seal_cy + (seal_r - 12) * math.sin(a),
    ], fill=RED, width=2)

sf.composite(deco, mode="normal", opacity=1.0)

# ---- text layer ----
sf.frame(40, 32, 880, 1268)

serial_box = sf.serial(70, 258, SERIAL, family="mono", size=22, fill=(58, 40, 28), anchor="lt", role="meta")
date_box = sf.datestamp(665, 108, DATE, family="mono", size=20, fill=(150, 42, 42), anchor="lt", role="meta")

# Japanese original quote
q_jp_box = sf.text(310, 340, quote_jp, family="cjk-jp", size=30, fill=(55, 38, 26), anchor="lt", role="quote", max_w=600, line_gap=0.42)

# Chinese translation of quote
if quote_zh:
    q_zh_box = sf.text(310, q_jp_box.bottom + 24, quote_zh, family="cjk-sc", size=20, fill=(92, 72, 50), anchor="lt", role="meta", max_w=600, line_gap=0.35)
else:
    q_zh_box = q_jp_box

# Japanese original fact
f_jp_box = sf.text(310, q_zh_box.bottom + 48, fact_jp, family="cjk-jp", size=28, fill=(55, 38, 26), anchor="lt", role="body", max_w=600, line_gap=0.38)

# Chinese translation of fact
if fact_zh:
    f_zh_box = sf.text(310, f_jp_box.bottom + 24, fact_zh, family="cjk-sc", size=20, fill=(92, 72, 50), anchor="lt", role="meta", max_w=600, line_gap=0.30)

sf.save(OUT_PATH)
