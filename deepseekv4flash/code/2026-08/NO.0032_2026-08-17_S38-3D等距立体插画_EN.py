import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 1040, 1720
sf = Surface(W, H, scale=2, bg=(30, 36, 54))
sf.frame(56, 40, W - 112, H - 80)

SS = 3.0
GW, GH = int(W * SS), int(H * SS)
ox, oy = 520.0, 760.0
dx, dy, dz = 72.7, 42.0, 72.0


def proj(gx, gy, gz=0.0):
    return (ox + (gx - gy) * dx, oy + (gx + gy) * dy - gz * dz)


def P(gx, gy, gz=0.0):
    sx, sy = proj(gx, gy, gz)
    return (int(round(sx * SS)), int(round(sy * SS)))


scene = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
draw = ImageDraw.Draw(scene)

# faint isometric ground grid
for gx in range(-8, 9):
    draw.line([P(gx, -3.6), P(gx, 3.6)], fill=(150, 148, 130, 20), width=2)
for gy in range(-3, 4):
    draw.line([P(-7.2, gy), P(7.2, gy)], fill=(150, 148, 130, 20), width=2)

# soft shadows on the ground plane
shadow = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
cxp, cyp = P(0, 0, 0)
sd.ellipse([cxp - int(330 * SS), cyp - int(205 * SS),
            cxp + int(330 * SS), cyp + int(205 * SS)], fill=(8, 10, 18, 62))


def blob(gx, gy, size, alpha=56):
    sx, sy = P(gx, gy, 0)
    rxx = int(size * dx * SS * 1.15)
    ryy = int(size * dy * SS * 1.15)
    sd.ellipse([sx - rxx, sy - ryy, sx + rxx, sy + ryy], fill=(8, 10, 18, alpha))


blob(-4.7, -2.2, 0.32, 40)
blob(-3.8, -0.6, 0.5)
blob(-3.2, 1.4, 0.7)
blob(3.4, -1.2, 0.55)
blob(1.6, 2.6, 0.5)
blob(4.4, 0.6, 0.5)
shadow = shadow.filter(ImageFilter.GaussianBlur(24))
scene.alpha_composite(shadow)


def dashed(p1, p2, col=(205, 195, 165, 40), width=2, dash=10, gap=8):
    x1, y1 = p1
    x2, y2 = p2
    L = math.hypot(x2 - x1, y2 - y1)
    if L < 2:
        return
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    t = 0.0
    while t < L:
        e = min(t + dash, L)
        draw.line([(x1 + ux * t, y1 + uy * t), (x1 + ux * e, y1 + uy * e)],
                  fill=col, width=int(width * SS))
        t += dash + gap


STONE = ((232, 211, 168), (197, 165, 119), (151, 119, 81))
STONE2 = ((224, 202, 158), (188, 155, 108), (142, 110, 73))
STONE3 = ((240, 222, 183), (202, 171, 125), (156, 123, 85))
TERR = ((230, 126, 92), (194, 95, 66), (148, 69, 48))
TERR2 = ((216, 108, 80), (178, 84, 58), (132, 62, 42))
OAK = ((198, 164, 118), (152, 122, 84), (108, 86, 60))
OAK2 = ((210, 180, 138), (166, 136, 98), (122, 96, 66))

plinth = [
    (0, 0, 0, 6.0, 2.4, 0.5, STONE),
    (0, 0, 0.5, 4.0, 1.7, 0.5, STONE2),
    (0, 0, 1.0, 2.6, 1.1, 0.45, STONE3),
]

floaters = [
    (-4.7, -2.2, 1.7, 0.32, 0.32, 0.32, TERR2),
    (-3.8, -0.6, 1.0, 0.5, 0.5, 0.5, TERR),
    (-3.2, 1.4, 0.6, 0.7, 0.7, 0.7, OAK),
    (3.4, -1.2, 1.2, 0.55, 0.55, 0.55, TERR2),
    (1.6, 2.6, 0.1, 0.5, 0.5, 0.5, OAK2),
    (4.4, 0.6, 0.35, 0.5, 0.5, 0.45, STONE),
]

all_blocks = sorted(plinth + floaters, key=lambda b: (b[0] + b[1], b[2]))


