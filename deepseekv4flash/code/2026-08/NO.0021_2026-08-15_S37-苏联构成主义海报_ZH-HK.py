from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw

W, H = 1000, 1780
sf = Surface(W, H, scale=2, bg=(243, 239, 230))
sf.frame(70, 40, 860, 1700)

S = 2
def P(v):
    return int(round(v * S))

fact_lines = sf.wrap(FACT, "cjk-hk", 32, max_w=720)
fact_top = 1270

# ---------- Tier 2 背景与装饰 ----------

# 1. 浅灰阴影线（与主斜带平行）
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
for y0 in range(220, 1150, 24):
    d.line([P(0), P(y0), P(1000), P(y0 - 350)], fill=(214, 208, 194, 255), width=P(2))
sf.composite(img, opacity=0.7)

# 2. 右上大红圆 + 黑点 + 白环
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.ellipse([P(600), P(-200), P(1200), P(400)], fill=(212, 37, 46, 255))
d.ellipse([P(872), P(72), P(928), P(128)], fill=(26, 26, 26, 255))
d.ellipse([P(810), P(10), P(990), P(190)], outline=(255, 255, 255, 255), width=P(5))
sf.composite(img)

# 3. 主斜黑带 + 内部白/红线
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.polygon([P(0), P(1062), P(1000), P(712), P(1000), P(828), P(0), P(1178)], fill=(26, 26, 26, 255))
d.line([P(0), P(1088), P(1000), P(738)], fill=(243, 239, 230, 255), width=P(4))
d.line([P(0), P(1144), P(1000), P(794)], fill=(212, 37, 46, 255), width=P(4))
sf.composite(img)

# 4. 速度线
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.line([P(0), P(950), P(700), P(705)], fill=(26, 26, 26, 255), width=P(3))
d.line([P(0), P(994), P(500), P(819)], fill=(26, 26, 26, 255), width=P(3))
sf.composite(img)

# 5. 左上黑块 + 红三角
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rectangle([P(0), P(0), P(250), P(112)], fill=(26, 26, 26, 255))
d.polygon([P(250), P(0), P(250), P(40), P(290), P(0)], fill=(212, 37, 46, 255))
sf.composite(img)

# 6. QUOTE 题花红条
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rectangle([P(90), P(216), P(150), P(226)], fill=(212, 37, 46, 255))
sf.composite(img)

# 7. QUOTE 第三行红色强调块
red_x = 62
red_w = int(sf.measure("不如企起身行。", "cjk-hk", 84, bold=True)[0]) + 56
red_y = 540
red_h = 140
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rectangle([P(red_x), P(red_y), P(red_x + red_w), P(red_y + red_h)], fill=(212, 37, 46, 255))
sf.composite(img)

# 8. 黑色圆环（红块右侧）
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.ellipse([P(752), P(522), P(828), P(598)], outline=(26, 26, 26, 255), width=P(5))
sf.composite(img)

# 9. FACT 红色引用竖线
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rectangle([P(112), P(fact_top - 12), P(122), P(fact_top + 240)], fill=(212, 37, 46, 255))
sf.composite(img)

# 10. 底部印刷标记
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.line([P(70), P(1580), P(930), P(1580)], fill=(26, 26, 26, 255), width=P(3))
d.rectangle([P(70), P(1600), P(110), P(1640)], fill=(26, 26, 26, 255))
d.rectangle([P(870), P(1600), P(930), P(1660)], fill=(212, 37, 46, 255))
d.ellipse([P(486), P(1586), P(514), P(1614)], fill=(212, 37, 46, 255))
sf.composite(img)

# ---------- Tier 1 文字 ----------
sf.serial(70, 60, SERIAL, family="sans", size=28, fill=(255, 255, 255), anchor="lm", bold=True, role="meta")
sf.datestamp(920, 310, DATE, family="sans", size=24, fill=(255, 255, 255), anchor="rm", bold=True, role="meta")

sf.text(90, 250, "人一世物一世，", family="cjk-hk", size=72, fill=(26, 26, 26), anchor="lt", role="quote", bold=True)
sf.text(90, 380, "與其坐喺度等，", family="cjk-hk", size=72, fill=(26, 26, 26), anchor="lt", role="quote", bold=True)
sf.text(90, red_y + red_h // 2, "不如企起身行。", family="cjk-hk", size=84, fill=(255, 255, 255), anchor="lm", role="title", bold=True)

fy = fact_top
for line in fact_lines:
    box = sf.text(142, fy, line, family="cjk-hk", size=32, fill=(26, 26, 26), anchor="lt", role="body", max_w=720)
    fy = box.bottom + 30

sf.save(OUT_PATH)
