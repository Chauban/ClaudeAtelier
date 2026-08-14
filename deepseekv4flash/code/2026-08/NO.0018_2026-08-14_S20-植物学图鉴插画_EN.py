from atelier_canvas import Surface
import numpy as np
import math
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1900
PAPER = (242, 236, 220)
INK_RGB = (58, 48, 38)
INK = (58, 48, 38, 255)
LEAF = (206, 213, 190)
BERRY = (148, 84, 72)

sf = Surface(W, H, scale=2, bg=PAPER)
sf.frame(80, 80, 840, 1780)

# ---------- layout (deterministic fixed steps, no overlap) ----------
zidx = FACT.find("（")
if zidx != -1:
    fact_en = FACT[:zidx].strip()
    fact_zh = FACT[zidx + 1:].strip()
    if fact_zh.endswith("）"):
        fact_zh = fact_zh[:-1].strip()
else:
    fact_en = FACT
    fact_zh = ""

qlines = sf.wrap(QUOTE, "serif", 36, 840)
en_lines = sf.wrap(fact_en, "serif", 28, 840)
zh_lines = sf.wrap(fact_zh, "cjk-sc", 28, 830)

Q_Y0 = 150
Q_STEP = 56
EN_Y0 = 1015
EN_STEP = 45
ZH_GAP = 20
ZH_STEP = 53
ANNOT_Y0 = 980
en_bottom_est = EN_Y0 + len(en_lines) * EN_STEP
zh_y0 = en_bottom_est + ZH_GAP
ANNOT_Y1 = zh_y0 + len(zh_lines) * ZH_STEP + 26
DIV_Y = Q_Y0 + (len(qlines) - 1) * Q_STEP + 42 + 32

# ---------- paper texture ----------
rng = np.random.RandomState(7)
tex = sf.layer()
tex[..., :3] = PAPER
noise = rng.normal(0, 3, (sf.H, sf.W, 1))
tex[..., :3] = np.clip(tex[..., :3].astype(np.float32) + noise, 0, 255).astype(np.uint8)
tex[..., 3] = 255
sf.composite(tex)

blot = sf.layer()
bp = Image.fromarray(blot)
bd = ImageDraw.Draw(bp)
for _ in range(30):
    bx = int(rng.randint(0, sf.W)); by = int(rng.randint(0, sf.H)); br = int(rng.randint(40, 160))
    bd.ellipse([bx - br, by - br, bx + br, by + br], fill=(186, 172, 148, 14))
blurred = bp.filter(ImageFilter.GaussianBlur(45))
sf.composite(np.array(blurred))

# ---------- pale watercolour washes ----------
wash = sf.layer()
yy = np.linspace(0, sf.H - 1, sf.H)[:, None].astype(np.float32)
xx = np.linspace(0, sf.W - 1, sf.W)[None, :].astype(np.float32)
g = np.exp(-(((xx - 1000) / 400) ** 2 + ((yy - 800) / 380) ** 2))
o = np.exp(-(((xx - 1000) / 520) ** 2 + ((yy - 280) / 250) ** 2))
wash[..., 0] = np.clip(176 * g + 206 * o, 0, 255).astype(np.uint8)
wash[..., 1] = np.clip(188 * g + 186 * o, 0, 255).astype(np.uint8)
wash[..., 2] = np.clip(156 * g + 146 * o, 0, 255).astype(np.uint8)
wash[..., 3] = np.clip(40 * g + 26 * o, 0, 255).astype(np.uint8)
sf.composite(wash)

# ---------- vignette ----------
vig = sf.layer()
dvy = np.linspace(0, 1, sf.H)[:, None]
dvx = np.linspace(0, 1, sf.W)[None, :]
dist = np.sqrt(((dvx - 0.5) / 0.5) ** 2 + ((dvy - 0.5) / 0.5) ** 2)
vig[..., 3] = (np.clip((dist - 0.72) / 0.5, 0, 1) * 50).astype(np.uint8)
vig[..., :3] = (72, 62, 46)
sf.composite(vig)