def cube_block(cx, cy, z0, w, d, h, pal):
    zt = z0 + h
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = cy - d / 2, cy + d / 2
    top_c = [P(x0, y0, zt), P(x1, y0, zt), P(x1, y1, zt), P(x0, y1, zt)]
    left_c = [P(x0, y0, zt), P(x0, y1, zt), P(x0, y1, z0), P(x0, y0, z0)]
    right_c = [P(x0, y1, zt), P(x1, y1, zt), P(x1, y1, z0), P(x0, y1, z0)]
    top_col, left_col, right_col = pal
    draw.polygon(left_c, fill=left_col)
    draw.polygon(right_c, fill=right_col)
    draw.polygon(top_c, fill=top_col)
    edge = tuple(max(0, c - 55) for c in top_col)
    draw.line(left_c + [left_c[0]], fill=edge, width=int(SS * 2))
    draw.line(right_c + [right_c[0]], fill=edge, width=int(SS * 2))
    draw.line(top_c + [top_c[0]], fill=edge, width=int(SS * 2))
    sheen = tuple(min(255, c + 28) for c in top_col)
    draw.line([P(x0, y1, zt), P(x1, y1, zt)], fill=sheen, width=int(SS * 3))


for cub in floaters:
    gx, gy, gz = cub[0], cub[1], cub[2]
    dashed(P(gx, gy, gz), P(gx, gy, 0))

for cub in all_blocks:
    cube_block(*cub)

# wooden bucket on the top step
bgsx, bgsy = P(0, 0, 1.45)
btpx, btpy = bgsx, int(bgsy - 46 * SS)
rxb, ryb = int(63 * SS), int(36 * SS)

draw.ellipse([bgsx - int(60 * SS), bgsy - int(24 * SS),
              bgsx + int(62 * SS), bgsy + int(28 * SS)], fill=(10, 12, 20, 90))

steps = 10
pts_l = [(btpx - rxb, btpy)]
for i in range(steps + 1):
    th = math.pi - (math.pi / 2) * (i / steps)
    pts_l.append((btpx + rxb * math.cos(th), btpy + ryb * math.sin(th)))
pts_l += [(btpx, bgsy), (btpx - rxb, bgsy)]
draw.polygon(pts_l, fill=(172, 120, 74))

pts_r = [(btpx + rxb, btpy)]
for i in range(steps + 1):
    th = (math.pi / 2) * (i / steps)
    pts_r.append((btpx + rxb * math.cos(th), btpy + ryb * math.sin(th)))
pts_r += [(btpx, bgsy), (btpx + rxb, bgsy)]
draw.polygon(pts_r, fill=(126, 84, 49))

draw.line([(btpx, btpy + ryb), (btpx, bgsy)], fill=(110, 72, 42), width=int(2 * SS))
draw.line([(btpx - rxb, btpy), (btpx - rxb, bgsy)], fill=(96, 62, 36), width=int(2 * SS))
draw.line([(btpx + rxb, btpy), (btpx + rxb, bgsy)], fill=(96, 62, 36), width=int(2 * SS))
draw.line([(btpx - rxb, bgsy), (btpx + rxb, bgsy)], fill=(40, 26, 16, 170), width=int(2 * SS))

band_col = (96, 62, 36)
for f, wd in [(0.40, 6), (0.72, 6)]:
    by = btpy + ryb * f
    hw = rxb * math.sqrt(max(0.0, 1 - f * f))
    draw.line([(btpx - hw, by), (btpx + hw, by)], fill=band_col, width=int(wd * SS))

irx, iry = int(rxb * 0.66), int(ryb * 0.62)
draw.ellipse([btpx - irx, btpy - iry, btpx + irx, btpy + iry], fill=(62, 40, 24))
draw.arc([btpx - irx, btpy - iry, btpx + irx, btpy + iry],
         start=180, end=360, fill=(44, 28, 16), width=int(3 * SS))
draw.ellipse([btpx - rxb, btpy - ryb, btpx + rxb, btpy + ryb],
             outline=(222, 176, 122), width=int(4 * SS))
draw.arc([btpx - 45 * SS, btpy - 78 * SS, btpx + 45 * SS, btpy + 28 * SS],
         start=180, end=360, fill=(198, 154, 102), width=int(5 * SS))
