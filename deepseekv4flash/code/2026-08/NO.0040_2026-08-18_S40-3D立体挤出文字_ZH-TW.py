import numpy as np
from PIL import Image, ImageDraw
from atelier_canvas import Surface

sf = Surface(1000, 1740, scale=2, bg=(7, 28, 60))
sf.frame(70, 60, 860, 1620)

W, H = sf.W, sf.H
H_LOGICAL = 1740

# 背景：深海漸層，底部轉為鹽漠
lay = sf.layer()
yy = np.linspace(0, H_LOGICAL, H)[:, None, None]
top = np.array([7, 28, 60]).reshape(1, 1, 3)
mid = np.array([13, 58, 100]).reshape(1, 1, 3)
c = top * (1.0 - yy / H_LOGICAL) + mid * (yy / H_LOGICAL)

salt_start = 1450.0
salt_end = 1680.0
st = np.clip((yy - salt_start) / (salt_end - salt_start), 0.0, 1.0)
salt_a = np.array([168, 160, 130]).reshape(1, 1, 3)
salt_b = np.array([238, 231, 202]).reshape(1, 1, 3)
salt_col = salt_a * (1.0 - st) + salt_b * st
c = c * (1.0 - st) + salt_col * st

lay[..., :3] = c.astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# 鹽漠透視線
grid = sf.layer()
gi = Image.fromarray(grid)
gd = ImageDraw.Draw(gi)
horizon = int(1465 * 2)
gd.line([(0, horizon), (W, horizon)], fill=(206, 198, 170, 255), width=4)
vp = (W // 2, horizon)
for k in range(-5, 6):
    x0 = vp[0] + k * 230
    gd.line([vp, (x0, H)], fill=(178, 168, 138, 255), width=3)
for i in range(1, 8):
    t = (i / 7.0) ** 2
    y = horizon + int(t * (H - horizon))
    gd.line([(0, y), (W, y)], fill=(178, 168, 138, 255), width=2)
sf.composite(grid, mode="normal", opacity=0.45)

# 鹽晶體
crystals = sf.layer()
ci = Image.fromarray(crystals)
cd = ImageDraw.Draw(ci)

def draw_crystal(cx, base, hgt, half):
    cx *= 2
    base *= 2
    hgt *= 2
    half *= 2
    pts = [
        (int(cx - half), int(base)),
        (int(cx), int(base - hgt)),
        (int(cx + half), int(base)),
    ]
    cd.polygon(pts, fill=(240, 233, 205, 180))
    cd.line([pts[0], pts[1], pts[2]], fill=(212, 202, 172, 230), width=3)

draw_crystal(180, 1605, 105, 52)
draw_crystal(420, 1570, 78, 40)
draw_crystal(680, 1600, 120, 58)
draw_crystal(880, 1620, 92, 46)
sf.composite(crystals, mode="normal", opacity=0.5)

# 暗角
vig = sf.layer()
xx = np.linspace(0, 1, W)[None, :]
yyv = np.linspace(0, 1, H)[:, None]
rv = ((xx - 0.5) * 1.7) ** 2 + ((yyv - 0.5) * 1.3) ** 2
v = np.clip(rv - 0.45, 0, 1.6)
vig[..., 3] = (v * 90).astype(np.uint8)
sf.composite(vig)

# 流水號／日期的立體銘牌
badge = sf.layer()
bi = Image.fromarray(badge)
bd = ImageDraw.Draw(bi)

def plaque(x1, y1, x2, y2, z=6):
    z *= 2
    x1 *= 2
    y1 *= 2
    x2 *= 2
    y2 *= 2
    bd.rectangle([(x1 + z, y1 + z), (x2 + z, y2 + z)], fill=(5, 22, 46, 255))
    bd.rectangle([(x1, y1), (x2, y2)], fill=(18, 62, 106, 255))
    bd.line([(x1, y1), (x2, y1), (x2, y2)], fill=(70, 150, 202, 255), width=3)
    bd.line([(x1, y2), (x2, y2)], fill=(8, 28, 50, 255), width=4)

plaque(70, 58, 192, 95)
plaque(808, 58, 930, 95)
sf.composite(badge, mode="normal", opacity=1.0)

# 3D 立體擠出文字
def extrude_line(cx, y, text, size, face, side, depth=12, dx=3, dy=14):
    for i in range(depth, 0, -1):
        sf.text(
            cx + i * dx, y + i * dy, text,
            family="cjk-tc", size=size, fill=side,
            anchor="mt", role="title", allow_overlap=True,
        )
    sf.text(
        cx, y, text,
        family="cjk-tc", size=size, fill=face,
        anchor="mt", role="title", allow_overlap=True,
    )

title_size = 96
if sf.measure("也曾是最白的鹽。", "cjk-tc", title_size)[0] > 790:
    title_size = 88

extrude_line(
    500, 390, "最深的藍，", title_size,
    face=(110, 224, 252), side=(58, 138, 210),
)
extrude_line(
    500, 610, "也曾是最白的鹽。", title_size,
    face=(253, 249, 231), side=(118, 138, 168),
)

# 冷知識正文
lines = sf.wrap(FACT, "cjk-tc", 31, max_w=860)
fy = 1060
for line in lines:
    sf.text(
        70, fy, line,
        family="cjk-tc", size=31, fill=(216, 232, 242),
        anchor="lt", role="body",
    )
    fy += 50

# 流水號與日期
date_x = 918 - int(sf.measure(DATE, "mono", 19)[0])
sf.serial(84, 68, SERIAL, family="mono", size=19, fill=(228, 243, 251), anchor="lt", role="meta")
sf.datestamp(date_x, 68, DATE, family="mono", size=19, fill=(228, 243, 251), anchor="lt", role="meta")

sf.save(OUT_PATH)
