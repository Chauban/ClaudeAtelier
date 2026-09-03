from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1200, 1800
sf = Surface(W, H, scale=2, bg=(16, 12, 10))

def img_actual(img):
    if img.size != (sf.W, sf.H):
        return img.resize((sf.W, sf.H), Image.LANCZOS)
    return img

# Base: dark warm gradient with top glow
xx = np.linspace(0, 1, W)[None, :]
yy = np.linspace(0, 1, H)[:, None]
glow = np.exp(-((xx - 0.55) ** 2 + (yy - 0.10) ** 2) * 16)
arr = np.zeros((H, W, 3), dtype=np.float32)
arr[..., 0] = 18 + 8 * yy + 42 * glow
arr[..., 1] = 14 + 6 * yy + 30 * glow
arr[..., 2] = 12 + 5 * yy + 20 * glow
base = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGB').convert('RGBA')
sf.composite(img_actual(base), mode="normal", opacity=1.0)

# Blurred gothic window behind everything
window = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dw = ImageDraw.Draw(window)
dw.polygon([(280, 0), (920, 0), (920, 400), (600, 540), (280, 400)], fill=(68, 52, 40, 140))
dw.polygon([(320, 0), (880, 0), (880, 370), (600, 500), (320, 370)], fill=(112, 88, 62, 110))
for x in [360, 440, 520, 600, 680, 760, 840]:
    dw.line([(x, 0), (x, 370)], fill=(30, 22, 17, 120), width=6)
window = window.filter(ImageFilter.GaussianBlur(16))
sf.composite(img_actual(window), mode="normal", opacity=0.9)

# Volumetric light shafts
beams = Image.new("RGBA", (W, H), (0, 0, 0, 0))
db = ImageDraw.Draw(beams)
db.polygon([(50, -160), (390, -160), (470, 580), (80, 660)], fill=(255, 218, 160, 18))
db.polygon([(800, -160), (1160, -120), (1180, 570), (760, 650)], fill=(255, 218, 160, 16))
db.polygon([(410, -220), (790, -220), (840, 820), (360, 820)], fill=(255, 218, 160, 12))
db.polygon([(130, -140), (290, -140), (370, 550), (170, 610)], fill=(255, 232, 190, 48))
db.polygon([(880, -140), (1070, -130), (1090, 550), (840, 610)], fill=(255, 232, 190, 42))
db.polygon([(490, -190), (710, -190), (740, 790), (460, 790)], fill=(255, 228, 180, 30))
beams_blur = beams.filter(ImageFilter.GaussianBlur(45))
sf.composite(img_actual(beams_blur), mode="screen", opacity=0.85)

# Bright beam cores
core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dc = ImageDraw.Draw(core)
dc.polygon([(160, -140), (260, -160), (340, 500), (200, 540)], fill=(255, 240, 210, 80))
dc.polygon([(910, -140), (1020, -130), (1060, 500), (920, 540)], fill=(255, 240, 210, 76))
dc.polygon([(510, -180), (690, -180), (720, 780), (480, 780)], fill=(255, 236, 190, 40))
core = core.filter(ImageFilter.GaussianBlur(18))
sf.composite(img_actual(core), mode="screen", opacity=0.8)

# Dust and bokeh particles
rng = np.random.RandomState(42)
dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(dust)
for _ in range(650):
    x = rng.uniform(0, W)
    y = rng.uniform(0, H)
    r = rng.uniform(0.5, 3.0)
    a = int(rng.uniform(20, 140))
    dd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 215, a))
for _ in range(100):
    x = rng.uniform(0, W)
    y = rng.uniform(0, H * 0.85)
    r = rng.uniform(4, 14)
    a = int(rng.uniform(8, 55))
    dd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 230, 185, a))
dust_blur = dust.filter(ImageFilter.GaussianBlur(6))
sf.composite(img_actual(dust), mode="screen", opacity=0.7)
sf.composite(img_actual(dust_blur), mode="screen", opacity=0.55)

