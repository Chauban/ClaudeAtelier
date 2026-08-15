import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 1000, 1600
sf = Surface(W, H, scale=2, bg=(244, 240, 234))
sf.frame(100, 100, 800, 1400)

scale = 2
SUPERSCRIPT_SET = set("⁰¹²³⁴⁵⁶⁷⁸⁹")

# ---------- 柔和纸张颗粒 ----------
lay = sf.layer()
rng = np.random.default_rng(20260816)
noise = rng.normal(0, 6.0, (sf.H, sf.W)).astype(np.float32)
yy, xx = np.mgrid[0:sf.H, 0:sf.W].astype(np.float32)
dx = (xx - 0.5 * sf.W) / (0.74 * sf.W)
dy = (yy - 0.33 * sf.H) / (0.72 * sf.H)
dist = np.sqrt(dx * dx + dy * dy).clip(0, 1.5)
lum = 255 + noise - 26.0 * dist
pix = np.clip(lum, 0, 255).astype(np.uint8)
lay[..., 0] = pix
lay[..., 1] = pix
lay[..., 2] = pix
lay[..., 3] = 62
sf.composite(lay)

# ---------- 山丘与太阳 ----------
def hill_polygon(cx, hgt, wid, base_y):
    pts = []
    for xp in range(0, sf.W + 1, 8):
        xl = xp / scale
        yl = base_y - hgt * math.exp(-((xl - cx) / wid) ** 2)
        pts.append((xp, yl * scale))
    pts.append((sf.W, base_y * scale))
    pts.append((0, base_y * scale))
    return pts

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
base_y = 320
d.ellipse([745 * scale - 72 * scale, 95 * scale - 72 * scale,
           745 * scale + 72 * scale, 95 * scale + 72 * scale],
          fill=(250, 244, 230, 85))
for cx, hgt, wid, col, alp in [
    (880, 250, 280, (150, 162, 148), 50),
    (210, 290, 320, (168, 180, 166), 60),
    (560, 180, 240, (158, 170, 156), 66),
]:
    d.polygon(hill_polygon(cx, hgt, wid, base_y), fill=col + (alp,))
img = img.filter(ImageFilter.GaussianBlur(5))
sf.composite(img)

# ---------- 金句 ----------
bq1 = sf.text(500, 360, QUOTE[:12],
              family="cjk-tc", size=40, fill=(55, 58, 54),
              anchor="mt", role="quote")
bq2 = sf.text(500, bq1.bottom + 14, QUOTE[12:],
              family="cjk-tc", size=40, fill=(55, 58, 54),
              anchor="mt", role="quote")

sep_y = bq2.bottom + 68

# ---------- 分隔装饰 ----------
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
cx0 = 500 * scale
sy0 = int(sep_y * scale)
g = (150, 154, 144, 155)
d.line([(int(cx0 - 74 * scale), sy0), (int(cx0 - 12 * scale), sy0)], fill=g, width=3)
d.line([(int(cx0 + 12 * scale), sy0), (int(cx0 + 74 * scale), sy0)], fill=g, width=3)
d.ellipse([int(cx0 - 5 * scale), sy0 - 5 * scale,
           int(cx0 + 5 * scale), sy0 + 5 * scale], fill=g)
sf.composite(img)

# ---------- 冷知识：混合字体分段绘制 ----------
def family_for(tok):
    if tok.isascii():
        return "sans"
    if all(ch in SUPERSCRIPT_SET or ch.isdigit() for ch in tok):
        return "sans"
    return "cjk-tc"

def tokenize(text):
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isdigit() and i + 1 < n and text[i + 1] in SUPERSCRIPT_SET:
            tokens.append(text[i:i + 2])
            i += 2
        elif ch.isascii():
            j = i
            while j < n and text[j].isascii():
                j += 1
            tokens.append(text[i:j])
            i = j
        else:
            tokens.append(ch)
            i += 1
    return tokens

def draw_mixed_block(cx, y0, text, size, fill, role, max_w, line_gap=10):
    toks = tokenize(text)
    measured = []
    for tok in toks:
        fam = family_for(tok)
        w, h = sf.measure(tok, fam, size)
        measured.append((tok, fam, w, h))

    lines = []
    cur = []
    cur_w = 0.0
    for item in measured:
        tw = item[2]
        if cur and cur_w + tw > max_w:
            lines.append(cur)
            cur = [item]
            cur_w = tw
        else:
            cur.append(item)
            cur_w += tw
    if cur:
        lines.append(cur)

    y = y0
    for line in lines:
        line_w = sum(item[2] for item in line)
        x = cx - line_w / 2.0
        line_h = max(item[3] for item in line)
        for tok, fam, tw, th in line:
            sf.text(x, y, tok, family=fam, size=size, fill=fill,
                    anchor="lt", role=role, allow_overlap=True)
            x += tw
        y += line_h + line_gap

fact_y = sep_y + 82
draw_mixed_block(500, fact_y, FACT, 31, (70, 74, 69), "body", max_w=740)

# ---------- 编号与日期 ----------
sf.serial(110, 1470, SERIAL, family="cjk-tc", size=17,
          fill=(100, 100, 94), anchor="lb", role="meta")
sf.datestamp(890, 1470, DATE, family="cjk-tc", size=17,
             fill=(100, 100, 94), anchor="rb", role="meta")

sf.save(OUT_PATH)
