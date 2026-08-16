import numpy as np
from atelier_canvas import Surface

W, H = 1000, 1600
scale = 2

BLACK = (0, 0, 0)
RED = (226, 8, 20)
GRAY = (210, 210, 210)

sf = Surface(W, H, scale=scale, bg=(255, 255, 255))

# ---------- Tier 2: decoration ----------
lay = sf.layer()

def rect(lyr, x, y, w, h, color, a=255):
    xs = int(round(x * scale))
    xe = int(round((x + w) * scale))
    ys = int(round(y * scale))
    ye = int(round((y + h) * scale))
    xs = max(0, min(xs, lyr.shape[1]))
    xe = max(0, min(xe, lyr.shape[1]))
    ys = max(0, min(ys, lyr.shape[0]))
    ye = max(0, min(ye, lyr.shape[0]))
    if xe <= xs or ye <= ys:
        return
    lyr[ys:ye, xs:xe, 0] = color[0]
    lyr[ys:ye, xs:xe, 1] = color[1]
    lyr[ys:ye, xs:xe, 2] = color[2]
    lyr[ys:ye, xs:xe, 3] = a

# top and bottom solid bars
rect(lay, 0, 0, W, 10, BLACK)
rect(lay, 0, H - 10, W, 10, BLACK)

# Swiss grid vertical rules
for gx in (357, 642):
    rect(lay, gx, 10, 1, H - 20, GRAY)

# header rule
rect(lay, 72, 72, 856, 2, BLACK)

# quote positions
q1_y = 150
q2_y = 290
q3_y = 430

q1_text = "有些声音被留在纸上，"
q2_text = "像一封寄给百年后"
q3_text = "耳朵的信。"

# red square aligned to right margin
rect(lay, 902, q1_y, 26, 26, RED)

# rule under quote
ry = 600
rect(lay, 72, ry, 216, 4, RED)
rect(lay, 288, ry, 640, 4, BLACK)

# sound-waveform bars
y_base = 1480
max_h = 280
bars_n = 49
bar_w = 9
gap = 6
total_w = bars_n * bar_w + (bars_n - 1) * gap
x0 = 72 + (856 - total_w) / 2

rng = np.random.RandomState(24)
t = np.linspace(0, 2.5 * np.pi, bars_n)
amp = 0.5 + 0.5 * np.sin(t)
heights = (max_h * 0.12 + amp * max_h * 0.88).astype(int)

for i in range(bars_n):
    bx = x0 + i * (bar_w + gap)
    by = y_base - heights[i]
    rect(lay, bx, by, bar_w, heights[i], BLACK)

# waveform baseline
rect(lay, 72, y_base, 856, 2, BLACK)

# footer rule above serial/date
rect(lay, 72, 1524, 856, 2, BLACK)

sf.composite(lay, mode="normal", opacity=1.0)

# ---------- Tier 1: text ----------
sf.frame(56, 24, 888, 1548)

sf.text(72, q1_y, q1_text, family="cjk-sc", size=80, bold=True,
        fill=BLACK, anchor="lt", role="quote", max_w=856)
sf.text(216, q2_y, q2_text, family="cjk-sc", size=80, bold=True,
        fill=BLACK, anchor="lt", role="quote", max_w=856)
sf.text(360, q3_y, q3_text, family="cjk-sc", size=80, bold=True,
        fill=BLACK, anchor="lt", role="quote", max_w=856)

sf.text(72, 660, FACT, family="cjk-sc", size=34, bold=False,
        fill=BLACK, anchor="lt", role="body", max_w=856, line_gap=0.6)

sf.serial(72, 1540, SERIAL, family="sans", size=22,
          fill=BLACK, anchor="lt", role="meta")
sf.datestamp(928, 1540, DATE, family="sans", size=22,
             fill=BLACK, anchor="rt", role="meta")

sf.save(OUT_PATH)
