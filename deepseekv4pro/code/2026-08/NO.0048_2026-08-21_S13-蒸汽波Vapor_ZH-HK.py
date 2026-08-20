from atelier_canvas import Surface
from PIL import Image, ImageDraw
import numpy as np

SC = 2

# ---------- 画布 ----------
W = 1000
H = 1700
sf = Surface(W, H, scale=2, bg=(18, 8, 30))
sf.frame(0, 0, W, H)

# ---------- 排版参数 ----------
quote_family = "cjk-hk"
fact_family = "cjk-hk"
meta_family = "mono"

quote_size = 42
fact_size = 32
meta_size = 20

window_x = 90
window_w = 820
window_y = 300
title_h = 56
window_bottom = H - 70

content_top = window_y + title_h

content_x = 120
content_w = 760
pad_top = 34
quote_gap = 80

# ---------- 背景渐变 ----------
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]

c1 = np.array([25, 8, 40], dtype=float)
c2 = np.array([120, 30, 100], dtype=float)
c3 = np.array([15, 15, 50], dtype=float)

t1 = np.clip(yy / 0.5, 0, 1)
top_mid = c1 * (1 - t1) + c2 * t1

t2 = np.clip((yy - 0.5) / 0.5, 0, 1)
mid_bot = c2 * (1 - t2) + c3 * t2

color = np.where(yy < 0.5, top_mid, mid_bot).astype(np.uint8)
lay[..., :3] = color[:, None, :]
lay[..., 3] = 255
sf.composite(lay)

# ---------- 落日太阳 ----------
sun = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
ds = ImageDraw.Draw(sun)

cx, cy, r = 500, 230, 170
ds.pieslice([(cx - r) * SC, (cy - r) * SC, (cx + r) * SC, (cy + r) * SC],
            180, 360, fill=(255, 120, 180, 255))

for line_y in [180, 200, 220, 240]:
    ds.line([(cx - r) * SC, line_y * SC, (cx + r) * SC, line_y * SC],
            fill=(85, 20, 80, 190), width=6 * SC)

sf.composite(sun, mode="normal", opacity=0.95)

# ---------- 棕榈树剪影 ----------
palm = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dp = ImageDraw.Draw(palm)

palm_color = (38, 14, 48, 255)
palm_x, palm_y = 230, 310
palm_x2, palm_y2 = 770, 305

for offset in range(-55, 56, 18):
    box = [(palm_x + offset - 70) * SC, (palm_y - 110) * SC,
           (palm_x + offset + 70) * SC, (palm_y + 45) * SC]
    dp.arc(box, start=190, end=310, fill=palm_color, width=11 * SC)

    box = [(palm_x2 + offset - 70) * SC, (palm_y2 - 110) * SC,
           (palm_x2 + offset + 70) * SC, (palm_y2 + 45) * SC]
    dp.arc(box, start=190, end=310, fill=palm_color, width=11 * SC)

dp.line([palm_x * SC, (palm_y - 90) * SC, (palm_x - 24) * SC, (palm_y + 80) * SC],
        fill=palm_color, width=22 * SC)
dp.line([palm_x2 * SC, (palm_y2 - 90) * SC, (palm_x2 + 24) * SC, (palm_y2 + 80) * SC],
        fill=palm_color, width=22 * SC)

sf.composite(palm, mode="normal", opacity=0.92)

# ---------- 透视网格 ----------
grid = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dg = ImageDraw.Draw(grid)

horizon = 900
bottom = H

y_line = horizon
spacing = 20
while y_line < bottom:
    alpha = 180 if y_line < window_bottom else 220
    dg.line([0, y_line * SC, W * SC, y_line * SC],
            fill=(0, 255, 240, alpha), width=2 * SC)
    y_line += spacing
    spacing *= 1.35

for ix in range(-4, 5):
    top_x = 500 + ix * 30
    bottom_x = 500 + ix * 280
    dg.line([top_x * SC, horizon * SC, bottom_x * SC, bottom * SC],
            fill=(255, 0, 180, 160), width=3 * SC)

sf.composite(grid, mode="normal", opacity=0.75)

# ---------- CRT 扫描线 ----------
scan = sf.layer()
scan[..., 0:3] = 0
scan[..., 3] = 0
scan[::4, :, 3] = 45
sf.composite(scan, mode="normal", opacity=0.08)

# ---------- 复古窗口 ----------
win = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dw = ImageDraw.Draw(win)

border_color = (0, 255, 240, 255)

# 外框发光
dw.rectangle([(window_x - 8) * SC, (window_y - 8) * SC,
              (window_x + window_w + 8) * SC, (window_bottom + 8) * SC],
             fill=border_color, width=4 * SC)

# 窗口主体
dw.rectangle([window_x * SC, window_y * SC,
              (window_x + window_w) * SC, window_bottom * SC],
             fill=(30, 15, 50, 255))

# 标题栏
dw.rectangle([window_x * SC, window_y * SC,
              (window_x + window_w) * SC, (window_y + title_h) * SC],
             fill=(255, 110, 180, 255))

# 三个小圆点
dot_y = (window_y + title_h // 2) * SC
for i, c in enumerate([(255, 85, 85), (255, 225, 85), (85, 255, 185)]):
    dot_x = (window_x + 24 + i * 26) * SC
    dw.ellipse([dot_x - 7 * SC, dot_y - 7 * SC, dot_x + 7 * SC, dot_y + 7 * SC],
               fill=c, outline=(0, 0, 0, 120), width=2 * SC)

# 内容区背景
dw.rectangle([window_x * SC, (window_y + title_h) * SC,
              (window_x + window_w) * SC, window_bottom * SC],
             fill=(25, 12, 40, 245))

# 窗口外框描边
dw.rectangle([window_x * SC, window_y * SC,
              (window_x + window_w) * SC, window_bottom * SC],
             outline=(0, 255, 240, 255), width=4 * SC)

sf.composite(win, mode="normal", opacity=0.98)

# ---------- 文字 ----------
quote_fill = (0, 240, 220)
fact_fill = (235, 230, 255)
meta_fill = (28, 12, 38)

# 金句
quote_box = sf.text(
    content_x, content_top + pad_top,
    QUOTE,
    family=quote_family, size=quote_size, fill=quote_fill,
    anchor="lt", role="quote", bold=True,
    max_w=content_w, line_gap=0.45
)

# 冷知识
fact_box = sf.text(
    content_x, quote_box.bottom + quote_gap,
    FACT,
    family=fact_family, size=fact_size, fill=fact_fill,
    anchor="lt", role="body", bold=False,
    max_w=content_w, line_gap=0.46
)

# 流水号与日期，放在标题栏内，避免与正文重叠
title_cy = window_y + title_h // 2

sf.serial(
    window_x + 190, title_cy,
    SERIAL,
    family=meta_family, size=meta_size, fill=meta_fill,
    anchor="lm", role="meta"
)

sf.datestamp(
    window_x + window_w - 20, title_cy,
    DATE,
    family=meta_family, size=meta_size, fill=meta_fill,
    anchor="rm", role="meta"
)

# ---------- 保存 ----------
sf.save(OUT_PATH)
