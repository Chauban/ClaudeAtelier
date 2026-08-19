from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 2
W, H = 900, 1760

sf = Surface(W, H, scale=2, bg=(200, 160, 108))
sf.frame(70, 70, 760, 1620)

# ---------- layout constants ----------
panel_x, panel_w = 80, 740
inner_x = panel_x + 32
max_w = panel_w - 64

body_size = 30
fact_lines = sf.wrap(FACT, "cjk-hk", body_size, max_w)
if len(fact_lines) > 8:
    body_size = 28
    fact_lines = sf.wrap(FACT, "cjk-hk", body_size, max_w)

line_heights = [sf.measure(l, "cjk-hk", body_size)[1] for l in fact_lines]
text_block_h = sum(line_heights) + 12 * (len(fact_lines) - 1)

panel_y = 900
text_top = panel_y + 38
panel_bottom = text_top + text_block_h + 40
panel_h = panel_bottom - panel_y
stamp_y = panel_bottom + 60

# ---------- base kraft paper ----------
rng = np.random.default_rng(11)
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
nr = rng.normal(0, 4.5, (sf.H, sf.W))
nr2 = rng.normal(0, 1.8, (sf.H, sf.W))
lay[..., 0] = np.clip(212 - 32*yy + 5*np.sin(xx*7) + nr, 0, 255).astype(np.uint8)
lay[..., 1] = np.clip(170 - 25*yy + 4*np.sin(xx*7) + nr + nr2, 0, 255).astype(np.uint8)
lay[..., 2] = np.clip(114 - 20*yy + 3*np.sin(xx*7) + nr - nr2, 0, 255).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# ---------- paper fibres ----------
fib = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(fib)
frng = np.random.default_rng(8)
for _ in range(18):
    x0 = float(frng.integers(0, W))
    y0 = float(frng.integers(0, H))
    ang = float(frng.uniform(0, np.pi))
    ln = float(frng.uniform(30, 130))
    d.line([x0*S, y0*S, (x0 + ln*np.cos(ang))*S, (y0 + ln*np.sin(ang))*S],
           fill=(250, 234, 196, 18), width=int(1*S))
fib = fib.filter(ImageFilter.GaussianBlur(int(0.6*S)))
sf.composite(fib)

# ---------- age stains ----------
stains = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(stains)
srng = np.random.default_rng(5)
for _ in range(22):
    cxp = int(srng.integers(0, sf.W))
    cyp = int(srng.integers(0, sf.H))
    rxp = int(srng.integers(26, 150) * S)
    ryp = int(srng.integers(16, 90) * S)
    a = int(srng.integers(8, 20))
    if int(srng.integers(0, 2)) == 0:
        col = (142, 100, 50, a)
    else:
        col = (236, 206, 158, a)
    d.ellipse([cxp - rxp, cyp - ryp, cxp + rxp, cyp + ryp], fill=col)
stains = stains.filter(ImageFilter.GaussianBlur(40))
sf.composite(stains)

# ---------- coffee rings ----------
rings = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(rings)
d.ellipse([70*S, 40*S, 230*S, 200*S], outline=(150, 90, 38, 40), width=int(2.6*S))
d.ellipse([78*S, 48*S, 222*S, 192*S], outline=(150, 90, 38, 24), width=int(1.4*S))
d.ellipse([704*S, 1244*S, 816*S, 1356*S], outline=(150, 90, 38, 34), width=int(2*S))
rings = rings.filter(ImageFilter.GaussianBlur(int(1.4*S)))
sf.composite(rings)

# ---------- faded teal watercolour wash ----------
wash = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(wash)
d.ellipse([150*S, 100*S, 750*S, 700*S], fill=(84, 138, 152, 42))
d.ellipse([300*S, 280*S, 630*S, 600*S], fill=(96, 150, 162, 26))
wash = wash.filter(ImageFilter.GaussianBlur(50))
sf.composite(wash)

# ---------- vignette ----------
vig = sf.layer()
vv = np.mgrid[0:sf.H, 0:sf.W].astype(np.float32)
nx = (vv[1] - sf.W / 2) / (sf.W / 2)
ny = (vv[0] - sf.H / 2) / (sf.H / 2)
dist = np.sqrt(nx * nx + ny * ny)
a = np.clip((dist - 0.60) / 0.55, 0, 1) ** 1.15
vig[..., 0] = 88
vig[..., 1] = 58
vig[..., 2] = 30
vig[..., 3] = (a * 110).astype(np.uint8)
sf.composite(vig)

# ---------- worn corners ----------
wear = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(wear)
for cx0, cy0 in [(-50, -50), (W + 50, -50), (-50, H + 50), (W + 50, H + 50)]:
    d.ellipse([(cx0 - 70)*S, (cy0 - 70)*S, (cx0 + 70)*S, (cy0 + 70)*S], fill=(66, 44, 24, 44))
wear = wear.filter(ImageFilter.GaussianBlur(int(14*S)))
sf.composite(wear)

# ---------- inner aged frame line ----------
fr = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(fr)
d.rectangle([24*S, 24*S, (W - 24)*S, (H - 24)*S], outline=(82, 55, 33, 100), width=int(1.2*S))
sf.composite(fr)

