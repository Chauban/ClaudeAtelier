from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math

W, H = 1000, 1780
SC = 2
BLUE = (31, 74, 122)
DBLUE = (22, 51, 92)

sf = Surface(W, H, scale=SC, bg=(248, 246, 239))
sf.frame(80, 100, 840, 1560)

# ---------- Tier 2 装饰 ----------
deco = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)

# 双线边框
d.rectangle([36*SC, 36*SC, (W-36)*SC, (H-36)*SC], outline=BLUE+(255,), width=4)
d.rectangle([45*SC, 45*SC, (W-45)*SC, (H-45)*SC], outline=BLUE+(255,), width=2)

# 顶部回纹带
for i in range(19):
    x = 89 + i * 44
    d.rectangle([x*SC, 64*SC, (x+30)*SC, 94*SC], outline=BLUE+(255,), width=6)
    d.rectangle([(x+9)*SC, 73*SC, (x+21)*SC, 85*SC], outline=BLUE+(255,), width=6)

# 云纹（DATE 两侧）
d.arc([310*SC, 128*SC, 350*SC, 168*SC], 180, 360, fill=BLUE+(150,), width=4)
d.arc([332*SC, 128*SC, 372*SC, 168*SC], 180, 360, fill=BLUE+(150,), width=4)
d.line([316*SC, 148*SC, 366*SC, 148*SC], fill=BLUE+(150,), width=4)
d.arc([650*SC, 128*SC, 690*SC, 168*SC], 180, 360, fill=BLUE+(150,), width=4)
d.arc([628*SC, 128*SC, 668*SC, 168*SC], 180, 360, fill=BLUE+(150,), width=4)
d.line([634*SC, 148*SC, 684*SC, 148*SC], fill=BLUE+(150,), width=4)

# 涟漪
for rx, ry, al, wd in [(168, 92, 46, 5), (190, 104, 36, 4), (214, 118, 26, 3), (242, 132, 20, 4)]:
    d.ellipse([(500-rx)*SC, (780-ry)*SC, (500+rx)*SC, (780+ry)*SC],
              outline=(31, 74, 122, al), width=wd)

# 缠枝
def bezier(p0, p1, p2, p3, width=5, alpha=110, n=80):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3*p0[0] + 3*mt**2*t*p1[0] + 3*mt*t**2*p2[0] + t**3*p3[0]
        y = mt**3*p0[1] + 3*mt**2*t*p1[1] + 3*mt*t**2*p2[1] + t**3*p3[1]
        pts.append((x*SC, y*SC))
    d.line(pts, fill=(31, 74, 122, alpha), width=width)

bezier((430, 840), (350, 870), (320, 920), (278, 952))
bezier((570, 840), (650, 870), (680, 920), (722, 952))

# 小叶
for (ex, ey, ew, eh) in [(336, 890, 26, 14), (302, 930, 22, 12),
                         (664, 890, 26, 14), (698, 930, 22, 12)]:
    d.ellipse([(ex-ew/2)*SC, (ey-eh/2)*SC, (ex+ew/2)*SC, (ey+eh/2)*SC],
              fill=(31, 74, 122, 30), outline=(31, 74, 122, 100), width=4)

# 底部莲瓣纹
for i in range(17):
    x = 113 + i * 46
    d.arc([x*SC, 1660*SC, (x+38)*SC, 1716*SC], 0, 180, fill=(31, 74, 122, 160), width=5)
    d.arc([(x+9)*SC, 1666*SC, (x+29)*SC, 1708*SC], 0, 180, fill=(31, 74, 122, 100), width=3)

# 底款双圈
d.ellipse([430*SC, 1460*SC, 570*SC, 1600*SC], outline=DBLUE+(255,), width=5)
d.ellipse([442*SC, 1472*SC, 558*SC, 1588*SC], outline=DBLUE+(255,), width=3)

sf.composite(deco)

# ---------- 青花莲花 ----------
petal = sf.layer()
Y, X = np.mgrid[0:sf.H, 0:sf.W].astype(np.float32)
cx, cy = 500.0 * SC, 780.0 * SC
R = float(SC)

for k in range(8):
    ang = k * math.pi / 4
    ca, sa = math.cos(-ang), math.sin(-ang)
    # 外瓣
    ox = cx + math.cos(ang) * 92 * R
    oy = cy + math.sin(ang) * 92 * R
    dx = (X - ox) * ca - (Y - oy) * sa
    dy = (X - ox) * sa + (Y - oy) * ca
    m = (dx / (64*R))**2 + (dy / (28*R))**2 <= 1.0
    petal[m] = (31, 74, 122, 58)
    # 内瓣
    ang2 = ang + math.pi / 8
    ca2, sa2 = math.cos(-ang2), math.sin(-ang2)
    ox = cx + math.cos(ang2) * 58 * R
    oy = cy + math.sin(ang2) * 58 * R
    dx = (X - ox) * ca2 - (Y - oy) * sa2
    dy = (X - ox) * sa2 + (Y - oy) * ca2
    m = (dx / (40*R))**2 + (dy / (20*R))**2 <= 1.0
    petal[m] = (31, 74, 122, 72)

# 花心淡圆
m = (X - cx)**2 + (Y - cy)**2 <= (24 * R) ** 2
petal[m] = (22, 54, 92, 45)

petal_img = Image.fromarray(petal, "RGBA")
sf.composite(petal_img.filter(ImageFilter.GaussianBlur(7)), opacity=0.8)
sf.composite(petal_img, opacity=0.9)

# 花心三曲水纹（换水意象）
core = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
cd = ImageDraw.Draw(core)
for wy, al, ph in [(770, 90, 0.0), (782, 75, 1.3), (794, 60, 2.6)]:
    xs = np.arange(476, 524, 2)
    ys = wy + 2.5 * np.sin((xs - 476) / 9 + ph)
    pts = [(float(x)*SC, float(y)*SC) for x, y in zip(xs, ys)]
    cd.line(pts, fill=(15, 42, 80, al), width=4)
sf.composite(core)

# ---------- Tier 1 文字 ----------
QUOTE_ZH = "一天四次，无需你开口，你的大脑就沐浴在自己制造的新水里——更新不是选择，而是身体最古老的习惯。"
parts = FACT.split("（")
FACT_EN = parts[0].strip()
FACT_ZH = parts[1].rstrip("）").strip() if len(parts) > 1 else ""

sf.datestamp(500, 142, DATE, family="serif", size=26, fill=DBLUE,
             anchor="mt", role="meta")

qb = sf.text(500, 204, QUOTE, family="serif", size=42, fill=DBLUE,
             anchor="mt", role="quote", max_w=760, line_gap=0.35)

qz = sf.text(500, qb.bottom + 36, QUOTE_ZH, family="cjk-sc", size=28,
             fill=BLUE, anchor="mt", role="quote", max_w=700, line_gap=0.35)

fb = sf.text(500, 980, FACT_EN, family="sans", size=36, fill=DBLUE,
             anchor="mt", role="body", max_w=760, line_gap=0.35)

fz = sf.text(500, fb.bottom + 34, FACT_ZH, family="cjk-sc", size=28,
             fill=BLUE, anchor="mt", role="body", max_w=700, line_gap=0.35)

sf.serial(500, 1530, SERIAL, family="serif", size=26, fill=DBLUE,
          anchor="mm", role="meta")

sf.save(OUT_PATH)
