from atelier_canvas import Surface
from PIL import Image, ImageDraw

W, H = 1200, 1360
F = 2
RW, RH = W * F, H * F

sf = Surface(W, H, scale=2, bg=(248, 248, 248))
sf.frame(110, 70, 980, 1180)

# 背景: 淡网格线
img = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

for gx in (200, 400, 600, 800, 1000):
    d.line([(gx * F, 150 * F), (gx * F, 1240 * F)], fill=(235, 235, 235, 255), width=1)

# 顶部标题栏线
d.line([(110 * F, 150 * F), (1090 * F, 150 * F)], fill=(18, 18, 18, 255), width=4)
d.rectangle([110 * F, 172 * F, 136 * F, 200 * F], fill=(220, 30, 40, 255))

# 引用与正文之间的分隔线
d.line([(110 * F, 560 * F), (1090 * F, 560 * F)], fill=(18, 18, 18, 255), width=2)
d.rectangle([110 * F, 584 * F, 128 * F, 600 * F], fill=(220, 30, 40, 255))

# 右侧图表(管风琴音管柱状意象)
axis_x = 780
base_y = 1200
d.line([(axis_x * F, 600 * F), (axis_x * F, base_y * F)], fill=(18, 18, 18, 255), width=2)
for gy in range(600, 1201, 100):
    d.line([(axis_x * F, gy * F), (1090 * F, gy * F)], fill=(226, 226, 226, 255), width=1)
d.line([(axis_x * F, base_y * F), (1090 * F, base_y * F)], fill=(18, 18, 18, 255), width=3)

bars = [(800, 150), (840, 260), (880, 110), (920, 330), (960, 190), (1000, 280), (1040, 220)]
for bx, bh in bars:
    d.rectangle([bx * F, (base_y - bh) * F, (bx + 30) * F, base_y * F], fill=(18, 18, 18, 255))

# 红色圆点(低频震动的视觉锚点)
cx, cy, rad = 1080, 780, 40
d.ellipse([(cx - rad) * F, (cy - rad) * F, (cx + rad) * F, (cy + rad) * F], fill=(220, 30, 40, 255))

# 底部深色色带
band_y = 1280
d.rectangle([0, band_y * F, RW - 1, RH - 1], fill=(18, 18, 18, 255))
d.rectangle([110 * F, (band_y + 30) * F, 136 * F, (band_y + 58) * F], fill=(220, 30, 40, 255))

sf.composite(img)

# 顶部信息
sf.datestamp(110, 80, DATE, family="sans", size=28, fill=(18, 18, 18), anchor="lt")
sf.serial(1090, 80, SERIAL, family="sans", size=28, fill=(215, 20, 35), anchor="rt", bold=True)

# 主金句 —— 大号粗体, 瑞士网格的视觉主体
qy = 230
for line in sf.wrap(QUOTE, "cjk-hk", 100, 980, bold=True):
    box = sf.text(110, qy, line, family="cjk-hk", size=100, fill=(18, 18, 18), anchor="lt", role="quote", bold=True, max_w=980)
    qy = box.bottom + 8

# 冷知识正文 —— 左栏, 与右侧音管柱状图并置
fy = 620
for line in sf.wrap(FACT, "cjk-hk", 32, 560):
    box = sf.text(136, fy, line, family="cjk-hk", size=32, fill=(36, 36, 36), anchor="lt", role="body", max_w=560)
    fy = box.bottom + 8

sf.save(OUT_PATH)
