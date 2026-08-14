from atelier_canvas import Surface

sf = Surface(1000, 1700, scale=2, bg=(230, 212, 166))

import math
import numpy as np
from PIL import Image, ImageDraw

LW, LH = 1000, 1700
P = 2
sf.frame(90, 90, 820, 1520)

qparts = QUOTE.split("\n")
quote_ja = qparts[0].strip()
quote_zh = qparts[1].strip() if len(qparts) > 1 else ""

fpos = FACT.rfind("（麦格克效应")
if fpos >= 0:
    fact_ja = FACT[:fpos].strip()
    fact_zh = FACT[fpos:].strip()
else:
    fact_ja = FACT
    fact_zh = ""

# ---- 固定排版坐标（不再依赖 measure 估算，避免重叠）----
qbox_top = 400
q_ja_y = 445
q_zh_y = 555
qbox_bottom = 645
sep_y = qbox_bottom + 42
fact_y0 = sep_y + 40

lay = sf.layer()
AH, AW = lay.shape[0], lay.shape[1]
lay[..., 3] = 255
lay[..., 0] = 230
lay[..., 1] = 212
lay[..., 2] = 166

yy = np.linspace(0, 1, AH)[:, None]
xx = np.linspace(0, 1, AW)[None, :]
dxy = ((xx - 0.5) * 1.15) ** 2 + ((yy - 0.5) * 1.55) ** 2
vig = np.clip(1.0 - 0.55 * dxy, 0.40, 1.0)
fl = lay[..., :3].astype(np.float32) * vig[..., None]
lay[..., :3] = np.clip(fl, 0, 255).astype(np.uint8)

rng = np.random.RandomState(20260815)
noise = rng.normal(0, 5, (AH, AW, 1))
fl = lay[..., :3].astype(np.float32) + noise
lay[..., :3] = np.clip(fl, 0, 255).astype(np.uint8)

