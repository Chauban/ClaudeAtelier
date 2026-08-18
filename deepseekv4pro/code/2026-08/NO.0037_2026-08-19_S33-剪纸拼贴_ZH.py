from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ─── 画布 ───
w, h = 1000, 1750
sf = Surface(w, h, scale=2, bg=(245, 240, 230))

rng = np.random.RandomState(37)

# ─── 背景纸纹理 ───
lay_bg = sf.layer()
noise = rng.randint(0, 10, size=(sf.H, sf.W, 1), dtype=np.uint8).astype(np.int16)
base = np.array([245, 240, 230], dtype=np.int16).reshape(1, 1, 3)
val = base - noise
lay_bg[..., 0] = np.clip(val[..., 0], 0, 255).astype(np.uint8)
lay_bg[..., 1] = np.clip(val[..., 1], 0, 255).astype(np.uint8)
lay_bg[..., 2] = np.clip(val[..., 2], 0, 255).astype(np.uint8)
lay_bg[..., 3] = 255
sf.composite(lay_bg)

# ─── 辅助：剪纸形状 ───
def torn_rect(x, y, w, h, jitter=7, seed=0):
    r = np.random.RandomState(seed)
    n = 9
    pts = []
    for i in range(n):
        pts.append((x + w * i / (n - 1), y + r.uniform(-jitter, jitter)))
    for i in range(1, n):
        pts.append((x + w + r.uniform(-jitter, jitter), y + h * i / (n - 1)))
    for i in range(1, n):
        pts.append((x + w * (1 - i / (n - 1)), y + h + r.uniform(-jitter, jitter)))
    for i in range(1, n):
        pts.append((x + r.uniform(-jitter, jitter), y + h * (1 - i / (n - 1))))
    return pts

def irregular_circle(cx, cy, r, jitter=6, seed=0):
    rnd = np.random.RandomState(seed)
    n = 28
    pts = []
    for i in range(n):
        ang = 2 * np.pi * i / n
        rad = r + rnd.uniform(-jitter, jitter)
        pts.append((cx + rad * np.cos(ang), cy + rad * np.sin(ang)))
    return pts

def dune_polygon(x, y, w, h, wave_amp, wave_freq, jitter, seed):
    rnd = np.random.RandomState(seed)
    n = 44
    pts = []
    for i in range(n):
        px = x + w * i / (n - 1)
        phase = 2 * np.pi * wave_freq * i / (n - 1)
        py = y + wave_amp * np.sin(phase) + rnd.uniform(-jitter, jitter)
        pts.append((px, py))
    pts.append((x + w, y + h))
    pts.append((x, y + h))
    return pts

# ─── 投影层 ───
proj_img = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
proj_draw = ImageDraw.Draw(proj_img)

def add_shadow(points_logic, offset=(5, 6)):
    """在投影图层上绘制偏移的黑色形状，坐标参数为逻辑像素"""
    pts = [(px * 2 + offset[0] * 2, py * 2 + offset[1] * 2) for px, py in points_logic]
    proj_draw.polygon(pts, fill=(0, 0, 0, 255))

# 纸片与场景几何
QUOTE_PAPER = torn_rect(88, 168, 824, 250, jitter=8, seed=11)
FACT_PAPER  = torn_rect(60, 585, 880, 455, jitter=9, seed=12)
TAG_L_PAPER = torn_rect(130, 1150, 230, 92, jitter=6, seed=13)
TAG_R_PAPER = torn_rect(650, 1150, 230, 92, jitter=6, seed=14)
DUNE_FAR    = dune_polygon(0, 405, 1000, 95, 16, 2.2, 6, seed=21)
DUNE_NEAR   = dune_polygon(0, 450, 1000, 135, 14, 2.5, 5, seed=22)
SUN_SHAPE   = irregular_circle(170, 105, 52, jitter=5, seed=23)

# 投影
for shape, off in [
    (DUNE_FAR, (4, 5)),
    (DUNE_NEAR, (5, 6)),
    (SUN_SHAPE, (5, 6)),
    (FACT_PAPER, (6, 7)),
    (QUOTE_PAPER, (5, 6)),
    (TAG_L_PAPER, (4, 5)),
    (TAG_R_PAPER, (4, 5)),
]:
    add_shadow(shape, offset=off)

proj_img = proj_img.filter(ImageFilter.GaussianBlur(7))
sf.composite(proj_img, mode='normal', opacity=0.22)

# ─── 装饰层（沙漠场景） ───
deco_img = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
deco_draw = ImageDraw.Draw(deco_img)

# 太阳
sun_pts = [(px * 2, py * 2) for px, py in SUN_SHAPE]
deco_draw.polygon(sun_pts, fill=(232, 163, 61, 255))

# 云朵（撕纸小片）
deco_draw.polygon([(450*2, 72*2), (490*2, 58*2), (535*2, 72*2), (515*2, 88*2), (470*2, 90*2)], fill=(250, 246, 236, 255))
deco_draw.polygon([(720*2, 110*2), (760*2, 96*2), (800*2, 112*2), (780*2, 128*2), (740*2, 130*2), (715*2, 120*2)], fill=(248, 243, 230, 255))

