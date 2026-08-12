from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw
import math

sf = Surface(900, 1620, scale=2, bg=(248, 242, 224))
sf.frame(60, 60, 780, 1500)

fact_it = FACT.split("（")[0].strip()
fact_cn = "（" + FACT.split("（", 1)[1].strip()

quote_max_w = 590
quote_size = 56
quote_lines = sf.wrap(QUOTE, "sans", quote_size, quote_max_w, bold=True)
quote_line_h = sf.measure("Ag", "sans", quote_size, bold=True)[1]
quote_text_h = len(quote_lines) * quote_line_h * 1.35

fact_it_max_w = 590
fact_it_size = 34
fact_it_lines = sf.wrap(fact_it, "sans", fact_it_size, fact_it_max_w)
fact_it_line_h = sf.measure("Ag", "sans", fact_it_size)[1]
fact_it_text_h = len(fact_it_lines) * fact_it_line_h * 1.35

fact_cn_max_w = 590
fact_cn_size = 28
fact_cn_lines = sf.wrap(fact_cn, "cjk-sc", fact_cn_size, fact_cn_max_w)
fact_cn_line_h = sf.measure("水", "cjk-sc", fact_cn_size)[1]
fact_cn_text_h = len(fact_cn_lines) * fact_cn_line_h * 1.35

quote_pad_v = 60
fact_pad_v = 50
fact_gap = 20

quote_box_h = quote_text_h + quote_pad_v * 2
fact_box_h = fact_it_text_h + fact_cn_text_h + fact_gap + fact_pad_v * 2

quote_box_x = 80
quote_box_y = 200
quote_box_w = 680

fact_box_x = 80
fact_box_y = quote_box_y + quote_box_h + 80
fact_box_w = 680

bottom_y = fact_box_y + fact_box_h + 80

# 背景点阵
img_bg = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
draw_bg = ImageDraw.Draw(img_bg)
step = 28
for y in range(step, sf.H, step):
    for x in range(step, sf.W, step):
        draw_bg.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(224, 218, 202, 120))
sf.composite(img_bg)

# 装饰层
img_deco = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img_deco)

# 顶部胶带
draw.polygon([(60, 20), (200, 0), (240, 70), (100, 90)], fill=(190, 215, 235, 140), outline=(160, 190, 210, 180))
draw.polygon([(600, 10), (780, 30), (760, 90), (580, 70)], fill=(240, 215, 180, 140), outline=(210, 180, 140, 180))

# QUOTE 便签
draw.rounded_rectangle(
    [quote_box_x, quote_box_y, quote_box_x + quote_box_w, quote_box_y + quote_box_h],
    radius=14, fill=(255, 250, 232, 235), outline=(200, 190, 160, 210), width=3
)

# FACT 便签
draw.rounded_rectangle(
    [fact_box_x, fact_box_y, fact_box_x + fact_box_w, fact_box_y + fact_box_h],
    radius=14, fill=(240, 248, 250, 235), outline=(170, 200, 210, 210), width=3
)

# 水星图案
cx = 820
cy = quote_box_y + 80
r = 40
draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(180, 180, 190, 230), outline=(130, 130, 140, 230), width=3)
for dx, dy, dr in [(-15, -10, 7), (10, -20, 5), (15, 10, 6), (-5, 18, 8), (5, 5, 4)]:
    draw.ellipse([cx + dx - dr, cy + dy - dr, cx + dx + dr, cy + dy + dr], fill=(150, 150, 160, 200))

# 太阳
sx = cx
sy = cy - 90
draw.ellipse([sx - 20, sy - 20, sx + 20, sy + 20], fill=(250, 200, 80, 235), outline=(220, 170, 60, 235), width=3)
for ang in range(0, 360, 45):
    rad = math.radians(ang)
    x1 = sx + 25 * math.cos(rad)
    y1 = sy + 25 * math.sin(rad)
    x2 = sx + 35 * math.cos(rad)
    y2 = sy + 35 * math.sin(rad)
    draw.line([x1, y1, x2, y2], fill=(240, 190, 70, 235), width=3)

# 底部标签
draw.rectangle([100, bottom_y + 20, 280, bottom_y + 20 + 50], fill=(235, 220, 190, 210), outline=(190, 170, 130, 210), width=2)
draw.rectangle([450, bottom_y + 20, 680, bottom_y + 20 + 50], fill=(220, 230, 210, 210), outline=(180, 200, 170, 210), width=2)

# 手绘星形
for sx, sy, sr in [(150, 130, 7), (700, 100, 6), (820, quote_box_y - 30, 6), (60, fact_box_y + 40, 6), (860, fact_box_y + 200, 7)]:
    pts = []
    for i in range(5):
        ang = math.radians(-90 + i * 72)
        px = sx + sr * math.cos(ang)
        py = sy + sr * math.sin(ang)
        pts.append((px, py))
        ang2 = math.radians(-90 + i * 72 + 36)
        px2 = sx + sr * 0.4 * math.cos(ang2)
        py2 = sy + sr * 0.4 * math.sin(ang2)
        pts.append((px2, py2))
    draw.polygon(pts, fill=(250, 220, 130, 200), outline=(210, 180, 90, 200))

sf.composite(img_deco)

# 文字
quote_x = quote_box_x + 45
quote_y = quote_box_y + quote_pad_v
box_quote = sf.text(
    quote_x, quote_y, "\n".join(quote_lines),
    family="sans", size=quote_size, fill=(50, 55, 70),
    anchor="lt", role="quote", bold=True,
    max_w=quote_max_w, line_gap=0.35, allow_overlap=False
)

fact_it_x = fact_box_x + 40
fact_it_y = fact_box_y + fact_pad_v
box_fact_it = sf.text(
    fact_it_x, fact_it_y, "\n".join(fact_it_lines),
    family="sans", size=fact_it_size, fill=(55, 60, 72),
    anchor="lt", role="body",
    max_w=fact_it_max_w, line_gap=0.35, allow_overlap=False
)

fact_cn_y = box_fact_it.bottom + fact_gap
box_fact_cn = sf.text(
    fact_it_x, fact_cn_y, "\n".join(fact_cn_lines),
    family="cjk-sc", size=fact_cn_size, fill=(90, 95, 105),
    anchor="lt", role="body",
    max_w=fact_cn_max_w, line_gap=0.35, allow_overlap=False
)

sf.serial(120, bottom_y + 32, SERIAL, family="sans", size=22, fill=(60, 60, 68), anchor="lt", role="meta", bold=False, allow_overlap=False)
sf.datestamp(470, bottom_y + 32, DATE, family="sans", size=22, fill=(60, 60, 68), anchor="lt", role="meta", bold=False, allow_overlap=False)

sf.save(OUT_PATH)
