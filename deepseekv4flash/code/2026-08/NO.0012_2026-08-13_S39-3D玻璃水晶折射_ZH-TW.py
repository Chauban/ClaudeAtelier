from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 1000, 1600
sf = Surface(W, H, scale=2, bg=(8, 12, 24))
sf.frame(90, 90, W - 180, H - 180)

# ---------- 背景：深夜曠野 ----------
bg = sf.layer()
yy = np.linspace(0, sf.H - 1, sf.H)[:, None]
xx = np.linspace(0, sf.W - 1, sf.W)[None, :]
dx = (xx - sf.W * 0.5) / (sf.W * 0.72)
dy = (yy - sf.H * 0.26) / (sf.H * 0.58)
d2 = dx * dx + dy * dy
t = np.clip(1.0 - d2, 0, 1) ** 1.4
base = np.array([8, 11, 22], dtype=np.float32)
glow_c = np.array([68, 56, 90], dtype=np.float32)
for c in range(3):
    bg[..., c] = (base[c] + (glow_c[c] - base[c]) * t).astype(np.uint8)
bg[..., 3] = 255
sf.composite(bg)

# 遠山
hill = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
hd = ImageDraw.Draw(hill)
hd.ellipse([1000 - 1500, 760 - 260, 1000 + 300, 760 + 550], fill=(22, 28, 52, 235))
hd.ellipse([1000 - 300, 760 - 240, 1000 + 1500, 760 + 550], fill=(17, 23, 44, 235))
hill = hill.filter(ImageFilter.GaussianBlur(60))
sf.composite(hill)

# 地平線盡頭的光
sun = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sun)
sd.ellipse([1000 - 110, 760 - 110, 1000 + 110, 760 + 110], fill=(255, 195, 140, 140))
sun = sun.filter(ImageFilter.GaussianBlur(70))
sf.composite(sun, mode="screen", opacity=0.9)

# 黃土路
road = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
rd = ImageDraw.Draw(road)
rd.polygon([(1000 - 620, sf.H + 80), (1000 + 620, sf.H + 80), (1000 + 36, 770), (1000 - 36, 770)], fill=(122, 80, 48, 210))
road = road.filter(ImageFilter.GaussianBlur(5))
sf.composite(road)

# 孤獨跑者的光點
run = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
rnd = ImageDraw.Draw(run)
rnd.ellipse([1000 - 6, 760 - 24, 1000 + 6, 760 - 10], fill=(255, 236, 200, 220))
run = run.filter(ImageFilter.GaussianBlur(14))
sf.composite(run, mode="screen", opacity=0.95)
rk = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
rkd = ImageDraw.Draw(rk)
rkd.ellipse([1000 - 2, 760 - 16, 1000 + 2, 760 - 10], fill=(255, 255, 235, 255))
rk = rk.filter(ImageFilter.GaussianBlur(4))
sf.composite(rk, mode="screen")

# 夜空塵點
dust = sf.layer()
rng = np.random.default_rng(7)
msk = rng.random((sf.H, sf.W)) < 0.003
dust[..., 0] = 205
dust[..., 1] = 218
dust[..., 2] = 255
dust[..., 3] = np.where(msk, 70, 0).astype(np.uint8)
sf.composite(dust, mode="screen")

# ---------- 厚玻璃板 ----------
# 玻璃投影
proj = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
pd = ImageDraw.Draw(proj)
pd.rounded_rectangle([140 + 44, 140 + 70, 1860 + 44, 3060 + 70], radius=88, fill=(0, 0, 0, 170))
proj = proj.filter(ImageFilter.GaussianBlur(46))
sf.composite(proj)

# 厚度層
thick = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
td = ImageDraw.Draw(thick)
td.rounded_rectangle([140 + 26, 140 + 26, 1860 + 26, 3060 + 26], radius=88, fill=(46, 64, 94, 235))
sf.composite(thick)

# 主玻璃面板
glass = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glass)
gd.rounded_rectangle([140, 140, 1860, 3060], radius=88, fill=(18, 30, 50, 230), outline=(215, 235, 255, 110), width=6)
glass = glass.filter(ImageFilter.GaussianBlur(2))
sf.composite(glass)

