# -*- coding: utf-8 -*-
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 960, 1620
S = 2
sf = Surface(W, H, scale=2, bg=(247, 241, 228))

CX = W // 2
MOON_CX, MOON_CY, MOON_R = 480, 590, 150

sf.frame(120, 150, 720, 1380)

# ---- split English original and Chinese translation from globals ----
def split_zh(text):
    idx = text.index("（")
    return text[:idx], text[idx+1:-1]  # strip （ ）

Q_EN, Q_ZH = split_zh(QUOTE)
F_EN, F_ZH = split_zh(FACT)

# ---------- helpers ----------

def bezier_pts(ctrl, n=70):
    pts = []
    for i in range(n + 1):
        t = i / n
        p = [list(c) for c in ctrl]
        while len(p) > 1:
            p = [[(1 - t) * q[0] + t * r[0], (1 - t) * q[1] + t * r[1]]
                 for q, r in zip(p, p[1:])]
        pts.append((p[0][0], p[0][1]))
    return pts


def ellipse_pts(cx, cy, rx, ry, theta, n=32):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = math.cos(a) * rx
        y = math.sin(a) * ry
        out.append((cx + x * math.cos(theta) - y * math.sin(theta),
                    cy + x * math.sin(theta) + y * math.cos(theta)))
    return out


def draw_stem(d, ctrl, width=5, color=(63, 94, 68, 255)):
    pts = bezier_pts(ctrl)
    px = [(x * S, y * S) for x, y in pts]
    d.line(px, fill=(46, 70, 52, 255), width=width * S, joint="curve")
    d.line(px, fill=color, width=max(2, int(width * S * 0.7)), joint="curve")
    d.line(px, fill=(166, 186, 142, 190), width=max(2, int(width * S * 0.3)), joint="curve")


def leaf(d, cx, cy, rx, ry, theta, fill=(116, 148, 106, 255), outline=(52, 76, 55, 255)):
    d.polygon([(x * S, y * S) for x, y in ellipse_pts(cx, cy, rx + 2.2, ry + 2.2, theta)], fill=outline)
    d.polygon([(x * S, y * S) for x, y in ellipse_pts(cx, cy, rx, ry, theta)], fill=fill)
    if rx > 18:
        x1 = cx - math.cos(theta) * rx * 0.75
        y1 = cy - math.sin(theta) * rx * 0.75
        x2 = cx + math.cos(theta) * rx * 0.75
        y2 = cy + math.sin(theta) * rx * 0.75
        d.line([(x1 * S, y1 * S), (x2 * S, y2 * S)], fill=(63, 94, 68, 200), width=2)


def flower(d, cx, cy, r, n_petals=5, fill=(222, 122, 140, 255),
           outline=(158, 76, 96, 255), center=(246, 214, 160, 255)):
    for i in range(n_petals):
        ang = 2 * math.pi * i / n_petals + math.pi / n_petals
        px = cx + math.cos(ang) * r * 0.55
        py = cy + math.sin(ang) * r * 0.55
        d.polygon([(x * S, y * S) for x, y in ellipse_pts(px, py, r * 0.7, r * 0.42, ang, 22)], fill=outline)
    for i in range(n_petals):
        ang = 2 * math.pi * i / n_petals + math.pi / n_petals
        px = cx + math.cos(ang) * r * 0.50
        py = cy + math.sin(ang) * r * 0.50
        d.polygon([(x * S, y * S) for x, y in ellipse_pts(px, py, r * 0.62, r * 0.34, ang, 22)], fill=fill)
    cr = r * 0.33
    d.ellipse([(cx - cr) * S, (cy - cr) * S, (cx + cr) * S, (cy + cr) * S], fill=center)
    cr2 = r * 0.13
    d.ellipse([(cx - cr2) * S, (cy - cr2) * S, (cx + cr2) * S, (cy + cr2) * S], fill=(178, 116, 70, 255))


def tendril(d, x0, y0, angle_deg, size=15, color=(128, 154, 112, 210)):
    pts = []
    for i in range(40):
        t = i / 39
        r = size * (0.25 + 0.75 * t)
        a0 = math.radians(angle_deg)
        pts.append((x0 + math.cos(a0) * size * 0.5 * t + r * math.cos(t * math.pi * 2.2),
                    y0 + math.sin(a0) * size * 0.5 * t + r * math.sin(t * math.pi * 2.2)))
    d.line([(x * S, y * S) for x, y in pts], fill=color, width=2)


