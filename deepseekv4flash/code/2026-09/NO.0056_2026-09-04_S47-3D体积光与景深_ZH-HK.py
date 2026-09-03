import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

# ---------- 画布基准 ----------
W0, H0 = 1000, 1880
sf = Surface(W0, H0, scale=2, bg=(10, 13, 24))
sf.frame(50, 60, 900, 1800)

RNG = np.random.default_rng(56)

# 纯暗底色：文字区可保持干净，光效集中在中段
base_arr = np.full((H0, W0, 3), (10, 13, 24), dtype=np.float32)
art = Image.fromarray(base_arr.astype(np.uint8), "RGB").convert("RGBA")


def beam(img, pts, color, alpha, blur):
    lay = Image.new("RGBA", (W0, H0), (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon(pts, fill=color + (int(alpha),))
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(lay)


def blob(img, cx, cy, rx, ry, color, alpha, blur):
    lay = Image.new("RGBA", (W0, H0), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse(
        [cx - rx, cy - ry, cx + rx, cy + ry], fill=color + (int(alpha),)
    )
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(lay)


# ---------- 中央体积光区（刻意避开上下两段文字） ----------
blob(art, 500, 860, 560, 450, (168, 148, 112), 14, 240)

beam(art, [(420, 540), (580, 540), (700, 1190), (300, 1190)], (255, 216, 156), 22, 130)
beam(art, [(280, 560), (720, 560), (900, 1230), (100, 1230)], (196, 220, 255), 9, 170)
beam(art, [(470, 560), (530, 560), (610, 1160), (390, 1160)], (255, 236, 190), 26, 85)

# 前景虚化光斑：只出现在中段视觉区
bokeh_spots = [
    (120, 720, 58, (205, 225, 255), 22),
    (900, 680, 48, (255, 216, 170), 20),
    (170, 1030, 66, (210, 230, 248), 14),
    (860, 1100, 60, (255, 202, 148), 16),
    (90, 900, 36, (255, 232, 196), 18),
    (915, 860, 36, (196, 220, 255), 16),
    (250, 600, 30, (255, 226, 185), 14),
    (750, 610, 28, (255, 226, 185), 12),
    (820, 980, 44, (200, 225, 252), 14),
    (180, 1180, 48, (255, 212, 168), 12),
]
for cx, cy, r, col, a in bokeh_spots:
    blob(art, cx, cy, r, r, col, a, 34)

# ---------- 尘埃与粒子 ----------
dust = Image.new("RGBA", (W0, H0), (0, 0, 0, 0))
d_dust = ImageDraw.Draw(dust)
dust_palette = [
    (255, 240, 205),
    (232, 224, 190),
    (214, 228, 250),
    (255, 216, 172),
    (178, 202, 238),
]
for _ in range(480):
    x = int(RNG.uniform(10, W0 - 10))
    y = int(RNG.uniform(520, 1270))
    c = dust_palette[int(RNG.integers(0, len(dust_palette)))]
    if RNG.random() < 0.7:
        r = int(RNG.integers(1, 3))
        a = int(RNG.integers(16, 60))
    else:
        r = int(RNG.integers(3, 6))
        a = int(RNG.integers(7, 24))
    d_dust.ellipse([x - r, y - r, x + r, y + r], fill=c + (a,))
dust = dust.filter(ImageFilter.GaussianBlur(1.0))
art.alpha_composite(dust)

# ---------- 发光人形「大」＋頭上一簪 → 「夫」 ----------
# 人形中軸：约 y=626(簪) 至 y=1100(足)，与上下文字错开
line_segments = [
    ((330, 626), (670, 626)),      # 簪：頭上那一橫
    ((500, 764), (500, 940)),      # 身
    ((500, 810), (320, 690)),      # 左臂
    ((500, 810), (680, 690)),      # 右臂
    ((500, 940), (410, 1100)),     # 左腿
    ((500, 940), (590, 1100)),     # 右腿
]
head_cx, head_cy, head_r = 500, 710, 54
head_box = [head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r]

# 外发光
glow_lay = Image.new("RGBA", (W0, H0), (0, 0, 0, 0))
d_glow = ImageDraw.Draw(glow_lay)
glow_col = (255, 206, 146, 52)
for p1, p2 in line_segments:
    d_glow.line([p1, p2], fill=glow_col, width=28)
d_glow.ellipse(head_box, outline=glow_col, width=28)
glow_lay = glow_lay.filter(ImageFilter.GaussianBlur(11))
art.alpha_composite(glow_lay)

# 高亮核心
core_lay = Image.new("RGBA", (W0, H0), (0, 0, 0, 0))
d_core = ImageDraw.Draw(core_lay)
core_col = (255, 244, 206, 255)
for p1, p2 in line_segments:
    d_core.line([p1, p2], fill=core_col, width=7)
d_core.ellipse(head_box, outline=core_col, width=7)
core_lay = core_lay.filter(ImageFilter.GaussianBlur(2.2))
art.alpha_composite(core_lay)

# 頭後一層暖光暈
blob(art, 500, 730, 130, 130, (255, 205, 145), 20, 60)

# ---------- 把上下文字區還原成乾淨底色，確保不被光效穿過 ----------
mask_img = Image.new("L", (W0, H0), 0)
md = ImageDraw.Draw(mask_img)
md.rectangle([10, 50, 990, 560], fill=255)      # 上：金句區
md.rectangle([10, 1280, 990, H0], fill=255)     # 下：冷知識＋落款區
mask_img = mask_img.filter(ImageFilter.GaussianBlur(90))
mask = np.asarray(mask_img, dtype=np.float32) / 255.0

cur_arr = np.asarray(art.convert("RGB"), dtype=np.float32)
cur_arr = cur_arr * (1.0 - mask[..., None]) + base_arr * mask[..., None]
art = Image.fromarray(np.clip(cur_arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

# ---------- 送入畫布（背景層，Tier 2） ----------
sf.composite(
    Image.fromarray(np.asarray(art.convert("RGB")), "RGB").resize(
        (sf.W, sf.H), Image.LANCZOS
    ),
    mode="normal",
    opacity=1.0,
)

# ---------- 文字（受控層，Tier 1） ----------
qbox = sf.text(
    500,
    180,
    QUOTE,
    family="cjk-hk",
    size=42,
    fill=(252, 240, 206),
    anchor="mt",
    max_w=870,
    line_gap=0.55,
    role="quote",
)

fbox = sf.text(
    500,
    1400,
    FACT,
    family="cjk-hk",
    size=30,
    fill=(232, 236, 234),
    anchor="mt",
    max_w=870,
    line_gap=0.58,
    role="body",
)

sf.serial(
    940,
    1760,
    SERIAL,
    family="mono",
    size=19,
    fill=(206, 220, 228),
    anchor="rt",
    role="meta",
)

sf.datestamp(
    940,
    1796,
    DATE,
    family="mono",
    size=19,
    fill=(206, 220, 228),
    anchor="rt",
    role="meta",
)

sf.save(OUT_PATH)
