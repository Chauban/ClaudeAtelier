# -*- coding: utf-8 -*-
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

LW, LH = 1000, 1700

sf = Surface(LW, LH, scale=2, bg=(246, 241, 231))
sf.frame(60, 50, 880, 1650)


def extract_parts(text):
    for marker in ("（中文翻译：", "(中文翻译:"):
        idx = text.find(marker)
        if idx != -1:
            return text[:idx].strip(), text[idx:].strip()
    return text.strip(), None


Q_IT, Q_CN = extract_parts(QUOTE)
F_IT, F_CN = extract_parts(FACT)

QL = sf.wrap(Q_IT, "serif", 32, 820)
FL = sf.wrap(F_IT, "sans", 28, 820)
QCL = sf.wrap(Q_CN, "cjk-sc", 24, 820) if Q_CN else []
FCL = sf.wrap(F_CN, "cjk-sc", 22, 820) if F_CN else []

Q_TOP = 850
Q_CN_TOP = Q_TOP + len(QL) * 48 + 40
Q_BOTTOM = Q_CN_TOP + len(QCL) * 36 + 26
F_TOP = Q_BOTTOM + 34
F_CN_TOP = F_TOP + len(FL) * 42 + 14
F_BOTTOM = F_CN_TOP + len(FCL) * 33 + 26

canvas = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))

_rng = np.random.default_rng(7)
_grain = _rng.normal(0, 1, (LH, LW, 3))
_grain = np.clip(_grain * 4 + 126, 0, 255).astype(np.uint8)
_gimg = np.zeros((LH, LW, 4), dtype=np.uint8)
_gimg[..., :3] = _grain
_gimg[..., 3] = 14
canvas.alpha_composite(Image.fromarray(_gimg, "RGBA"))


def draw_paper(draw_fn, fill, offset=(10, 14), blur=20, strength=0.38, bbox=None):
    if bbox is not None:
        bx0 = max(0, int(bbox[0] + offset[0] - blur - 8))
        by0 = max(0, int(bbox[1] + offset[1] - blur - 8))
        bx1 = min(LW, int(bbox[2] + offset[0] + blur + 8) + 1)
        by1 = min(LH, int(bbox[3] + offset[1] + blur + 8) + 1)
        bw, bh = bx1 - bx0, by1 - by0
        sh = Image.new("RGBA", (max(1, bw), max(1, bh)), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        draw_fn(sd, (0, 0, 0, 255), (offset[0] - bx0, offset[1] - by0))
        sh = sh.filter(ImageFilter.GaussianBlur(blur))
        a = sh.getchannel("A").point(lambda v: int(v * strength))
        sh.putalpha(a)
        canvas.alpha_composite(sh, (bx0, by0))
    else:
        sh = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        draw_fn(sd, (0, 0, 0, 255), offset)
        sh = sh.filter(ImageFilter.GaussianBlur(blur))
        a = sh.getchannel("A").point(lambda v: int(v * strength))
        sh.putalpha(a)
        canvas.alpha_composite(sh)
    d = ImageDraw.Draw(canvas)
    draw_fn(d, fill + (255,), (0, 0))


def circle_points(cx, cy, r, n, phase=-math.pi / 2):
    if n <= 0:
        return []
    return [(cx + r * math.cos(phase + 2 * math.pi * i / n),
             cy + r * math.sin(phase + 2 * math.pi * i / n)) for i in range(n)]


def draw_disc(cx, cy, r, fill, offset=(8, 14), blur=18, strength=0.36):
    def shape(d, col, off):
        d.ellipse([cx - r + off[0], cy - r + off[1], cx + r + off[0], cy + r + off[1]], fill=col)

    draw_paper(shape, fill, offset=offset, blur=blur, strength=strength,
               bbox=(cx - r, cy - r, cx + r, cy + r))
    d = ImageDraw.Draw(canvas)
    d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
              outline=(255, 255, 255, 110), width=2)


def draw_chords(points, line_color, dot_color, lw=2, dot_r=5, off=(2, 3), blur=4, strength=0.45):
    segs = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            segs.append((points[i], points[j]))
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    bx0 = max(0, int(min(xs) - dot_r + off[0] - blur - 4))
    by0 = max(0, int(min(ys) - dot_r + off[1] - blur - 4))
    bx1 = min(LW, int(max(xs) + dot_r + off[0] + blur + 4) + 1)
    by1 = min(LH, int(max(ys) + dot_r + off[1] + blur + 4) + 1)
    sh = Image.new("RGBA", (max(1, bx1 - bx0), max(1, by1 - by0)), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for (x1, y1), (x2, y2) in segs:
        sd.line([x1 + off[0] - bx0, y1 + off[1] - by0, x2 + off[0] - bx0, y2 + off[1] - by0],
                fill=(0, 0, 0, 255), width=lw)
    for (x, y) in points:
        sd.ellipse([x + off[0] - dot_r - bx0, y + off[1] - dot_r - by0,
                    x + off[0] + dot_r - bx0, y + off[1] + dot_r - by0], fill=(0, 0, 0, 255))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    a = sh.getchannel("A").point(lambda v: int(v * strength))
    sh.putalpha(a)
    canvas.alpha_composite(sh, (bx0, by0))

    d = ImageDraw.Draw(canvas)
    for (x1, y1), (x2, y2) in segs:
        d.line([x1, y1, x2, y2], fill=line_color + (255,), width=lw)
    for (x, y) in points:
        d.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r],
                  fill=dot_color + (255,), outline=(255, 255, 255, 160), width=1)