# ---------- pufferfish mystery circle (ink drawing) ----------
nest = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
nd = ImageDraw.Draw(nest)
ink = (62, 42, 28, 215)
cx, cy, R = 450, 400, 245
nrng = np.random.default_rng(21)

for k in range(90):
    a0 = k * 2 * np.pi / 90
    a1 = (k + 1) * 2 * np.pi / 90
    rj = R + float(nrng.normal(0, 1.2))
    nd.line([(cx + rj*np.cos(a0))*S, (cy + rj*np.sin(a0))*S,
             (cx + rj*np.cos(a1))*S, (cy + rj*np.sin(a1))*S],
            fill=ink, width=int(3.2*S))

for k in range(26):
    a = k * 2 * np.pi / 26 + float(nrng.normal(0, 0.015))
    r0 = 40 + float(nrng.normal(0, 3))
    r1 = R - 14 + float(nrng.normal(0, 5))
    midr = (r0 + r1) / 2
    am = a + float(nrng.normal(0, 0.035))
    p0 = (cx + r0*np.cos(a), cy + r0*np.sin(a))
    pm = (cx + midr*np.cos(am), cy + midr*np.sin(am))
    p1 = (cx + r1*np.cos(a), cy + r1*np.sin(a))
    wdt = 3 if k % 3 == 0 else 2
    nd.line([p0[0]*S, p0[1]*S, pm[0]*S, pm[1]*S, p1[0]*S, p1[1]*S],
            fill=ink, width=int(wdt*S), joint="curve")

for rr, wd in [(75, 2), (130, 1)]:
    nd.ellipse([(cx - rr)*S, (cy - rr)*S, (cx + rr)*S, (cy + rr)*S], outline=ink, width=int(wd*S))

for rr, span, off in [(150, 2.2, 0.7), (172, 1.8, 3.6)]:
    a_s = float(nrng.uniform(0, 2 * np.pi)) + off
    nd.arc([(cx - rr)*S, (cy - rr)*S, (cx + rr)*S, (cy + rr)*S],
           start=round(np.degrees(a_s), 1), end=round(np.degrees(a_s + span), 1),
           fill=ink, width=int(2*S))

for _ in range(4):
    a = float(nrng.uniform(0, 2 * np.pi))
    ra = float(nrng.uniform(128, 142))
    rb = float(nrng.uniform(164, 180))
    nd.line([(cx + ra*np.cos(a))*S, (cy + ra*np.sin(a))*S,
             (cx + rb*np.cos(a))*S, (cy + rb*np.sin(a))*S], fill=ink, width=int(1.6*S))

for _ in range(30):
    a = float(nrng.uniform(0, 2 * np.pi))
    rr = float(nrng.uniform(R - 52, R - 14))
    s = float(nrng.uniform(1.4, 3.0))
    x = cx + rr * np.cos(a)
    y = cy + rr * np.sin(a)
    nd.ellipse([(x - s)*S, (y - s)*S, (x + s)*S, (y + s)*S], fill=ink)

nd.ellipse([(cx - 14)*S, (cy - 12)*S, (cx + 14)*S, (cy + 12)*S], outline=ink, width=int(2.2*S))
nd.ellipse([(cx - 4)*S, (cy - 4)*S, (cx + 4)*S, (cy + 4)*S], fill=ink)

for bx, by, br, ba in [(562, 142, 8, 90), (588, 112, 5, 70), (546, 168, 4, 60)]:
    nd.ellipse([(bx - br)*S, (by - br)*S, (bx + br)*S, (by + br)*S], outline=(62, 42, 28, ba), width=int(1.4*S))

fx, fy = 700, 576
nd.ellipse([(fx - 26)*S, (fy - 13)*S, (fx + 26)*S, (fy + 13)*S], outline=ink, width=int(2*S))
nd.line([(fx + 22)*S, (fy - 11)*S, (fx + 48)*S, fy*S], fill=ink, width=int(2*S))
nd.line([(fx + 48)*S, fy*S, (fx + 22)*S, (fy + 11)*S], fill=ink, width=int(2*S))
nd.ellipse([(fx - 13)*S, (fy - 4)*S, (fx - 6)*S, (fy + 4)*S], fill=ink)

nest = nest.filter(ImageFilter.GaussianBlur(int(0.8*S)))
sf.composite(nest)

# ---------- hand-drawn divider ----------
div = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(div)
div_col = (86, 58, 34, 175)
rngd = np.random.default_rng(33)
div_y = 858
pts = []
for i in range(12):
    x = 190 + i * 47.3
    y = div_y + float(rngd.normal(0, 1.6))
    pts.append((x * S, y * S))
d.line(pts, fill=div_col, width=int(2*S))
d.polygon([(450*S, (div_y - 10)*S), (464*S, div_y*S), (450*S, (div_y + 10)*S), (436*S, div_y*S)],
          fill=div_col, outline=div_col)
d.line([(155*S, div_y*S), (436*S, div_y*S)], fill=div_col, width=int(2*S))
d.line([(464*S, div_y*S), (745*S, div_y*S)], fill=div_col, width=int(2*S))
sf.composite(div)

