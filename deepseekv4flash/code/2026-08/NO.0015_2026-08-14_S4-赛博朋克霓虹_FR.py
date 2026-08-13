import math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from atelier_canvas import Surface

W, H = 1000, 1210
sf = Surface(W, H, scale=2, bg=(6, 9, 18))
sf.frame(60, 50, W - 120, H - 100)

# ---------- 拆分原文 / 中文翻译 ----------
if "\n" in QUOTE:
    Q_FR, Q_CN = QUOTE.split("\n", 1)
    Q_CN = Q_CN.strip()
else:
    idx = QUOTE.find("（")
    if idx > 0:
        Q_FR = QUOTE[:idx].strip()
        Q_CN = QUOTE[idx:].strip()
    else:
        Q_FR = QUOTE
        Q_CN = ""

if "\n" in FACT:
    F_FR, F_CN = FACT.split("\n", 1)
    F_CN = F_CN.strip()
else:
    idx = FACT.find("（")
    if idx > 0:
        F_FR = FACT[:idx].strip()
        F_CN = FACT[idx:].strip()
    else:
        F_FR = FACT
        F_CN = ""

# ---------- 排版预算 ----------
q_parts = Q_FR.split(" ; ")
q_lines = []
for i, p in enumerate(q_parts):
    p = p.strip()
    q_lines.append(p + " ;" if i < len(q_parts) - 1 else p)

qsize = 38
q_m = [sf.measure(l, "sans", qsize, bold=True) for l in q_lines]
while max(m[0] for m in q_m) > 860 and qsize > 30:
    qsize -= 2
    q_m = [sf.measure(l, "sans", qsize, bold=True) for l in q_lines]
q_line_h = int(qsize * 2.1)
quote_y = 400
quote_bottom = quote_y + (len(q_lines) - 1) * q_line_h + q_m[-1][1]

q_cn_size = 28
q_cn_lines = sf.wrap(Q_CN, "cjk-sc", q_cn_size, 860)
q_cn_m = [sf.measure(l, "cjk-sc", q_cn_size) for l in q_cn_lines]
q_cn_line_h = int(q_cn_size * 2.1)
q_cn_y = quote_bottom + 38
q_cn_bottom = q_cn_y + (len(q_cn_lines) - 1) * q_cn_line_h + q_cn_m[-1][1]

fact_x = 100
fact_w = 800
f_fr_size = 30
f_fr_lines = sf.wrap(F_FR, "sans", f_fr_size, fact_w)
f_fr_m = [sf.measure(l, "sans", f_fr_size) for l in f_fr_lines]
f_fr_line_h = int(f_fr_size * 2.1)
fact_y = q_cn_bottom + 56
f_fr_bottom = fact_y + (len(f_fr_lines) - 1) * f_fr_line_h + f_fr_m[-1][1]

f_cn_size = 28
f_cn_lines = sf.wrap(F_CN, "cjk-sc", f_cn_size, fact_w)
f_cn_m = [sf.measure(l, "cjk-sc", f_cn_size) for l in f_cn_lines]
f_cn_line_h = int(f_cn_size * 2.1)
f_cn_y = f_fr_bottom + 36

div_y = fact_y - 34

# ============ Tier 2: 背景与装饰 ============

# 深蓝 → 暗紫渐变
bg = sf.layer()
yyv = np.linspace(0, 1, sf.H)[:, None]
bg[..., 0] = (6 + 18 * yyv).astype(np.uint8)
bg[..., 1] = (9 + 13 * yyv).astype(np.uint8)
bg[..., 2] = (18 + 40 * yyv).astype(np.uint8)
bg[..., 3] = 255
sf.composite(bg)

# 霓虹斜带
bands = sf.layer()
d = ImageDraw.Draw(Image.fromarray(bands))
d.line([(0, int(sf.H * 0.90)), (int(sf.W), int(sf.H * 0.50))], fill=(255, 42, 109, 34), width=12)
d.line([(0, int(sf.H * 0.95)), (int(sf.W), int(sf.H * 0.55))], fill=(255, 42, 109, 18), width=6)
bands_img = Image.fromarray(bands).filter(ImageFilter.GaussianBlur(22))
sf.composite(bands_img, mode="screen", opacity=0.8)

# 均匀网格
grid = sf.layer()
d = ImageDraw.Draw(Image.fromarray(grid))
for gx in range(0, sf.W + 1, 120):
    d.line([(gx, 0), (gx, sf.H)], fill=(5, 217, 232, 16), width=1)
for gy in range(0, sf.H + 1, 120):
    d.line([(0, gy), (sf.W, gy)], fill=(5, 217, 232, 16), width=1)
sf.composite(grid)

# 底部透视网格（压到文字下方，作为收尾装饰）
persp = sf.layer()
d = ImageDraw.Draw(Image.fromarray(persp))
horizon = int(sf.H * 0.72)
cxm = sf.W / 2.0
for i in range(-16, 17):
    xa = cxm + i * 12
    xb = cxm + i * 110
    d.line([(xa, horizon), (xb, sf.H)], fill=(5, 217, 232, 30), width=2)
