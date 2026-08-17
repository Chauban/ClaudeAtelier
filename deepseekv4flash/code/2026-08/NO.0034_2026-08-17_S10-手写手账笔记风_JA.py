from atelier_canvas import Surface

import math
import numpy as np
from PIL import Image, ImageDraw

W, H = 1000, 1500
sf = Surface(W, H, scale=2, bg=(250, 246, 233))
sf.frame(64, 64, W - 128, H - 128)


def L(x, y):
    return (int(x * 2), int(y * 2))


# ---- split fact into Japanese / Chinese halves ----
zh_marker = "（中文："
fact_jp = FACT
fact_zh = None
if zh_marker in FACT:
    fact_jp, fact_zh = FACT.split(zh_marker, 1)
    fact_zh = zh_marker + fact_zh

# ---- layout metrics ----
quote_size = 38
fact_size = 28
zh_size = 24
qy = 452
jy = 730

fact_lines = sf.wrap(fact_jp, "cjk-jp", fact_size, 830)
n = len(fact_lines)
flh = max(44, (1130 - jy) // n)
fact_bottom = jy + n * flh
fact_zh_y = fact_bottom + 42

if fact_zh:
    zh_lines = sf.wrap(fact_zh, "cjk-sc", zh_size, 780)
    zh_h = len(zh_lines) * 32 + 8
else:
    zh_h = 0
waves_y1 = fact_zh_y + zh_h + 30
waves_y2 = waves_y1 + 62
waves_y3 = waves_y2 + 62

# ---- background paper ----
base = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
base[..., 0] = (252 - 6 * yy).astype(np.uint8)
base[..., 1] = (248 - 8 * yy).astype(np.uint8)
base[..., 2] = (235 - 10 * yy).astype(np.uint8)
base[..., 3] = 255
rng = np.random.default_rng(11)
g = rng.normal(0, 4, (sf.H, sf.W, 1))
base[..., :3] = np.clip(base[..., :3].astype(np.int16) + g, 0, 255).astype(np.uint8)
sf.composite(base)

# ---- hand-drawn decorations ----
art = sf.layer()
d = ImageDraw.Draw(Image.fromarray(art, "RGBA"))

for py in range(90, H - 40, 44):
    for px in range(80, W - 60, 44):
        d.ellipse([px * 2 - 3, py * 2 - 3, px * 2 + 3, py * 2 + 3], fill=(176, 172, 164, 50))


def wavy(d, x0, x1, y, col, w=3, amp=4, ph=0, step=10):
    pts = []
    nx = int((x1 - x0) / step)
    for i in range(nx + 1):
        px = x0 + i * step
        py = y + math.sin(i * 0.7 + ph) * amp
        pts.append(L(px, py))
    d.line(pts, fill=col, width=w, joint="curve")


def shrimp(d, x, y, s, flip, col):
    pts = []
    for k in range(12):
        t = k / 11
        px = x + math.sin(t * 2.6) * 11 * s * (-1 if flip else 1)
        py = y - (t - 0.5) * 30 * s
        pts.append(L(px, py))
    d.line(pts, fill=col, width=max(2, int(3 * s)), joint="curve")
    ex = x + (-1 if flip else 1) * 8 * s
    ey = y - 16 * s
    d.ellipse([L(ex - 2, ey - 2), L(ex + 2, ey + 2)], fill=col)


def star(d, cx, cy, r, fil, rot=0):
    pts = []
    for k in range(10):
        ang = rot + k * math.pi / 5 - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.42
        pts.append(L(cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    d.polygon(pts, fill=fil)


star(d, 250, 300, 26, (244, 200, 120, 210))
d.ellipse([L(170, 230), L(212, 272)], outline=(168, 140, 110, 120), width=3)
d.ellipse([L(320, 210), L(352, 242)], outline=(168, 140, 110, 100), width=2)
d.ellipse([L(150, 350), L(196, 396)], outline=(168, 140, 110, 110), width=3)

# glass sponge illustration
CX, CY = 505, 290
d.rounded_rectangle([L(CX - 66, CY - 88), L(CX + 66, CY + 92)], radius=30, fill=(203, 210, 218, 70))
for i in range(-4, 5):
    yy = CY + i * 22
    pts = []
    for k in range(13):
        t = k / 12
        x0 = CX - 66 + t * 132
        wv = math.sin(t * math.pi * 2) * 2
        pts.append(L(x0, yy + wv))
    d.line(pts, fill=(96, 118, 138, 165), width=3)
for dxp in range(-60, 61, 21):
    pts = []
    for k in range(13):
        t = k / 12
        yy = CY - 88 + t * 180
        bend = -math.sin(math.pi * t) * 9
        pts.append(L(CX + dxp + bend, yy))
    d.line(pts, fill=(96, 118, 138, 165), width=3)
d.line([L(CX - 70, CY - 84), L(CX - 76, CY), L(CX - 68, CY + 90)], fill=(72, 92, 112, 230), width=5, joint="curve")
d.line([L(CX + 70, CY - 84), L(CX + 76, CY), L(CX + 68, CY + 90)], fill=(72, 92, 112, 230), width=5, joint="curve")
d.ellipse([L(CX - 66, CY - 90), L(CX + 66, CY - 68)], outline=(72, 92, 112, 230), width=4)
d.line([L(CX, CY + 88), L(CX, CY + 102)], fill=(72, 92, 112, 200), width=4)
d.ellipse([L(CX - 26, CY + 98), L(CX + 26, CY + 112)], outline=(72, 92, 112, 160), width=3)
shrimp(d, CX - 26, CY + 2, 1.0, False, (178, 92, 56, 230))
shrimp(d, CX + 28, CY - 4, 0.8, True, (178, 92, 56, 230))
for bx, by, br in [(120, 180, 6), (905, 160, 5), (890, 380, 7), (140, 420, 4), (890, 260, 4)]:
    d.ellipse([L(bx - br, by - br), L(bx + br, by + br)], outline=(96, 118, 138, 110), width=2)

# two overlapping rings
gold = (190, 130, 80, 230)
d.ellipse([L(428, 585), L(496, 653)], outline=gold, width=6)
d.ellipse([L(478, 585), L(546, 653)], outline=gold, width=6)
d.ellipse([L(440, 596), L(454, 610)], outline=(230, 180, 120, 190), width=3)

# divider waves under the quote
wavy(d, 100, 880, 674, (148, 144, 138, 170), w=4, amp=5, ph=0)
wavy(d, 100, 880, 695, (148, 144, 138, 120), w=3, amp=5, ph=2.4)

# fact margin line on the left
my = 740
while my < fact_bottom:
    x = 70 + math.sin((my - 740) * 0.09) * 3
    d.line([L(x, my), L(x, my + 5)], fill=(160, 120, 100, 155), width=4)
    my += 8

# bottom waves + free shrimp
wavy(d, 40, 960, waves_y1, (130, 165, 182, 95), w=4, amp=8, ph=0.0)
wavy(d, 40, 960, waves_y2, (130, 165, 182, 75), w=5, amp=12, ph=1.8)
wavy(d, 40, 960, waves_y3, (130, 165, 182, 65), w=6, amp=16, ph=0.9)
shrimp(d, 800, fact_bottom - 44, 1.35, True, (178, 92, 56, 210))
shrimp(d, 868, fact_bottom - 22, 1.05, False, (178, 92, 56, 180))

sf.composite(art)

# ---- sticky notes & tape ----
def make_note(w, h, angle, fill=(255, 238, 170, 240)):
    img = Image.new("RGBA", (int(w * 2), int(h * 2)), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, int(w * 2) - 1, int(h * 2) - 1], radius=10, fill=fill)
    dr.polygon([(int(w * 2) - 30, int(h * 2) - 1), (int(w * 2) - 1, int(h * 2) - 1), (int(w * 2) - 1, int(h * 2) - 30)],
               fill=(226, 200, 130, 255))
    return img.rotate(angle, expand=True, resample=Image.BICUBIC)


def make_tape(w, h, angle, fill=(240, 226, 188, 170)):
    img = Image.new("RGBA", (int(w * 2), int(h * 2)), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 3, int(w * 2) - 1, int(h * 2) - 4], fill=fill)
    nz = 8
    for i in range(nz):
        x0 = int(w * 2) * i // nz
        x1 = int(w * 2) * (i + 1) // nz
        dr.polygon([(x0, 3), (x1, 3), (x1, 0), (x0, 0)], fill=fill)
        dr.polygon([(x0, int(h * 2) - 4), (x1, int(h * 2) - 4), (x1, int(h * 2) - 1), (x0, int(h * 2) - 1)], fill=fill)
    return img.rotate(angle, expand=True, resample=Image.BICUBIC)


def stamp(img, x, y):
    arr = np.array(img)
    ih, iw = arr.shape[:2]
    lay = sf.layer()
    yy, xx = int(y * 2), int(x * 2)
    hh = min(ih, sf.H - yy)
    ww = min(iw, sf.W - xx)
    lay[yy:yy + hh, xx:xx + ww] = arr[:hh, :ww]
    sf.composite(lay)


stamp(make_note(190, 52, -4), 66, 56)
stamp(make_note(200, 52, 3), 722, 58)
stamp(make_tape(90, 26, 10), 134, 70)
stamp(make_tape(80, 24, -8), 780, 190)
stamp(make_tape(110, 26, -5), 790, waves_y1 + 8)

# ---- quote highlighter ----
quote_lines = sf.wrap(QUOTE, "cjk-jp", quote_size, 820)
qlh = 57

hl = sf.layer()
hd = ImageDraw.Draw(Image.fromarray(hl, "RGBA"))
for i, ln in enumerate(quote_lines):
    lw, _ = sf.measure(ln, "cjk-jp", quote_size)
    yy = qy + i * qlh + 24
    xx = 94 + (9 if i % 2 == 1 else 0)
    for off in (-5, 0, 6):
        hd.rectangle([L(xx + off, yy), L(xx + lw + 16 + off, yy + 16)], fill=(250, 216, 92, 55))
sf.composite(hl)

# ---- text layer ----
sf.serial(104, 80, SERIAL, family="sans", size=22, fill=(96, 78, 42, 255),
          anchor="lt", role="meta")
sf.datestamp(838, 82, DATE, family="sans", size=22, fill=(96, 78, 42, 255),
             anchor="rt", role="meta")

q_box = sf.text(90, qy, QUOTE,
                family="cjk-jp", size=quote_size, fill=(58, 52, 46, 255),
                anchor="lt", role="quote", max_w=820, line_gap=0.5)

quote_zh = "即使无法逃出的牢笼，只要两人能在一起，那里便不再是监狱，而是家。"
sf.text(100, q_box.bottom + 14, quote_zh,
        family="cjk-sc", size=zh_size, fill=(110, 96, 88, 255),
        anchor="lt", role="meta", max_w=800, line_gap=0.5)


def draw_fact_mixed(line, x, y, size, fill, flagged):
    """Draw one line mixing cjk-jp for Japanese and cjk-tc for traditional chars."""
    GAP = 2
    cx = x
    rest = line
    while rest:
        pos = -1
        for ch in flagged:
            p = rest.find(ch)
            if p != -1 and (pos == -1 or p < pos):
                pos = p
        if pos == -1:
            sf.text(cx, y, rest, family="cjk-jp", size=size, fill=fill,
                    anchor="lt", role="body")
            break
        if pos > 0:
            part = rest[:pos]
            sf.text(cx, y, part, family="cjk-jp", size=size, fill=fill,
                    anchor="lt", role="body")
            cx += sf.measure(part, "cjk-jp", size)[0] + GAP
        ch = rest[pos]
        sf.text(cx, y, ch, family="cjk-tc", size=size, fill=fill,
                anchor="lt", role="body")
        cx += sf.measure(ch, "cjk-tc", size)[0] + GAP
        rest = rest[pos + 1:]


flagged = set("網長")
cy = jy
for line in fact_lines:
    draw_fact_mixed(line, 90, cy, fact_size, (62, 56, 50, 255), flagged)
    cy += flh

if fact_zh:
    sf.text(112, fact_zh_y, fact_zh,
            family="cjk-sc", size=zh_size, fill=(110, 96, 88, 255),
            anchor="lt", role="meta", max_w=780, line_gap=0.5)

sf.save(OUT_PATH)
