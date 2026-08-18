from atelier_canvas import Surface
from PIL import Image, ImageDraw
import numpy as np

sf = Surface(1000, 1580, scale=2, bg=(238, 226, 196))

# ── Tier 2：復古醫典底紙 ──
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]

r = 198 + 52 * np.sin(xx * 5.1) + 38 * np.sin(yy * 7.7)
g = 186 + 44 * np.sin(xx * 3.9 + 1.3) + 30 * np.sin(yy * 6.1 + 2.2)
b = 158 + 40 * np.sin(xx * 4.7 + 0.6) + 34 * np.sin(yy * 8.3 + 0.9)
base = np.stack([r, g, b], axis=-1)

noise = np.random.default_rng(34).normal(0, 6, (sf.H, sf.W, 1))
base = base + noise
base[..., 0] = np.clip(base[..., 0] + 10 * xx, 0, 255)
base[..., 1] = np.clip(base[..., 1] + 4 * yy, 0, 255)
base[..., 2] = np.clip(base[..., 2] - 8 * yy + 6 * xx, 0, 255)
base = np.clip(base, 0, 255).astype(np.uint8)

lay[..., :3] = base
lay[..., 3] = 255
sf.composite(lay)

# 陳年污漬（避開上方主要文字區，污漬集中在下半與側邊）
stain = sf.layer()
sy = np.linspace(0, 1, sf.H)[:, None]
sx = np.linspace(0, 1, sf.W)[None, :]
rspot = (210 + 28 * np.exp(-(((sx - 0.22) / 0.18) ** 2 + ((sy - 0.58) / 0.14) ** 2))).astype(np.uint8)
gspot = (190 + 20 * np.exp(-(((sx - 0.84) / 0.22) ** 2 + ((sy - 0.70) / 0.16) ** 2))).astype(np.uint8)
bspot = (158 + 22 * np.exp(-(((sx - 0.68) / 0.20) ** 2 + ((sy - 0.48) / 0.10) ** 2))).astype(np.uint8)
aspot = (60 * np.exp(-(((sx - 0.22) / 0.18) ** 2 + ((sy - 0.58) / 0.14) ** 2)) +
         50 * np.exp(-(((sx - 0.84) / 0.22) ** 2 + ((sy - 0.70) / 0.16) ** 2)) +
         55 * np.exp(-(((sx - 0.68) / 0.20) ** 2 + ((sy - 0.48) / 0.10) ** 2))).astype(np.uint8)
stain[..., 0] = rspot
stain[..., 1] = gspot
stain[..., 2] = bspot
stain[..., 3] = aspot
sf.composite(stain, mode="multiply", opacity=0.5)

# 邊框：解剖銅版畫雙線框
frame_img = Image.fromarray(sf.layer())
draw = ImageDraw.Draw(frame_img)
ink = (52, 42, 28, 255)
draw.rectangle([36, 36, 964, 1544], outline=ink, width=3)
draw.rectangle([46, 46, 954, 1534], outline=ink, width=1)
draw.rectangle([60, 60, 940, 1520], outline=(128, 100, 66, 180), width=2)
for x, y in [(60, 60), (940, 60), (60, 1520), (940, 1520)]:
    draw.line([x - 14, y, x + 14, y], fill=ink, width=2)
    draw.line([x, y - 14, x, y + 14], fill=ink, width=2)
sf.composite(np.array(frame_img))

# ── 主圖：米蘭達剖面與人影墜落（下方） ──
fig_img = Image.fromarray(sf.layer())
fig = ImageDraw.Draw(fig_img)

miranda_cx, miranda_cy, miranda_r = 320, 820, 168
fig.ellipse([miranda_cx - miranda_r - 10, miranda_cy - miranda_r - 10,
             miranda_cx + miranda_r + 10, miranda_cy + miranda_r + 10],
            fill=(222, 206, 168, 255), outline=(52, 42, 28, 255), width=4)
fig.ellipse([miranda_cx - miranda_r, miranda_cy - miranda_r,
             miranda_cx + miranda_r, miranda_cy + miranda_r],
            fill=(198, 178, 140, 255), outline=(52, 42, 28, 255), width=2)

fig.polygon([(155, 892), (160, 656), (245, 604), (280, 614), (280, 898)],
            fill=(224, 207, 170, 255), outline=(52, 42, 28, 255))
fig.polygon([(475, 888), (465, 668), (378, 690), (345, 870)],
            fill=(186, 164, 126, 255), outline=(52, 42, 28, 255))
