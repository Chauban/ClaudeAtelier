from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw

# 画布尺寸（竖版，缩短高度以优化上下平衡）
W, H = 900, 1400
sf = Surface(W, H, scale=2, bg=(253, 246, 236))

# ---- 孟菲斯撞色 ----
PINK   = (255, 94, 142, 255)
YELLOW = (255, 217, 61, 255)
TEAL   = (78, 205, 196, 255)
CORAL  = (255, 107, 107, 255)
MINT   = (168, 230, 207, 255)
BLACK  = (26, 26, 46, 255)
WHITE  = (255, 255, 255, 255)

DEEP_RGB = (44, 62, 80)
FACT_RGB = (62, 62, 62)
TRAN_RGB = (85, 85, 85)   # 翻译文字稍浅

# ---- 装饰层（先画） ----
W2, H2 = W * 2, H * 2
deco = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)

def L(x):
    return int(x * 2)

def T(y):
    return int(y * 2)

# 顶部色块带（保持位置不变）
d.rectangle([L(0), T(0), L(370), T(190)], fill=PINK)
d.rectangle([L(370), T(20), L(670), T(210)], fill=YELLOW)
d.rectangle([L(670), T(0), L(900), T(190)], fill=TEAL)

# 黑色锯齿分隔
for i in range(5):
    x0 = 370 + i * 50
    d.polygon([(L(x0), T(20)), (L(x0+50), T(0)),
               (L(x0+50), T(190)), (L(x0), T(210))], fill=BLACK)

# 黄色块波点
for i in range(3):
    cx = 435 + i * 60
    d.ellipse([L(cx-15), T(85-15), L(cx+15), T(85+15)], fill=BLACK)

# 青色块白圆环
d.ellipse([L(730), T(50), L(810), T(130)], outline=WHITE, width=L(4))

# 粉色块白三角
d.polygon([(L(200), T(60)), (L(260), T(60)), (L(230), T(120))], fill=WHITE)

# 左侧几何点缀
d.polygon([(L(40), T(260)), (L(160), T(260)), (L(40), T(410))], fill=PINK)
d.ellipse([L(70), T(450), L(180), T(560)], fill=YELLOW)

# 右侧几何点缀（调整位置，避免与文字冲突）
d.ellipse([L(770), T(270), L(845), T(345)], outline=CORAL, width=L(5))
d.ellipse([L(810), T(600), L(875), T(665)], fill=MINT)

# 半透明黏液房子（移到左下方，避开文字区域）
house_cx, house_cy, house_r = 170, 930, 65
d.ellipse([L(house_cx-house_r), T(house_cy-house_r),
           L(house_cx+house_r), T(house_cy+house_r)],
          fill=(78, 205, 196, 90), outline=(78, 205, 196, 200), width=L(3))

# 房子内小生物（深色椭圆 + 尾巴）
d.ellipse([L(house_cx-22), T(house_cy-14), L(house_cx-4), T(house_cy+6)],
          fill=(44, 62, 80, 220))
d.line([L(house_cx-22), T(house_cy-6),
        L(house_cx-52), T(house_cy-18)],
       fill=(44, 62, 80, 220), width=L(4))

# 下沉虚线（从房子底部向下延伸）
for yy in range(1000, 1250, 60):
    d.line([L(house_cx), T(yy), L(house_cx), T(yy+25)],
           fill=(44, 62, 80, 80), width=L(3))

# 底部波浪（位置下移到底部，不影响文字）
for i in range(0, 820, 80):
    d.polygon([(L(i), T(1280)), (L(i+40), T(1230)), (L(i+80), T(1280))],
              fill=TEAL if (i//80) % 2 == 0 else PINK)
for i in range(80, 820, 80):
    d.polygon([(L(i), T(1340)), (L(i+40), T(1290)), (L(i+80), T(1340))],
              fill=YELLOW)

sf.composite(np.array(deco))

# ---- 安全区 ----
sf.frame(40, 30, 820, 1330)

# ---- 流水号 / 日期（顶部不变） ----
sf.serial(50, 75, SERIAL,
          family="sans", size=22, fill=DEEP_RGB,
          bold=True, role="meta", anchor="lt")
sf.datestamp(850, 70, DATE,
             family="sans", size=20, fill=DEEP_RGB,
             bold=True, role="meta", anchor="rt")

# ---- 金句（动态行距，避免重叠） ----
quote_x = 150
quote_y = 280
quote_lines = sf.wrap(QUOTE, "cjk-jp", 48, max_w=590, bold=True)
for line in quote_lines:
    b = sf.text(quote_x, quote_y, line,
                family="cjk-jp", size=48, fill=DEEP_RGB,
                anchor="lt", role="quote", bold=True)
    quote_y = b.bottom + 8          # 额外留白，避免紧贴

# ---- 冷知识：拆分日文原文与中文翻译 ----
fact_raw = FACT.strip()
# 找到最后一个全角左括号，作为翻译开始的标记
idx = fact_raw.rfind("（")
if idx != -1:
    fact_ja = fact_raw[:idx].strip()
    fact_zh = fact_raw[idx+1:].rstrip("）").strip()
else:
    fact_ja = fact_raw
    fact_zh = ""

# 日文原文（使用日文字体，body 字号）
body_y = quote_y + 20
box_ja = sf.text(80, body_y, fact_ja,
                 family="cjk-jp", size=28, fill=FACT_RGB,
                 anchor="lt", role="body", bold=False,
                 max_w=600, line_gap=0.45)

# 中文翻译（使用简体中文字体，较小字号，作为 meta，放在原文下方）
if fact_zh:
    trans_y = box_ja.bottom + 16
    sf.text(80, trans_y, fact_zh,
            family="cjk-sc", size=24, fill=TRAN_RGB,
            anchor="lt", role="meta", bold=False,
            max_w=600, line_gap=0.4)

# ---- 保存 ----
sf.save(OUT_PATH)
