from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# 逻辑尺寸
W, H = 1000, 1700
sf = Surface(W, H, scale=2, bg=(248, 244, 230))

# --- 装饰层：植物学图鉴线稿 ---
deco = Image.new('RGBA', (W*2, H*2), (0,0,0,0))
draw = ImageDraw.Draw(deco)
border_col = (72, 55, 35, 255)
frame_col = (90, 75, 50, 255)
text_col = (60, 45, 30, 255)

# 外边框与内边框
draw.rectangle([110, 110, W*2-110, H*2-110], outline=border_col, width=5)
draw.rectangle([130, 130, W*2-130, H*2-130], outline=border_col, width=2)

# 顶部装饰细线（移到 QUOTE 上方）
draw.line([130, 240, W*2-130, 240], fill=(130, 110, 75, 120), width=2)

# 底部标签框（位于标签文字后方）
label_box_x0, label_box_y0 = 280, 2760
label_box_x1, label_box_y1 = 1720, 2940
draw.rectangle([label_box_x0, label_box_y0, label_box_x1, label_box_y1],
               outline=border_col, width=3, fill=(240, 232, 210, 255))
# 标签框内分隔线
draw.line([900, label_box_y0+20, 900, label_box_y1-20], fill=(130, 110, 75, 200), width=2)

# 底部装饰线（标签框上方）
draw.line([130, 2700, W*2-130, 2700], fill=(130, 110, 75, 120), width=2)

# 地平线
ground_y = 1350
draw.line([180, ground_y, W*2-180, ground_y], fill=(105, 125, 85, 220), width=3)

# 主蚁丘插图（楔形，窄边视角与宽面纹理）
top = (1000, 800)
base_left = (840, 1350)
base_right = (1160, 1350)
draw.polygon([top, base_left, base_right], fill=(234, 220, 183, 255), outline=border_col, width=4)
# 内部纹理：横向层次与斜排线
for i in range(1, 7):
    frac = i / 8
    y = 800 + (1350-800)*frac
    half_w = (1000-840) * (1-frac)
    x1 = 1000 - half_w
    x2 = 1000 + half_w
    draw.line([x1, y, x2, y], fill=(135, 108, 68, 200), width=2)
    if i % 2 == 0:
        draw.line([x1+15, y+12, x2-15, y-12], fill=(165, 138, 92, 160), width=1)

# 草地线条
for sx in range(200, W*2-200, 60):
    draw.line([sx, ground_y, sx, ground_y+28], fill=(112, 142, 86, 210), width=2)
    draw.line([sx+12, ground_y, sx+12, ground_y+17], fill=(112, 142, 86, 210), width=2)

# 远处小蚁丘
small_ones = [(340, 1140), (610, 1240), (1480, 1190), (1720, 1080), (740, 1190)]
for (sx, sy) in small_ones:
    draw.polygon([(sx*2, sy*2), (sx*2-55, 1350), (sx*2+55, 1350)],
                 outline=(118, 98, 68, 210), fill=(238, 225, 192, 255))

# 指南针装饰（右上角，无文字）
compass_cx, compass_cy, compass_r = 1700, 580, 95
draw.ellipse([compass_cx-compass_r, compass_cy-compass_r, compass_cx+compass_r, compass_cy+compass_r],
             outline=(92, 76, 50, 255), width=3)
draw.line([compass_cx, compass_cy-compass_r+10, compass_cx, compass_cy+compass_r-10], fill=(92, 76, 50, 255), width=2)
draw.line([compass_cx-compass_r+10, compass_cy, compass_cx+compass_r-10, compass_cy], fill=(92, 76, 50, 255), width=2)
draw.polygon([(compass_cx, compass_cy-compass_r+10),
              (compass_cx-14, compass_cy-compass_r+36),
              (compass_cx+14, compass_cy-compass_r+36)], fill=(130, 95, 62, 255))

# 合并装饰层
sf.composite(deco, mode="normal", opacity=1.0)

# --- 文字层 ---
sf.frame(80, 80, W-160, H-160)

# 金句（居中，衬线字体，深棕）
quote_box = sf.text(W//2, 170, QUOTE,
                   family="serif-cjk", size=46, fill=(60, 45, 30),
                   anchor="mt", role="quote", bold=True,
                   max_w=820, line_gap=0.5)

# 冷知识（居中，衬线字体）
fact_box = sf.text(W//2, 820, FACT,
                  family="serif-cjk", size=32, fill=(55, 42, 28),
                  anchor="mt", role="body", bold=False,
                  max_w=800, line_gap=0.45)

# 标签：流水号与日期（融入标签框）
sf.serial(170, 1420, SERIAL,
          family="serif-cjk", size=22, fill=(50, 40, 25),
          anchor="lt", role="meta", bold=False)
sf.datestamp(830, 1420, DATE,
             family="serif-cjk", size=22, fill=(50, 40, 25),
             anchor="rt", role="meta", bold=False)

sf.save(OUT_PATH)