def draw_mountain(base_y, color, amp, phase, offset=(10, 14), blur=16, strength=0.34):
    pts = []
    for x in range(-20, LW + 21, 5):
        y = base_y + amp * (0.62 * math.sin(x * 0.013 + phase) + 0.38 * math.sin(x * 0.029 + phase * 1.9))
        pts.append((x, y))
    ys = [p[1] for p in pts] + [LH]
    bbox = (-20, min(ys), LW + 20, LH)

    def shape(d, col, off):
        poly = [(px + off[0], py + off[1]) for px, py in pts]
        poly.append((LW + 20, LH + 20))
        poly.append((-20, LH + 20))
        d.polygon(poly, fill=col)

    draw_paper(shape, color, offset=offset, blur=blur, strength=strength, bbox=bbox)


d = ImageDraw.Draw(canvas)

d.rounded_rectangle([60, 54, 940, 70], radius=6, fill=(222, 211, 190, 230),
                    outline=(170, 150, 125, 100))

small_centers = [(110, 225), (300, 225), (490, 225), (680, 225), (870, 225)]
small_r = 38
for i, (cx, cy) in enumerate(small_centers):
    n = i + 1
    pts = circle_points(cx, cy, small_r, n)
    draw_disc(cx, cy, small_r, (255, 252, 243))
    if n >= 2:
        draw_chords(pts, (180, 138, 96), (112, 80, 58), lw=1, dot_r=3, off=(1, 2), blur=3, strength=0.4)
    else:
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(112, 80, 58, 255),
                  outline=(255, 255, 255, 160), width=1)

C1 = (330, 500)
r1 = 140
p5 = circle_points(C1[0], C1[1], r1, 5)
draw_disc(C1[0], C1[1], r1, (255, 252, 243))
draw_chords(p5, (166, 124, 82), (88, 60, 42), lw=2, dot_r=5, off=(3, 4), blur=5, strength=0.5)

C2 = (670, 520)
r2 = 150
p6 = circle_points(C2[0], C2[1], r2, 6, phase=-math.pi / 2)
draw_disc(C2[0], C2[1], r2, (255, 250, 239))
draw_chords(p6, (122, 84, 52), (70, 44, 30), lw=2, dot_r=5, off=(3, 4), blur=5, strength=0.5)

d.line([492, 502, 508, 518], fill=(160, 60, 40, 255), width=3)
d.line([508, 502, 492, 518], fill=(160, 60, 40, 255), width=3)

C3 = (500, 730)
r3 = 85
p7 = circle_points(C3[0], C3[1], r3, 7, phase=-math.pi / 2)
draw_disc(C3[0], C3[1], r3, (248, 240, 225))
draw_chords(p7, (158, 116, 78), (92, 64, 44), lw=1, dot_r=4, off=(2, 3), blur=4, strength=0.42)

dias = [(150, 648), (850, 648), (150, 786), (850, 786)]
for (dx, dy) in dias:
    d.polygon([(dx, dy - 9), (dx + 11, dy), (dx, dy + 9), (dx - 11, dy)],
              fill=(196, 178, 152, 220), outline=(120, 100, 80, 120))

draw_mountain(1575, (228, 220, 202), 30, 0.0, (12, 16), 16, 0.32)
draw_mountain(1625, (218, 208, 188), 35, 2.1, (10, 14), 14, 0.34)
draw_mountain(1668, (207, 196, 174), 40, 4.2, (8, 12), 12, 0.36)

d.rounded_rectangle([60, 1612, 940, 1636], radius=8, fill=(222, 211, 190, 235),
                    outline=(170, 150, 125, 110))
d.line([60, 1614, 940, 1614], fill=(170, 150, 125, 90), width=1)
d.line([60, 1634, 940, 1634], fill=(170, 150, 125, 90), width=1)

for i in range(18):
    x0 = 60 + i * 30
    x1 = x0 + 20
    y0 = Q_TOP - 24
    y1 = y0 + 5 * math.sin(i * 1.3)
    d.line([x0, y0, x1, y1], fill=(170, 150, 125, 160), width=2)

canvas = canvas.resize((sf.W, sf.H), Image.LANCZOS)
sf.composite(canvas, mode="normal", opacity=1.0)

sf.text(60, Q_TOP, Q_IT, family="serif", size=32, fill=(56, 42, 30),
        anchor="lt", role="quote", max_w=820, line_gap=0.35)
if Q_CN:
    sf.text(60, Q_CN_TOP, Q_CN, family="cjk-sc", size=24, fill=(100, 82, 62),
            anchor="lt", role="meta", max_w=820, line_gap=0.35)

sf.text(60, F_TOP, F_IT, family="sans", size=28, fill=(64, 50, 38),
        anchor="lt", role="body", max_w=820, line_gap=0.35)
if F_CN:
    sf.text(60, F_CN_TOP, F_CN, family="cjk-sc", size=22, fill=(100, 82, 62),
            anchor="lt", role="meta", max_w=820, line_gap=0.35)

sf.serial(60, 1646, SERIAL, family="serif", size=20, fill=(68, 52, 38),
          anchor="lt", role="meta")
sf.datestamp(940, 1646, DATE, family="serif", size=20, fill=(68, 52, 38),
             anchor="rt", role="meta")

sf.save(OUT_PATH)
