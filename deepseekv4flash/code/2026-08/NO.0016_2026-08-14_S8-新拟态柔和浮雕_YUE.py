from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1620
S = 2
sf = Surface(W, H, scale=S, bg=(234, 238, 243))
sf.frame(60, 60, W - 120, H - 120)

# 背景垂直漸變
g = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
g[..., 0] = (236 + 8 * yy).astype(np.uint8)
g[..., 1] = (239 + 6 * yy).astype(np.uint8)
g[..., 2] = (244 + 3 * yy).astype(np.uint8)
g[..., 3] = 255
sf.composite(g)

DARK = (193, 204, 220)
LIGHT = (255, 255, 255)
BASE_OUT = (237, 241, 247)
BASE_IN = (223, 230, 239)
INK = (52, 61, 78)
SUB = (150, 162, 180)


def _img():
    return Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))


def put(img, blur=0):
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    sf.composite(np.array(img))


def card(x, y, w, h, r, base, inset=False, off=9, blur=26):
    img = _img()
    d = ImageDraw.Draw(img)
    if inset:
        d.rounded_rectangle([(x - off) * S, (y - off) * S, (x + w - off) * S, (y + h - off) * S], r * S, fill=DARK + (255,))
    else:
        d.rounded_rectangle([(x + off) * S, (y + off) * S, (x + w + off) * S, (y + h + off) * S], r * S, fill=DARK + (255,))
    put(img, blur)
    img = _img()
    d = ImageDraw.Draw(img)
    if inset:
        d.rounded_rectangle([(x + off) * S, (y + off) * S, (x + w + off) * S, (y + h + off) * S], r * S, fill=LIGHT + (255,))
    else:
        d.rounded_rectangle([(x - off) * S, (y - off) * S, (x + w - off) * S, (y + h - off) * S], r * S, fill=LIGHT + (255,))
    put(img, blur)
    img = _img()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], r * S, fill=base + (255,))
    put(img)


def circle(cx, cy, r, base, inset=False, off=3, blur=7):
    img = _img()
    d = ImageDraw.Draw(img)
    if inset:
        d.ellipse([(cx - r - off) * S, (cy - r - off) * S, (cx + r - off) * S, (cy + r - off) * S], fill=DARK + (255,))
    else:
        d.ellipse([(cx - r + off) * S, (cy - r + off) * S, (cx + r + off) * S, (cy + r + off) * S], fill=DARK + (255,))
    put(img, blur)
    img = _img()
    d = ImageDraw.Draw(img)
    if inset:
        d.ellipse([(cx - r + off) * S, (cy - r + off) * S, (cx + r + off) * S, (cy + r + off) * S], fill=LIGHT + (255,))
    else:
        d.ellipse([(cx - r - off) * S, (cy - r - off) * S, (cx + r - off) * S, (cy + r - off) * S], fill=LIGHT + (255,))
    put(img, blur)
    img = _img()
    d = ImageDraw.Draw(img)
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=base + (255,))
    put(img)


def dot(cx, cy, r, color):
    img = _img()
    d = ImageDraw.Draw(img)
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=color + (255,))
    put(img)


# ---- Tier 2：卡片與裝飾 ----
# 頂部兩個藥丸（外凸）
card(70, 90, 250, 66, 33, BASE_OUT, off=7, blur=20)
card(690, 90, 240, 66, 33, BASE_OUT, off=7, blur=20)

# 金句卡（外凸）
card(70, 230, 860, 400, 54, BASE_OUT, off=10, blur=30)

# 冷知識卡（內凹）
card(70, 720, 860, 720, 54, BASE_IN, inset=True, off=10, blur=30)

# 金句卡內：內凹大圓 + 花粉微粒
circle(500, 310, 26, BASE_IN, inset=True, off=4, blur=9)
dot(480, 304, 5, SUB)
dot(514, 298, 5, SUB)
dot(506, 322, 5, SUB)

# 兩卡之間的雲朵（三個外凸小圓）
circle(500, 660, 15, BASE_OUT, off=3, blur=8)
circle(462, 669, 15, BASE_OUT, off=3, blur=8)
circle(538, 669, 15, BASE_OUT, off=3, blur=8)

# FACT卡內部：分隔槽 + 三個內凹小圓
card(140, 1330, 720, 12, 6, BASE_IN, inset=True, off=3, blur=7)
circle(472, 1395, 10, BASE_IN, inset=True, off=3, blur=7)
circle(500, 1395, 10, BASE_IN, inset=True, off=3, blur=7)
circle(528, 1395, 10, BASE_IN, inset=True, off=3, blur=7)

# 底部裝飾：外凸藥丸 + 圓點
card(330, 1500, 340, 60, 30, BASE_OUT, off=7, blur=18)
circle(480, 1570, 8, BASE_OUT, off=3, blur=6)
circle(500, 1570, 8, BASE_OUT, off=3, blur=6)
circle(520, 1570, 8, BASE_OUT, off=3, blur=6)

# ---- Tier 1：文字 ----
sf.serial(144, 110, SERIAL, family="sans", size=25, fill=INK, anchor="lt", role="meta")
sf.datestamp(738, 110, DATE, family="sans", size=25, fill=INK, anchor="lt", role="meta")

# 金句
sf.text(500, 360, QUOTE,
        family="cjk-hk", size=46, fill=INK,
        anchor="mt", role="quote", bold=True,
        max_w=680, line_gap=0.45)

# 冷知識
sf.text(110, 810, FACT,
        family="cjk-hk", size=36, fill=INK,
        anchor="lt", role="body",
        max_w=740, line_gap=0.42)

sf.save(OUT_PATH)
