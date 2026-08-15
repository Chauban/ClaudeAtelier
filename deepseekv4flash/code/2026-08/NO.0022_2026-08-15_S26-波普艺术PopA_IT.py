from atelier_canvas import Surface
from PIL import Image, ImageDraw
import math

W, H = 1000, 1700
sf = Surface(W, H, scale=2, bg=(255, 232, 131))
sf.frame(60, 50, 880, 1600)
S = 2

# ---------- 文本布局计算（先量后画，保证不重叠） ----------
quote_lines = sf.wrap(QUOTE, "sans", 40, 800, bold=True)
quote_heights = [sf.measure(l, "sans", 40, bold=True)[1] for l in quote_lines]
q_text_h = sum(quote_heights) + 8 * max(0, len(quote_lines) - 1)
q_pad = 26
q_bh = q_text_h + q_pad * 2
q_max_w = max(sf.measure(l, "sans", 40, bold=True)[0] for l in quote_lines)
q_bw = q_max_w + 56

idx = FACT.index("（")
it_text = FACT[:idx]
zh_text = FACT[idx:]

it_lines = sf.wrap(it_text, "serif", 28, 790)
zh_lines = sf.wrap(zh_text, "cjk-sc", 28, 790)

it_heights = [sf.measure(l, "serif", 28)[1] for l in it_lines]
zh_heights = [sf.measure(l, "cjk-sc", 28)[1] for l in zh_lines]
it_text_h = sum(it_heights) + 8 * max(0, len(it_lines) - 1)
zh_text_h = sum(zh_heights) + 8 * max(0, len(zh_lines) - 1)

f_pad = 26
f_gap = 16
f_bh = f_pad * 2 + it_text_h + f_gap + zh_text_h

it_max_w = max(sf.measure(l, "serif", 28)[0] for l in it_lines)
zh_max_w = max(sf.measure(l, "cjk-sc", 28)[0] for l in zh_lines)
f_bw = max(it_max_w, zh_max_w) + 56

q_by = 1120
f_by = q_by + q_bh + 32
f_bottom = f_by + f_bh
if f_bottom > 1650:
    q_by -= (f_bottom - 1650) + 4
    f_by = q_by + q_bh + 32

q_bx = 500 - q_bw / 2
f_bx = 500 - f_bw / 2

# ---------- 背景与装饰（PIL 自由层） ----------
Wp, Hp = sf.W, sf.H
g = Image.new("RGBA", (Wp, Hp), (0, 0, 0, 0))
d = ImageDraw.Draw(g)

# 波普放射线
cx, cy = 500.0, 780.0
R = 1900.0
n = 16
cols = [(255, 90, 90, 70), (255, 200, 60, 70), (90, 190, 255, 70), (255, 120, 210, 70)]
for i in range(n):
    a0 = 2 * math.pi * i / n
    a1 = 2 * math.pi * (i + 0.7) / n
    d.polygon([(cx * S, cy * S),
               (cx * S + R * S * math.cos(a0), cy * S + R * S * math.sin(a0)),
               (cx * S + R * S * math.cos(a1), cy * S + R * S * math.sin(a1))],
              fill=cols[i % 4])

# 中央圆盘
d.ellipse([140 * S, 390 * S, 860 * S, 1100 * S],
          fill=(255, 248, 222, 255), outline=(0, 0, 0, 255), width=8 * S)

# 两肺（靠垫）
d.ellipse([520 * S, 585 * S, 780 * S, 935 * S],
          fill=(255, 175, 175, 255), outline=(0, 0, 0, 255), width=8 * S)
d.ellipse([215 * S, 600 * S, 445 * S, 920 * S],
          fill=(255, 185, 185, 255), outline=(0, 0, 0, 255), width=8 * S)

def heart_poly(hx, hy, k, nn=80):
    pts = []
    for i in range(nn):
        t = 2 * math.pi * i / nn
        xp = 16 * math.sin(t) ** 3
        yp = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((hx + k * xp, hy - k * yp))
    return [(x * S, y * S) for x, y in pts]

# 心切迹：背景色心形切入左肺右缘
d.polygon(heart_poly(462, 800, 3.6),
          fill=(255, 248, 222, 255), outline=(0, 0, 0, 255), width=6 * S)
# 红色心脏嵌在凹槽里
d.polygon(heart_poly(455, 800, 2.9),
          fill=(235, 50, 70, 255), outline=(0, 0, 0, 255), width=6 * S)

# 靠垫纽扣：右肺三颗、左肺两颗（对应肺叶数）
for bx, by, r in [(590, 700, 18), (700, 740, 18), (640, 870, 18)]:
    d.ellipse([(bx - r) * S, (by - r) * S, (bx + r) * S, (by + r) * S],
              fill=(60, 150, 230, 255), outline=(0, 0, 0, 255), width=4 * S)
