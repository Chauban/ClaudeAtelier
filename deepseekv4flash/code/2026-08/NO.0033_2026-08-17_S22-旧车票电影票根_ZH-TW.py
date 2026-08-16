from atelier_canvas import Surface
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PX = 2
W, H = 1000, 1760
sf = Surface(W, H, scale=PX, bg=(30, 46, 42))

# ---------- Tier 2：背景 ----------
bg = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
rad = np.sqrt(((xx - 0.5) * 1.25) ** 2 + ((yy - 0.5) * 0.9) ** 2)
vig = np.clip(1.0 - 0.30 * rad, 0.42, 1.0)
bg[..., 0] = (34 * vig).astype(np.uint8)
bg[..., 1] = (50 * vig).astype(np.uint8)
bg[..., 2] = (44 * vig).astype(np.uint8)
bg[..., 3] = 255
sf.composite(bg)

# 卡片投影
sh = sf.layer()
sh_img = Image.fromarray(sh)
shd = ImageDraw.Draw(sh_img)
shd.rounded_rectangle([PX * 76, PX * 40, PX * 936, PX * 1740], radius=PX * 16, fill=(0, 0, 0, 120))
sh_img = sh_img.filter(ImageFilter.GaussianBlur(PX * 22))
sf.composite(sh_img)

# ---------- 卡片主体 ----------
x0, x1, y0, y1 = 70, 930, 30, 1730
card = sf.layer()
img = Image.fromarray(card)
d = ImageDraw.Draw(img)


def R(a, b, c, d):
    return [PX * a, PX * b, PX * c, PX * d]


def snowflake(dr, cx, cy, r, fill, width=2):
    cx, cy, r, width = cx * PX, cy * PX, r * PX, width * PX
    for i in range(6):
        a = math.pi / 3 * i - math.pi / 2
        x1 = cx + r * math.cos(a)
        y1 = cy + r * math.sin(a)
        dr.line([(cx, cy), (x1, y1)], fill=fill, width=width)
        for da in (0.62, -0.62):
            bx = x1 + 0.42 * r * math.cos(a + da)
            by = y1 + 0.42 * r * math.sin(a + da)
            dr.line([(x1, y1), (bx, by)], fill=fill, width=width)


# 卡纸底色
d.rounded_rectangle(R(x0, y0, x1, y1), radius=PX * 16, fill=(240, 230, 208, 255))

# 顶部双线
for ly in (52, 58):
    d.line([(PX * 84, PX * ly), (PX * 916, PX * ly)], fill=(150, 110, 75, 110), width=2)

# 副券斜纹
cw, ch = (x1 - x0) * PX, (y1 - 1200) * PX
coupon = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
dc = ImageDraw.Draw(coupon)
for b in range(-cw, ch + 1, 48):
    dc.line([(0, b), (cw, cw + b)], fill=(213, 197, 165, 150), width=2)
img.alpha_composite(coupon, (PX * x0, PX * 1200))

# 日期戳（印章）
d.ellipse(R(102, 67, 278, 243), outline=(150, 55, 40, 220), width=3)
d.ellipse(R(116, 81, 264, 229), outline=(150, 55, 40, 110), width=1)

# 右上角冰晶徽记
snowflake(d, 810, 155, 42, (130, 96, 66, 230), width=2)
d.ellipse(R(758, 103, 862, 207), outline=(130, 96, 66, 120), width=2)

# 金句分隔线
d.line([(PX * 440, PX * 492), (PX * 560, PX * 492)], fill=(150, 110, 75, 180), width=4)
d.ellipse(R(429, 485, 443, 499), fill=(150, 110, 75, 200))
d.ellipse(R(557, 485, 571, 499), fill=(150, 110, 75, 200))

# 底部水印雪花
snowflake(d, 500, 1010, 88, (180, 146, 104, 65), width=1)

# 副券票号框
d.rectangle(R(360, 1445, 640, 1525), outline=(110, 80, 55, 200), width=4)

# 副券底部装饰线
for ly in (1656, 1666, 1676):
    d.line([(PX * 430, PX * ly), (PX * 570, PX * ly)], fill=(150, 110, 75, 170), width=2)

# 右下撕角
d.polygon([(PX * 930, PX * 1670), (PX * 930, PX * 1730), (PX * 870, PX * 1730)], fill=(0, 0, 0, 0))

# 左右锯齿缺口
for cyv in (120, 424, 728, 1032, 1336, 1640):
    d.ellipse(R(70 - 22, cyv - 22, 70 + 22, cyv + 22), fill=(0, 0, 0, 0))
    d.ellipse(R(930 - 22, cyv - 22, 930 + 22, cyv + 22), fill=(0, 0, 0, 0))

# 撕票打孔线
for px in range(96, 905, 28):
    d.ellipse(R(px - 5, 1195, px + 5, 1205), fill=(0, 0, 0, 0))

# 检票孔
for px in (700, 735, 770):
    d.ellipse(R(px - 5.5, 1044.5, px + 5.5, 1055.5), fill=(0, 0, 0, 0))

# 挂票孔
d.ellipse(R(131, 1309, 153, 1331), fill=(0, 0, 0, 0))

sf.composite(img)

# 纸纹颗粒
rng = np.random.default_rng(20260817)
nz = sf.layer()
nv = rng.normal(128, 38, (sf.H, sf.W)).clip(0, 255).astype(np.uint8)
nz[..., 0] = nv
nz[..., 1] = nv
nz[..., 2] = nv
nz[..., 3] = 32
sf.composite(nz)

# 旧渍
stain = sf.layer()
st_img = Image.fromarray(stain)
sd2 = ImageDraw.Draw(st_img)
sd2.ellipse(R(180, 660, 340, 800), fill=(176, 140, 96, 34))
sd2.ellipse(R(700, 390, 850, 560), fill=(158, 118, 78, 28))
sd2.ellipse(R(500, 1400, 680, 1560), fill=(168, 132, 88, 30))
st_img = st_img.filter(ImageFilter.GaussianBlur(PX * 30))
sf.composite(st_img)

# ---------- Tier 1：文字 ----------
sf.frame(100, 60, 800, 1640)

q_head, q_tail = QUOTE.split("；", 1)
q_lines = [q_head + "；", q_tail]
for ln in q_lines:
    assert sf.measure(ln, "serif-cjk", 44)[0] <= 740
b1 = sf.text(500, 295, q_lines[0], family="serif-cjk", size=44, fill=(58, 42, 30), anchor="mt", role="quote", max_w=740)
sf.text(500, b1.bottom + 40, q_lines[1], family="serif-cjk", size=44, fill=(58, 42, 30), anchor="mt", role="quote", max_w=740)

f_lines = sf.wrap(FACT, "cjk-tc", 30, 720)
yf = 540
for ln in f_lines:
    bb = sf.text(500, yf, ln, family="cjk-tc", size=30, fill=(70, 55, 38), anchor="mt", role="body", max_w=720)
    yf = bb.bottom + 10

dw, dh = sf.measure(DATE, "mono", 20)
sf.datestamp(190 - dw / 2, 155 - dh / 2, DATE, family="mono", size=20, fill=(150, 55, 40))

sw, sh = sf.measure(SERIAL, "mono", 40)
sf.serial(500 - sw / 2, 1485 - sh / 2, SERIAL, family="mono", size=40, fill=(62, 45, 28))

sf.save(OUT_PATH)
