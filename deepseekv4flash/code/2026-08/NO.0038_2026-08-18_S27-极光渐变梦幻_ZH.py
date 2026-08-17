from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 900, 1360
sf = Surface(W, H, scale=2, bg=(5, 7, 28))
sf.frame(70, 50, 760, 1260)

# ---------- night sky ----------
bg = sf.layer()
t = np.linspace(0, 1, sf.H)[:, None]
k1 = np.clip(t * 2, 0, 1)[:, :, None]
k2 = np.clip((t - 0.5) * 2, 0, 1)[:, :, None]
c_top = np.array([6, 10, 34], np.float32)
c_mid = np.array([18, 14, 54], np.float32)
c_bot = np.array([8, 26, 58], np.float32)
col = c_top[None, None, :] * (1 - k1) + c_mid[None, None, :] * k1
col = col * (1 - k2) + c_bot[None, None, :] * k2
bg[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
bg[..., 3] = 255
sf.composite(bg)

# ---------- moon ----------
moon = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dm = ImageDraw.Draw(moon)
mx, my = int(0.76 * sf.W), int(0.12 * sf.H)
mr = 104
dm.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=(240, 245, 255, 210))
dm.ellipse((mx - mr + 18, my - mr + 12, mx - mr + 58, my - mr + 50), fill=(190, 205, 235, 160))
dm.ellipse((mx + 6, my + 16, mx + 46, my + 54), fill=(195, 208, 240, 140))
dm.ellipse((mx - 30, my + 30, mx + 2, my + 60), fill=(188, 202, 232, 130))
moon = moon.filter(ImageFilter.GaussianBlur(5))
halo = moon.filter(ImageFilter.GaussianBlur(90))
sf.composite(halo, mode="screen", opacity=0.45)
sf.composite(moon, mode="screen", opacity=0.95)

# ---------- aurora bands ----------
def aurora(color, cbase, camp, cfreq, cphase, sigma_f, opacity, brightness=1.0):
    lay = sf.layer()
    x = np.arange(sf.W, dtype=np.float32)[None, :]
    ctr = (cbase + camp * np.sin(2 * np.pi * cfreq * x / sf.W + cphase)) * sf.H
    yy = np.arange(sf.H, dtype=np.float32)[:, None]
    sigma = max(6.0, sigma_f * sf.H)
    inten = brightness * np.exp(-0.5 * ((yy - ctr) / sigma) ** 2)
    inten = np.clip(inten, 0, 1)
    lay[..., 0] = (color[0] * inten).astype(np.uint8)
    lay[..., 1] = (color[1] * inten).astype(np.uint8)
    lay[..., 2] = (color[2] * inten).astype(np.uint8)
    lay[..., 3] = (255 * np.clip(inten * 1.15, 0, 1)).astype(np.uint8)
    sf.composite(Image.fromarray(lay, "RGBA").filter(ImageFilter.GaussianBlur(14)), mode="screen", opacity=opacity)

aurora((40, 200, 150), 0.32, 0.08, 1.4, 0.3, 0.032, 0.40)
aurora((90, 255, 190), 0.32, 0.08, 1.4, 0.3, 0.011, 0.50, 0.9)
aurora((140, 90, 255), 0.55, 0.09, 1.1, 2.4, 0.040, 0.38)
aurora((190, 140, 255), 0.55, 0.09, 1.1, 2.4, 0.013, 0.48, 0.9)
aurora((255, 110, 200), 0.78, 0.07, 1.7, 4.0, 0.034, 0.36)
aurora((255, 170, 230), 0.78, 0.07, 1.7, 4.0, 0.011, 0.48, 0.9)
aurora((70, 200, 255), 0.14, 0.06, 2.0, 1.2, 0.030, 0.30)
aurora((80, 220, 255), 0.92, 0.05, 1.5, 5.5, 0.024, 0.24)

