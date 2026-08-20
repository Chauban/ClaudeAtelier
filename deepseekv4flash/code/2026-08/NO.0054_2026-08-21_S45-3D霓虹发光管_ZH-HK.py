import numpy as np
import math
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 1000, 1800
sf = Surface(W, H, scale=2, bg=(14, 14, 24))
sf.frame(60, 60, 880, 1680)
F = 2

# ---- choose quote wrap width so no orphan line ----
q_size = 46
max_q_w = 820
while True:
    q_lines = sf.wrap(QUOTE, "cjk-hk", q_size, max_q_w, bold=True)
    if len(q_lines) >= 2 and len(q_lines[-1]) >= 4:
        break
    max_q_w -= 20

f_lines = sf.wrap(FACT, "cjk-hk", 30, 820, bold=False)
q_h = len(q_lines) * q_size * 1.35
f_h = len(f_lines) * 30 * 1.35
q_y = 400
sep_y = int(q_y + q_h + 70)
f_y = int(sep_y + 78)
f_bottom = f_y + f_h

ring_cy = min(int(f_bottom + 130), 1280)
ring_r = 110
box_top = 1500
box = (150, box_top, 850, box_top + 165)
panel_box = (160, box_top + 10, 840, box_top + 155)

pink = (255, 92, 168)
cyan = (96, 224, 255)


def px(pts):
    return [(x * F, y * F) for x, y in pts]


def bbox_px(b):
    return (b[0] * F, b[1] * F, b[2] * F, b[3] * F)


def arc_pts(cx, cy, r, a0, a1, n=76):
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


class GlowGroup:
    def __init__(self, rgb):
        self.rgb = rgb
        self.img = Image.fromarray(sf.layer())
        self.d = ImageDraw.Draw(self.img)

    def line(self, pts, width=15):
        self.d.line(px(pts), fill=self.rgb + (255,), width=int(width * F), joint="curve")

    def circle(self, xy, r):
        x, y = xy
        self.d.ellipse([(x - r) * F, (y - r) * F, (x + r) * F, (y + r) * F], fill=self.rgb + (255,))

    def rounded_rect(self, bbox, radius, width):
        self.d.rounded_rectangle(bbox_px(bbox), radius=int(radius * F), outline=self.rgb + (255,), width=int(width * F))

    def flush(self, blur=22, opacity=0.72):
        im = self.img.filter(ImageFilter.GaussianBlur(blur * F))
        sf.composite(im, mode="screen", opacity=opacity)


# ---- background ----
bg = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
bg[..., 0] = (26 - 14 * yy).astype(np.uint8)
bg[..., 1] = (21 - 10 * yy).astype(np.uint8)
bg[..., 2] = (38 - 20 * yy).astype(np.uint8)
bg[..., 3] = 255
rng = np.random.default_rng(5)
tex_small = Image.fromarray(rng.integers(0, 256, (120, 67), dtype=np.uint8)).resize((sf.W, sf.H), Image.BILINEAR)
tex = np.array(tex_small).astype(np.float32) / 255.0
adj = (tex - 0.5) * 16
for c in range(3):
    ch = bg[..., c].astype(np.int16) + adj.astype(np.int16)
    bg[..., c] = np.clip(ch, 0, 255).astype(np.uint8)
sf.composite(bg)

amb = sf.layer()
ai = Image.fromarray(amb)
ad = ImageDraw.Draw(ai)
ad.ellipse([-250 * F, -120 * F, 1150 * F, 950 * F], fill=(255, 70, 150, 20))
ad.ellipse([400 * F, 1050 * F, 1600 * F, 2100 * F], fill=(70, 210, 255, 16))
ad.ellipse([-400 * F, 1450 * F, 800 * F, 2700 * F], fill=(255, 190, 70, 12))
ai = ai.filter(ImageFilter.GaussianBlur(220 * F))
sf.composite(ai, mode="screen", opacity=0.55)

vig = sf.layer()
d = np.sqrt(((xx - 0.5) * 1.25) ** 2 + ((yy - 0.5) * 1.15) ** 2)
va = np.clip((d - 0.52) * 520, 0, 85).astype(np.uint8)
vig[..., 3] = va
sf.composite(vig)

