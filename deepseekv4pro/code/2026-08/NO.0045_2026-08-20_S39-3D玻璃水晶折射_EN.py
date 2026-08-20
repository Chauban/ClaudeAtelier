from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1700
sf = Surface(W, H, scale=2, bg=(6, 7, 18))
sf.frame(60, 130, W - 120, H - 260)

S = 2  # actual pixel scale

# ---------- background glow ----------
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None].astype(np.float32)
xx = np.linspace(0, 1, sf.W)[None, :].astype(np.float32)
cx, cy = 0.5, 0.36
dist = np.sqrt(((xx - cx) * 1.2) ** 2 + ((yy - cy) * 1.3) ** 2) / 0.75
glow = np.clip(1 - dist, 0, 1) ** 1.5
lay[..., 0] = (8 + 42 * glow).astype(np.uint8)
lay[..., 1] = (9 + 58 * glow).astype(np.uint8)
lay[..., 2] = (24 + 118 * glow).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# ---------- soft color blobs behind glass ----------
blob = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
bd = ImageDraw.Draw(blob)
bd.ellipse((0, 0, 720 * S, 900 * S), fill=(38, 108, 174, 120))
bd.ellipse((440 * S, 120 * S, 1040 * S, 860 * S), fill=(132, 58, 158, 100))
bd.ellipse((180 * S, 760 * S, 900 * S, 1580 * S), fill=(170, 112, 42, 90))
bd.ellipse((560 * S, 1020 * S, 1100 * S, 1760 * S), fill=(20, 168, 158, 100))
blob = blob.filter(ImageFilter.GaussianBlur(120 * S))
sf.composite(blob, mode="screen", opacity=0.30)

# ---------- bismuth crystal accent ----------
# Placed in the lower area, away from text
cry = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
cd = ImageDraw.Draw(cry)

# main faceted block (logical coords)
top = [(520, 1140), (720, 1070), (800, 1180), (580, 1260)]
left = [(580, 1260), (800, 1180), (785, 1320), (565, 1400)]
right = [(800, 1180), (840, 1230), (815, 1360), (785, 1320)]

top_px = [(x * S, y * S) for x, y in top]
left_px = [(x * S, y * S) for x, y in left]
right_px = [(x * S, y * S) for x, y in right]

cd.polygon(top_px, fill=(188, 224, 242, 210))
cd.polygon(left_px, fill=(82, 138, 168, 200))
cd.polygon(right_px, fill=(50, 80, 112, 210))

# iridescent oxide edges
cd.line(top_px + [top_px[0]], fill=(225, 248, 255, 200), width=3 * S)
cd.line([top_px[0], top_px[1]], fill=(255, 78, 178, 255), width=5 * S)
cd.line([top_px[1], top_px[2]], fill=(80, 220, 255, 255), width=5 * S)
cd.line([top_px[2], top_px[3]], fill=(255, 215, 80, 255), width=5 * S)
cd.line([top_px[3], top_px[0]], fill=(140, 255, 185, 255), width=4 * S)
cd.line([left_px[0], left_px[1]], fill=(205, 232, 255, 180), width=3 * S)

# smaller attached crystal
small = [(560, 1080), (680, 1050), (710, 1110), (590, 1140)]
small_px = [(x * S, y * S) for x, y in small]
cd.polygon(small_px, fill=(142, 202, 170, 210))
cd.line([small_px[0], small_px[1]], fill=(255, 92, 180, 240), width=4 * S)
cd.line([small_px[1], small_px[2]], fill=(80, 220, 255, 240), width=4 * S)
cd.line([small_px[2], small_px[3]], fill=(255, 220, 80, 240), width=4 * S)
cd.line([small_px[3], small_px[0]], fill=(120, 255, 175, 230), width=4 * S)

# faint alpha-decay flash
cd.ellipse((660 * S, 1120 * S, 696 * S, 1156 * S), fill=(255, 255, 255, 215))
cry = cry.filter(ImageFilter.GaussianBlur(4 * S))
sf.composite(cry, mode="normal", opacity=0.92)

# ---------- main glass slab ----------
x0, y0, x1, y1 = 80, 150, 920, 1530

panel = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
pd = ImageDraw.Draw(panel)

# frosted translucent body
pd.rounded_rectangle((x0 * S, y0 * S, x1 * S, y1 * S), radius=36 * S,
                     fill=(15, 18, 32, 215), outline=(112, 142, 182, 255), width=4 * S)

# thick glass bevel
pd.line([(x0 * S + 16 * S, y0 * S + 14 * S), (x1 * S - 16 * S, y0 * S + 14 * S)],
        fill=(204, 232, 255, 255), width=8 * S)
pd.line([(x0 * S + 14 * S, y0 * S + 16 * S), (x0 * S + 14 * S, y1 * S - 16 * S)],
        fill=(172, 210, 248, 230), width=8 * S)
pd.line([(x0 * S + 18 * S, y1 * S - 14 * S), (x1 * S - 18 * S, y1 * S - 14 * S)],
        fill=(18, 22, 42, 255), width=10 * S)
pd.line([(x1 * S - 14 * S, y0 * S + 18 * S), (x1 * S - 14 * S, y1 * S - 18 * S)],
        fill=(18, 22, 42, 255), width=10 * S)

