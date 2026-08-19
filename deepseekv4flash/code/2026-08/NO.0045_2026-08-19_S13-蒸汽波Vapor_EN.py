from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

sf = Surface(1000, 1780, scale=2, bg=(12, 5, 30))
LW, LH = 1000, 1780
W, H = sf.W, sf.H

# ================= 背景渐变 =================
bg = sf.layer()
yy = np.linspace(0, 1, H)[:, None]
xx = np.linspace(0, 1, W)[None, :]
g_top = np.array([12, 5, 30])
g_mid = np.array([46, 20, 70])
g_bot = np.array([118, 36, 98])
for c in range(3):
    a = g_top[c] + (g_mid[c] - g_top[c]) * np.clip(yy / 0.52, 0, 1) ** 1.15
    b = g_mid[c] + (g_bot[c] - g_mid[c]) * np.clip((yy - 0.52) / 0.48, 0, 1) ** 0.85
    bg[..., c] = np.clip(np.where(yy < 0.52, a, b), 0, 255).astype(np.uint8)
bg[..., 3] = 255
sf.composite(bg)

# ================= 环境光晕 =================
haze = sf.layer()
dx = xx - 0.16
dy = yy - 0.34
dist = np.sqrt((dx / 0.5) ** 2 + (dy / 0.5) ** 2)
m = np.clip(1 - dist, 0, 1) ** 2
haze[..., 0] = 0
haze[..., 1] = 210
haze[..., 2] = 255
haze[..., 3] = (m * 36).astype(np.uint8)
sf.composite(haze, mode="screen")

haze2 = sf.layer()
dx = xx - 0.84
dy = yy - 0.38
dist = np.sqrt((dx / 0.5) ** 2 + (dy / 0.5) ** 2)
m = np.clip(1 - dist, 0, 1) ** 2
haze2[..., 0] = 255
haze2[..., 1] = 100
haze2[..., 2] = 190
haze2[..., 3] = (m * 42).astype(np.uint8)
sf.composite(haze2, mode="screen")

# ================= 小星点 =================
np.random.seed(13)
rn = np.random.rand(H, W)
ys, xs = np.where((rn < 0.0006) & (np.linspace(0, 1, H)[:, None] < 0.52))
dots = sf.layer()
for y, x in zip(ys, xs):
    dots[y, x, :3] = [255, 255, 255]
    dots[y, x, 3] = np.random.randint(50, 140)
sf.composite(dots, opacity=0.85)

# ================= 蒸汽波条纹太阳 =================
sun_cx, sun_cy = int(W * 0.5), int(H * 0.175)
sun_r = int(W * 0.19)