# ---------- stars ----------
rng = np.random.default_rng(20260818)
star_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
ds = ImageDraw.Draw(star_img)
for _ in range(240):
    x = int(rng.integers(0, sf.W))
    y = int(rng.integers(0, sf.H))
    r = int(rng.integers(1, 4))
    a = int(rng.integers(55, 210))
    if y < int(0.55 * sf.H) and rng.random() < 0.16:
        rr = int(rng.integers(170, 255))
        gg = min(255, int(rng.integers(160, 235)))
        ds.ellipse((x - r, y - r, x + r, y + r), fill=(rr, gg, 255, a))
    else:
        ds.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, a))
sf.composite(star_img.filter(ImageFilter.GaussianBlur(10)), mode="screen", opacity=0.65)
sf.composite(star_img, mode="screen", opacity=1.0)

# ---------- sparkles & bokeh ----------
spark = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dsp = ImageDraw.Draw(spark)
for _ in range(14):
    x = int(rng.integers(int(0.05 * sf.W), int(0.95 * sf.W)))
    y = int(rng.integers(int(0.05 * sf.H), int(0.75 * sf.H)))
    s = int(rng.integers(8, 22))
    a = int(rng.integers(90, 210))
    dsp.line((x - s, y, x + s, y), fill=(255, 255, 255, a), width=2)
    dsp.line((x, y - s, x, y + s), fill=(255, 255, 255, a), width=2)
sf.composite(spark.filter(ImageFilter.GaussianBlur(2)), mode="screen", opacity=0.9)

bokeh = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
db = ImageDraw.Draw(bokeh)
pal = [(120, 220, 255), (255, 170, 220), (170, 160, 255), (140, 255, 200)]
for _ in range(22):
    x = int(rng.integers(0, sf.W))
    y = int(rng.integers(int(0.04 * sf.H), int(0.96 * sf.H)))
    r = int(rng.integers(18, 70))
    colp = pal[int(rng.integers(0, len(pal)))]
    a = int(rng.integers(16, 46))
    db.ellipse((x - r, y - r, x + r, y + r), fill=(colp[0], colp[1], colp[2], a))
sf.composite(bokeh.filter(ImageFilter.GaussianBlur(45)), mode="screen", opacity=0.50)

# ---------- shooting star ----------
shoot = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dsh = ImageDraw.Draw(shoot)
sx, sy = 0.34 * sf.W, 0.08 * sf.H
ex, ey = 0.16 * sf.W, 0.24 * sf.H
for i in range(60):
    tt = i / 59.0
    px = sx + (ex - sx) * tt
    py = sy + (ey - sy) * tt
    radr = max(1.0, 3.5 * (1 - tt) + 1)
    aa = int(200 * (1 - tt) ** 1.5)
    dsh.ellipse((px - radr, py - radr, px + radr, py + radr), fill=(255, 255, 255, aa))
sf.composite(shoot.filter(ImageFilter.GaussianBlur(3)), mode="screen", opacity=0.85)

# ---------- clean dark panel behind all text ----------
panel_x0, panel_y0, panel_x1, panel_y1 = 90, 330, 810, 1180
mask = Image.new("L", (sf.W, sf.H), 0)
dmask = ImageDraw.Draw(mask)
dmask.rounded_rectangle(
    (panel_x0 * 2, panel_y0 * 2, panel_x1 * 2, panel_y1 * 2),
    radius=40 * 2, fill=255
)
mask_np = np.array(mask, dtype=np.float32) / 255.0  # 2D: (H, W)
panel_arr = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
yy = np.linspace(0, 1, sf.H)[:, None]
panel_arr[..., 0] = np.clip(16 - 8 * yy, 0, 255).astype(np.uint8)
panel_arr[..., 1] = np.clip(22 - 12 * yy, 0, 255).astype(np.uint8)
panel_arr[..., 2] = np.clip(52 - 26 * yy, 0, 255).astype(np.uint8)
panel_arr[..., 3] = (238 * mask_np).astype(np.uint8)
panel_img = Image.fromarray(panel_arr, "RGBA").filter(ImageFilter.GaussianBlur(16))
sf.composite(panel_img, opacity=1.0)