# ---------- ink engraving layer ----------
ink = sf.layer()
ip = Image.fromarray(ink)
d = ImageDraw.Draw(ip)

S = 2
def P(p):
    return (int(p[0] * S), int(p[1] * S))

def R(a, b):
    return (int(a[0] * S), int(a[1] * S), int(b[0] * S), int(b[1] * S))

def bez(p0, p1, p2, p3, t):
    mt = 1.0 - t
    x = mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0]
    y = mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]
    return (x, y)

def draw_leaf(d, base, tip, width, fill=None, outline=INK, lw=1):
    x1, y1 = base
    x2, y2 = tip
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 2.0:
        return
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    pts = []
    N = 12
    for i in range(N + 1):
        s = i / N
        hw = width * 0.5 * math.sin(math.pi * s)
        pts.append((x1 + dx * s + px * hw, y1 + dy * s + py * hw))
    for i in range(N + 1):
        s = i / N
        hw = width * 0.5 * math.sin(math.pi * s)
        pts.append((x1 + dx * s - px * hw, y1 + dy * s - py * hw))
    d.polygon([P(p) for p in pts], fill=fill, outline=outline)
    d.line([P(base), P(tip)], fill=outline, width=lw)

def corner_sprig(d, ox, oy, sx, sy):
    p0 = (0.0, 0.0); p1 = (50.0, 8.0); p2 = (95.0, 24.0); p3 = (128.0, 54.0)
    stem = [bez(p0, p1, p2, p3, i / 28.0) for i in range(29)]
    d.line([P((ox + sx * x, oy + sy * y)) for (x, y) in stem], fill=INK, width=2)
    for i, t in enumerate((0.18, 0.38, 0.58, 0.78)):
        pt = bez(p0, p1, p2, p3, t)
        t2 = min(1.0, t + 0.02)
        pt2 = bez(p0, p1, p2, p3, t2)
        tx, ty = pt2[0] - pt[0], pt2[1] - pt[1]
        L = math.hypot(tx, ty)
        if L == 0:
            continue
        tx, ty = tx / L, ty / L
        pxn, pyn = -ty, tx
        side = 1 if i % 2 == 0 else -1
        base = (ox + sx * pt[0], oy + sy * pt[1])
        tip = (ox + sx * (pt[0] + pxn * 30 * side + tx * 10),
               oy + sy * (pt[1] + pyn * 30 * side + ty * 10))
        draw_leaf(d, base, tip, 11, fill=(LEAF[0], LEAF[1], LEAF[2], 220), outline=INK, lw=1)
        bx = (ox + sx * (pt[0] - pxn * 8 * side + tx * 6),
              oy + sy * (pt[1] - pyn * 8 * side + ty * 6))
        d.ellipse(R((bx[0] - 3, bx[1] - 3), (bx[0] + 3, bx[1] + 3)),
                  fill=(BERRY[0], BERRY[1], BERRY[2], 255), outline=INK, width=1)

def draw_gable(d, cx, peak_y, base_y=750, half=30):
    d.polygon([P((cx, peak_y)), P((cx - half, base_y)), P((cx + half, base_y))],
              fill=(232, 222, 205, 255), outline=INK, width=2)
    for yy in range(int(peak_y) + 6, base_y, 7):
        t = (yy - peak_y) / (base_y - peak_y)
        hw = half * t
        d.line([P((cx - hw, yy)), P((cx + hw, yy))], fill=INK, width=1)
    d.line([P((cx + 8, peak_y - 16)), P((cx + 16, peak_y - 16))], fill=INK, width=2)
    d.line([P((cx + 16, peak_y - 16)), P((cx + 16, peak_y))], fill=INK, width=2)

