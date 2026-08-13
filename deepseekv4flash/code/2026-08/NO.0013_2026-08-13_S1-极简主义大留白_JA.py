from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1500
sf = Surface(W, H, scale=2, bg=(248, 247, 243))

# ---- background: warm near-white, barely fading downward ----
bg = sf.layer()
t = np.linspace(0, 1, sf.H)[:, None]
bg[..., 0] = (249 - 4 * t).astype(np.uint8)
bg[..., 1] = (248 - 4 * t).astype(np.uint8)
bg[..., 2] = (244 - 4 * t).astype(np.uint8)
bg[..., 3] = 255
sf.composite(bg)

# ---- tiny fondue pot, the single splash of colour ----
cx, pt = 500, 260

sh = sf.layer()
sh_img = Image.fromarray(sh)
ds = ImageDraw.Draw(sh_img)
ds.ellipse([(cx - 64) * 2, (pt + 156) * 2, (cx + 64) * 2, (pt + 190) * 2], fill=(0, 0, 0, 55))
sf.composite(sh_img.filter(ImageFilter.GaussianBlur(26)))

art = sf.layer()
art_img = Image.fromarray(art)
d = ImageDraw.Draw(art_img)

d.rounded_rectangle([(cx - 42) * 2, (pt + 146) * 2, (cx + 42) * 2, (pt + 154) * 2],
                    radius=8, fill=(128, 125, 119, 255))
d.ellipse([(cx - 26) * 2, (pt + 108) * 2, (cx + 26) * 2, (pt + 130) * 2], fill=(139, 136, 129, 255))
d.ellipse([(cx - 9) * 2, (pt + 122) * 2, (cx + 9) * 2, (pt + 142) * 2], fill=(255, 144, 46, 255))
d.ellipse([(cx - 4) * 2, (pt + 128) * 2, (cx + 4) * 2, (pt + 138) * 2], fill=(255, 214, 79, 255))
d.rounded_rectangle([(cx - 88) * 2, (pt + 18) * 2, (cx + 88) * 2, (pt + 110) * 2],
                    radius=48, fill=(191, 50, 37, 255))
d.rounded_rectangle([(cx - 118) * 2, (pt + 38) * 2, (cx - 100) * 2, (pt + 74) * 2],
                    radius=18, fill=(166, 39, 29, 255))
d.rounded_rectangle([(cx + 100) * 2, (pt + 38) * 2, (cx + 118) * 2, (pt + 74) * 2],
                    radius=18, fill=(166, 39, 29, 255))
d.ellipse([(cx - 105) * 2, pt * 2, (cx + 105) * 2, (pt + 30) * 2], fill=(166, 39, 29, 255))
d.ellipse([(cx - 93) * 2, (pt + 10) * 2, (cx + 93) * 2, (pt + 28) * 2], fill=(226, 195, 133, 255))
d.rounded_rectangle([(cx - 60) * 2, (pt + 20) * 2, (cx - 52) * 2, (pt + 62) * 2],
                    radius=8, fill=(226, 195, 133, 255))
d.ellipse([(cx - 64) * 2, (pt + 56) * 2, (cx - 48) * 2, (pt + 70) * 2], fill=(226, 195, 133, 255))
sf.composite(art_img)

# ---- a few snow specks in the empty margins ----
rng = np.random.default_rng(13)
sx = np.concatenate([rng.uniform(180, 820, 10), rng.uniform(180, 820, 8)])
sy = np.concatenate([rng.uniform(120, 220, 10), rng.uniform(1200, 1320, 8)])
sr = np.concatenate([rng.uniform(0.8, 1.8, 10), rng.uniform(0.8, 1.8, 8)])
snow = sf.layer()
snow_img = Image.fromarray(snow)
d = ImageDraw.Draw(snow_img)
for x, y, r in zip(sx, sy, sr):
    d.ellipse([int((x - r) * 2), int((y - r) * 2), int((x + r) * 2), int((y + r) * 2)],
              fill=(224, 228, 233, 255))
sf.composite(snow_img, opacity=0.9)

# ---- text ----
sf.frame(150, 90, 700, 1340)

# strip the Chinese translation from QUOTE
q_text = QUOTE
idx = q_text.find("（国民")
if idx != -1:
    q_text = q_text[:idx].strip()

# quote: two balanced lines, high on the sheet
q1 = sf.text(500, 480, "国民食は、生まれたときから", family="cjk-jp", size=46,
             fill=(40, 39, 37), anchor="mt", role="quote")
q2 = sf.text(500, q1.bottom + 6, "国民食ではない。", family="cjk-jp", size=46,
             fill=(40, 39, 37), anchor="mt", role="quote")

sf.text(500, q2.bottom + 34, "国民料理，并非生来就是国民料理。",
        family="cjk-sc", size=22, fill=(110, 108, 102), anchor="mt", role="meta")

# strip the Chinese translation from FACT
f_text = FACT
idx = f_text.find("（瑞士")
if idx != -1:
    f_text = f_text[:idx].strip()

# FACT contains traditional characters (語・連・郷・圏) → use cjk-tc
fbox = sf.text(500, 744, f_text, family="cjk-tc", size=30, fill=(58, 56, 52),
               anchor="mt", role="body", max_w=680)

ft_zh = "瑞士的国民料理奶酪火锅，其实是1930年代瑞士奶酪联盟为消化过剩奶酪而宣传推出的「国民料理」；此前它只是法语圈部分地区的地方菜。"
sf.text(500, fbox.bottom + 30, ft_zh, family="cjk-sc", size=22, fill=(110, 108, 102),
        anchor="mt", role="meta", max_w=680)

sf.serial(160, 1400, SERIAL, family="mono", size=18, fill=(110, 108, 102), anchor="lt", role="meta")
sf.datestamp(840, 1400, DATE, family="mono", size=18, fill=(110, 108, 102), anchor="rt", role="meta")

sf.save(OUT_PATH)
