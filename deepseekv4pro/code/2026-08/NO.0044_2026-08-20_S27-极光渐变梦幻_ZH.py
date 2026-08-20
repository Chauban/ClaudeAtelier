from atelier_canvas import Surface
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import math

W, H = 1000, 1260
sf = Surface(W, H, scale=2, bg=(5, 6, 18))
sf.frame(70, 70, W - 140, H - 140)

# ---------- 颜色 ----------
PALE = (236, 244, 249)
PALE_FACT = (219, 230, 238)
META = (177, 225, 224)
GOLD_PALE = (239, 226, 175)
UNIFORM_BG = np.array([5, 6, 18], dtype=np.float32)

# ---------- 2D 坐标网格 ----------
yy = np.linspace(0, 1, sf.H)[:, None].astype(np.float32)
xx = np.linspace(0, 1, sf.W)[None, :].astype(np.float32)

def smoothstep(a, b, x):
    u = np.clip((x - a) / (b - a + 1e-8), 0, 1)
    return u * u * (3 - 2 * u)

# 中央文字区域要安静，背景尽量干净
qx = smoothstep(0.03, 0.09, xx) * (1 - smoothstep(0.89, 0.96, xx))
qy = smoothstep(0.23, 0.27, yy) * (1 - smoothstep(0.86, 0.93, yy))
quiet_w = 0.90 * qx * qy            # 文字区约 0.90，外部约 0
quiet = 1 - quiet_w                 # 极光在文字区约 0.10

# ---------- 背景：外部保留渐变，文字区压成均匀深色 ----------
base_top = np.array([8, 10, 34], dtype=np.float32).reshape(1, 1, 3)
base_mid = np.array([42, 23, 74], dtype=np.float32).reshape(1, 1, 3)
base_bot = np.array([10, 16, 34], dtype=np.float32).reshape(1, 1, 3)

grad = (
    base_top * (1 - yy[..., None] * 0.18)
    + base_mid * (yy[..., None] * 0.55)
    + base_bot * (yy[..., None] * 0.35)
)
az = np.clip(xx * 0.35 + 0.65, 0, 1)
grad = grad * az[..., None]

col = grad * (1 - quiet_w[..., None]) + UNIFORM_BG * quiet_w[..., None]
col = np.clip(col, 0, 255).astype(np.uint8)

bg_lay = sf.layer()
bg_lay[..., :3] = col
bg_lay[..., 3] = 255
sf.composite(bg_lay)

# ---------- 噪声调制极光 ----------
noise_a = np.random.default_rng(17).random((sf.H, sf.W), dtype=np.float32)
noise_b = np.random.default_rng(31).random((sf.H, sf.W), dtype=np.float32)
noise = (noise_a * 0.65 + noise_b * 0.35).astype(np.float32)
nv = noise * 0.28 + 0.72

xuv = (xx * 2.2 - 1.1).astype(np.float32)
yuv = (yy * 2.0 - 1.0).astype(np.float32)
curl = nv * (
    np.sin(yuv * 9.0 + xuv * 2.6) * 0.85
    + np.sin(yuv * 2.7 - xuv * 4.5) * 0.45
    + 0.8
)
curl = np.clip(curl, 0, 1)

m1 = (1 - smoothstep(0.22, 0.40, yy)) * smoothstep(0.16, 0.30, curl)
m2 = smoothstep(0.26, 0.38, yy) * smoothstep(0.02, 0.10, curl) * 0.7
m3 = smoothstep(0.45, 0.56, yy) * smoothstep(0.34, 0.46, curl) * 1.0
m4 = smoothstep(0.66, 0.75, yy) * smoothstep(0.14, 0.24, curl) * 0.8
m5 = smoothstep(0.80, 0.92, yy) * smoothstep(0.45, 0.54, curl) * 0.9
mask = (m1 + m2 + m3 + m4 + m5) * quiet
mask = np.clip(mask, 0, 1.6)

pal = np.array([
    [38, 24, 88],
    [68, 21, 110],
    [120, 36, 134],
    [84, 150, 170],
    [90, 202, 169],
    [166, 247, 206],
    [225, 242, 238],
], dtype=np.float32)
t = np.clip((curl * 6.6 - mask * 1.2), 0, 6)
f = np.floor(t).astype(np.int32)
g = np.clip(f + 1, 0, 6)
frac = (t - f)[..., None]
val = pal[f] * (1 - frac) + pal[g] * frac

aur = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
aur[..., :3] = np.clip(val, 0, 255).astype(np.uint8)
aur[..., 3] = np.clip(mask * 185, 0, 255).astype(np.uint8)
aur_pil = Image.fromarray(aur, "RGBA").filter(ImageFilter.GaussianBlur(14))
sf.composite(aur_pil, mode="screen", opacity=1.0)

