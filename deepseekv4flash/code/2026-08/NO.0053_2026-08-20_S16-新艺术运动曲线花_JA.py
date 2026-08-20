from atelier_canvas import Surface
import math
import numpy as np
from PIL import Image, ImageDraw

W, H = 1000, 1700
sf = Surface(W, H, scale=2, bg=(244, 237, 224))
sf.frame(80, 50, 840, 1600)

# 文字颜色
T_GOLD = (150, 110, 38)
T_GREEN = (28, 76, 56)
T_INK = (58, 46, 32)
T_SOFT = (96, 84, 62)

# 装饰颜色
P_GOLD = (176, 132, 50, 255)
P_GOLD_D = (142, 106, 36, 255)
P_GOLD_L = (226, 204, 150, 255)
P_GREEN_D = (30, 78, 58, 255)
P_GREEN_M = (84, 138, 104, 150)
P_LEAF = (52, 104, 76, 230)

# ---- 背景：米白做旧纸 + 噪点 ----
lay = sf.layer()
hh, ww = lay.shape[:2]
S = ww / W

vy = np.linspace(0, 1, hh)[:, None]
r0 = np.clip(247 - 14 * vy, 0, 255)
g0 = np.clip(240 - 10 * vy, 0, 255)
b0 = np.clip(227 - 16 * vy, 0, 255)
nz = np.random.normal(0, 3.0, (hh, ww))
lay[..., 0] = np.clip(r0 + nz, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(g0 + nz, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(b0 + nz, 0, 255).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# ---- 新艺术运动曲线花卉装饰 ----
deco = Image.new("RGBA", (ww, hh), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)


def wave(draw, x0, x1, y, amp, k, color, width, phase=0.0):
    pts = []
    steps = int((x1 - x0) / 3)
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        yy = y + amp * math.sin(math.pi * t * k + phase)
        pts.append((x * S, yy * S))
    draw.line(pts, fill=color, width=max(1, int(width * S)))


def bezier(draw, p0, p1, ctrl, color, width):
    pts = []
    for i in range(25):
        t = i / 24
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * ctrl[0] + t * t * p1[0]
        y = u * u * p0[1] + 2 * u * t * ctrl[1] + t * t * p1[1]
        pts.append((x * S, y * S))
    draw.line(pts, fill=color, width=max(1, int(width * S)))


def petal(draw, cx, cy, rx, ry, ang, color):
    ca = math.cos(math.radians(ang))
    sa = math.sin(math.radians(ang))
    pts = []
    for t in range(0, 360, 6):
        rd = math.radians(t)
        x = rx * math.cos(rd)
        y = ry * math.sin(rd)
        xr = x * ca - y * sa
        yr = x * sa + y * ca
        pts.append(((cx + xr) * S, (cy + yr) * S))
    draw.polygon(pts, fill=color)


def flower(draw, cx, cy, r, n=6, rot=0.0, outer=P_GOLD, inner=P_GOLD_L, center=P_GOLD_D):
    for i in range(n):
        ang = rot + i * (360.0 / n)
        px = cx + math.cos(math.radians(ang)) * r * 0.55
        py = cy + math.sin(math.radians(ang)) * r * 0.55
        petal(draw, px, py, r * 1.02, r * 0.5, ang, outer)
        petal(draw, px, py, r * 0.72, r * 0.32, ang, inner)
    draw.ellipse([(cx - r * 0.26) * S, (cy - r * 0.26) * S,
                  (cx + r * 0.26) * S, (cy + r * 0.26) * S], fill=center)
    draw.ellipse([(cx - r * 0.12) * S, (cy - r * 0.12) * S,
                  (cx + r * 0.12) * S, (cy + r * 0.12) * S], fill=(240, 226, 190, 255))


def dashed(draw, p, q, color, width=2, seg=8, gap=6):
    x0, y0 = p
    x1, y1 = q
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 0:
        return
    step = seg + gap
    t = 0.0
    while t < 1.0:
        t0 = t
        t1 = min(t0 + seg / L, 1.0)
        draw.line(
            [((x0 + (x1 - x0) * t0) * S, (y0 + (y1 - y0) * t0) * S),
             ((x0 + (x1 - x0) * t1) * S, (y0 + (y1 - y0) * t1) * S)],
            fill=color, width=int(width * S))
        t += step / L


# 顶部花带
wave(d, 120, 880, 70, 13, 2.0, P_GREEN_D, 3)
wave(d, 120, 880, 104, 10, 1.5, P_GOLD, 2, 1.2)
flower(d, 260, 64, 16, n=6, rot=15)
flower(d, 500, 104, 12, n=5, rot=0)
flower(d, 740, 64, 16, n=6, rot=30)

# 两侧垂蔓
bezier(d, (85, 400), (105, 890), (95, 650), P_GREEN_D, 2)
flower(d, 95, 770, 9, n=5, rot=10)
bezier(d, (915, 400), (895, 890), (905, 650), P_GREEN_D, 2)
flower(d, 905, 770, 9, n=5, rot=25)

# 流水号两侧短线
d.line([(330 * S, 168 * S), (412 * S, 168 * S)], fill=P_GOLD_D, width=2)
d.line([(588 * S, 168 * S), (670 * S, 168 * S)], fill=P_GOLD_D, width=2)
for px in (330, 412, 588, 670):
    d.ellipse([(px - 3) * S, 165 * S, (px + 3) * S, 171 * S], fill=P_GOLD_D)

# QUOTE 下方的分隔曲线
wave(d, 180, 820, 448, 6, 1.0, P_GREEN_D, 2, 0.6)
flower(d, 500, 436, 10, n=5, rot=20)

# 五十音图网格（5 段 × 10 行）
gx0, gy0 = 150, 500
gw, gh = 700, 240
cw, ch = gw / 10.0, gh / 5.0
d.rectangle([gx0 * S, gy0 * S, (gx0 + gw) * S, (gy0 + gh) * S],
            outline=P_GOLD, width=int(2 * S))
for i in range(1, 10):
    xx = gx0 + cw * i
    d.line([(xx * S, gy0 * S), (xx * S, (gy0 + gh) * S)], fill=P_GREEN_M, width=max(1, int(S)))
for j in range(1, 5):
    yy = gy0 + ch * j
    d.line([(gx0 * S, yy * S), ((gx0 + gw) * S, yy * S)], fill=P_GREEN_M, width=max(1, int(S)))

# 『ん』的孤格（虚线框 + 金点）
nx0, ny0 = gx0 + gw + 26, gy0 + 4 * ch
dashed(d, (nx0, ny0), (nx0 + cw, ny0), P_GOLD_D, 2)
dashed(d, (nx0 + cw, ny0), (nx0 + cw, ny0 + ch), P_GOLD_D, 2)
dashed(d, (nx0 + cw, ny0 + ch), (nx0, ny0 + ch), P_GOLD_D, 2)
dashed(d, (nx0, ny0 + ch), (nx0, ny0), P_GOLD_D, 2)
dcx, dcy = nx0 + cw / 2.0, ny0 + ch / 2.0
d.ellipse([(dcx - 7) * S, (dcy - 7) * S, (dcx + 7) * S, (dcy + 7) * S], fill=P_GOLD)

# FACT 上方细金线
d.line([(280 * S, 796 * S), (720 * S, 796 * S)], fill=P_GOLD_L, width=1)

# 底部花茎
bezier(d, (500, 1690), (500, 1490), (500, 1590), P_GREEN_D, 4)
bezier(d, (185, 1690), (332, 1585), (240, 1640), P_GREEN_D, 3)
bezier(d, (815, 1690), (668, 1585), (760, 1640), P_GREEN_D, 3)
for ang in range(180, 361, 30):
    petal(d, 500, 1692, 30, 12, ang, P_LEAF)
flower(d, 500, 1458, 36, n=8, rot=22.5)
flower(d, 325, 1580, 13, n=5, rot=10)
flower(d, 675, 1580, 13, n=5, rot=40)
petal(d, 458, 1522, 24, 10, -42, P_LEAF)
petal(d, 546, 1564, 22, 9, 52, P_LEAF)
petal(d, 316, 1622, 18, 8, 24, P_LEAF)
petal(d, 684, 1622, 18, 8, -24, P_LEAF)

sf.composite(deco)

# ---- 文字层 ----
sf.serial(500, 152, SERIAL, family="sans", size=21, fill=T_GOLD, anchor="mm", role="meta")
sf.datestamp(500, 1378, DATE, family="sans", size=21, fill=T_GOLD, anchor="mm", role="meta")

q_parts = QUOTE.strip().split("\n")
quote_jp = q_parts[0].strip()
quote_zh = "\n".join(q_parts[1:]).strip()
if not quote_zh:
    quote_zh = "（什么都没有的声音，一直站在日语的最末尾。）"

q_lines = sf.wrap(quote_jp, "cjk-jp", 40, 820)
yy = 206
for ln in q_lines:
    box = sf.text(500, yy, ln, family="cjk-jp", size=40, fill=T_GREEN, anchor="mt", role="quote")
    yy = box.bottom + 14

sf.text(500, yy, quote_zh, family="cjk-sc", size=28, fill=T_SOFT, anchor="mt", role="quote")

parts = FACT.strip().split("\n")
fact_jp = parts[0].strip() if parts else ""
fact_zh = "\n".join(parts[1:]).strip()
if not fact_zh:
    idx = FACT.find("。（")
    if 0 < idx < len(FACT) - 1:
        fact_jp = FACT[:idx + 1].strip()
        fact_zh = FACT[idx + 1:].strip()

f_lines = sf.wrap(fact_jp, "cjk-jp", 31, 820)
yy = 832
for ln in f_lines:
    box = sf.text(500, yy, ln, family="cjk-jp", size=31, fill=T_INK, anchor="mt", role="body")
    yy = box.bottom + 10

if fact_zh:
    yy += 22
    z_lines = sf.wrap(fact_zh, "cjk-sc", 28, 820)
    for ln in z_lines:
        box = sf.text(500, yy, ln, family="cjk-sc", size=28, fill=T_SOFT, anchor="mt", role="body")
        yy = box.bottom + 8

sf.save(OUT_PATH)
