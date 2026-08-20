from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1800
sf = Surface(W, H, scale=2, bg=(10, 13, 22))
sf.frame(140, 170, 720, 1340)

# ---------- split bilingual content ----------
qi = QUOTE.find("(换")
q_en = QUOTE[:qi].rstrip() if qi >= 0 else QUOTE
q_cn = QUOTE[qi:] if qi >= 0 else ""
fi = FACT.find("(硫")
fact_en = FACT[:fi].rstrip() if fi >= 0 else FACT
fact_cn = FACT[fi:] if fi >= 0 else ""

# ---------- Tier 2: background & glass ----------

# deep radial background
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
cx, cy, rx, ry = 0.5, 0.35, 0.62, 0.9
d = np.clip(np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2), 0, 1)
top = np.array([38, 50, 78]); bot = np.array([7, 9, 18])
for i in range(3):
    lay[..., i] = (top[i] * (1 - d) + bot[i] * d).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# soft ambient glow dots
glow = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([120 * 2, 220 * 2, 330 * 2, 430 * 2], fill=(70, 130, 220, 46))
gd.ellipse([690 * 2, 140 * 2, 990 * 2, 440 * 2], fill=(140, 70, 210, 34))
gd.ellipse([590 * 2, 1300 * 2, 910 * 2, 1640 * 2], fill=(40, 170, 180, 32))
gd.ellipse([40 * 2, 980 * 2, 260 * 2, 1200 * 2], fill=(210, 110, 50, 28))
glow = glow.filter(ImageFilter.GaussianBlur(70))
sf.composite(glow, mode="screen", opacity=0.45)

# glass plate geometry
gx0, gy0, gx1, gy1 = 60, 100, 940, 1690
rad = 72
mask_img = Image.new("L", (sf.W, sf.H), 0)
md = ImageDraw.Draw(mask_img)
md.rounded_rectangle([gx0 * 2, gy0 * 2, gx1 * 2, gy1 * 2], radius=rad * 2, fill=255)
glass_mask = np.array(mask_img) > 128

# drop shadow outside glass
sh = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sh)
sd.rounded_rectangle([(gx0 + 22) * 2, (gy0 + 28) * 2, (gx1 + 32) * 2, (gy1 + 38) * 2],
                     radius=rad * 2, fill=(0, 0, 0, 150))
sh = sh.filter(ImageFilter.GaussianBlur(36))
sh_arr = np.array(sh)
sh_arr[glass_mask] = 0
sf.composite(Image.fromarray(sh_arr), opacity=0.72)

# diagonal wavy stripes across the whole canvas (content behind glass)
stripe = sf.layer()
rows = np.arange(sf.H)[:, None]
cols = np.arange(sf.W)[None, :]
v = np.sin(cols * 0.013 + rows * 0.028)
a = (v * 0.5 + 0.5) * 52
stripe[..., 0] = (70 + v * 55).astype(np.uint8)
stripe[..., 1] = (110 + v * 75).astype(np.uint8)
stripe[..., 2] = (180 + v * 60).astype(np.uint8)
stripe[..., 3] = a.astype(np.uint8)
sf.composite(stripe, mode="screen", opacity=0.5)

# refracted offset copy inside the glass only
off_arr = np.zeros_like(stripe)
off_arr[:, :-28] = stripe[:, 28:]
off_arr[~glass_mask] = 0
sf.composite(Image.fromarray(off_arr), mode="screen", opacity=0.5)

# glass body fill
glass_fill = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
gfd = ImageDraw.Draw(glass_fill)
gfd.rounded_rectangle([gx0 * 2, gy0 * 2, gx1 * 2, gy1 * 2], radius=rad * 2,
                      fill=(140, 195, 235, 38))
sf.composite(glass_fill)

