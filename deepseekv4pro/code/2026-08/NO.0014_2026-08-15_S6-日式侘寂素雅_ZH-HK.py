import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

w = 1000
h = 1450

sf = Surface(w, h, scale=2, bg=(242, 238, 228))

# ---------- background: rice paper with soft gradient and vignette ----------
lay = sf.layer()
H, W = sf.H, sf.W
yy = np.linspace(0, 1, H)[:, None]
xx = np.linspace(0, 1, W)[None, :]

vert = 1.0 - 0.055 * yy
dx = (xx - 0.5) * 1.15
dy = (yy - 0.48) * 1.6
dist = np.sqrt(dx ** 2 + dy ** 2)
vig = 1.0 - 0.12 * np.clip((dist - 0.35) / 0.75, 0, 1) ** 2
mult = vert * vig

base = np.array([242, 238, 228], dtype=np.float64)
rgb = np.clip(base[None, None, :] * mult[..., None], 0, 255).astype(np.uint8)
lay[..., :3] = rgb
lay[..., 3] = 255
sf.composite(lay)

# speckle: washi paper fibres
lay2 = sf.layer()
rng = np.random.RandomState(14)
mask = rng.rand(H, W) > 0.9994
lay2[mask, :3] = (174, 159, 138)
lay2[mask, 3] = 255
mask2 = rng.rand(H, W) > 0.99985
lay2[mask2, :3] = (150, 135, 115)
lay2[mask2, 3] = 200
sf.composite(lay2, mode="normal", opacity=0.35)

# ---------- soft ink wash behind the interrobang ----------
wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(wash)
d.ellipse([(450 - 260) * 2, (440 - 230) * 2, (450 + 260) * 2, (440 + 230) * 2],
          fill=(196, 172, 148, 60))
d.ellipse([(450 - 140) * 2, (440 - 130) * 2, (450 + 140) * 2, (440 + 130) * 2],
          fill=(208, 186, 160, 42))
wash = wash.filter(ImageFilter.GaussianBlur(70))
sf.composite(wash, mode="normal", opacity=0.66)

# ---------- enso arc (wabi-sabi imperfect circle) ----------
gx, gy = 450, 430
glyph_size = 360
gw, gh = sf.measure("\u203d", "serif", glyph_size)
enso_r = int(max(gw, gh) / 2) + 30

enso = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(enso)
ex, ey = gx * 2, gy * 2
er = enso_r * 2
d.arc([ex - er, ey - er, ex + er, ey + er], start=205, end=332,
      fill=(158, 138, 118, 120), width=7)
d.arc([ex - er, ey - er, ex + er, ey + er], start=25, end=52,
      fill=(158, 138, 118, 80), width=7)
enso = enso.filter(ImageFilter.GaussianBlur(1.0))
sf.composite(enso, mode="normal", opacity=0.7)

# ---------- abstract vermillion seal ----------
seal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(seal)
sx, sy, ss = 858, 484, 32
box = [sx * 2, sy * 2, (sx + ss) * 2, (sy + ss) * 2]
d.rounded_rectangle(box, radius=7 * 2, outline=(168, 76, 62, 220), width=8)
d.ellipse([(sx + ss / 2 - 4) * 2, (sy + ss / 2 - 4) * 2,
           (sx + ss / 2 + 4) * 2, (sy + ss / 2 + 4) * 2],
          fill=(168, 76, 62, 200))
seal = seal.filter(ImageFilter.GaussianBlur(0.6))
sf.composite(seal, mode="normal", opacity=0.9)

# ---------- text safe area ----------
sf.frame(80, 70, w - 160, h - 150)

# the interrobang as the main sumi figure
sf.text(gx, gy, "\u203d", family="serif", size=glyph_size,
        fill=(47, 44, 41), anchor="mm", role="title")

# ---------- quote ----------
quote_size = 44
quote_maxw = 600
quote_y = 720

quote_box = sf.text(500, quote_y, QUOTE, family="serif-cjk", size=quote_size,
                    fill=(60, 56, 52), anchor="mt", role="quote",
                    max_w=quote_maxw, line_gap=0.42)

divider_y = quote_box.bottom + 38
fact_y = divider_y + 52

# ---------- thin lines ----------
lines_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(lines_layer)
d.line([(500 - 60) * 2, int(divider_y * 2), (500 + 60) * 2, int(divider_y * 2)],
       fill=(170, 155, 135, 190), width=6)
d.line([80 * 2, int(1310 * 2), 920 * 2, int(1310 * 2)],
       fill=(190, 178, 160, 130), width=2)
sf.composite(lines_layer, mode="normal", opacity=0.85)

# ---------- fact, rendered with mixed fonts ----------
fact_size = 28
line_height = int(fact_size * 1.55)
MAX_LINE_W = 825
TOKEN_GAP = 8.0

fact_lines = [
    [("「", "cjk-hk"), ("\u203d", "serif"), ("」", "cjk-hk")],
    [("（interrobang）是把問號與感嘆號疊合而成", "cjk-hk")],
    [("的一個標點符號，1962 年由美國廣告人", "cjk-hk")],
    [("Martin K. Speckter", "serif"), ("提出；", "cjk-hk")],
    [("名字由拉丁文 ", "cjk-hk"), ("interrogatio", "serif"),
     ("（修辭式提問）", "cjk-hk")],
    [("與印刷界行話 ", "cjk-hk"), ("bang", "serif"),
     ("（感嘆號）拼合而成。", "cjk-hk")],
    [("1968 年，部分", "cjk-hk"), ("Remington", "serif"),
     ("打字機甚至配備過", "cjk-hk")],
    [("一顆", "cjk-hk"), ("interrobang", "serif"), ("鍵。", "cjk-hk")],
]


def draw_centered_line(sfc, top_y, tokens, size, fill, gap=TOKEN_GAP):
    widths = [sfc.measure(t, f, size)[0] for t, f in tokens]
    total = sum(widths) + gap * (len(tokens) - 1)
    if total > MAX_LINE_W:
        raise ValueError("fact line width is %.1f, too wide" % total)
    x = 500 - total / 2.0
    for (t, f) in tokens:
        b = sfc.text(x, top_y, t, family=f, size=size, fill=fill,
                     anchor="lt", role="body")
        x = b.right + gap


for i, tokens in enumerate(fact_lines):
    top_y = fact_y + i * line_height
    draw_centered_line(sf, top_y, tokens, fact_size, (98, 92, 84))

# ---------- serial and date ----------
sf.serial(80, 1330, SERIAL, family="serif", size=18, fill=(112, 105, 96),
          anchor="lt", role="meta")
sf.datestamp(920, 1330, DATE, family="serif", size=18, fill=(112, 105, 96),
             anchor="rt", role="meta")

sf.save(OUT_PATH)
