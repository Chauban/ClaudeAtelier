import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SERIF_B = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
IDX = 4

S = 2
W, H = 1000, 1600
img = Image.new("RGB", (W * S, H * S), (234, 228, 213))
d = ImageDraw.Draw(img)

def F(path, size, idx=IDX):
    return ImageFont.truetype(path, size * S, index=idx)

def tw(text, font):
    bb = d.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def wrap(text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if tw(cur + ch, font) > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines

# ---------- sand base: subtle noise + vertical tint ----------
arr = np.asarray(img).astype(np.float32)
rng = np.random.default_rng(42)
noise = rng.normal(0, 4.5, (H * S, W * S, 1))
arr = np.clip(arr + noise, 0, 255)
gy = np.linspace(-6, 6, H * S)[:, None, None]
arr = np.clip(arr + gy, 0, 255)
img = Image.fromarray(arr.astype(np.uint8))
d = ImageDraw.Draw(img)

# ---------- raked sand: fine horizontal lines ----------
rake = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
rd = ImageDraw.Draw(rake)
step = 16 * S
for y in range(40 * S, H * S - 40 * S, step):
    rd.line([(50 * S, y), (W * S - 50 * S, y)], fill=(190, 181, 158, 70), width=S)
img = Image.alpha_composite(img.convert("RGBA"), rake)
d = ImageDraw.Draw(img)

# ---------- text first pass: measure layout to know safe zones ----------
INK = (58, 54, 46)
SOFT = (105, 99, 86)

fq = F(SERIF_B, 44)
q_lines = wrap(QUOTE, fq, 780 * S)
ff = F(SERIF, 29)
f_lines = wrap(FACT, ff, 800 * S)

q_top = 170 * S
q_h = len(q_lines) * 74 * S
div_y = q_top + q_h + 40 * S
f_top = div_y + 60 * S
f_h = len(f_lines) * 52 * S
text_bottom = f_top + f_h

# ---------- stones in the clear zone below the text ----------
stones = [
    (310, 1030, 92, 60),
    (435, 1105, 55, 38),
    (690, 1290, 70, 47),
]

rip = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
rd = ImageDraw.Draw(rip)
for (cx, cy, rx, ry) in stones:
    cxS, cyS, rxS, ryS = cx * S, cy * S, rx * S, ry * S
    gap = 15 * S
    for k in range(1, 6):
        rr_x = rxS + gap * k + 12 * S
        rr_y = ryS + gap * k + 12 * S
        if cxS - rr_x < 40 * S or cxS + rr_x > W * S - 40 * S:
            continue
        if cyS - rr_y < text_bottom + 30 * S or cyS + rr_y > H * S - 120 * S:
            continue
        bbox = [cxS - rr_x, cyS - rr_y, cxS + rr_x, cyS + rr_y]
        rd.arc(bbox, 0, 360, fill=(168, 158, 133, 120), width=2 * S)
img = Image.alpha_composite(img, rip)
d = ImageDraw.Draw(img)

# stone shadows
sh = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
sd = ImageDraw.Draw(sh)
for (cx, cy, rx, ry) in stones:
    sd.ellipse([(cx - rx) * S, (cy - ry + 14) * S, (cx + rx) * S, (cy + ry + 14) * S],
               fill=(60, 55, 45, 70))
sh = sh.filter(ImageFilter.GaussianBlur(14 * S))
img = Image.alpha_composite(img, sh)

# stone bodies with vertical shading + highlight
for (cx, cy, rx, ry) in stones:
    x0, y0, x1, y1 = (cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S
    body = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    hh = y1 - y0
    for yy in range(y0, y1):
        t = (yy - y0) / hh
        c = int(150 - 55 * t)
        bd.line([(x0, yy), (x1, yy)], fill=(c, c - 3, c - 10, 255))
    mask = Image.new("L", (W * S, H * S), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([x0, y0, x1, y1], fill=255)
    img.paste(body, (0, 0), mask)
    hi = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.ellipse([cx * S - rx * S * 0.5, cy * S - ry * S * 0.75,
                cx * S + rx * S * 0.1, cy * S - ry * S * 0.2],
               fill=(255, 252, 240, 55))
    hi = hi.filter(ImageFilter.GaussianBlur(8 * S))
    hi.putalpha(Image.composite(hi.split()[3], Image.new("L", hi.size, 0), mask))
    img = Image.alpha_composite(img, hi)
d = ImageDraw.Draw(img)

# ---------- faint enso circle in upper area (kept clear of text) ----------
enso = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
ed = ImageDraw.Draw(enso)
ecx, ecy, er = W * S // 2, 90 * S, 150 * S
for a in range(-40, 250, 2):
    r1 = er - 4 * S
    r2 = er + 4 * S
    p1 = (ecx + r1 * math.cos(math.radians(a)), ecy + r1 * math.sin(math.radians(a)))
    p2 = (ecx + r2 * math.cos(math.radians(a)), ecy + r2 * math.sin(math.radians(a)))
    alpha = int(50 * (1 - abs(a - 105) / 160))
    ed.line([p1, p2], fill=(90, 86, 76, max(alpha, 14)), width=S)
enso = enso.filter(ImageFilter.GaussianBlur(1.2 * S))
img = Image.alpha_composite(img, enso)
d = ImageDraw.Draw(img)

# ---------- draw text on top of everything ----------
y = q_top
for ln in q_lines:
    d.text(((W * S - tw(ln, fq)) / 2, y), ln, font=fq, fill=INK)
    y += 74 * S

# divider: short centered line with generous spacing
d.line([(W * S - 90 * S) / 2, div_y, (W * S + 90 * S) / 2, div_y],
       fill=(150, 140, 118), width=2 * S)

y = f_top
for ln in f_lines:
    d.text(((W * S - tw(ln, ff)) / 2, y), ln, font=ff, fill=SOFT)
    y += 52 * S

# ---------- serial / date as carved inscription ----------
fs = F(SERIF, 24)
meta = SERIAL + "　·　" + DATE
mw = tw(meta, fs)
my = H * S - 110 * S
d.line([(W * S - mw) / 2 - 30 * S, my - 22 * S, (W * S + mw) / 2 + 30 * S, my - 22 * S],
       fill=(180, 170, 146), width=S)
d.text(((W * S - mw) / 2, my), meta, font=fs, fill=(130, 122, 104))
d.line([(W * S - mw) / 2 - 30 * S, my + 44 * S, (W * S + mw) / 2 + 30 * S, my + 44 * S],
       fill=(180, 170, 146), width=S)

img = img.convert("RGB").resize((W, H), Image.LANCZOS)
img.save(OUT_PATH)
