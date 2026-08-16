from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1350
GREEN = (0, 255, 65)
GREEN_DIM = (0, 190, 70)

sf = Surface(W, H, scale=2, bg=(3, 8, 5))
s = sf.W // W

# ---------- 背景 ----------
base = sf.layer()
base[..., 0] = 3
base[..., 1] = 8
base[..., 2] = 5
base[..., 3] = 255
sf.composite(base)

glow = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([int(sf.W * 0.30), int(sf.H * 0.14), int(sf.W * 0.70), int(sf.H * 0.36)], fill=(0, 255, 70, 18))
gd.ellipse([int(sf.W * 0.28), int(sf.H * 0.46), int(sf.W * 0.72), int(sf.H * 0.72)], fill=(0, 255, 70, 14))
glow = glow.filter(ImageFilter.GaussianBlur(80))
sf.composite(glow, mode="screen", opacity=0.6)

vig = sf.layer()
yy, xx = np.mgrid[0:sf.H, 0:sf.W].astype(np.float32)
nx = xx / (sf.W * 0.5) - 1.0
ny = yy / (sf.H * 0.5) - 1.0
r = np.sqrt(nx * nx + ny * ny)
a = np.clip((r - 0.95) / 0.4, 0.0, 1.0) * 0.4
vig[..., 3] = (a * 255).astype(np.uint8)
sf.composite(vig)

scan = sf.layer()
for sy in range(0, sf.H, 8):
    scan[sy:sy + 2, :, 3] = 30
sf.composite(scan)

bord = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
bd = ImageDraw.Draw(bord)
bd.rounded_rectangle([60 * s, 45 * s, (W - 60) * s, (H - 45) * s], radius=16 * s, outline=(0, 255, 65, 150), width=4)
bd.rounded_rectangle([70 * s, 55 * s, (W - 70) * s, (H - 55) * s], radius=12 * s, outline=(0, 255, 65, 60), width=2)
bd.line([100 * s, 152 * s, (W - 100) * s, 152 * s], fill=(0, 255, 65, 85), width=2)
sf.composite(bord)

# ---------- 文字 ----------
sf.frame(96, 96, 808, H - 192)

sf.serial(100, 112, SERIAL, family="mono", size=20, fill=GREEN, role="meta", anchor="lt")
dw, _ = sf.measure(DATE, "mono", 20)
sf.datestamp(int(W - 100 - dw), 112, DATE, family="mono", size=20, fill=GREEN, role="meta", anchor="lt")

q_lines = QUOTE.split("\n", 1)
quote_de = q_lines[0].strip()
quote_zh = q_lines[1].strip() if len(q_lines) > 1 else ""

qbox = sf.text(130, 210, quote_de, family="mono", size=34, fill=GREEN, role="quote",
               anchor="lt", max_w=W - 240, line_gap=0.4)

qzh = None
if quote_zh:
    qzh = sf.text(130, qbox.bottom + 20, quote_zh, family="cjk-sc", size=24, fill=GREEN_DIM,
                  role="meta", anchor="lt", max_w=W - 240, line_gap=0.4)

f_lines = FACT.split("\n", 1)
fact_de = f_lines[0].strip()
fact_zh = f_lines[1].strip() if len(f_lines) > 1 else ""

y_fact = (qzh.bottom + 72) if qzh is not None else (qbox.bottom + 72)
fbox = sf.text(100, y_fact, fact_de, family="mono", size=30, fill=GREEN, role="body",
               anchor="lt", max_w=W - 200, line_gap=0.4)

fzh = None
if fact_zh:
    fzh = sf.text(100, fbox.bottom + 20, fact_zh, family="cjk-sc", size=24, fill=GREEN_DIM,
                  role="meta", anchor="lt", max_w=W - 200, line_gap=0.4)

# ---------- 终端装饰（不遮挡文字） ----------
dec = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
dd = ImageDraw.Draw(dec)

top_y = int(qbox.y * s)
bot_y = int((qzh.bottom if qzh is not None else qbox.bottom) * s)
dd.line([112 * s, top_y, 112 * s, bot_y], fill=(0, 255, 65, 110), width=4)

sep_y = int(((qzh.bottom if qzh is not None else qbox.bottom) + 36) * s)
dd.line([100 * s, sep_y, (W - 100) * s, sep_y], fill=(0, 255, 65, 70), width=2)

cur_y = int(((fzh.bottom if fzh is not None else fbox.bottom) + 36) * s)
dd.rectangle([100 * s, cur_y, (100 + 14) * s, cur_y + 24 * s], fill=(0, 255, 65, 230))

sf.composite(dec)

sf.save(OUT_PATH)
