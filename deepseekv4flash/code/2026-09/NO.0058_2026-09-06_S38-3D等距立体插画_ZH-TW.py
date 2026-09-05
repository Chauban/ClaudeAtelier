from atelier_canvas import Surface
import numpy as np
import random
from PIL import Image, ImageDraw

W, H = 1020, 1700
sf = Surface(W, H, scale=2, bg=(9, 9, 30))
sf.frame(60, 54, W - 120, H - 100)

# ---------- sky gradient ----------
grad = sf.layer()
hh = grad.shape[0]
ww = grad.shape[1]
yy = np.linspace(0, 1, hh)
stops_t = [0.0, 0.22, 0.48, 0.72, 1.0]
stops = [
    (8, 8, 30),
    (20, 24, 72),
    (58, 66, 126),
    (34, 36, 92),
    (12, 12, 40),
]
rgb = np.empty((hh, ww, 3), dtype=np.uint8)
for ch in range(3):
    vals = np.interp(yy, stops_t, [c[ch] for c in stops])
    rgb[..., ch] = vals[:, None]
grad[..., :3] = rgb
grad[..., 3] = 255
sf.composite(grad)

# ---------- stars ----------
rng = np.random.default_rng(7)
stars = sf.layer()
n = 150
sy = rng.integers(0, int(2 * 1250), n)
sx = rng.integers(0, 2 * W, n)
brt = rng.integers(120, 255, n)
stars[sy, sx, 0] = brt
stars[sy, sx, 1] = brt
stars[sy, sx, 2] = brt
stars[sy, sx, 3] = brt
sf.composite(stars)

# ---------- red glow behind sprite ----------
glow = sf.layer()
yy2 = np.linspace(0, 1, glow.shape[0])[:, None] * 1500
xx2 = np.linspace(0, 1, glow.shape[1])[None, :] * W
cxg = W * 0.55
cyg = 640.0
d2 = ((xx2 - cxg) / 370.0) ** 2 + ((yy2 - cyg) / 330.0) ** 2
a_int = np.clip(180 * np.exp(-d2), 0, 255).astype(np.uint8)
glow[..., 0] = 255
glow[..., 1] = 102
glow[..., 2] = 70
glow[..., 3] = a_int
sf.composite(glow, mode="screen", opacity=0.9)

# ---------- isometric block artwork ----------
art = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
dd = ImageDraw.Draw(art)
PX = 2


def cube(cx, cy, a, top, lc, rc):
    """One isometric cube: top rhombus + left/right faces."""
    a2 = a * PX
    cx *= PX
    cy *= PX
    hx = 0.8660254 * a2
    hy = a2 * 0.5

    N = (cx, cy - hy)
    E = (cx + hx, cy)
    S = (cx, cy + hy)
    Wp = (cx - hx, cy)
    Eb = (cx + hx, cy + a2)
    Sb = (cx, cy + hy + a2)
    Wb = (cx - hx, cy + a2)

    dd.polygon([N, E, S, Wp], fill=top)
    dd.polygon([E, S, Sb, Eb], fill=rc)
    dd.polygon([Wp, S, Sb, Wb], fill=lc)


# ---------- storm cloud towers (bottom voxel field) ----------
rngc = random.Random(38)

for i, xx in enumerate(range(18, W - 10, 33)):
    xc = xx + rngc.randint(-7, 7)
    dv = np.exp(-((xc - W / 2) / 250.0) ** 2)
    hgt = int(1 + 5.2 * dv + rngc.randint(0, 3))
    top_y = 1410 + (1 - dv) * 150 + rngc.randint(-20, 55)
    cw = 34
    shades = [
        ((150, 145, 215), (80, 78, 150), (52, 54, 110)),
        ((120, 124, 190), (62, 68, 128), (42, 48, 92)),
        ((140, 148, 210), (74, 80, 148), (48, 52, 110)),
    ]
    col = shades[rngc.randint(0, len(shades) - 1)]
    for k in range(hgt):
        cy = top_y + k * cw
        if cy > H + 20:
            break
        cube(xc, cy, cw, col[0], col[1], col[2])

# small stepping white marks above cloud top
for i, x in enumerate(range(220, W, 220)):
    yy0 = 1400 + i * 4
    cube(x, yy0, 22, (255, 246, 220), (235, 210, 180), (190, 165, 140))

# ---------- red sprite: head sheet ----------
spr_colors = [
    ((255, 205, 130), (235, 95, 75), (150, 38, 48)),
    ((255, 170, 105), (215, 80, 68), (138, 34, 50)),
    ((255, 150, 100), (220, 90, 70), (150, 36, 48)),
    ((255, 180, 115), (225, 85, 66), (132, 36, 52)),
]
head_xs = list(range(330, 681, 42))
for idx, x in enumerate(head_xs):
    col = spr_colors[idx % len(spr_colors)]
    yc = 465 + (4 - abs(idx - 4)) * 6
    cube(x, yc, 46, col[0], col[1], col[2])

# ---------- red sprite: hanging tendrils ----------
tendrils = [
    (342, 5), (388, 7), (430, 6), (474, 9),
    (518, 8), (566, 7), (614, 6), (662, 4),
]
for x, depth in tendrils:
    col = spr_colors[(int(x / 40) + 1) % len(spr_colors)]
    a = 30
    base_y = 585.0
    for k in range(depth):
        cy = base_y + k * a
        cube(x, cy, a, col[0], col[1], col[2])

# outer magenta fringe
fringe_x = [410, 456, 502, 548, 594, 640]
fcols = [
    ((255, 120, 150), (190, 60, 100), (118, 30, 78)),
    ((255, 140, 150), (200, 70, 100), (120, 34, 78)),
]
for idx, x in enumerate(fringe_x):
    col = fcols[idx % 2]
    for k in range(3):
        cube(x, 640 + idx * 5 + k * 26, 24, col[0], col[1], col[2])

# drifting sparks
spark_xs = [250, 292, 742, 788, 440, 610, 676]
for i, sx in enumerate(spark_xs):
    col = fcols[i % 2]
    cube(sx, 720 + (i % 3) * 16, 16, col[0], col[1], col[2])

sf.composite(art)

# ---------- subtle dark veil behind lower FACT zone ----------
veil = sf.layer()
yv = np.linspace(0, 1, veil.shape[0])[:, None] * H
av = np.clip(120 * np.exp(-(((yv - 1290) / 190)) ** 2), 0, 255).astype(np.uint8)
veil[..., 0] = 4
veil[..., 1] = 5
veil[..., 2] = 20
veil[..., 3] = av
sf.composite(veil)

# ---------- text ----------
sf.serial(60, 78, SERIAL, family="mono", size=24, fill=(230, 224, 238),
          anchor="lt", role="meta")
sf.datestamp(W - 60, 78, DATE, family="mono", size=24, fill=(230, 224, 238),
             anchor="rt", role="meta")

quote_lines = sf.wrap(QUOTE, "cjk-tc", 58, max_w=W - 180)
qy = 170
for line in quote_lines:
    box = sf.text(W / 2, qy, line, family="cjk-tc", size=58,
                  fill=(245, 236, 226), anchor="mt", role="quote",
                  max_w=W - 180, line_gap=0.5)
    qy = box.bottom + 28

sf.text(W / 2, 1165, FACT, family="cjk-tc", size=30,
        fill=(228, 226, 240), anchor="mt", role="body",
        max_w=W - 140, line_gap=0.5)

sf.save(OUT_PATH)
