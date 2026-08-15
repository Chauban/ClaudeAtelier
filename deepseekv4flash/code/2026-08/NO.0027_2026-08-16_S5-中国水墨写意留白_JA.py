import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

random.seed(20260816)

W, H = 1000, 1780
sf = Surface(W, H, scale=2, bg=(248, 246, 241))
sf.frame(70, 70, 860, 1640)

INK = (36, 40, 44)
INK2 = (46, 49, 53)

# ---- 紙肌 ----
paper = sf.layer()
nz = np.random.rand(sf.H, sf.W, 1)
paper[..., 0] = 255
paper[..., 1] = 253
paper[..., 2] = 248
paper[..., 3] = (nz[..., 0] * 18).astype(np.uint8)
sf.composite(paper)

# ---- 朝日 ----
sun = sf.layer()
sun_img = Image.fromarray(sun)
sd = ImageDraw.Draw(sun_img)
sd.ellipse([(150 - 36) * 2, (170 - 36) * 2, (150 + 36) * 2, (170 + 36) * 2],
           fill=(208, 94, 66, 64))
sf.composite(sun_img.filter(ImageFilter.GaussianBlur(8)))

# ---- 遠山の淡墨 ----
for color, y0, amp, freq, opa, rad in [
    ((210, 207, 201), 676, 14, 260, 0.18, 22),
    ((190, 186, 180), 724, 20, 200, 0.22, 16),
]:
    lay = sf.layer()
    img = Image.fromarray(lay)
    d = ImageDraw.Draw(img)
    pts = [(0, y0 * 2)]
    for x in range(0, sf.W + 60, 60):
        y = y0 * 2 + amp * 2 * math.sin(x / freq) + (amp // 2) * 2 * math.sin(x / (freq * 0.43))
        pts.append((x, y))
    pts += [(sf.W, sf.H), (0, sf.H)]
    d.polygon(pts, fill=color + (255,))
    sf.composite(img.filter(ImageFilter.GaussianBlur(rad)), opacity=opa)

# ---- 融雪の池 ----
pool = sf.layer()
yy, xx = np.mgrid[0:sf.H, 0:sf.W]
pcx, pcy, prad = 500 * 2, 1000 * 2, 200 * 2
dist = np.sqrt((xx - pcx) ** 2 + (yy - pcy) ** 2)
vg = np.clip((yy - (pcy - prad)) / (prad * 2), 0, 1)
base = 92 + 30 * vg
pool[..., 0] = base
pool[..., 1] = base + 4
pool[..., 2] = base - 2
edge = np.clip((prad - dist) / (prad * 0.30), 0, 1)
edge = edge * edge * (3 - 2 * edge)
pool[..., 3] = (edge * 230).astype(np.uint8)
sf.composite(Image.fromarray(pool).filter(ImageFilter.GaussianBlur(5)))

# ---- 水面の光 ----
hl = sf.layer()
hl_img = Image.fromarray(hl)
hd = ImageDraw.Draw(hl_img)
hd.ellipse([(500 - 118) * 2, (1020 - 14) * 2, (500 + 118) * 2, (1020 + 22) * 2],
           fill=(168, 164, 158, 70))
hd.ellipse([(500 - 60) * 2, (1032 - 10) * 2, (500 - 8) * 2, (1032 + 12) * 2],
           fill=(210, 206, 200, 55))
sf.composite(hl_img.filter(ImageFilter.GaussianBlur(6)), opacity=0.6)

# ---- 花の映り込み ----
refl = sf.layer()
refl_img = Image.fromarray(refl)
rd = ImageDraw.Draw(refl_img)
rd.ellipse([(500 - 88) * 2, (1028 - 30) * 2, (500 + 88) * 2, (1028 + 40) * 2],
           fill=(74, 64, 70, 85))
sf.composite(refl_img.filter(ImageFilter.GaussianBlur(9)), opacity=0.7)

# ---- ザゼンソウ ----
flower = sf.layer()
fimg = Image.fromarray(flower)
fd = ImageDraw.Draw(fimg)
fd.ellipse([(500 - 120) * 2, (1040 - 34) * 2, (500 + 120) * 2, (1040 + 34) * 2],
           fill=(76, 64, 70, 210))
fd.ellipse([(500 - 86) * 2, (950 - 126) * 2, (500 + 86) * 2, (950 + 126) * 2],
           fill=(62, 52, 60, 240))
fd.ellipse([(500 - 60) * 2, (908 - 50) * 2, (500 + 60) * 2, (908 + 50) * 2],
           fill=(72, 60, 66, 225))
fd.ellipse([(500 - 34) * 2, (962 - 92) * 2, (500 + 52) * 2, (962 + 92) * 2],
           fill=(44, 38, 46, 205))
fd.ellipse([(500 - 12) * 2, (960 - 82) * 2, (500 + 12) * 2, (960 + 72) * 2],
           fill=(138, 100, 108, 210))
fd.ellipse([(500 - 78) * 2, (918 - 98) * 2, (500 - 6) * 2, (918 + 82) * 2],
           fill=(122, 110, 118, 85))
for _ in range(110):
    a = random.uniform(0, math.tau)
    rr = math.sqrt(random.random()) * 92
    px = 500 * 2 + rr * math.cos(a) * 2
    py = 958 * 2 + rr * math.sin(a) * 1.5 * 2
    pr = random.uniform(2, 10) * 2
    fd.ellipse([px - pr, py - pr, px + pr, py + pr],
               fill=(54, 46, 54, random.randint(110, 210)))
sf.composite(fimg.filter(ImageFilter.GaussianBlur(2.2)), opacity=0.98)

# ---- 雪の縁 ----
rim = sf.layer()
rim_img = Image.fromarray(rim)
rd2 = ImageDraw.Draw(rim_img)
for _ in range(130):
    a = random.uniform(0, math.tau)
    rr = prad + random.uniform(-6, 30) * 2
    px = pcx + rr * math.cos(a)
    py = pcy + rr * math.sin(a)
    pr = random.uniform(6, 20) * 2
    rd2.ellipse([px - pr, py - pr, px + pr, py + pr],
                fill=(116, 112, 106, random.randint(40, 95)))
sf.composite(rim_img.filter(ImageFilter.GaussianBlur(8)), opacity=0.8)

# ---- 池辺の草 ----
grass = sf.layer()
gimg = Image.fromarray(grass)
gd = ImageDraw.Draw(gimg)
for _ in range(30):
    if random.random() < 0.5:
        bx = random.uniform(200, 460)
    else:
        bx = random.uniform(540, 800)
    by = random.uniform(1030, 1210)
    hgt = random.uniform(36, 85)
    lean = random.uniform(-16, 16)
    gd.line([(bx * 2, by * 2), (bx * 2 + lean * 2, (by - hgt) * 2)],
            fill=(72, 68, 64, random.randint(130, 210)), width=random.choice([2, 3]))
    gd.line([(bx * 2 + 6 * 2, by * 2), (bx * 2 + 8 * 2 + lean * 0.4 * 2, (by - hgt * 0.65) * 2)],
            fill=(72, 68, 64, random.randint(90, 160)), width=2)
sf.composite(gimg.filter(ImageFilter.GaussianBlur(0.5)), opacity=0.85)

# ---- 湯気 ----
steam = sf.layer()
simg = Image.fromarray(steam)
smd = ImageDraw.Draw(simg)
for _ in range(170):
    px = 500 * 2 + random.uniform(-170, 170) * 2
    py = 990 * 2 - random.uniform(0, 340) * 2
    pr = random.uniform(18, 52) * 2
    smd.ellipse([px - pr, py - pr, px + pr, py + pr],
                fill=(255, 255, 255, random.randint(6, 18)))
sf.composite(simg.filter(ImageFilter.GaussianBlur(30)))

# ---- ハエ ----
flies = sf.layer()
flimg = Image.fromarray(flies)
fld = ImageDraw.Draw(flimg)
for fx, fy in [(565, 782), (618, 840), (548, 714), (628, 748), (606, 912),
               (588, 668), (648, 796), (572, 868)]:
    fx, fy = fx * 2, fy * 2
    fld.ellipse([fx - 6, fy - 4, fx + 6, fy + 4], fill=(30, 30, 30, 235))
    fld.ellipse([fx - 10, fy - 6, fx - 4, fy + 1], fill=(92, 90, 87, 90))
    fld.ellipse([fx + 4, fy - 6, fx + 10, fy + 1], fill=(92, 90, 87, 90))
sf.composite(flimg.filter(ImageFilter.GaussianBlur(0.8)))

# ================= 文字 =================

# ---- QUOTE 縦書き ----
qsize = 48
qpitch = 78
col_x = [872, 806, 740, 674, 608]
lines = ["雪を溶かすのは", "太陽だけじゃない。", "花は自分の熱で、", "自分の春を", "先取りする。"]

for ci, line in enumerate(lines):
    for i, ch in enumerate(line):
        sf.text(col_x[ci], 140 + i * qpitch, ch,
                family="cjk-jp", size=qsize, fill=INK, role="quote")

# ---- FACT 分割描画（「時」は繁体字形） ----
idx = FACT.rfind("（")
fact_jp = FACT[:idx].strip()
fact_zh = FACT[idx:].strip()

def draw_jp_line(cx, cy, text, size, fill):
    """Draw a Japanese line, replacing 時 with cjk-tc font."""
    x = cx
    last_box = None
    if "時" in text:
        parts = text.split("時")
        for pi, part in enumerate(parts):
            if part:
                bw, bh = sf.measure(part, "cjk-jp", size)
                box = sf.text(x, cy, part, family="cjk-jp", size=size, fill=fill, role="body")
                x = box.right + 4
                last_box = box
            if pi < len(parts) - 1:
                bw, bh = sf.measure("時", "cjk-tc", size)
                box = sf.text(x, cy, "時", family="cjk-tc", size=size, fill=fill, role="body")
                x = box.right + 4
                last_box = box
        if last_box is None:
            last_box = sf.text(cx, cy, text, family="cjk-jp", size=size, fill=fill, role="body")
        return last_box
    return sf.text(cx, cy, text, family="cjk-jp", size=size, fill=fill, role="body")

wrapped_jp = sf.wrap(fact_jp, "cjk-jp", 30, 800)
ypos = 1260
for ln in wrapped_jp:
    box = draw_jp_line(80, ypos, ln, 30, INK2)
    ypos = box.bottom + 18

sf.text(80, ypos + 2, fact_zh, family="cjk-sc", size=28,
        fill=(100, 97, 92), role="body", max_w=800, line_gap=0.44)

# ---- 落款印 ----
ser_w, ser_h = sf.measure(SERIAL, "cjk-sc", 20, bold=True)
seal_w = ser_w + 44
seal_h = ser_h + 30
seal_x = 872 - seal_w
seal_y = 1692 - seal_h

seal = sf.layer()
seal_img = Image.fromarray(seal)
seald = ImageDraw.Draw(seal_img)
seald.rectangle([seal_x * 2, seal_y * 2, (seal_x + seal_w) * 2, (seal_y + seal_h) * 2],
                fill=(176, 50, 40, 255))
for _ in range(120):
    px = seal_x * 2 + random.uniform(0, seal_w * 2)
    py = seal_y * 2 + random.uniform(0, seal_h * 2)
    pr = random.uniform(4, 13) * 2
    seald.ellipse([px - pr, py - pr, px + pr, py + pr],
                  fill=(150, 42, 34, random.randint(120, 220)))
sf.composite(seal_img.filter(ImageFilter.GaussianBlur(1.2)))

sf.serial(seal_x + (seal_w - ser_w) // 2, seal_y + (seal_h - ser_h) // 2,
          SERIAL, family="cjk-sc", size=20, fill=(252, 250, 246),
          role="meta", bold=True)

# ---- 日付 ----
dw, dh = sf.measure(DATE, "cjk-jp", 18)
sf.datestamp(seal_x - 26 - dw, 1692 - dh,
             DATE, family="cjk-jp", size=18,
             fill=(40, 40, 40), role="meta")

sf.save(OUT_PATH)