sun_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(sun_img)
stripe_h = max(3, sun_r // 9)
n_stripe = 20
for i in range(n_stripe):
    rel = -sun_r + (i + 0.5) * (2 * sun_r / n_stripe)
    if abs(rel) >= sun_r:
        continue
    chord = np.sqrt(max(0, sun_r * sun_r - rel * rel))
    d.rectangle(
        [sun_cx - chord, sun_cy + rel - stripe_h // 2,
         sun_cx + chord, sun_cy + rel + stripe_h // 2],
        fill=(255, 110, 199, 235))
sf.composite(sun_img, opacity=0.95)

sg1 = sun_img.filter(ImageFilter.GaussianBlur(60))
sf.composite(sg1, mode="screen", opacity=0.5)
sg2 = sun_img.filter(ImageFilter.GaussianBlur(14))
sf.composite(sg2, mode="screen", opacity=0.25)

# ================= 放射光芒 =================
rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(rays)
for ang in range(-115, 116, 8):
    a = np.radians(ang)
    ddx, ddy = np.cos(a), np.sin(a)
    x0 = sun_cx + ddx * (sun_r + 10)
    y0 = sun_cy - ddy * (sun_r + 10)
    x1 = sun_cx + ddx * (sun_r + 62)
    y1 = sun_cy - ddy * (sun_r + 62)
    d.line([(int(x0), int(y0)), (int(x1), int(y1))],
           fill=(255, 100, 200, 110), width=5)
sf.composite(rays, opacity=0.8)

# ================= 透视网格 =================
grid_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(grid_img)
gy0 = int(H * 0.65)
van_x = W // 2

for i in range(11):
    t = i / 10
    y = gy0 + (H - gy0) * (t ** 2.2)
    alpha = int(120 - t * 55)
    d.line([(0, int(y)), (W, int(y))], fill=(255, 40, 220, alpha), width=2)

for i in range(-9, 10):
    x1 = van_x + i * 130
    d.line([(van_x, gy0), (int(x1), H)], fill=(255, 40, 220, 85), width=2)

d.line([(0, gy0), (W, gy0)], fill=(0, 240, 255, 220), width=4)
grid_img = grid_img.filter(ImageFilter.GaussianBlur(1))
sf.composite(grid_img, opacity=0.8)

gt = sf.layer()
tt = np.clip((np.linspace(0, 1, H)[:, None] - 0.65) / 0.35, 0, 1) ** 1.5
gt[..., 0] = 255
gt[..., 1] = 60
gt[..., 2] = 210
gt[..., 3] = (tt * 60).astype(np.uint8)
sf.composite(gt, opacity=0.45)

# ================= 鸽子剪影 =================
pg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(pg)

def draw_pigeon(x, y, s, col, w=4):
    x, y = int(x * 2), int(y * 2)
    d.ellipse([x - 11 * s, y - 6 * s, x + 12 * s, y + 6 * s],
              outline=col, width=w)
    d.arc([x + 8 * s, y - 13 * s, x + 22 * s, y + 2 * s],
          180, 360, fill=col, width=int(w * 0.9))
    d.line([(x + 20 * s, y - 7 * s), (x + 27 * s, y - 9 * s)], fill=col, width=w)
    d.line([(x - 3 * s, y - 4 * s), (x - 22 * s, y - 20 * s)], fill=col, width=w)
    d.line([(x + 1 * s, y - 4 * s), (x + 22 * s, y - 20 * s)], fill=col, width=w)
    d.line([(x - 10 * s, y + 3 * s), (x - 24 * s, y + 15 * s)], fill=col, width=w)
    d.ellipse([x + 13 * s, y - 8 * s, x + 16 * s, y - 5 * s], fill=col)

draw_pigeon(190, 430, 1.5, (0, 240, 255, 230))
draw_pigeon(830, 470, 1.2, (255, 110, 199, 230))
draw_pigeon(760, 385, 0.9, (255, 255, 255, 220))
sf.composite(pg, opacity=0.95)

# ================= 十字星 =================
sp_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(sp_img)

def spark(x, y, r, col, w):
    x, y, r = int(x * 2), int(y * 2), int(r * 2)
    d.line([(x - r, y), (x + r, y)], fill=col, width=w)
    d.line([(x, y - r), (x, y + r)], fill=col, width=w)
    d.line([(int(x - r * 0.55), int(y - r * 0.55)),
            (int(x + r * 0.55), int(y + r * 0.55))], fill=col, width=w)
    d.line([(int(x - r * 0.55), int(y + r * 0.55)),
            (int(x + r * 0.55), int(y - r * 0.55))], fill=col, width=w)

spark(120, 400, 26, (0, 240, 255, 220), 4)
spark(880, 340, 22, (255, 255, 255, 210), 4)
spark(300, 525, 18, (255, 110, 199, 200), 4)
spark(700, 545, 16, (255, 220, 255, 190), 4)
spark(430, 530, 14, (255, 255, 255, 200), 4)
sf.composite(sp_img, opacity=0.9)

# ================= 装饰双线 =================
ln = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(ln)
d.line([(130 * 2, 564 * 2), (870 * 2, 564 * 2)], fill=(0, 240, 255, 200), width=4)
d.line([(130 * 2, 578 * 2), (870 * 2, 578 * 2)], fill=(255, 90, 190, 170), width=2)
d.line([(130 * 2, 564 * 2), (130 * 2, 578 * 2)], fill=(0, 240, 255, 180), width=3)
d.line([(870 * 2, 564 * 2), (870 * 2, 578 * 2)], fill=(0, 240, 255, 180), width=3)
sf.composite(ln, opacity=0.9)

# ================= 日期底板 =================
pill = sf.layer()
px0, py0 = int((500 - 130) * 2), int(1665 * 2)
px1, py1 = int((500 + 130) * 2), int(1715 * 2)
pw = px1 - px0
ramp = np.ones(pw)
for i in range(50):
    ramp[i] = i / 50
    ramp[-1 - i] = i / 50
pill[py0:py1, px0:px1, 0] = 20
pill[py0:py1, px0:px1, 1] = 9
pill[py0:py1, px0:px1, 2] = 44
pill[py0:py1, px0:px1, 3] = (168 * ramp).astype(np.uint8)[None, :]
sf.composite(pill, opacity=0.85)

# ================= 文字层 =================
sf.frame(60, 50, 880, 1688)

sf.serial(60, 54, SERIAL,
          family="mono", size=20, fill=(0, 240, 255),
          anchor="lt", role="meta", bold=True)

box_q = sf.text(70, 600, QUOTE,
                family="sans", size=32, fill=(255, 120, 210),
                anchor="lt", role="quote", bold=True,
                max_w=860, line_gap=0.40)

# FACT 拆成英文原文 + 中文翻译分别渲染
fact_split = FACT.find("（")
fact_en = FACT[:fact_split].strip()
fact_zh = FACT[fact_split:].strip()

box_fe = sf.text(70, box_q.bottom + 50, fact_en,
                 family="sans", size=30, fill=(245, 245, 255),
                 anchor="lt", role="body", bold=False,
                 max_w=860, line_gap=0.40)

box_fz = sf.text(70, box_fe.bottom + 36, fact_zh,
                 family="cjk-sc", size=28, fill=(245, 245, 255),
                 anchor="lt", role="body", bold=False,
                 max_w=860, line_gap=0.40)

sf.datestamp(500, 1692, DATE,
             family="mono", size=18, fill=(0, 240, 255),
             anchor="mt", role="meta", bold=True)

# ================= 扫描线与噪点 =================
scan = sf.layer()
scan[::4, :, :3] = 0
scan[::4, :, 3] = 12
sf.composite(scan)

np.random.seed(99)
nl = sf.layer()
rnd2 = np.random.rand(H, W)
mask_n = rnd2 < 0.006
nl[..., :3] = 255
nl[..., 3] = (mask_n * 26).astype(np.uint8)
sf.composite(nl, opacity=0.8)

sf.save(OUT_PATH)
