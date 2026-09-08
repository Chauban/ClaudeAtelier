from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from atelier_canvas import Surface

W, H = 950, 1800
CX = W / 2.0
S = 2
AW, AH = W * S, H * S

def px(v):
    return int(round(v * S))

sf = Surface(W, H, scale=2, bg=(224, 230, 236))
sf.frame(55, 55, W - 110, H - 110)

DARK_BAND = (27, 35, 46)
INK       = (38, 50, 68)
SOFT_INK  = (52, 64, 84)
CREAM     = (238, 228, 204)
ORANGE    = (226, 94, 52)
VINYL     = (26, 30, 38)
NAVY      = (28, 45, 72)
LABEL_TXT = (238, 230, 211)

# ---------- sleeve header / footer bands ----------
bands = Image.new("RGBA", (AW, AH), (0, 0, 0, 0))
bd = ImageDraw.Draw(bands)
bd.rectangle([px(70), px(88), px(W - 70), px(144)], fill=DARK_BAND + (255,))
bd.rectangle([px(70), px(1746), px(W - 70), px(1796)], fill=DARK_BAND + (255,))
bd.rectangle([px(99), px(106), px(127), px(124)], fill=ORANGE + (255,))
bd.line([px(70), px(149), px(W - 70), px(149)], fill=(190, 170, 140, 150), width=2)
bd.line([px(70), px(1742), px(W - 70), px(1742)], fill=(190, 170, 140, 150), width=2)
sf.composite(bands)

# ---------- vinyl drop shadow ----------
cy_px = px(995)
cx_px = px(CX)
R_DISC = px(300)

shadow = Image.new("RGBA", (AW, AH), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.ellipse([cx_px - R_DISC, cy_px - R_DISC + px(30),
            cx_px + R_DISC, cy_px + R_DISC + px(30)],
           fill=(70, 76, 82, 110))
shadow = shadow.filter(ImageFilter.GaussianBlur(px(22)))
sf.composite(shadow)

# ---------- vinyl disc ----------
vinyl = Image.new("RGBA", (AW, AH), (0, 0, 0, 0))
vd = ImageDraw.Draw(vinyl)

vd.ellipse([cx_px - R_DISC, cy_px - R_DISC,
            cx_px + R_DISC, cy_px + R_DISC],
           fill=VINYL + (255,))

# micro-grooves on the shoulder
for rr in range(px(205), R_DISC - px(6), px(7)):
    vd.ellipse([cx_px - rr, cy_px - rr, cx_px + rr, cy_px + rr],
               outline=(132, 142, 150, 42), width=1)

# vinyl surface sheen
vd.arc([cx_px - px(288), cy_px - px(288), cx_px + px(288), cy_px + px(288)],
       start=15, end=140, fill=(180, 190, 198, 100), width=px(7))
vd.arc([cx_px - px(296), cy_px - px(296), cx_px + px(296), cy_px + px(296)],
       start=30, end=125, fill=(195, 205, 212, 55), width=px(3))

# printed label
R_LBL = px(176)
vd.ellipse([cx_px - R_LBL, cy_px - R_LBL, cx_px + R_LBL, cy_px + R_LBL],
           fill=NAVY + (255,))

# concentric label rings
vd.ellipse([cx_px - px(170), cy_px - px(170), cx_px + px(170), cy_px + px(170)],
           outline=CREAM + (255,), width=2)
vd.ellipse([cx_px - px(162), cy_px - px(162), cx_px + px(162), cy_px + px(162)],
           outline=ORANGE + (230,), width=2)
vd.ellipse([cx_px - px(50), cy_px - px(50), cx_px + px(50), cy_px + px(50)],
           outline=(255, 255, 255, 70), width=2)
vd.ellipse([cx_px - px(44), cy_px - px(44), cx_px + px(44), cy_px + px(44)],
           outline=(255, 255, 255, 50), width=1)

# spindle hole
hr = px(14)
vd.ellipse([cx_px - hr, cy_px - hr, cx_px + hr, cy_px + hr],
           fill=(0, 0, 0, 0))

sf.composite(vinyl)

# ---------- warm "red fin heat" wash on the groove zone ----------
yy = np.arange(AH, dtype=np.float32)[:, None]
xx = np.arange(AW, dtype=np.float32)[None, :]
dx = xx - cx_px
dy = yy - cy_px
dist = np.sqrt(dx * dx + dy * dy)
ang = np.arctan2(dy, dx)

warm_zone = (dist >= px(206)) & (dist <= R_DISC - px(8)) & (ang > -2.25) & (ang < -0.5)

warm = sf.layer()
warm[..., 0] = 240
warm[..., 1] = 96
warm[..., 2] = 48
alpha_warm = np.zeros((AH, AW), dtype=np.uint8)
alpha_warm[warm_zone] = 150
warm[..., 3] = alpha_warm
warm_blur = Image.fromarray(warm).filter(ImageFilter.GaussianBlur(px(26)))
sf.composite(warm_blur, mode="screen", opacity=0.5)

# ---------- quote ----------
q1 = QUOTE[:6]
q2 = QUOTE[6:]

q_y = 232
b1 = sf.text(CX, q_y, q1,
             family="cjk-hk", size=96, bold=True,
             fill=INK, anchor="mt", max_w=W - 120,
             role="quote")
q_y = b1.bottom + 30
b2 = sf.text(CX, q_y, q2,
             family="cjk-hk", size=96, bold=True,
             fill=INK, anchor="mt", max_w=W - 120,
             role="quote")

# ---------- label typography ----------
sf.serial(CX, 918, SERIAL,
          family="serif", size=25, bold=False,
          fill=LABEL_TXT, anchor="mt", role="meta")

sf.datestamp(CX, 1100, DATE,
             family="serif", size=23, bold=False,
             fill=LABEL_TXT, anchor="mt", role="meta")

# ---------- separator rule above liner note ----------
rule = Image.new("RGBA", (AW, AH), (0, 0, 0, 0))
rd = ImageDraw.Draw(rule)
rd.line([px(125), px(1338), px(W - 125), px(1338)],
        fill=(168, 176, 184, 170), width=2)
rd.rectangle([px(118), px(1335), px(150), px(1341)],
             fill=ORANGE + (255,))
sf.composite(rule)

# ---------- fact as printed liner text ----------
fact_rows = sf.wrap(FACT, "cjk-hk", 28, W - 240)

fy = 1378
for row in fact_rows:
    b = sf.text(125, fy, row,
                family="cjk-hk", size=28,
                fill=SOFT_INK, anchor="lt",
                max_w=W - 240, line_gap=0.2,
                role="body")
    fy = b.bottom + 6

sf.save(OUT_PATH)
