from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1720
sf = Surface(W, H, scale=2, bg=(22, 18, 16))
sf.frame(70, 70, 860, 1580)

# ---------- 唱片主体 ----------
yy, xx = np.mgrid[0:sf.H, 0:sf.W].astype(np.float32)
dx = xx - 1000.0
dy = yy - 1780.0
dist = np.sqrt(dx * dx + dy * dy)

lay = sf.layer()
disc = dist < 742
lay[disc, 0] = 9
lay[disc, 1] = 9
lay[disc, 2] = 12
lay[disc, 3] = 255

lip = (dist >= 734) & (dist < 742)
lay[lip, 0] = 128
lay[lip, 1] = 108
lay[lip, 2] = 84
lay[lip, 3] = 255

for rr in range(696, 228, -12):
    ring = (dist >= rr - 1.5) & (dist < rr)
    lay[ring, 0] = 44
    lay[ring, 1] = 44
    lay[ring, 2] = 52
    lay[ring, 3] = 255

tring = (dist >= 205) & (dist < 212)
lay[tring, 0] = 60
lay[tring, 1] = 42
lay[tring, 2] = 18
lay[tring, 3] = 255

tag = dist < 205
lay[tag, 0] = 213
lay[tag, 1] = 148
lay[tag, 2] = 56
lay[tag, 3] = 255

d1 = (dist >= 180) & (dist < 184)
lay[d1, 0] = 100
lay[d1, 1] = 68
lay[d1, 2] = 28
lay[d1, 3] = 255

d2 = (dist >= 148) & (dist < 151)
lay[d2, 0] = 100
lay[d2, 1] = 68
lay[d2, 2] = 28
lay[d2, 3] = 255

hole = dist < 20
lay[hole, 0] = 9
lay[hole, 1] = 9
lay[hole, 2] = 12
lay[hole, 3] = 255

sf.composite(lay)

# ---------- 唱片高光斜带 ----------
hl = sf.layer()
band = (np.abs(dy - dx) < 55) & (dist > 260) & (dist < 700)
hl[band, 0] = 238
hl[band, 1] = 234
hl[band, 2] = 222
hl[band, 3] = 55
band2 = (np.abs(dy - dx) < 20) & (dist > 320) & (dist < 660)
hl[band2, 3] = 110
sf.composite(Image.fromarray(hl).filter(ImageFilter.GaussianBlur(18)), mode="screen", opacity=0.9)

# ---------- 装饰线 ----------
deco = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)
d.rectangle([860, 238, 1140, 242], fill=(197, 138, 54, 255))
d.rectangle([940, 248, 1060, 251], fill=(197, 138, 54, 255))
d.rectangle([860, 504, 1140, 510], fill=(197, 138, 54, 255))
d.rectangle([940, 3216, 1060, 3224], fill=(197, 138, 54, 255))
sf.composite(deco)

# ---------- QUOTE ----------
q1 = "樹有多長，樓就有多闊。"
w1 = sf.measure(q1, "cjk-hk", 48, bold=True)[0]
sf.text(500 - w1 / 2, 170, q1, family="cjk-hk", size=48, fill=(242, 234, 220), anchor="lt", role="quote", bold=True)

q2 = "城市最初的尺度，由一棵杉木寫成。"
w2 = sf.measure(q2, "cjk-hk", 34)[0]
sf.text(500 - w2 / 2, 268, q2, family="cjk-hk", size=34, fill=(226, 200, 168), anchor="lt", role="quote")

# ---------- FACT ----------
fy = 1340
for ln in sf.wrap(FACT, "cjk-hk", 28, 780):
    w = sf.measure(ln, "cjk-hk", 28)[0]
    sf.text(500 - w / 2, fy, ln, family="cjk-hk", size=28, fill=(222, 212, 196), anchor="lt", role="body")
    fy += 43

# ---------- 唱片中心标签编号与日期 ----------
sf.serial(500, 838, SERIAL, family="sans", size=21, fill=(44, 30, 10), anchor="mm", role="meta")
sf.datestamp(500, 942, DATE, family="sans", size=18, fill=(44, 30, 10), anchor="mm", role="meta")

sf.save(OUT_PATH)
