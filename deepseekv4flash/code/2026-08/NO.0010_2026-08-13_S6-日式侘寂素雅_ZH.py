import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 960, 1560
sf = Surface(W, H, scale=2, bg=(247, 244, 238))
sf.frame(70, 60, 820, 1440)

INK = (58, 54, 48)
FAINT = (90, 85, 78)
MOSS = (120, 132, 110)

# 1) 和纸颗粒噪点
rng = np.random.default_rng(11)
grain = sf.layer()
spots = (rng.random((sf.H, sf.W)) < 0.045)
grain[..., 0] = 0
grain[..., 1] = 0
grain[..., 2] = 0
grain[..., 3] = (spots * 12).astype(np.uint8)
sf.composite(grain, mode="multiply", opacity=1.0)

# 2) 右上淡墨晕染
blob = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
bd = ImageDraw.Draw(blob)
bd.ellipse([580 * 2, 110 * 2, 950 * 2, 490 * 2], fill=(60, 56, 50, 40))
blur = blob.filter(ImageFilter.GaussianBlur(60))
sf.composite(blur, opacity=0.55)

# 3) 不完整墨圆（enso，开口朝右下）
arc = sf.layer()
aimg = Image.fromarray(arc)
ad = ImageDraw.Draw(aimg)
ad.arc([660 * 2, 110 * 2, 930 * 2, 380 * 2], start=20, end=295,
       fill=(60, 56, 50, 42), width=12)
sf.composite(arc, opacity=0.7)

# 4) 一片淡银杏叶（扇形 + 柄，左下）
leaf = sf.layer()
limg = Image.fromarray(leaf)
ld = ImageDraw.Draw(limg)
ld.pieslice([104 * 2, 1234 * 2, 196 * 2, 1326 * 2],
            start=180, end=360, fill=(120, 132, 110, 42))
ld.line([150 * 2, 1280 * 2, 150 * 2, 1322 * 2],
        fill=(120, 132, 110, 52), width=4)
sf.composite(leaf, opacity=0.8)

# 5) 海波纹细线（底部）
waves = sf.layer()
wimg = Image.fromarray(waves)
wd = ImageDraw.Draw(wimg)
for xs, xe, y, a in [(100, 430, 1340, 22),
                     (140, 375, 1372, 18),
                     (95, 465, 1404, 15)]:
    wd.line([(xs * 2, y * 2), (xe * 2, y * 2)], fill=(60, 56, 50, a), width=6)
sf.composite(waves)

# 6) 朱印点（右上）
seal = sf.layer()
simg = Image.fromarray(seal)
sd = ImageDraw.Draw(simg)
sd.ellipse([884 * 2, 86 * 2, 906 * 2, 108 * 2], fill=(172, 88, 62, 80))
sf.composite(seal)

# ---------- 文字 ----------
qb = sf.text(80, 390, QUOTE,
             family="serif-cjk", size=44, fill=INK,
             anchor="lt", role="quote",
             max_w=640, line_gap=0.45)

fy = int(qb.bottom) + 140
fb = sf.text(80, fy, FACT,
             family="cjk-sc", size=30, fill=FAINT,
             anchor="lt", role="body",
             max_w=720, line_gap=0.62)

sf.serial(870, 1410, SERIAL,
          family="serif-cjk", size=19, fill=(95, 90, 82), anchor="rt")
sf.datestamp(870, 1450, DATE,
             family="serif-cjk", size=19, fill=(95, 90, 82), anchor="rt")

sf.save(OUT_PATH)
