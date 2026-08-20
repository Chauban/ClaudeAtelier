import numpy as np
from PIL import Image, ImageDraw
from atelier_canvas import Surface

# ---------------- 画布 ----------------
W, H = 1000, 1620
sf = Surface(W, H, scale=2, bg=(238, 226, 199))
sf.frame(70, 60, 860, 1500)

S2 = 2
def P(*pts):
    return [(int(S2 * p[0]), int(S2 * p[1])) for p in pts]

INK   = (88, 63, 40, 255)    # 深墨棕
INKL  = (126, 94, 60, 255)   # 较浅的棕
ACC   = (138, 60, 46, 255)   # 砖红点缀
TXT   = (72, 50, 34)

# ---------------- 背景：做旧纸（量化渐晕，保持色板克制） ----------------
lay = sf.layer()
base = np.array([238, 226, 199], dtype=np.float64)
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
dist = np.sqrt(((xx - 0.5) * 1.18) ** 2 + ((yy - 0.46) * 1.02) ** 2) / 0.92
vig = np.clip(dist, 0, 1)
vig = np.round(vig * 5) / 5
mult = 1.0 - 0.20 * vig
lay[..., 0] = np.clip(base[0] * mult, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(base[1] * mult, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(base[2] * mult, 0, 255).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# 纸纤维与旧斑
rng = np.random.default_rng(7)
tex = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
td = ImageDraw.Draw(tex)
for _ in range(60):
    x0 = int(rng.integers(0, sf.W)); y0 = int(rng.integers(0, sf.H))
    ang = float(rng.uniform(0, np.pi))
    ln = float(rng.integers(8, 28))
    x1 = int(x0 + ln * np.cos(ang)); y1 = int(y0 + ln * np.sin(ang))
    td.line([x0, y0, x1, y1], fill=(202, 182, 144, 30), width=1)
for _ in range(8):
    x = int(rng.integers(0, sf.W)); y = int(rng.integers(0, sf.H))
    td.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(178, 150, 110, 50))
for _ in range(2):
    bx = int(rng.integers(180, sf.W - 180)); by = int(rng.integers(180, sf.H - 180))
    br = int(rng.integers(160, 260))
    td.ellipse([bx - br, by - br, bx + br, by + br], fill=(176, 142, 98, 20))
sf.composite(tex)

# ---------------- 主视觉：解剖图版 ----------------
vis = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(vis)

# 解剖盘
d.ellipse([S2 * 160, S2 * 190, S2 * 840, S2 * 850], outline=INKL, width=2)
d.ellipse([S2 * 172, S2 * 202, S2 * 828, S2 * 838], outline=(126, 94, 60, 110), width=1)

# 盘内点状阴影
rng2 = np.random.default_rng(11)
for _ in range(110):
    a = float(rng2.uniform(0.1, np.pi - 0.1))
    rr = float(rng2.uniform(24, 280))
    x = 500 + rr * np.cos(a)
    y = 540 + rr * np.sin(a) * 0.92
    r = int(rng2.integers(2, 4))
    d.ellipse([S2 * (x - r), S2 * (y - r), S2 * (x + r), S2 * (y + r)], fill=(88, 63, 40, 70))

# 十字测量标
def crosshair(dr, x, y, half=40, color=INKL):
    dr.line(P((x - half, y), (x + half, y)), fill=color, width=2)
    dr.line(P((x, y - half), (x, y + half)), fill=color, width=2)
    off = 8
    dr.line(P((x + half - 10, y - off), (x + half, y - off)), fill=color, width=2)
    dr.line(P((x + half - 10, y + off), (x + half, y + off)), fill=color, width=2)
    dr.line(P((x - half + 10, y - off), (x - half, y - off)), fill=color, width=2)
    dr.line(P((x - half + 10, y + off), (x - half, y + off)), fill=color, width=2)
    dr.line(P((x - off, y - half + 10), (x - off, y - half)), fill=color, width=2)
    dr.line(P((x + off, y - half + 10), (x + off, y - half)), fill=color, width=2)
    dr.line(P((x - off, y + half - 10), (x - off, y + half)), fill=color, width=2)
    dr.line(P((x + off, y + half - 10), (x + off, y + half)), fill=color, width=2)

crosshair(d, 118, 150, 40)
crosshair(d, 882, 150, 40)
crosshair(d, 118, 1490, 36)
crosshair(d, 882, 1490, 36)

# 顶部标签间的细线
d.line(P((300, 88), (700, 88)), fill=(126, 94, 60, 150), width=1)

# ---------------- 标本瓶 ----------------
# 瓶塞
d.polygon(P((467, 262), (533, 262), (545, 300), (455, 300)), fill=(166, 124, 82, 255), outline=INK)
# 瓶口
d.rectangle([S2 * 456, S2 * 300, S2 * 544, S2 * 318], fill=(238, 226, 199, 255), outline=INK)
# 瓶颈
d.line(P((444, 318), (444, 388)), fill=INK, width=3)
d.line(P((556, 318), (556, 388)), fill=INK, width=3)
d.line(P((444, 388), (556, 388)), fill=INK, width=3)
# 瓶肩
d.polygon(P((330, 448), (670, 448), (612, 400), (388, 400)), outline=INK, width=3)
# 瓶身
d.rounded_rectangle([S2 * 330, S2 * 400, S2 * 670, S2 * 790], radius=S2 * 55,
                    outline=INK, width=3, fill=(242, 230, 206, 50))

# 液体
pts = []
for i in range(25):
    wx = 342 + i * (658 - 342) / 24
    wy = 626 + 3.5 * np.sin(i * 0.9)
    pts.append((wx, wy))
poly = pts + [(658, 786), (342, 786)]
d.polygon([(S2 * x, S2 * y) for x, y in poly], fill=(204, 178, 132, 78))
d.line([(S2 * x, S2 * y) for x, y in pts], fill=INKL, width=2)

# 气泡
for bx, by, br in [(390, 690, 9), (430, 736, 6), (600, 700, 8), (630, 660, 6), (360, 660, 7), (650, 740, 6)]:
    d.ellipse([S2 * (bx - br), S2 * (by - br), S2 * (bx + br), S2 * (by + br)],
              outline=(252, 246, 230, 150), width=2)

# 玻璃高光
d.arc([S2 * 348, S2 * 410, S2 * 652, S2 * 780], start=135, end=212, fill=(253, 248, 232, 105), width=8)
d.arc([S2 * 450, S2 * 410, S2 * 650, S2 * 600], start=300, end=350, fill=(253, 248, 232, 60), width=5)

# ---------------- 瓶内：標本中的殿堂 ----------------
# 三角楣
d.line(P((392, 476), (608, 476)), fill=INK, width=3)
d.line(P((392, 476), (500, 422)), fill=INK, width=3)
d.line(P((608, 476), (500, 422)), fill=INK, width=3)
# 楣饰
for tx in range(404, 597, 24):
    d.line(P((tx, 476), (tx, 468)), fill=INK, width=2)
# 横梁
d.line(P((382, 478), (618, 478)), fill=INK, width=4)
# 柱子
for cx in (418, 478, 522, 582):
    d.line(P((cx - 5, 478), (cx - 5, 640)), fill=INK, width=3)
    d.line(P((cx + 5, 478), (cx + 5, 640)), fill=INK, width=3)
    d.line(P((cx - 9, 478), (cx + 9, 478)), fill=INK, width=3)
    d.line(P((cx - 9, 640), (cx + 9, 640)), fill=INK, width=3)
    d.line(P((cx - 5, 558), (cx + 5, 558)), fill=INK, width=2)
# 基座
d.rectangle([S2 * 380, S2 * 640, S2 * 620, S2 * 684], outline=INK, width=3)
d.line(P((380, 662), (620, 662)), fill=INK, width=2)
# 台阶
d.line(P((392, 684), (608, 684)), fill=INK, width=3)
d.line(P((402, 712), (598, 712)), fill=INK, width=3)
d.line(P((414, 740), (586, 740)), fill=INK, width=3)

# 小人（瓶内样本）
def stick(dr, x, y, h, color=INK, lw=1):
    r = max(3, int(h * 0.14))
    dr.ellipse([S2 * (x - r), S2 * (y - r), S2 * (x + r), S2 * (y + r)], outline=color, width=S2 * lw)
    dr.line(P((x, y + r), (x, y + int(h * 0.55))), fill=color, width=S2 * lw)
    dr.line(P((x, y + int(h * 0.30)), (x - int(h * 0.42), y + int(h * 0.18))), fill=color, width=S2 * lw)
    dr.line(P((x, y + int(h * 0.30)), (x + int(h * 0.42), y + int(h * 0.18))), fill=color, width=S2 * lw)
    dr.line(P((x, y + int(h * 0.55)), (x - int(h * 0.38), y + h)), fill=color, width=S2 * lw)
    dr.line(P((x, y + int(h * 0.55)), (x + int(h * 0.38), y + h)), fill=color, width=S2 * lw)

for sx in (428, 470, 530, 572):
    stick(d, sx, 752, 34)

# 瓶外排队的人（虚线行伍）
for i in range(7):
    qx0 = 176 + i * 12
    d.line(P((qx0, 800), (qx0 + 5, 800)), fill=INKL, width=2)
stick(d, 212, 786, 34)
stick(d, 252, 786, 34)

# ---------------- 解剖工具與注記 ----------------
# 左侧引线
d.line(P((500, 422), (292, 430)), fill=INKL, width=2)
d.line(P((292, 430), (272, 452)), fill=INKL, width=2)
d.ellipse([S2 * 262, S2 * 444, S2 * 286, S2 * 468], fill=(238, 226, 199, 255), outline=ACC, width=3)
d.ellipse([S2 * 271, S2 * 453, S2 * 277, S2 * 459], fill=ACC)
# 右侧引线
d.line(P((500, 422), (730, 404)), fill=ACC, width=2)
d.polygon(P((730, 404), (744, 399), (740, 413)), fill=ACC)

# 解剖刀
d.line(P((166, 636), (246, 616)), fill=INK, width=9)
d.ellipse([S2 * (174 - 3), S2 * (630 - 3), S2 * (174 + 3), S2 * (630 + 3)], outline=INK, width=2)
d.line(P((246, 606), (254, 628)), fill=INK, width=4)
d.polygon(P((254, 612), (312, 588), (308, 628), (252, 630)), fill=(136, 102, 66, 255), outline=INK)

# 放大镜
d.ellipse([S2 * 738, S2 * 556, S2 * 798, S2 * 616], outline=INK, width=5)
d.line(P((748, 586), (788, 586)), fill=(250, 244, 228, 110), width=3)
d.line(P((768, 566), (768, 606)), fill=(250, 244, 228, 90), width=3)
d.line(P((798, 616), (832, 652)), fill=INK, width=10)
d.line(P((816, 636), (826, 628)), fill=ACC, width=3)

# ⊕ 注記符
def plus_circle(dr, x, y, r, color, lw=2):
    dr.ellipse([S2 * (x - r), S2 * (y - r), S2 * (x + r), S2 * (y + r)], outline=color, width=S2 * lw)
    dr.line(P((x - int(r * 0.68), y), (x + int(r * 0.68), y)), fill=color, width=2)
    dr.line(P((x, y - int(r * 0.68)), (x, y + int(r * 0.68))), fill=color, width=2)

plus_circle(d, 258, 700, 16, ACC)
plus_circle(d, 740, 720, 14, ACC)
plus_circle(d, 726, 250, 12, INKL)
plus_circle(d, 300, 320, 13, INKL)

# 标尺
d.line(P((180, 886), (820, 886)), fill=INKL, width=2)
for i in range(33):
    x = 180 + i * 20
    hgt = 16 if i % 5 == 0 else 8
    d.line(P((x, 886), (x, 886 + hgt)), fill=INKL, width=3 if i % 5 == 0 else 1)

# ---------------- 标本标签框（编号与日期） ----------------
d.rectangle([S2 * 70, S2 * 64, S2 * 300, S2 * 112], fill=(246, 236, 214, 255), outline=INK, width=2)
d.rectangle([S2 * 75, S2 * 69, S2 * 295, S2 * 107], outline=(126, 94, 60, 140), width=1)
d.ellipse([S2 * 82, S2 * 70, S2 * 94, S2 * 82], fill=ACC)
d.ellipse([S2 * 276, S2 * 70, S2 * 288, S2 * 82], fill=ACC)

d.rectangle([S2 * 700, S2 * 64, S2 * 930, S2 * 112], fill=(246, 236, 214, 255), outline=INK, width=2)
d.rectangle([S2 * 705, S2 * 69, S2 * 925, S2 * 107], outline=(126, 94, 60, 140), width=1)
d.ellipse([S2 * 712, S2 * 70, S2 * 724, S2 * 82], fill=ACC)
d.ellipse([S2 * 906, S2 * 70, S2 * 918, S2 * 82], fill=ACC)

# 底部图版花饰
d.line(P((260, 1452), (740, 1452)), fill=INKL, width=2)
d.polygon(P((500, 1442), (514, 1452), (500, 1462), (486, 1452)), fill=ACC)

sf.composite(vis)

# ---------------- 文字层 ----------------
sf.datestamp(185, 88, DATE, family="serif", size=20, fill=TXT, anchor="mt", role="meta")
sf.serial(815, 88, SERIAL, family="serif", size=20, fill=TXT, anchor="mt", role="meta")

box_q = sf.text(500, 962, QUOTE, family="serif-cjk", size=33, fill=TXT,
                anchor="mt", role="quote", max_w=860, line_gap=0.4)

sf.text(500, box_q.bottom + 52, FACT, family="serif-cjk", size=28, fill=TXT,
        anchor="mt", role="body", max_w=860, line_gap=0.5)

sf.save(OUT_PATH)
