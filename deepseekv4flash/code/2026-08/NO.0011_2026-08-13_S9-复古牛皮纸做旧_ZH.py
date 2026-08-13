from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 900, 1450
U = 2
sf = Surface(W, H, scale=U, bg=(200, 176, 132))
sf.frame(70, 85, 760, 1280)

rng = np.random.default_rng(20260813)
SW, SH = sf.W, sf.H

yy = np.linspace(0, 1, SH)[:, None]
xx = np.linspace(0, 1, SW)[None, :]

# ===== 牛皮纸基底：轻微渐晕 + 噪点 =====
base = np.empty((SH, SW, 3), dtype=np.float32)
base[..., 0] = 206.0 - 16.0 * yy + 6.0 * np.sin(xx * 11.0)
base[..., 1] = 179.0 - 14.0 * yy + 5.0 * np.sin(xx * 9.0)
base[..., 2] = 131.0 - 11.0 * yy + 4.0 * np.sin(xx * 7.0)
base += rng.normal(0, 5.0, (SH, SW, 3)).astype(np.float32)
lay = sf.layer()
lay[..., :3] = np.clip(base, 0, 255).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# ===== 纸纤维噪点 =====
tex = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
td = ImageDraw.Draw(tex)
for _ in range(2600):
    px = int(rng.uniform(0, SW))
    py = int(rng.uniform(0, SH))
    a = int(rng.uniform(8, 24))
    if rng.random() < 0.5:
        td.point((px, py), fill=(134, 106, 68, a))
    else:
        td.point((px, py), fill=(246, 232, 198, a))
tex = tex.filter(ImageFilter.GaussianBlur(0.6))
sf.composite(tex, opacity=0.85)

# ===== 旧水渍 =====
stain = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
sdd = ImageDraw.Draw(stain)
for _ in range(28):
    cx = rng.uniform(80, SW - 80)
    cy = rng.uniform(80, SH - 80)
    r = rng.uniform(80, 380)
    a = int(rng.uniform(7, 20))
    sdd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(118, 82, 46, a))
for _ in range(9):
    cx = rng.uniform(120, SW - 120)
    cy = rng.uniform(120, SH - 120)
    r = rng.uniform(70, 240)
    a = int(rng.uniform(6, 14))
    sdd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 228, 194, a))
stain = stain.filter(ImageFilter.GaussianBlur(60))
sf.composite(stain, opacity=0.9)

# ===== 折痕 =====
fold = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
fld = ImageDraw.Draw(fold)
for yp in (360, 760, 1140):
    yp = yp * U
    fld.line([0, yp, SW, yp], fill=(78, 50, 30, 26), width=U * 2)
    fld.line([0, yp + U * 2, SW, yp + U * 2], fill=(255, 246, 216, 18), width=U * 2)
fold = fold.filter(ImageFilter.GaussianBlur(2.0 * U))
sf.composite(fold)

# ===== 暗角 =====
vig = sf.layer()
dd = np.sqrt(((xx - 0.5) * 1.4) ** 2 + ((yy - 0.5) * 1.0) ** 2)
vv = np.clip((dd - 0.42) / 0.58, 0.0, 1.0) ** 1.25
vig[..., 0] = (66 * vv).astype(np.uint8)
vig[..., 1] = (44 * vv).astype(np.uint8)
vig[..., 2] = (24 * vv).astype(np.uint8)
vig[..., 3] = (235 * vv).astype(np.uint8)
sf.composite(vig)

# ===== 做旧边框 =====
M = 90
MP = M * U
frame = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
fdd = ImageDraw.Draw(frame)
fdd.rectangle([MP, MP, SW - MP, SH - MP], outline=(82, 56, 34, 230), width=U * 5)
fdd.rectangle([MP + 10 * U, MP + 10 * U, SW - MP - 10 * U, SH - MP - 10 * U],
              outline=(82, 56, 34, 120), width=U * 3)
frame = frame.filter(ImageFilter.GaussianBlur(1.0 * U))
sf.composite(frame, opacity=0.9)

