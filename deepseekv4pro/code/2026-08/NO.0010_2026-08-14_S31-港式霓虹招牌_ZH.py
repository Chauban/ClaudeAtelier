import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W = 1000
H = 1600
SC = 2

sf = Surface(W, H, scale=SC, bg=(8, 12, 24))

def S(v):
    return int(round(v * SC))

# Background gradient
lay_bg = sf.layer()
yy = np.linspace(0, 1, lay_bg.shape[0])[:, None]
top = np.array([10, 15, 30], dtype=np.float64)
bot = np.array([2, 4, 12], dtype=np.float64)
for c in range(3):
    lay_bg[..., c] = (top[c] + (bot[c] - top[c]) * yy).astype(np.uint8)
lay_bg[..., 3] = 255
sf.composite(lay_bg, mode="normal", opacity=1.0)

# Ambient glow layer
glow_layer = sf.layer()
pil_glow = Image.fromarray(glow_layer, 'RGBA')
dg = ImageDraw.Draw(pil_glow)

dg.ellipse([S(120), S(180), S(880), S(620)], fill=(255, 92, 138, 80))
dg.ellipse([S(120), S(640), S(880), S(1080)], fill=(77, 232, 247, 70))
dg.ellipse([S(120), S(1080), S(880), S(1540)], fill=(106, 76, 147, 60))

# Border glow
dg.rectangle([S(60), S(60), S(940), S(1540)], outline=(184, 115, 51, 120), width=S(10))

# Whale bone spine glow
bone_pts = []
for i in range(6):
    cx = 220 + i * 110
    cy = 1450 - i * 8
    bone_pts.append((cx, cy))
    dg.ellipse([S(cx - 35), S(cy - 28), S(cx + 35), S(cy + 28)], fill=(106, 76, 147, 110))
    if i > 0:
        px, py = bone_pts[i - 1]
        dg.line([S(px + 35), S(py), S(cx - 35), S(cy)], fill=(106, 76, 147, 110), width=S(6))

# Red gill filaments glow
for cx, cy in bone_pts:
    for a in range(-60, 61, 20):
        rad = math.radians(a)
        x2 = cx + 55 * math.sin(rad)
        y2 = cy - 80 - abs(a) * 0.5
        dg.line([S(cx), S(cy - 20), S(x2), S(y2)], fill=(255, 77, 109, 90), width=S(8))

# Green roots glow
for cx, cy in bone_pts:
    for a in range(-45, 46, 20):
        rad = math.radians(a)
        x2 = cx + 35 * math.sin(rad)
        y2 = cy + 50 + abs(a) * 0.3
        dg.line([S(cx), S(cy + 20), S(x2), S(y2)], fill=(92, 230, 92, 80), width=S(7))

pil_glow = pil_glow.filter(ImageFilter.GaussianBlur(S(28)))
sf.composite(pil_glow, mode="screen", opacity=0.75)

# Neon tube line layer
line_layer = sf.layer()
pil_line = Image.fromarray(line_layer, 'RGBA')
dl = ImageDraw.Draw(pil_line)

# Border tubes
dl.rectangle([S(60), S(60), S(940), S(1540)], outline=(255, 179, 71, 255), width=S(4))
for cxy in [(60, 60), (940, 60), (60, 1540), (940, 1540)]:
    r = S(8)
    cx, cy = cxy
    dl.ellipse([S(cx) - r, S(cy) - r, S(cx) + r, S(cy) + r], fill=(255, 179, 71, 255))
dl.rectangle([S(80), S(80), S(920), S(1520)], outline=(255, 179, 71, 110), width=S(2))

# Bone tube lines
for i, (cx, cy) in enumerate(bone_pts):
    dl.ellipse([S(cx - 35), S(cy - 28), S(cx + 35), S(cy + 28)], outline=(150, 111, 214, 255), width=S(3))
    if i > 0:
        px, py = bone_pts[i - 1]
        dl.line([S(px + 35), S(py), S(cx - 35), S(cy)], fill=(150, 111, 214, 255), width=S(3))

# Red gill tubes
for cx, cy in bone_pts:
    for a in range(-60, 61, 20):
        rad = math.radians(a)
        x2 = cx + 60 * math.sin(rad)
        y2 = cy - 85 - abs(a) * 0.6
        dl.line([S(cx), S(cy - 20), S(x2), S(y2)], fill=(255, 77, 109, 255), width=S(3))

# Green root tubes
for cx, cy in bone_pts:
    for a in range(-45, 46, 20):
        rad = math.radians(a)
        x2 = cx + 40 * math.sin(rad)
        y2 = cy + 55 + abs(a) * 0.4
        dl.line([S(cx), S(cy + 20), S(x2), S(y2)], fill=(92, 230, 92, 255), width=S(3))

sf.composite(pil_line, mode="screen", opacity=1.0)

# Clean dark panels behind text to improve contrast / avoid busy background
panel_layer = sf.layer()
pil_panel = Image.fromarray(panel_layer, 'RGBA')
dp = ImageDraw.Draw(pil_panel)

# Quote panel
quote_panel_x0, quote_panel_y0 = 50, 220
quote_panel_x1, quote_panel_y1 = 950, 680
dp.rounded_rectangle(
    [S(quote_panel_x0), S(quote_panel_y0), S(quote_panel_x1), S(quote_panel_y1)],
    radius=S(24),
    fill=(6, 10, 20, 240),
    outline=(255, 179, 71, 130),
    width=S(2)
)

# Fact panel
fact_panel_x0, fact_panel_y0 = 50, 900
fact_panel_x1, fact_panel_y1 = 950, 1380
dp.rounded_rectangle(
    [S(fact_panel_x0), S(fact_panel_y0), S(fact_panel_x1), S(fact_panel_y1)],
    radius=S(24),
    fill=(6, 10, 20, 240),
    outline=(255, 179, 71, 130),
    width=S(2)
)

sf.composite(pil_panel, mode="normal", opacity=1.0)

# Safe area for text
sf.frame(70, 70, 860, 1460)

# Serial and date
sf.serial(70, 150, SERIAL, family="cjk-sc", size=20, fill=(255, 224, 102), role="meta", anchor="lt")
sf.datestamp(930, 150, DATE, family="cjk-sc", size=20, fill=(255, 224, 102), role="meta", anchor="rt")

# Quote as main neon sign
quote_box = sf.text(
    70, 250, QUOTE,
    family="cjk-sc", size=72, fill=(255, 107, 157),
    bold=True, role="quote", anchor="lt",
    max_w=860, line_gap=0.5
)

# Fact as secondary neon text, placed lower to occupy more vertical space
fact_box = sf.text(
    70, 930, FACT,
    family="cjk-sc", size=38, fill=(93, 226, 231),
    role="body", anchor="lt",
    max_w=860, line_gap=0.48
)

sf.save(OUT_PATH)
