import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 1000, 1400
PAPER = (239, 230, 210, 255)
INK = (46, 35, 26, 255)
INK_SOFT = (46, 35, 26, 160)

sf = Surface(W, H, scale=2, bg=PAPER)
sf.frame(50, 40, 900, 1300)

def L(v):
    return int(round(v * 2))

# ---------- 正文折行测量 ----------
body_size = 32
line_h = 52
col_x1, col_x2, col_w = 70, 530, 410
body_y0 = 920
lines = sf.wrap(FACT, "serif-cjk", body_size, col_w)
if len(lines) > 12:
    body_size = 28
    line_h = 46
    lines = sf.wrap(FACT, "serif-cjk", body_size, col_w)
n = len(lines)
per_col = (n + 1) // 2
bar_bottom = body_y0 + per_col * line_h + 6
bottom_rule_y = max(1280, bar_bottom + 60)
deco_y = bottom_rule_y + 35

# ---------- 纸色 + 噪点 ----------
base = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
base[..., 0] = 239
base[..., 1] = 230
base[..., 2] = 210
base[..., 3] = 255
noise = np.random.randint(-5, 6, size=(sf.H, sf.W, 1)).astype(np.int16)
for c in (0, 1, 2):
    base[..., c] = np.clip(base[..., c].astype(np.int16) + noise[..., 0], 0, 255).astype(np.uint8)
sf.composite(base)

# ---------- 印刷网点 ----------
dot = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
yy_g, xx_g = np.mgrid[0:sf.H, 0:sf.W]
dot_mask = (yy_g % 14 < 2) & (xx_g % 14 < 2)
dot[..., 3] = (dot_mask * 16).astype(np.uint8)
dot[..., 0] = 80
dot[..., 1] = 70
dot[..., 2] = 60
sf.composite(dot)

# ---------- 陈渍 ----------
stain = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
sd = ImageDraw.Draw(stain)
for sx, sy, sr, sa in [
    (150, 120, 70, 22), (870, 600, 90, 16), (210, 1150, 85, 18),
    (850, 240, 60, 14), (700, 90, 55, 12), (120, 950, 80, 14),
]:
    sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(175, 145, 100, sa))
stain = stain.filter(ImageFilter.GaussianBlur(60))
sf.composite(stain)

# ---------- 暗角 ----------
vig = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
yy_v, xx_v = np.mgrid[0:sf.H, 0:sf.W].astype(np.float32)
dx_n = (xx_v - sf.W / 2) / (sf.W / 2)
dy_n = (yy_v - sf.H / 2) / (sf.H / 2)
dist = np.sqrt(dx_n * dx_n + dy_n * dy_n)
a_v = np.clip((dist - 0.75) / 0.5, 0.0, 1.0)
a_v = (np.power(a_v, 1.3) * 60).astype(np.uint8)
vig[..., 0] = 80
vig[..., 1] = 68
vig[..., 2] = 55
vig[..., 3] = a_v
sf.composite(vig)

# ---------- 装饰线条层 ----------
deco = sf.layer()
dp = Image.fromarray(deco)
d = ImageDraw.Draw(dp)

def hline(y, x1, x2, w=2, color=INK):
    d.line([L(x1), L(y), L(x2), L(y)], fill=color, width=L(w))

def vline(x, y1, y2, w=2, color=INK):
    d.line([L(x), L(y1), L(x), L(y2)], fill=color, width=L(w))

def rhombus(cx, cy, r, color=INK):
    d.polygon([(L(cx), L(cy - r)), (L(cx + r), L(cy)),
               (L(cx), L(cy + r)), (L(cx - r), L(cy))], fill=color)

hline(44, 50, 950, w=1)
hline(135, 80, 425, w=2)
hline(135, 575, 920, w=2)
rhombus(80, 135, 5)
rhombus(920, 135, 5)
hline(225, 50, 950, w=5)
hline(231, 50, 950, w=1)

rhombus(500, 258, 8)
rhombus(500, 264, 4, color=INK_SOFT)
vline(110, 258, 500, w=1)
vline(890, 258, 500, w=1)
hline(500, 110, 890, w=2)
hline(542, 110, 890, w=1)

vline(505, 918, bar_bottom, w=2)

hline(bottom_rule_y, 50, 950, w=5)
hline(bottom_rule_y + 6, 50, 950, w=1)
rhombus(500, deco_y, 8)
rhombus(470, deco_y, 3, color=INK_SOFT)
rhombus(530, deco_y, 3, color=INK_SOFT)
hline(deco_y, 440, 485, w=2)
hline(deco_y, 515, 560, w=2)
sf.composite(dp)

