from atelier_canvas import Surface
from PIL import Image, ImageDraw
import numpy as np
import math

PAPER = (248, 246, 241)
INK = (30, 27, 23)
RED = (203, 42, 36)
BROWN_D = (91, 64, 41)
BROWN_M = (124, 91, 59)
BROWN_L = (159, 121, 82)
OWL_BROWN = (158, 128, 90)
OWL_EDGE = (108, 78, 52)
CREAM = (246, 241, 230)
FACE = (247, 244, 236)
GOLD = (246, 184, 28)
GRASS = (168, 150, 112)

W, H = 1000, 1500
sf = Surface(W, H, scale=2, bg=PAPER)
sf.frame(90, 60, 820, 1320)

SC = 2


def R(v):
    return int(round(v * SC))


def C(c, a=255):
    return (c[0], c[1], c[2], a)


def hline(y, x0, x1, color, width=1.2):
    im = Image.fromarray(sf.layer(), "RGBA")
    dd = ImageDraw.Draw(im)
    dd.line([R(x0), R(y), R(x1), R(y)], fill=C(color), width=max(1, R(width)))
    sf.composite(im)


# 顶部基准细线（瑞士网格编排线）
hline(126, 90, 910, (35, 31, 27), 1.6)

# 底部朱红色带（装饰，不承载文字）
red_band_im = Image.fromarray(sf.layer(), "RGBA")
drb = ImageDraw.Draw(red_band_im)
drb.rectangle([0, R(1442), R(W), R(H)], fill=C(RED))
sf.composite(red_band_im)

# ===== 插图主图层 =====
im = Image.fromarray(sf.layer(), "RGBA")
d = ImageDraw.Draw(im)


def ell(cx, cy, rx, ry, fill, outline=None, width=0):
    kw = {"fill": C(fill)}
    if outline is not None:
        kw["outline"] = C(outline)
        if width > 0:
            kw["width"] = R(width)
    d.ellipse([R(cx - rx), R(cy - ry), R(cx + rx), R(cy + ry)], **kw)


def rrect(x0, y0, x1, y1, r, fill):
    d.rounded_rectangle(
        [R(x0), R(y0), R(x1), R(y1)],
        radius=R(r),
        fill=C(fill)
    )


def beetle(x, y, r=8):
    ell(x, y, r, r * 0.9, RED)
    ell(x - r * 0.4, y - r * 0.25, r * 0.3, r * 0.3, (20, 17, 15))
    d.line([R(x + r * 0.35), R(y - r * 0.5), R(x + r * 0.8), R(y - r * 1.05)],
           fill=(40, 35, 30), width=max(1, R(1.2)))
    d.line([R(x - r * 0.3), R(y - r * 0.55), R(x - r * 0.7), R(y - r * 1.05)],
           fill=(40, 35, 30), width=max(1, R(1.2)))


G = 704

# 地线
d.line([R(120), R(G + 2), R(890), R(G + 2)], fill=C(INK), width=R(1.8))

# 洞口前扁塌的牛粪堆
ell(238, 686, 108, 21, BROWN_D)
ell(180, 691, 54, 12, BROWN_M)
ell(285, 691, 46, 11, BROWN_M)
ell(210, 673, 22, 10, (146, 107, 66))
ell(258, 674, 18, 9, (146, 107, 66))
ell(150, 696, 28, 8, (79, 55, 34))
ell(318, 697, 24, 7, (79, 55, 34))

# 埋头劳作的深色推粪蜣螂
ell(238, 676, 10, 8, (28, 24, 21))
ell(238, 672, 5, 5, (58, 46, 34))
d.arc([R(226), R(664), R(250), R(684)], 200, 330, fill=C((62, 48, 36)), width=R(1.5))

# 循味赶来的红甲虫群
beetle(320, 610, 6.5)
beetle(350, 648, 6.5)
beetle(405, 594, 7.5)
beetle(466, 630, 7)
beetle(526, 576, 8)
beetle(588, 609, 7.5)
beetle(625, 660, 7)

