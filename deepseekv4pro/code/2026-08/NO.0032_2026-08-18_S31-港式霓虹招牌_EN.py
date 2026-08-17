import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

# ---------- helpers ----------

def lighten(c, f=0.6):
    return tuple(min(255, int(ch + (255 - ch) * f)) for ch in c)


def draw_blur(draw_op, blur, mode="screen", opacity=1.0):
    img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_op(d)
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    sf.composite(np.array(img), mode=mode, opacity=opacity)


def neon_line(x0, y0, x1, y1, color, width=5, glow_blur=26, alpha=175):
    p0 = (int(x0 * 2), int(y0 * 2))
    p1 = (int(x1 * 2), int(y1 * 2))
    draw_blur(lambda d: d.line([p0, p1], fill=color + (alpha,),
                               width=int(width * 2 * 4)), glow_blur)
    draw_blur(lambda d: d.line([p0, p1], fill=lighten(color, 0.7),
                               width=int(width * 2)), 5)


def neon_rounded_rect(cx, cy, w, h, color, radius=28, tube_w=6,
                      glow_blur=38, alpha=175, fill_alpha=40, fill_blur=70):
    x0 = (cx - w / 2) * 2
    y0 = (cy - h / 2) * 2
    x1 = (cx + w / 2) * 2
    y1 = (cy + h / 2) * 2
    if fill_alpha:
        img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x0, y0, x1, y1], radius=radius * 2,
                            fill=color + (fill_alpha,))
        img = img.filter(ImageFilter.GaussianBlur(fill_blur))
        sf.composite(np.array(img), mode="screen", opacity=1.0)
    draw_blur(lambda d: d.rounded_rectangle([x0, y0, x1, y1], radius=radius * 2,
                                            outline=color + (alpha,),
                                            width=int(tube_w * 2 * 4)), glow_blur)
    draw_blur(lambda d: d.rounded_rectangle([x0, y0, x1, y1], radius=radius * 2,
                                            outline=lighten(color, 0.7),
                                            width=int(tube_w * 2)), 5)


def neon_ellipse(cx, cy, rx, ry, color, tube_w=4, glow_blur=34, alpha=150):
    bbox = [(cx - rx) * 2, (cy - ry) * 2, (cx + rx) * 2, (cy + ry) * 2]
    draw_blur(lambda d: d.ellipse(bbox, outline=color + (alpha,),
                                  width=int(tube_w * 2 * 3)), glow_blur)
    draw_blur(lambda d: d.ellipse(bbox, outline=lighten(color, 0.7),
                                  width=int(tube_w * 2)), 5)


def neon_dot(cx, cy, r, color, glow_blur=22, alpha=190):
    bbox = [(cx - r) * 2, (cy - r) * 2, (cx + r) * 2, (cy + r) * 2]
    draw_blur(lambda d: d.ellipse(bbox, fill=color + (alpha,)), glow_blur)
    draw_blur(lambda d: d.ellipse(bbox, fill=lighten(color, 0.7)), 4)


# ---------- canvas ----------
sf = Surface(1000, 1350, scale=2, bg=(8, 10, 22))

# background: deep night gradient + grain + slight vignette
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
top = np.array([10, 13, 26], dtype=np.float32)
bottom = np.array([17, 22, 38], dtype=np.float32)
rng = np.random.default_rng(7)
noise = rng.normal(0, 4, (sf.H, sf.W))
for i, ch in enumerate([0, 1, 2]):
    ramp = top[i] + (bottom[i] - top[i]) * yy
    lay[..., ch] = np.clip(ramp + noise, 0, 255).astype(np.uint8)
vig = 1 - 0.14 * np.sqrt((xx - 0.5) ** 2 * 0.7 + (yy - 0.5) ** 2 * 1.1)
lay[..., :3] = (lay[..., :3] * np.clip(vig, 0.82, 1.0)[..., None]).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# ---------- text metrics ----------
QUOTE_SIZE = 46
FACT_EN_SIZE = 29
FACT_ZH_SIZE = 24
META_SIZE = 24

quote_max_w = 700
fact_max_w = 740

quote_lines = sf.wrap(QUOTE, "sans", QUOTE_SIZE, max_w=quote_max_w, bold=True)
quote_w = max(sf.measure(l, "sans", QUOTE_SIZE, bold=True)[0] for l in quote_lines)
quote_h = QUOTE_SIZE * 1.35 * len(quote_lines)

if "（" in FACT:
    fact_en = FACT[:FACT.index("（")]
    fact_zh = FACT[FACT.index("（"):]
else:
    fact_en = FACT
    fact_zh = ""

fact_en_lines = sf.wrap(fact_en, "sans", FACT_EN_SIZE, max_w=fact_max_w, bold=False)
fact_en_w = max(sf.measure(l, "sans", FACT_EN_SIZE, bold=False)[0] for l in fact_en_lines)
fact_en_h = FACT_EN_SIZE * 1.35 * len(fact_en_lines)