fig.line([280, 615, 280, 894], fill=(52, 42, 28, 255), width=4)
fig.line([340, 692, 340, 870], fill=(52, 42, 28, 255), width=4)
fig.polygon([(160, 895), (470, 890), (550, 970), (60, 980)],
            fill=(176, 154, 118, 255), outline=(52, 42, 28, 255))

person_x, person_y = 388, 752
fig.ellipse([person_x - 7, person_y - 12, person_x + 7, person_y],
            fill=(52, 42, 28, 255))
fig.line([person_x, person_y + 2, person_x, person_y + 16], fill=(52, 42, 28, 255), width=3)
fig.line([person_x, person_y + 6, person_x - 9, person_y + 14], fill=(52, 42, 28, 255), width=2)
fig.line([person_x, person_y + 6, person_x + 8, person_y + 13], fill=(52, 42, 28, 255), width=2)
fig.line([person_x, person_y + 16, person_x - 6, person_y + 27], fill=(52, 42, 28, 255), width=2)
fig.line([person_x, person_y + 16, person_x + 5, person_y + 26], fill=(52, 42, 28, 255), width=2)

fig.line([385, 623, person_x, person_y - 8], fill=(120, 90, 55, 200), width=1)
for d in range(10, 105, 14):
    trail_x = 385
    trail_y = 623 + d
    fig.ellipse([trail_x - 2, trail_y - 2, trail_x + 3, trail_y + 3],
                fill=(120, 90, 55, 190))

for d in range(600, 890, 24):
    fig.line([165, d, 272, d + 8], fill=(128, 100, 66, 110), width=1)
    fig.line([345, d + 20, 462, d + 14], fill=(120, 90, 55, 110), width=1)
for d in range(600, 870, 24):
    fig.line([320, d, 350, d + 30], fill=(128, 100, 66, 90), width=1)

sf.composite(np.array(fig_img))

# 解剖圖引線（純裝飾）
lead_img = Image.fromarray(sf.layer())
lab = ImageDraw.Draw(lead_img)
def leader(x1, y1, x2, y2, w=2):
    lab.line([x1, y1, x2, y2], fill=(52, 42, 28, 255), width=w)
    r = 4
    lab.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], outline=(52, 42, 28, 255), width=1)
    lab.ellipse([x2 - r, y2 - r, x2 + r, y2 + r], outline=(52, 42, 28, 255), width=1)

leader(920, 540, 590, 680)
leader(880, 620, 480, 730)
leader(905, 710, 365, 775)
leader(925, 800, 585, 855)
leader(930, 890, 505, 945)
sf.composite(np.array(lead_img))

# ── 乾淨文字底板：仿圖版說明區 ──
panel = sf.layer()
ps = 2
x0, x1 = 72 * ps, 930 * ps
y0, y1 = 84 * ps, 520 * ps
panel[y0:y1, x0:x1, :3] = (238, 226, 196)
panel[y0:y1, x0:x1, 3] = 225

border_color = (52, 42, 28, 255)
thick = 3 * ps
panel[y0:y0 + thick, x0:x1] = border_color
panel[y1 - thick:y1, x0:x1] = border_color
panel[y0:y1, x0:x0 + thick] = border_color
panel[y0:y1, x1 - thick:x1] = border_color
sf.composite(panel)

# ── Tier 1：文字 ──
ink = (52, 42, 28)
sf.frame(78, 78, 844, 1464)

# 金句
qy = 104
quote_lines = sf.wrap(QUOTE, "cjk-hk", 30, max_w=810, bold=False)
for line in quote_lines:
    box = sf.text(78, qy, line, family="cjk-hk", size=30, fill=(62, 48, 30),
                  role="quote", anchor="lt", allow_overlap=False)
    qy = box.bottom + 12

# 冷知識
fy = qy + 16
fact_lines = sf.wrap(FACT, "cjk-hk", 28, max_w=812, bold=False)
for line in fact_lines:
    box = sf.text(78, fy, line, family="cjk-hk", size=28, fill=(52, 42, 28),
                  role="body", anchor="lt", allow_overlap=False)
    fy = box.bottom + 10

# 編號與日期：置於下方版框內
serial_box = sf.serial(88, 1310, SERIAL, family="cjk-hk", size=20, fill=(118, 92, 60),
                         role="meta", anchor="lt", allow_overlap=False)
sf.datestamp(88, serial_box.bottom + 12, DATE, family="cjk-hk", size=20, fill=(118, 92, 60),
             role="meta", anchor="lt", allow_overlap=False)

sf.save(OUT_PATH)
