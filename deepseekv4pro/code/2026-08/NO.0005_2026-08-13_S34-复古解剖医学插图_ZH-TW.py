import numpy as np
from PIL import Image, ImageDraw
import math
from atelier_canvas import Surface

# === 画布 ===
w = 1000
h = 1360
sf = Surface(w, h, scale=2, bg=(242, 233, 218))

# 安全区
sf.frame(80, 40, 840, 1280)

# === 复古解剖装饰层 ===
deco_img = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
draw = ImageDraw.Draw(deco_img)

INK = (70, 55, 45, 255)
RED = (135, 50, 45, 255)
OCHRE = (185, 155, 115, 255)
FAINT = (170, 150, 130, 255)

cx = 500
cy_ball = 590
r_ball = 45
feather_len = 270
feather_start_y = cy_ball - r_ball
num_feathers = 16
angle_start = -50.0
angle_end = 50.0

box_x1, box_y1, box_x2, box_y2 = 290, 230, 710, 700

def dashed_rect(draw, x1, y1, x2, y2, color, dash=12, gap=8, width=2):
    x = x1
    while x < x2:
        draw.line([(x * 2, y1 * 2), (min(x + dash, x2) * 2, y1 * 2)], fill=color, width=width)
        x += dash + gap
    x = x1
    while x < x2:
        draw.line([(x * 2, y2 * 2), (min(x + dash, x2) * 2, y2 * 2)], fill=color, width=width)
        x += dash + gap
    y = y1
    while y < y2:
        draw.line([(x1 * 2, y * 2), (x1 * 2, min(y + dash, y2) * 2)], fill=color, width=width)
        y += dash + gap
    y = y1
    while y < y2:
        draw.line([(x2 * 2, y * 2), (x2 * 2, min(y + dash, y2) * 2)], fill=color, width=width)
        y += dash + gap

dashed_rect(draw, box_x1, box_y1, box_x2, box_y2, INK, dash=12, gap=8, width=2)

cross_size = 8
for (cx_c, cy_c) in [(box_x1, box_y1), (box_x2, box_y1), (box_x1, box_y2), (box_x2, box_y2)]:
    draw.line([(cx_c * 2 - cross_size * 2, cy_c * 2), (cx_c * 2 + cross_size * 2, cy_c * 2)], fill=INK, width=2)
    draw.line([(cx_c * 2, cy_c * 2 - cross_size * 2), (cx_c * 2, cy_c * 2 + cross_size * 2)], fill=INK, width=2)

ball_box = (cx - r_ball, cy_ball - r_ball, cx + r_ball, cy_ball + r_ball)
draw.pieslice([ball_box[0] * 2, ball_box[1] * 2, ball_box[2] * 2, ball_box[3] * 2], 180, 360, fill=OCHRE)
draw.arc([ball_box[0] * 2, ball_box[1] * 2, ball_box[2] * 2, ball_box[3] * 2], 180, 360, fill=INK, width=3)
draw.line([(cx - r_ball) * 2, cy_ball * 2, (cx + r_ball) * 2, cy_ball * 2], fill=INK, width=2)

for i in range(num_feathers):
    angle_deg = angle_start + (angle_end - angle_start) * i / (num_feathers - 1)
    angle_rad = math.radians(angle_deg)
    end_x = cx + feather_len * math.sin(angle_rad)
    end_y = feather_start_y - feather_len * math.cos(angle_rad)

    draw.line([cx * 2, feather_start_y * 2, end_x * 2, end_y * 2], fill=INK, width=3)

    dx = end_x - cx
    dy = end_y - feather_start_y
    length = math.sqrt(dx * dx + dy * dy)
    if length > 0:
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        for t in range(60, int(length), 20):
            base_x = cx + dx * t / length
            base_y = feather_start_y + dy * t / length
            half_len = 7
            draw.line([
                (base_x - px * half_len) * 2, (base_y - py * half_len) * 2,
                (base_x + px * half_len) * 2, (base_y + py * half_len) * 2
            ], fill=(80, 65, 50, 255), width=1)

    ellipse_w = 14
    ellipse_h = 6
    draw.ellipse([
        (end_x - ellipse_w / 2) * 2, (end_y - ellipse_h / 2) * 2,
        (end_x + ellipse_w / 2) * 2, (end_y + ellipse_h / 2) * 2
    ], fill=OCHRE, outline=INK)

