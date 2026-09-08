import numpy as np
import math
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

# ─── 画布 ────────────────────────────────────────────
W, H = 900, 1500
sf = Surface(W, H, scale=2, bg=(218, 198, 160))

# 羊皮纸底色渐变
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
r = (213 - 26 * yy) * (1 + 0.07 * np.sin(xx * 25))
g = (195 - 30 * yy) * (1 + 0.05 * np.sin(xx * 31 + 2))
b = (158 - 32 * yy) * (1 + 0.06 * np.sin(xx * 27 + 4))
lay[..., 0] = np.clip(r, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(g, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(b, 0, 255).astype(np.uint8)
lay[..., 3] = 255
np.random.seed(57)
noise = np.random.normal(0, 7, (sf.H, sf.W, 3))
lay[..., :3] = np.clip(lay[..., :3].astype(np.float32) + noise, 0, 255).astype(np.uint8)
dist = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2)
vign = np.clip(1 - 0.45 * (dist / np.sqrt(0.5)), 0.55, 1)[..., None]
lay[..., :3] = (lay[..., :3].astype(np.float32) * vign).astype(np.uint8)
sf.composite(lay)

# ─── 装饰图层（海图元素） ─────────────────────────────
dec = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(dec)

INK = (74, 58, 38, 230)
RED = (158, 61, 43, 200)
TEAL = (39, 92, 96, 170)

# 经纬网格
step = 190
for gx in range(-600, W + 600, step):
    d.line([(gx, -50), (gx + 120, H + 50)], fill=(74, 58, 38, 32), width=2)
for gy in range(-100, H + 100, 155):
    d.line([(-50, gy), (W + 50, gy - 28)], fill=(74, 58, 38, 32), width=2)

# 三重边框
d.rectangle([30, 30, W - 30, H - 30], outline=INK, width=6)
d.rectangle([46, 46, W - 46, H - 46], outline=(74, 58, 38, 130), width=2)
d.rectangle([58, 58, W - 58, H - 58], outline=(74, 58, 38, 80), width=1)

# 罗盘玫瑰
cx, cy = W // 2, 148
r0 = 78
for i in range(4):
    ang = np.pi / 2 * i
    dx, dy = np.cos(ang), np.sin(ang)
    tipx = cx + dx * r0 * 1.25
    tipy = cy - dy * r0 * 1.25
    px = cx - dy * 10
    py = cy - dx * 10
    qx = cx + dy * 10
    qy = cy + dx * 10
    d.polygon([(tipx, tipy), (px, py), (qx, qy)], fill=RED)
    ang2 = ang + np.pi / 4
    dx2, dy2 = np.cos(ang2), np.sin(ang2)
    tip2x = cx + dx2 * r0 * 0.55
    tip2y = cy - dy2 * r0 * 0.55
    p2x = cx - dy * 6 + dx * 6
    p2y = cy - dx * 6 - dy * 6
    q2x = cx + dy * 6 + dx * 6
    q2y = cy + dx * 6 - dy * 6
    d.polygon([(tip2x, tip2y), (p2x, p2y), (q2x, q2y)], fill=INK)
d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], outline=INK, width=3)
d.ellipse([cx - r0 * 0.62, cy - r0 * 0.62, cx + r0 * 0.62, cy + r0 * 0.62],
          outline=INK, width=2)
d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=INK)

# 航线虚线
pts = [(cx, cy + r0 + 14), (cx + 90, 300), (cx - 40, 390), (cx + 110, 520),
       (cx - 70, 650), (cx + 60, 790)]
d.line(pts, fill=RED, width=3)
gap = 18
for p1, p2 in zip(pts[:-1], pts[1:]):
    x1, y1 = p1
    x2, y2 = p2
    dist_l = math.hypot(x2 - x1, y2 - y1)
    steps = max(int(dist_l / gap), 1)
    for s in range(steps):
        t0 = s / steps
        t1 = (s + 0.45) / steps
        sx0 = x1 + (x2 - x1) * t0
        sy0 = y1 + (y2 - y1) * t0
        sx1 = x1 + (x2 - x1) * t1
        sy1 = y1 + (y2 - y1) * t1
        d.line([(sx0, sy0), (sx1, sy1)], fill=(218, 198, 160, 240), width=4)

