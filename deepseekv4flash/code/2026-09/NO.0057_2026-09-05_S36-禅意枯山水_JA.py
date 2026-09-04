from atelier_canvas import Surface
import numpy as np
import math
from PIL import Image, ImageDraw, ImageFilter

# ---------------------------------------------------------------- canvas
W_L, H_L = 1000, 1920
sf = Surface(W_L, H_L, scale=2, bg=(240, 234, 222))
sf.frame(80, 90, 840, 1790)

P_H, P_W = sf.H, sf.W

# ---------------------------------------------------------------- washi ground
paper = sf.layer()
yy = np.linspace(0.0, 1.0, P_H, dtype=np.float32).reshape(P_H, 1, 1)
top_c = np.array([247, 242, 232], dtype=np.float32).reshape(1, 1, 3)
bot_c = np.array([225, 216, 198], dtype=np.float32).reshape(1, 1, 3)
rgb = top_c * (1.0 - yy) + bot_c * yy
paper[..., :3] = rgb.astype(np.uint8)
paper[..., 3] = 255
sf.composite(paper)

# ---------------------------------------------------------------- raked gravel lines
sand = Image.fromarray(sf.layer())
sd = ImageDraw.Draw(sand)
y_l = 360
row = 0
while y_l < 1520:
    phase = row * 19.0
    fade = 0.32 + 0.36 * abs(math.sin(row * 0.85 + 0.9))
    pts = []
    for x_l in range(-40, 1041, 14):
        wob = math.sin((x_l + phase) / 82.0)
        y_w = y_l + int(wob * 13.0 * fade)
        pts.append((int(x_l * 2), int(y_w * 2)))
    sd.line(pts, fill=(184, 172, 148, 80), width=3)
    row += 1
    y_l += 130

sand = sand.filter(ImageFilter.GaussianBlur(2))
sf.composite(sand)

# ---------------------------------------------------------------- shadows
main_shadow = Image.new("RGBA", (P_W, P_H), (0, 0, 0, 0))
d = ImageDraw.Draw(main_shadow)
d.ellipse([int(310 * 2), int(560 * 2), int(790 * 2), int(1020 * 2)],
          fill=(45, 36, 28, 160))
main_shadow = main_shadow.filter(ImageFilter.GaussianBlur(92))
sf.composite(main_shadow, mode="multiply", opacity=0.85)

small_shadow = Image.new("RGBA", (P_W, P_H), (0, 0, 0, 0))
d = ImageDraw.Draw(small_shadow)
d.ellipse([int(770 * 2), int(900 * 2), int(1000 * 2), int(1100 * 2)],
          fill=(45, 36, 28, 120))
small_shadow = small_shadow.filter(ImageFilter.GaussianBlur(46))
sf.composite(small_shadow, mode="multiply", opacity=0.85)

# ---------------------------------------------------------------- stones
stones = Image.fromarray(sf.layer())
dst = ImageDraw.Draw(stones)


def sp(pts, col):
    dst.polygon([(int(px * 2), int(py * 2)) for px, py in pts], fill=col)


# master stone, weathered
sp([
    (348, 748), (354, 664), (390, 584), (442, 526),
    (514, 486), (600, 482), (676, 512), (716, 570),
    (724, 648), (690, 726), (626, 776), (550, 806),
    (468, 802), (400, 780),
], (50, 42, 34, 255))

# light catching ridge
sp([
    (482, 604), (520, 546), (578, 520), (634, 536),
    (660, 600), (622, 664), (562, 660), (502, 636),
], (108, 95, 78, 255))

# shadowed cleft
sp([
    (354, 756), (368, 684), (408, 614), (452, 676),
    (480, 726), (448, 784), (386, 798),
], (27, 22, 17, 255))

# moss tones
dst.ellipse([int(516 * 2), int(528 * 2), int(598 * 2), int(584 * 2)],
            fill=(104, 104, 81, 180))
dst.ellipse([int(566 * 2), int(706 * 2), int(650 * 2), int(788 * 2)],
            fill=(79, 78, 58, 205))
dst.ellipse([int(408 * 2), int(616 * 2), int(476 * 2), int(670 * 2)],
            fill=(88, 88, 68, 175))

# small distant stone
sp([
    (790, 1010), (808, 944), (852, 906), (902, 912),
    (938, 950), (942, 1012), (884, 1044), (826, 1034),
], (52, 44, 36, 255))
sp([
    (822, 1010), (840, 952), (890, 940), (920, 998),
    (864, 1024),
], (92, 81, 66, 255))

sf.composite(stones)

# ---------------------------------------------------------------- typography
INK = (44, 36, 30)

# split FACT into Japanese original + Chinese translation
jp_raw, zh_seg = FACT.split("（中文：", 1)
zh_raw = "（中文：" + zh_seg

SAFE_BOTTOM = 1880
JP_SIZE = 33
ZH_SIZE = 29
GAP = 36

# Place the Chinese translation first, anchored to the bottom safe edge.
ch_box = sf.text(
    500, SAFE_BOTTOM - 14,
    zh_raw,
    family="cjk-sc",
    size=ZH_SIZE,
    fill=INK,
    anchor="mb",
    role="body",
    max_w=840,
    line_gap=0.48,
)

# Japanese original on top of it.
jp_bottom = ch_box.y - GAP
jp_box = sf.text(
    500, jp_bottom,
    jp_raw,
    family="cjk-jp",
    size=JP_SIZE,
    fill=INK,
    anchor="mb",
    role="body",
    max_w=840,
    line_gap=0.48,
)

# ---------------------------------------------------------------- cinnabar seal meta
META = (135, 49, 32)
sf.serial(
    902, 96,
    SERIAL,
    family="cjk-jp",
    size=21,
    fill=META,
    anchor="rt",
    role="meta",
)
sf.datestamp(
    902, 132,
    DATE,
    family="cjk-jp",
    size=21,
    fill=META,
    anchor="rt",
    role="meta",
)

# ---------------------------------------------------------------- quote — clear of header meta
sf.text(
    500, 210,
    QUOTE,
    family="cjk-jp",
    size=48,
    fill=INK,
    anchor="mt",
    role="quote",
    max_w=840,
    line_gap=0.5,
)

sf.save(OUT_PATH)