# ---- neon tubes ----
tube1 = arc_pts(340, 190, 125, 180, 360)
tube2 = arc_pts(660, 190, 105, 180, 360)
tube3 = arc_pts(500, 260, 85, 180, 360)
tube_balls = [
    (215, 190, 6), (465, 190, 6),
    (555, 190, 5), (765, 190, 5),
    (415, 260, 5), (585, 260, 5),
    (340, 190, 7), (660, 190, 6),
]
tube_cores = [(340, 190, 3), (660, 190, 2.8), (500, 260, 2.8)]

sep_pts = [(x, sep_y + 6 * math.sin((x - 150) / 740 * math.pi)) for x in range(150, 891, 16)]
ring_pts = [(500 + ring_r * math.cos(a), ring_cy + ring_r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 100)]
brow_pts = [(290, 1525), (710, 1525)]
brow_balls = [(290, 1525, 4), (710, 1525, 4)]
brow_cores = [(290, 1525, 2.2), (710, 1525, 2.2)]

stone_pos = [
    (475, ring_cy - 30, 4.5),
    (530, ring_cy + 28, 4),
    (455, ring_cy + 65, 3.5),
]
hair_base = ring_cy + ring_r
hair_lines = [
    (475, hair_base + 30, 468, hair_base + 66),
    (505, hair_base + 32, 505, hair_base + 70),
    (535, hair_base + 30, 542, hair_base + 66),
]

pink_g = GlowGroup(pink)
for lp in (tube1, tube2, tube3):
    pink_g.line(lp, 15)
for (x, y, r) in tube_balls:
    pink_g.circle((x, y), r + 3)
pink_g.rounded_rect(box, 18, 14)

cyan_g = GlowGroup(cyan)
cyan_g.line(sep_pts, 11)
cyan_g.line(ring_pts, 12)
cyan_g.line(brow_pts, 9)
for (x, y, r) in brow_balls:
    cyan_g.circle((x, y), r + 2)

# signboard panel
panel = sf.layer()
pi = Image.fromarray(panel)
pd = ImageDraw.Draw(pi)
pd.rounded_rectangle(bbox_px(panel_box), radius=int(14 * F), fill=(27, 22, 46, 235))
sf.composite(pi, opacity=0.92)

pink_g.flush(22, 0.72)
cyan_g.flush(18, 0.7)

# pink solids + cores
ps = sf.layer()
psi = Image.fromarray(ps)
psd = ImageDraw.Draw(psi)
for lp in (tube1, tube2, tube3):
    psd.line(px(lp), fill=pink + (255,), width=int(13 * F), joint="curve")
for (x, y, r) in tube_balls:
    psd.ellipse([(x - r) * F, (y - r) * F, (x + r) * F, (y + r) * F], fill=pink + (255,))
psd.rounded_rectangle(bbox_px(box), radius=int(18 * F), outline=pink + (255,), width=int(10 * F))
sf.composite(psi, opacity=0.95)

pk = sf.layer()
pki = Image.fromarray(pk)
pkd = ImageDraw.Draw(pki)
for lp in (tube1, tube2, tube3):
    pkd.line(px(lp), fill=(255, 255, 255, 230), width=int(5 * F), joint="curve")
for (x, y, r) in tube_cores:
    pkd.ellipse([(x - r) * F, (y - r) * F, (x + r) * F, (y + r) * F], fill=(255, 255, 255, 255))
for (x, y, r) in tube_balls:
    pkd.ellipse([(x - r) * 0.4 * F, (y - r) * 0.4 * F, (x + r) * 0.4 * F, (y + r) * 0.4 * F], fill=(255, 255, 255, 255))
pkd.rounded_rectangle(bbox_px(box), radius=int(18 * F), outline=(255, 255, 255, 210), width=int(3.5 * F))
sf.composite(pki, mode="screen", opacity=0.88)

# cyan solids + cores
cy_layer = sf.layer()
cyi = Image.fromarray(cy_layer)
cyd = ImageDraw.Draw(cyi)
cyd.line(px(sep_pts), fill=cyan + (255,), width=int(9 * F), joint="curve")
cyd.line(px(ring_pts), fill=cyan + (255,), width=int(10 * F), joint="curve")
cyd.line(px(brow_pts), fill=cyan + (255,), width=int(7 * F), joint="curve")
for (x, y, r) in brow_balls:
    cyd.ellipse([(x - r) * F, (y - r) * F, (x + r) * F, (y + r) * F], fill=cyan + (255,))
sf.composite(cyi, opacity=0.95)