for bx, by, r in [(295, 690, 18), (285, 830, 18)]:
    d.ellipse([(bx - r) * S, (by - r) * S, (bx + r) * S, (by + r) * S],
              fill=(60, 210, 220, 255), outline=(0, 0, 0, 255), width=4 * S)

# 半调圆点
spacing = 36
radius = 7
for yy in range(0, Hp, spacing * S):
    off = 0 if (yy // (spacing * S)) % 2 == 0 else (spacing * S) // 2
    for xx in range(off, Wp, spacing * S):
        d.ellipse([xx - radius * S, yy - radius * S, xx + radius * S, yy + radius * S],
                  fill=(0, 0, 0, 36))

# 波普四角星
def burst_star(sx, sy, ro, ri, fill):
    pts = []
    for i in range(8):
        r = ro if i % 2 == 0 else ri
        a = math.pi / 2 + i * math.pi / 4
        pts.append((sx * S + r * S * math.cos(a), sy * S - r * S * math.sin(a)))
    d.polygon(pts, fill=fill, outline=(0, 0, 0, 255), width=4 * S)

burst_star(130, 300, 55, 22, (255, 210, 40, 255))
burst_star(880, 300, 48, 20, (60, 150, 230, 255))
burst_star(170, 1110, 45, 18, (230, 50, 70, 255))
burst_star(850, 1110, 48, 20, (60, 210, 220, 255))

# 顶部与底部色带
d.rectangle([0, 0, Wp, 110 * S], fill=(220, 50, 60, 255), outline=(0, 0, 0, 255), width=6 * S)
d.rectangle([0, Hp - 80 * S, Wp, Hp], fill=(40, 110, 210, 255), outline=(0, 0, 0, 255), width=6 * S)

# 流水号徽章
serial_w, serial_h = sf.measure(SERIAL, "sans", 30, bold=True)
sbcx = 100 + serial_w / 2
sbcy = 60 + serial_h / 2
sb_rx = serial_w / 2 + 26
sb_ry = serial_h / 2 + 18
d.ellipse([(sbcx - sb_rx) * S, (sbcy - sb_ry) * S, (sbcx + sb_rx) * S, (sbcy + sb_ry) * S],
          fill=(255, 210, 40, 255), outline=(0, 0, 0, 255), width=5 * S)

# 日期徽章
date_w, date_h = sf.measure(DATE, "sans", 22, bold=True)
dbcx, dbcy = 820, 82
db_w = date_w + 40
db_h = date_h + 30
db_x0 = dbcx - db_w / 2
db_y0 = dbcy - db_h / 2
d.rounded_rectangle([db_x0 * S, db_y0 * S, (db_x0 + db_w) * S, (db_y0 + db_h) * S],
                    radius=14 * S, fill=(40, 100, 200, 255), outline=(0, 0, 0, 255), width=5 * S)

# 金句背景块
d.rounded_rectangle([q_bx * S, q_by * S, (q_bx + q_bw) * S, (q_by + q_bh) * S],
                    radius=22 * S, fill=(255, 250, 215, 255), outline=(0, 0, 0, 255), width=6 * S)

# 冷知识背景块
d.rounded_rectangle([f_bx * S, f_by * S, (f_bx + f_bw) * S, (f_by + f_bh) * S],
                    radius=22 * S, fill=(255, 255, 245, 255), outline=(0, 0, 0, 255), width=6 * S)

sf.composite(g)

# ---------- 文字（受控层，用 box.bottom 推进） ----------
sf.serial(100, 60, SERIAL, family="sans", size=30, fill=(20, 20, 20),
          anchor="lt", role="meta", bold=True)
sf.datestamp(dbcx, dbcy, DATE, family="sans", size=22, fill=(255, 255, 255),
             anchor="mm", role="meta", bold=True)

y = q_by + q_pad
for i, line in enumerate(quote_lines):
    w, _ = sf.measure(line, "sans", 40, bold=True)
    box = sf.text(500 - w / 2, y, line, family="sans", size=40, fill=(25, 25, 25),
                  anchor="lt", role="quote", bold=True)
    if i < len(quote_lines) - 1:
        y = box.bottom + 8

y = f_by + f_pad
for i, line in enumerate(it_lines):
    w, _ = sf.measure(line, "serif", 28)
    box = sf.text(500 - w / 2, y, line, family="serif", size=28, fill=(30, 30, 30),
                  anchor="lt", role="body")
    if i < len(it_lines) - 1:
        y = box.bottom + 8
    else:
        y = box.bottom + f_gap

for i, line in enumerate(zh_lines):
    w, _ = sf.measure(line, "cjk-sc", 28)
    box = sf.text(500 - w / 2, y, line, family="cjk-sc", size=28, fill=(30, 30, 30),
                  anchor="lt", role="body")
    if i < len(zh_lines) - 1:
        y = box.bottom + 8

sf.save(OUT_PATH)
