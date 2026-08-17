import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 1000, 1360
margin = 80

sf = Surface(W, H, scale=2, bg=(8, 5, 22))
sf.frame(margin, margin, W - 2 * margin, H - 2 * margin)

# ---------- background ----------
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
lay[..., 0] = (12 + 45 * yy + 12 * xx).astype(np.uint8)
lay[..., 1] = (8 + 30 * yy + 22 * xx).astype(np.uint8)
lay[..., 2] = (45 + 75 * yy - 30 * xx).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

Y, X = np.mgrid[0:sf.H, 0:sf.W]
d = np.sqrt((X - sf.W * 0.82) ** 2 + (Y - sf.H * 0.08) ** 2)
glow = np.clip(1 - d / (sf.W * 0.55), 0, 1)
light = np.zeros_like(lay)
light[..., 0] = (140 * glow).astype(np.uint8)
light[..., 1] = (150 * glow).astype(np.uint8)
light[..., 2] = (250 * glow).astype(np.uint8)
light[..., 3] = (255 * glow).astype(np.uint8)
sf.composite(light, mode="screen", opacity=0.55)

d2 = np.sqrt((X - sf.W * 0.16) ** 2 + (Y - sf.H * 0.92) ** 2)
glow2 = np.clip(1 - d2 / (sf.W * 0.58), 0, 1)
light2 = np.zeros_like(lay)
light2[..., 0] = (185 * glow2).astype(np.uint8)
light2[..., 1] = (135 * glow2).astype(np.uint8)
light2[..., 2] = (225 * glow2).astype(np.uint8)
light2[..., 3] = (255 * glow2).astype(np.uint8)
sf.composite(light2, mode="screen", opacity=0.45)

# ---------- glass helpers ----------
def draw_glow_sphere(cx, cy, r, color, opacity=0.5):
    layer = sf.layer()
    img = Image.fromarray(layer, 'RGBA')
    d = ImageDraw.Draw(img)
    cx2, cy2, r2 = int(cx * 2), int(cy * 2), int(r * 2)
    steps = 9
    for i in range(steps, 0, -1):
        rr = int(r2 * i / steps)
        alpha = int(55 * (1 - i / steps)) + 25
        d.ellipse([cx2 - rr, cy2 - rr, cx2 + rr, cy2 + rr], fill=color + (min(255, alpha),))
    img = img.filter(ImageFilter.GaussianBlur(r2 * 0.32))
    sf.composite(img, mode="screen", opacity=opacity)

def draw_light_streak(x, y1, y2, color, width_logical):
    layer = sf.layer()
    img = Image.fromarray(layer, 'RGBA')
    d = ImageDraw.Draw(img)
    d.line([(int(x * 2), int(y1 * 2)), (int(x * 2), int(y2 * 2))], fill=color, width=int(width_logical * 2))
    img = img.filter(ImageFilter.GaussianBlur(width_logical * 1.2))
    sf.composite(img, mode="screen", opacity=0.7)

def draw_prism(points, fill=(255, 255, 255, 20), edge=(160, 210, 255, 150)):
    layer = sf.layer()
    img = Image.fromarray(layer, 'RGBA')
    d = ImageDraw.Draw(img)
    pts = [(int(p[0] * 2), int(p[1] * 2)) for p in points]
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=edge, width=10)
    d.line([(pts[0][0] + 7, pts[0][1]), (pts[1][0] + 7, pts[1][1]),
            (pts[2][0] + 7, pts[2][1]), (pts[0][0] + 7, pts[0][1])],
           fill=(255, 80, 80, 130), width=5)
    img = img.filter(ImageFilter.GaussianBlur(8))
    sf.composite(img)

def draw_backing(x1, y1, x2, y2, radius=44, fill=(15, 17, 28, 255)):
    layer = sf.layer()
    img = Image.fromarray(layer, 'RGBA')
    d = ImageDraw.Draw(img)
    s = 2
    d.rounded_rectangle([int(x1 * s), int(y1 * s), int(x2 * s), int(y2 * s)],
                        radius=int(radius * s), fill=fill)
    sf.composite(img)

