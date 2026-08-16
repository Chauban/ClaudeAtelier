import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

LW, LH = 1000, 1500
S = 2

sf = Surface(LW, LH, scale=S, bg=(12, 14, 14))

# ---- CRT bezel & screen ----
img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([20 * S, 20 * S, LW * S - 20 * S, LH * S - 20 * S],
                    radius=70, fill=(20, 22, 24, 255), outline=(78, 80, 82, 255), width=8)
d.rounded_rectangle([78 * S, 95 * S, LW * S - 78 * S, LH * S - 78 * S],
                    radius=45, fill=(3, 11, 6, 255), outline=(42, 70, 48, 255), width=6)
sf.composite(img)

# ---- vignette ----
vig = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
dist = np.sqrt(((xx - 0.5) * 1.35) ** 2 + ((yy - 0.5) * 0.95) ** 2)
alpha = np.clip((dist - 0.30) * 260, 0, 220).astype(np.uint8)
vig[..., 0] = 0
vig[..., 1] = 0
vig[..., 2] = 0
vig[..., 3] = alpha
sf.composite(vig, mode="normal", opacity=0.55)

# ---- phosphor center glow ----
glow_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow_img)
gd.ellipse([sf.W * 0.22, sf.H * 0.16, sf.W * 0.78, sf.H * 0.88],
           fill=(25, 80, 38, 120))
glow_img = glow_img.filter(ImageFilter.GaussianBlur(140))
sf.composite(glow_img, mode="screen", opacity=0.6)

# ---- scanlines ----
scan = sf.layer()
for y in range(95 * S, LH * S - 78 * S, 5):
    if y < scan.shape[0]:
        scan[y, 78 * S:LW * S - 78 * S, 0] = 0
        scan[y, 78 * S:LW * S - 78 * S, 1] = 0
        scan[y, 78 * S:LW * S - 78 * S, 2] = 0
        scan[y, 78 * S:LW * S - 78 * S, 3] = 55
sf.composite(scan, mode="normal", opacity=0.32)

# ---- status separator line ----
line_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
ld = ImageDraw.Draw(line_img)
ld.line([120 * S, 295 * S, 880 * S, 295 * S], fill=(85, 255, 130, 220), width=4)
sf.composite(line_img, mode="normal", opacity=0.9)

# ---- bottom CRT grid decoration ----
grid_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
gd = ImageDraw.Draw(grid_img)
for gx in range(150, 851, 100):
    gd.line([gx * S, 1260 * S, gx * S, 1395 * S], fill=(50, 180, 80, 80), width=2)
for gy in range(1260, 1396, 35):
    gd.line([150 * S, gy * S, 850 * S, gy * S], fill=(50, 180, 80, 60), width=2)
sf.composite(grid_img, mode="screen", opacity=0.35)

# ---- safe area for text ----
sf.frame(120, 160, 760, 1170)

# ---- meta: serial + date ----
serial_box = sf.serial(130, 235, SERIAL,
                       family="mono", size=30,
                       fill=(185, 255, 195),
                       anchor="lt", role="meta", bold=True)

date_w, _ = sf.measure(DATE, "mono", 30, bold=True)
date_box = sf.datestamp(880 - date_w, 235, DATE,
                        family="mono", size=30,
                        fill=(185, 255, 195),
                        anchor="lt", role="meta", bold=True)

# ---- quote ----
quote_size = 47
quote_box = sf.text(130, 350, QUOTE,
                    family="cjk-sc", size=quote_size,
                    fill=(205, 255, 215),
                    anchor="lt", role="quote",
                    max_w=740, line_gap=0.38, bold=True)

# ---- fact: anchor bottom to keep inside safe area and fill lower zone ----
fact_size = 31
fact_box = sf.text(130, 1315, FACT,
                   family="cjk-sc", size=fact_size,
                   fill=(155, 250, 185),
                   anchor="lb", role="body",
                   max_w=740, line_gap=0.38)

sf.save(OUT_PATH)
