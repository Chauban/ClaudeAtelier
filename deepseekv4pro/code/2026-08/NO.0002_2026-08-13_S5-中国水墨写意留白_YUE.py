from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

LW, LH = 1000, 1560

sf = Surface(LW, LH, scale=2, bg=(246, 243, 236))

K = sf.W // LW
MK = lambda v: int(v * K)

# ---------- 背景：宣紙留白 + 淡墨水痕 ----------
ink = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(ink)

d.ellipse([MK(470), MK(-140), MK(1190), MK(420)], fill=(112, 108, 100, 24))
d.ellipse([MK(-340), MK(580), MK(220), MK(1260)], fill=(88, 84, 78, 20))
d.ellipse([MK(500), MK(1070), MK(1260), MK(1600)], fill=(70, 68, 64, 22))

d.line([MK(120), MK(460), MK(180), MK(580)], fill=(45, 42, 40, 32), width=MK(18))
d.line([MK(830), MK(260), MK(900), MK(560)], fill=(55, 51, 48, 26), width=MK(14))
d.line([MK(700), MK(1320), MK(820), MK(1180)], fill=(50, 48, 44, 24), width=MK(16))

sf.composite(ink.filter(ImageFilter.GaussianBlur(MK(7))), mode="multiply", opacity=0.65)

# ---------- 右下角朱紅印章底 ----------
seal_w, seal_h = 170, 74
seal_x = LW - 250
seal_y = LH - 190

seal = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
sd = ImageDraw.Draw(seal)
sd.rounded_rectangle(
    [MK(seal_x), MK(seal_y), MK(seal_x + seal_w), MK(seal_y + seal_h)],
    radius=MK(12),
    fill=(176, 46, 38, 255),
)
sf.composite(seal)

# ---------- 文字安全區 ----------
sf.frame(90, 90, LW - 180, LH - 180)

quote_box = sf.text(
    90, 280, QUOTE,
    family="cjk-hk", size=56, fill=(32, 30, 29),
    anchor="lt", role="quote", bold=True,
    max_w=560, line_gap=0.55, allow_overlap=False,
)

fact_box = sf.text(
    90, quote_box.bottom + 80, FACT,
    family="cjk-hk", size=32, fill=(54, 51, 47),
    anchor="lt", role="body",
    max_w=770, line_gap=0.62, allow_overlap=False,
)

seal_cx = seal_x + seal_w / 2
seal_cy = seal_y + seal_h / 2

sf.serial(
    seal_cx, seal_cy, SERIAL,
    family="sans", size=23, fill=(255, 250, 244),
    anchor="mm", role="meta", bold=True,
)

# 日期移到左下角，遠離右下角的暗色墨水痕與紅印章
sf.datestamp(
    90, 1440, DATE,
    family="sans", size=20, fill=(50, 46, 43),
    anchor="lt", role="meta",
)

sf.save(OUT_PATH)