# ---------- 星点（避开文字区） ----------
star_lay = sf.layer()
rng = np.random.default_rng(99)
n_stars = 650
sx = rng.integers(0, sf.W, n_stars)
sy = rng.integers(0, sf.H, n_stars)
bright = rng.random(n_stars) ** 2.2
for x, y, b in zip(sx, sy, bright):
    xf, yf = x / sf.W, y / sf.H
    if 0.06 < xf < 0.94 and 0.24 < yf < 0.88:
        continue
    ix, iy = int(round(x)), int(round(y))
    if 0 <= ix < sf.W and 0 <= iy < sf.H:
        c = int(150 + 105 * b)
        star_lay[iy, ix, :3] = [c, c, 255]
        star_lay[iy, ix, 3] = 255
sf.composite(star_lay, mode="screen", opacity=0.9)

# ---------- 散景光斑（放在顶部与底部，避免文字后方） ----------
bokeh = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
bd = ImageDraw.Draw(bokeh)
for cx, cy, cr, r, g, b, o in [
    (250, 155, 145, 75, 195, 160, 40),
    (800, 120, 180, 120, 145, 205, 32),
    (620, 210, 120, 105, 180, 140, 38),
    (920, 260, 110, 90, 190, 170, 30),
    (140, 1120, 150, 125, 160, 190, 34),
    (850, 1150, 170, 80, 164, 176, 28),
    (180, 1185, 130, 120, 138, 135, 26),
    (820, 1210, 140, 95, 168, 126, 24),
]:
    bd.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(int(r), int(g), int(b), int(o)))
bokeh = bokeh.filter(ImageFilter.GaussianBlur(32))
sf.composite(bokeh, mode="screen", opacity=1.0)

# ---------- 暗角 ----------
vig = sf.layer()
vx = (np.linspace(0, 1, sf.W)[None, :].astype(np.float32) - 0.5) * 2.0
vy = (np.linspace(0, 1, sf.H)[:, None].astype(np.float32) - 0.5) * 2.0
m_vig = 1 - (0.55 * (vx * vx) + 0.75 * (vy * vy))
m_vig = np.clip(m_vig, 0.35, 1)
vig[..., :3] = np.clip(vig[..., :3] * m_vig[..., None], 0, 255).astype(np.uint8)
vig[..., 3] = 255
sf.composite(vig, mode="multiply", opacity=1.0)

# ---------- 顶部规则线 ----------
head_rule = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
hr_d = ImageDraw.Draw(head_rule)
hr_d.line([70, 138, W - 70, 138], fill=(168, 218, 222, 70), width=2)
sf.composite(head_rule, mode="normal", opacity=1.0)

# ---------- 顶部装饰星 ----------
star_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
star_d = ImageDraw.Draw(star_img)
def draw_star_pil(cx, cy, rad, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = rad if i % 2 == 0 else rad * 0.45
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    star_d.polygon(pts, fill=fill)

draw_star_pil(500, 245, 18, (208, 234, 238, 255))
draw_star_pil(500, 245, 12, (255, 255, 255, 255))
sf.composite(star_img, mode="normal", opacity=1.0)

# ---------- 顶部元信息 ----------
sf.serial(70, 76, SERIAL, family="mono", size=20, fill=META,
          anchor="lt", role="meta", bold=True)
date_w, _ = sf.measure(DATE, family="mono", size=20, bold=True)
sf.datestamp(W - 70 - date_w, 76, DATE, family="mono", size=20,
             fill=META, anchor="lt", role="meta", bold=True)

# ---------- 金句 ----------
q_box1 = sf.text(500, 380, "让那些觉得自己能做得更好的人，",
                 family="serif-cjk", size=56, fill=PALE,
                 anchor="mt", role="quote", line_gap=0.18)
q_box2 = sf.text(500, q_box1.bottom + 22, "来试试看吧。",
                 family="serif-cjk", size=56, fill=PALE,
                 anchor="mt", role="quote", line_gap=0.18)

# ---------- 金句与冷知识之间的装饰分隔线 ----------
sep_y = q_box2.bottom + 52
sep_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
sep_d = ImageDraw.Draw(sep_img)
sep_d.line([370, sep_y + 12, 630, sep_y + 12], fill=(168, 218, 222, 120), width=2)
draw_star_pil(500, sep_y, 12, (225, 242, 238, 255))
sf.composite(sep_img, mode="normal", opacity=1.0)

# ---------- 冷知识 ----------
fact_top = sep_y + 66
fact_wrap = sf.wrap(FACT, family="cjk-sc", size=34, max_w=860)
fact_y = fact_top
last_bottom = fact_y
for line in fact_wrap:
    fb = sf.text(500, fact_y, line, family="cjk-sc", size=34,
                 fill=PALE_FACT, anchor="mt", role="body", line_gap=0.5)
    last_bottom = fb.bottom
    fact_y = last_bottom + 14

# ---------- 底部装饰星（非文字） ----------
bottom_star = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
bs_d = ImageDraw.Draw(bottom_star)
draw_star_pil(500, last_bottom + 42, 14, (208, 234, 238, 255))
sf.composite(bottom_star, mode="normal", opacity=1.0)

sf.save(OUT_PATH)