# inner shadow
inner = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
idr = ImageDraw.Draw(inner)
idr.rounded_rectangle([(gx0 + 28) * 2, (gy0 + 28) * 2, (gx1 - 28) * 2, (gy1 - 28) * 2],
                      radius=(rad - 28) * 2, outline=(0, 0, 0, 220), width=110)
inner = inner.filter(ImageFilter.GaussianBlur(30))
in_arr = np.array(inner)
in_arr[~glass_mask] = 0
sf.composite(Image.fromarray(in_arr), mode="multiply", opacity=0.55)

# chromatic dispersion edges
edge = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
ed = ImageDraw.Draw(edge)
ed.rounded_rectangle([(gx0 + 5) * 2, (gy0 + 2) * 2, (gx1 + 5) * 2, (gy1 + 2) * 2],
                     radius=rad * 2, outline=(255, 70, 50, 120), width=12)
ed.rounded_rectangle([(gx0 - 5) * 2, (gy0 - 2) * 2, (gx1 - 5) * 2, (gy1 - 2) * 2],
                     radius=rad * 2, outline=(40, 110, 255, 120), width=12)
ed.rounded_rectangle([gx0 * 2, gy0 * 2, gx1 * 2, gy1 * 2], radius=rad * 2,
                     outline=(130, 225, 255, 170), width=6)
edge = edge.filter(ImageFilter.GaussianBlur(5))
sf.composite(edge, mode="screen", opacity=0.8)
edge_glow = edge.filter(ImageFilter.GaussianBlur(14))
sf.composite(edge_glow, mode="screen", opacity=0.4)

# main glare
glare = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
gld = ImageDraw.Draw(glare)
gld.rounded_rectangle([(gx0 + 12) * 2, (gy0 + 12) * 2, (gx0 + 350) * 2, (gy0 + 165) * 2],
                      radius=65, fill=(255, 255, 255, 85))
glare = glare.filter(ImageFilter.GaussianBlur(38))
sf.composite(glare, mode="screen", opacity=0.5)

# sharp highlight line on upper-left
hl = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
hld = ImageDraw.Draw(hl)
hld.line([(gx0 + 34) * 2, (gy0 + 50) * 2, (gx0 + 390) * 2, (gy0 + 24) * 2],
         fill=(255, 255, 255, 210), width=18)
hl = hl.filter(ImageFilter.GaussianBlur(3))
sf.composite(hl, mode="screen", opacity=0.75)

# smaller bottom-right glare
g2 = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
g2d = ImageDraw.Draw(g2)
g2d.rounded_rectangle([(gx1 - 270) * 2, (gy1 - 155) * 2, (gx1 - 12) * 2, (gy1 - 12) * 2],
                      radius=65, fill=(200, 235, 255, 55))
g2 = g2.filter(ImageFilter.GaussianBlur(34))
sf.composite(g2, mode="screen", opacity=0.35)

# tiny bubbles inside glass
bub = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
bd = ImageDraw.Draw(bub)
for (bx, by, br, ba) in [
    (285, 345, 11, 70), (525, 625, 7, 55), (650, 305, 14, 80),
    (420, 1055, 9, 45), (255, 1380, 13, 65), (735, 905, 6, 40),
    (825, 1325, 8, 50), (870, 240, 5, 45)
]:
    bd.ellipse([(bx - br) * 2, (by - br) * 2, (bx + br) * 2, (by + br) * 2],
               fill=(255, 255, 255, ba))
bub = bub.filter(ImageFilter.GaussianBlur(3))
sf.composite(bub, mode="screen", opacity=0.5)