# 边框磨损
wear = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
wdd = ImageDraw.Draw(wear)
for _ in range(16):
    side = int(rng.integers(0, 4))
    t = rng.uniform(0.15, 0.85)
    if side == 0:
        wx, wy = SW * t, MP
    elif side == 1:
        wx, wy = SW * t, SH - MP
    elif side == 2:
        wx, wy = MP, SH * t
    else:
        wx, wy = SW - MP, SH * t
    r = rng.uniform(44, 120)
    wdd.ellipse([wx - r, wy - r, wx + r, wy + r], fill=(200, 176, 132, 255))
wear = wear.filter(ImageFilter.GaussianBlur(4.0 * U))
sf.composite(wear, opacity=0.85)

# ===== 水墨夜空：银河光带（收窄避开文字区） =====
sky = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
skd = ImageDraw.Draw(sky)
skd.ellipse([60 * U, 80 * U, 840 * U, 560 * U], fill=(52, 64, 84, 95))
skd.ellipse([140 * U, 130 * U, 760 * U, 480 * U], fill=(42, 52, 70, 75))
sky = sky.filter(ImageFilter.GaussianBlur(42 * U))
sf.composite(sky)

milky = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
mdd = ImageDraw.Draw(milky)
for i in range(90):
    t = i / 89.0
    mx = 240 + t * 430
    my = 210 + t * 240 + np.sin(t * np.pi * 2.0) * 28
    r = (11 + 16 * np.sin(t * np.pi)) * 2 * U
    a = int((12 + 18 * np.sin(t * np.pi)) * 1.8)
    mdd.ellipse([(mx - r) * U, (my - r) * U, (mx + r) * U, (my + r) * U],
                fill=(234, 228, 202, a))
milky = milky.filter(ImageFilter.GaussianBlur(20 * U))
sf.composite(milky, mode="screen", opacity=0.5)

stars = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
stdd = ImageDraw.Draw(stars)
for _ in range(55):
    sx = rng.uniform(150, 780) * U
    sy = rng.uniform(160, 460) * U
    sr = rng.uniform(1.0, 4.5) * U
    sa = int(rng.uniform(35, 120))
    stdd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 252, 238, sa))
stars = stars.filter(ImageFilter.GaussianBlur(1.6 * U))
sf.composite(stars, mode="screen", opacity=0.9)

# ===== 蜣螂与粪球剪影 =====
INKB = (56, 36, 22)
beetle = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
bdd = ImageDraw.Draw(beetle)

bx, by, br = 265, 1105, 36
bdd.ellipse([U * (bx - br), U * (by - br), U * (bx + br), U * (by + br)], fill=INKB + (255,))
bdd.ellipse([U * (bx - 12), U * (by - 18), U * (bx + 7), U * (by + 4)], fill=(122, 94, 62, 255))

cx, cy = 380, 1092
bdd.ellipse([U * (cx - 52), U * (cy - 36), U * (cx + 42), U * (cy + 36)], fill=INKB + (255,))
bdd.ellipse([U * (cx + 30), U * (cy - 27), U * (cx + 58), U * (cy + 22)], fill=INKB + (255,))

# 后腿推球
bdd.line([U * (cx - 25), U * (cy + 32), U * (cx - 42), U * (cy + 46), U * (bx + 18), U * (by - 4)],
         fill=INKB + (255,), width=U * 9)
bdd.line([U * (cx - 18), U * (cy + 35), U * (cx - 30), U * (cy + 56), U * (bx + 26), U * (by + 12)],
         fill=INKB + (255,), width=U * 8)
# 前足
bdd.line([U * (cx + 20), U * (cy + 28), U * (cx + 48), U * (cy + 44)], fill=INKB + (255,), width=U * 8)
bdd.line([U * (cx + 10), U * (cy + 30), U * (cx + 30), U * (cy + 54)], fill=INKB + (255,), width=U * 8)
# 触角
bdd.line([U * (cx + 50), U * (cy - 26), U * (cx + 62), U * (cy - 40)], fill=INKB + (255,), width=U * 4)
bdd.line([U * (cx + 44), U * (cy - 28), U * (cx + 50), U * (cy - 44)], fill=INKB + (255,), width=U * 4)

