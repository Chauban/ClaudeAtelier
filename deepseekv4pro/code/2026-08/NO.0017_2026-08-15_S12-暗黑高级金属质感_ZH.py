import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 1000, 1400
s = 2  # scale

sf = Surface(W, H, scale=2, bg=(16, 16, 20))

# ---------- 背景：暗黑金属渐变 + 拉丝纹理 + 暗角 ----------
lay = sf.layer()
Y, X = np.mgrid[0:sf.H, 0:sf.W]
cx, cy = sf.W / 2, sf.H / 2
dist = np.sqrt(((X - cx) / (sf.W / 2)) ** 2 + ((Y - cy) / (sf.H / 2)) ** 2)
base = 16 + 14 * (1 - np.clip(dist, 0, 1))

rng = np.random.default_rng(17)
row = rng.normal(0, 3.2, (sf.H, 1)).repeat(sf.W, axis=1)
fine = rng.normal(0, 1.4, (sf.H, sf.W))
texture = row + fine

vig_mult = 1 - 0.55 * np.clip(dist, 0, 1)
R = np.clip((base + texture) * vig_mult, 8, 255)
G = np.clip((base + texture * 0.92) * vig_mult, 8, 255)
B = np.clip((base + texture * 1.08) * vig_mult, 8, 255)

lay[..., 0] = R.astype(np.uint8)
lay[..., 1] = G.astype(np.uint8)
lay[..., 2] = B.astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# ---------- 金属装饰 ----------
dec = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dr = ImageDraw.Draw(dec)

# 画面边框细线与金角
dr.line([(70 * s, 60 * s), (70 * s, 1340 * s)], fill=(88, 93, 105, 255), width=2)
dr.line([(930 * s, 60 * s), (930 * s, 1340 * s)], fill=(88, 93, 105, 255), width=2)
dr.line([(70 * s, 60 * s), (128 * s, 60 * s)], fill=(188, 152, 54, 255), width=4)
dr.line([(70 * s, 60 * s), (70 * s, 118 * s)], fill=(188, 152, 54, 255), width=4)
dr.line([(930 * s, 60 * s), (872 * s, 60 * s)], fill=(188, 152, 54, 255), width=4)
dr.line([(930 * s, 60 * s), (930 * s, 118 * s)], fill=(188, 152, 54, 255), width=4)
dr.line([(70 * s, 1340 * s), (128 * s, 1340 * s)], fill=(188, 152, 54, 255), width=4)
dr.line([(70 * s, 1340 * s), (70 * s, 1282 * s)], fill=(188, 152, 54, 255), width=4)
dr.line([(930 * s, 1340 * s), (872 * s, 1340 * s)], fill=(188, 152, 54, 255), width=4)
dr.line([(930 * s, 1340 * s), (930 * s, 1282 * s)], fill=(188, 152, 54, 255), width=4)

# 标题上下细金线
dr.line([(70 * s, 148 * s), (930 * s, 148 * s)], fill=(188, 152, 54, 255), width=2)
dr.polygon([(500 * s, 142 * s), (507 * s, 148 * s), (500 * s, 154 * s), (493 * s, 148 * s)], fill=(188, 152, 54, 255))
dr.line([(70 * s, 1310 * s), (930 * s, 1310 * s)], fill=(188, 152, 54, 255), width=2)
dr.polygon([(500 * s, 1304 * s), (507 * s, 1310 * s), (500 * s, 1316 * s), (493 * s, 1310 * s)], fill=(188, 152, 54, 255))

# 地面阴影
dr.ellipse([250 * s, 892 * s, 720 * s, 930 * s], fill=(0, 0, 0, 120))
dr.ellipse([330 * s, 898 * s, 670 * s, 924 * s], fill=(0, 0, 0, 70))

# 锡罐主体：圆柱形金属渐变
can_cx, top_cy, rx, ry, bottom = 500, 600, 180, 66, 900
x0, x1 = int((can_cx - rx) * s), int((can_cx + rx) * s)
y_mid, y_bot = int(top_cy * s), int(bottom * s)

for px in range(x0, x1 + 1):
    d = (px / s - can_cx) / rx
    val = 58 + 190 * math.exp(-(d ** 2) / 0.16)
    r = max(0, min(255, int(val * 0.90)))
    g = max(0, min(255, int(val * 0.96)))
    b = max(0, min(255, int(val * 1.10)))
    dr.line([(px, y_mid), (px, y_bot)], fill=(r, g, b, 255), width=1)