def draw_church(d):
    d.polygon([P((652, 470)), P((622, 634)), P((682, 634))],
              fill=(232, 222, 205, 255), outline=INK, width=2)
    for yy in (502, 534, 566, 598):
        t = (yy - 470) / (634 - 470)
        hw = 30 * t
        d.line([P((652 - hw, yy)), P((652 + hw, yy))], fill=INK, width=1)
    d.line([P((652, 456)), P((652, 478))], fill=INK, width=2)
    d.line([P((644, 466)), P((660, 466))], fill=INK, width=2)
    d.rectangle(R((618, 634), (686, 752)), fill=(232, 222, 205, 255), outline=INK, width=2)
    d.ellipse(R((634, 655), (670, 691)), outline=INK, width=2)
    d.line([P((652, 655)), P((652, 691))], fill=INK, width=1)
    d.line([P((634, 673)), P((670, 673))], fill=INK, width=1)

def flower_stalk(d, cx, side):
    top_y = 660
    d.line([P((cx, 900)), P((cx, top_y))], fill=INK, width=2)
    for i, yy in enumerate(range(868, 660, -26)):
        sgn = 1 if i % 2 == 0 else -1
        draw_leaf(d, (cx, yy), (cx + side * sgn * 36, yy - 18), 12,
                  fill=(LEAF[0], LEAF[1], LEAF[2], 220), outline=INK, lw=1)
        draw_leaf(d, (cx, yy + 8), (cx + side * sgn * 24, yy + 6), 9,
                  fill=(LEAF[0], LEAF[1], LEAF[2], 200), outline=INK, lw=1)
    for (ox, oy) in ((0, 0), (-9, 8), (10, 9), (0, 16), (-7, 18), (8, 19)):
        fx = cx + side * ox
        fy = top_y + oy
        d.ellipse(R((fx - 4, fy - 4), (fx + 4, fy + 4)), outline=INK, width=1)
    d.ellipse(R((cx - 3, top_y - 3), (cx + 3, top_y + 3)), fill=INK)

# frame
d.rectangle(R((58, 58), (942, 1842)), outline=INK, width=3)
d.rectangle(R((70, 70), (930, 1830)), outline=INK, width=1)

corner_sprig(d, 70, 70, 1, 1)
corner_sprig(d, 930, 70, -1, 1)
corner_sprig(d, 70, 1830, 1, -1)
corner_sprig(d, 930, 1830, -1, -1)

# divider under quote
dy = DIV_Y
d.line([P((270, dy)), P((410, dy))], fill=INK, width=1)
d.line([P((590, dy)), P((730, dy))], fill=INK, width=1)
draw_leaf(d, (506, dy), (540, dy - 14), 11, fill=(LEAF[0], LEAF[1], LEAF[2], 220), outline=INK, lw=1)
draw_leaf(d, (494, dy), (460, dy - 14), 11, fill=(LEAF[0], LEAF[1], LEAF[2], 220), outline=INK, lw=1)
d.ellipse(R((492, dy - 6), (508, dy + 6)), outline=INK, width=2)

# houses behind the wall
for cx, py in ((210, 620), (275, 600), (340, 630), (400, 610)):
    draw_gable(d, cx, py)
for cx, py in ((740, 625), (795, 605)):
    draw_gable(d, cx, py)

draw_church(d)

# perimeter wall
d.rectangle(R((180, 750), (820, 880)), fill=(236, 226, 208, 255), outline=INK, width=2)
for x in range(188, 820, 26):
    d.rectangle(R((x, 734), (x + 14, 756)), fill=INK)
for yy in (780, 810, 840):
    d.line([P((184, yy)), P((816, yy))], fill=INK, width=1)
d.rectangle(R((176, 880), (824, 900)), fill=(236, 226, 208, 255), outline=INK, width=2)

# gate tower
d.polygon([P((415, 704)), P((585, 704)), P((500, 558))], fill=(232, 222, 205, 255), outline=INK, width=2)
for yy in range(580, 704, 9):
    t = (yy - 558) / (704 - 558)
    hw = 85 * t
    d.line([P((500 - hw, yy)), P((500 + hw, yy))], fill=INK, width=1)
