from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math

W, H = 1000, 1720
sf = Surface(W, H, scale=2, bg=(15, 15, 20))
sf.frame(70, 70, W - 140, H - 140)

s = 2
GOLD = (226, 206, 158)
GOLD_LINE = (206, 184, 130)


def split_cn(t):
    if "（中文：" in t:
        a, b = t.split("（中文：", 1)
        return a.strip(), b.rstrip("）").strip()
    return t, ""


q_fr, q_cn = split_cn(QUOTE)
f_fr, f_cn = split_cn(FACT)

# ---------- layout (computed from measured wraps) ----------
QL, QG = 44, 1.55
CL, CG = 28, 1.55
FL, FG = 31, 1.52

q_lines = sf.wrap(q_fr, "serif", QL, 860)
q_cn_lines = sf.wrap(q_cn, "cjk-sc", CL, 860) if q_cn else []
f_lines = sf.wrap(f_fr, "serif", FL, 860)
f_cn_lines = sf.wrap(f_cn, "cjk-sc", CL, 860) if f_cn else []

qp = QL * QG
cp = CL * CG
fp = FL * FG

quote_y = 428
div_y1 = quote_y + len(q_lines) * qp + 30 + len(q_cn_lines) * cp + 22
fact_y = div_y1 + 48
fcn_y = fact_y + len(f_lines) * fp + 30
plaque_y = max(fcn_y + len(f_cn_lines) * cp + 76, 1300)
assert plaque_y + 100 < H - 40

# ---------- background base ----------
yyy, xxx = np.mgrid[0:sf.H, 0:sf.W].astype(np.float32)