# Open book pages
left_pts = [(90, 380), (590, 330), (610, 1460), (70, 1470)]
right_pts = [(610, 330), (1130, 390), (1160, 1460), (610, 1455)]

# Page shadow for depth
pshadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ds = ImageDraw.Draw(pshadow)
off = 18
ds.polygon([(p[0] + off, p[1] + off) for p in left_pts], fill=(0, 0, 0, 130))
ds.polygon([(p[0] + off, p[1] + off) for p in right_pts], fill=(0, 0, 0, 130))
pshadow = pshadow.filter(ImageFilter.GaussianBlur(35))
sf.composite(img_actual(pshadow), mode="normal", opacity=0.85)

# Page base
pages = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dp = ImageDraw.Draw(pages)
dp.polygon(left_pts, fill=(234, 216, 178, 255))
dp.polygon(right_pts, fill=(237, 219, 182, 255))
dp.polygon([(560, 340), (640, 340), (655, 1450), (555, 1470)], fill=(92, 62, 38, 130))
dp.line(left_pts + [left_pts[0]], fill=(118, 82, 52, 255), width=4)
dp.line(right_pts + [right_pts[0]], fill=(118, 82, 52, 255), width=4)
dp.line([(90, 380), (590, 330)], fill=(255, 240, 210, 200), width=6)
dp.line([(610, 330), (1130, 390)], fill=(255, 240, 210, 200), width=6)
sf.composite(img_actual(pages), mode="normal", opacity=1.0)

# Ruled lines, red margin, rubricator marks
details = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dr = ImageDraw.Draw(details)
dr.line([(155, 460), (150, 1330)], fill=(165, 45, 40, 160), width=3)
dr.line([(1125, 460), (1130, 1330)], fill=(165, 45, 40, 160), width=3)
for y in range(480, 1351, 52):
    dr.line([(180, y), (540, y)], fill=(110, 78, 48, 45), width=1)
    dr.line([(650, y), (1090, y)], fill=(110, 78, 48, 45), width=1)
    dr.rectangle([(180, y + 8), (204, y + 22)], fill=(165, 45, 40, 150))
sf.composite(img_actual(details), mode="normal", opacity=1.0)

# Soft light on pages
page_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pg = ImageDraw.Draw(page_glow)
pg.ellipse([120, 360, 600, 780], fill=(255, 242, 210, 24))
pg.ellipse([620, 360, 1120, 780], fill=(255, 242, 210, 24))
page_glow = page_glow.filter(ImageFilter.GaussianBlur(60))
sf.composite(img_actual(page_glow), mode="screen", opacity=0.5)

# Plates for serial and date
plates = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dp = ImageDraw.Draw(plates)
dp.rectangle([115, 1552, 340, 1610], fill=(25, 18, 13, 180))
dp.rectangle([860, 1552, 1085, 1610], fill=(25, 18, 13, 180))
plates = plates.filter(ImageFilter.GaussianBlur(3))
sf.composite(img_actual(plates), mode="normal", opacity=1.0)

# Text safe area
sf.frame(100, 360, 1050, 1320)

# Wrap checks
sf.wrap(QUOTE, "cjk-hk", 42, 340, bold=True)
sf.wrap(FACT, "cjk-hk", 30, 380)

# Left page: quote, raised to reduce top void
sf.text(
    320, 620, QUOTE,
    family="cjk-hk", size=42, fill=(62, 42, 27),
    anchor="mm", role="quote", bold=True,
    max_w=340, line_gap=0.5
)

# Right page: fact, raised to begin beside the quote
sf.text(
    930, 820, FACT,
    family="cjk-hk", size=30, fill=(72, 48, 29),
    anchor="mm", role="body", bold=False,
    max_w=380, line_gap=0.55
)

# Serial and date, styled as old catalogue marks
sf.serial(
    150, 1570, SERIAL,
    family="mono", size=22, fill=(225, 205, 165),
    anchor="lt", role="meta"
)
sf.datestamp(
    1070, 1570, DATE,
    family="mono", size=22, fill=(225, 205, 165),
    anchor="rt", role="meta"
)

sf.save(OUT_PATH)
