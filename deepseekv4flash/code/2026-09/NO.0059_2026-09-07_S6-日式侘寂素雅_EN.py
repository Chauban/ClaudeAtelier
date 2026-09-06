import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface


def split_translation(s):
    """QUOTE/FACT may carry a bracketed Chinese translation at the end."""
    i = s.find("（")
    if i < 0:
        return s.strip(), ""
    return s[:i].strip(), s[i:].strip()


quote_en, quote_zh = split_translation(QUOTE)
fact_en, fact_zh = split_translation(FACT)

# ---------------------------------------------------------------
# quiet upright canvas — wabi-sabi leaves most of the paper empty
# ---------------------------------------------------------------
LW, LH = 900, 2000
sf = Surface(LW, LH, scale=2, bg=(236, 230, 220))

# warm vertical paper drift
wash = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
wash[..., 0] = (245 - 18 * yy).astype(np.uint8)
wash[..., 1] = (240 - 19 * yy).astype(np.uint8)
wash[..., 2] = (232 - 20 * yy).astype(np.uint8)
wash[..., 3] = 255
sf.composite(wash)

# dim body-glow breathing through the upper void
glow = sf.layer()
yyg = np.linspace(0, sf.H - 1, sf.H)[:, None]
xxg = np.linspace(0, sf.W - 1, sf.W)[None, :]
gcx = 0.52 * sf.W
gcy = 0.38 * sf.H
gr = np.sqrt(((xxg - gcx) / (0.82 * sf.W)) ** 2 +
             ((yyg - gcy) / (0.78 * sf.H)) ** 2)
ga = np.clip(1.0 - gr, 0.0, 1.0) ** 2 * 30
glow[..., 0] = 252
glow[..., 1] = 250
glow[..., 2] = 244
glow[..., 3] = ga.astype(np.uint8)
sf.composite(glow)

# old paper darkens toward its edges
vig = sf.layer()
dvx = np.maximum(xxg, sf.W - 1 - xxg) / (0.5 * sf.W)
dvy = np.maximum(yyg, sf.H - 1 - yyg) / (0.5 * sf.H)
dv = np.clip(np.maximum(dvx, dvy) - 0.74, 0, 0.26) / 0.26
dv = (dv * 24).astype(np.uint8)
vig[..., 0] = 64
vig[..., 1] = 57
vig[..., 2] = 49
vig[..., 3] = dv
sf.composite(vig, mode="multiply", opacity=0.7)

# fine washi tooth
grain = sf.layer()
rng = np.random.default_rng(17)
noise = np.abs(rng.standard_normal((sf.H, sf.W))) * 6
noise = np.clip(noise, 0, 20).astype(np.uint8)
grain[..., 0] = 92
grain[..., 1] = 84
grain[..., 2] = 73
grain[..., 3] = noise
sf.composite(grain, mode="multiply", opacity=0.35)

# a half-finished enso, faintly visible as if at dusk
enso = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
de = ImageDraw.Draw(enso)
ecx, ecy = int(0.50 * LW) * 2, int(244) * 2
er = int(94) * 2
de.arc([ecx - er, ecy - er, ecx + er, ecy + er],
       start=-72, end=286,
       fill=(122, 110, 92, 58), width=2)
enso = enso.filter(ImageFilter.GaussianBlur(0.8))
sf.composite(enso)

# one lone ink fleck, deliberately off-balance
fleck = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
df = ImageDraw.Draw(fleck)
fx, fy = int(LW * 0.612) * 2, int(150) * 2
df.ellipse([fx - 5, fy - 2, fx + 5, fy + 2], fill=(116, 102, 86, 55))
df.ellipse([fx - 2, fy - 5, fx + 2, fy + 3], fill=(108, 95, 79, 34))
fleck = fleck.filter(ImageFilter.GaussianBlur(0.9))
sf.composite(fleck)

# ---------------------------------------------------------------
# typography — drawn only after every surface layer is set down
# ---------------------------------------------------------------
sf.frame(66, 70, 768, LH - 160)

INK = (54, 48, 41)
SUB_INK = (101, 92, 78)
META_INK = (121, 111, 95)

# small registration notes on the right, like marks on a scroll margin
sf.serial(LW - 76, 128, SERIAL,
          family="serif", size=19, fill=META_INK,
          anchor="rt", role="meta")
sf.datestamp(LW - 76, 164, DATE,
             family="serif", size=19, fill=META_INK,
             anchor="rt", role="meta")

X = 158
TW = 596

q_en = sf.text(X, 516, quote_en,
               family="serif", size=33, fill=INK,
               anchor="lt", role="quote",
               max_w=TW, line_gap=0.58)

if quote_zh:
    q_zh = sf.text(X, int(q_en.bottom) + 44, quote_zh,
                   family="cjk-sc", size=29, fill=SUB_INK,
                   anchor="lt", role="body",
                   max_w=TW, line_gap=0.5)
    fact_top = int(q_zh.bottom) + 124
else:
    fact_top = int(q_en.bottom) + 124

f_en = sf.text(X, fact_top, fact_en,
               family="serif", size=30, fill=INK,
               anchor="lt", role="body",
               max_w=TW, line_gap=0.58)

if fact_zh:
    sf.text(X, int(f_en.bottom) + 38, fact_zh,
            family="cjk-sc", size=29, fill=SUB_INK,
            anchor="lt", role="body",
            max_w=TW, line_gap=0.5)

sf.save(OUT_PATH)
