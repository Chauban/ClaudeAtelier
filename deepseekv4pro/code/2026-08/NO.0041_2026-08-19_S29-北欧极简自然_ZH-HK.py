from atelier_canvas import Surface
from PIL import Image, ImageDraw
import numpy as np

w, h = 920, 1600
sf = Surface(w, h, scale=2, bg=(247, 245, 239))
sf.frame(70, 80, 780, 1420)

# 柔和渐变底
grad = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
grad[..., 0] = (248 - 5 * yy).astype(np.uint8)
grad[..., 1] = (246 - 3 * yy).astype(np.uint8)
grad[..., 2] = (240 - 4 * yy).astype(np.uint8)
grad[..., 3] = 255
sf.composite(grad, opacity=0.72)

S = 2
def P(*v):
    return tuple(x * S for x in v)

decor = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(decor)

# 北欧淡彩几何 / 植物意象
d.ellipse(P(700, -140, 980, 170), fill=(174, 188, 174, 44))
d.ellipse(P(-180, 880, 300, 1480), fill=(202, 180, 158, 42))
d.ellipse(P(760, 1350, 980, 1540), fill=(188, 197, 186, 40))

# 细线
d.line(P(70, 64, 850, 64), fill=(160, 172, 160, 150), width=2)
d.line(P(70, 1260, 850, 1260), fill=(160, 172, 160, 150), width=2)

# 右上小枝
d.line(P(806, 86, 750, 156), fill=(125, 145, 128, 220), width=3)
for x, y in [(795, 102), (770, 118), (748, 138)]:
    d.ellipse(P(x - 7, y - 3, x + 7, y + 3), outline=(125, 145, 128, 220), width=2)
for x, y in [(784, 108), (756, 124), (738, 146)]:
    d.ellipse(P(x - 2, y - 2, x + 2, y + 2), fill=(174, 132, 106, 220))

# 左下小枝
d.line(P(150, 1300, 100, 1440), fill=(125, 145, 128, 180), width=3)
for x, y in [(138, 1330), (112, 1362), (94, 1398)]:
    d.ellipse(P(x - 6, y - 3, x + 6, y + 3), outline=(125, 145, 128, 180), width=2)

sf.composite(decor, mode="normal", opacity=1.0)

quote_box = sf.text(
    70, 180, QUOTE,
    family="cjk-hk", size=38, fill=(45, 55, 48),
    anchor="lt", role="quote", bold=True,
    max_w=780, line_gap=0.55
)

fact_y = quote_box.bottom + 80
fact_box = sf.text(
    70, fact_y, FACT,
    family="cjk-hk", size=28, fill=(74, 81, 74),
    anchor="lt", role="body", bold=False,
    max_w=780, line_gap=0.52
)

meta_y = 1284
sf.serial(70, meta_y, SERIAL, family="sans", size=18, fill=(99, 108, 99), anchor="lt", role="meta")
sf.datestamp(850, meta_y, DATE, family="sans", size=18, fill=(99, 108, 99), anchor="rt", role="meta")

sf.save(OUT_PATH)
