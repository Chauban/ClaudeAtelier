from atelier_canvas import Surface
from PIL import Image, ImageDraw

W, H = 1000, 1060
sf = Surface(W, H, scale=2, bg=(248, 247, 244))

# ---- 装饰层：小方块、细线、底部实心圆 ----
dec = sf.layer()
img = Image.fromarray(dec, 'RGBA')
d = ImageDraw.Draw(img)

# 编号前的小方块
d.rectangle([(70 * 2, 92 * 2), (82 * 2, 104 * 2)], fill=(26, 26, 25, 255))
# 顶部分隔细线
d.line([(70 * 2, 142 * 2), (930 * 2, 142 * 2)], fill=(26, 26, 25, 255), width=3)
# 底部右侧留白区实心圆，平衡下半部空白
cx, cy, r = 880, 996, 36
d.ellipse([(cx - r) * 2, (cy - r) * 2, (cx + r) * 2, (cy + r) * 2], fill=(26, 26, 25, 255))

sf.composite(img, mode='normal')

# ---- 文字安全区 ----
sf.frame(70, 80, 860, 900)

INK = (42, 42, 40)
QUOTE_INK = (26, 26, 25)
FACT_INK = (74, 74, 72)

sf.serial(94, 92, SERIAL, family='mono', size=20, fill=INK, anchor='lt', role='meta')
sf.datestamp(930, 92, DATE, family='mono', size=20, fill=INK, anchor='rt', role='meta')

box_q = sf.text(70, 280, QUOTE, family='cjk-hk', size=58, fill=QUOTE_INK,
                anchor='lt', role='quote', max_w=860, line_gap=0.65)

sf.text(70, 700, FACT, family='cjk-hk', size=31, fill=FACT_INK,
        anchor='lt', role='body', max_w=840, line_gap=0.56)

sf.save(OUT_PATH)
