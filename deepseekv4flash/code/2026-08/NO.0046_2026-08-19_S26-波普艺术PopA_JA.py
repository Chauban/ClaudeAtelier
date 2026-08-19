from atelier_canvas import Surface
import math
import numpy as np
from PIL import Image, ImageDraw

W, H = 1000, 2100
sf = Surface(W, H, scale=2, bg=(255, 222, 0))
sf.frame(50, 50, 900, 2000)

QUOTE_ZH = "这首曲子奏完之时，开始它的人和听过它的人，都已不在世上。可声音仍在继续——像一封寄往未来的信。"
FACT_ZH = "约翰·凯奇的管风琴曲《ASLSP＝越慢越好》于2001年9月5日在德国哈尔伯施塔特的教堂开演，预定在639年后的2640年9月5日结束，是全世界历时最长的音乐会之一。最初17个月管子不发声，之后琴键由沙袋压住，一个和弦能持续数年。"

P = lambda v: int(v * 2)

img = Image.new("RGBA", (P(W), P(H)), (0, 0, 0, 0))
d = ImageDraw.Draw(img)


def dot_grid(dr, x0, y0, x1, y1, r, col, spacing):
    row = 0
    yy = y0
    while yy < y1:
        xx = x0 + (spacing / 2 if row % 2 else 0)
        while xx < x1:
            dr.ellipse([P(xx - r), P(yy - r), P(xx + r), P(yy + r)], fill=col + (255,))
            xx += spacing
        yy += spacing
        row += 1


def sparkle(dr, cx0, cy0, r, col):
    pts = []
    for i in range(8):
        a = i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.35
        pts.append((P(cx0 + rr * math.cos(a)), P(cy0 + rr * math.sin(a))))
    dr.polygon(pts, fill=col + (255,), outline=(0, 0, 0, 255))


def draw_note(dr, x, y, s, col):
    dr.ellipse([P(x - s), P(y - s), P(x + s), P(y + s)], fill=col + (255,), outline=(0, 0, 0, 255), width=6)
    dr.line([P(x + s * 0.8), P(y - s * 0.6), P(x + s * 0.8), P(y - s * 2.0)], fill=(0, 0, 0, 255), width=8)
    dr.line([P(x + s * 0.8), P(y - s * 2.0), P(x + s * 1.7), P(y - s * 1.3)], fill=(0, 0, 0, 255), width=6)
    dr.line([P(x + s * 1.7), P(y - s * 1.3), P(x + s * 1.4), P(y - s * 0.8)], fill=(0, 0, 0, 255), width=6)


# 顶部黑色刊头条
d.rectangle([0, P(64), P(W), P(150)], fill=(25, 25, 25, 255))
d.rectangle([P(440), P(84), P(478), P(130)], fill=(255, 46, 147, 255))
d.rectangle([P(486), P(84), P(524), P(130)], fill=(0, 208, 208, 255))
d.rectangle([P(532), P(84), P(570), P(130)], fill=(255, 210, 0, 255))

# 品红半色调网点带
dot_grid(d, 0, 156, W, 204, 8, (255, 46, 147), 28)

# 管风琴管道
pipe_cols = [(0, 208, 208), (255, 110, 180), (200, 200, 215), (255, 210, 0), (200, 200, 215), (255, 110, 180), (0, 208, 208)]
pipe_hs = [130, 100, 115, 80, 115, 100, 130]
pipe_w, gap = 38, 10
box_top = 810
x0p = 337
for i, (col, h) in enumerate(zip(pipe_cols, pipe_hs)):
    px0 = x0p + i * (pipe_w + gap)
    py0 = box_top - h
    d.rounded_rectangle([P(px0), P(py0), P(px0 + pipe_w), P(box_top)], radius=P(8), fill=col + (255,), outline=(0, 0, 0, 255), width=8)