def draw_glass_slab(x1, y1, x2, y2, radius=42, fill=(25, 35, 62, 185), edge=(215, 235, 255, 230), blur=8):
    layer = sf.layer()
    img = Image.fromarray(layer, 'RGBA')
    d = ImageDraw.Draw(img)
    s = 2
    box = [int(x1 * s), int(y1 * s), int(x2 * s), int(y2 * s)]
    rr = int(radius * s)
    d.rounded_rectangle(box, radius=rr, fill=fill)
    d.rounded_rectangle([box[0] + 5, box[1] + 5, box[2] - 5, box[3] - 5], radius=rr,
                        outline=(255, 70, 70, 150), width=8)
    d.rounded_rectangle([box[0] - 5, box[1] - 5, box[2] + 5, box[3] + 5], radius=rr,
                        outline=(70, 180, 255, 150), width=8)
    d.rounded_rectangle(box, radius=rr, outline=edge, width=8)
    d.line([(box[0] + rr, box[1] + 12), (box[2] - rr, box[1] + 12)], fill=(255, 255, 255, 190), width=14)
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    sf.composite(img)

# ---------- decorative glass ----------
draw_glow_sphere(820, 100, 220, (150, 190, 255), 0.5)
draw_glow_sphere(120, 1290, 210, (190, 140, 255), 0.45)
draw_glow_sphere(880, 1330, 140, (120, 230, 210), 0.3)

draw_light_streak(120, 0, 400, (255, 190, 210, 190), 7)
draw_light_streak(900, 1000, 1360, (190, 220, 255, 190), 7)

draw_prism([(40, 20), (260, 60), (130, 260)], fill=(255, 255, 255, 20), edge=(160, 220, 255, 170))
draw_prism([(760, 1080), (970, 1180), (840, 1300)], fill=(255, 255, 255, 16), edge=(200, 170, 255, 160))
draw_prism([(50, 1110), (190, 1230), (100, 1340)], fill=(255, 255, 255, 14), edge=(170, 220, 255, 150))

# ---------- layout ----------
panel_x = margin
panel_right = W - margin
panel_w = panel_right - panel_x
text_x = panel_x + 40
text_w = panel_w - 80

quote_family = "cjk-hk"
fact_family = "cjk-hk"

quote_size = 50
quote_gap = 0.55
quote_lines = sf.wrap(QUOTE, quote_family, quote_size, max_w=text_w, bold=True)
quote_line_h = sf.measure("腦", quote_family, quote_size, bold=True)[1]
quote_block_h = len(quote_lines) * quote_line_h * (1 + quote_gap)

fact_size = 34
fact_gap = 0.48
fact_lines = sf.wrap(FACT, fact_family, fact_size, max_w=text_w, bold=False)
fact_line_h = sf.measure("腦", fact_family, fact_size, bold=False)[1]
fact_block_h = len(fact_lines) * fact_line_h * (1 + fact_gap)

q_pad = 52
f_pad = 50
q_panel_top = 170
q_panel_h = quote_block_h + 2 * q_pad
q_panel_bottom = q_panel_top + q_panel_h

f_panel_top = q_panel_bottom + 55
f_panel_h = fact_block_h + 2 * f_pad

quote_text_top = q_panel_top + q_pad
fact_text_top = f_panel_top + f_pad

# clean backing for text, so no background decor crosses type
draw_backing(panel_x - 3, q_panel_top - 3, panel_right + 3, q_panel_bottom + 3)
draw_backing(panel_x - 3, f_panel_top - 3, panel_right + 3, f_panel_top + f_panel_h + 3)

# ---------- glass slab panels ----------
draw_glass_slab(panel_x, q_panel_top, panel_right, q_panel_bottom,
                radius=42, fill=(25, 35, 62, 185), edge=(215, 235, 255, 230), blur=8)
draw_glass_slab(panel_x, f_panel_top, panel_right, f_panel_top + f_panel_h,
                radius=42, fill=(22, 30, 55, 190), edge=(215, 235, 255, 230), blur=7)

# ---------- tags ----------
sf.serial(panel_x + 18, 80, SERIAL, family="mono", size=20,
          fill=(220, 235, 255), anchor="lt", role="meta", bold=True)
sf.datestamp(panel_right - 18, 80, DATE, family="mono", size=20,
             fill=(220, 235, 255), anchor="rt", role="meta", bold=True)

# ---------- text ----------
sf.text(text_x, quote_text_top, QUOTE,
        family=quote_family, size=quote_size, fill=(245, 248, 255),
        anchor="lt", role="quote", bold=True,
        max_w=text_w, line_gap=quote_gap, allow_overlap=False)

sf.text(text_x, fact_text_top, FACT,
        family=fact_family, size=fact_size, fill=(235, 240, 252),
        anchor="lt", role="body", bold=False,
        max_w=text_w, line_gap=fact_gap, allow_overlap=False)

sf.save(OUT_PATH)
