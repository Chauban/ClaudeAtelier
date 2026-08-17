from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math
import random

W, H = 1000, 1150
sf = Surface(W, H, scale=2, bg=(246, 239, 223))
sf.frame(120, 40, 780, 1070)

P2 = lambda v: int(round(v * 2))

# ---- tier 2: paper background ----
lay = sf.layer()
Hpx, Wpx = sf.H, sf.W
xx = np.linspace(0, 1, Wpx)[None, :]

base_r = (246 - 14 * xx).astype(np.float32)
base_g = (238 - 10 * xx).astype(np.float32)
base_b = (220 - 14 * xx).astype(np.float32)

rng = np.random.default_rng(29)
n_r = rng.normal(0, 4, (Hpx, Wpx)).astype(np.float32)
n_g = rng.normal(0, 4, (Hpx, Wpx)).astype(np.float32)
n_b = rng.normal(0, 4, (Hpx, Wpx)).astype(np.float32)

lay[..., 0] = np.clip(base_r + n_r, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(base_g + n_g, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(base_b + n_b, 0, 255).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay, mode="normal", opacity=1.0)

# ---- decoration layer ----
deco = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)

# notebook ruled lines
for y in range(140, H - 30, 44):
    d.line([(P2(70), P2(y)), (P2(W - 62), P2(y))],
           fill=(189, 205, 200, 105), width=P2(2))

# red margin line
d.line([(P2(88), P2(50)), (P2(88), P2(H - 30))],
       fill=(222, 120, 120, 175), width=P2(3))

# spiral punch holes
for y in range(80, H - 30, 105):
    d.ellipse([P2(51), P2(y), P2(73), P2(y + 22)],
              outline=(152, 142, 132, 170), width=P2(2))

# clean paper panels behind text blocks
d.rounded_rectangle([P2(130), P2(250), P2(850), P2(520)],
                    radius=P2(14), fill=(242, 236, 224, 245),
                    outline=(210, 200, 185, 140), width=P2(1))
d.rounded_rectangle([P2(130), P2(610), P2(850), P2(970)],
                    radius=P2(14), fill=(242, 236, 224, 245),
                    outline=(210, 200, 185, 140), width=P2(1))

# washi tape function
def draw_tape(cx, cy, w, h, angle_deg, fill, dot_color=None):
    a = math.radians(angle_deg)
    pts = []
    for px, py in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
        x = cx + px * math.cos(a) - py * math.sin(a)
        y = cy + px * math.sin(a) + py * math.cos(a)
        pts.append((P2(x), P2(y)))
    d.polygon(pts, fill=fill)
    if dot_color:
        for t in np.linspace(-w / 2 + 16, w / 2 - 16, 6):
            x = cx + t * math.cos(a)
            y = cy + t * math.sin(a)
            rr = 5
            d.ellipse([P2(x - rr), P2(y - rr), P2(x + rr), P2(y + rr)], fill=dot_color)

# top washi tape
draw_tape(500, 82, 280, 40, -3, (168, 213, 197, 150), dot_color=(255, 250, 240, 115))

# small tape near fact panel
draw_tape(780, 635, 150, 28, 2.2, (242, 170, 150, 145), dot_color=(255, 248, 238, 110))

# sticky note for serial
sticky_cx, sticky_cy = 812, 128
d.polygon([(P2(sticky_cx - 75 + 4), P2(sticky_cy - 75 + 6)),
           (P2(sticky_cx + 75 + 4), P2(sticky_cy - 75 + 6)),
           (P2(sticky_cx + 75 + 4), P2(sticky_cy + 75 + 6)),
           (P2(sticky_cx - 75 + 4), P2(sticky_cy + 75 + 6))],
          fill=(120, 100, 80, 80))
d.polygon([(P2(sticky_cx - 75), P2(sticky_cy - 75)),
           (P2(sticky_cx + 75), P2(sticky_cy - 75)),
           (P2(sticky_cx + 75), P2(sticky_cy + 75)),
           (P2(sticky_cx - 75), P2(sticky_cy + 75))],
          fill=(255, 236, 170, 235))

