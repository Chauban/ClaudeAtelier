from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math

W, H = 1000, 1500
sf = Surface(W, H, scale=2, bg=(245, 240, 230))
sf.frame(60, 100, 880, 1330)

PAPER = (245, 240, 230)
INK = (38, 43, 60)
INK_MID = (44, 49, 66)
POST_INK = (58, 68, 92)
STAMP_INK = (232, 238, 248)
rng = np.random.default_rng(20260813)


def split_cjk(s):
    idx = s.find('\uff08')
    if idx == -1:
        return s, ''
    return s[:idx], s[idx:]


paper_np = sf.layer()
n = rng.normal(0, 8, (sf.H, sf.W))
n = np.clip(n, -40, 40)
paper_np[..., 0] = np.clip(128 + n, 0, 255).astype(np.uint8)
paper_np[..., 1] = np.clip(128 + n, 0, 255).astype(np.uint8)
paper_np[..., 2] = np.clip(128 + n, 0, 255).astype(np.uint8)
paper_np[..., 3] = 14
sf.composite(paper_np)

bdr = sf.layer()
yy, xx = np.mgrid[0:sf.H, 0:sf.W]
m = 92
edge = (xx < m) | (xx >= sf.W - m) | (yy < m) | (yy >= sf.H - m)
diag = ((xx + yy) // 19) % 3
cols = [(203, 32, 40), (250, 250, 246), (28, 60, 140)]
for i, col in enumerate(cols):
    sel = edge & (diag == i)
    bdr[sel, 0] = col[0]
    bdr[sel, 1] = col[1]
    bdr[sel, 2] = col[2]
    bdr[sel, 3] = 255
sf.composite(bdr)

deco = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)
d.rectangle([m + 4, m + 4, sf.W - m - 4, sf.H - m - 4], outline=(196, 28, 36, 190), width=3)
d.rectangle([m + 10, m + 10, sf.W - m - 10, sf.H - m - 10], outline=(28, 60, 140, 140), width=2)
sf.composite(deco)

tag = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(tag)
d.rectangle([140, 198, 330, 264], fill=(28, 60, 140, 255))
pc = (248, 248, 243, 255)
d.polygon([(306, 228), (168, 218), (168, 238)], fill=pc)
d.line([(306, 228), (168, 228)], fill=(28, 60, 140, 255), width=3)
d.polygon([(184, 228), (216, 210), (216, 228)], fill=pc)
d.polygon([(184, 228), (216, 246), (216, 228)], fill=pc)
d.line([(212, 255), (320, 247)], fill=(248, 248, 243, 170), width=2)
d.line([(218, 260), (326, 252)], fill=(248, 248, 243, 110), width=2)
sf.composite(tag)

sx0, sy0, sx1, sy1 = 1270, 260, 1890, 900
hs = sy1 - sy0
tt = np.linspace(0, 1, hs)[:, None]
stamp_np = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
stamp_np[sy0:sy1, sx0:sx1, 0] = (10 + 26 * tt).astype(np.uint8)
stamp_np[sy0:sy1, sx0:sx1, 1] = (14 + 32 * tt).astype(np.uint8)
stamp_np[sy0:sy1, sx0:sx1, 2] = (36 + 70 * tt).astype(np.uint8)
stamp_np[sy0:sy1, sx0:sx1, 3] = 255

yy_m, xx_m = np.mgrid[sy0:sy1, sx0:sx1]
m1x, m1y, m1r = 1580, 600, 265
m2x, m2y, m2r = 1580, 312, 268
r1 = np.sqrt((xx_m - m1x) ** 2 + (yy_m - m1y) ** 2)
r2 = np.sqrt((xx_m - m2x) ** 2 + (yy_m - m2y) ** 2)
moon = (r1 <= m1r) & (r2 >= m2r)
luma = np.clip((r2 - m2r) / 55.0, 0, 1) * 56 + 198
luma = np.clip(luma + rng.normal(0, 4, luma.shape), 0, 255)
moon_rgb = np.stack([
    np.clip(luma * 0.92, 0, 255).astype(np.uint8),
    np.clip(luma * 0.97, 0, 255).astype(np.uint8),
    np.clip(luma * 1.04, 0, 255).astype(np.uint8),
    np.full_like(luma, 255, dtype=np.uint8),
], axis=-1)
vis = stamp_np[sy0:sy1, sx0:sx1]
vis[moon] = moon_rgb[moon]

stamp_img = Image.fromarray(stamp_np, "RGBA")
d = ImageDraw.Draw(stamp_img)

for _ in range(180):
    px_s = int(rng.integers(sx0 + 24, sx1 - 24))
    py_s = int(rng.integers(sy0 + 24, sy1 - 24))
    if (px_s - m1x) ** 2 + (py_s - m1y) ** 2 < (m1r + 16) ** 2:
        continue
    s = int(rng.integers(1, 3))
    a = int(rng.integers(100, 210))
    d.ellipse([px_s - s, py_s - s, px_s + s, py_s + s], fill=(255, 255, 255, a))

pts = []
for x in range(1340, 1850, 26):
    y = 655 + 30 * math.sin((x - 1340) * 0.09 + 1.1) - (x - 1340) * 0.05
    pts.append((x, y))
d.line([(x + 6, y + 10) for x, y in pts], fill=(14, 20, 34, 150), width=14)
d.line(pts, fill=(40, 50, 74, 255), width=7)
d.line([(x, y - 2) for x, y in pts], fill=(190, 205, 228, 190), width=3)
for x in range(1390, 1870, 46):
    y = 655 + 30 * math.sin((x - 1340) * 0.09 + 1.1) - (x - 1340) * 0.05
    d.line([x, y, x, y + 16], fill=(56, 66, 88, 170), width=2)
