import numpy as np
from PIL import Image, ImageDraw
from atelier_canvas import Surface

W, H = 1000, 1880
sf = Surface(W, H, scale=2, bg=(247, 241, 228))
sf.frame(70, 70, 860, 1760)

L = 2

def P(x, y):
    return (int(round(x * L)), int(round(y * L)))

def R(a, b, c, d):
    return (int(round(a * L)), int(round(b * L)), int(round(c * L)), int(round(d * L)))

INK = (58, 52, 44, 255)
INK_SOFT = (76, 68, 57, 255)
GREEN = (64, 94, 66, 255)

# ---- paper grain ----
lay = sf.layer()
rng = np.random.default_rng(2026)
mask = rng.random((sf.H, sf.W)) < 0.05
lay[..., 0] = 82
lay[..., 1] = 72
lay[..., 2] = 56
lay[..., 3] = (mask * 38).astype(np.uint8)
sf.composite(lay)

# ---- paper fibres ----
img = Image.fromarray(sf.layer())
d = ImageDraw.Draw(img)
rng2 = np.random.default_rng(48)
for _ in range(2400):
    x = int(rng2.integers(0, sf.W))
    y = int(rng2.integers(0, sf.H))
    ln = int(rng2.integers(6, 44))
    a = int(rng2.integers(10, 36))
    d.line([(x, y), (x + ln, y)], fill=(86, 78, 64, a), width=1)
sf.composite(img)

# ---- main illustration layer ----
img = Image.fromarray(sf.layer())
d = ImageDraw.Draw(img)

# double frame + corner dots
d.rectangle(R(38, 38, W - 38, H - 38), outline=INK, width=4)
d.rectangle(R(52, 52, W - 52, H - 52), outline=INK_SOFT, width=2)
for (acx, acy, adx, ady) in [(52, 52, 1, 1), (W - 52, 52, -1, 1),
                             (52, H - 52, 1, -1), (W - 52, H - 52, -1, -1)]:
    for k in (9, 17, 25):
        d.ellipse(R(acx + adx * k - 2.5, acy + ady * k - 2.5,
                    acx + adx * k + 2.5, acy + ady * k + 2.5),
                  outline=GREEN, width=2)

# engraved sun
sx, sy, sr = 852, 152, 26
d.ellipse(R(sx - sr, sy - sr, sx + sr, sy + sr), fill=(238, 220, 184, 110), outline=INK, width=3)
d.ellipse(R(sx - sr + 7, sy - sr + 7, sx + sr - 7, sy + sr - 7), outline=(58, 52, 44, 140), width=2)
for k in range(12):
    a0 = k * np.pi / 6
    d.line([P(sx + np.cos(a0) * (sr + 8), sy + np.sin(a0) * (sr + 8)),
            P(sx + np.cos(a0) * (sr + 24), sy + np.sin(a0) * (sr + 24))], fill=INK, width=3)

# far mountain ridges
m2 = [(70, 690), (250, 560), (430, 630), (610, 540), (780, 600), (930, 690)]
d.polygon([P(x, y) for x, y in m2], fill=(222, 225, 213, 90), outline=(130, 136, 124, 90), width=2)
m1 = [(70, 690), (170, 480), (310, 610), (480, 440), (650, 580), (810, 490), (930, 690)]
d.polygon([P(x, y) for x, y in m1], fill=(210, 215, 205, 120), outline=(118, 124, 112, 130), width=2)

# penitentes ice blades
ground_y = 690
rng = np.random.default_rng(7)
blades = []
for i in range(15):
    cx = 155 + i * 49 + int(rng.integers(-12, 13))
    base_off = int(rng.integers(-12, 13))
    h = int(rng.integers(80, 151) + 130 * np.exp(-((i - 7.0) / 5.2) ** 2))
    w = int(rng.integers(40, 76))
    tilt = int(rng.integers(-16, 40))
    far = (i % 3 == 0)
    blades.append((cx, base_off, h, w, tilt, far))
blades.sort(key=lambda b: b[2])