# date swash underline
d.line([(P2(148), P2(114)), (P2(188), P2(120)), (P2(268), P2(112)), (P2(348), P2(122))],
       fill=(160, 120, 100, 180), width=P2(2))

# chemistry doodle: glowing flask, placed low and clear of text
flask_color = (80, 100, 110, 235)
flask_pts = [
    (730, 1000), (790, 1000), (788, 1060), (836, 1098), (822, 1130),
    (700, 1130), (688, 1098), (736, 1060)
]
rnd = random.Random(17)
jpts = []
for p in flask_pts:
    jpts.append((p[0] + rnd.uniform(-2, 2), p[1] + rnd.uniform(-2, 2)))
d.line([(P2(x), P2(y)) for x, y in jpts] + [(P2(jpts[0][0]), P2(jpts[0][1]))],
       fill=flask_color, width=P2(3), joint="curve")

# liquid inside flask
liq_pts = [(710, 1130), (814, 1130), (806, 1096), (718, 1096)]
d.polygon([(P2(x), P2(y)) for x, y in liq_pts], fill=(168, 218, 176, 170))

# glow above flask opening
glow_r = P2(56)
glow = Image.new("RGBA", (glow_r * 2 + 4, glow_r * 2 + 4), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([2, 2, glow_r * 2 + 2, glow_r * 2 + 2], fill=(188, 236, 168, 110))
glow = glow.filter(ImageFilter.GaussianBlur(P2(15)))
deco.paste(glow, (P2(730) - glow_r, P2(990) - glow_r), glow)

d.ellipse([P2(722), P2(984), P2(738), P2(1000)], fill=(218, 248, 208, 230))

# sparkles
def draw_star(cx, cy, r, color):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.4
        a = math.radians(i * 45 - 90)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon([(P2(x), P2(y)) for x, y in pts], fill=color)

draw_star(678, 970, 9, (210, 235, 190, 220))
draw_star(796, 952, 7, (212, 238, 186, 210))
draw_star(658, 1042, 6, (206, 232, 190, 200))
draw_star(814, 1032, 8, (210, 236, 182, 210))
draw_star(850, 990, 5, (206, 232, 190, 200))

sf.composite(deco, mode="normal", opacity=1.0)

# ---- tier 1: text ----
# date
sf.datestamp(150, 82, "17.08.2026", family="serif", size=24,
             fill=(91, 66, 50), role="meta", anchor="lt", rotate=0.0)

# serial on sticky note
sf.serial(sticky_cx, sticky_cy, SERIAL, family="sans", size=18,
          fill=(96, 70, 45), role="meta", anchor="mm", rotate=0.0)

# quote
quote_cn = "他寻找黄金，却找到了光：有时我们舍弃的东西，守护着最纯净的光芒。"

q_box = sf.text(140, 270, QUOTE, family="serif", size=34,
                fill=(74, 52, 38), role="quote", max_w=750, line_gap=0.45,
                anchor="lt", bold=False, rotate=0.0, allow_overlap=False)

qcn_box = sf.text(140, q_box.bottom + 18, quote_cn, family="cjk-sc", size=22,
                  fill=(105, 94, 84), role="meta", max_w=750, line_gap=0.4,
                  anchor="lt", bold=False, rotate=0.0, allow_overlap=False)

# fact: split Italian original and embedded Chinese translation
if '（' in FACT:
    fact_it = FACT.split('（', 1)[0].strip()
    fact_cn_in = '（' + FACT.split('（', 1)[1]
else:
    fact_it = FACT
    fact_cn_in = ""

f_box = sf.text(140, 630, fact_it, family="sans", size=28,
                fill=(66, 58, 52), role="body", max_w=750, line_gap=0.42,
                anchor="lt", bold=False, rotate=0.0, allow_overlap=False)

if fact_cn_in:
    fcn_box = sf.text(140, f_box.bottom + 22, fact_cn_in, family="cjk-sc", size=20,
                      fill=(105, 94, 84), role="meta", max_w=750, line_gap=0.4,
                      anchor="lt", bold=False, rotate=0.0, allow_overlap=False)

sf.save(OUT_PATH)