beetle = beetle.filter(ImageFilter.GaussianBlur(1.4 * U))
sf.composite(beetle)

# 滚动的轨迹
track = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
trd = ImageDraw.Draw(track)
for i in range(34):
    t = i / 33.0
    x0 = (bx + br + 6 + t * (cx - bx - br - 28)) * U
    y0 = (by - 14 + t * (cy - by + 18)) * U
    a = int(150 * (1.0 - t * 0.65))
    trd.line([x0, y0, x0 + 9 * U, y0 + 7 * U], fill=(104, 76, 48, a), width=U * 4)
track = track.filter(ImageFilter.GaussianBlur(1.6 * U))
sf.composite(track, opacity=0.8)

# ===== 底部日期戳 =====
pmark = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
pdd = ImageDraw.Draw(pmark)
dcx, dcy, dr = 450 * U, 1290 * U, 62 * U
for i in range(26):
    ang = i / 26.0 * np.pi * 2.0
    px = dcx + np.cos(ang) * (dr + 18 * U)
    py = dcy + np.sin(ang) * (dr + 18 * U)
    pdd.ellipse([px - 4 * U, py - 4 * U, px + 4 * U, py + 4 * U], fill=(126, 82, 54, 190))
pdd.ellipse([dcx - dr, dcy - dr, dcx + dr, dcy + dr], outline=(126, 82, 54, 200), width=U * 4)
pdd.ellipse([dcx - dr * 0.72, dcy - dr * 0.72, dcx + dr * 0.72, dcy + dr * 0.72],
            outline=(126, 82, 54, 110), width=U * 2)
pmark = pmark.filter(ImageFilter.GaussianBlur(0.8 * U))
sf.composite(pmark, opacity=0.85)

# ===== 右上编号图章：实心深棕，完全包住 serial 文字块 =====
stamp = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
sdd2 = ImageDraw.Draw(stamp)
# serial 文字块约 x 654-787, y 121-167；图章覆盖 x 520-900, y 75-220
sx0, sy0, sx1, sy1 = 520 * U, 75 * U, 900 * U, 220 * U
sdd2.rectangle([sx0, sy0, sx1, sy1], fill=(58, 34, 18, 255))
sdd2.rectangle([sx0, sy0, sx1, sy1], outline=(134, 56, 40, 255), width=U * 5)
sdd2.rectangle([sx0 + 10 * U, sy0 + 10 * U, sx1 - 10 * U, sy1 - 10 * U],
               outline=(134, 56, 40, 130), width=U * 2)
sf.composite(stamp, opacity=1.0)

# ===== 文字层 =====
INK_TXT = (56, 34, 18)
PALE_INK = (255, 249, 235)

sf.serial(721, 144, SERIAL, family="serif-cjk", size=32, fill=PALE_INK,
          anchor="mm", role="meta", bold=True)

quote_size = 46
qlines = sf.wrap(QUOTE, "serif-cjk", quote_size, max_w=700)
qy = 550
for ln in qlines:
    bq = sf.text(450, qy, ln, family="serif-cjk", size=quote_size,
                 fill=INK_TXT, anchor="mt", role="quote")
    qy = int(bq.bottom + quote_size * 0.45)

fact_size = 34
flines = sf.wrap(FACT, "serif-cjk", fact_size, max_w=690)
fy = 720
for ln in flines:
    bf = sf.text(105, fy, ln, family="serif-cjk", size=fact_size,
                 fill=INK_TXT, anchor="lt", role="body")
    fy = int(bf.bottom + fact_size * 0.35)

sf.datestamp(450, 1290, DATE, family="serif-cjk", size=24, fill=INK_TXT,
             anchor="mm", role="meta")

sf.save(OUT_PATH)