fact_zh_lines = sf.wrap(fact_zh, "cjk-sc", FACT_ZH_SIZE, max_w=fact_max_w, bold=False)
fact_zh_w = max(sf.measure(l, "cjk-sc", FACT_ZH_SIZE, bold=False)[0] for l in fact_zh_lines)
fact_zh_h = FACT_ZH_SIZE * 1.35 * len(fact_zh_lines)

QUOTE_TOP = 250
quote_bottom = QUOTE_TOP + quote_h

FACT_EN_TOP = quote_bottom + 135
fact_en_bottom = FACT_EN_TOP + fact_en_h

FACT_ZH_TOP = fact_en_bottom + 44
fact_zh_bottom = FACT_ZH_TOP + fact_zh_h

META_Y = 1190

# safe area covering all text
sf.frame(70, 130, 860, 1090)

# ---------- decor: Hong Kong neon signage ----------
PINK = (255, 82, 178)
CYAN = (0, 205, 240)
AMBER = (255, 190, 60)
GREEN = (112, 255, 150)
RUBY = (255, 88, 104)

# side vertical neon tubes + top rail
neon_line(54, 130, 54, 1200, PINK, width=5, glow_blur=24, alpha=165)
neon_line(946, 130, 946, 1200, CYAN, width=5, glow_blur=24, alpha=165)
neon_line(54, 130, 946, 130, GREEN, width=5, glow_blur=24, alpha=165)

# large crossed sign rings behind quote
neon_ellipse(435, 400, 265, 225, PINK, tube_w=4, glow_blur=48, alpha=85)
neon_ellipse(565, 400, 265, 225, CYAN, tube_w=4, glow_blur=48, alpha=85)

# quote sign box
quote_cx = 500
quote_cy = QUOTE_TOP + quote_h / 2
qfw = quote_w + 130
qfh = quote_h + 105
neon_rounded_rect(quote_cx, quote_cy, qfw, qfh, PINK, radius=30, tube_w=6,
                  glow_blur=36, alpha=180, fill_alpha=38)

# fact sign box (covers English + Chinese)
fp_top = FACT_EN_TOP - 42
fp_bottom = fact_zh_bottom + 42
fp_cx = 500
fp_cy = (fp_top + fp_bottom) / 2
fp_w = 815
fp_h = fp_bottom - fp_top
neon_rounded_rect(fp_cx, fp_cy, fp_w, fp_h, CYAN, radius=26, tube_w=5,
                  glow_blur=32, alpha=160, fill_alpha=30)

# symbolic two-lobed liver in the middle gap
neon_ellipse(450, 1085, 145, 85, RUBY, tube_w=3, glow_blur=30, alpha=130)
neon_ellipse(550, 1085, 145, 85, RUBY, tube_w=3, glow_blur=30, alpha=130)
neon_dot(500, 1085, 7, AMBER, glow_blur=20, alpha=190)

# small corner dots on the quote sign
neon_dot(quote_cx - qfw / 2 - 10, quote_cy - qfh / 2 - 10, 6, PINK, glow_blur=18, alpha=200)
neon_dot(quote_cx + qfw / 2 + 10, quote_cy - qfh / 2 - 10, 6, PINK, glow_blur=18, alpha=200)
neon_dot(quote_cx - qfw / 2 - 10, quote_cy + qfh / 2 + 10, 6, CYAN, glow_blur=18, alpha=200)
neon_dot(quote_cx + qfw / 2 + 10, quote_cy + qfh / 2 + 10, 6, AMBER, glow_blur=18, alpha=200)

# clean dark plate behind serial + date so no decoration crosses the meta text
plate = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
pd = ImageDraw.Draw(plate)
pd.rounded_rectangle([100 * 2, 1170 * 2, 900 * 2, 1235 * 2],
                     radius=22, fill=(8, 10, 25, 235))
sf.composite(np.array(plate), mode="normal", opacity=1.0)

# ---------- text ----------
quote_text = "\n".join(quote_lines)
quote_x = 500 - quote_w / 2
sf.text(quote_x, QUOTE_TOP, quote_text,
        family="sans", size=QUOTE_SIZE, fill=(255, 222, 244),
        anchor="lt", role="quote", bold=True,
        max_w=quote_max_w, line_gap=0.35, allow_overlap=False)

fact_en_text = "\n".join(fact_en_lines)
sf.text(130, FACT_EN_TOP, fact_en_text,
        family="sans", size=FACT_EN_SIZE, fill=(220, 248, 255),
        anchor="lt", role="body", bold=False,
        max_w=fact_max_w, line_gap=0.35, allow_overlap=False)

fact_zh_text = "\n".join(fact_zh_lines)
sf.text(130, FACT_ZH_TOP, fact_zh_text,
        family="cjk-sc", size=FACT_ZH_SIZE, fill=(255, 226, 160),
        anchor="lt", role="meta", bold=False,
        max_w=fact_max_w, line_gap=0.35, allow_overlap=False)

sf.serial(120, META_Y, SERIAL,
          family="mono", size=META_SIZE, fill=(170, 255, 192),
          anchor="lt", role="meta", bold=True)

sf.datestamp(880, META_Y, DATE,
             family="mono", size=META_SIZE, fill=(255, 208, 122),
             anchor="rt", role="meta", bold=True)

sf.save(OUT_PATH)
