import numpy as np
from atelier_canvas import Surface

# ── S=1 极简主义大留白 ─────────────────────────────
W, H = 920, 1150
sf = Surface(W, H, scale=2, bg=(248, 246, 241))
sf.frame(120, 100, W - 240, H - 200)

INK = (45, 43, 41)
BODY = (80, 77, 73)
META = (122, 119, 114)

# ── 背景装饰：右下角极淡同心环 + 小圆点（沉石意象）──
lay = sf.layer()
yy, xx = np.mgrid[0:sf.H, 0:sf.W]
cx = int(sf.W * 0.82)
cy = int(sf.H * 0.84)
d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)

for r, a in [(sf.W * 0.045, 60), (sf.W * 0.075, 38), (sf.W * 0.105, 22)]:
    ring = (np.abs(d - r) < 1.6)
    lay[ring, 0] = 196
    lay[ring, 1] = 192
    lay[ring, 2] = 187
    lay[ring, 3] = a

dot = d < sf.W * 0.008
lay[dot, 0] = 60
lay[dot, 1] = 58
lay[dot, 2] = 55
lay[dot, 3] = 200
sf.composite(lay)

# ── 编号与日期：左上角极小 meta ──
sf.serial(140, 150, SERIAL, family="sans", size=18, fill=META, role="meta", anchor="lt")
sf.datestamp(140, 178, DATE, family="sans", size=18, fill=META, role="meta", anchor="lt")

# ── 金句：大号、深墨、宽松行距 ──
q_lines = sf.wrap(QUOTE, "cjk-hk", 36, 620)
qy = 340
for ln in q_lines:
    box = sf.text(140, qy, ln, family="cjk-hk", size=36, fill=INK,
                  role="quote", anchor="lt", line_gap=0.6)
    qy = box.bottom + 22

# ── 冷知识：中号、灰、疏朗排版 ──
f_lines = sf.wrap(FACT, "cjk-hk", 32, 620)
fy = 600
for ln in f_lines:
    box = sf.text(140, fy, ln, family="cjk-hk", size=32, fill=BODY,
                  role="body", anchor="lt", line_gap=0.5)
    fy = box.bottom + 20

sf.save(OUT_PATH)
