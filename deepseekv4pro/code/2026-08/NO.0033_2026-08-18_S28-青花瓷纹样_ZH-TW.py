import math
import numpy as np
from atelier_canvas import Surface
from PIL import Image, ImageDraw

W, H = 1000, 1700
bg = (250, 250, 246)
sf = Surface(W, H, scale=2, bg=bg)

INK = (28, 52, 114, 255)
INK2 = (64, 101, 160, 255)
INK3 = (122, 155, 200, 255)
PANEL = (247, 249, 252, 255)
TEXT = (20, 42, 100)
TEXT2 = (64, 101, 160)

lay = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dr = ImageDraw.Draw(lay)

def P(x, y):
    return (int(x * 2), int(y * 2))

def R(x0, y0, x1, y1):
    return [int(x0 * 2), int(y0 * 2), int(x1 * 2), int(y1 * 2)]

def W(v):
    return max(1, int(v * 2))

# ---------- 頂飾帶 ----------
dr.rectangle(R(40, 36, 960, 148), outline=INK, width=W(3))
dr.rectangle(R(55, 52, 945, 132), outline=INK2, width=W(2))
y_mid = 92
for i, x in enumerate(range(78, 930, 52)):
    rad = 16
    col = INK if i % 2 == 0 else INK2
    dr.ellipse([P(x - rad, y_mid - rad), P(x + rad, y_mid + rad)], outline=col, width=W(2))
    if i % 2 == 0:
        dr.ellipse([P(x - 4, y_mid - 4), P(x + 4, y_mid + 4)], fill=INK)
    else:
        dr.polygon([P(x, y_mid - 17), P(x + 8, y_mid), P(x, y_mid + 17), P(x - 8, y_mid)], outline=INK, width=W(2))

# ---------- 中央圓光 ----------
cx, cy = 500, 441
rings = [
    (280, 6, INK),
    (270, 2, INK2),
    (250, 5, INK2),
    (230, 2, INK2),
    (228, 4, INK),
    (218, 2, INK2),
]
for r, wd, col in rings:
    dr.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], outline=col, width=W(wd))

for ang in range(0, 360, 15):
    a = math.radians(ang)
    x = cx + 239 * math.cos(a)
    y = cy + 239 * math.sin(a)
    pr = 8
    dr.ellipse([P(x - pr, y - pr), P(x + pr, y + pr)], outline=INK2, width=W(1))

# ---------- 正文青花板 ----------
dr.rectangle(R(100, 752, 900, 1360), fill=PANEL)
dr.rectangle(R(100, 752, 900, 1360), outline=INK, width=W(5))
dr.rectangle(R(114, 766, 886, 1346), outline=INK2, width=W(2))

corner_angles = {
    (114, 766): (180, 270),
    (886, 766): (270, 360),
    (114, 1346): (90, 180),
    (886, 1346): (0, 90),
}
for (cx0, cy0), (a0, a1) in corner_angles.items():
    for r in (30, 52, 74):
        box = [int((cx0 - r) * 2), int((cy0 - r) * 2), int((cx0 + r) * 2), int((cy0 + r) * 2)]
        dr.arc(box, a0, a1, fill=INK2, width=W(2))
    dr.ellipse([P(cx0 - 3, cy0 - 3), P(cx0 + 3, cy0 + 3)], fill=INK)

# 板內下方蓮花團花
lx, ly = 500, 1235
dr.ellipse([P(lx - 58, ly - 58), P(lx + 58, ly + 58)], outline=INK2, width=W(2))
for ang in range(0, 360, 45):
    a = math.radians(ang)
    px = lx + 42 * math.cos(a)
    py = ly + 42 * math.sin(a)
    dr.ellipse([P(px - 11, py - 15), P(px + 11, py + 15)], outline=INK, width=W(2))
dr.ellipse([P(lx - 16, ly - 16), P(lx + 16, ly + 16)], outline=INK2, width=W(2))
dr.ellipse([P(lx - 5, ly - 5), P(lx + 5, ly + 5)], fill=INK2)

# ---------- 底下海水帶 ----------
dr.rectangle(R(40, 1380, 960, 1512), outline=INK, width=W(3))
dr.rectangle(R(55, 1396, 945, 1496), outline=INK2, width=W(2))
for y0, ph, col in [(1410, 0, INK), (1432, 1, INK2), (1454, 2, INK3), (1476, 3, INK2)]:
    pts = [P(x, y0 + 7 * math.sin((x + ph * 15) / 22.0)) for x in range(70, 931, 8)]
    dr.line(pts, fill=col, width=W(2))

# ---------- 底款框 ----------
dr.rectangle(R(438, 1532, 562, 1612), outline=INK, width=W(3))
dr.rectangle(R(450, 1542, 550, 1604), outline=INK2, width=W(1))

sf.composite(np.asarray(lay), mode="normal", opacity=1.0)

# ---------- 文字 ----------
sf.frame(70, 60, 860, 1570)

sf.text(
    500, 441, QUOTE,
    family="cjk-tc", size=34, fill=TEXT,
    anchor="mm", role="quote",
    max_w=430, line_gap=0.55, allow_overlap=False,
)

sf.text(
    150, 825, FACT,
    family="cjk-tc", size=32, fill=TEXT,
    anchor="lt", role="body",
    max_w=700, line_gap=0.55, allow_overlap=False,
)

sf.serial(
    500, 1556, SERIAL,
    family="sans", size=20, fill=TEXT,
    anchor="mm", role="meta", allow_overlap=False,
)

sf.datestamp(
    500, 1591, DATE,
    family="sans", size=18, fill=TEXT2,
    anchor="mm", role="meta", allow_overlap=False,
)

sf.save(OUT_PATH)