sm = rng.rand(AH, AW) < 0.003
rr = lay[..., 0].astype(np.int16); rr[sm] -= 16
gg = lay[..., 1].astype(np.int16); gg[sm] -= 12
bb = lay[..., 2].astype(np.int16); bb[sm] -= 7
lay[..., 0] = np.clip(rr, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(gg, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(bb, 0, 255).astype(np.uint8)

img = Image.fromarray(lay, "RGBA")
d = ImageDraw.Draw(img)

def L(v):
    return int(round(v * P))

for gx in range(L(180), AW, L(180)):
    d.line([(gx, 0), (gx, AH)], fill=(156, 124, 80, 55), width=1)
for gy in range(L(180), AH, L(180)):
    d.line([(0, gy), (AW, gy)], fill=(156, 124, 80, 55), width=1)

rcx, rcy = L(830), L(300)
for k in range(16):
    rad = math.radians(k * 22.5)
    ex = rcx + math.cos(rad) * AW * 1.3
    ey = rcy + math.sin(rad) * AH * 1.3
    d.line([(rcx, rcy), (ex, ey)], fill=(168, 100, 58, 40), width=1)

edge = (70, 52, 34, 190)
m0 = L(56)
d.rectangle([m0, m0, AW - m0, AH - m0], outline=edge, width=3)
m1 = L(72)
d.rectangle([m1, m1, AW - m1, AH - m1], outline=(70, 52, 34, 120), width=1)
for px, py in [(L(60), L(60)), (AW - L(60), L(60)), (L(60), AH - L(60)), (AW - L(60), AH - L(60))]:
    r4 = L(12)
    d.rectangle([px - r4, py - r4, px + r4, py + r4], outline=(70, 52, 34, 200), width=2)
    r5 = L(24)
    d.polygon([(px, py - r5), (px + r5, py), (px, py + r5), (px - r5, py)], outline=(70, 52, 34, 170))

d.rectangle([L(260), L(112), L(740), L(192)], outline=(70, 52, 34, 210), width=2)
d.rectangle([L(270), L(121), L(730), L(183)], outline=(70, 52, 34, 110), width=1)
d.polygon([(L(480), L(140)), (L(498), L(152)), (L(480), L(164)), (L(462), L(152))], outline=(70, 52, 34, 200))

def draw_compass(cx, cy, r_big, r_small, col_diag, col_main, col_ring):
    for k in range(4):
        deg = 22.5 + k * 45
        rad = math.radians(deg)
        tip = (cx + math.cos(rad) * r_big, cy + math.sin(rad) * r_big)
        s1 = (cx + math.cos(rad + math.pi / 2) * r_small, cy + math.sin(rad + math.pi / 2) * r_small)
        s2 = (cx + math.cos(rad - math.pi / 2) * r_small, cy + math.sin(rad - math.pi / 2) * r_small)
        d.polygon([tip, s1, (cx, cy), s2], fill=col_diag)
    for deg in (0, 90, 180, 270):
        rad = math.radians(deg)
        tip = (cx + math.cos(rad) * r_big, cy + math.sin(rad) * r_big)
        rs = int(r_small * 1.2)
        s1 = (cx + math.cos(rad + math.pi / 2) * rs, cy + math.sin(rad + math.pi / 2) * rs)
        s2 = (cx + math.cos(rad - math.pi / 2) * rs, cy + math.sin(rad - math.pi / 2) * rs)
        d.polygon([tip, s1, (cx, cy), s2], fill=col_main)
    ring = int(r_small * 1.6)
    d.ellipse([cx - ring, cy - ring, cx + ring, cy + ring], outline=col_ring, width=2)

draw_compass(rcx, rcy, L(95), L(22), (96, 76, 50, 130), (150, 66, 48, 210), (70, 52, 34, 190))
d.ellipse([rcx - L(15), rcy - L(9), rcx + L(15), rcy + L(9)], fill=(238, 226, 198, 230), outline=(70, 52, 34, 180), width=2)
d.ellipse([rcx - L(7), rcy - L(11), rcx + L(7), rcy + L(11)], fill=(52, 72, 100, 230))
d.ellipse([rcx - L(3), rcy - L(5), rcx + L(3), rcy + L(5)], fill=(18, 22, 28, 240))

d.rectangle([L(170), L(qbox_top), L(830), L(qbox_bottom)], fill=(248, 238, 205, 46), outline=(70, 52, 34, 180), width=2)
d.rectangle([L(182), L(qbox_top + 12), L(818), L(qbox_bottom - 12)], outline=(70, 52, 34, 100), width=1)

d.line([(L(180), L(sep_y)), (L(420), L(sep_y))], fill=(70, 52, 34, 180), width=2)
d.line([(L(580), L(sep_y)), (L(820), L(sep_y))], fill=(70, 52, 34, 180), width=2)
d.polygon([(L(500), L(sep_y - 18)), (L(510), L(sep_y)), (L(500), L(sep_y + 18)), (L(490), L(sep_y))], fill=(150, 66, 48, 210))

draw_compass(L(240), L(1410), L(95), L(22), (70, 58, 38, 32), (140, 60, 45, 40), (70, 52, 34, 60))

xs = np.linspace(L(100), AW - L(100), 600)
ts = np.linspace(0, 2 * math.pi * 2.2, 600)
ys1 = L(1585) + L(9) * np.sin(ts)
d.line(list(zip(xs.tolist(), ys1.tolist())), fill=(42, 62, 92, 150), width=3)
ys2 = L(1610) + L(8) * np.sin(ts + 1.0)
d.line(list(zip(xs.tolist(), ys2.tolist())), fill=(42, 62, 92, 90), width=2)

sx, sy = L(800), L(1570)
d.polygon([(sx - L(46), sy), (sx + L(22), sy), (sx + L(4), sy - L(24))], fill=(70, 52, 36, 230))
d.line([(sx - L(18), sy - L(22)), (sx - L(18), sy - L(92))], fill=(70, 52, 36, 220), width=2)
d.polygon([(sx - L(20), sy - L(88)), (sx + L(26), sy - L(54)), (sx - L(20), sy - L(32))], fill=(198, 170, 126, 235))
d.polygon([(sx - L(14), sy - L(96)), (sx + L(2), sy - L(90)), (sx - L(14), sy - L(84))], fill=(150, 66, 48, 230))

sf.composite(img)

serial_w, _ = sf.measure(SERIAL, "serif", 30)
sf.serial(310, 152, SERIAL, family="serif", size=30, fill=(64, 48, 32), anchor="lm")

date_w, _ = sf.measure(DATE, "serif", 30)
sf.datestamp(LW - 294 - date_w, 152, DATE, family="serif", size=30, fill=(64, 48, 32), anchor="lm")

sf.text(500, q_ja_y, quote_ja, family="cjk-jp", size=64, fill=(42, 50, 72), anchor="mt", role="quote")
sf.text(500, q_zh_y, quote_zh, family="cjk-sc", size=34, fill=(92, 80, 62), anchor="mt", role="quote")

y = fact_y0
for ln in sf.wrap(fact_ja, "cjk-jp", 38, 820):
    b = sf.text(500, y, ln, family="cjk-jp", size=38, fill=(52, 44, 36), anchor="mt", role="body")
    y = int(b.bottom) + 16

y += 30
for ln in sf.wrap(fact_zh, "cjk-sc", 31, 820):
    b = sf.text(500, y, ln, family="cjk-sc", size=31, fill=(88, 78, 66), anchor="mt", role="body")
    y = int(b.bottom) + 14

sf.save(OUT_PATH)