# ---------- torn paper panel for FACT ----------
panel = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(panel)
d.polygon([(panel_x*S, panel_y*S),
           ((panel_x + panel_w)*S, panel_y*S),
           ((panel_x + panel_w - 8)*S, panel_bottom*S),
           (panel_x*S, panel_bottom*S)],
          fill=(224, 184, 130, 235))
d.polygon([(panel_x*S, panel_y*S),
           ((panel_x + panel_w)*S, panel_y*S),
           ((panel_x + panel_w - 8)*S, panel_bottom*S),
           (panel_x*S, panel_bottom*S)],
          outline=(130, 88, 42, 160), width=int(1.5*S))
for i in range(10):
    x0 = panel_x + i * (panel_w / 10)
    x1 = x0 + panel_w / 10
    y0 = panel_bottom + (4 if i % 2 == 0 else -3)
    y1 = panel_bottom + (-3 if i % 2 == 0 else 4)
    d.line([(x0*S, y0*S), (x1*S, y1*S)], fill=(224, 184, 130, 235), width=int(2*S))
panel = panel.filter(ImageFilter.GaussianBlur(int(0.6*S)))
sf.composite(panel)

# ---------- corner holes on panel ----------
holes = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(holes)
for hx, hy in [(panel_x + 22, panel_y + 22), (panel_x + panel_w - 22, panel_y + 22)]:
    d.ellipse([(hx - 8)*S, (hy - 8)*S, (hx + 8)*S, (hy + 8)*S], fill=(200, 160, 108, 255))
holes = holes.filter(ImageFilter.GaussianBlur(int(1*S)))
sf.composite(holes)

# ---------- TEXT (Tier 1) ----------

# Quote: 世上無難事，只怕有心魚。
qbox = sf.text(450, 700, QUOTE,
               family="serif-cjk", size=52, fill=(58, 40, 26),
               anchor="mt", role="quote", bold=True)

# Hand-drawn line under quote
ul = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(ul)
uy = qbox.bottom + 18
rngu = np.random.default_rng(7)
pts = []
for i in range(16):
    x = 210 + i * 30
    y = uy + float(rngu.normal(0, 1.2))
    pts.append((x * S, y * S))
d.line(pts, fill=(86, 58, 34, 165), width=int(1.6*S))
sf.composite(ul)

# Fact panel text — placed sequentially using box.bottom to prevent overlap
fact_size = body_size
fy = text_top
for line in fact_lines:
    box = sf.text(inner_x, fy, line,
                  family="cjk-hk", size=fact_size, fill=(58, 40, 26),
                  anchor="lt", role="body", max_w=max_w)
    fy = box.bottom + 12

# ---------- ink scale decorations on panel ----------
deco = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)
for i in range(4):
    d.arc([(panel_x + panel_w - 60 + i*8)*S, (panel_bottom - 60 + i*6)*S,
           (panel_x + panel_w - 30 + i*8)*S, (panel_bottom - 30 + i*6)*S],
          start=0, end=180, fill=(86, 58, 34, 120), width=int(1.4*S))
d.arc([(panel_x + 30)*S, (panel_bottom - 55)*S, (panel_x + 85)*S, (panel_bottom)*S],
      start=180, end=270, fill=(86, 58, 34, 100), width=int(1.4*S))
sf.composite(deco)

# ---------- date & serial in aged typewriter style ----------
sf.serial(140, stamp_y, SERIAL,
          family="mono", size=30, fill=(128, 60, 40),
          anchor="lt", role="meta", bold=True, rotate=-2.0)

sf.datestamp(W - 140, stamp_y, DATE,
             family="mono", size=28, fill=(62, 44, 28),
             anchor="rt", role="meta", bold=False, rotate=1.5)

# ---------- aged stamp frame ----------
stmp = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(stmp)
sy = stamp_y - 18
d.rectangle([(120)*S, (sy - 16)*S, (260)*S, (sy + 42)*S],
            outline=(128, 60, 40, 110), width=int(1.2*S))
d.rectangle([(124)*S, (sy - 12)*S, (256)*S, (sy + 38)*S],
            outline=(128, 60, 40, 70), width=int(0.8*S))
d.line([(W - 260)*S, (stamp_y + 8)*S, (W - 118)*S, (stamp_y + 8)*S],
       fill=(62, 44, 28, 90), width=int(1*S))
d.line([(W - 260)*S, (stamp_y - 14)*S, (W - 118)*S, (stamp_y - 14)*S],
       fill=(62, 44, 28, 60), width=int(0.8*S))
sf.composite(stmp)

# ---------- small hand-drawn fish tail accents ----------
acc = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(acc)
for ax, ay, rot in [(150, 140, 1.0), (750, 150, -0.8)]:
    d.arc([(ax - 22)*S, (ay - 12)*S, (ax + 22)*S, (ay + 12)*S],
          start=int(180 + rot * 40), end=int(360 - rot * 30),
          fill=(86, 58, 34, 130), width=int(2*S))
sf.composite(acc)

sf.save(OUT_PATH)
