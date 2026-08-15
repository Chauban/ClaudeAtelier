from atelier_canvas import Surface
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ---------- 画布与安全区 ----------
w = 1000
h = 1600
sf = Surface(w, h, scale=2, bg=(4, 7, 20))
sf.frame(64, 56, 872, 1496)

W_actual = int(sf.W)
H_actual = int(sf.H)
SC = W_actual / w

def P(x, y):
    return (int(round(x * SC)), int(round(y * SC)))

# ---------- 文本测量 ----------
panel_x = 74
panel_w = 852
inner_pad_x = 30
text_max_w = panel_w - 2 * inner_pad_x

QUOTE_FONT = "cjk-tc"
QUOTE_SIZE = 46
FACT_FONT = "cjk-tc"
FACT_SIZE = 28

quote_lines = sf.wrap(QUOTE, QUOTE_FONT, QUOTE_SIZE, max_w=text_max_w, bold=True)
quote_line_h = int(QUOTE_SIZE * 1.42)
quote_pad_y = 26
quote_h = len(quote_lines) * quote_line_h + quote_pad_y * 2
quote_y = 72

fact_lines = sf.wrap(FACT, FACT_FONT, FACT_SIZE, max_w=text_max_w, bold=False)
fact_line_h = int(FACT_SIZE * 1.42)
fact_pad_y = 22
fact_h = len(fact_lines) * fact_line_h + fact_pad_y * 2
fact_y = quote_y + quote_h + 26

# ---------- Tier 2：深空渐变 ----------
g = sf.layer()
H_arr, W_arr = g.shape[0], g.shape[1]
yy = np.linspace(0, 1, H_arr)[:, None]
g[..., 0] = np.round(6 - 4 * yy).astype(np.uint8)
g[..., 1] = np.round(10 - 6 * yy).astype(np.uint8)
g[..., 2] = np.round(38 * (1 - yy) + 14 * yy).astype(np.uint8)
g[..., 3] = 255
sf.composite(g, mode="normal", opacity=1.0)

# ---------- Tier 2：星野 ----------
rng = np.random.default_rng(19)
stars = Image.new("RGBA", (W_actual, H_actual), (0, 0, 0, 0))
ds = ImageDraw.Draw(stars)
for _ in range(520):
    x = rng.uniform(18, w - 18)
    y = rng.uniform(12, 1450)
    rr = rng.uniform(0.6, 1.6)
    bri = rng.uniform(110, 255)
    col = (int(bri), int(bri * 0.95), int(min(255, bri * 1.05)), 255)
    x0, y0 = P(x - rr, y - rr)
    x1, y1 = P(x + rr, y + rr)
    if x1 <= x0:
        x1 = x0 + 1
    if y1 <= y0:
        y1 = y0 + 1
    ds.ellipse([x0, y0, x1, y1], fill=col)
sf.composite(stars, mode="screen", opacity=0.75)

# ---------- Tier 2：3D 线框透视网格 + 发光几何体 ----------
grid_img = Image.new("RGBA", (W_actual, H_actual), (0, 0, 0, 0))
dg = ImageDraw.Draw(grid_img)

cyan = (0, 235, 255, 255)
cyan_dim = (0, 150, 190, 255)
magenta = (255, 50, 150, 255)
green = (0, 255, 200, 255)

VP_x = 500
VP_y = 1040
bottom_y = 1580

# 地平线
dg.line([P(20, VP_y), P(980, VP_y)], fill=cyan, width=4)

# 地面径向线
for xb in [60, 130, 200, 280, 360, 430, 500, 570, 650, 730, 810, 890, 950]:
    dg.line([P(xb, bottom_y), P(VP_x, VP_y)], fill=cyan_dim, width=2)

# 上方空间径向线
for xt in [80, 180, 300, 420, 500, 580, 700, 830, 940]:
    dg.line([P(xt, -10), P(VP_x, VP_y)], fill=(20, 110, 150, 255), width=2)

# 地面横向透视网格
D = bottom_y - VP_y
n = 13
for i in range(1, n + 1):
    t = (i / n) ** 1.75
    yl = VP_y + D * t
    dg.line([P(0, yl), P(w, yl)], fill=(0, 160, 200, 255), width=2)

