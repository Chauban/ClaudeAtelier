import numpy as np
from PIL import Image, ImageDraw
from atelier_canvas import Surface

# ── 画布 ──────────────────────────────────────────────
W, H = 1000, 1540
sf = Surface(W, H, scale=2, bg=(0, 0, 0))

# 孟菲斯撞色盘
INK     = (20, 18, 32)
CREAM   = (244, 238, 218)
HOTPINK = (255, 83, 146)
TANGER  = (255, 124, 58)
LEMON   = (250, 226, 54)
MINT    = (83, 208, 174)
LILAC   = (154, 128, 232)
COBALT  = (52, 90, 246)
BLACK   = (16, 14, 24)

def rgba(c):
    return (c[0], c[1], c[2], 255)

def fill_block(arr, x0, y0, x1, y1, rgb):
    x0, y0, x1, y1 = int(x0*2), int(y0*2), int(x1*2), int(y1*2)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(sf.W, x1), min(sf.H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    arr[y0:y1, x0:x1, 0] = rgb[0]
    arr[y0:y1, x0:x1, 1] = rgb[1]
    arr[y0:y1, x0:x1, 2] = rgb[2]
    arr[y0:y1, x0:x1, 3] = 255

# ── 底色：黑色边框 + 中央米色文字区 ─────────────────────
bg = sf.layer()
fill_block(bg, 0, 0, W, H, BLACK)
fill_block(bg, 60, 88, 940, 1380, CREAM)

# 孟菲斯饰线、波点只放在边框内，不侵入中央文字区
draw_img = Image.fromarray(bg, "RGBA")
draw = ImageDraw.Draw(draw_img)

def rect(x0, y0, x1, y1, fill, outline=BLACK, width=5):
    draw.rectangle([x0*2, y0*2, x1*2, y1*2],
                   fill=rgba(fill), outline=rgba(outline), width=width)

def ellipse(x0, y0, x1, y1, fill, outline=BLACK, width=5):
    draw.ellipse([x0*2, y0*2, x1*2, y1*2],
                 fill=rgba(fill), outline=rgba(outline), width=width)

def line(x0, y0, x1, y1, fill=BLACK, width=8):
    draw.line([x0*2, y0*2, x1*2, y1*2], fill=rgba(fill), width=width)

# 顶部边框内的几何块
rect(70, 12, 150, 72, HOTPINK)
rect(180, 18, 260, 66, LEMON)
rect(290, 10, 350, 74, MINT)
ellipse(480, 16, 548, 88, TANGER, outline=BLACK, width=5)
rect(740, 14, 800, 70, TANGER)
rect(830, 16, 900, 68, LILAC)

# 底部边框内的几何块
rect(70, 1395, 150, 1500, COBALT)
rect(180, 1410, 260, 1495, LEMON)
rect(640, 1390, 700, 1500, HOTPINK)
rect(810, 1405, 890, 1485, MINT)
ellipse(900, 1400, 930, 1510, TANGER, outline=BLACK, width=5)

# 左侧边框内的波点
ellipse(12, 140, 48, 176, MINT)
ellipse(14, 300, 46, 334, LEMON)
ellipse(12, 520, 48, 556, HOTPINK)
ellipse(14, 710, 46, 744, COBALT)
ellipse(12, 900, 48, 936, TANGER)
ellipse(14, 1090, 46, 1126, LILAC)
ellipse(12, 1250, 48, 1286, MINT)

# 右侧边框内的波点
ellipse(952, 150, 988, 186, HOTPINK)
ellipse(954, 320, 986, 354, COBALT)
ellipse(952, 540, 988, 576, LEMON)
ellipse(954, 730, 986, 764, LILAC)
ellipse(952, 920, 988, 956, TANGER)
ellipse(954, 1110, 986, 1146, MINT)
ellipse(952, 1260, 988, 1296, COBALT)

sf.composite(draw_img, mode="normal")

# ── 安全区 ────────────────────────────────────────────
M = 70
sf.frame(M, M, W - 2*M, H - 2*M)

# ── 文字 ──────────────────────────────────────────────
# 顶部：Ye Olde → The Olde
sf.text(M, 120, "Ye Olde", family="serif", size=150,
        fill=INK, anchor="lt", role="title", bold=True)

sf.text(M, 316, "→ 讀做 The Olde", family="cjk-hk",
        size=34, fill=BLACK, anchor="lt", role="meta", max_w=330)

sf.text(M, 451, QUOTE, family="cjk-hk",
        size=41, fill=BLACK, anchor="lt", role="quote",
        line_gap=0.48, max_w=W - 2*M)

sf.text(M, 670, "冷知識 / 語言與文字", family="cjk-hk",
        size=30, fill=BLACK, anchor="lt", role="meta", bold=True)

sf.text(M, 744, FACT, family="cjk-hk",
        size=43, fill=BLACK, anchor="lt", role="body",
        line_gap=0.55, max_w=W - 2*M)

# 底部编号与日期
tag_y = 1258
sf.text(M, tag_y, "—— 第 0051 期 ——", family="cjk-hk",
        size=32, fill=BLACK, anchor="lt", role="meta", bold=True)
sf.datestamp(M, tag_y + 58, DATE, family="cjk-hk",
             size=30, fill=BLACK, anchor="lt", role="meta", bold=True)
sf.serial(W - M - 240, tag_y, SERIAL, family="sans",
          size=30, fill=BLACK, anchor="lt", role="meta", bold=True)

sf.save(OUT_PATH)