for i in range(5):
    px_f = 1390 + i * 105
    py_f = 704 + 14 * math.sin(i * 2.1)
    d.ellipse([px_f - 3, py_f - 3, px_f + 3, py_f + 3], fill=(60, 70, 92, 200))
d.polygon([(1635, 640), (1668, 606), (1688, 640)], fill=(150, 166, 192, 170))

d.rectangle([sx0 + 28, sy0 + 28, sx1 - 28, sy1 - 28], outline=(222, 230, 242, 105), width=4)

hr = 15
for x in range(sx0 + hr * 2, sx1 - hr * 2 + 1, 34):
    d.ellipse([x - hr, sy0 - hr, x + hr, sy0 + hr], fill=PAPER + (255,))
    d.ellipse([x - hr, sy1 - hr, x + hr, sy1 + hr], fill=PAPER + (255,))
for y in range(sy0 + hr * 2, sy1 - hr * 2 + 1, 34):
    d.ellipse([sx0 - hr, y - hr, sx0 + hr, y + hr], fill=PAPER + (255,))
    d.ellipse([sx1 - hr, y - hr, sx1 + hr, y + hr], fill=PAPER + (255,))
for cx, cy in [(sx0, sy0), (sx1, sy0), (sx0, sy1), (sx1, sy1)]:
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=PAPER + (255,))

sf.composite(stamp_img)

pm = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(pm)
pcx, pcy, br = 500, 2565, 240
INK_A = POST_INK + (150,)
outer = []
for i in range(88):
    ang = 2 * math.pi * i / 88
    r = br + 22 if i % 2 == 0 else br - 12
    outer.append((pcx + r * math.cos(ang), pcy + r * math.sin(ang)))
d.polygon(outer, fill=INK_A)
inner_r = br - 16
d.ellipse([pcx - inner_r, pcy - inner_r, pcx + inner_r, pcy + inner_r], fill=PAPER + (255,))
d.ellipse([pcx - inner_r + 6, pcy - inner_r + 6, pcx + inner_r - 6, pcy + inner_r - 6], outline=INK_A, width=4)
for yb in (pcy - 96, pcy + 96):
    x = pcx - 128
    while x < pcx + 128:
        d.line([x, yb, x + 9, yb - 6, x + 18, yb], fill=INK_A, width=3)
        x += 18
d.line([pcx - 126, pcy + 44, pcx - 16, pcy + 44], fill=INK_A, width=3)
d.line([pcx + 16, pcy + 44, pcx + 126, pcy + 44], fill=INK_A, width=3)
pm_np = np.array(pm)
mk = pm_np[..., 3] > 0
npn = rng.normal(0, 13, mk.shape)
for c in range(3):
    ch = pm_np[..., c]
    ch[mk] = np.clip(ch[mk].astype(np.int16) + npn[mk].astype(np.int16), 0, 255).astype(np.uint8)
pm = Image.fromarray(pm_np, "RGBA").filter(ImageFilter.GaussianBlur(1.1))
sf.composite(pm, opacity=0.88)

div = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(div)
y0d = 960
x = 150
while x < 1850:
    x2 = min(x + 54, 1850)
    d.line([x, y0d, x2, y0d], fill=(28, 60, 140, 110), width=3)
    x += 82
cx_d = 995
d.polygon([(cx_d, y0d - 13), (cx_d + 15, y0d), (cx_d, y0d + 13), (cx_d - 15, y0d)], fill=(203, 32, 40, 190))
d.line([cx_d - 50, y0d, cx_d - 24, y0d], fill=(203, 32, 40, 150), width=3)
d.line([cx_d + 24, y0d, cx_d + 50, y0d], fill=(203, 32, 40, 150), width=3)
sf.composite(div)

trail = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(trail)
xs = np.linspace(160, 1840, 80)
ys = 2160 + 22 * np.sin((xs - 160) / (1840 - 160) * 2 * math.pi * 1.5)
for i in range(0, 79, 2):
    d.line([(xs[i], ys[i]), (xs[i + 1], ys[i + 1])], fill=(70, 82, 108, 110), width=4)
tx, ty = xs[-1] + 14, ys[-1] - 14
d.polygon([(tx - 10, ty + 10), (tx + 28, ty - 8), (tx + 10, ty + 12)], fill=(70, 82, 108, 150))
sf.composite(trail)

q_it, q_cn = split_cjk(QUOTE)
f_it, f_cn = split_cjk(FACT)

qbox = sf.text(70, 120, q_it, family="serif", size=28, fill=INK, anchor="lt", role="quote", max_w=520, line_gap=0.36)
next_y = qbox.bottom + 20
if q_cn:
    cq = sf.text(70, next_y, q_cn, family="cjk-sc", size=28, fill=INK_MID, anchor="lt", role="body", max_w=520, line_gap=0.36)
    next_y = cq.bottom + 50
else:
    next_y = qbox.bottom + 50

f_y = max(470, next_y)
fbox = sf.text(70, f_y, f_it, family="serif", size=28, fill=INK, anchor="lt", role="body", max_w=860, line_gap=0.36)
if f_cn:
    sf.text(70, fbox.bottom + 16, f_cn, family="cjk-sc", size=28, fill=INK_MID, anchor="lt", role="body", max_w=860, line_gap=0.36)

sf.serial(790, 158, SERIAL, family="mono", size=20, fill=STAMP_INK, anchor="mt", role="meta")
sf.datestamp(250, 1282, DATE, family="mono", size=27, fill=POST_INK, anchor="mm", role="meta")

sf.save(OUT_PATH)
