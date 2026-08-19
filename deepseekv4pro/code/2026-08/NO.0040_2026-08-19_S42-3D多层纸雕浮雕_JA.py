from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def _split_text(text, fallback):
    t = text.strip()
    for marker in ("（译：", "(译:"):
        if marker in t:
            src, tr = t.split(marker, 1)
            return src.strip(), tr.rstrip("）) ").strip()
    return t, fallback

quote_src, quote_tr = _split_text(
    QUOTE,
    "大海没有乐谱，所以它每天都不会把同一首曲子弹第二遍。",
)
fact_src, fact_tr = _split_text(
    FACT,
    "位于克罗地亚扎达尔的「海风琴」把35根管子藏在大理石阶梯下，海浪涌来时推动空气发声，由建筑师尼古拉·巴希奇设计，2005年4月15日向公众开放。",
)

INK = (31, 56, 66)
INK_SOFT = (64, 82, 88)
CREAM = (250, 241, 224)
PAPER = (252, 245, 229)
CARD_LINE = (204, 176, 146)
SHADOW = (66, 56, 52, 100)

W = 1000
H = 1720
sf = Surface(W, H, scale=2, bg=(248, 238, 218))
sf.frame(70, 30, 860, 1660)

# base paper-like gradient
lay = sf.layer()
hh, ww = lay.shape[0], lay.shape[1]
yy = np.linspace(0, 1, hh)[:, None]
topc = np.array([251, 243, 229], dtype=np.float32)
botc = np.array([234, 194, 150], dtype=np.float32)
grad = topc[None, None, :] + (botc[None, None, :] - topc[None, None, :]) * yy[..., None]
rng = np.random.default_rng(7)
noise = rng.normal(0, 5, (hh, ww, 1)).astype(np.float32)
grad = np.clip(grad + noise, 0, 255).astype(np.uint8)
lay[..., :3] = grad
lay[..., 3] = 255
sf.composite(lay)

def block_height(lines, family, size, bold, gap):
    if not lines:
        return 0.0
    total = 0.0
    for line in lines:
        total += sf.measure(line, family, size, bold=bold)[1]
    return total + gap * (len(lines) - 1)

# wrap and predict quote height
q_lines = sf.wrap(quote_src, "cjk-jp", 52, max_w=780, bold=True)
qtr_lines = sf.wrap(quote_tr, "cjk-sc", 26, max_w=780)
q_h = block_height(q_lines, "cjk-jp", 52, True, 12)
qtr_h = block_height(qtr_lines, "cjk-sc", 26, False, 8)
quote_y_top = 220
quote_bottom_pred = quote_y_top + q_h + 20 + qtr_h
card_top = max(650, int(round(quote_bottom_pred + 100)))

# wrap fact and translation, predict card bottom with generous padding
f_size = 28
ft_size = 22
f_lines = sf.wrap(fact_src, "cjk-jp", f_size, max_w=720)
ftr_lines = sf.wrap(fact_tr, "cjk-sc", ft_size, max_w=720)
f_gap = 9
ftr_gap = 6
sep = 14
pad_top = 30
pad_bottom = 110
f_h = block_height(f_lines, "cjk-jp", f_size, False, f_gap)
ftr_h = block_height(ftr_lines, "cjk-sc", ft_size, False, ftr_gap)
card_x0 = 110
card_x1 = 890
card_bottom = int(round(card_top + pad_top + f_h + sep + ftr_h + pad_bottom))

Wpx, Hpx = sf.W, sf.H

def wave_pts(yb, amp, periods, phases, xshift=0, yshift=0):
    x = np.arange(Wpx)
    xs = x + xshift * 2
    y = ((yb + yshift) * 2) + (amp * 2) * np.sin(2 * np.pi * xs / (periods[0] * 2) + phases[0])
    if len(periods) > 1:
        y = y + (amp * 2 * 0.55) * np.sin(2 * np.pi * xs / (periods[1] * 2) + phases[1])
    y = np.clip(y, 0, Hpx - 1).astype(np.int32)
    pts = [(int(x[i]), int(y[i])) for i in range(Wpx)]
    pts.append((Wpx - 1, Hpx - 1))
    pts.append((0, Hpx - 1))
    return pts, y

def shadow_wave(base, yb, amp, periods, phases, xshift=5, yshift=-20, blur=22):
    pts, _ = wave_pts(yb, amp, periods, phases, xshift=xshift, yshift=yshift)
    sh = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.polygon(pts, fill=SHADOW)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, sh)

def solid_wave(base, yb, amp, periods, phases, color):
    pts, _ = wave_pts(yb, amp, periods, phases, 0, 0)
    im = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon(pts, fill=color + (255,))
    return Image.alpha_composite(base, im)

art = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))

# sun, mostly behind the fact card
sun_cx = int(930 * 2)
sun_cy = int((card_top - 18) * 2)
sun_r = int(72 * 2)
glow = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
g_r = int(150 * 2)
gd.ellipse([sun_cx - g_r, sun_cy - g_r, sun_cx + g_r, sun_cy + g_r], fill=(235, 130, 82, 80))
glow = glow.filter(ImageFilter.GaussianBlur(120))
art = Image.alpha_composite(art, glow)
sd = ImageDraw.Draw(art)
sd.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=(234, 128, 76, 255))
sd.ellipse([sun_cx - int(50 * 2), sun_cy - int(50 * 2), sun_cx + int(50 * 2), sun_cy + int(50 * 2)], fill=(248, 173, 110, 255))

