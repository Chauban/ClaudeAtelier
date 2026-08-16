import math
import numpy as np
from PIL import Image, ImageDraw

from atelier_canvas import Surface

w, h = 1000, 1800
S = 2

sf = Surface(w, h, scale=2, bg=(245, 242, 233))
sf.frame(85, 70, 830, 1680)

# ---- Tier 2: karesansui background art ---------------------------------
art = sf.layer()
img = Image.fromarray(art, 'RGBA')
d = ImageDraw.Draw(img)

# Raked sand field in the middle band, light and quiet
for i, ylog in enumerate(range(440, 941, 15)):
    phase = i * 0.65
    pts = []
    for xlog in range(120, 931, 2):
        x = xlog * S
        y = ylog * S + int(7 * math.sin((xlog - 120) * 0.022 + phase))
        pts.append((x, y))
    d.line(pts, fill=(203, 195, 178, 255), width=3)

# A few irregular rocks, gray with lighter top surfaces
rock_fill = (112, 110, 108, 255)
rock_light = (188, 184, 176, 255)

rock1 = [(345, 884), (410, 850), (505, 842), (575, 862), (610, 892),
         (570, 920), (435, 922), (355, 905)]
d.polygon([(x * S, y * S) for x, y in rock1], fill=rock_fill)
d.polygon([(390 * S, 870 * S), (460 * S, 858 * S), (520 * S, 856 * S),
           (545 * S, 876 * S), (500 * S, 896 * S), (420 * S, 892 * S)],
          fill=rock_light)

rock2 = [(675, 872), (738, 849), (798, 856), (820, 887),
         (782, 914), (702, 906)]
d.polygon([(x * S, y * S) for x, y in rock2], fill=rock_fill)
d.polygon([(702 * S, 865 * S), (748 * S, 857 * S), (785 * S, 864 * S),
           (800 * S, 880 * S), (765 * S, 892 * S), (715 * S, 884 * S)],
          fill=rock_light)

rock3 = [(840, 899), (880, 887), (910, 904), (892, 927), (848, 920)]
d.polygon([(x * S, y * S) for x, y in rock3], fill=rock_fill)
d.polygon([(854 * S, 902 * S), (878 * S, 895 * S), (897 * S, 902 * S),
           (882 * S, 916 * S), (858 * S, 912 * S)], fill=rock_light)

# Pebbles
for cx, cy, rx, ry in [(640, 890, 11, 7), (678, 877, 8, 5), (720, 894, 12, 8)]:
    d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S],
              fill=(174, 170, 162, 255))

# Thin registration line for serial/date, drawn before text as part of decor
d.line([(85 * S, 1700 * S), (340 * S, 1700 * S)], fill=(122, 120, 116, 255), width=2)

sf.composite(img)

# ---- Tier 1: text -------------------------------------------------------
ink = (52, 50, 46)
muted = (92, 89, 83)

quote_en = QUOTE.split('（')[0].strip()
quote_cn = QUOTE.split('（')[1].rstrip('）').strip()

fact_en = FACT.split('（')[0].strip()
fact_cn = FACT.split('（')[1].rstrip('）').strip()

# Quote
q_box = sf.text(
    85, 150, quote_en,
    family="serif", size=40, fill=ink,
    anchor="lt", role="quote",
    max_w=830, line_gap=0.5
)
qt_box = sf.text(
    85, q_box.bottom + 26, quote_cn,
    family="cjk-sc", size=28, fill=muted,
    anchor="lt", role="body",
    max_w=830, line_gap=0.45
)

# Fact
fact_y = 1010
fact_box = sf.text(
    85, fact_y, fact_en,
    family="sans", size=30, fill=ink,
    anchor="lt", role="body",
    max_w=830, line_gap=0.4
)
ft_box = sf.text(
    85, fact_box.bottom + 26, fact_cn,
    family="cjk-sc", size=28, fill=muted,
    anchor="lt", role="body",
    max_w=830, line_gap=0.4
)

# Serial and date
serial_y = 1710
serial_box = sf.serial(
    85, serial_y, SERIAL,
    family="sans", size=18, fill=muted,
    anchor="lt", role="meta"
)
sf.datestamp(
    serial_box.right + 30, serial_y, DATE,
    family="sans", size=18, fill=muted,
    anchor="lt", role="meta"
)

sf.save(OUT_PATH)