# 玻璃形狀 mask
mask = Image.new("L", (sf.W, sf.H), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle([140, 140, 1860, 3060], radius=88, fill=255)

# 折射錯位的路（玻璃內側，位置偏移）
refr = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
rdd = ImageDraw.Draw(refr)
rdd.polygon([(1000 - 620 + 48, sf.H + 40), (1000 + 620 + 48, sf.H + 40), (1000 + 36 + 48, 770 + 28), (1000 - 36 + 48, 770 + 28)], fill=(150, 122, 195, 64))
refr = refr.filter(ImageFilter.GaussianBlur(8))
r, g, b, a = refr.split()
a = ImageChops.multiply(a, mask)
refr = Image.merge("RGBA", (r, g, b, a))
sf.composite(refr, mode="screen", opacity=0.85)

# 內陰影
insh = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
isd = ImageDraw.Draw(insh)
isd.rounded_rectangle([140, 140, 1860, 3060], radius=88, outline=(0, 0, 0, 190), width=96)
insh = insh.filter(ImageFilter.GaussianBlur(40))
r, g, b, a = insh.split()
a = ImageChops.multiply(a, mask)
insh = Image.merge("RGBA", (r, g, b, a))
sf.composite(insh, mode="multiply", opacity=0.85)

# 玻璃高光
highlight = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
hld = ImageDraw.Draw(highlight)
hld.rounded_rectangle([140 + 46, 140 + 46, 1860 - 46, 140 + 330], radius=80, fill=(255, 255, 255, 42))
hld.rounded_rectangle([140 + 46, 140 + 46, 140 + 270, 3060 - 46], radius=80, fill=(255, 255, 255, 32))
highlight = highlight.filter(ImageFilter.GaussianBlur(46))
sf.composite(highlight, mode="screen", opacity=0.9)

# 邊緣色散虹光
chroma = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
cd = ImageDraw.Draw(chroma)
cd.rounded_rectangle([140 + 10, 140 + 10, 1860 - 10, 3060 - 10], radius=88, outline=(100, 225, 255, 80), width=12)
cd.rounded_rectangle([140 - 10, 140 - 10, 1860 + 10, 3060 + 10], radius=88, outline=(255, 100, 130, 80), width=12)
cd.rounded_rectangle([140 + 32, 140 + 32, 1860 - 32, 3060 - 32], radius=88, outline=(255, 225, 140, 44), width=8)
chroma = chroma.filter(ImageFilter.GaussianBlur(16))
sf.composite(chroma, mode="screen", opacity=0.75)

# 玻璃表面反射光斑
speck = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
sp = ImageDraw.Draw(speck)
sp.ellipse([1000 - 180, 2000 - 90, 1000 - 120, 2000 - 30], fill=(255, 255, 255, 22))
sp.ellipse([1000 + 140, 2200 - 70, 1000 + 200, 2200 - 10], fill=(255, 255, 255, 16))
speck = speck.filter(ImageFilter.GaussianBlur(34))
sf.composite(speck, mode="screen")

# 底部稜鏡色帶
prism = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
prd = ImageDraw.Draw(prism)
prd.polygon([(500, 2700), (540, 2700), (660, 2300), (620, 2300)], fill=(255, 90, 130, 40))
prd.polygon([(580, 2700), (620, 2700), (740, 2300), (700, 2300)], fill=(120, 230, 255, 36))
prd.polygon([(660, 2700), (700, 2700), (820, 2300), (780, 2300)], fill=(220, 240, 255, 30))
prism = prism.filter(ImageFilter.GaussianBlur(14))
sf.composite(prism, mode="screen", opacity=0.7)

# ---------- 磨砂文字底板：讓文字落在乾淨的玻璃平面上 ----------
matte = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
md_ = ImageDraw.Draw(matte)
# 金句區（實際像素座標）
md_.rounded_rectangle([200, 360, 1800, 1060], radius=50, fill=(30, 44, 68, 255), outline=(120, 160, 200, 60), width=4)
# 冷知識區
md_.rounded_rectangle([200, 1100, 1800, 2080], radius=50, fill=(30, 44, 68, 255), outline=(120, 160, 200, 60), width=4)
# 編號日期區
md_.rounded_rectangle([300, 2816, 1700, 2960], radius=40, fill=(30, 44, 68, 255), outline=(120, 160, 200, 60), width=4)
sf.composite(matte)

# ---------- 文字（RGB 色散偏移 = 玻璃折射感） ----------
def chr_text(x, y, text, family, size, max_w=None, anchor="lt", line_gap=0.35, off=6):
    sf.text(x - off, y, text, family=family, size=size, fill=(255, 110, 135), anchor=anchor, max_w=max_w, line_gap=line_gap, allow_overlap=True)
    sf.text(x + off, y, text, family=family, size=size, fill=(110, 225, 255), anchor=anchor, max_w=max_w, line_gap=line_gap, allow_overlap=True)
    box = sf.text(x, y, text, family=family, size=size, fill=(246, 249, 255), anchor=anchor, max_w=max_w, line_gap=line_gap, allow_overlap=True)
    return box

if "——" in QUOTE:
    _parts = QUOTE.split("——")
    q_main = _parts[0].strip()
    q_src = "——" + _parts[1].strip()
else:
    q_main = QUOTE
    q_src = ""

q_box = chr_text(500, 250, q_main, "serif-cjk", 48, max_w=760, anchor="mt", line_gap=0.4, off=7)
a_box = chr_text(500, q_box.bottom + 30, q_src, "serif-cjk", 28, anchor="mt", line_gap=0.2, off=4)
f_box = chr_text(500, a_box.bottom + 80, FACT, "cjk-tc", 32, max_w=760, anchor="mt", line_gap=0.35, off=6)

sf.serial(200, 1450, SERIAL, family="mono", size=24, fill=(188, 212, 236), anchor="lm")
sf.datestamp(800, 1450, DATE, family="mono", size=24, fill=(188, 212, 236), anchor="rm")

sf.save(OUT_PATH)
