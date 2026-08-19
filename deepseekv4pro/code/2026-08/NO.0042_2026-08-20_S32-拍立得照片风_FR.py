from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw

W, H = 1000, 1900
sf = Surface(W, H, scale=2, bg=(247, 243, 236))

# ---------- 拍立得照片主体 ----------
photo = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)

yy_full = (np.arange(sf.H) / 2.0)[:, None]
xx_full = (np.arange(sf.W) / 2.0)[None, :]

x0, y0, x1, y1 = 70, 70, 930, 870
mask = (yy_full >= y0) & (yy_full < y1) & (xx_full >= x0) & (xx_full < x1)
photo[..., 3] = np.where(mask, 255, 0).astype(np.uint8)

t = np.where(mask, (yy_full - y0) / (y1 - y0), 0.0)
horizon = 0.64

sky_mask = mask & (t < horizon)
snow_mask = mask & (t >= horizon)

sky_prog = np.clip(t / max(horizon, 1e-6), 0, 1)
sky_r = (86 + (216 - 86) * sky_prog).astype(np.uint8)
sky_g = (138 + (230 - 138) * sky_prog).astype(np.uint8)
sky_b = (180 + (235 - 180) * sky_prog).astype(np.uint8)
photo[..., 0][sky_mask] = sky_r[sky_mask]
photo[..., 1][sky_mask] = sky_g[sky_mask]
photo[..., 2][sky_mask] = sky_b[sky_mask]

snow_prog = np.clip((t - horizon) / max(1 - horizon, 1e-6), 0, 1)
snow_r = (225 + (250 - 225) * snow_prog).astype(np.uint8)
snow_g = (232 + (252 - 232) * snow_prog).astype(np.uint8)
snow_b = (237 + (252 - 237) * snow_prog).astype(np.uint8)
photo[..., 0][snow_mask] = snow_r[snow_mask]
photo[..., 1][snow_mask] = snow_g[snow_mask]
photo[..., 2][snow_mask] = snow_b[snow_mask]

photo_img = Image.fromarray(photo, "RGBA")
pd = ImageDraw.Draw(photo_img)

# 远处山脊
pd.polygon([
    (70*2, 630*2), (210*2, 500*2), (370*2, 630*2),
    (550*2, 470*2), (730*2, 610*2), (930*2, 520*2),
    (930*2, 870*2), (70*2, 870*2)
], fill=(168, 188, 201, 225))

# 太阳
for radius, col in [(95, (255, 240, 200, 255)),
                     (62, (255, 248, 220, 255)),
                     (34, (255, 253, 238, 255))]:
    pd.ellipse([
        int((178 - radius) * 2), int((152 - radius) * 2),
        int((178 + radius) * 2), int((152 + radius) * 2)
    ], fill=col)

# 薄云
pd.ellipse([180*2, 235*2, 480*2, 268*2], fill=(255, 255, 255, 130))
pd.ellipse([620*2, 198*2, 860*2, 226*2], fill=(255, 255, 255, 110))

# 忏悔雪 blade
def blade(draw, cx, cy_base, h, w, tilt, fill):
    bx = int(round(cx * 2))
    by = int(round(cy_base * 2))
    bh = int(round(h * 2))
    bw = int(round(w * 2))
    tipx = int(round((cx + tilt) * 2))
    draw.polygon([(bx - bw, by), (bx + bw, by), (tipx, by - bh)], fill=fill)

rng = np.random.default_rng(7)
rows_spec = [
    (615, 24, (10, 26), (5, 8), (-9, 9), [(202, 217, 224, 255), (216, 228, 233, 255)]),
    (655, 22, (20, 44), (8, 13), (-13, 11), [(191, 208, 215, 255), (208, 222, 228, 255)]),
    (695, 18, (34, 70), (11, 17), (-18, 15), [(180, 199, 206, 255), (198, 214, 220, 255)]),
    (745, 14, (52, 92), (14, 22), (-21, 18), [(172, 192, 199, 255), (192, 209, 215, 255)]),
    (800, 10, (74, 125), (18, 27), (-24, 22), [(165, 187, 194, 255), (184, 202, 209, 255)]),
]

for yb, count, hr, wr, tr, colors in rows_spec:
    for i in range(count):
        cx = rng.uniform(95, 905)
        h = rng.uniform(hr[0], hr[1])
        w = rng.uniform(wr[0], wr[1])
        tilt = rng.uniform(tr[0], tr[1])
        col = colors[i % len(colors)]
        blade(pd, cx, yb, h, w, tilt, col)

sf.composite(photo_img, mode="normal", opacity=1.0)

# 白色相纸边框
border = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
bd = ImageDraw.Draw(border)
bd.rectangle([70*2, 70*2, 930*2, 870*2], outline=(228, 220, 206, 255), width=5)
sf.composite(border, mode="normal", opacity=1.0)

# 胶带
tape = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
td = ImageDraw.Draw(tape)
for tx, ty in [(150, 70), (850, 70)]:
    td.rectangle([(tx-55)*2, (ty-14)*2, (tx+55)*2, (ty+14)*2], fill=(236, 224, 194, 170))
sf.composite(tape, mode="normal", opacity=1.0)

# ---------- 顶部手写标注：流水号与日期 ----------
sf.frame(10, 8, 980, 60)
sf.serial(80, 16, SERIAL,
          family="cjk-sc", size=18, fill=(130, 118, 100),
          role="meta", anchor="lt")
sf.datestamp(920, 16, DATE,
             family="cjk-sc", size=18, fill=(130, 118, 100),
             role="meta", anchor="rt")

# ---------- 文字区 ----------
def split_bilingual(text):
    idx = text.find("（")
    if idx == -1:
        return text.strip(), ""
    return text[:idx].strip(), text[idx:].strip()

quote_fr, quote_cn = split_bilingual(QUOTE)
fact_fr, fact_cn = split_bilingual(FACT)

sf.frame(70, 900, 860, 920)
y = 920

q_box = sf.text(
    70, y, quote_fr,
    family="serif", size=32, fill=(44, 58, 73),
    role="quote", anchor="lt", max_w=820, line_gap=0.26
)
y = q_box.bottom + 8

q_cn_box = sf.text(
    70, y, quote_cn,
    family="cjk-sc", size=22, fill=(92, 100, 110),
    role="meta", anchor="lt", max_w=820, line_gap=0.20
)
y = q_cn_box.bottom + 22

f_box = sf.text(
    70, y, fact_fr,
    family="sans", size=28, fill=(76, 84, 94),
    role="body", anchor="lt", max_w=820, line_gap=0.22
)
y = f_box.bottom + 8

f_cn_box = sf.text(
    70, y, fact_cn,
    family="cjk-sc", size=22, fill=(92, 100, 110),
    role="meta", anchor="lt", max_w=820, line_gap=0.18
)

sf.save(OUT_PATH)
