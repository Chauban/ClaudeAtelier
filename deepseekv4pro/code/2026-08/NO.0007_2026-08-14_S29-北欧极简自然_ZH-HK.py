from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw

w, h = 900, 1500
sf = Surface(w, h, scale=2, bg=(246, 243, 237))
sf.frame(90, 60, 720, 1380)

S = 2
def P(v):
    return int(round(v * S))
def LW(v):
    return max(1, int(round(v * S)))

# ---------- background: soft nordic off-white gradient ----------
lay = sf.layer()
tt = np.linspace(0, 1, sf.H)[:, None]
top = np.array([248, 246, 241], dtype=np.float64)
bot = np.array([234, 230, 219], dtype=np.float64)
bg = (top[None, None, :] * (1 - tt[:, :, None]) + bot[None, None, :] * tt[:, :, None]).astype(np.uint8)
lay[..., :3] = np.broadcast_to(bg, (sf.H, sf.W, 3))
lay[..., 3] = 255
sf.composite(lay, mode="normal", opacity=1.0)

# ---------- fixed layout values, generous spacing to avoid overlap ----------
q1_y = 170
q2_y = 290
draw_top = 416
base_y = draw_top + 230
console_bottom = base_y + 70
halo_top = draw_top + 10
halo_bottom = draw_top + 350
halo_cy = (halo_top + halo_bottom) / 2
halo_r = (halo_bottom - halo_top) / 2
fact_top = 820

fact_lines = sf.wrap(FACT, "cjk-hk", 30, max_w=640)
fact_est_h = len(fact_lines) * 46
footer_y = max(fact_top + fact_est_h + 110, 1160)
if footer_y + 56 > h - 56:
    footer_y = h - 112

# ---------- graphics ----------
gfx = sf.layer()
img = Image.fromarray(gfx, mode="RGBA")
d = ImageDraw.Draw(img)

INK = (58, 68, 62, 240)
SAND = (213, 199, 173, 255)
SAGE_RULE = (168, 182, 167, 220)
HALO = (198, 208, 196, 120)

# top rule
d.line([P(90), P(130), P(810), P(130)], fill=SAGE_RULE, width=LW(1.5))

# halo circle behind organ
d.ellipse([P(450 - halo_r), P(halo_cy - halo_r), P(450 + halo_r), P(halo_cy + halo_r)],
          outline=HALO, width=LW(1.5))

# organ pipes
pipe_x0 = 315
pipe_w = 26
pipe_gap = 9
heights = [140, 170, 200, 225, 240, 225, 200, 160]
for i, ph in enumerate(heights):
    x0 = pipe_x0 + i * (pipe_w + pipe_gap)
    x1 = x0 + pipe_w
    top_y = draw_top + (230 - ph)
    d.rounded_rectangle([P(x0), P(top_y), P(x1), P(base_y)], radius=P(13),
                        outline=INK, width=LW(2))

# pipe rack
d.line([P(300), P(base_y - 12), P(600), P(base_y - 12)], fill=INK, width=LW(2))

# console
d.rounded_rectangle([P(280), P(base_y), P(610), P(console_bottom)], radius=P(10),
                    outline=INK, width=LW(2))

# keyboard ticks
ky = base_y + 45
d.line([P(312), P(ky), P(580), P(ky)], fill=INK, width=LW(2))
for k in range(7):
    kx = 312 + k * 44
    d.line([P(kx), P(ky), P(kx), P(ky + 14)], fill=INK, width=LW(2))

# sandbags holding keys
for sx in [352, 438, 520]:
    sy = ky - 8
    d.ellipse([P(sx - 18), P(sy - 11), P(sx + 18), P(sy + 12)], fill=SAND, outline=INK, width=LW(2))
    d.line([P(sx), P(sy - 12), P(sx), P(sy - 16)], fill=INK, width=LW(2))
    d.line([P(sx - 5), P(sy - 15), P(sx + 5), P(sy - 15)], fill=INK, width=LW(2))

# blower machine
mx0, my0, mx1, my1 = 648, base_y + 20, 702, base_y + 66
d.rounded_rectangle([P(mx0), P(my0), P(mx1), P(my1)], radius=P(8), outline=INK, width=LW(2))
d.line([P(664), P(my0 + 10), P(664), P(my1 - 10)], fill=INK, width=LW(2))
d.line([P(682), P(my0 + 10), P(682), P(my1 - 10)], fill=INK, width=LW(2))
d.line([P(mx0), P(my0 + 23), P(610), P(base_y + 22)], fill=INK, width=LW(2))
for wy in [my0 + 12, my0 + 23, my0 + 34]:
    d.line([P(mx1 + 6), P(wy), P(mx1 + 16), P(wy)], fill=INK, width=LW(2))

# footer rule and small mark
d.line([P(90), P(footer_y), P(810), P(footer_y)], fill=SAGE_RULE, width=LW(1.5))
d.rectangle([P(96), P(footer_y + 26), P(107), P(footer_y + 37)], fill=SAGE_RULE)

sf.composite(np.array(img), mode="normal", opacity=1.0)

# ---------- text ----------
ink_text = (60, 70, 64)

sf.text(450, q1_y, "慢，係另一種速度；", family="cjk-hk", size=52, fill=ink_text, anchor="mt", role="quote")
sf.text(450, q2_y, "沉默，係第一個音符。", family="cjk-hk", size=52, fill=ink_text, anchor="mt", role="quote")

sf.text(130, fact_top, FACT, family="cjk-hk", size=30, fill=(66, 76, 70),
        anchor="lt", role="body", max_w=640, line_gap=0.5)

meta_ink = (82, 92, 86)
sf.serial(130, footer_y + 24, SERIAL, family="sans", size=19, fill=meta_ink, anchor="lt", role="meta")
sf.datestamp(770, footer_y + 24, DATE, family="sans", size=19, fill=meta_ink, anchor="rt", role="meta")

sf.save(OUT_PATH)