for cx, base_off, h, w, tilt, far in blades:
    base = ground_y + base_off
    x_top = cx + tilt
    if far:
        al = 118
        fillc = (250, 248, 242, al)
        shc = (199, 208, 215, al)
        inc = (82, 74, 60, al)
    else:
        al = 255
        fillc = (252, 250, 244, 255)
        shc = (201, 210, 218, 255)
        inc = (62, 56, 46, 255)
    d.ellipse(R(cx - w * 0.85, base - 4, cx + w * 0.85, base + 14),
              fill=(92, 82, 66, int(0.22 * al)))
    tri = [P(cx - w // 2, base), P(x_top, base - h), P(cx + w // 2, base)]
    d.polygon(tri, fill=fillc, outline=inc, width=3)
    shad = [P(cx, base), P(x_top, base - h), P(cx + w // 2, base)]
    d.polygon(shad, fill=shc)
    d.line(tri + [tri[0]], fill=inc, width=3)
    if not far:
        for k in range(1, 4):
            t = k / 4
            hx1 = cx + (x_top - cx) * t
            hy1 = base - h * t
            hx2 = hx1 + w * 0.30
            hy2 = hy1 + h * 0.16
            d.line([P(hx1, hy1), P(hx2, hy2)], fill=inc, width=2)

# ground snow line
gpts = [(x, ground_y + int(5 * np.sin(x / 55) + rng.integers(-3, 4))) for x in range(72, 930, 14)]
d.line([P(x, y) for x, y in gpts], fill=INK, width=4)
d.line([P(72, ground_y + 9), P(928, ground_y + 9)], fill=(110, 100, 82, 70), width=6)

# unlettered scale bar (plate convention)
bx0, by = 180, 748
d.line([P(bx0, by), P(bx0 + 80, by)], fill=INK, width=3)
d.line([P(bx0, by - 7), P(bx0, by + 7)], fill=INK, width=3)
d.line([P(bx0 + 80, by - 7), P(bx0 + 80, by + 7)], fill=INK, width=3)
d.ellipse(R(bx0 + 40 - 3, by - 3, bx0 + 40 + 3, by + 3), fill=INK)

# italic divider
scx, scy = W // 2, 802
d.line([P(scx - 150, scy), P(scx - 18, scy)], fill=INK, width=3)
d.line([P(scx + 18, scy), P(scx + 150, scy)], fill=INK, width=3)
d.polygon([P(scx, scy - 7), P(scx + 7, scy), P(scx, scy + 7), P(scx - 7, scy)], fill=INK)

# specimen labels (bottom)
d.rectangle(R(74, 1684, 336, 1800), fill=(251, 247, 237, 255), outline=INK, width=3)
d.rectangle(R(664, 1684, 926, 1800), fill=(251, 247, 237, 255), outline=INK, width=3)
for pxx in (205, 795):
    d.ellipse(R(pxx - 5, 1678 - 5, pxx + 5, 1678 + 5), fill=(120, 108, 92, 255), outline=INK, width=2)
    d.line([P(pxx - 2, 1678 - 2), P(pxx + 2, 1678 - 2)], fill=(240, 236, 226, 255), width=2)

# small snow-crystal ornament
def crystal(cx, cy, rad, col=INK):
    for k in range(6):
        a0 = np.pi / 3 * k + np.pi / 6
        x1 = cx + np.cos(a0) * rad
        y1 = cy + np.sin(a0) * rad
        d.line([P(cx, cy), P(x1, y1)], fill=col, width=2)
        x2a = cx + np.cos(a0) * rad * 0.5
        y2a = cy + np.sin(a0) * rad * 0.5
        for sgn in (-1, 1):
            a1 = a0 + sgn * np.pi / 4
            d.line([P(x2a, y2a),
                    P(x2a + np.cos(a1) * rad * 0.38, y2a + np.sin(a1) * rad * 0.38)],
                   fill=col, width=2)
    d.ellipse(R(cx - 2, cy - 2, cx + 2, cy + 2), fill=col)

crystal(140, 1616, 15)
crystal(188, 1608, 11)
crystal(152, 1648, 9)
d.line([P(96, 1662), P(214, 1662)], fill=INK_SOFT, width=2)

sf.composite(img)

# ---- subtle vignette ----
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
dist = ((xx - 0.5) * 1.05) ** 2 + ((yy - 0.5) * 1.05) ** 2
ramp = np.clip((dist - 0.10) / 0.38, 0, 1) ** 1.3
lay[..., 0] = 150
lay[..., 1] = 138
lay[..., 2] = 118
lay[..., 3] = (ramp * 22).astype(np.uint8)
sf.composite(lay, mode="multiply")

# ---- text ----
box_q = sf.text(W // 2, 838, QUOTE,
                family="serif", size=33, fill=(44, 68, 52),
                anchor="mt", max_w=824, role="quote")

box_qcn = sf.text(W // 2, box_q.bottom + 26,
                  "有一种雪不会融化：它跪下来，祈祷，然后化作风。",
                  family="cjk-sc", size=23, fill=(108, 96, 80),
                  anchor="mt", max_w=824, role="meta")

sep_idx = FACT.find('（')
if sep_idx != -1:
    fact_es = FACT[:sep_idx].strip()
    fact_zh = FACT[sep_idx:].strip()
else:
    fact_es = FACT.strip()
    fact_zh = "（在干旱的安第斯山脉海拔4000米以上，生长着「忏悔者」：高达5米的硬化积雪刃脊。在极度干燥的空气中，它们不会融化，而是直接升华——冰直接变成水蒸气。其名源于它们酷似圣周游行中戴尖帽的信众；达尔文于1835年穿越其间时首次记录了它们。）"

box_f = sf.text(88, box_qcn.bottom + 52, fact_es,
                family="serif", size=28, fill=(52, 46, 38),
                anchor="lt", max_w=824, role="body")

box_fcn = sf.text(88, box_f.bottom + 30, fact_zh,
                  family="cjk-sc", size=23, fill=(108, 96, 80),
                  anchor="lt", max_w=824, role="meta")

sf.serial(98, 1722, SERIAL, family="serif", size=24, fill=(52, 46, 38), anchor="lt", role="meta")
sf.datestamp(902, 1722, DATE, family="serif", size=24, fill=(52, 46, 38), anchor="rt", role="meta")

sf.save(OUT_PATH)
