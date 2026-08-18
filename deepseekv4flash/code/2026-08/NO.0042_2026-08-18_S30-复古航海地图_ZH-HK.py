import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

# ================= 画布 =================
LW, LH = 1000, 1700
sf = Surface(LW, LH, scale=2, bg=(216, 198, 162))
sf.frame(90, 90, 820, 1520)

def P(v):
    return int(round(v * 2))

rng = np.random.default_rng(20260818)
prng = random.Random(20260818)

# ================= 背景纹理 =================
noise = rng.normal(0, 10, (sf.H, sf.W))
lv = np.clip(noise + 128, 0, 255).astype(np.uint8)
nl = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
nl[..., 0] = lv
nl[..., 1] = lv
nl[..., 2] = lv
nl[..., 3] = 14
sf.composite(nl, mode="normal")

paper = rng.standard_normal((sf.H // 10, sf.W // 10)) * 16
pimg = Image.fromarray(np.clip(paper + 128, 0, 255).astype(np.uint8), "L")
pimg = pimg.resize((sf.W, sf.H), Image.BILINEAR).convert("RGBA")
pa = np.asarray(pimg)
pl = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
pl[..., 0] = pa[..., 0]
pl[..., 1] = pa[..., 0]
pl[..., 2] = pa[..., 0]
pl[..., 3] = 14
sf.composite(pl, mode="normal")

stain = sf.layer()
simg = Image.fromarray(stain, "RGBA")
sd = ImageDraw.Draw(simg)
for _ in range(6):
    bx = prng.randint(70, 930)
    by = prng.randint(70, 1630)
    rx = prng.randint(70, 200)
    ry = prng.randint(45, 130)
    sd.ellipse([P(bx - rx), P(by - ry), P(bx + rx), P(by + ry)], fill=(135, 100, 58, 16))
simg = simg.filter(ImageFilter.GaussianBlur(45))
sf.composite(simg, mode="normal")

yy, xx = np.mgrid[0:sf.H, 0:sf.W]
cxv, cyv = sf.W / 2.0, sf.H * 0.44
dist = np.sqrt((xx - cxv) ** 2 + (yy - cyv) ** 2)
dist = dist / np.sqrt(sf.W ** 2 + sf.H ** 2)
vig = np.clip((dist - 0.30) / 0.45, 0.0, 1.0) ** 1.5
vn = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
vn[..., 0] = 66
vn[..., 1] = 49
vn[..., 2] = 28
vn[..., 3] = (vig * 80).astype(np.uint8)
sf.composite(vn, mode="normal")

# ================= 装饰主层 =================
dec = sf.layer()
dimg = Image.fromarray(dec, "RGBA")
d = ImageDraw.Draw(dimg)

# 经纬网格线
grid_col = (150, 118, 82, 52)
for gy in (110, 280, 450, 620, 790, 960, 1130, 1300, 1470, 1600):
    d.line([P(55), P(gy), P(945), P(gy)], fill=grid_col, width=P(1))
for gx in (110, 270, 430, 590, 750, 910):
    d.line([P(gx), P(55), P(gx), P(1650)], fill=grid_col, width=P(1))

# 罗盘放射线
ray_col = (130, 100, 65, 24)
for i in range(16):
    th = i * math.pi / 8.0
    dx0, dy0 = math.cos(th), math.sin(th)
    d.line([P(500 + dx0 * 20), P(1200 + dy0 * 20),
            P(500 + dx0 * 680), P(1200 + dy0 * 680)],
           fill=ray_col, width=P(1))

def in_avoid(x, y, rects):
    for (ax0, ay0, ax1, ay1) in rects:
        if ax0 <= x <= ax1 and ay0 <= y <= ay1:
            return True
    return False

# 金句卷轴区域（装饰要避开，保证背景干净）
avoid_quote = [(100, 104, 900, 416)]
# FACT 正文区域（避开，避免星点压在文字上）
avoid_fact = [(160, 470, 900, 760)]

# 上部星点：卷轴两侧及上下窄带
star_pts = []
guard = 0
while guard < 3000 and sum(1 for p in star_pts if p[1] < 480) < 22:
    guard += 1
    x = prng.uniform(55, 945)
    y = prng.uniform(52, 476)
    if not in_avoid(x, y, [avoid_quote[0], (160, 460, 900, 480)]):
        star_pts.append((x, y))

# 中下部星点：避开 FACT 区域与罗盘主体
guard = 0
while guard < 5000 and sum(1 for p in star_pts if p[1] >= 760) < 34:
    guard += 1
    x = prng.uniform(55, 945)
    y = prng.uniform(760, 1545)
    if (x - 500) ** 2 + (y - 1200) ** 2 > 285 ** 2:
        star_pts.append((x, y))

# 边缘补一些
for _ in range(8):
    star_pts.append((prng.uniform(62, 938), prng.uniform(448, 472)))
for _ in range(6):
    star_pts.append((prng.uniform(60, 940), prng.uniform(64, 100)))
for _ in range(6):
    star_pts.append((prng.uniform(60, 940), prng.uniform(1520, 1540)))

for (sx, sy) in star_pts:
    tt = prng.random()
    if tt < 0.38:
        r = prng.uniform(2.2, 4.2)
        d.ellipse([P(sx - r), P(sy - r), P(sx + r), P(sy + r)], fill=(42, 38, 32, 190))
    elif tt < 0.76:
        r = prng.uniform(2.2, 4.2)
        d.ellipse([P(sx - r), P(sy - r), P(sx + r), P(sy + r)], fill=(196, 148, 62, 210))
    else:
        r = prng.uniform(2.6, 4.6)
        d.ellipse([P(sx - r), P(sy - r), P(sx + r), P(sy + r)], fill=(196, 148, 62, 220))
        d.ellipse([P(sx - r - 2.5), P(sy - r - 2.5), P(sx + r + 2.5), P(sy + r + 2.5)],
                  outline=(40, 36, 32, 170), width=P(1))

# 亮星光芒（避开卷轴）
bright_pts = [(128, 450), (872, 452), (158, 866), (842, 886), (158, 96), (842, 953), (500, 1558)]
for (bx, by) in bright_pts:
    col = (78, 58, 38, 200)
    d.line([P(bx - 15), P(by), P(bx + 15), P(by)], fill=col, width=P(1))
    d.line([P(bx), P(by - 15), P(bx), P(by + 15)], fill=col, width=P(1))
    d.ellipse([P(bx - 3.5), P(by - 3.5), P(bx + 3.5), P(by + 3.5)], fill=col)

# 星座连线（左右两组，FACT 下方）
const1 = [(120, 908), (158, 892), (198, 906), (236, 880), (276, 894), (252, 858), (292, 842)]
const2 = [(880, 908), (842, 892), (802, 906), (764, 880), (724, 894), (748, 858), (708, 842)]
for pts in (const1, const2):
    for i in range(len(pts) - 1):
        d.line([P(pts[i][0]), P(pts[i][1]), P(pts[i + 1][0]), P(pts[i + 1][1])],
               fill=(92, 66, 40, 110), width=P(1))
    for (px, py) in pts:
        d.ellipse([P(px - 3), P(py - 3), P(px + 3), P(py + 3)], fill=(70, 50, 32, 210))

# ================= 金句卷轴画框 =================
qx0, qx1, qy_top, qy_bot = 140, 860, 112, 408
# 卷轴内部浅色底
d.rectangle([P(qx0), P(qy_top + 24), P(qx1), P(qy_bot - 24)], fill=(229, 212, 176, 255))
# 画框边线
d.rectangle([P(qx0 + 12), P(qy_top + 36), P(qx1 - 12), P(qy_bot - 36)],
            outline=(120, 95, 60, 70), width=P(1))
# 上轴
d.rectangle([P(qx0), P(qy_top), P(qx1), P(qy_top + 24)], fill=(114, 77, 45, 255))
for j in range(qx0 + 20, qx1 + 1, 30):
    d.line([P(j), P(qy_top + 2), P(j), P(qy_top + 22)], fill=(88, 58, 33, 90), width=P(1))
d.rectangle([P(qx0), P(qy_top), P(qx1), P(qy_top + 24)], outline=(80, 52, 30, 160), width=P(1))
d.ellipse([P(qx0 - 20), P(qy_top - 4), P(qx0 + 8), P(qy_top + 28)], fill=(92, 60, 34, 255))
d.ellipse([P(qx1 - 8), P(qy_top - 4), P(qx1 + 20), P(qy_top + 28)], fill=(92, 60, 34, 255))
# 下轴
d.rectangle([P(qx0), P(qy_bot - 24), P(qx1), P(qy_bot)], fill=(114, 77, 45, 255))
for j in range(qx0 + 20, qx1 + 1, 30):
    d.line([P(j), P(qy_bot - 22), P(j), P(qy_bot - 2)], fill=(88, 58, 33, 90), width=P(1))
d.rectangle([P(qx0), P(qy_bot - 24), P(qx1), P(qy_bot)], outline=(80, 52, 30, 160), width=P(1))
d.ellipse([P(qx0 - 20), P(qy_bot - 28), P(qx0 + 8), P(qy_bot + 4)], fill=(92, 60, 34, 255))
d.ellipse([P(qx1 - 8), P(qy_bot - 28), P(qx1 + 20), P(qy_bot + 4)], fill=(92, 60, 34, 255))

# ================= 罗盘玫瑰 =================
cx0, cy0, R = 500, 1200, 205
darkb = (48, 66, 96, 255)
redb = (150, 78, 46, 255)
midb = (116, 90, 58, 255)
for i in range(16):
    th = -math.pi / 2 + i * (2 * math.pi / 16)
    if i % 4 == 0:
        L, cc, ww = R, darkb, 30.0
    elif i % 2 == 0:
        L, cc, ww = R * 0.84, redb, 24.0
    else:
        L, cc, ww = R * 0.66, midb, 19.0
    dx, dy = math.cos(th), math.sin(th)
    nx, ny = -dy, dx
    k = L / R
    aw = ww * k
    ox, oy = cx0 + dx * L, cy0 + dy * L
    ax, ay = cx0 + dx * L * 0.40 + nx * aw, cy0 + dy * L * 0.40 + ny * aw
    bx, by = cx0 + dx * L * 0.40 - nx * aw, cy0 + dy * L * 0.40 - ny * aw
    ix, iy = cx0 - dx * L * 0.16, cy0 - dy * L * 0.16
    d.polygon([P(ox), P(oy), P(ax), P(ay), P(ix), P(iy), P(bx), P(by)], fill=cc)

d.ellipse([P(cx0 - R - 22), P(cy0 - R - 22), P(cx0 + R + 22), P(cy0 + R + 22)],
          outline=(96, 70, 44, 130), width=P(2))
d.ellipse([P(cx0 - R - 32), P(cy0 - R - 32), P(cx0 + R + 32), P(cy0 + R + 32)],
          outline=(96, 70, 44, 70), width=P(1))
d.ellipse([P(cx0 - 18), P(cy0 - 18), P(cx0 + 18), P(cy0 + 18)], fill=(92, 66, 40, 255))
d.ellipse([P(cx0 - 7), P(cy0 - 7), P(cx0 + 7), P(cy0 + 7)], fill=(238, 222, 186, 255))
d.ellipse([P(cx0 - 3), P(cy0 - 3), P(cx0 + 3), P(cy0 + 3)], fill=(60, 45, 30, 255))

# 底部装饰线
d.line([P(220), P(1462), P(780), P(1462)], fill=(92, 66, 40, 70), width=P(1))

# 外框
ink = (92, 66, 40, 255)
d.rectangle([P(50), P(50), P(950), P(1650)], outline=ink, width=P(3))
d.rectangle([P(62), P(62), P(938), P(1638)], outline=(92, 66, 40, 110), width=P(1))
for (qx, qy) in ((50, 50), (950, 50), (50, 1650), (950, 1650)):
    d.polygon([P(qx), P(qy - 10), P(qx + 10), P(qy),
               P(qx), P(qy + 10), P(qx - 10), P(qy)], fill=ink)

# 顶部装饰线
d.line([P(170), P(92), P(830), P(92)], fill=(92, 66, 40, 150), width=P(2))
d.line([P(170), P(99), P(830), P(99)], fill=(92, 66, 40, 60), width=P(1))
d.polygon([P(500), P(82), P(512), P(96), P(500), P(110), P(488), P(96)], fill=(92, 66, 40, 150))

# 中部隔线（FACT 上方）
d.line([P(180), P(436), P(820), P(436)], fill=(92, 66, 40, 130), width=P(2))
d.line([P(180), P(443), P(820), P(443)], fill=(92, 66, 40, 55), width=P(1))

# 底部比例尺（在地图外框内，装饰性）
d.line([P(92), P(1578), P(272), P(1578)], fill=(92, 66, 40, 170), width=P(2))
d.line([P(92), P(1570), P(114), P(1570)], fill=(92, 66, 40, 170), width=P(2))
d.line([P(250), P(1570), P(272), P(1570)], fill=(92, 66, 40, 170), width=P(2))
d.line([P(728), P(1578), P(908), P(1578)], fill=(92, 66, 40, 170), width=P(2))
d.line([P(728), P(1570), P(750), P(1570)], fill=(92, 66, 40, 170), width=P(2))
d.line([P(886), P(1570), P(908), P(1570)], fill=(92, 66, 40, 170), width=P(2))

sf.composite(dimg, mode="normal")

# ================= FACT 正文与左侧竖线 =================
fact_lines = sf.wrap(FACT, "cjk-hk", 30, 700)
line_h = 52
fy = 480
f_top = fy
for _ in fact_lines:
    fy += line_h
f_bottom = fy - line_h + 44

flay = sf.layer()
fimg = Image.fromarray(flay, "RGBA")
fd = ImageDraw.Draw(fimg)
fd.line([P(150), P(f_top - 8), P(150), P(f_bottom)], fill=(92, 66, 40, 150), width=P(2))
fd.line([P(158), P(f_top - 8), P(158), P(f_bottom)], fill=(92, 66, 40, 55), width=P(1))
fd.line([P(150), P(f_top - 8), P(168), P(f_top - 8)], fill=(92, 66, 40, 150), width=P(2))
fd.line([P(150), P(f_bottom), P(168), P(f_bottom)], fill=(92, 66, 40, 150), width=P(2))
sf.composite(fimg, mode="normal")

fy = 480
for fln in fact_lines:
    sf.text(180, fy, fln, family="cjk-hk", size=30, fill=(70, 52, 32),
            anchor="lt", role="body", line_gap=0)
    fy += line_h

# ================= QUOTE =================
qm = sf.measure("星圖會褪色，", "serif-cjk", 56)
line_h_q = qm[1]
q_total = line_h_q * 2 + 26
q_y0 = 112 + 24 + (296 - q_total) / 2.0

sf.text(500, q_y0, "星圖會褪色，", family="serif-cjk", size=56,
        fill=(56, 42, 28), anchor="mt", role="quote", line_gap=0)
sf.text(500, q_y0 + line_h_q + 26, "星空不會。", family="serif-cjk", size=56,
        fill=(56, 42, 28), anchor="mt", role="quote", line_gap=0)

# ================= 编号与日期 =================
sf.serial(94, 1536, SERIAL, family="serif", size=20, fill=(80, 56, 34),
          anchor="lt", role="meta", line_gap=0)
sf.datestamp(906, 1536, DATE, family="serif", size=20, fill=(80, 56, 34),
             anchor="rt", role="meta", line_gap=0)

sf.save(OUT_PATH)