# 远处沙丘
dune_far_pts = [(px * 2, py * 2) for px, py in DUNE_FAR]
deco_draw.polygon(dune_far_pts, fill=(224, 196, 154, 255))

# 近处沙丘
dune_near_pts = [(px * 2, py * 2) for px, py in DUNE_NEAR]
deco_draw.polygon(dune_near_pts, fill=(201, 149, 107, 255))

# ─── 蚂蚁剪影 ───
ant_color = (62, 42, 30, 255)
# 头
deco_draw.ellipse([625*2, 470*2, 670*2, 508*2], fill=ant_color)
# 胸
deco_draw.ellipse([560*2, 460*2, 625*2, 515*2], fill=ant_color)
# 腹
deco_draw.ellipse([450*2, 452*2, 560*2, 530*2], fill=ant_color)
# 连接补填
deco_draw.polygon([(622*2, 472*2), (636*2, 472*2), (636*2, 506*2), (622*2, 506*2)], fill=ant_color)
deco_draw.polygon([(558*2, 466*2), (574*2, 466*2), (574*2, 512*2), (558*2, 512*2)], fill=ant_color)

# 触角
deco_draw.line([(662*2, 476*2), (688*2, 452*2), (704*2, 440*2)], fill=ant_color, width=5)
deco_draw.line([(654*2, 474*2), (678*2, 448*2), (692*2, 436*2)], fill=ant_color, width=4)

# 腿（侧面三条，前腿为踩高跷长腿）
deco_draw.line([(610*2, 505*2), (638*2, 565*2), (654*2, 590*2)], fill=ant_color, width=7)
deco_draw.line([(592*2, 508*2), (584*2, 560*2)], fill=ant_color, width=6)
deco_draw.line([(567*2, 506*2), (540*2, 555*2)], fill=ant_color, width=6)

# 高跷小腿细线
deco_draw.line([(635*2, 565*2), (650*2, 588*2)], fill=(100, 70, 45, 255), width=3)

sf.composite(deco_img, mode='normal', opacity=1.0)

# ─── 文字纸片 ───
paper_img = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
paper_draw = ImageDraw.Draw(paper_img)

# FACT 纸片（下层）
fact_pts = [(px * 2, py * 2) for px, py in FACT_PAPER]
paper_draw.polygon(fact_pts, fill=(245, 232, 220, 255))

# QUOTE 纸片（上层，覆盖 FACT 重叠处）
quote_pts = [(px * 2, py * 2) for px, py in QUOTE_PAPER]
paper_draw.polygon(quote_pts, fill=(253, 248, 237, 255))

# 标签纸片
tag_l_pts = [(px * 2, py * 2) for px, py in TAG_L_PAPER]
paper_draw.polygon(tag_l_pts, fill=(232, 217, 192, 255))
tag_r_pts = [(px * 2, py * 2) for px, py in TAG_R_PAPER]
paper_draw.polygon(tag_r_pts, fill=(232, 217, 192, 255))

# 装饰小纸片
paper_draw.polygon([(70*2, 120*2), (100*2, 100*2), (90*2, 145*2)], fill=(196, 90, 50, 255))
paper_draw.polygon([(110*2, 130*2), (140*2, 115*2), (125*2, 155*2)], fill=(90, 122, 140, 255))
paper_draw.ellipse([(830*2, 80*2), (870*2, 120*2)], fill=(216, 170, 80, 255))
paper_draw.ellipse([(855*2, 120*2), (895*2, 160*2)], fill=(180, 130, 70, 255))
paper_draw.polygon([(45*2, 415*2), (70*2, 405*2), (67*2, 450*2), (42*2, 440*2)], fill=(140, 170, 155, 255))

sf.composite(paper_img, mode='normal', opacity=1.0)

# ─── 文字 ───
sf.frame(40, 150, 920, 1150)

# QUOTE（纸上居中）
quote_box = sf.text(
    500, 285,
    QUOTE,
    family='serif-cjk', size=40, fill=(62, 42, 30),
    anchor='mm', role='quote', bold=True,
    max_w=690, line_gap=0.45,
    allow_overlap=False
)

# FACT（左对齐）
fact_box = sf.text(
    145, 665,
    FACT,
    family='cjk-sc', size=30, fill=(58, 42, 26),
    anchor='lt', role='body', bold=False,
    max_w=710, line_gap=0.5,
    allow_overlap=False
)

# SERIAL 标签
sf.serial(
    165, 1196,
    SERIAL,
    family='cjk-sc', size=22, fill=(74, 58, 42),
    anchor='lm', role='meta', bold=False,
    max_w=None, line_gap=0.3,
    allow_overlap=False
)

# DATE 标签
sf.datestamp(
    685, 1196,
    DATE,
    family='cjk-sc', size=22, fill=(74, 58, 42),
    anchor='lm', role='meta', bold=False,
    max_w=None, line_gap=0.3,
    allow_overlap=False
)

sf.save(OUT_PATH)
