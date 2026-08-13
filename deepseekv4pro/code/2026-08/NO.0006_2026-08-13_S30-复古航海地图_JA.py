from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math

W = 1000
H = 1860
sf = Surface(W, H, scale=2, bg=(216, 193, 156))

# ---- 文字拆分（日文原文 + 中文翻译） ----
quote_ja, quote_zh_raw = QUOTE.split("（", 1)
quote_zh = "（" + quote_zh_raw

fact_ja, fact_zh_raw = FACT.split("（", 1)
fact_zh = "（" + fact_zh_raw

# ---- 排版常量 ----
content_w = 800
left_x = 90
center_x = 500

Q_SIZE = 40
QZ_SIZE = 25
F_SIZE = 30
FZ_SIZE = 25
SERIAL_SIZE = 23

INK = (55, 38, 22)
INK_SOFT = (95, 70, 38)
PARCHMENT = (230, 202, 150, 255)
PANEL_OUTLINE = (105, 72, 36, 255)

# 日文正文用包含汉字/假名字形的 CJK 字体，避开地区字形误判
JP_FONT = "cjk-tc"

GAN = 0.5
GEN = 0.35

# ---- 坐标规划（以实际测量留足余量，避免重叠） ----
top_q = 440
qzh_y = 604
divider_y = 677
fact_top = 710
fzh_y = 968
serial_y = 1642

# ---- 背景：牛皮纸做旧 ----
rng = np.random.default_rng(20260813)
lay = sf.layer()
hh, ww = lay.shape[:2]
yy = np.linspace(0, 1, hh)[:, None]
xx = np.linspace(0, 1, ww)[None, :]

lay[..., 0] = 232
lay[..., 1] = 210
lay[..., 2] = 164
lay[..., 3] = 255

dist = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) / np.sqrt(0.5)
v = 0.72 + 0.45 * dist
for i in range(3):
    lay[..., i] = np.clip(lay[..., i] * v, 0, 255).astype(np.uint8)

noise = rng.normal(0, 6, (hh, ww)).astype(np.int16)
for i in range(3):
    lay[..., i] = np.clip(lay[..., i].astype(np.int16) + noise, 0, 255).astype(np.uint8)

grain = (np.sin(yy * 160) * 4).astype(np.int16)
for i in range(3):
    lay[..., i] = np.clip(lay[..., i].astype(np.int16) + grain, 0, 255).astype(np.uint8)

sf.composite(lay, mode="normal", opacity=1.0)

# 污渍
st = sf.layer()
st_img = Image.fromarray(st, "RGBA")
sd = ImageDraw.Draw(st_img, "RGBA")
for _ in range(14):
    x = int(rng.integers(0, ww))
    y = int(rng.integers(0, hh))
    r = int(rng.integers(80, 240))
    a = int(rng.integers(18, 45))
    sd.ellipse([x - r, y - r, x + r, y + r], fill=(85, 58, 26, a))
st_img = st_img.filter(ImageFilter.GaussianBlur(70))
sf.composite(st_img, mode="multiply", opacity=0.65)

# ---- 航海地图线稿层 ----
map_layer = sf.layer()
map_img = Image.fromarray(map_layer, "RGBA")
draw = ImageDraw.Draw(map_img, "RGBA")

def P(x, y):
    return (int(round(x * 2)), int(round(y * 2)))

def Rv(v):
    return int(round(v * 2))

# 边框
draw.rectangle([P(52, 52), P(948, 1808)], outline=(70, 40, 20, 255), width=Rv(3))
draw.rectangle([P(66, 66), P(934, 1794)], outline=(70, 40, 20, 170), width=Rv(1.5))

# 四角装饰
for cx, cy in [(52, 52), (948, 52), (52, 1808), (948, 1808)]:
    draw.ellipse([P(cx - 18, cy - 18), P(cx + 18, cy + 18)],
                 fill=(232, 210, 164, 255), outline=(70, 40, 20, 220), width=Rv(2))
    draw.ellipse([P(cx - 7, cy - 7), P(cx + 7, cy + 7)], fill=(155, 58, 40, 255))

# 罗盘（顶部，放射线限制在 300px 内，不穿过文字区）
compass_center = (500, 280)
for deg in range(0, 360, 15):
    rad = math.radians(deg)
    ex = compass_center[0] + 300 * math.cos(rad)
    ey = compass_center[1] + 300 * math.sin(rad)
    draw.line([P(compass_center[0], compass_center[1]), P(ex, ey)],
              fill=(95, 67, 38, 70), width=Rv(1))

for rlog in (120, 180, 250):
    draw.ellipse(
        [P(compass_center[0] - rlog, compass_center[1] - rlog),
         P(compass_center[0] + rlog, compass_center[1] + rlog)],
        outline=(95, 67, 38, 65), width=Rv(1))

# 八芒星罗盘
Rstar = 100
rstar = 42
pts = []
for i in range(16):
    ang = -90 + i * 22.5
    rad = Rstar if i % 2 == 0 else rstar
    pts.append(P(compass_center[0] + rad * math.cos(math.radians(ang)),
                 compass_center[1] + rad * math.sin(math.radians(ang))))
draw.polygon(pts, fill=(72, 42, 20, 255))