# thioacetone ball-and-stick motif at the bottom (background decoration)
mol = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
mdd = ImageDraw.Draw(mol)
cx, cy = 500, 1545
m1x, m1y = 428, 1487
m2x, m2y = 572, 1487
sx, sy = 500, 1615
mdd.line([(cx * 2, cy * 2), (m1x * 2, m1y * 2)], fill=(200, 225, 245, 150), width=7)
mdd.line([(cx * 2, cy * 2), (m2x * 2, m2y * 2)], fill=(200, 225, 245, 150), width=7)
mdd.line([(cx * 2, cy * 2), (sx * 2, sy * 2)], fill=(255, 225, 90, 190), width=9)
mdd.line([(cx * 2 - 5, cy * 2), (sx * 2 - 5, sy * 2)], fill=(255, 225, 90, 120), width=4)
mdd.ellipse([(sx - 14) * 2, (sy - 14) * 2, (sx + 14) * 2, (sy + 14) * 2],
            fill=(245, 215, 70, 230))
mdd.ellipse([(cx - 11) * 2, (cy - 11) * 2, (cx + 11) * 2, (cy + 11) * 2],
            fill=(195, 205, 215, 230))
mdd.ellipse([(m1x - 9) * 2, (m1y - 9) * 2, (m1x + 9) * 2, (m1y + 9) * 2],
            fill=(165, 185, 205, 210))
mdd.ellipse([(m2x - 9) * 2, (m2y - 9) * 2, (m2x + 9) * 2, (m2y + 9) * 2],
            fill=(165, 185, 205, 210))
mol = mol.filter(ImageFilter.GaussianBlur(1))
sf.composite(mol, mode="screen", opacity=0.5)

# ---------- frosted text panel (clean backing for the text) ----------
panel = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
pd = ImageDraw.Draw(panel)
panel_box = (150, 230, 850, 1330)
pd.rounded_rectangle([panel_box[0] * 2, panel_box[1] * 2,
                      panel_box[2] * 2, panel_box[3] * 2],
                     radius=30 * 2, fill=(10, 16, 30, 215))
panel = panel.filter(ImageFilter.GaussianBlur(6))
sf.composite(panel)

# faint edge light on the panel
p_edge = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
ped = ImageDraw.Draw(p_edge)
ped.rounded_rectangle([(panel_box[0] - 1) * 2, (panel_box[1] - 1) * 2,
                       (panel_box[2] + 1) * 2, (panel_box[3] + 1) * 2],
                      radius=30 * 2, outline=(140, 190, 220, 55), width=3)
p_edge = p_edge.filter(ImageFilter.GaussianBlur(2))
sf.composite(p_edge, mode="screen", opacity=0.6)

# ---------- Tier 1: text (positions driven by returned boxes) ----------

tx = 158
tw = 700
y = 265

# English quote (latin font)
for ln in sf.wrap(q_en, "sans", 44, tw):
    b = sf.text(tx, y, ln, family="sans", size=44,
                fill=(235, 245, 255), anchor="lt", role="quote")
    y = b.bottom + 14
y += 34

# Chinese translation of the quote (cjk font)
if q_cn:
    for ln in sf.wrap(q_cn, "cjk-sc", 29, tw):
        b = sf.text(tx, y, ln, family="cjk-sc", size=29,
                    fill=(175, 205, 220), anchor="lt", role="body")
        y = b.bottom + 10
    y += 56

# English fact (latin font)
for ln in sf.wrap(fact_en, "sans", 34, tw):
    b = sf.text(tx, y, ln, family="sans", size=34,
                fill=(222, 236, 246), anchor="lt", role="body")
    y = b.bottom + 12
y += 24

# Chinese translation of the fact (cjk font)
if fact_cn:
    for ln in sf.wrap(fact_cn, "cjk-sc", 29, tw):
        b = sf.text(tx, y, ln, family="cjk-sc", size=29,
                    fill=(168, 196, 210), anchor="lt", role="body")
        y = b.bottom + 10

# serial & date, like etched glass labels above the molecule
sf.serial(160, 1450, SERIAL, family="mono", size=22,
          fill=(150, 200, 215), anchor="lb", role="meta")
sf.datestamp(840, 1450, DATE, family="mono", size=22,
             fill=(150, 200, 215), anchor="rb", role="meta")

sf.save(OUT_PATH)
