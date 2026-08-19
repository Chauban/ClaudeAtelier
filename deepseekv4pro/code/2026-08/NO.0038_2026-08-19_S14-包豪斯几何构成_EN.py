from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw

sf = Surface(1000, 1400, scale=2, bg=(245, 240, 228))
sf.frame(70, 60, 870, 1325)

def L(v):
    return int(round(v * 2))

im = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)

def rect(x, y, w, h, fill, outline=None, ow=0):
    x0, y0 = L(x), L(y)
    x1, y1 = L(x + w) - 1, L(y + h) - 1
    kw = {}
    if outline is not None:
        kw["outline"] = outline
        kw["width"] = L(ow)
    d.rectangle([x0, y0, x1, y1], fill=fill, **kw)

# top red band
rect(0, 0, 1000, 60, (208, 40, 32, 255))
rect(0, 60, 1000, 6, (0, 0, 0, 255))

# left black strip
rect(0, 0, 18, 1400, (0, 0, 0, 255))

# right yellow strip
rect(976, 0, 24, 1400, (235, 195, 28, 255))

# bottom blue band
rect(0, 1330, 1000, 70, (25, 70, 160, 255))

# top strip colour blocks
rect(90, 16, 60, 28, (235, 195, 28, 255))
rect(160, 16, 60, 28, (0, 0, 0, 255))
rect(230, 16, 60, 28, (245, 240, 228, 255))

# yellow circle, kept outside the text column
d.ellipse([L(980), L(90), L(1160), L(270)],
          fill=(235, 195, 28, 255), outline=(0, 0, 0, 255), width=L(3))

# blue circle, right margin
d.ellipse([L(960), L(330), L(1040), L(410)],
          fill=(30, 80, 180, 255), outline=(0, 0, 0, 255), width=L(2))

# red square lower left
rect(30, 1120, 70, 70, (205, 42, 36, 255), outline=(0, 0, 0, 255), ow=3)

# yellow triangle lower left
d.polygon([(L(70), L(1060)), (L(160), L(1060)), (L(115), L(1180))],
          fill=(235, 195, 28, 255))

# blue square lower middle-right
rect(840, 900, 60, 60, (30, 80, 180, 255), outline=(0, 0, 0, 255), ow=2)

# diagonal black accent
d.line([L(0), L(1250), L(1000), L(1050)], fill=(0, 0, 0, 255), width=L(8))

# red horizontal accent
d.line([L(250), L(1300), L(850), L(1300)], fill=(208, 40, 32, 255), width=L(6))

# small colour chips on bottom band
rect(390, 1342, 50, 36, (235, 195, 28, 255))
rect(460, 1342, 50, 36, (208, 40, 32, 255))
rect(530, 1342, 50, 36, (0, 0, 0, 255))

sf.composite(im, mode="normal", opacity=1.0)

def split_en_zh(s):
    idx = s.find('（')
    if idx == -1:
        return s.strip(), ''
    return s[:idx].strip(), s[idx:].strip()

quote_en, quote_zh = split_en_zh(QUOTE)

y = 118
box = sf.text(
    70, y, quote_en,
    family="sans", size=34, fill=(10, 10, 10),
    anchor="lt", role="quote", bold=True,
    max_w=860, line_gap=0.45, allow_overlap=False,
)
y = box.bottom + 14

if quote_zh:
    box2 = sf.text(
        70, y, quote_zh,
        family="cjk-sc", size=28, fill=(45, 45, 45),
        anchor="lt", role="body", bold=False,
        max_w=860, line_gap=0.4, allow_overlap=False,
    )
    y = box2.bottom + 56
else:
    y += 56

fact_en, fact_zh = split_en_zh(FACT)

box3 = sf.text(
    70, y, fact_en,
    family="sans", size=29, fill=(10, 10, 10),
    anchor="lt", role="body", bold=False,
    max_w=860, line_gap=0.4, allow_overlap=False,
)
y = box3.bottom + 12

if fact_zh:
    box4 = sf.text(
        70, y, fact_zh,
        family="cjk-sc", size=28, fill=(45, 45, 45),
        anchor="lt", role="body", bold=False,
        max_w=860, line_gap=0.4, allow_overlap=False,
    )

sf.serial(
    70, 1348, SERIAL,
    family="sans", size=18, fill=(255, 255, 255),
    anchor="lt", role="meta", bold=True, allow_overlap=False,
)

sf.datestamp(
    940, 1348, DATE,
    family="sans", size=18, fill=(255, 255, 255),
    anchor="rt", role="meta", bold=False, allow_overlap=False,
)

sf.save(OUT_PATH)