# 罐顶椭圆罐盖
box = [(can_cx - rx) * s, (top_cy - ry) * s, (can_cx + rx) * s, (top_cy + ry) * s]
dr.ellipse(box, fill=(126, 132, 148, 255), outline=(48, 52, 60, 255), width=5)
inner_rx, inner_ry = rx - 26, ry - 14
box2 = [(can_cx - inner_rx) * s, (top_cy - inner_ry) * s, (can_cx + inner_rx) * s, (top_cy + inner_ry) * s]
dr.ellipse(box2, fill=(24, 26, 31, 255), outline=(86, 92, 106, 255), width=4)
dr.arc([(can_cx - rx + 10) * s, (top_cy - ry + 10) * s, (can_cx + rx - 10) * s, (top_cy + ry - 10) * s],
       start=175, end=290, fill=(212, 218, 232, 255), width=5)

# 罐身封口与接缝
front_edge_y = int((top_cy + ry) * s)
dr.line([(x0, front_edge_y), (x1, front_edge_y)], fill=(205, 210, 224, 255), width=5)
dr.line([(x0, int((top_cy + ry + 10) * s)), (x1, int((top_cy + ry + 10) * s))], fill=(28, 30, 36, 255), width=4)
dr.line([(x0, int((bottom - 8) * s)), (x1, int((bottom - 8) * s))], fill=(32, 34, 41, 255), width=6)
dr.line([(x0, int((bottom - 2) * s)), (x1, int((bottom - 2) * s))], fill=(168, 175, 190, 255), width=4)
dr.line([(int((can_cx + rx - 20) * s), int((top_cy + ry) * s)), (int((can_cx + rx - 20) * s), int((bottom - 8) * s))],
       fill=(42, 46, 56, 255), width=4)

# 锤子：木柄 + 金属锤头
dr.polygon([(280 * s, 910 * s), (302 * s, 910 * s), (316 * s, 598 * s), (296 * s, 592 * s)], fill=(112, 82, 56, 255))
dr.line([(291 * s, 888 * s), (308 * s, 608 * s)], fill=(158, 122, 92, 255), width=5)
dr.rounded_rectangle([240 * s, 552 * s, 350 * s, 600 * s], radius=24, fill=(124, 130, 146, 255),
                     outline=(50, 54, 64, 255), width=4)
dr.line([(248 * s, 562 * s), (342 * s, 562 * s)], fill=(198, 204, 220, 255), width=5)

# 凿子：斜靠在罐右侧
dr.polygon([(655 * s, 535 * s), (678 * s, 553 * s), (716 * s, 900 * s), (692 * s, 912 * s)],
           fill=(116, 123, 138, 255), outline=(52, 56, 66, 255), width=3)
dr.line([(662 * s, 546 * s), (704 * s, 894 * s)], fill=(184, 190, 208, 255), width=4)

# 凿尖火花
dr.line([(648 * s, 520 * s), (628 * s, 498 * s)], fill=(224, 214, 165, 255), width=4)
dr.line([(642 * s, 538 * s), (612 * s, 526 * s)], fill=(200, 190, 150, 255), width=4)
dr.line([(658 * s, 510 * s), (678 * s, 486 * s)], fill=(220, 205, 150, 255), width=3)

sf.composite(dec, mode="normal", opacity=1.0)

# 罐后方柔和泛光
glow = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([(can_cx - 270) * s, (560 - 150) * s, (can_cx + 270) * s, (860 + 160) * s], fill=(140, 140, 165, 80))
glow = glow.filter(ImageFilter.GaussianBlur(80))
sf.composite(glow, mode="screen", opacity=0.5)

# ---------- 文字 ----------
sf.frame(70, 60, 860, 1280)

sf.serial(90, 95, SERIAL, family="sans", size=26, fill=(214, 176, 58), anchor="lt", role="meta", bold=False)
sf.datestamp(930, 95, DATE, family="sans", size=26, fill=(214, 176, 58), anchor="rt", role="meta", bold=False)

# 金句
quote_lines = sf.wrap(QUOTE, "cjk-sc", 46, max_w=840)
qy = 190
for ln in quote_lines:
    box = sf.text(500, qy, ln, family="cjk-sc", size=46, fill=(218, 178, 60),
                  anchor="mt", role="quote", max_w=840)
    qy = box.bottom + 16

# 冷知识
fact_lines = sf.wrap(FACT, "cjk-sc", 28, max_w=840)
fy = 1000
for ln in fact_lines:
    box = sf.text(500, fy, ln, family="cjk-sc", size=28, fill=(198, 202, 214),
                  anchor="mt", role="body", max_w=840)
    fy = box.bottom + 12

sf.save(OUT_PATH)
