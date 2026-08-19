import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 900, 1140
SCALE = 2

def PX(v):
    return int(round(v * SCALE))

sf = Surface(W, H, scale=2, bg=(8, 13, 28))
sf.frame(70, 60, 760, 1020)

# ---------- background ----------
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]

vert = 1.0 - yy
r_ch = (7 + 14 * vert)
g_ch = (11 + 11 * vert)
b_ch = (26 + 20 * vert)

dx = xx - 0.5
dy = yy - (465.0 / H)
r2 = dx * dx + dy * dy
glow = np.exp(-r2 / (2 * 0.26 ** 2))
r_ch = r_ch + 32 * glow
g_ch = g_ch + 30 * glow
b_ch = b_ch + 46 * glow

dnx = xx - 0.22
dny = yy - 0.16
rn2 = dnx * dnx + dny * dny
neb = np.exp(-rn2 / (2 * 0.15 ** 2))
r_ch = r_ch + 24 * neb
g_ch = g_ch + 10 * neb
b_ch = b_ch + 34 * neb

lay[..., 0] = np.clip(r_ch, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(g_ch, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(b_ch, 0, 255).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# ---------- star field ----------
star_layer = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
sd = ImageDraw.Draw(star_layer)
rng = np.random.RandomState(20260820)

for _ in range(42):
    x = rng.uniform(25, W - 25)
    y = rng.uniform(25, H - 25)
    r = rng.uniform(1.0, 2.3)
    b = int(rng.uniform(175, 255))
    col = (b, int(b * 0.96), int(b * 0.88), int(rng.uniform(150, 235)))
    sd.ellipse([PX(x - r), PX(y - r), PX(x + r), PX(y + r)], fill=col)

for _ in range(210):
    x = rng.uniform(10, W - 10)
    y = rng.uniform(10, H - 10)
    r = rng.uniform(0.4, 1.1)
    b = int(rng.uniform(120, 225))
    col = (b, int(b * 0.97), int(b * 0.92), int(rng.uniform(120, 215)))
    sd.ellipse([PX(x - r), PX(y - r), PX(x + r), PX(y + r)], fill=col)

star_layer = star_layer.filter(ImageFilter.GaussianBlur(1.5))
sf.composite(star_layer, mode="screen", opacity=0.9)

# ---------- celestial chart plate ----------
plat = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
pd = ImageDraw.Draw(plat)

C = (450.0, 465.0)
R = 235.0

pd.ellipse([PX(C[0] - R), PX(C[1] - R), PX(C[0] + R), PX(C[1] + R)],
           fill=(16, 28, 58, 255))
pd.ellipse([PX(C[0] - R), PX(C[1] - R), PX(C[0] + R), PX(C[1] + R)],
           outline=(201, 176, 122, 255), width=PX(2))

for rr in [R - 13, R - 38, R - 73]:
    pd.ellipse([PX(C[0] - rr), PX(C[1] - rr), PX(C[0] + rr), PX(C[1] + rr)],
               outline=(201, 176, 122, 150), width=PX(1))

for deg in range(0, 360, 10):
    a = math.radians(deg)
    r1 = R - (12 if deg % 30 == 0 else 6)
    r2 = R - 1
    pd.line([PX(C[0] + r1 * math.cos(a)), PX(C[1] + r1 * math.sin(a)),
             PX(C[0] + r2 * math.cos(a)), PX(C[1] + r2 * math.sin(a))],
            fill=(201, 176, 122, 230), width=PX(1.3))

# ---------- chiton constellation ----------
cx, cy, rx, ry = 450.0, 465.0, 155.0, 96.0
gx, gy = rx + 17, ry + 17

for deg in range(0, 360, 6):
    a = math.radians(deg)
    ex = cx + gx * math.cos(a)
    ey = cy + gy * math.sin(a)
    rdot = 1.6
    pd.ellipse([PX(ex - rdot), PX(ey - rdot), PX(ex + rdot), PX(ey + rdot)],
               fill=(201, 176, 122, 170))

pd.ellipse([PX(cx - rx), PX(cy - ry), PX(cx + rx), PX(cy + ry)],
           outline=(222, 197, 148, 245), width=PX(1.8))

n = 8
top_pts = []
bot_pts = []
for i in range(n + 1):
    fx = i / n
    x = cx - rx + 2 * rx * fx
    yoff = ry * math.sqrt(max(0.0, 1.0 - ((x - cx) / rx) ** 2))
    top_pts.append((x, cy - yoff))
    bot_pts.append((x, cy + yoff))

def bez(pt0, pt1, pt2, nseg=20):
    pts = []
    for k in range(nseg + 1):
        t = k / nseg
        x = (1 - t) ** 2 * pt0[0] + 2 * (1 - t) * t * pt1[0] + t ** 2 * pt2[0]
        y = (1 - t) ** 2 * pt0[1] + 2 * (1 - t) * t * pt1[1] + t ** 2 * pt2[1]
        pts.append((x, y))
    return pts

def pline(pts, fill, wid):
    pd.line([(PX(x), PX(y)) for x, y in pts], fill=fill, width=PX(wid))

for i in range(1, n):
    T = top_pts[i]
    B = bot_pts[i]
    mid = ((T[0] + B[0]) / 2 - 12.0, (T[1] + B[1]) / 2)
    pline(bez(T, mid, B, 20), (214, 188, 138, 210), 1.5)

star_col = (245, 235, 210)

def star(p, r=2.2):
    pd.ellipse([PX(p[0] - r), PX(p[1] - r), PX(p[0] + r), PX(p[1] + r)],
               fill=star_col + (255,))
    gl = r + 1.8
    pd.line([PX(p[0] - gl), PX(p[1]), PX(p[0] + gl), PX(p[1])],
            fill=star_col + (190,), width=PX(0.8))
    pd.line([PX(p[0]), PX(p[1] - gl), PX(p[0]), PX(p[1] + gl)],
            fill=star_col + (190,), width=PX(0.8))

for i in range(n + 1):
    if i == 0 or i == n:
        star(top_pts[i], r=3.2)
    else:
        star(top_pts[i], r=2.2)
        star(bot_pts[i], r=2.2)

for _ in range(140):
    ang = rng.uniform(0, 2 * math.pi)
    rad = math.sqrt(rng.uniform(0, 1))
    ex = cx + rx * rad * math.cos(ang)
    ey = cy + ry * rad * math.sin(ang)
    er = rng.uniform(0.7, 1.7)
    b = int(rng.uniform(165, 240))
    col = (b, int(b * 0.95), int(b * 0.86), int(rng.uniform(140, 230)))
    pd.ellipse([PX(ex - er), PX(ey - er), PX(ex + er), PX(ey + er)], fill=col)

sf.composite(plat, mode="normal", opacity=1.0)

# ---------- text ----------
def draw_centered(text, family, size, fill, y_start, max_w, line_gap, role):
    lines = sf.wrap(text, family, size, max_w, bold=False)
    y = y_start
    last_bottom = y_start
    for line in lines:
        b = sf.text(450, y, line, family=family, size=size, fill=fill,
                    anchor="mt", role=role, bold=False, max_w=None)
        last_bottom = b.bottom
        y = b.bottom + size * line_gap
    return last_bottom

quote_y = 96
q_bottom = draw_centered(QUOTE, "cjk-hk", 34, (245, 236, 215),
                         quote_y, 720, 0.34, "quote")

fact_y = 747
f_bottom = draw_centered(FACT, "cjk-hk", 28, (224, 215, 190),
                         fact_y, 700, 0.42, "body")

cart_y = f_bottom + 36

cart_layer = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
cd2 = ImageDraw.Draw(cart_layer)
top_y = cart_y - 14
bot_y = cart_y + 26
cd2.line([PX(120), PX(top_y), PX(430), PX(top_y)], fill=(201, 176, 122, 215), width=PX(1.2))
cd2.line([PX(470), PX(top_y), PX(780), PX(top_y)], fill=(201, 176, 122, 215), width=PX(1.2))
cd2.line([PX(120), PX(bot_y), PX(430), PX(bot_y)], fill=(201, 176, 122, 215), width=PX(1.2))
cd2.line([PX(470), PX(bot_y), PX(780), PX(bot_y)], fill=(201, 176, 122, 215), width=PX(1.2))
sf.composite(cart_layer)

sf.serial(120, cart_y, SERIAL, family="mono", size=18,
          fill=(201, 176, 122), anchor="lt", role="meta")
sf.datestamp(780, cart_y, DATE, family="mono", size=18,
             fill=(201, 176, 122), anchor="rt", role="meta")

sf.save(OUT_PATH)