# glowing panel edge
edge = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
de = ImageDraw.Draw(edge)
de.rounded_rectangle(
    (panel_x0 * 2, panel_y0 * 2, panel_x1 * 2, panel_y1 * 2),
    radius=40 * 2, outline=(120, 180, 255, 170), width=5
)
sf.composite(edge.filter(ImageFilter.GaussianBlur(18)), mode="screen", opacity=0.55)
sf.composite(edge, mode="screen", opacity=0.40)

# ---------- small meta chips ----------
def chip(x0, y0, x1, y1):
    img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0 * 2, y0 * 2, x1 * 2, y1 * 2), radius=15 * 2, fill=(10, 16, 45, 180))
    sf.composite(img.filter(ImageFilter.GaussianBlur(6)), opacity=0.95)

chip(70, 60, 180, 98)
chip(700, 60, 830, 98)

# ---------- ornament divider inside panel ----------
orn = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dorn = ImageDraw.Draw(orn)
x0, x1, yor = 330, 570, 670
steps_n = 80
for i in range(steps_n):
    tt = i / (steps_n - 1)
    x = x0 + (x1 - x0) * tt
    rr = int(120 + 110 * tt)
    gg = int(180 + 40 * tt)
    bb = int(255 - 70 * tt)
    dorn.ellipse((x * 2 - 5, yor * 2 - 5, x * 2 + 5, yor * 2 + 5), fill=(rr, gg, bb, 190))
sf.composite(orn.filter(ImageFilter.GaussianBlur(5)), mode="screen", opacity=0.90)

spark2 = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dsp2 = ImageDraw.Draw(spark2)
cx, cy = 450 * 2, yor * 2
dsp2.polygon([(cx, cy - 24), (cx + 7, cy), (cx, cy + 24), (cx - 7, cy)], fill=(255, 255, 255, 230))
dsp2.polygon([(cx - 24, cy), (cx, cy - 7), (cx + 24, cy), (cx, cy + 7)], fill=(255, 255, 255, 185))
for ex2 in (x0 * 2, x1 * 2):
    ey2 = yor * 2
    dsp2.polygon([(ex2, ey2 - 11), (ex2 + 4, ey2), (ex2, ey2 + 11), (ex2 - 4, ey2)], fill=(255, 255, 255, 170))
    dsp2.polygon([(ex2 - 11, ey2), (ex2, ey2 - 4), (ex2 + 11, ey2), (ex2, ey2 + 4)], fill=(255, 255, 255, 130))
sf.composite(spark2.filter(ImageFilter.GaussianBlur(2)), mode="screen", opacity=0.95)

# ---------- text ----------
sf.serial(80, 78, SERIAL, family="sans", size=20, fill=(205, 225, 255), anchor="lt", role="meta")
sf.datestamp(820, 78, DATE, family="sans", size=20, fill=(205, 225, 255), anchor="rt", role="meta")

qlines = ["有些字改了自己的读音，", "只为不让人把绝症听成小病。"]
qy = 420
for i, line in enumerate(qlines):
    fill = (232, 240, 255) if i % 2 == 0 else (255, 232, 242)
    b = sf.text(450, qy, line, family="serif-cjk", size=50, fill=fill, anchor="mt", role="quote", line_gap=0.4)
    qy = b.bottom + 16

flines = sf.wrap(FACT, "cjk-sc", 28, 650)
fy = 800
for line in flines:
    b = sf.text(450, fy, line, family="cjk-sc", size=28, fill=(218, 228, 248), anchor="mt", role="body", line_gap=0.4)
    fy = b.bottom + 8

sf.save(OUT_PATH)