# 天花板横向透视网格
Dup = VP_y + 80
n2 = 8
for i in range(1, n2 + 1):
    t = (i / n2) ** 1.6
    yl = VP_y - Dup * t
    if yl > -20:
        dg.line([P(0, yl), P(w, yl)], fill=(0, 110, 150, 255), width=2)

# 线框球体
cx, cy, r = 260, 850, 178
for lat in (-60, -30, 0, 30, 60):
    yc = cy + r * math.sin(math.radians(lat))
    xr = r * math.cos(math.radians(lat))
    yr = xr * 0.35
    dg.ellipse([P(cx - xr, yc - yr), P(cx + xr, yc + yr)], outline=green, width=2)
for a in range(0, 180, 30):
    xr = abs(r * math.cos(math.radians(a)))
    dg.ellipse([P(cx - xr, cy - r), P(cx + xr, cy + r)], outline=cyan, width=2)

# 线框立方体
x0, y0, s = 710, 730, 180
dx, dy = 64, -64
front = [(x0, y0), (x0 + s, y0), (x0 + s, y0 + s), (x0, y0 + s)]
back = [(x0 + dx, y0 + dy), (x0 + dx + s, y0 + dy), (x0 + dx + s, y0 + dy + s), (x0 + dx, y0 + dy + s)]
dg.polygon([P(*p) for p in front], outline=magenta, width=3)
dg.polygon([P(*p) for p in back], outline=(0, 200, 255, 255), width=3)
for i in range(4):
    dg.line([P(*front[i]), P(*back[i])], fill=(0, 190, 255, 255), width=2)

# 发光叠加
grid_blur = grid_img.filter(ImageFilter.GaussianBlur(7))
sf.composite(grid_blur, mode="screen", opacity=0.50)
sf.composite(grid_img, mode="screen", opacity=0.85)

# ---------- Tier 2：HUD 面板与底栏 ----------
panels = Image.new("RGBA", (W_actual, H_actual), (0, 0, 0, 0))
dp = ImageDraw.Draw(panels)

panel_fill = (5, 12, 30, 255)
panel_border = (0, 210, 255, 255)
accent = (255, 50, 150, 255)

dp.rounded_rectangle([P(panel_x, quote_y), P(panel_x + panel_w, quote_y + quote_h)],
                     radius=18, fill=panel_fill, outline=panel_border, width=3)
dp.rounded_rectangle([P(panel_x, fact_y), P(panel_x + panel_w, fact_y + fact_h)],
                     radius=18, fill=panel_fill, outline=panel_border, width=3)

dp.rectangle([P(panel_x, quote_y + 14), P(panel_x + 5, quote_y + quote_h - 14)], fill=accent)
dp.rectangle([P(panel_x, fact_y + 14), P(panel_x + 5, fact_y + fact_h - 14)], fill=accent)

dp.rounded_rectangle([P(76, 1500), P(340, 1540)], radius=10,
                     fill=(4, 20, 40, 255), outline=(0, 180, 255, 255), width=2)
dp.rounded_rectangle([P(660, 1500), P(924, 1540)], radius=10,
                     fill=(4, 20, 40, 255), outline=(0, 180, 255, 255), width=2)

sf.composite(panels, mode="normal", opacity=1.0)

# ---------- Tier 1：文字 ----------
sf.text(panel_x + inner_pad_x, quote_y + quote_pad_y, QUOTE,
        family=QUOTE_FONT, size=QUOTE_SIZE, fill=(247, 249, 255),
        anchor="lt", role="quote", bold=True, max_w=text_max_w, line_gap=0.42)

sf.text(panel_x + inner_pad_x, fact_y + fact_pad_y, FACT,
        family=FACT_FONT, size=FACT_SIZE, fill=(205, 240, 255),
        anchor="lt", role="body", bold=False, max_w=text_max_w, line_gap=0.42)

sf.serial(96, 1520, SERIAL, family="mono", size=18,
          fill=(120, 235, 255), anchor="lm", role="meta")
sf.datestamp(904, 1520, DATE, family="mono", size=18,
             fill=(120, 235, 255), anchor="rm", role="meta")

# ---------- 保存 ----------
sf.save(OUT_PATH)