for j in range(1, 9):
    f = (j / 9.0) ** 2
    yph = int(horizon + (sf.H - horizon) * f)
    d.line([(0, yph), (sf.W, yph)], fill=(5, 217, 232, 22), width=1)
d.line([(0, horizon), (sf.W, horizon)], fill=(5, 217, 232, 55), width=2)
persp_img = Image.fromarray(persp).filter(ImageFilter.GaussianBlur(1))
sf.composite(persp_img)

# 青色大气辉光
xxg = np.linspace(0, 1, sf.W)[None, :]
yyg = np.linspace(0, 1, sf.H)[:, None]
glow = sf.layer()
ga = np.exp(-((xxg - 0.5) ** 2 * 3 + (yyg - 0.20) ** 2 * 16))
glow[..., 0] = 5
glow[..., 1] = 217
glow[..., 2] = 232
glow[..., 3] = (ga * 70).astype(np.uint8)
sf.composite(glow, mode="screen")

# 粉色角落辉光
glowp = sf.layer()
gb = np.exp(-((xxg - 0.70) ** 2 * 10 + (yyg - 0.55) ** 2 * 8))
glowp[..., 0] = 255
glowp[..., 1] = 42
glowp[..., 2] = 109
glowp[..., 3] = (gb * 46).astype(np.uint8)
sf.composite(glowp, mode="screen")

# 噪点
noise = sf.layer()
rng = np.random.default_rng(2026)
noise[..., 0] = rng.integers(0, 70, size=(sf.H, sf.W), dtype=np.uint8)
noise[..., 1] = rng.integers(0, 70, size=(sf.H, sf.W), dtype=np.uint8)
noise[..., 2] = rng.integers(0, 90, size=(sf.H, sf.W), dtype=np.uint8)
noise[..., 3] = 12
sf.composite(noise, mode="screen")

# 故障色块
glitch = sf.layer()
d = ImageDraw.Draw(Image.fromarray(glitch))
rg = np.random.default_rng(9)
for _ in range(14):
    gx0 = int(rg.integers(80, W - 80))
    gy0 = int(rg.integers(90, int(H * 0.72)))
    gw = int(rg.integers(20, 120))
    gh = int(rg.integers(2, 5))
    col = (255, 42, 109, 55) if rg.random() < 0.5 else (5, 217, 232, 45)
    d.rectangle([gx0 * 2, gy0 * 2, (gx0 + gw) * 2, (gy0 + gh) * 2], fill=col)
sf.composite(glitch, mode="screen")

# HUD 顶栏
hud = sf.layer()
d = ImageDraw.Draw(Image.fromarray(hud))
d.rectangle([120, 100, (W - 60) * 2, 200], fill=(5, 217, 232, 10))
d.line([(120, 200), ((W - 60) * 2, 200)], fill=(5, 217, 232, 60), width=1)
cc = (5, 217, 232, 150)
Lc = 20
d.line([(120, 100), (120 + Lc, 100)], fill=cc, width=2)
d.line([(120, 100), (120, 100 + Lc)], fill=cc, width=2)
d.line([((W - 60) * 2 - Lc, 100), ((W - 60) * 2, 100)], fill=cc, width=2)
d.line([((W - 60) * 2, 100), ((W - 60) * 2, 100 + Lc)], fill=cc, width=2)
sf.composite(hud)

# 漂浮粒子
particles = sf.layer()
d = ImageDraw.Draw(Image.fromarray(particles))
rp = np.random.default_rng(42)
for _ in range(8):
    ppx = int(rp.integers(120, W - 120))
    ppy = int(rp.integers(110, 350))
    prad = int(rp.integers(2, 5))
    pcol = (5, 217, 232, 130) if rp.random() < 0.6 else (255, 42, 109, 130)
    d.ellipse([(ppx - prad) * 2, (ppy - prad) * 2, (ppx + prad) * 2, (ppy + prad) * 2], fill=pcol)
parts_img = Image.fromarray(particles).filter(ImageFilter.GaussianBlur(3))
sf.composite(parts_img, mode="screen", opacity=0.8)

# 十进制时钟：外发光
CX, CY, CR = 500, 225, 108
cg = sf.layer()
d = ImageDraw.Draw(Image.fromarray(cg))
cx, cy, r = CX * 2, CY * 2, CR * 2
d.ellipse([cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8], outline=(5, 217, 232, 70), width=10)
for i in range(10):
    ang = math.radians(-90 + i * 36)
    x1 = cx + (r - 20) * math.cos(ang)
    y1 = cy + (r - 20) * math.sin(ang)
    x2 = cx + (r - 2) * math.cos(ang)
    y2 = cy + (r - 2) * math.sin(ang)
    d.line([(x1, y1), (x2, y2)], fill=(5, 217, 232, 80), width=7)
