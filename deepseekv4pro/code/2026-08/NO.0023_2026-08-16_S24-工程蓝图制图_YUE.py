from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw

W, H = 900, 1600
SCALE = 2

sf = Surface(W, H, scale=SCALE, bg=(10, 20, 55))

# ─── Tier 2: Background grid ───
grid_layer = sf.layer()

minor_c = np.array([16, 34, 82, 255], dtype=np.uint8)
major_c = np.array([34, 60, 125, 255], dtype=np.uint8)

for x_log in range(0, W + 1, 25):
    x_phys = int(x_log * SCALE)
    if 0 <= x_phys < sf.W:
        grid_layer[:, x_phys:x_phys + 1, :] = minor_c

for y_log in range(0, H + 1, 25):
    y_phys = int(y_log * SCALE)
    if 0 <= y_phys < sf.H:
        grid_layer[y_phys:y_phys + 1, :, :] = minor_c

for x_log in range(0, W + 1, 100):
    x_phys = int(x_log * SCALE)
    if 0 <= x_phys < sf.W:
        grid_layer[:, x_phys:x_phys + 2, :] = major_c

for y_log in range(0, H + 1, 100):
    y_phys = int(y_log * SCALE)
    if 0 <= y_phys < sf.H:
        grid_layer[y_phys:y_phys + 2, :, :] = major_c

sf.composite(grid_layer, mode="screen", opacity=0.35)

# ─── Tier 2: Border, title block, technical decorations ───
deco_arr = sf.layer()
deco_img = Image.fromarray(deco_arr, mode="RGBA")
draw = ImageDraw.Draw(deco_img)

def PL(x):
    return int(x * SCALE)

WHITE = (220, 235, 255, 255)
CYAN  = (160, 200, 255, 200)

# Double border
draw.rectangle([PL(40), PL(40), PL(W - 40), PL(H - 40)], outline=WHITE, width=4)
draw.rectangle([PL(48), PL(48), PL(W - 48), PL(H - 48)], outline=CYAN, width=2)

# Corner registration ticks
tick_len = 28
tick_gap = 10
corners = [
    (40, 40, 1, 1),
    (W - 40, 40, -1, 1),
    (40, H - 40, 1, -1),
    (W - 40, H - 40, -1, -1),
]
for cx, cy, dx, dy in corners:
    x0 = PL(cx + dx * tick_gap)
    y0 = PL(cy + dy * tick_gap)
    x1 = PL(cx + dx * (tick_gap + tick_len))
    y1 = PL(cy + dy * (tick_gap + tick_len))
    draw.line([x0, PL(cy), x1, PL(cy)], fill=WHITE, width=2)
    draw.line([PL(cx), y0, PL(cx), y1], fill=WHITE, width=2)

# Title block (bottom right)
tb_x1, tb_y1 = 540, 1440
tb_x2, tb_y2 = 852, 1540
draw.rectangle([PL(tb_x1), PL(tb_y1), PL(tb_x2), PL(tb_y2)], outline=WHITE, width=2)
draw.line([PL(tb_x1), PL(tb_y1 + 42), PL(tb_x2), PL(tb_y1 + 42)], fill=CYAN, width=2)
draw.line([PL(tb_x1 + 160), PL(tb_y1 + 42), PL(tb_x1 + 160), PL(tb_y2)], fill=CYAN, width=2)

# Decorative bottle silhouette (left side, between fact and title block)
bx_center = 150
neck_w = 26
body_w = 78
b_top = 760
b_bottom = 1080
neck_h = 90