draw.line([(btpx - rxb + 8 * SS, btpy + 20 * SS),
           (btpx - rxb + 11 * SS, bgsy - 6 * SS)],
          fill=(235, 190, 138, 110), width=int(2 * SS))

# small dice beside the bucket
dice = [
    (0.72, -0.18, 1.45, 0.22, 0.22, 0.22, TERR),
    (-0.85, 0.3, 1.45, 0.18, 0.18, 0.26, OAK2),
]
for dc in dice:
    cube_block(*dc)

# top rule, footer rule, corner brackets
for x0, x1 in [(60, 478), (562, 980)]:
    draw.line([(x0 * SS, 100 * SS), (x1 * SS, 100 * SS)],
              fill=(150, 140, 115, 180), width=int(SS * 1.5))
r = int(11 * SS)
draw.polygon([(520 * SS, (100 - 11) * SS), (520 * SS + r, 100 * SS),
              (520 * SS, (100 + 11) * SS), (520 * SS - r, 100 * SS)],
             fill=(216, 140, 96, 235))

draw.line([(60 * SS, 1692 * SS), (980 * SS, 1692 * SS)],
          fill=(150, 140, 115, 150), width=int(SS))
r2 = int(7 * SS)
draw.polygon([(520 * SS, (1692 - 7) * SS), (520 * SS + r2, 1692 * SS),
              (520 * SS, (1692 + 7) * SS), (520 * SS - r2, 1692 * SS)],
             fill=(216, 140, 96, 220))

for cx, cy in [(36, 36), (W - 36, 36), (36, H - 36), (W - 36, H - 36)]:
    draw.line([(cx * SS, cy * SS), (cx * SS, (cy + 22) * SS)],
              fill=(150, 140, 115, 170), width=int(SS * 2))
    draw.line([(cx * SS, cy * SS), ((cx + 22) * SS, cy * SS)],
              fill=(150, 140, 115, 170), width=int(SS * 2))

# flatten onto background colour before downsampling (avoids dark fringes)
scene_img = Image.new("RGBA", (GW, GH), (30, 36, 54, 255))
scene_img.alpha_composite(scene)
scene_img = scene_img.resize((W * 2, H * 2), Image.LANCZOS)
sf.composite(scene_img, opacity=1.0)

# vignette
vig = sf.layer()
hh, ww = vig.shape[0], vig.shape[1]
yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
dxn = (xx - ww / 2) / (ww * 0.52)
dyn = (yy - hh / 2) / (hh * 0.52)
d = np.sqrt(dxn * dxn + dyn * dyn)
vig[..., 0] = 16
vig[..., 1] = 20
vig[..., 2] = 32
vig[..., 3] = np.clip((d - 0.55) * 110, 0, 110).astype(np.uint8)
sf.composite(vig)

# light grain
grain = sf.layer()
rng = np.random.default_rng(3)
noise = rng.integers(0, 255, size=(grain.shape[0], grain.shape[1]), dtype=np.uint8)
grain[..., 0] = 220
grain[..., 1] = 215
grain[..., 2] = 195
grain[..., 3] = np.where(noise < 60, 12, 0).astype(np.uint8)
sf.composite(grain)

# ---- text ----
idx = FACT.find(" (")
if idx <= 0:
    fact_en, fact_zh = FACT, ""
else:
    fact_en, fact_zh = FACT[:idx], FACT[idx + 1:]

qx = W // 2
qb = sf.text(qx, 1000, QUOTE, family="serif", size=40, fill=(245, 235, 213),
             anchor="mt", role="quote", max_w=880, line_gap=0.42)
fb = sf.text(qx, qb.bottom + 40, fact_en, family="sans", size=28, fill=(215, 204, 176),
             anchor="mt", role="body", max_w=860, line_gap=0.42)
if fact_zh:
    sf.text(qx, fb.bottom + 16, fact_zh, family="cjk-sc", size=22, fill=(190, 180, 154),
            anchor="mt", role="meta", max_w=860, line_gap=0.38)

sf.serial(60, 62, SERIAL, family="mono", size=20, fill=(198, 188, 162),
          anchor="lt", role="meta")
sf.datestamp(W - 60, 62, DATE, family="mono", size=20, fill=(198, 188, 162),
             anchor="rt", role="meta")

sf.save(OUT_PATH)
