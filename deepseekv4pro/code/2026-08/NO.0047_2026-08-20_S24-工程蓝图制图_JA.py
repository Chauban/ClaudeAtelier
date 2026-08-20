from atelier_canvas import Surface
from PIL import Image, ImageDraw
import numpy as np

def split_quote(q):
    idx = q.find('（')
    if idx == -1:
        return q, ''
    end = q.rfind('）')
    return q[:idx], q[idx+1:end]

def split_fact(f):
    idx = f.find('（中文：')
    if idx == -1:
        return f, ''
    end = f.rfind('）')
    return f[:idx], f[idx+4:end]

quote_jp, quote_cn = split_quote(QUOTE)
fact_jp, fact_cn = split_fact(FACT)

w = 1000
h = 1600
sf = Surface(w, h, scale=2, bg=(12, 34, 58))

sf.frame(60, 65, 880, 1470)

# 背景底层
base = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
bd = ImageDraw.Draw(base)

# 主网格
step = 40 * 2
for x in range(0, sf.W, step):
    bd.line([(x, 0), (x, sf.H)], fill=(165, 200, 240, 22), width=1)
for y in range(0, sf.H, step):
    bd.line([(0, y), (sf.W, y)], fill=(165, 200, 240, 22), width=1)

# 次级网格
step2 = 10 * 2
for x in range(0, sf.W, step2):
    bd.line([(x, 0), (x, sf.H)], fill=(150, 190, 230, 8), width=1)
for y in range(0, sf.H, step2):
    bd.line([(0, y), (sf.W, y)], fill=(150, 190, 230, 8), width=1)

# 外框
m = 24 * 2
bd.rectangle([m, m, sf.W-m, sf.H-m], outline=(245, 248, 255, 255), width=3)
bd.rectangle([m+10, m+10, sf.W-m-10, sf.H-m-10], outline=(190, 210, 240, 170), width=1)

# 角标括号
b = 24 * 2
white = (255, 255, 255, 255)
bd.line([(m, m+b), (m, m), (m+b, m)], fill=white, width=4)
bd.line([(sf.W-m-b, m), (sf.W-m, m), (sf.W-m, m+b)], fill=white, width=4)
bd.line([(m, sf.H-m-b), (m, sf.H-m), (m+b, sf.H-m)], fill=white, width=4)
bd.line([(sf.W-m-b, sf.H-m), (sf.W-m, sf.H-m), (sf.W-m, sf.H-m-b)], fill=white, width=4)

# 中央分隔线（quote 与 fact 之间）
sep_y = 432 * 2
bd.line([(80*2, sep_y), (920*2, sep_y)], fill=(190, 210, 240, 200), width=2)
# 分隔线两端箭头
bd.polygon([(80*2, sep_y), (80*2+12, sep_y-6), (80*2+12, sep_y+6)], fill=(215, 230, 250, 255))
bd.polygon([(920*2, sep_y), (920*2-12, sep_y-6), (920*2-12, sep_y+6)], fill=(215, 230, 250, 255))

# 右下角标题栏（更详细一点的蓝图标题栏）
tb_w = 300 * 2
tb_h = 76 * 2
tb_x = 660 * 2
tb_y = 1456 * 2
bd.rectangle([tb_x, tb_y, tb_x+tb_w, tb_y+tb_h], outline=(240, 245, 255, 255), width=2)
# 内部分割线
bd.line([(tb_x+150*2, tb_y), (tb_x+150*2, tb_y+tb_h)], fill=(240, 245, 255, 180), width=1)
bd.line([(tb_x, tb_y+38*2), (tb_x+tb_w, tb_y+38*2)], fill=(240, 245, 255, 150), width=1)

# 左下角与右上的装饰性尺寸标注
def dim_horizontal(y_logical, x1_logical, x2_logical):
    y = y_logical * 2
    x1 = x1_logical * 2
    x2 = x2_logical * 2
    bd.line([(x1, y), (x2, y)], fill=(180, 200, 230, 200), width=1)
    bd.line([(x1, y-8), (x1, y+8)], fill=(180, 200, 230, 200), width=1)
    bd.line([(x2, y-8), (x2, y+8)], fill=(180, 200, 230, 200), width=1)
    bd.polygon([(x1-6, y-4), (x1-6, y+4), (x1, y)], fill=(180, 200, 230, 255))
    bd.polygon([(x2+6, y-4), (x2+6, y+4), (x2, y)], fill=(180, 200, 230, 255))

dim_horizontal(1350, 90, 910)   # 下部横向尺寸线
dim_horizontal(100, 90, 300)    # 上部横向尺寸线

# 右上角圆形标记
cx = 860 * 2
cy = 90 * 2
bd.ellipse([cx-18, cy-18, cx+18, cy+18], outline=(230, 240, 255, 255), width=2)
bd.line([(cx-24, cy), (cx+24, cy)], fill=(230, 240, 255, 220), width=1)
bd.line([(cx, cy-24), (cx, cy+24)], fill=(230, 240, 255, 220), width=1)

# 左下角角度弧线
bd.arc([(90*2-12), (1390*2-12), (90*2+48), (1390*2+48)], start=0, end=90, fill=(230, 240, 255, 200), width=2)

sf.composite(base, mode="normal", opacity=1.0)

# ---- 文字 ----
x_text = 80

# 金句（日文原文，按检查器要求改用 cjk-tc 避免繁体字形错配）
y = 130
box1 = sf.text(x_text, y, quote_jp, family="cjk-tc", size=34, fill=(242, 246, 255), anchor="lt", role="quote", max_w=640, line_gap=0.5)
y = box1.bottom + 16
box2 = sf.text(x_text, y, quote_cn, family="cjk-sc", size=28, fill=(205, 220, 245), anchor="lt", role="quote", max_w=640, line_gap=0.35)

# 冷知识（日文原文用 cjk-tc，中文翻译用 cjk-sc）
y = 480
box3 = sf.text(x_text, y, fact_jp, family="cjk-tc", size=28, fill=(228, 238, 252), anchor="lt", role="body", max_w=840, line_gap=0.4)
y = box3.bottom + 18
box4 = sf.text(x_text, y, fact_cn, family="cjk-sc", size=28, fill=(198, 216, 238), anchor="lt", role="body", max_w=840, line_gap=0.35)

# 流水号与日期（蓝图标题栏内）
sf.serial(675, 1475, SERIAL, family="mono", size=17, fill=(215, 225, 255), anchor="lt", role="meta")
sf.datestamp(835, 1475, DATE, family="mono", size=17, fill=(215, 225, 255), anchor="lt", role="meta")

sf.save(OUT_PATH)