# Neck
draw.line([PL(bx_center - neck_w // 2), PL(b_top), PL(bx_center + neck_w // 2), PL(b_top)], fill=CYAN, width=2)
draw.line([PL(bx_center - neck_w // 2), PL(b_top), PL(bx_center - neck_w // 2), PL(b_top + neck_h)], fill=CYAN, width=2)
draw.line([PL(bx_center + neck_w // 2), PL(b_top), PL(bx_center + neck_w // 2), PL(b_top + neck_h)], fill=CYAN, width=2)

# Shoulder (ellipse)
body_top = b_top + neck_h
draw.ellipse(
    [PL(bx_center - body_w), PL(body_top - 18), PL(bx_center + body_w), PL(body_top + 18)],
    outline=CYAN, width=2
)

# Body sides
draw.line([PL(bx_center - body_w), PL(body_top), PL(bx_center - body_w), PL(b_bottom - 30)], fill=CYAN, width=2)
draw.line([PL(bx_center + body_w), PL(body_top), PL(bx_center + body_w), PL(b_bottom - 30)], fill=CYAN, width=2)

# Bottom arc
draw.ellipse(
    [PL(bx_center - body_w), PL(b_bottom - 60), PL(bx_center + body_w), PL(b_bottom)],
    outline=CYAN, width=2
)

# Label lines inside bottle
draw.line([PL(bx_center - body_w + 8), PL(body_top + 55), PL(bx_center + body_w - 8), PL(body_top + 55)], fill=CYAN, width=1)
draw.line([PL(bx_center - body_w + 8), PL(body_top + 70), PL(bx_center + body_w - 8), PL(body_top + 70)], fill=CYAN, width=1)

# Dimension line for bottle
draw.line([PL(bx_center - body_w - 35), PL(b_top), PL(bx_center - body_w - 35), PL(b_bottom)], fill=CYAN, width=1)
draw.line([PL(bx_center - body_w - 42), PL(b_top), PL(bx_center - body_w - 28), PL(b_top)], fill=CYAN, width=1)
draw.line([PL(bx_center - body_w - 42), PL(b_bottom), PL(bx_center - body_w - 28), PL(b_bottom)], fill=CYAN, width=1)

# Crosshair marks in empty space
for cy_cross in [660, 1280]:
    ch_len = 16
    draw.line([PL(450 - ch_len), PL(cy_cross), PL(450 + ch_len), PL(cy_cross)], fill=CYAN, width=1)
    draw.line([PL(450), PL(cy_cross - ch_len), PL(450), PL(cy_cross + ch_len)], fill=CYAN, width=1)
    draw.ellipse([PL(450 - ch_len - 6), PL(cy_cross - ch_len - 6), PL(450 + ch_len + 6), PL(cy_cross + ch_len + 6)], outline=CYAN, width=1)

# Large faint guide circle (right side, below fact)
guide_cx, guide_cy, guide_r = 750, 950, 160
draw.ellipse(
    [PL(guide_cx - guide_r), PL(guide_cy - guide_r), PL(guide_cx + guide_r), PL(guide_cy + guide_r)],
    outline=(100, 140, 200, 110), width=1
)
# Crosshair at center of guide circle
draw.line([PL(guide_cx - 25), PL(guide_cy), PL(guide_cx + 25), PL(guide_cy)], fill=CYAN, width=1)
draw.line([PL(guide_cx), PL(guide_cy - 25), PL(guide_cx), PL(guide_cy + 25)], fill=CYAN, width=1)

deco_result = np.array(deco_img)
sf.composite(deco_result, mode="normal", opacity=0.9)

# ─── Tier 1: Text ───
sf.frame(48, 48, W - 96, H - 96)

quote_box = sf.text(
    80, 110, QUOTE,
    family="cjk-hk", size=38, fill=(235, 242, 255),
    anchor="lt", role="quote", bold=True,
    max_w=W - 160, line_gap=0.4
)

fact_y = quote_box.bottom + 45
fact_box = sf.text(
    80, fact_y, FACT,
    family="cjk-hk", size=30, fill=(205, 220, 250),
    anchor="lt", role="body", bold=False,
    max_w=W - 160, line_gap=0.35
)

# Serial and date inside title block
serial_center_x = tb_x1 + 80
date_center_x = tb_x1 + 160 + 76
tb_text_y = tb_y1 + 42 + (tb_y2 - (tb_y1 + 42)) // 2

sf.serial(
    serial_center_x, tb_text_y, SERIAL,
    family="mono", size=20, fill=(225, 238, 255),
    anchor="mm", role="meta"
)

sf.datestamp(
    date_center_x, tb_text_y, DATE,
    family="mono", size=20, fill=(225, 238, 255),
    anchor="mm", role="meta"
)

sf.save(OUT_PATH)