# 小礁石
d.ellipse([110, 430, 170, 490], outline=INK, width=2, fill=(158, 61, 43, 70))
d.ellipse([126, 446, 166, 486], outline=(74, 58, 38, 120), width=1)
for spr in range(4):
    a = np.pi * spr / 2 + 0.35
    sx0 = 140 + np.cos(a) * 22
    sy0 = 460 - np.sin(a) * 22 + 8
    sx1 = 140 + np.cos(a) * 42
    sy1 = 460 - np.sin(a) * 42 + 2
    d.line([(sx0, sy0), (sx1, sy1)], fill=INK, width=2)

# 波浪线（右下）
for wy in [(1110, 70), (1140, 46), (1170, 24)]:
    d.arc([W - 195, wy[0] - 26, W - 95, wy[0] + 22], 200, 340, fill=TEAL, width=3)

# 深海蓝光点
np.random.seed(58)
for _ in range(36):
    bx = np.random.randint(90, W - 90)
    by = np.random.randint(820, 1220)
    rad = np.random.randint(3, 9)
    alpha = np.random.randint(80, 190)
    col = (56, 88, 140, alpha) if np.random.rand() > 0.5 else (39, 92, 96, alpha)
    d.ellipse([bx - rad, by - rad, bx + rad, by + rad], fill=col)

# 猪籮柚虫装饰
def pigbutt(px0, py0, s):
    d.ellipse([px0, py0, px0 + 56 * s, py0 + 52 * s], fill=(180, 108, 98, 170),
              outline=(74, 58, 38, 200), width=2)
    d.ellipse([px0 + 48 * s, py0, px0 + 96 * s, py0 + 44 * s], fill=(180, 108, 98, 170),
              outline=(74, 58, 38, 200), width=2)
    d.ellipse([px0 + 20 * s, py0 + 18 * s, px0 + 32 * s, py0 + 30 * s],
              fill=(74, 58, 38, 190))
    d.ellipse([px0 + 64 * s, py0 + 16 * s, px0 + 76 * s, py0 + 28 * s],
              fill=(74, 58, 38, 190))

pigbutt(362, 25, 6.2)

sf.composite(np.array(dec), mode="normal", opacity=0.95)

# 蓝光模糊光晕
glow_im = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow_im)
np.random.seed(58)
for _ in range(36):
    bx = np.random.randint(90, W - 90)
    by = np.random.randint(820, 1220)
    rad = np.random.randint(10, 22)
    gd.ellipse([bx - rad, by - rad, bx + rad, by + rad],
               fill=(56, 88, 140, 90))
glow_im = glow_im.filter(ImageFilter.GaussianBlur(18))
sf.composite(glow_im, mode="screen", opacity=0.6)

# ─── 文字区域垫底（干净纯色，不透明） ─────────────────
back = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
bd = ImageDraw.Draw(back)

# 金句区域
bd.rectangle([60, 250, 840, 480], fill=(232, 212, 178, 255))
# 事实区域
bd.rectangle([60, 500, 840, 950], fill=(232, 212, 178, 255))
# 底部 meta 图章：深褐色背景，浅色文字
bd.rectangle([580, 1372, 840, 1484], fill=(74, 58, 38, 255))

sf.composite(np.array(back), mode="normal", opacity=1.0)

# ─── 金句 ──────────────────────────────────────────
sf.frame(90, 260, W - 180, H - 360)

qu_box = sf.text(W // 2, 290, QUOTE,
                 family="cjk-hk", size=46, fill=(74, 58, 38),
                 anchor="mt", role="quote", bold=True,
                 max_w=W - 180, line_gap=0.38, allow_overlap=False)

# ─── 冷知识 ────────────────────────────────────────
sep_y = qu_box.bottom + 50
sf.frame(90, sep_y, W - 180, H - sep_y - 90)

fact_box = sf.text(W // 2, sep_y + 24, FACT,
                   family="cjk-hk", size=31, fill=(62, 50, 34),
                   anchor="mt", role="body", bold=False,
                   max_w=W - 180, line_gap=0.45, allow_overlap=False)

# ─── 流水号与日期（深色章内，上下排布） ─────────────
sf.frame(580, 1372, 260, 112)

sf.serial(600, 1388, SERIAL,
          family="cjk-hk", size=24, fill=(232, 212, 178),
          anchor="lt", role="meta", bold=True, allow_overlap=False)

sf.datestamp(600, 1438, DATE,
             family="cjk-hk", size=24, fill=(232, 212, 178),
             anchor="lt", role="meta", bold=False, allow_overlap=False)

sf.save(OUT_PATH)
