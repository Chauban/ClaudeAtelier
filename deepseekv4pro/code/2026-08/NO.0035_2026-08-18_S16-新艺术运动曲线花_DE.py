import math
import numpy as np
from PIL import Image, ImageDraw
from atelier_canvas import Surface

W = 1000
X_LEFT = 100
RIGHT_X = 900
MAX_W = 800

FONT_DE = "serif"
FONT_ZH = "cjk-sc"

def split_bilingual(text):
    text = text.strip()
    if '\n' in text:
        parts = text.split('\n')
        original = parts[0].strip()
        translation = ' '.join(parts[1:]).strip()
    else:
        idx = text.find('（')
        if idx == -1:
            idx = text.find('(')
        if idx != -1:
            original = text[:idx].strip()
            translation = text[idx:].strip()
        else:
            original = text
            translation = ''
    translation = translation.strip('（）() ')
    return original, translation

q_de, q_zh = split_bilingual(QUOTE)
f_de, f_zh = split_bilingual(FACT)

# 先用临时画布测量文字，确定最终高度
tmp = Surface(W, 2000, scale=2, bg=(247, 240, 222))

def block_h(lines, family, size, gap):
    total = 0.0
    for i, ln in enumerate(lines):
        w, h = tmp.measure(ln, family, size, bold=False)
        total += h
        if i < len(lines) - 1:
            total += h * gap
    return total

quote_lines = tmp.wrap(q_de, FONT_DE, 43, max_w=MAX_W)
quote_zh_lines = tmp.wrap(q_zh, FONT_ZH, 28, max_w=MAX_W)
fact_lines = tmp.wrap(f_de, FONT_DE, 29, max_w=MAX_W)
fact_zh_lines = tmp.wrap(f_zh, FONT_ZH, 28, max_w=MAX_W)

TOP_META_Y = 170
QUOTE_TOP = 254

quote_h = block_h(quote_lines, FONT_DE, 43, 0.30)
quote_zh_h = block_h(quote_zh_lines, FONT_ZH, 28, 0.35)
quote_bottom = QUOTE_TOP + quote_h + 12 + quote_zh_h

div_y = quote_bottom + 46
FACT_TOP = div_y + 56

fact_h = block_h(fact_lines, FONT_DE, 29, 0.35)
fact_zh_h = block_h(fact_zh_lines, FONT_ZH, 28, 0.42)
fact_bottom = FACT_TOP + fact_h + 20 + fact_zh_h

H = int(math.ceil(fact_bottom + 250))
if H < 1300:
    H = 1300

sf = Surface(W, H, scale=2, bg=(247, 240, 222))
sf.frame(X_LEFT, 90, MAX_W, H - 170)

def render_background(surf):
    lay = surf.layer()
    yy = np.linspace(0, 1, surf.H)[:, None]
    xx = np.linspace(0, 1, surf.W)[None, :]
    r = (250 - 12 * yy).astype(np.float32)
    g = (244 - 10 * yy).astype(np.float32)
    b = (225 - 14 * yy).astype(np.float32)
    glow = np.exp(-((xx - 0.5) ** 2 + (yy - 0.22) ** 2) * 4.0)
    r = np.clip(r + 10 * glow, 0, 255).astype(np.uint8)
    g = np.clip(g + 8 * glow, 0, 255).astype(np.uint8)
    b = np.clip(b + 5 * glow, 0, 255).astype(np.uint8)
    lay[..., 0] = r
    lay[..., 1] = g
    lay[..., 2] = b
    lay[..., 3] = 255
    surf.composite(lay)