# 球头下方散落的坏羽毛
for i in range(5):
    x_off = -70 + i * 35
    y_base = 670 + (i % 2) * 18
    draw.line([(cx + x_off - 18) * 2, y_base * 2, (cx + x_off + 18) * 2, (y_base + 14) * 2],
              fill=(90, 70, 50, 255), width=2)
    draw.line([(cx + x_off - 10) * 2, (y_base + 2) * 2, (cx + x_off + 10) * 2, (y_base + 10) * 2],
              fill=(90, 70, 50, 255), width=1)

# 暗红标注箭头（无文字）
draw.line([(box_x1 * 2, cy_ball * 2), ((box_x1 - 28) * 2, cy_ball * 2)], fill=RED, width=2)
draw.polygon([
    (box_x1 * 2 - 6, cy_ball * 2 - 4),
    (box_x1 * 2 - 6, cy_ball * 2 + 4),
    (box_x1 * 2 - 18, cy_ball * 2)
], fill=RED)

target_y = box_y1 + 110
draw.line([(box_x2 * 2, target_y * 2), ((box_x2 + 28) * 2, target_y * 2)], fill=RED, width=2)
draw.polygon([
    (box_x2 * 2 + 6, target_y * 2 - 4),
    (box_x2 * 2 + 6, target_y * 2 + 4),
    (box_x2 * 2 + 18, target_y * 2)
], fill=RED)

# === 底部复古解剖装饰（填补底部留白，不添加文字）===
# 底部细线图版末尾
bottom_line_y = 1195
draw.line([(150 * 2, bottom_line_y * 2), (850 * 2, bottom_line_y * 2)], fill=FAINT, width=1)
draw.line([(150 * 2, (bottom_line_y + 6) * 2), (850 * 2, (bottom_line_y + 6) * 2)], fill=FAINT, width=1)

# 底部刻度线
for tick_x in range(250, 801, 50):
    draw.line([(tick_x * 2, bottom_line_y * 2), (tick_x * 2, (bottom_line_y + 8) * 2)], fill=FAINT, width=1)

# 底部散落羽毛与剖面小图
for i in range(6):
    fx = 160 + i * 55
    fy = 1230 + (i % 2) * 40
    draw.line([(fx - 14) * 2, fy * 2, (fx + 14) * 2, (fy + 11) * 2], fill=(90, 70, 50, 255), width=2)
    draw.line([(fx - 8) * 2, (fy + 2) * 2, (fx + 8) * 2, (fy + 8) * 2], fill=(90, 70, 50, 255), width=1)

# 一个小的羽毛横截面椭圆，位于底部右侧
ellipse_center = (820, 1270)
draw.ellipse([
    (ellipse_center[0] - 26) * 2, (ellipse_center[1] - 10) * 2,
    (ellipse_center[0] + 26) * 2, (ellipse_center[1] + 10) * 2
], outline=INK, width=2)
draw.line([
    (ellipse_center[0] - 20) * 2, ellipse_center[1] * 2,
    (ellipse_center[0] + 20) * 2, ellipse_center[1] * 2
], fill=INK, width=1)

sf.composite(np.array(deco_img))

# === 文字层 ===
TEXT_QUOTE = (60, 40, 30)
TEXT_FACT = (50, 42, 35)
TEXT_META = (110, 45, 40)

sf.serial(80, 55, SERIAL, family="mono", size=16, fill=TEXT_META, anchor="lt", role="meta")
sf.datestamp(920, 55, DATE, family="mono", size=16, fill=TEXT_META, anchor="rt", role="meta")

quote_y = 780
box_q = sf.text(500, quote_y, QUOTE, family="serif-cjk", size=36, fill=TEXT_QUOTE,
                anchor="mt", role="quote", max_w=840, line_gap=0.5)

fact_y = box_q.bottom + 45
sf.text(80, fact_y, FACT, family="cjk-tc", size=28, fill=TEXT_FACT,
        anchor="lt", role="body", max_w=840, line_gap=0.4)

sf.save(OUT_PATH)
