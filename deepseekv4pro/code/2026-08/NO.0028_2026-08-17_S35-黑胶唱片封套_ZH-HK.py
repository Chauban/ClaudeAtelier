from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from atelier_canvas import Surface

# ---------- 画布 ----------
W_L, H_L = 1000, 1600
sf = Surface(W_L, H_L, scale=2, bg=(13, 13, 15))
sf.frame(70, 70, 860, 1460)

scale = 2
cx = int(500 * scale)
cy = int(610 * scale)
R = int(320 * scale)
r_label = int(150 * scale)
r_hole = int(14 * scale)

# ---------- 背景渐变 ----------
yy = np.linspace(0, 1, sf.H)[:, None].astype(np.float32)
xx = np.linspace(0, 1, sf.W)[None, :].astype(np.float32)

bg = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
r_ch = (15 + 11 * yy + 4 * xx).astype(np.uint8)
g_ch = (15 + 10 * yy + 3 * xx).astype(np.uint8)
b_ch = (18 + 12 * yy + 3 * xx).astype(np.uint8)
bg[..., 0] = r_ch
bg[..., 1] = g_ch
bg[..., 2] = b_ch
bg[..., 3] = 255
sf.composite(bg)

# ---------- 黑胶唱片 ----------
gx = np.arange(sf.W)[None, :]
gy = np.arange(sf.H)[:, None]
dist = np.sqrt((gx - cx) ** 2 + (gy - cy) ** 2)
mask = dist <= R

base = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
fade = np.clip((R - dist) / R, 0, 1)
val = (16 + 11 * fade).astype(np.uint8)
base[..., 0] = (val * 0.72).astype(np.uint8)
base[..., 1] = (val * 0.80).astype(np.uint8)
base[..., 2] = (val * 1.00 + 5).astype(np.uint8)
base[..., 3] = np.where(mask, 255, 0).astype(np.uint8)

disc = Image.fromarray(base, 'RGBA')
d = ImageDraw.Draw(disc)

# 槽纹
for i, r in enumerate(range(int(R - 7 * scale), int(r_label + 18 * scale), -int(6 * scale))):
    shade = 15 + (i % 5) * 3
    d.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        outline=(shade, shade, shade + 2, 255),
        width=2,
    )

# 外缘细弧线
d.arc([cx - R, cy - R, cx + R, cy + R], start=330, end=400, fill=(215, 215, 225, 60), width=4 * scale)
d.arc([cx - R, cy - R, cx + R, cy + R], start=150, end=200, fill=(190, 190, 200, 42), width=3 * scale)

# 中央 label
label_fill = (237, 226, 202, 255)
label_edge = (20, 20, 22, 255)
d.ellipse(
    [cx - r_label, cy - r_label, cx + r_label, cy + r_label],
    fill=label_fill,
    outline=label_edge,
    width=6 * scale,
)
d.ellipse(
    [cx - (r_label - 18 * scale), cy - (r_label - 18 * scale),
     cx + (r_label - 18 * scale), cy + (r_label - 18 * scale)],
    outline=(172, 92, 56, 255),
    width=2 * scale,
)
d.ellipse(
    [cx - (r_label - 40 * scale), cy - (r_label - 40 * scale),
     cx + (r_label - 40 * scale), cy + (r_label - 40 * scale)],
    outline=(48, 48, 50, 255),
    width=1 * scale,
)
d.ellipse(
    [cx - r_hole, cy - r_hole, cx + r_hole, cy + r_hole],
    fill=(15, 15, 17, 255),
)

# 光泽
shimmer = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shimmer)
bbox = [cx - R, cy - R, cx + R, cy + R]
sd.pieslice(bbox, start=-50, end=22, fill=(200, 200, 210, 34))
sd.pieslice(bbox, start=135, end=202, fill=(180, 180, 190, 26))
shimmer = shimmer.filter(ImageFilter.GaussianBlur(38))
disc = Image.alpha_composite(disc, shimmer)

sf.composite(disc)

# ---------- 边框 ----------
border = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
bd = ImageDraw.Draw(border)
bd.rectangle(
    [28 * scale, 28 * scale, (W_L - 28) * scale, (H_L - 28) * scale],
    outline=(95, 86, 76, 130),
    width=2,
)
bd.rectangle(
    [38 * scale, 38 * scale, (W_L - 38) * scale, (H_L - 38) * scale],
    outline=(55, 55, 60, 90),
    width=1,
)
sf.composite(border)

# ---------- 文字 ----------
quote_box = sf.text(
    120, 100, QUOTE,
    family="cjk-hk", size=40, fill=(242, 233, 216),
    anchor="lt", role="quote", bold=True,
    max_w=740, line_gap=0.4,
)

fact_box = sf.text(
    120, 1060, FACT,
    family="cjk-hk", size=28, fill=(226, 220, 204),
    anchor="lt", role="body", bold=False,
    max_w=760, line_gap=0.4,
)

sf.serial(
    500, 562, SERIAL,
    family="mono", size=20, fill=(28, 22, 18),
    anchor="mm", role="meta",
)

sf.datestamp(
    500, 627, DATE,
    family="mono", size=18, fill=(28, 22, 18),
    anchor="mm", role="meta",
)

sf.save(OUT_PATH)
