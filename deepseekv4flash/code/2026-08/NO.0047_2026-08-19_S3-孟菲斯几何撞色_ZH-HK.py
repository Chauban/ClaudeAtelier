from atelier_canvas import Surface
import math
import random
from PIL import Image, ImageDraw

W, H = 1000, 1320
SC = 2
sf = Surface(W, H, scale=SC, bg=(240, 234, 220))


def LX(v):
    return int(round(v * SC))


def LY(v):
    return int(round(v * SC))


TEA = (0, 176, 168)
YES = (247, 214, 64)
RED = (228, 62, 50)
BLU = (36, 54, 166)
PNK = (255, 120, 160)
GRN = (4, 159, 130)
BGC = (240, 234, 220)
BLK = (20, 20, 20)
WHT = (255, 255, 255)

random.seed(47)

img = Image.new("RGBA", (W * SC, H * SC), BGC + (255,))
d = ImageDraw.Draw(img)


def rect(x0, y0, x1, y1, fill, border=None, bw=6):
    if border is not None:
        d.rectangle([LX(x0) - LX(bw), LY(y0) - LY(bw),
                     LX(x1) + LX(bw), LY(y1) + LY(bw)], fill=border)
    d.rectangle([LX(x0), LY(y0), LX(x1), LY(y1)], fill=fill)


def disc(cx, cy, r, fill):
    cxp, cyp = LX(cx), LY(cy)
    rr = LX(r)
    d.ellipse([cxp - rr - 7, cyp - rr - 7, cxp + rr + 7, cyp + rr + 7], fill=BLK)
    d.ellipse([cxp - rr, cyp - rr, cxp + rr, cyp + rr], fill=fill)


# 水磨石碎点
for _ in range(240):
    px = random.randint(0, W * SC)
    py = random.randint(0, H * SC)
    pr = random.randint(2, 7)
    pc = random.choice([RED, BLU, PNK, GRN, YES, TEA, BLK])
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=pc)

# 顶部色条
rect(0, 0, 340, 70, TEA, BLK, 5)
red_pts = [(LX(720), 0)]
x = 720
while x < 1000:
    red_pts.append((LX(x), LY(120)))
    red_pts.append((LX(min(x + 30, 1000)), LY(142)))
    x += 60
red_pts.append((LX(1000), LY(120)))
red_pts.append((LX(1000), 0))
d.polygon(red_pts, fill=RED, outline=BLK, width=LX(5))

for a in (15, 45, 75, 105):
    rad = math.radians(a)
    x0, y0 = LX(715), LY(128)
    x1 = x0 + int(140 * SC * math.cos(rad) * 0.6)
    y1 = y0 + int(140 * SC * math.sin(rad) * 0.9)
    d.line([x0, y0, x1, y1], fill=BLK, width=LX(4))

rect(100, 110, 300, 174, YES, BLK, 6)
rect(330, 96, 570, 158, BLU, BLK, 6)

# 中部几何
rect(0, 250, 46, 430, BLU, BLK, 5)
rect(954, 290, 1000, 490, PNK, BLK, 5)

d.polygon([(LX(735), LY(285)), (LX(835), LY(285)), (LX(785), LY(368))],
          fill=BLU, outline=BLK, width=LX(5))
disc(835, 400, 55, PNK)
rect(700, 478, 748, 526, GRN, BLK, 6)
disc(915, 518, 24, YES)
d.ellipse([LX(756), LY(558), LX(780), LY(582)], fill=BLK)
disc(450, 195, 12, YES)
rect(110, 296, 568, 304, RED, None)

# QUOTE 衬块（位置下移，容纳三行大字）
rect(84, 400, 686, 560, BLK)
rect(90, 406, 680, 554, YES)

# FACT 白块
rect(64, 580, 936, 1080, BLK)
rect(70, 586, 100, 1074, YES)
rect(100, 586, 930, 1074, WHT)
d.ellipse([LX(110), LY(598), LX(130), LY(618)], fill=BLK)