ck = sf.layer()
cki = Image.fromarray(ck)
ckd = ImageDraw.Draw(cki)
ckd.line(px(sep_pts), fill=(255, 255, 255, 230), width=int(3.5 * F), joint="curve")
ckd.line(px(ring_pts), fill=(255, 255, 255, 230), width=int(4 * F), joint="curve")
ckd.line(px(brow_pts), fill=(255, 255, 255, 230), width=int(2.5 * F), joint="curve")
for (x, y, r) in brow_cores:
    ckd.ellipse([(x - r) * F, (y - r) * F, (x + r) * F, (y + r) * F], fill=(255, 255, 255, 255))
sf.composite(cki, mode="screen", opacity=0.88)

# metal clamps
cl = sf.layer()
cli = Image.fromarray(cl)
cld = ImageDraw.Draw(cli)
for (cx, cy) in [(340, 65), (247, 127), (433, 127), (660, 85), (571, 139), (750, 145), (415, 260), (585, 260)]:
    cld.rounded_rectangle([(cx - 8) * F, (cy - 3) * F, (cx + 8) * F, (cy + 3) * F],
                          radius=int(2 * F), fill=(44, 44, 66, 230))
sf.composite(cli, opacity=0.95)

# ear stones (glowing crystals)
sg = sf.layer()
sgi = Image.fromarray(sg)
sgd = ImageDraw.Draw(sgi)
for (x, y, r) in stone_pos:
    rad = r * 2.6
    sgd.ellipse([(x - rad) * F, (y - rad) * F, (x + rad) * F, (y + rad) * F], fill=(255, 210, 130, 255))
sgi = sgi.filter(ImageFilter.GaussianBlur(10))
sf.composite(sgi, mode="screen", opacity=0.6)

sc = sf.layer()
sci = Image.fromarray(sc)
scd = ImageDraw.Draw(sci)
for (x, y, r) in stone_pos:
    scd.ellipse([(x - r) * F, (y - r) * F, (x + r) * F, (y + r) * F], fill=(255, 255, 255, 255))
sf.composite(sci, mode="screen", opacity=0.95)

# hair cells
hl = sf.layer()
hli = Image.fromarray(hl)
hld = ImageDraw.Draw(hli)
for (x0, y0, x1, y1) in hair_lines:
    hld.line(px([(x0, y0), (x1, y1)]), fill=(255, 255, 255, 210), width=int(3.5 * F), joint="curve")
hli = hli.filter(ImageFilter.GaussianBlur(4))
sf.composite(hli, mode="screen", opacity=0.8)

# signboard led backlight
led = sf.layer()
ledi = Image.fromarray(led)
ledd = ImageDraw.Draw(ledi)
ledd.ellipse([360 * F, (box_top + 50) * F, 640 * F, (box_top + 140) * F], fill=(255, 255, 255, 24))
ledi = ledi.filter(ImageFilter.GaussianBlur(45 * F))
sf.composite(ledi, mode="screen", opacity=0.65)

# text glow pools
qg = sf.layer()
qgi = Image.fromarray(qg)
qgd = ImageDraw.Draw(qgi)
qgd.rounded_rectangle(bbox_px((55, q_y - 25, 945, q_y + int(q_h) + 35)), radius=50, fill=(255, 205, 70, 22))
qgi = qgi.filter(ImageFilter.GaussianBlur(60 * F))
sf.composite(qgi, mode="screen", opacity=0.85)

fg = sf.layer()
fgi = Image.fromarray(fg)
fgd = ImageDraw.Draw(fgi)
fgd.rounded_rectangle(bbox_px((55, f_y - 25, 945, f_y + int(f_h) + 35)), radius=50, fill=(96, 224, 255, 18))
fgi = fgi.filter(ImageFilter.GaussianBlur(55 * F))
sf.composite(fgi, mode="screen", opacity=0.85)

# text — single pass per block, neon color only (glow comes from the pools)
sf.text(90, q_y, QUOTE, family="cjk-hk", size=q_size, fill=(255, 216, 100),
        anchor="lt", role="quote", bold=True, max_w=max_q_w)
sf.text(90, f_y, FACT, family="cjk-hk", size=30, fill=(170, 238, 255),
        anchor="lt", role="body", bold=False, max_w=820)

sf.serial(500, 1563, SERIAL, family="cjk-hk", size=28, fill=(255, 255, 255), anchor="mt", role="meta", bold=True)
sf.datestamp(500, 1613, DATE, family="cjk-hk", size=24, fill=(255, 255, 255), anchor="mt", role="meta", bold=True)

sf.save(OUT_PATH)