R2 = 54
r2 = 22
pts2 = []
for i in range(8):
    ang = -90 + i * 45
    rad = R2 if i % 2 == 0 else r2
    pts2.append(P(compass_center[0] + rad * math.cos(math.radians(ang)),
                  compass_center[1] + rad * math.sin(math.radians(ang))))
draw.polygon(pts2, fill=(155, 58, 40, 255))

draw.ellipse([P(compass_center[0] - 12, compass_center[1] - 12),
              P(compass_center[0] + 12, compass_center[1] + 12)],
             fill=(232, 210, 164, 255), outline=(72, 42, 20, 255), width=Rv(2.5))

# 底部小帆船装饰
ship_cx, ship_cy = 720, 1420
draw.polygon([P(ship_cx - 80, ship_cy), P(ship_cx + 80, ship_cy),
              P(ship_cx + 55, ship_cy + 30), P(ship_cx - 55, ship_cy + 30)],
             fill=(70, 40, 20, 220))
for mx in (-40, 0, 40):
    draw.line([P(ship_cx + mx, ship_cy), P(ship_cx + mx, ship_cy - 110)],
              fill=(70, 40, 20, 230), width=Rv(2.5))
draw.polygon([P(ship_cx - 40, ship_cy - 104), P(ship_cx - 8, ship_cy - 50),
              P(ship_cx - 40, ship_cy - 20)], fill=(155, 58, 40, 230))
draw.polygon([P(ship_cx, ship_cy - 104), P(ship_cx + 32, ship_cy - 50),
              P(ship_cx, ship_cy - 20)], fill=(90, 67, 38, 230))
draw.polygon([P(ship_cx + 40, ship_cy - 104), P(ship_cx + 70, ship_cy - 50),
              P(ship_cx + 40, ship_cy - 20)], fill=(90, 67, 38, 230))

# 底部波浪
for idx, y0 in enumerate([1610, 1660, 1710]):
    pts = []
    for x in range(60, 940, 15):
        y = y0 + 8 * math.sin(2 * math.pi * (x - 60) / 180 + idx)
        pts.append(P(x, y))
    draw.line(pts, fill=(80, 60, 30, 120), width=Rv(1))

# 底部中央编号盒
draw.rounded_rectangle([P(290, 1600), P(710, 1735)], radius=Rv(20),
                       fill=(232, 210, 164, 245), outline=(70, 40, 20, 220), width=Rv(2))
draw.rounded_rectangle([P(300, 1610), P(700, 1725)], radius=Rv(14),
                       outline=(70, 40, 20, 110), width=Rv(1))

sf.composite(map_img, mode="normal", opacity=0.92)

# ---- 干净羊皮纸标签层（垫在文字区下方，遮住装饰） ----
panel_layer = sf.layer()
panel_img = Image.fromarray(panel_layer, "RGBA")
pd = ImageDraw.Draw(panel_img, "RGBA")

# 金句整块标签（覆盖日文 + 中文翻译）
pd.rounded_rectangle([P(80, 408), P(920, 662)], radius=Rv(24),
                     fill=PARCHMENT, outline=PANEL_OUTLINE, width=Rv(2))

# 冷知识整块标签（覆盖日文正文 + 中文翻译）
pd.rounded_rectangle([P(76, 692), P(924, 1135)], radius=Rv(24),
                     fill=PARCHMENT, outline=PANEL_OUTLINE, width=Rv(2))

# 两标签之间的分隔线
pd.line([P(180, divider_y), P(430, divider_y)], fill=(75, 48, 26, 210), width=Rv(1.5))
pd.line([P(570, divider_y), P(820, divider_y)], fill=(75, 48, 26, 210), width=Rv(1.5))
pd.polygon([P(500, divider_y - 7), P(509, divider_y),
            P(500, divider_y + 7), P(491, divider_y)], fill=(155, 58, 40, 255))

sf.composite(panel_img, mode="normal", opacity=1.0)

# ---- 文字安全区 ----
sf.frame(70, 90, 860, 1710)

# 金句日文原文
box_q = sf.text(center_x, top_q, quote_ja,
                family=JP_FONT, size=Q_SIZE, fill=INK,
                anchor="mt", role="quote", bold=True,
                max_w=content_w, line_gap=GAN)

# 金句中文翻译
box_qz = sf.text(center_x, qzh_y, quote_zh,
                 family="cjk-sc", size=QZ_SIZE, fill=INK_SOFT,
                 anchor="mt", role="meta",
                 max_w=content_w, line_gap=GEN)

# 冷知识日文正文
box_f = sf.text(left_x, fact_top, fact_ja,
                family=JP_FONT, size=F_SIZE, fill=INK,
                anchor="lt", role="body",
                max_w=content_w, line_gap=0.45)

# 冷知识中文翻译
box_fz = sf.text(left_x, fzh_y, fact_zh,
                 family="cjk-sc", size=FZ_SIZE, fill=INK_SOFT,
                 anchor="lt", role="meta",
                 max_w=content_w, line_gap=GEN)

# 流水号与日期
sf.serial(330, serial_y, SERIAL, family="serif", size=SERIAL_SIZE,
          fill=INK, anchor="lt", role="meta")
sf.datestamp(560, serial_y, DATE, family="serif", size=SERIAL_SIZE,
             fill=INK, anchor="lt", role="meta")

sf.save(OUT_PATH)
