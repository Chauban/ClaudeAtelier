from atelier_canvas import Surface
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

W, H = 1000, 1550
sf = Surface(W, H, scale=2, bg=(4, 8, 5))
sf.frame(110, 120, 780, 1310)

GREEN = (152, 255, 165)
GREEN_DIM = (108, 220, 132)
GREEN_SOFT = (136, 244, 146)

bezel = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 255))
bd = ImageDraw.Draw(bezel)
bd.rounded_rectangle([24, 24, sf.W - 24, sf.H - 24], radius=100, fill=(28, 32, 28, 255))
bd.rounded_rectangle([64, 64, sf.W - 64, sf.H - 64], radius=76, fill=(5, 11, 6, 255))
sf.composite(bezel, mode="normal", opacity=1.0)

yy = np.linspace(-1, 1, sf.H)[:, None]
xx = np.linspace(-1, 1, sf.W)[None, :]
rr = np.sqrt(xx * xx * 0.85 + yy * yy * 0.65)

bloom = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
alpha = np.clip(230 * (1 - rr / 1.3), 0, 255).astype(np.uint8)
bloom[..., 0] = 22
bloom[..., 1] = 112
bloom[..., 2] = 58
bloom[..., 3] = alpha
sf.composite(bloom, mode="screen", opacity=0.55)

vignette = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
av = np.clip(200 * (rr / 1.2 - 0.3), 0, 230).astype(np.uint8)
vignette[..., 0] = 0
vignette[..., 1] = 0
vignette[..., 2] = 0
vignette[..., 3] = av
sf.composite(vignette, mode="normal", opacity=1.0)

scan = sf.layer()
mask = (np.arange(sf.H) % 4) < 2
scan[mask, :, :3] = 0
scan[mask, :, 3] = 80
sf.composite(scan, mode="normal", opacity=1.0)

def draw_panel(x0, y0, x1, y1, radius=16, fill=(7, 14, 9, 255), outline=(86, 210, 112, 255), width=3):
    img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0 * 2, y0 * 2, x1 * 2, y1 * 2], radius=radius, fill=fill, outline=outline, width=width)
    sf.composite(img, mode="normal", opacity=1.0)

q_size = 46
q_max_w = 500
q_pad = 34
q_y0 = 260

q_lines = sf.wrap(QUOTE, "cjk-sc", q_size, max_w=q_max_w, bold=False)
if len(q_lines) > 1 and len(q_lines[-1]) <= 4:
    q_max_w = 440
    q_lines = sf.wrap(QUOTE, "cjk-sc", q_size, max_w=q_max_w, bold=False)

q_line_h = int(q_size * 1.4)
q_h = len(q_lines) * q_line_h + q_pad * 2
q_y1 = q_y0 + q_h

draw_panel(130, q_y0, 870, q_y1)

fact_y0 = q_y1 + 50
fact_size = 34
fact_max_w = 680
fact_pad = 32

f_lines = sf.wrap(FACT, "cjk-sc", fact_size, max_w=fact_max_w, bold=False)
fact_line_h = int(fact_size * 1.5)
fact_h = len(f_lines) * fact_line_h + fact_pad * 2
fact_y1 = fact_y0 + fact_h

if fact_y1 > 1130:
    fact_size = 32
    fact_max_w = 700
    f_lines = sf.wrap(FACT, "cjk-sc", fact_size, max_w=fact_max_w, bold=False)
    fact_line_h = int(fact_size * 1.5)
    fact_h = len(f_lines) * fact_line_h + fact_pad * 2
    fact_y1 = fact_y0 + fact_h

draw_panel(130, fact_y0, 870, fact_y1)

map_y0 = fact_y1 + 44
map_y1 = 1290
if map_y1 - map_y0 < 160:
    map_y0 = map_y1 - 160

footer_y0 = 1335
footer_y1 = 1395
draw_panel(130, 1335, 870, 1395)

def draw_map(x0, y0, x1, y1):
    img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0 * 2, y0 * 2, x1 * 2, y1 * 2], radius=14,
                        fill=(8, 17, 11, 255), outline=(72, 180, 102, 255), width=3)

    gx0 = x0 + 112
    gx1 = x1 - 112
    gy0 = y0 + int((y1 - y0) * 0.17)
    gy1 = y1 - int((y1 - y0) * 0.17)
    d.rounded_rectangle([gx0 * 2, gy0 * 2, gx1 * 2, gy1 * 2], radius=12,
                        fill=(12, 27, 15, 255), outline=(92, 224, 124, 255), width=2)

    rng = np.random.default_rng(13)

    n_out = 270
    xs = rng.uniform(x0 + 14, x1 - 14, n_out)
    ys = rng.uniform(y0 + 14, y1 - 14, n_out)
    for x, y in zip(xs, ys):
        if gx0 + 10 < x < gx1 - 10 and gy0 + 10 < y < gy1 - 10:
            continue
        s = float(rng.uniform(1.8, 6.5))
        c = int(rng.uniform(70, 190))
        col = (int(c * 0.6), c, int(c * 0.65), 255)
        d.rectangle([(x - s / 2) * 2, (y - s / 2) * 2, (x + s / 2) * 2, (y + s / 2) * 2], fill=col)

    step = 11.5
    for gx in np.arange(gx0 + 10, gx1 - 8, step):
        for gy in np.arange(gy0 + 10, gy1 - 8, step):
            s = float(rng.uniform(2.4, 4.2))
            d.rectangle([(gx - s / 2) * 2, (gy - s / 2) * 2, (gx + s / 2) * 2, (gy + s / 2) * 2],
                        fill=(92, 224, 124, 255))

    sf.composite(img, mode="normal", opacity=1.0)

draw_map(130, map_y0, 870, map_y1)

sf.text(160, q_y0 + q_pad, QUOTE,
        family="cjk-sc", size=q_size, fill=GREEN,
        role="quote", max_w=q_max_w, line_gap=0.4, bold=False)

sf.text(160, fact_y0 + fact_pad, FACT,
        family="cjk-sc", size=fact_size, fill=GREEN_SOFT,
        role="body", max_w=fact_max_w, line_gap=0.5, bold=False)

sf.serial(150, 1352, SERIAL,
          family="mono", size=18, fill=GREEN,
          role="meta", max_w=None)

sf.datestamp(355, 1352, DATE,
             family="mono", size=18, fill=GREEN_DIM,
             role="meta", max_w=None)

sf.save(OUT_PATH)