# back waves, visible above the card as distant sea layers
back_waves = [
    dict(yb=800, amp=30, periods=(640, 300), phases=(0.3, 1.1), color=(236, 188, 154)),
    dict(yb=870, amp=34, periods=(580, 280), phases=(1.2, 0.6), color=(224, 149, 105)),
    dict(yb=938, amp=38, periods=(530, 250), phases=(2.0, 1.5), color=(200, 101, 70)),
]
for i, wd in enumerate(back_waves):
    if i > 0:
        art = shadow_wave(art, wd["yb"], wd["amp"], wd["periods"], wd["phases"])
    art = solid_wave(art, wd["yb"], wd["amp"], wd["periods"], wd["phases"], wd["color"])

# drop shadow behind fact card
card_sh = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
cd = ImageDraw.Draw(card_sh)
cd.rounded_rectangle(
    [card_x0 * 2, card_top * 2 + 10, card_x1 * 2, card_bottom * 2 + 10],
    radius=12, fill=(65, 55, 48, 110),
)
card_sh = card_sh.filter(ImageFilter.GaussianBlur(14))
art = Image.alpha_composite(art, card_sh)

# fact card: flat, opaque, generous margins
card_im = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
cd = ImageDraw.Draw(card_im)
cd.rounded_rectangle(
    [card_x0 * 2, card_top * 2, card_x1 * 2, card_bottom * 2],
    radius=10, fill=PAPER + (255,), outline=CARD_LINE + (255,), width=4,
)
cd.rounded_rectangle(
    [card_x0 * 2 + 8, card_top * 2 + 8, card_x1 * 2 - 8, card_bottom * 2 - 8],
    radius=6, outline=(222, 200, 172, 180), width=2,
)
art = Image.alpha_composite(art, card_im)

# front waves: start safely below card bottom and all text, so no text sits on them
front_waves = [
    dict(yb=card_bottom + 150, amp=40, periods=(540, 240), phases=(0.9, 2.0), color=(62, 112, 123)),
    dict(yb=card_bottom + 205, amp=44, periods=(490, 220), phases=(1.6, 0.5), color=(45, 84, 97)),
    dict(yb=card_bottom + 262, amp=48, periods=(450, 200), phases=(2.4, 1.1), color=(29, 58, 70)),
    dict(yb=card_bottom + 320, amp=52, periods=(410, 190), phases=(0.4, 2.3), color=(19, 39, 50)),
    dict(yb=card_bottom + 378, amp=56, periods=(380, 180), phases=(1.1, 0.8), color=(13, 28, 38)),
    dict(yb=card_bottom + 438, amp=60, periods=(350, 170), phases=(2.0, 0.2), color=(10, 20, 29)),
]
for wd in front_waves:
    art = shadow_wave(art, wd["yb"], wd["amp"], wd["periods"], wd["phases"])
    art = solid_wave(art, wd["yb"], wd["amp"], wd["periods"], wd["phases"], wd["color"])

# small paper tag for serial
tag_x0, tag_y0, tag_x1, tag_y1 = 70, 62, 250, 124
tag_sh = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
td = ImageDraw.Draw(tag_sh)
td.rounded_rectangle(
    [tag_x0 * 2, tag_y0 * 2 + 5, tag_x1 * 2, tag_y1 * 2 + 5],
    radius=6, fill=(70, 60, 52, 90),
)
tag_sh = tag_sh.filter(ImageFilter.GaussianBlur(8))
art = Image.alpha_composite(art, tag_sh)

tag_im = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
td = ImageDraw.Draw(tag_im)
td.rounded_rectangle(
    [tag_x0 * 2, tag_y0 * 2, tag_x1 * 2, tag_y1 * 2],
    radius=6, fill=(252, 244, 228, 255), outline=(200, 172, 140, 255), width=3,
)
art = Image.alpha_composite(art, tag_im)

sf.composite(art)

# quote
q_y = quote_y_top
for line in q_lines:
    b = sf.text(500, q_y, line, family="cjk-jp", size=52, fill=INK,
                anchor="mt", role="quote", bold=True, max_w=780)
    q_y = b.bottom + 12
q_y += 8
for line in qtr_lines:
    b = sf.text(500, q_y, line, family="cjk-sc", size=26, fill=INK_SOFT,
                anchor="mt", role="meta", max_w=780)
    q_y = b.bottom + 8

# fact block on card
fact_y = card_top + pad_top
for line in f_lines:
    b = sf.text(500, fact_y, line, family="cjk-jp", size=f_size, fill=INK,
                anchor="mt", role="body", max_w=720)
    fact_y = b.bottom + f_gap
fact_y += (sep - f_gap)
for line in ftr_lines:
    b = sf.text(500, fact_y, line, family="cjk-sc", size=ft_size, fill=INK_SOFT,
                anchor="mt", role="meta", max_w=720)
    fact_y = b.bottom + ftr_gap

# required identifiers
sf.serial(80, 76, SERIAL, family="sans", size=20, fill=INK, anchor="lt", role="meta")
sf.datestamp(880, H - 56, DATE, family="sans", size=20, fill=CREAM, anchor="rt", role="meta")

sf.save(OUT_PATH)