def render_decorations(surf, div_y, serial_panel, date_panel):
    lay = surf.layer()
    img = Image.fromarray(lay, "RGBA")
    d = ImageDraw.Draw(img)
    K = 2
    W_log = surf.W
    H_log = surf.H
    green_dark = (52, 72, 46, 255)
    green = (74, 96, 64, 255)
    gold = (172, 140, 78, 255)
    pale_gold = (226, 202, 145, 255)

    def organic_line(p0, p1, amp, cycles, color, width):
        x0, y0 = p0[0] * K, p0[1] * K
        x1, y1 = p1[0] * K, p1[1] * K
        horiz = abs(x1 - x0) >= abs(y1 - y0)
        pts = []
        n = 200
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            off = (amp * K * math.sin(2 * math.pi * cycles * t)
                   + 0.45 * amp * K * math.sin(4 * math.pi * cycles * t + 0.5))
            if horiz:
                y += off
            else:
                x += off
            pts.append((x, y))
        d.line(pts, fill=color, width=width * K, joint="curve")

    def draw_wavy_frame(m, amp, cycles, color, width):
        cs = [(m, m), (W_log - m, m),
              (W_log - m, H_log - m), (m, H_log - m)]
        for i in range(4):
            organic_line(cs[i], cs[(i + 1) % 4], amp, cycles, color, width)

    draw_wavy_frame(58, 24, 3, green_dark, 9)
    draw_wavy_frame(112, 29, 4, green, 6)
    draw_wavy_frame(158, 20, 3.5, gold, 4)

    def leaf(x, y, angle_deg, length, width, fill, outline):
        ang = math.radians(angle_deg)
        pts = []
        for i in range(21):
            t = i / 20
            lx = -length / 2 + length * t
            w = math.sin(math.pi * t) * width / 2
            px = x + math.cos(ang) * lx - math.sin(ang) * w
            py = y + math.sin(ang) * lx + math.cos(ang) * w
            bend = 0.28 * math.sin(math.pi * t)
            px += math.cos(ang + math.pi / 2) * bend * length * 0.18
            py += math.sin(ang + math.pi / 2) * bend * length * 0.18
            pts.append((px * K, py * K))
        for i in range(20, -1, -1):
            t = i / 20
            lx = -length / 2 + length * t
            w = math.sin(math.pi * t) * width / 2
            px = x + math.cos(ang) * lx + math.sin(ang) * w
            py = y + math.sin(ang) * lx - math.cos(ang) * w
            px += math.cos(ang + math.pi / 2) * math.sin(math.pi * t) * length * 0.05
            py += math.sin(ang + math.pi / 2) * math.sin(math.pi * t) * length * 0.05
            pts.append((px * K, py * K))
        d.polygon(pts, fill=fill, outline=outline)

    # 侧边花叶全部放在版心之外，避免穿过文字
    for py in [0.14, 0.32, 0.52, 0.72, 0.88]:
        y = surf.H * py
        leaf(62, y, 150, 72, 20, gold, green_dark)
        leaf(86, y, 170, 46, 15, green, green_dark)
        leaf(W_log - 62, y, 30, 72, 20, gold, green_dark)
        leaf(W_log - 86, y, 10, 46, 15, green, green_dark)

    def bloom(cx, cy, r, petal_fill, outline_w):
        d.ellipse([cx * K - r * K, cy * K - r * K,
                   cx * K + r * K, cy * K + r * K],
                  outline=outline_w, width=7 * K)
        for i in range(8):
            ang = i / 8 * 2 * math.pi
            px = cx + math.cos(ang) * r * 0.72
            py = cy + math.sin(ang) * r * 0.72
            rr = r * 0.30
            d.ellipse([px * K - rr * K, py * K - rr * K,
                       px * K + rr * K, py * K + rr * K],
                      fill=petal_fill, outline=outline_w, width=5 * K)
        d.ellipse([cx * K - r * 0.25 * K, cy * K - r * 0.25 * K,
                   cx * K + r * 0.25 * K, cy * K + r * 0.25 * K],
                  fill=outline_w)

    bloom(W_log / 2, 82, 68, gold, green_dark)
    bloom(W_log / 2, H_log - 94, 62, gold, green_dark)

    # 分隔花枝
    cy = div_y
    organic_line((190, cy), (W_log - 190, cy), 13, 2.5, gold, 7)
    d.ellipse([W_log / 2 * K - 17 * K, cy * K - 17 * K,
               W_log / 2 * K + 17 * K, cy * K + 17 * K],
              fill=pale_gold, outline=green_dark, width=5 * K)

    # 在流水号与日期下方垫干净的底色块，避免装饰线穿过文字
    for panel in (serial_panel, date_panel):
        if panel is None:
            continue
        x0, y0, x1, y1 = panel
        d.rectangle([x0 * K, y0 * K, x1 * K, y1 * K],
                    fill=(247, 240, 222, 255), outline=gold, width=3 * K)

    surf.composite(np.array(img), mode="normal", opacity=1.0)

# 测量流水号与日期宽度，用来放背景垫板
w_serial, h_serial = tmp.measure(SERIAL, FONT_DE, 21, bold=False)
w_date, h_date = tmp.measure(DATE, FONT_DE, 21, bold=False)

serial_panel = (X_LEFT - 12, TOP_META_Y - 10, X_LEFT + w_serial + 12, TOP_META_Y + h_serial + 10)
date_panel = (RIGHT_X - w_date - 12, TOP_META_Y - 10, RIGHT_X + 12, TOP_META_Y + h_date + 10)

render_background(sf)
render_decorations(sf, div_y, serial_panel, date_panel)

sf.serial(X_LEFT, TOP_META_Y, SERIAL,
          family=FONT_DE, size=21, fill=(150, 115, 55),
          anchor="lt", role="meta", bold=False)
sf.datestamp(RIGHT_X, TOP_META_Y, DATE,
             family=FONT_DE, size=21, fill=(150, 115, 55),
             anchor="rt", role="meta", bold=False)

def draw_text_lines(surf, lines, family, size, x, y, fill, role, gap=0.35):
    for i, ln in enumerate(lines):
        box = surf.text(x, y, ln,
                        family=family, size=size, fill=fill,
                        anchor="lt", role=role, bold=False,
                        max_w=MAX_W, line_gap=0, allow_overlap=False)
        if i < len(lines) - 1:
            y = box.bottom + gap * box.h
        else:
            y = box.bottom
    return y

y = QUOTE_TOP
y = draw_text_lines(sf, quote_lines, FONT_DE, 43, X_LEFT, y,
                    (48, 58, 46), "quote", gap=0.30)
y += 12
y = draw_text_lines(sf, quote_zh_lines, FONT_ZH, 28, X_LEFT, y,
                    (62, 78, 60), "quote", gap=0.35)

y = FACT_TOP
y = draw_text_lines(sf, fact_lines, FONT_DE, 29, X_LEFT, y,
                    (40, 50, 44), "body", gap=0.35)
y += 20
y = draw_text_lines(sf, fact_zh_lines, FONT_ZH, 28, X_LEFT, y,
                    (66, 76, 62), "body", gap=0.42)

sf.save(OUT_PATH)