# ---------- 报头太阳 ----------
sun = sf.layer()
sp = Image.fromarray(sun)
sd2 = ImageDraw.Draw(sp)
scx, scy = L(500), L(135)
ro, ri = L(48), L(28)
for i in range(20):
    ang = 2.0 * math.pi * i / 20.0
    x1 = scx + (ri + 3) * math.cos(ang)
    y1 = scy + (ri + 3) * math.sin(ang)
    x2 = scx + (ro - 4) * math.cos(ang)
    y2 = scy + (ro - 4) * math.sin(ang)
    sd2.line([x1, y1, x2, y2], fill=INK, width=3)
sd2.ellipse([scx - ri, scy - ri, scx + ri, scy + ri], outline=INK, width=3)
sd2.ellipse([scx - ro, scy - ro, scx + ro, scy + ro], outline=INK, width=4)
sd2.ellipse([scx - 9, scy - 9, scx + 9, scy + 9], fill=INK)
sf.composite(sp)

# ---------- 罐头木刻插图 ----------
can = sf.layer()
cp = Image.fromarray(can)
cd = ImageDraw.Draw(cp)
ink2 = (52, 40, 28, 255)
cx_c, top_cy, bot_cy = L(500), L(590), L(840)
r_c, rh_c = L(105), L(22)

cd.ellipse([cx_c - r_c, bot_cy - rh_c, cx_c + r_c, bot_cy + rh_c],
           fill=PAPER, outline=ink2, width=L(2))
cd.rectangle([cx_c - r_c, top_cy + rh_c - 6, cx_c + r_c, bot_cy - rh_c + 6],
             fill=PAPER, outline=ink2, width=L(2))
for i in range(-5, 6):
    xx0 = cx_c + i * L(17)
    cd.line([xx0, top_cy + rh_c - 4, xx0, bot_cy - rh_c + 4],
            fill=(52, 40, 28, 44), width=2)
cd.ellipse([cx_c - r_c, top_cy - rh_c, cx_c + r_c, top_cy + rh_c],
           fill=PAPER, outline=ink2, width=L(2))
cd.ellipse([cx_c - r_c + L(10), top_cy - rh_c + 8, cx_c + r_c - L(10), top_cy + rh_c - 10],
           outline=ink2, width=2)
for yy0 in [L(610), L(616), L(622), L(814), L(820)]:
    cd.line([cx_c - r_c - 8, yy0, cx_c + r_c + 8, yy0], fill=ink2, width=2)
cd.rectangle([cx_c - r_c + L(14), L(650), cx_c + r_c - L(14), L(780)],
             outline=ink2, width=2)
cd.line([L(414), L(672), L(586), L(672)], fill=(52, 40, 28, 85), width=2)
cd.line([L(414), L(758), L(586), L(758)], fill=(52, 40, 28, 85), width=2)
cd.polygon([(L(500), L(701)), (L(514), L(715)), (L(500), L(729)), (L(486), L(715))],
           fill=(155, 55, 40, 220))
cd.ellipse([L(395), L(878), L(605), L(898)], outline=(52, 40, 28, 90), width=2)
cd.line([L(398), L(894), L(602), L(894)], fill=(52, 40, 28, 60), width=2)
sf.composite(cp)

# ---------- 文字 ----------
sf.serial(80, 52, SERIAL, family="serif", size=22, fill=INK, role="meta", anchor="lt")
sf.datestamp(920, 52, DATE, family="serif", size=22, fill=INK, role="meta", anchor="rt")

q1, q2 = QUOTE.split("，", 1)
q1 = q1 + "，"
sf.text(500, 280, q1, family="serif-cjk", size=54, fill=INK, role="quote", bold=True, anchor="mt")
sf.text(500, 370, q2, family="serif-cjk", size=54, fill=INK, role="quote", bold=True, anchor="mt")

for i, ln in enumerate(lines):
    if i < per_col:
        sf.text(col_x1, body_y0 + i * line_h, ln, family="serif-cjk",
                size=body_size, fill=INK, role="body", anchor="lt")
    else:
        j = i - per_col
        sf.text(col_x2, body_y0 + j * line_h, ln, family="serif-cjk",
                size=body_size, fill=INK, role="body", anchor="lt")

sf.save(OUT_PATH)