# 细小的飞行轨迹点
for t in np.linspace(0.05, 0.95, 9):
    px = 312 + (640 - 300) * t
    py = 620 - 36 * math.sin(math.pi * t * 0.85) - 14 * math.sin(math.pi * t * 2.1)
    if 636 <= px + 20 <= 660:
        continue
    ell(px, py, 1.7, 1.7, (163, 153, 137))

# 穴小鸮：圆胖身体
CX = 698
rrect(CX - 47, 604, CX + 47, G + 2, 28, OWL_BROWN)
rrect(CX - 26, 618, CX + 26, G + 1, 22, CREAM)

# 腹部细横纹
for sy, sx0, sx1 in [(642, CX - 16, CX + 16), (662, CX - 14, CX + 14), (682, CX - 16, CX + 16)]:
    d.line([R(sx0), R(sy), R(sx1), R(sy)], fill=C((174, 143, 99)), width=R(1.3))

# 头与两侧收拢的翼羽
ell(CX, 566, 58, 55, BROWN_L)
rrect(CX - 49, 662, CX - 30, G, 12, OWL_EDGE)
rrect(CX + 30, 662, CX + 49, G, 12, OWL_EDGE)

# 白色面盘与一双圆眼
ell(CX, 574, 43, 42, FACE)
for ex in (CX - 25, CX + 25):
    ell(ex, 569, 13.5, 13.5, (22, 19, 17))
    ell(ex, 569, 10.5, 10.5, GOLD)
ell(CX - 25 - 2, 569, 5, 5, (20, 17, 15))
ell(CX + 25 - 2, 569, 5, 5, (20, 17, 15))

# 喙与脚
ell(CX, 598, 4.6, 6.4, (116, 82, 48))
for fx in (CX - 18, CX + 18):
    d.line([R(fx), R(G - 6), R(fx), R(G + 3)], fill=(156, 126, 86), width=R(2.2))

# 洞口边稀疏干草
for gx, gh in [(760, 8), (786, 13), (822, 6), (858, 11), (300, 5), (138, 9)]:
    d.line([R(gx), R(G + 1), R(gx - 2), R(G - gh)], fill=C(GRASS), width=R(1.4))
    d.line([R(gx + 1), R(G + 1), R(gx + 3), R(G - gh + 3)], fill=C(GRASS), width=R(1.4))

sf.composite(im)

# 红色方形编辑记号
red_mark = Image.fromarray(sf.layer(), "RGBA")
drm = ImageDraw.Draw(red_mark)
drm.rectangle([R(90), R(143), R(202), R(156)], fill=C(RED))
sf.composite(red_mark)

# 图与正文之间的分隔细线
hline(788, 90, 910, (150, 145, 136), 1.0)

# ===== 文字层 =====

# 顶部元信息
sf.serial(90, 70, SERIAL, family="cjk-sc", size=29, fill=INK, role="meta", bold=True)
sf.datestamp(910, 70, DATE, family="cjk-sc", size=29, fill=INK, role="meta", anchor="rt", bold=True)

# 金句标题
sf.text(90, 212, QUOTE, family="cjk-sc", size=62, fill=INK, role="quote",
        anchor="lt", max_w=690, line_gap=0.35, bold=True)

# 提前检查不同折行宽度下冷知识段落的末行宽度，
# 选一个不会让末行只剩“例。”两个字的配置，再交给 sf.text 绘制。
best_cfg = None
fallback_cfg = None
for sz in (31, 30, 29):
    for mw in range(700, 478, -2):
        lines = sf.wrap(FACT, "cjk-sc", sz, mw)
        if not lines or len(lines) > 9:
            continue
        last_w = sf.measure(lines[-1], "cjk-sc", sz)[0]
        ratio = last_w / mw
        if fallback_cfg is None or ratio > fallback_cfg[0]:
            fallback_cfg = (ratio, sz, mw)
        if ratio >= 0.5:
            best_cfg = (ratio, sz, mw)
            break
    if best_cfg is not None:
        break
if best_cfg is None:
    best_cfg = fallback_cfg

_, BODY_SZ, BODY_MW = best_cfg

# 冷知识正文
sf.text(90, 850, FACT, family="cjk-sc", size=BODY_SZ, fill=(40, 36, 31),
        role="body", anchor="lt", max_w=BODY_MW, line_gap=0.56)

sf.save(OUT_PATH)