# chromatic dispersion edges
pd.line([(x0 * S + 2 * S, y0 * S + 42 * S), (x0 * S + 2 * S, y1 * S - 42 * S)],
        fill=(255, 60, 180, 255), width=4 * S)
pd.line([(x0 * S + 9 * S, y0 * S + 30 * S), (x0 * S + 9 * S, y1 * S - 30 * S)],
        fill=(70, 215, 255, 255), width=3 * S)
pd.line([(x1 * S - 2 * S, y0 * S + 42 * S), (x1 * S - 2 * S, y1 * S - 42 * S)],
        fill=(255, 215, 80, 255), width=4 * S)

# diagonal reflection wedge
pd.polygon([(x0 * S + 42 * S, y0 * S + 18 * S),
            (x0 * S + 198 * S, y0 * S + 18 * S),
            (x0 * S + 22 * S, y0 * S + 360 * S),
            (x0 * S + 22 * S, y0 * S + 165 * S)],
           fill=(222, 242, 255, 36))

# inner faint glass rings / refraction hints
pd.ellipse((x0 * S + 580 * S, y0 * S + 90 * S, x0 * S + 820 * S, y0 * S + 330 * S),
           outline=(120, 230, 255, 55), width=3 * S)
pd.ellipse((x0 * S + 30 * S, y0 * S + 760 * S, x0 * S + 390 * S, y0 * S + 1140 * S),
           outline=(255, 110, 200, 45), width=3 * S)

panel = panel.filter(ImageFilter.GaussianBlur(1.2 * S))
sf.composite(panel, mode="normal", opacity=1.0)

# ---------- outer chromatic border ----------
edge = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
ed = ImageDraw.Draw(edge)
ed.rounded_rectangle((x0 * S - 7, y0 * S - 7, x1 * S + 7, y1 * S + 7),
                     radius=42 * S, outline=(70, 220, 255, 210), width=4 * S)
ed.rounded_rectangle((x0 * S + 7, y0 * S + 7, x1 * S - 7, y1 * S - 7),
                     radius=34 * S, outline=(255, 62, 182, 170), width=4 * S)
ed.polygon([(x0 * S + 210 * S, y0 * S + 6 * S),
            (x0 * S + 350 * S, y0 * S + 6 * S),
            (x0 * S + 54 * S, y1 * S - 6 * S),
            (x0 * S + 0 * S, y1 * S - 6 * S)],
           fill=(235, 250, 255, 22))
edge = edge.filter(ImageFilter.GaussianBlur(1.5 * S))
sf.composite(edge, mode="screen", opacity=0.8)

# ---------- split bilingual strings ----------
def split_bilingual(text):
    idx = text.find("（")
    if idx == -1:
        return text.strip(), ""
    main = text[:idx].strip()
    trans = text[idx + 1:].strip().rstrip("）").strip()
    return main, trans

quote_en, quote_cn = split_bilingual(QUOTE)
fact_en, fact_cn = split_bilingual(FACT)

# Replace superscript '¹⁹' with '^19' to avoid 
# both missing-glyph errors and accidental "1019" 
fact_cn_display = fact_cn.replace("¹⁹", "^19")

# ---------- text ----------
quote_box = sf.text(
    150, 330,
    quote_en,
    family="sans", size=44, fill=(238, 246, 255),
    anchor="lt", role="quote", bold=True,
    max_w=700, line_gap=0.45,
)

quote_cn_box = sf.text(
    150, quote_box.bottom + 18,
    quote_cn,
    family="cjk-sc", size=26, fill=(186, 216, 242),
    anchor="lt", role="meta",
    max_w=700, line_gap=0.42,
)

# divider made of glass-dispersion strokes
div_y = quote_cn_box.bottom + 40
div = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dd = ImageDraw.Draw(div)
dd.line([(150 * S, div_y * S), (520 * S, div_y * S)], fill=(80, 220, 255, 235), width=4 * S)
dd.line([(515 * S, div_y * S), (848 * S, div_y * S)], fill=(255, 70, 185, 235), width=4 * S)
dd.line([(848 * S, div_y * S), (850 * S, div_y * S + 8 * S)], fill=(255, 218, 80, 235), width=3 * S)
div = div.filter(ImageFilter.GaussianBlur(0.8 * S))
sf.composite(div, mode="normal", opacity=1.0)

fact_box = sf.text(
    150, div_y + 38,
    fact_en,
    family="sans", size=31, fill=(225, 235, 248),
    anchor="lt", role="body",
    max_w=700, line_gap=0.42,
)

# Chinese translation rendered entirely in cjk-sc
fact_cn_box = sf.text(
    150, fact_box.bottom + 24,
    fact_cn_display,
    family="cjk-sc", size=23, fill=(176, 206, 231),
    anchor="lt", role="meta",
    max_w=700, line_gap=0.40,
)

# ---------- serial + date ----------
serial_y = fact_cn_box.bottom + 75
serial_w = sf.measure(SERIAL, "mono", 16, bold=True)[0]

sf.serial(
    150, serial_y,
    SERIAL,
    family="mono", size=16, fill=(172, 206, 241),
    anchor="lt", role="meta", bold=True,
)

sf.datestamp(
    150 + serial_w + 42, serial_y,
    DATE,
    family="mono", size=16, fill=(172, 206, 241),
    anchor="lt", role="meta", bold=True,
)

sf.save(OUT_PATH)