def star4(d, cx, cy, r=5, color=(176, 144, 94, 220)):
    d.line([(cx - r) * S, cy * S, (cx + r) * S, cy * S], fill=color, width=2)
    d.line([cx * S, (cy - r) * S, cx * S, (cy + r) * S], fill=color, width=2)
    d.line([(cx - r * 0.4) * S, (cy - r * 0.4) * S, (cx + r * 0.4) * S, (cy + r * 0.4) * S], fill=color, width=1)
    d.line([(cx - r * 0.4) * S, (cy + r * 0.4) * S, (cx + r * 0.4) * S, (cy - r * 0.4) * S], fill=color, width=1)


# ---------- 1. moon glow ----------
glow = sf.layer()
yy, xx = np.ogrid[0:sf.H, 0:sf.W]
dxg = (xx - MOON_CX * S).astype(np.float32)
dyg = (yy - MOON_CY * S).astype(np.float32)
distg = np.sqrt(dxg * dxg + dyg * dyg)
gval = np.clip(1.0 - distg / (MOON_R * S * 2.1), 0.0, 1.0) ** 1.5
glow[..., 0] = 244
glow[..., 1] = 234
glow[..., 2] = 208
glow[..., 3] = (gval * 50).astype(np.uint8)
sf.composite(glow)

# ---------- 2. rings + laurel leaves ----------
ring = sf.layer()
d = ImageDraw.Draw(Image.fromarray(ring))
for off, alpha, width_px in [(28, 210, 3), (54, 120, 2)]:
    rr = MOON_R + off
    d.ellipse([(MOON_CX - rr) * S, (MOON_CY - rr) * S,
               (MOON_CX + rr) * S, (MOON_CY + rr) * S],
              outline=(176, 144, 94, alpha), width=width_px * S)
for k in range(10):
    ang = k * 2 * math.pi / 10 + 0.3
    lx = MOON_CX + (MOON_R + 54) * math.cos(ang)
    ly = MOON_CY + (MOON_R + 54) * math.sin(ang)
    leaf(d, lx, ly, 15, 7, ang, fill=(126, 158, 112, 235), outline=(58, 82, 58, 230))
sf.composite(ring)

# ---------- 3. back vegetation ----------
veg = sf.layer()
d = ImageDraw.Draw(Image.fromarray(veg))

stems = [
    [(480, 738), (462, 806), (404, 850), (306, 868), (205, 838)],
    [(480, 738), (528, 802), (600, 848), (694, 840), (788, 782)],
    [(352, 658), (306, 618), (258, 546), (268, 478), (296, 428)],
    [(608, 658), (654, 616), (700, 546), (688, 478), (660, 426)],
]
for st in stems:
    draw_stem(d, st, width=5)

leaves = [
    (430, 830, 26, 12, -0.6), (360, 856, 28, 12, 0.1), (285, 870, 26, 12, 0.5),
    (235, 852, 22, 10, 1.1),
    (505, 812, 24, 11, 0.7), (565, 838, 27, 12, -0.1), (645, 852, 26, 12, -0.5),
    (722, 832, 22, 10, -1.0), (762, 802, 20, 9, -1.3),
    (320, 636, 24, 11, -0.5), (266, 570, 26, 12, 0.3), (272, 500, 21, 10, 0.8),
    (642, 632, 24, 11, 0.5), (694, 566, 26, 12, -0.3), (690, 496, 21, 10, -0.8),
]
fills = [(106, 140, 104), (126, 158, 116), (88, 122, 92)]
for i, (lx, ly, rx, ry, th) in enumerate(leaves):
    col = fills[i % 3]
    leaf(d, lx, ly, rx, ry, th, fill=(col[0], col[1], col[2], 240))

flowers = [
    (200, 824, 28, 6),
    (788, 766, 32, 5),
    (304, 430, 20, 6),
    (656, 418, 20, 5),
]
for fx, fy, fr, pet in flowers:
    flower(d, fx, fy, fr, pet)

