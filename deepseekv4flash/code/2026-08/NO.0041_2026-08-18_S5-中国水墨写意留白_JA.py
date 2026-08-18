from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 900, 2400
sf = Surface(W, H, scale=2, bg=(248, 244, 235))
rng = np.random.default_rng(42)


def L(v):
    return int(round(v * 2))


# ---------- 宣纸纹理 ----------
fib_lay = sf.layer()
fib = Image.fromarray(fib_lay)
fd = ImageDraw.Draw(fib)
for _ in range(1800):
    fx = int(rng.integers(0, sf.W))
    fy = int(rng.integers(0, sf.H))
    fr = int(rng.integers(1, 5))
    fa = int(rng.integers(8, 26))
    fd.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=(135, 123, 103, fa))
sf.composite(fib.filter(ImageFilter.GaussianBlur(1.0)))

# ---------- 左上淡墨晕与墨点 ----------
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.ellipse([L(80), L(190), L(210), L(320)], fill=(125, 115, 100, 40))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(18))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
for px, py, pr, pa in [(120, 350, 5, 70), (150, 385, 3, 55), (92, 325, 4, 60), (185, 360, 3, 45), (135, 270, 4, 50)]:
    d.ellipse([L(px - pr), L(py - pr), L(px + pr), L(py + pr)], fill=(70, 63, 54, pa))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(2))))

# ---------- 1975 原型相机（烤面包机大小） ----------
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(55), L(885), L(425), L(1285)], radius=L(42), fill=(125, 115, 100, 55))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(16))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(64), L(902), L(416), L(1268)], radius=L(32), fill=(95, 86, 75, 85))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(9))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(72), L(922), L(408), L(1250)], radius=L(24), fill=(68, 62, 53, 100))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(5))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(76), L(1040), L(404), L(1244)], radius=L(20), fill=(55, 50, 43, 125))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(4))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(140), L(830), L(310), L(902)], radius=L(14), fill=(75, 67, 58, 85))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(6))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(150), L(840), L(300), L(892)], radius=L(10), fill=(52, 47, 41, 110))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(3))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.ellipse([L(120), L(990), L(320), L(1190)], fill=(70, 63, 54, 90))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(10))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.ellipse([L(145), L(1015), L(295), L(1165)], fill=(42, 38, 34, 170))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(4))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.ellipse([L(165), L(1030), L(230), L(1095)], fill=(240, 230, 210, 85))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(6))))

# 镜头内的静电噪点
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
for _ in range(60):
    px = int(rng.integers(150, 290))
    py = int(rng.integers(1020, 1160))
    pr = int(rng.integers(1, 4))
    pa = int(rng.integers(50, 160))
    col = (222, 214, 198) if rng.random() < 0.5 else (18, 16, 14)
    d.ellipse([L(px - pr), L(py - pr), L(px + pr), L(py + pr)], fill=col + (pa,))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(1))))

# 机身四周飞白墨点
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
for _ in range(22):
    px = int(rng.integers(35, 450))
    py = int(rng.integers(820, 1295))
    pr = int(rng.integers(2, 6))
    pa = int(rng.integers(20, 100))
    d.ellipse([L(px - pr), L(py - pr), L(px + pr), L(py + pr)], fill=(70, 62, 54, pa))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(2))))

# ---------- 手机微影 ----------
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(478), L(958), L(516), L(1082)], radius=L(6), fill=(55, 50, 45, 150))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(2))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(484), L(965), L(510), L(1075)], radius=L(3), fill=(215, 205, 190, 70))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(1))))

# ---------- 50ms → 23秒 点线 ----------
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
for i in range(14):
    t = i / 13.0
    px = int(L(290 + 188 * t))
    py = int(L(1075 + 40 * np.sin(t * np.pi) + 10 * t))
    pr = max(2, int(L(6 - 4 * t)))
    pa = int(150 - 90 * t)
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(60, 54, 47, pa))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(1.5))))

# ---------- 朱文印章 ----------
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(694), L(44), L(876), L(102)], radius=L(10), fill=(150, 35, 28, 26))
sf.composite(img.filter(ImageFilter.GaussianBlur(L(5))))

lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.rounded_rectangle([L(700), L(50), L(870), L(96)], radius=L(5), outline=(150, 35, 28, 235), width=5)
sf.composite(img.filter(ImageFilter.GaussianBlur(L(1))))

# ================= 受控文字层 =================
sf.frame(24, 24, W - 48, H - 48)
INK = (40, 38, 34)

# 流水号（印章内）+ 日期（落款）
sw, sh = sf.measure(SERIAL, "serif", 24, bold=True)
sf.serial(int(785 - sw / 2), int(71 - sh / 2), SERIAL, family="serif", size=24,
          fill=(150, 35, 28), bold=True, anchor="lt")
dw, dh = sf.measure(DATE, "serif", 18)
sf.datestamp(int(785 - dw / 2), 132, DATE, family="serif", size=18,
             fill=(105, 96, 85), anchor="lt")

# ---------- 金句竖排（右→左） ----------
q_r, sep, q_l = QUOTE.partition("。しかし、")
q_r += sep

YQ, VSIZE, VGAP = 170, 40, 10
XR, XL = 740, 610
y = YQ
for ch in q_r:
    x = XR + (8 if ch in "。、" else 0)
    b = sf.text(x, y, ch, family="cjk-jp", size=VSIZE, fill=INK, anchor="lt", role="quote")
    y = b.bottom + VGAP
y = YQ
for ch in q_l:
    x = XL + (8 if ch in "。、" else 0)
    b = sf.text(x, y, ch, family="cjk-jp", size=VSIZE, fill=INK, anchor="lt", role="quote")
    y = b.bottom + VGAP

# ---------- 金句中文翻译（相机下方） ----------
QUOTE_ZH = "最初的一枚是慢的。然而，正是那份慢，让世界变快了。"
box_tt = sf.text(430, 1400, QUOTE_ZH, family="cjk-sc", size=28, fill=(110, 100, 90),
                 anchor="lt", role="body", max_w=420)

# ---------- 冷知识：底部锚定，中文在日文上方，确保不越界 ----------
FACT_ZH = "世界上第一台一体化数码相机，由柯达工程师史蒂文·萨森于1975年试制而成。画质仅0.01百万像素（100×100），机身烤面包机大小、重3.6公斤。按下快门只需50毫秒，可把一张图像录进磁带却要23秒，而且拍出来还是黑白照。"

box_jp = sf.text(70, H - 24 - 46, FACT, family="cjk-jp", size=28, fill=(60, 55, 48),
                 anchor="lb", role="body", max_w=780)
zh_bottom = box_jp.y - 24
box_zh = sf.text(70, zh_bottom, FACT_ZH, family="cjk-sc", size=28, fill=(110, 100, 90),
                 anchor="lb", role="body", max_w=780)

sf.save(OUT_PATH)