# 底部波浪线
wv = []
for x in range(60, 941, 4):
    y = 1090 + 12 * math.sin(x / 38.0) + 8 * math.sin(x / 13.0)
    wv.append((LX(x), LY(y)))
d.line(wv, fill=BLK, width=LX(7), joint="curve")

# 红色锯齿带
zpts = []
x = -40
while x <= 1040:
    zpts.append((LX(x), LY(1108)))
    zpts.append((LX(x + 40), LY(1148)))
    x += 80
zpts.append((LX(1040), LY(1108)))
d.polygon(zpts, fill=RED, outline=BLK, width=LX(4))

# 绿方格
rect(110, 1165, 230, 1275, GRN, BLK, 6)
d.line([LX(110), LY(1200), LX(230), LY(1200)], fill=WHT, width=LX(4))
d.line([LX(110), LY(1235), LX(230), LY(1235)], fill=WHT, width=LX(4))
d.line([LX(145), LY(1165), LX(145), LY(1275)], fill=WHT, width=LX(4))
d.line([LX(180), LY(1165), LX(180), LY(1275)], fill=WHT, width=LX(4))

# 蓝半圆（大圆被画布底部裁剪）
d.ellipse([LX(240), LY(1150), LX(900), LY(1810)], fill=BLU, outline=BLK, width=LX(8))
disc(570, 1260, 24, YES)
d.ellipse([LX(530), LY(1210), LX(550), LY(1230)], fill=WHT)
d.ellipse([LX(610), LY(1240), LX(628), LY(1258)], fill=WHT)

# 粉圆环
cx, cy, rr = LX(885), LY(1200), LX(42)
d.ellipse([cx - rr - 4, cy - rr - 4, cx + rr + 4, cy + rr + 4], outline=BLK, width=LX(3))
d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=PNK, width=LX(14))

# 黄三角（叠在蓝半圆上）
d.polygon([(LX(470), LY(1295)), (LX(552), LY(1295)), (LX(511), LY(1223))],
          fill=YES, outline=BLK, width=LX(5))

# 小红方块
rect(905, 1270, 941, 1306, RED, BLK, 5)

# 散落黑点
for (sx, sy, sr) in [(70, 1250, 12), (60, 1290, 8), (950, 1280, 10),
                     (300, 1210, 8), (700, 1280, 10), (420, 1230, 7)]:
    d.ellipse([LX(sx - sr), LY(sy - sr), LX(sx + sr), LY(sy + sr)], fill=BLK)

# 小十字
for (cx2, cy2, s2) in [(360, 1290, 12), (620, 1280, 9), (60, 1180, 10)]:
    d.line([LX(cx2 - s2), LY(cy2), LX(cx2 + s2), LY(cy2)], fill=BLK, width=LX(5))
    d.line([LX(cx2), LY(cy2 - s2), LX(cx2), LY(cy2 + s2)], fill=BLK, width=LX(5))

sf.composite(img)

# 文字层
sf.frame(70, 70, 860, 1180)

sf.serial(200, 146, SERIAL, family="sans", size=30, bold=True,
          fill=(20, 20, 20), anchor="mm", role="meta")
sf.datestamp(450, 127, DATE, family="sans", size=24, bold=True,
             fill=(255, 255, 255), anchor="mm", role="meta")

# 三行金句：用 box.bottom 串接，避免重叠
q1 = sf.text(110, 215, "一杯劣酒，", family="cjk-hk", size=60,
             fill=(20, 20, 20), anchor="lt", role="quote", bold=True)
q2 = sf.text(205, q1.bottom + 14, "一場血戰，", family="cjk-hk", size=72,
             fill=(20, 20, 20), anchor="lt", role="quote", bold=True)
q3 = sf.text(118, q2.bottom + 14, "四百七十年找數。", family="cjk-hk", size=54,
             fill=(20, 20, 20), anchor="lt", role="quote", bold=True)

# 冷知识正文（白块内，起点固定）
sf.text(130, 622, FACT, family="cjk-hk", size=30, fill=(25, 25, 25),
        anchor="lt", role="body", max_w=780, line_gap=0.25)

sf.save(OUT_PATH)