for bx, by, br in [(250, 830, 9), (360, 862, 8), (620, 858, 8), (740, 830, 9),
                   (282, 610, 7), (696, 606, 7)]:
    d.ellipse([(bx - br) * S, (by - br * 0.7) * S, (bx + br) * S, (by + br * 0.7) * S],
              fill=(206, 132, 148, 235))
    d.ellipse([(bx - br * 0.5) * S, (by - br * 0.35) * S, (bx + br * 0.5) * S, (by + br * 0.35) * S],
              fill=(246, 214, 160, 235))

tendril(d, 262, 822, 200, 14)
tendril(d, 320, 872, 330, 12)
tendril(d, 640, 862, 210, 12)
tendril(d, 760, 736, 150, 14)

sf.composite(veg)

# ---------- 4. moon body ----------
moon = sf.layer()
yy, xx = np.ogrid[0:sf.H, 0:sf.W]
dxm = (xx - MOON_CX * S).astype(np.float32)
dym = (yy - MOON_CY * S).astype(np.float32)
distm = np.sqrt(dxm * dxm + dym * dym)
edge = np.clip((MOON_R * S - distm) / (2.5 * S) + 0.5, 0.0, 1.0)
shade = np.clip(0.30 * distm / (MOON_R * S), 0.0, 0.30)
base = np.array([246, 233, 208], dtype=np.float32)
hi = np.array([253, 248, 235], dtype=np.float32)
col = hi[None, None, :] - (hi - base)[None, None, :] * shade[..., None]
moon[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
moon[..., 3] = (edge * 255).astype(np.uint8)

im = Image.fromarray(moon)
d = ImageDraw.Draw(im)


def _mare(mx, my, rx, ry, al):
    d.ellipse([(mx - rx) * S, (my - ry) * S, (mx + rx) * S, (my + ry) * S],
              fill=(198, 178, 142, al))


_mare(458, 612, 62, 76, 55)
_mare(524, 554, 42, 50, 45)
_mare(442, 502, 34, 40, 35)
_mare(548, 648, 18, 22, 40)
im2 = im.filter(ImageFilter.GaussianBlur(4 * S))
sf.composite(np.asarray(im2))

# ---------- 5. moon detail (faults & craters) ----------
md = sf.layer()
d = ImageDraw.Draw(Image.fromarray(md))

rr = MOON_R
d.ellipse([(MOON_CX - rr) * S, (MOON_CY - rr) * S,
           (MOON_CX + rr) * S, (MOON_CY + rr) * S],
          outline=(168, 140, 100, 220), width=3)


def fault(pts, dark=(146, 116, 80, 255), light=(255, 244, 220, 240)):
    pxs = [(x * S, y * S) for x, y in pts]
    d.line(pxs, fill=dark, width=3)
    d.line([(x + S, y + S) for x, y in pxs], fill=light, width=2)
    d.line([(x + S * 0.6, y + S * 1.4) for x, y in pxs[1:-1]], fill=light, width=2)


fault([(370, 565), (405, 538), (448, 518), (490, 506)])
fault([(505, 615), (545, 625), (585, 612), (620, 590)])
fault([(425, 660), (462, 685), (505, 695), (548, 690)])
fault([(530, 468), (548, 482), (572, 505), (585, 520)])


def crater(cx, cy, cr):
    d.ellipse([(cx - cr) * S, (cy - cr) * S, (cx + cr) * S, (cy + cr) * S],
              outline=(196, 176, 140, 210), width=2)
    d.arc([(cx - cr) * S, (cy - cr) * S, (cx + cr) * S, (cy + cr) * S], 70, 235,
          fill=(172, 148, 110, 200), width=3)


crater(430, 566, 30)
crater(540, 650, 22)
crater(470, 478, 26)
crater(580, 540, 18)
crater(415, 505, 14)
crater(500, 640, 12)

sf.composite(md)

# ---------- 6. front decoration ----------
front = sf.layer()
d = ImageDraw.Draw(Image.fromarray(front))

leaf(d, 368, 692, 24, 11, -0.8, fill=(132, 162, 118, 245), outline=(58, 82, 58, 240))
leaf(d, 598, 700, 24, 11, 0.9, fill=(110, 144, 106, 245), outline=(58, 82, 58, 240))

flower(d, 480, 378, 16, 5, fill=(224, 136, 152, 255), outline=(168, 88, 108, 255))
flower(d, 344, 706, 14, 5, fill=(224, 136, 152, 255), outline=(168, 88, 108, 255))
flower(d, 620, 716, 14, 5, fill=(224, 136, 152, 255), outline=(168, 88, 108, 255))

for sx, sy, sr in [(170, 430, 5), (810, 430, 4), (150, 720, 4), (830, 700, 5),
                   (250, 350, 4), (720, 360, 4), (200, 560, 3), (780, 560, 3),
                   (110, 255, 3), (860, 260, 3), (170, 640, 3), (800, 620, 3)]:
    star4(d, sx, sy, sr)

sf.composite(front)

# ---------- 7. bottom ornament ----------
bot = sf.layer()
d = ImageDraw.Draw(Image.fromarray(bot))

flower(d, 480, 1476, 15, 5, fill=(224, 136, 152, 255), outline=(168, 88, 108, 255))
flower(d, 456, 1482, 10, 5, fill=(238, 182, 172, 250), outline=(176, 106, 118, 240))
flower(d, 504, 1482, 10, 5, fill=(238, 182, 172, 250), outline=(176, 106, 118, 240))
leaf(d, 448, 1468, 16, 7, -2.2, fill=(120, 152, 110, 240), outline=(58, 82, 58, 235))
leaf(d, 512, 1468, 16, 7, 2.2, fill=(120, 152, 110, 240), outline=(58, 82, 58, 235))

tendril(d, 365, 1498, 190, 12, color=(128, 154, 112, 210))
tendril(d, 595, 1498, 170, 12, color=(128, 154, 112, 210))

sf.composite(bot)

# ---------- 8. double frame ----------
frame = sf.layer()
d = ImageDraw.Draw(Image.fromarray(frame))
gold = (168, 134, 88, 255)
d.rectangle([16 * S, 16 * S, (W - 16) * S, (H - 16) * S], outline=gold, width=4)
d.rectangle([26 * S, 26 * S, (W - 26) * S, (H - 26) * S], outline=(168, 134, 88, 170), width=2)


def corner_curl(cx, cy, ang):
    pts = []
    for i in range(46):
        t = i / 45
        r = 34 * (0.25 + 0.75 * t)
        a = math.radians(ang) + t * 1.6
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.line([(x * S, y * S) for x, y in pts], fill=(168, 134, 88, 210), width=3)


corner_curl(44, 44, 45)
corner_curl(W - 44, 44, 135)
corner_curl(44, H - 44, -45)
corner_curl(W - 44, H - 44, -135)

for cx, cy, th in [(120, 60, 0.6), (W - 120, 60, -0.6), (120, H - 60, 1.2), (W - 120, H - 60, -1.2)]:
    leaf(d, cx, cy, 16, 7, th, fill=(140, 166, 122, 220), outline=(58, 82, 58, 210))

sf.composite(frame)

# ---------- 9. text ----------
q_lines = sf.wrap(Q_EN, family="serif", size=30, max_w=700)
qt_lines = sf.wrap(Q_ZH, family="cjk-sc", size=20, max_w=700)
f_lines = sf.wrap(F_EN, family="serif", size=28, max_w=720)
ft_lines = sf.wrap(F_ZH, family="cjk-sc", size=21, max_w=720)

y = 174
for line in q_lines:
    box = sf.text(CX, y, line, family="serif", size=30, fill=(60, 68, 58),
                  anchor="mt", role="quote", max_w=700)
    y = box.bottom + 16

y += 4
for line in qt_lines:
    box = sf.text(CX, y, line, family="cjk-sc", size=20, fill=(122, 120, 96),
                  anchor="mt", role="meta", max_w=700)
    y = box.bottom + 6

fy = 935
for line in f_lines:
    box = sf.text(130, fy, line, family="serif", size=28, fill=(62, 70, 60),
                  anchor="lt", role="body", max_w=720)
    fy = box.bottom + 10

fy += 14
for line in ft_lines:
    box = sf.text(130, fy, line, family="cjk-sc", size=21, fill=(108, 114, 94),
                  anchor="lt", role="meta", max_w=720)
    fy = box.bottom + 6

sf.serial(434, 1502, SERIAL, family="serif", size=19, fill=(140, 104, 60),
          anchor="rm", role="meta")
sf.datestamp(526, 1502, DATE, family="serif", size=19, fill=(140, 104, 60),
             anchor="lm", role="meta")

sf.save(OUT_PATH)
