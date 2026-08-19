from atelier_canvas import Surface
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import random

W, H = 1000, 1700
sf = Surface(W, H, scale=2, bg=(38, 43, 48))

# ================= 背景 =================
bg = sf.layer()
yy = np.arange(sf.H)[:, None]
bg[..., 0] = 38
bg[..., 1] = 43
bg[..., 2] = 48
bg[..., 3] = 255
stripe = ((yy // 8) % 11 == 0).astype(np.int16) * 7
bg[..., 0] = np.clip(bg[..., 0].astype(np.int16) + stripe, 0, 255).astype(np.uint8)
bg[..., 1] = np.clip(bg[..., 1].astype(np.int16) + stripe, 0, 255).astype(np.uint8)
bg[..., 2] = np.clip(bg[..., 2].astype(np.int16) + stripe, 0, 255).astype(np.uint8)
rng = np.random.default_rng(7)
noise = rng.integers(-9, 10, (sf.H, sf.W), dtype=np.int16)
bg[..., 0] = np.clip(bg[..., 0].astype(np.int16) + noise, 0, 255).astype(np.uint8)
bg[..., 1] = np.clip(bg[..., 1].astype(np.int16) + noise, 0, 255).astype(np.uint8)
bg[..., 2] = np.clip(bg[..., 2].astype(np.int16) + noise, 0, 255).astype(np.uint8)
sf.composite(bg)

# ================= 票根装饰 =================
deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))

# 阴影
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle([104, 55, 896, 1572], radius=26, fill=(0, 0, 0, 110))
shadow = shadow.filter(ImageFilter.GaussianBlur(9))
deco.alpha_composite(shadow)

d = ImageDraw.Draw(deco)

# 纸体
d.rounded_rectangle([110, 48, 890, 1562], radius=18, fill=(234, 219, 192, 255))

# 顶部装饰带
d.rectangle([110, 48, 890, 222], fill=(126, 59, 44, 255))
d.rectangle([110, 48, 890, 54], fill=(168, 108, 62, 255))
d.rectangle([110, 208, 890, 222], fill=(168, 108, 62, 255))
d.line([125, 136, 875, 136], fill=(201, 157, 82, 120), width=1)
d.polygon([(500, 106), (528, 136), (500, 166), (472, 136)], fill=(207, 162, 84, 255), outline=(240, 220, 180, 255))

# 横向撕票虚线
def dashed_line(d, x0, x1, y, color, dash=16, gap=12, width=2):
    x = x0
    while x < x1:
        d.line([(x, y), (min(x + dash, x1), y)], fill=color, width=width)
        x += dash + gap

dashed_line(d, 132, 870, 575, (96, 60, 34, 255))
dashed_line(d, 132, 870, 1288, (96, 60, 34, 255))

# 做旧斑点
rnd = random.Random(11)
for _ in range(32):
    rx = rnd.randint(150, 850)
    ry = rnd.randint(300, 1540)
    rr = rnd.randint(8, 35)
    aa = rnd.randint(10, 36)
    d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(161, 116, 68, aa))

# 存根区浅色块（撕边）
d.polygon([
    (110, 1293), (135, 1288), (160, 1295), (190, 1288), (220, 1294),
    (255, 1286), (285, 1293), (315, 1287), (350, 1295), (380, 1289),
    (410, 1294), (445, 1287), (480, 1293), (510, 1286), (545, 1294),
    (575, 1288), (605, 1295), (635, 1287), (665, 1293), (695, 1286),
    (725, 1294), (755, 1288), (785, 1295), (815, 1287), (845, 1293),
    (870, 1286), (890, 1293),
    (890, 1500), (110, 1500)
], fill=(242, 228, 203, 255))

# 日期戳圆框
d.ellipse([712, 1348, 828, 1464], outline=(88, 52, 26, 240), width=3)
d.ellipse([718, 1354, 822, 1458], outline=(150, 105, 62, 140), width=1)

# 票号框
d.rectangle([165, 1352, 395, 1432], outline=(88, 52, 26, 220), width=2)
d.line([165, 1392, 395, 1392], fill=(130, 88, 48, 170), width=1)

# 幸运饼干简笔装饰
biscuit_col = (92, 56, 30, 215)
d.ellipse([385, 985, 615, 1145], outline=biscuit_col, width=3)
d.line([393, 1098, 607, 1027], fill=biscuit_col, width=3)
d.line([390, 1063, 362, 1084], fill=biscuit_col, width=3)
d.line([362, 1084, 390, 1108], fill=biscuit_col, width=3)
d.line([610, 1042, 638, 1020], fill=biscuit_col, width=3)
d.line([638, 1020, 610, 1068], fill=biscuit_col, width=3)

# 齿孔排（上、下缘）
def perforations(d, y_center, x0, x1, r, color, spacing=42):
    x = x0 + spacing // 2
    while x <= x1:
        d.ellipse([x - r, y_center - r, x + r, y_center + r], fill=color)
        x += spacing

hole_col = (38, 43, 48, 255)
perforations(d, 48, 124, 878, 16, hole_col)
perforations(d, 1562, 124, 878, 16, hole_col)

# 右缘缺口
d.ellipse([860, 940, 920, 1000], fill=hole_col)

lay = np.array(deco.resize((sf.W, sf.H), Image.LANCZOS))
sf.composite(lay)

# ================= 文字（受控层） =================
sf.frame(140, 270, 720, 1220)

q_box = sf.text(
    500, 300, QUOTE,
    family="cjk-tc", size=44, fill=(47, 30, 18, 255),
    anchor="mt", role="quote", bold=True, line_gap=0.55, max_w=680
)

f_box = sf.text(
    140, q_box.bottom + 82, FACT,
    family="cjk-tc", size=30, fill=(58, 37, 21, 255),
    anchor="lt", role="body", bold=False, line_gap=0.62, max_w=680
)

sf.serial(
    195, 1364, SERIAL,
    family="mono", size=22, fill=(60, 36, 20, 255),
    anchor="lt", role="meta", bold=True
)

sf.datestamp(
    770, 1406, DATE,
    family="mono", size=16, fill=(60, 36, 20, 255),
    anchor="mm", role="meta", bold=True
)

sf.save(OUT_PATH)