# 管风琴箱体
d.rounded_rectangle([P(280), P(box_top), P(720), P(970)], radius=P(16), fill=(255, 46, 147, 255), outline=(0, 0, 0, 255), width=12)
d.ellipse([P(333), P(828), P(363), P(858)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=5)
d.ellipse([P(653), P(873), P(683), P(903)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=5)

# 键盘
d.rectangle([P(300), P(970), P(700), P(995)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=8)
for i in range(1, 10):
    kx = 300 + i * 40
    d.line([P(kx), P(970), P(kx), P(995)], fill=(0, 0, 0, 255), width=5)

# 沙袋（压在琴键上的重物）
d.rounded_rectangle([P(325), P(958), P(465), P(992)], radius=P(10), fill=(148, 136, 116, 255), outline=(0, 0, 0, 255), width=8)
d.rounded_rectangle([P(520), P(958), P(660), P(992)], radius=P(10), fill=(160, 148, 128, 255), outline=(0, 0, 0, 255), width=8)
d.line([P(340), P(975), P(450), P(975)], fill=(90, 78, 58, 255), width=4)
d.line([P(365), P(966), P(365), P(984)], fill=(90, 78, 58, 255), width=3)
d.line([P(425), P(966), P(425), P(984)], fill=(90, 78, 58, 255), width=3)
d.line([P(535), P(975), P(645), P(975)], fill=(90, 78, 58, 255), width=4)
d.line([P(560), P(966), P(560), P(984)], fill=(90, 78, 58, 255), width=3)
d.line([P(620), P(966), P(620), P(984)], fill=(90, 78, 58, 255), width=3)

# 两侧波普大圆
d.ellipse([P(100), P(810), P(240), P(950)], fill=(0, 208, 208, 255), outline=(0, 0, 0, 255), width=10)
d.ellipse([P(155), P(865), P(185), P(895)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=5)
d.ellipse([P(755), P(825), P(905), P(975)], fill=(224, 20, 22, 255), outline=(0, 0, 0, 255), width=10)
d.ellipse([P(815), P(885), P(845), P(915)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=5)

# 音符与四芒星
draw_note(d, 195, 710, 18, (255, 110, 180))
draw_note(d, 795, 670, 16, (0, 208, 208))
sparkle(d, 100, 630, 30, (255, 210, 0))
sparkle(d, 890, 720, 26, (0, 208, 208))

# 青色半色调网点带
dot_grid(d, 0, 1000, W, 1040, 7, (0, 208, 208), 30)

# 白色信息块（漫画对话框风格）
d.rounded_rectangle([P(70), P(1050), P(930), P(1990)], radius=P(28), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=12)
dot_grid(d, 95, 1075, 905, 1965, 3, (225, 225, 225), 26)

# 底部黑条 + 彩色圆点
d.rectangle([0, P(2000), P(W), P(H)], fill=(25, 25, 25, 255))
for i, col in enumerate([(255, 46, 147), (0, 208, 208), (255, 210, 0), (255, 110, 180), (0, 208, 208)]):
    cx0 = 100 + i * 200
    d.ellipse([P(cx0 - 18), P(2018), P(cx0 + 18), P(2054)], fill=col + (255,))

lay = np.array(img)
sf.composite(lay, mode="normal", opacity=1.0)

# ===== 文字层 =====
qbox = sf.text(500, 240, QUOTE, family="cjk-jp", size=44, fill=(30, 30, 30),
               anchor="mt", role="quote", bold=True, max_w=880, line_gap=0.45)
sf.text(500, qbox.bottom + 30, QUOTE_ZH, family="cjk-sc", size=30, fill=(30, 30, 30),
        anchor="mt", role="body", max_w=880, line_gap=0.4)

jp_box = sf.text(110, 1075, FACT, family="cjk-sc", size=30, fill=(30, 30, 30),
                 anchor="lt", role="body", bold=True, max_w=800, line_gap=0.4)
sf.text(110, jp_box.bottom + 28, FACT_ZH, family="cjk-sc", size=28, fill=(50, 50, 50),
        anchor="lt", role="body", max_w=800, line_gap=0.4)

sf.serial(90, 107, SERIAL, family="sans", size=30, fill=(255, 255, 255), anchor="lm", role="meta", bold=True)
sf.datestamp(910, 107, DATE, family="sans", size=30, fill=(255, 255, 255), anchor="rm", role="meta", bold=True)

sf.save(OUT_PATH)
