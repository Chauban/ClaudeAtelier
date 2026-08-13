from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sf = Surface(1000, 1080, scale=2, bg=(4, 7, 24))
SC = 2

# ---------- 背景：极光渐变 ----------
lay = sf.layer()
H, W = lay.shape[:2]

yy = np.linspace(0, 1, H)[:, None].astype(np.float32)
xx = np.linspace(0, 1, W)[None, :].astype(np.float32)

y3 = np.linspace(0, 1, H)[:, None, None].astype(np.float32)
c0 = np.array([3, 6, 20], dtype=np.float32).reshape(1, 1, 3)
c1 = np.array([8, 22, 48], dtype=np.float32).reshape(1, 1, 3)
c2 = np.array([18, 12, 40], dtype=np.float32).reshape(1, 1, 3)
c3 = np.array([6, 16, 34], dtype=np.float32).reshape(1, 1, 3)

mask1 = y3 < 0.42
mask2 = (y3 >= 0.42) & (y3 < 0.75)
mask3 = y3 >= 0.75
t1 = y3 / 0.42
t2 = (y3 - 0.42) / 0.33
t3 = (y3 - 0.75) / 0.25

base = np.zeros((H, W, 3), dtype=np.float32)
base += np.where(mask1, c0 * (1 - t1) + c1 * t1, 0.0).astype(np.float32)
base += np.where(mask2, c1 * (1 - t2) + c2 * t2, 0.0).astype(np.float32)
base += np.where(mask3, c2 * (1 - t3) + c3 * t3, 0.0).astype(np.float32)


def aurora_band(col, cy, amp, freq, phase, sigma, strength):
    off = cy + amp * np.sin(2 * np.pi * freq * (xx + phase))
    d = (yy - off) / sigma
    g = np.exp(-0.5 * d * d)
    return g[..., None] * (strength * col.reshape(1, 1, 3))


bands = [
    (( 72, 235, 185), 0.26, 0.13, 1.1, 0.05, 0.055, 0.80),
    (( 58, 200, 232), 0.33, 0.12, 1.4, 0.22, 0.060, 0.72),
    ((150, 105, 255), 0.39, 0.11, 1.7, 0.38, 0.065, 0.66),
    ((236, 105, 200), 0.46, 0.10, 2.1, 0.55, 0.060, 0.56),
    ((100, 190, 255), 0.54, 0.11, 2.5, 0.72, 0.070, 0.46),
    (( 96, 255, 180), 0.62, 0.09, 2.9, 0.15, 0.055, 0.40),
]

for col, cy, amp, freq, phase, sigma, strength in bands:
    col_f = np.array(col, dtype=np.float32) / 255.0
    base += aurora_band(col_f, cy, amp, freq, phase, sigma, strength)

base = np.clip(base, 0.0, 1.0)
lay[..., :3] = (base * 255).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# ---------- 繁星 ----------
stars = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(stars)
rng = np.random.default_rng(27)
for _ in range(360):
    x = float(rng.random()) * (W - 1)
    y = float(rng.random() ** 1.7) * H * 0.94
    rr = 1 if rng.random() < 0.72 else 2
    alpha = int(85 + 130 * rng.random())
    b = int(170 + 85 * rng.random())
    draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(b, b, 255, alpha))

stars_b = stars.filter(ImageFilter.GaussianBlur(1.5))
sf.composite(stars_b, mode='screen', opacity=0.85)

# ---------- 半透明暗色面板，保证文字对比度 ----------
panel = Image.new('RGBA', (W, H), (0, 0, 0, 0))
dp = ImageDraw.Draw(panel)
dp.rounded_rectangle(
    [55 * SC, 55 * SC, 945 * SC, 1025 * SC],
    radius=32 * SC,
    fill=(5, 9, 26, 158),
    outline=(150, 190, 255, 120),
    width=2 * SC,
)
sf.composite(panel)

# ---------- 面板上微弱光晕，呼应极光 ----------
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
rng = np.random.default_rng(8)
for _ in range(26):
    gx = float(rng.random() * 0.82 + 0.09) * W
    gy = float(rng.random() * 0.70 + 0.16) * H
    gr = float(rng.random() * 16 + 8) * SC
    col = rng.choice([(72, 235, 185), (58, 200, 232), (150, 105, 255),
                      (236, 105, 200), (100, 190, 255)])
    a = int(20 + 40 * rng.random())
    gd.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(*col, a))
glow = glow.filter(ImageFilter.GaussianBlur(18))
sf.composite(glow, mode='screen', opacity=0.35)

# ---------- 文字 ----------
sf.frame(105, 105, 790, 910)

quote_lines = [ln.strip() for ln in QUOTE.splitlines() if ln.strip()]
fact_lines = [ln.strip() for ln in FACT.splitlines() if ln.strip()]
quote_de = quote_lines[0]
quote_zh = quote_lines[1] if len(quote_lines) > 1 else ''
fact_de = fact_lines[0]
fact_zh = fact_lines[1] if len(fact_lines) > 1 else ''

top_y = 136
s_box = sf.serial(110, top_y, SERIAL, family='mono', size=20,
                  fill=(180, 210, 255), role='meta')
d_box = sf.datestamp(890, top_y, DATE, family='mono', size=20,
                     fill=(180, 210, 255), role='meta', anchor='rt')

y = s_box.bottom + 34

# 金句（德文）
q_de_box = sf.text(110, y, quote_de,
                   family='sans', size=44, fill=(250, 252, 255),
                   role='quote', bold=True, max_w=780, line_gap=0.44)
y = q_de_box.bottom + 18

# 金句中文翻译
if quote_zh:
    q_zh_box = sf.text(110, y, quote_zh,
                       family='cjk-sc', size=24, fill=(205, 220, 255),
                       role='meta', max_w=780, line_gap=0.46)
    y = q_zh_box.bottom + 46
else:
    y = q_de_box.bottom + 46

# 冷知识（德文）
f_de_box = sf.text(110, y, fact_de,
                   family='sans', size=32, fill=(238, 242, 250),
                   role='body', max_w=780, line_gap=0.48)
y = f_de_box.bottom + 10

# 冷知识中文翻译
if fact_zh:
    f_zh_box = sf.text(110, y, fact_zh,
                       family='cjk-sc', size=22, fill=(198, 218, 246),
                       role='meta', max_w=780, line_gap=0.46)

sf.save(OUT_PATH)
