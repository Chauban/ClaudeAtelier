import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

sf = Surface(1000, 1700, scale=2, bg=(244, 240, 230))

# 米色宣紙底
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
lay[..., 0] = (246 - 8 * xx - 4 * yy).astype(np.uint8)
lay[..., 1] = (241 - 7 * xx - 4 * yy).astype(np.uint8)
lay[..., 2] = (231 - 7 * xx - 5 * yy).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# 圓相
enso = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(enso)
cx, cy = 500 * 2, 470 * 2
r_out = 280 * 2
r_in = 235 * 2
d.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], outline=(166, 159, 146, 88), width=10)
d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], outline=(166, 159, 146, 60), width=7)
enso = enso.filter(ImageFilter.GaussianBlur(6))
sf.composite(enso, mode="normal", opacity=0.8)

# 枯山水砂紋
rake = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dr = ImageDraw.Draw(rake)
for j in range(48):
    base_y = 1220 + j * 7
    phase = j * 0.55
    pts = []
    for x in range(60, 941, 8):
        y = base_y + 6 * math.sin((x / 1000) * 2 * math.pi * 1.65 + phase)
        pts.append((x * 2, y * 2))
    dr.line(pts, fill=(174, 166, 150, 160), width=4)
rake = rake.filter(ImageFilter.GaussianBlur(1.0))
sf.composite(rake, mode="normal", opacity=0.85)

# 朱印
seal = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
ds = ImageDraw.Draw(seal)
sx, sy, side = 70, 1580, 34
ds.rounded_rectangle([sx * 2, sy * 2, (sx + side) * 2, (sy + side) * 2], radius=8 * 2, fill=(185, 78, 58, 235))
seal = seal.filter(ImageFilter.GaussianBlur(0.4))
sf.composite(seal, mode="normal", opacity=0.75)

# 文字安全區
sf.frame(70, 80, 860, 1540)

ink_quote = (45, 43, 40)
ink_fact = (60, 57, 52)
ink_meta = (78, 74, 66)

qbox = sf.text(
    80, 185, QUOTE,
    family="cjk-tc",
    size=56,
    fill=ink_quote,
    anchor="lt",
    role="quote",
    max_w=840,
    line_gap=0.75,
    allow_overlap=False
)

fact_y = qbox.bottom + 210
sf.text(
    80, fact_y, FACT,
    family="cjk-tc",
    size=28,
    fill=ink_fact,
    anchor="lt",
    role="body",
    max_w=840,
    line_gap=0.7,
    allow_overlap=False
)

sf.serial(116, 1580, SERIAL, family="cjk-tc", size=19, fill=ink_meta, anchor="lt", role="meta")
sf.datestamp(930, 1580, DATE, family="cjk-tc", size=19, fill=ink_meta, anchor="rt", role="meta")

sf.save(OUT_PATH)