lay = sf.layer()
gr = np.linspace(0, 1, sf.H)[:, None]
lay[..., 0] = (16 + 22 * gr).astype(np.uint8)
lay[..., 1] = (16 + 24 * gr).astype(np.uint8)
lay[..., 2] = (19 + 29 * gr).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# ---------- subtle grain (will be covered by the clean panel) ----------
rng = np.random.default_rng(71)
lay = sf.layer()
noise = rng.normal(0, 1, (sf.H, sf.W)).astype(np.float32)
nimg = Image.fromarray(np.clip((noise * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(1.8)
)
nz = (np.asarray(nimg).astype(np.float32) - 128.0) / 128.0
v = np.clip(nz * 1.3, -1, 1)
lay[..., 0] = np.clip(26 + v * 16, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(26 + v * 17, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(31 + v * 20, 0, 255).astype(np.uint8)
lay[..., 3] = np.clip(np.abs(v) * 170, 0, 255).astype(np.uint8)
sf.composite(lay, opacity=0.45)

# ---------- brushed sheen, only outside the central panel ----------
lay = sf.layer()
t = (0.82 * xxx + 0.42 * yyy) / 60.0
shv = (0.5 + 0.5 * np.sin(t)) ** 4
edge_mask = ((yyy / s) < 320) | ((yyy / s) > 1470)
lay[..., 0] = np.clip(140 + shv * 60, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(136 + shv * 56, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(130 + shv * 44, 0, 255).astype(np.uint8)
lay[..., 3] = np.clip(shv * 180 * edge_mask, 0, 255).astype(np.uint8)
sf.composite(lay, mode="screen", opacity=0.28)

# ---------- warm glow & vignette ----------
lay = sf.layer()
dx = xxx / s - 500
dy = yyy / s - 250
d = np.sqrt(dx * dx + dy * dy) / 520.0
g = np.clip(1.0 - d, 0, 1) ** 2
lay[..., 0] = (g * 90).astype(np.uint8)
lay[..., 1] = (g * 78).astype(np.uint8)
lay[..., 2] = (g * 60).astype(np.uint8)
lay[..., 3] = (g * 255).astype(np.uint8)
sf.composite(lay, mode="screen", opacity=0.25)

lay = sf.layer()
nx = (xxx / s - W / 2) / (W / 2)
ny = (yyy / s - H / 2) / (H / 2)
vgt = np.clip(nx * nx + ny * ny, 0, 1) ** 1.4
lay[..., 0] = np.clip(vgt * 28, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(vgt * 28, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(vgt * 34, 0, 255).astype(np.uint8)
lay[..., 3] = (vgt * 255).astype(np.uint8)
sf.composite(lay, mode="multiply", opacity=0.5)

# ---------- outer engraved frame ----------
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
xm, ym = 74, 74
d.rectangle([xm * s, ym * s, (W - xm) * s, (H - ym) * s], outline=(104, 92, 62, 255), width=2)
d.rectangle([(xm + 8) * s, (ym + 8) * s, (W - xm - 8) * s, (H - ym - 8) * s], outline=(150, 132, 92, 170), width=1)
d.line([(xm + 9) * s, (ym + 9) * s, (W - xm - 9) * s, (ym + 9) * s], fill=(200, 182, 130, 140), width=1)
d.line([(xm + 9) * s, (H - ym - 9) * s, (W - xm - 9) * s, (H - ym - 9) * s], fill=(10, 10, 8, 255), width=2)
for bx, by in [(xm, ym), (W - xm, ym), (xm, H - ym), (W - xm, H - ym)]:
    d.line([(bx * s, (by + 20) * s), (bx * s, by * s), ((bx + 20) * s, by * s)], fill=GOLD_LINE, width=2)
sf.composite(lay)

# ---------- Lutetia medal (top, text-free, 71 marks representing Lu) ----------
mcx, mcy, R = 500, 232, 74
lay = sf.layer()
px = xxx / s - mcx
py = yyy / s - mcy
rr = np.sqrt(px * px + py * py)
inside = rr <= R
dd = np.sqrt((px + R * 0.30) ** 2 + (py + R * 0.26) ** 2)
b = np.clip(1.0 - dd / (R * 1.06), 0, 1) ** 1.6
ang2 = math.radians(50)
nxv = math.cos(ang2)
nyv = math.sin(ang2)
dline = np.abs(-nyv * px + nxv * (py + R * 0.30))
sheen2 = np.exp(-(dline * dline) / ((R * 0.40) ** 2))
b = np.clip(b + sheen2 * 0.45, 0, 1)
edge = np.clip((rr / R) ** 2, 0, 1)
rch = np.clip(46 + 92 * b - 24 * edge, 0, 255)
gch = np.clip(43 + 75 * b - 20 * edge, 0, 255)
bch = np.clip(36 + 48 * b - 16 * edge, 0, 255)
lay[..., 0] = np.where(inside, rch, 0).astype(np.uint8)
lay[..., 1] = np.where(inside, gch, 0).astype(np.uint8)
lay[..., 2] = np.where(inside, bch, 0).astype(np.uint8)
lay[..., 3] = np.where(inside, 255, 0).astype(np.uint8)
sf.composite(lay)

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.ellipse([(mcx - R - 3) * s, (mcy - R - 3) * s, (mcx + R + 3) * s, (mcy + R + 3) * s], outline=(24, 22, 18, 255), width=8)
d.ellipse([(mcx - R - 1) * s, (mcy - R - 1) * s, (mcx + R + 1) * s, (mcy + R + 1) * s], outline=(190, 168, 116, 255), width=2)
d.ellipse([(mcx - R + 12) * s, (mcy - R + 12) * s, (mcx + R - 12) * s, (mcy + R - 12) * s], outline=(52, 48, 40, 255), width=2)
ri = int(R * 0.62)
d.ellipse([(mcx - ri) * s, (mcy - ri) * s, (mcx + ri) * s, (mcy + ri) * s], outline=(140, 122, 86, 160), width=2)
for i in range(71):
    a = 2 * math.pi * i / 71.0
    r1 = R - 8
    r2 = R - 1
    if i % 6 == 0:
        r1 = R - 13
    x1 = mcx + r1 * math.cos(a)
    y1 = mcy + r1 * math.sin(a)
    x2 = mcx + r2 * math.cos(a)
    y2 = mcy + r2 * math.sin(a)
    col = (176, 156, 112, 255) if i % 6 else (208, 186, 132, 255)
    d.line([int(x1 * s), int(y1 * s), int(x2 * s), int(y2 * s)], fill=col, width=1)
d.polygon(
    [
        (int(mcx * s), int((mcy - 6) * s)),
        (int((mcx + 6) * s), int(mcy * s)),
        (int(mcx * s), int((mcy + 6) * s)),
        (int((mcx - 6) * s), int(mcy * s)),
    ],
    fill=(212, 192, 140, 255),
)
sf.composite(lay)

# ---------- the clean dark metal panel (keeps text area pristine) ----------
panel_top, panel_bot = 336, 1470
panel_l, panel_r = 96, 904

lay = sf.layer()
pyy = yyy / s
inside = (pyy >= panel_top) & (pyy <= panel_bot)
lay[..., 0] = np.where(inside, 22, 0).astype(np.uint8)
lay[..., 1] = np.where(inside, 22, 0).astype(np.uint8)
lay[..., 2] = np.where(inside, 28, 0).astype(np.uint8)
lay[..., 3] = np.where(inside, 255, 0).astype(np.uint8)
sf.composite(lay)

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
# panel bevel edges
d.line([panel_l * s, panel_top * s, panel_r * s, panel_top * s], fill=(196, 174, 122, 230), width=1)
d.line([panel_l * s, (panel_top + 3) * s, panel_r * s, (panel_top + 3) * s], fill=(52, 50, 58, 180), width=1)
d.line([panel_l * s, panel_bot * s, panel_r * s, panel_bot * s], fill=(8, 8, 8, 255), width=2)
d.line([panel_l * s, (panel_bot - 3) * s, panel_r * s, (panel_bot - 3) * s], fill=(60, 58, 66, 160), width=1)
d.line([panel_l * s, panel_top * s, panel_l * s, panel_bot * s], fill=(140, 124, 88, 160), width=1)
d.line([(panel_l + 4) * s, panel_top * s, (panel_l + 4) * s, panel_bot * s], fill=(30, 30, 36, 200), width=1)
d.line([panel_r * s, panel_top * s, panel_r * s, panel_bot * s], fill=(140, 124, 88, 160), width=1)
d.line([(panel_r - 4) * s, panel_top * s, (panel_r - 4) * s, panel_bot * s], fill=(28, 28, 34, 200), width=1)

# engraved fret band at top and bottom of panel (above / below text)
for y_band, y_end in ((352, 388), (1430, 1462)):
    d.line([(panel_l + 50) * s, y_band * s, (panel_r - 50) * s, y_band * s], fill=(78, 72, 62, 160), width=1)
    d.line([(panel_l + 50) * s, (y_band + 6) * s, (panel_r - 50) * s, (y_band + 6) * s], fill=(50, 48, 54, 180), width=1)
    for cx in range(140, 861, 90):
        d.polygon(
            [
                (int(cx * s), int((y_band + 3) * s)),
                (int((cx - 3) * s), int((y_band - 2) * s)),
                (int(cx * s), int((y_band + 1) * s)),
                (int((cx + 3) * s), int((y_band - 2) * s)),
            ],
            fill=(118, 106, 80, 200),
        )
sf.composite(lay)


def divider(y, x1=140, x2=860):
    lay = sf.layer()
    img = Image.fromarray(lay)
    d = ImageDraw.Draw(img)
    d.line([x1 * s, int(y * s), x2 * s, int(y * s)], fill=(92, 86, 76, 220), width=1)
    d.line([x1 * s, int((y + 1) * s), x2 * s, int((y + 1) * s)], fill=(40, 40, 46, 180), width=1)
    cx = (x1 + x2) // 2
    d.polygon(
        [
            (int(cx * s), int((y - 5) * s)),
            (int((cx + 5) * s), int(y * s)),
            (int(cx * s), int((y + 5) * s)),
            (int((cx - 5) * s), int(y * s)),
        ],
        fill=(196, 176, 126, 255),
    )
    sf.composite(lay)


divider(div_y1)
divider(plaque_y - 52)
divider(H - 108, 400, 600)

# ---------- engraved plaque beneath serial / date ----------
lay = sf.layer()
pyy = yyy / s
top = plaque_y - 26
bot = plaque_y + 26
inside = (pyy >= top) & (pyy <= bot)
lay[..., 0] = np.where(inside, 40, 0).astype(np.uint8)
lay[..., 1] = np.where(inside, 38, 0).astype(np.uint8)
lay[..., 2] = np.where(inside, 45, 0).astype(np.uint8)
lay[..., 3] = np.where(inside, 255, 0).astype(np.uint8)
sf.composite(lay)
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.line([300 * s, top * s, 700 * s, top * s], fill=(190, 170, 120, 220), width=1)
d.line([300 * s, bot * s, 700 * s, bot * s], fill=(12, 12, 10, 255), width=2)
d.line([300 * s, top * s, 300 * s, bot * s], fill=(120, 106, 78, 160), width=1)
d.line([700 * s, top * s, 700 * s, bot * s], fill=(120, 106, 78, 160), width=1)
d.polygon(
    [
        (int(W / 2 * s), int((plaque_y - 6) * s)),
        (int((W / 2 + 6) * s), int(plaque_y * s)),
        (int(W / 2 * s), int((plaque_y + 6) * s)),
        (int((W / 2 - 6) * s), int(plaque_y * s)),
    ],
    fill=(214, 194, 142, 255),
)
sf.composite(lay)

# ---------- text layer (Tier 1) ----------
y = quote_y
for ln in q_lines:
    sf.text(W // 2, y, ln, family="serif", size=QL, fill=GOLD, anchor="mt", role="quote", max_w=860)
    y += qp

if q_cn_lines:
    y += 30
    for ln in q_cn_lines:
        sf.text(W // 2, y, ln, family="cjk-sc", size=CL, fill=(196, 194, 188), anchor="mt", role="body", max_w=860)
        y += cp

y = fact_y
for ln in f_lines:
    sf.text(W // 2, y, ln, family="serif", size=FL, fill=(224, 220, 212), anchor="mt", role="body", max_w=860)
    y += fp

if f_cn_lines:
    y += 30
    for ln in f_cn_lines:
        sf.text(W // 2, y, ln, family="cjk-sc", size=CL, fill=(186, 184, 179), anchor="mt", role="body", max_w=860)
        y += cp

sw_t, sh_t = sf.measure(SERIAL, "mono", 24)
dw_t, dh_t = sf.measure(DATE, "mono", 24)
gap = 64
tot = sw_t + gap + dw_t
base_l = (W - tot) // 2
ser_cx = base_l + sw_t // 2
dat_cx = base_l + sw_t + gap + dw_t // 2

sf.serial(ser_cx, plaque_y, SERIAL, family="mono", size=24, fill=(222, 202, 152), anchor="mm", role="meta")
sf.datestamp(dat_cx, plaque_y, DATE, family="mono", size=24, fill=(222, 202, 152), anchor="mm", role="meta")

sf.save(OUT_PATH)