d.line([(cx, cy), (cx, cy + r - 52)], fill=(255, 42, 109, 90), width=10)
cg_img = Image.fromarray(cg).filter(ImageFilter.GaussianBlur(12))
sf.composite(cg_img, mode="screen", opacity=0.85)

# 十进制时钟：实体表盘
clock = sf.layer()
d = ImageDraw.Draw(Image.fromarray(clock))
cx, cy, r = CX * 2, CY * 2, CR * 2
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(5, 217, 232, 235), width=3)
d.ellipse([cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12], outline=(5, 217, 232, 70), width=1)
for i in range(10):
    ang = math.radians(-90 + i * 36)
    x1 = cx + (r - 20) * math.cos(ang)
    y1 = cy + (r - 20) * math.sin(ang)
    x2 = cx + (r - 2) * math.cos(ang)
    y2 = cy + (r - 2) * math.sin(ang)
    wd = 5 if i in (0, 5) else 3
    d.line([(x1, y1), (x2, y2)], fill=(5, 217, 232, 220), width=wd)
ang5 = math.radians(90)
tip_len = CR - 28
tx0, ty0 = CX + tip_len * math.cos(ang5), CY + tip_len * math.sin(ang5)
tlx, tly = CX - 16 * math.cos(ang5), CY - 16 * math.sin(ang5)
d.line([(int(tlx * 2), int(tly * 2)), (int(tx0 * 2), int(ty0 * 2))], fill=(255, 42, 109, 240), width=6)
d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(5, 217, 232, 235))
d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 42, 109, 240))
sf.composite(clock)

# 分隔线
div = sf.layer()
d = ImageDraw.Draw(Image.fromarray(div))
dv = int(div_y * 2)
d.line([(150 * 2, dv), ((W - 150) * 2, dv)], fill=(255, 42, 109, 120), width=2)
d.rectangle([(150 * 2 - 5, dv - 5), (150 * 2 + 5, dv + 5)], fill=(5, 217, 232, 200))
d.rectangle([((W - 150) * 2 - 5, dv - 5), ((W - 150) * 2 + 5, dv + 5)], fill=(5, 217, 232, 200))
div_img = Image.fromarray(div).filter(ImageFilter.GaussianBlur(5))
sf.composite(div_img, mode="screen", opacity=0.8)

# 金句辉光
qg = sf.layer()
d = ImageDraw.Draw(Image.fromarray(qg))
q_h_est = int(quote_bottom - quote_y)
d.rectangle([int((W / 2 - 430) * 2), int((quote_y - 30) * 2),
             int((W / 2 + 430) * 2), int((quote_y + q_h_est + 30) * 2)],
            fill=(255, 42, 109, 46))
qg_img = Image.fromarray(qg).filter(ImageFilter.GaussianBlur(30))
sf.composite(qg_img, mode="screen")

# 冷知识辉光
fg = sf.layer()
d = ImageDraw.Draw(Image.fromarray(fg))
fact_h_est = int(f_fr_bottom - fact_y)
d.rectangle([(fact_x - 30) * 2, (fact_y - 30) * 2,
             (fact_x + fact_w + 30) * 2, (fact_y + fact_h_est) * 2],
            fill=(5, 217, 232, 24))
fg_img = Image.fromarray(fg).filter(ImageFilter.GaussianBlur(26))
sf.composite(fg_img, mode="screen")

# ============ Tier 1: 文字 ============

# 金句法文
for i, line in enumerate(q_lines):
    lw, _ = q_m[i]
    sf.text((W - lw) / 2, quote_y + i * q_line_h, line,
            family="sans", size=qsize, fill=(255, 82, 136),
            anchor="lt", role="quote", bold=True, line_gap=0.4)

# 金句中文翻译
for i, line in enumerate(q_cn_lines):
    lw, _ = q_cn_m[i]
    sf.text((W - lw) / 2, q_cn_y + i * q_cn_line_h, line,
            family="cjk-sc", size=q_cn_size, fill=(214, 224, 235),
            anchor="lt", role="body", line_gap=0.35)

# 冷知识法文
for i, line in enumerate(f_fr_lines):
    sf.text(fact_x, fact_y + i * f_fr_line_h, line,
            family="sans", size=f_fr_size, fill=(186, 228, 238),
            anchor="lt", role="body", line_gap=0.4)

# 冷知识中文翻译
for i, line in enumerate(f_cn_lines):
    sf.text(fact_x, f_cn_y + i * f_cn_line_h, line,
            family="cjk-sc", size=f_cn_size, fill=(150, 172, 192),
            anchor="lt", role="body", line_gap=0.35)

# 编号与日期
sf.serial(60, 64, SERIAL, family="mono", size=20, fill=(5, 217, 232), anchor="lt", role="meta")
sf.datestamp(W - 60, 64, DATE, family="mono", size=20, fill=(5, 217, 232), anchor="rt", role="meta")

sf.save(OUT_PATH)