d.line([P((500, 558)), P((500, 544))], fill=INK, width=2)
d.ellipse(R((496, 538), (504, 546)), fill=INK)
d.rectangle(R((430, 704), (570, 900)), fill=(236, 226, 208, 255), outline=INK, width=2)
d.line([P((432, 710)), P((432, 898))], fill=INK, width=2)
d.line([P((568, 710)), P((568, 898))], fill=INK, width=2)
d.rectangle(R((442, 724), (462, 744)), outline=INK, width=2)
d.rectangle(R((538, 724), (558, 744)), outline=INK, width=2)
d.pieslice(R((468, 718), (532, 784)), start=180, end=360, fill=(44, 37, 30, 255))
d.rectangle(R((468, 751), (532, 900)), fill=(44, 37, 30, 255))
d.arc(R((468, 718), (532, 784)), start=180, end=360, fill=INK, width=2)
d.line([P((468, 751)), P((468, 900))], fill=INK, width=2)
d.line([P((532, 751)), P((532, 900))], fill=INK, width=2)
for xx in range(482, 532, 10):
    d.line([P((xx, 756)), P((xx, 898))], fill=(104, 92, 78, 255), width=1)
d.ellipse(R((491, 846), (499, 854)), outline=(150, 140, 120, 255), width=1)
d.ellipse(R((486, 852), (514, 876)), outline=(150, 140, 120, 255), width=2)

# ground
d.line([P((110, 900)), P((890, 900))], fill=INK, width=2)
for x in range(120, 890, 9):
    d.line([P((x, 900)), P((x - 6, 930))], fill=INK, width=1)
    d.line([P((x + 5, 900)), P((x + 11, 928))], fill=INK, width=1)
# path from the gate
d.line([P((468, 900)), P((430, 950))], fill=INK, width=1)
d.line([P((532, 900)), P((570, 950))], fill=INK, width=1)
for yy in (915, 935, 950):
    halfw = 18 + (yy - 900) * 0.16
    d.line([P((500 - halfw, yy)), P((500 + halfw, yy))], fill=INK, width=1)

# botanical stalks at the sides
flower_stalk(d, 128, 1)
flower_stalk(d, 872, 1)

# little ivy climbing the left wall edge
for i, yy in enumerate(range(840, 748, -18)):
    if i % 2 == 0:
        draw_leaf(d, (182, yy), (192, yy - 12), 8, fill=(LEAF[0], LEAF[1], LEAF[2], 200), outline=INK, lw=1)
    else:
        draw_leaf(d, (182, yy), (172, yy - 14), 7, fill=(LEAF[0], LEAF[1], LEAF[2], 200), outline=INK, lw=1)

# clean annotation panel behind the fact text
d.rectangle(R((96, ANNOT_Y0), (904, ANNOT_Y1)), fill=(246, 241, 227, 255), outline=INK, width=2)

# specimen label
d.rectangle(R((330, 1748), (670, 1812)), fill=(246, 241, 227, 255), outline=INK, width=2)
d.line([P((338, 1758)), P((662, 1758))], fill=INK, width=1)

sf.composite(ink)

# ---------- text ----------
# quote
for i, ln in enumerate(qlines):
    sf.text(500, Q_Y0 + i * Q_STEP, ln, family="serif", size=36,
            fill=INK_RGB, anchor="mt", role="quote")

# fact english
for i, ln in enumerate(en_lines):
    sf.text(500, EN_Y0 + i * EN_STEP, ln, family="serif", size=28,
            fill=INK_RGB, anchor="mt", role="body")

# fact chinese translation
if fact_zh:
    for i, ln in enumerate(zh_lines):
        sf.text(500, zh_y0 + i * ZH_STEP, ln, family="cjk-sc", size=28,
                fill=INK_RGB, anchor="mt", role="body")

# specimen label text
sf.serial(348, 1782, SERIAL, family="serif", size=25, fill=INK_RGB, anchor="lt")
sf.datestamp(652, 1782, DATE, family="serif", size=25, fill=INK_RGB, anchor="rt")

sf.save(OUT_PATH)
