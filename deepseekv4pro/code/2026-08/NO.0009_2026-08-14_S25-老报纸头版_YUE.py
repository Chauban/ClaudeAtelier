import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

w, h = 1000, 1120
sf = Surface(w, h, scale=2, bg=(242, 230, 208))
sf.frame(60, 30, 880, 1060)

# ---------- Tier 2：背景与装饰 ----------

# 纸张噪点
paper = sf.layer()
rng = np.random.RandomState(13)
noise = rng.normal(0, 5, (sf.H, sf.W, 3)).astype(np.int16)
paper[..., :3] = np.clip(242 + noise, 0, 255).astype(np.uint8)
paper[..., 1] = np.clip(230 + noise[..., 1], 0, 255).astype(np.uint8)
paper[..., 2] = np.clip(208 + noise[..., 2], 0, 255).astype(np.uint8)
paper[..., 3] = 255
sf.composite(paper, opacity=0.2)

# 暗角
vig = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
dist = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) * 1.4
vig_alpha = np.clip((dist - 0.42) * 220, 0, 45).astype(np.uint8)
vig[..., 0] = 100
vig[..., 1] = 78
vig[..., 2] = 50
vig[..., 3] = vig_alpha
sf.composite(vig)

# 报纸线条、正文底垫
lines_img = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
draw = ImageDraw.Draw(lines_img)
dark = (70, 55, 40, 255)
mid = (110, 95, 75, 255)

# 正文区域干净底垫
draw.rectangle([58 * 2, 336 * 2, 478 * 2, 572 * 2], fill=(241, 228, 205, 255))
draw.rectangle([510 * 2, 336 * 2, 942 * 2, 572 * 2], fill=(241, 228, 205, 255))

# 顶部双线
draw.line([(60 * 2, 36 * 2), (940 * 2, 36 * 2)], fill=dark, width=5)
draw.line([(60 * 2, 42 * 2), (940 * 2, 42 * 2)], fill=dark, width=2)

# 报头下双线
draw.line([(60 * 2, 150 * 2), (940 * 2, 150 * 2)], fill=dark, width=2)
draw.line([(60 * 2, 156 * 2), (940 * 2, 156 * 2)], fill=dark, width=5)

# 标题下细线
draw.line([(60 * 2, 334 * 2), (940 * 2, 334 * 2)], fill=mid, width=2)

# 正文分栏竖线
draw.line([(500 * 2, 336 * 2), (500 * 2, 572 * 2)], fill=mid, width=2)

# 插图边框
draw.rectangle([(78 * 2, 600 * 2), (922 * 2, 1036 * 2)], outline=dark, width=4)
draw.rectangle([(82 * 2, 604 * 2), (918 * 2, 1032 * 2)], outline=mid, width=1)

# 底部双线
draw.line([(60 * 2, 1076 * 2), (940 * 2, 1076 * 2)], fill=dark, width=2)
draw.line([(60 * 2, 1082 * 2), (940 * 2, 1082 * 2)], fill=dark, width=5)

sf.composite(lines_img)

# ---------- 红色精灵插图 ----------
illu_arr = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
il_left, il_top = 82 * 2, 604 * 2
il_right, il_bottom = 918 * 2, 1032 * 2
il_w = il_right - il_left
il_h = il_bottom - il_top

# 夜空渐变
grad = np.linspace(0, 1, il_h)[:, None]
sky = np.zeros((il_h, 1, 3), dtype=np.uint8)
sky[..., 0] = (14 + 24 * (1 - grad)).astype(np.uint8)
sky[..., 1] = (11 + 19 * (1 - grad)).astype(np.uint8)
sky[..., 2] = (62 + 30 * (1 - grad)).astype(np.uint8)
illu_arr[il_top:il_bottom, il_left:il_right, :3] = np.broadcast_to(sky, (il_h, il_w, 3))
illu_arr[il_top:il_bottom, il_left:il_right, 3] = 255

# 星星
rng = np.random.RandomState(777)
n_stars = 110
star_x = rng.randint(il_left + 8, il_right - 8, n_stars)
star_y = rng.randint(il_top + 8, il_bottom - 8, n_stars)
for i in range(n_stars):
    t_rel = (star_y[i] - il_top) / il_h
    if t_rel < 0.08:
        continue
    bright = rng.randint(120, 255)
    illu_arr[star_y[i], star_x[i], :3] = bright
    illu_arr[star_y[i], star_x[i], 3] = 255
    if bright > 220:
        if star_x[i] + 1 < il_right - 1:
            illu_arr[star_y[i], star_x[i] + 1, :3] = int(bright * 0.7)
            illu_arr[star_y[i], star_x[i] + 1, 3] = 255
        if star_y[i] + 1 < il_bottom - 1:
            illu_arr[star_y[i] + 1, star_x[i], :3] = int(bright * 0.7)
            illu_arr[star_y[i] + 1, star_x[i], 3] = 255

illu_img = Image.fromarray(illu_arr)

# 光晕
glow_center_x, glow_center_y = 1000, 1520
glow_layer = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow_layer)
for radius, alpha in [(220, 70), (160, 110), (115, 150), (80, 190), (46, 220)]:
    gdraw.ellipse(
        [glow_center_x - radius, glow_center_y - radius,
         glow_center_x + radius, glow_center_y + radius],
        fill=(235, 50, 20, alpha)
    )
gdraw.ellipse(
    [glow_center_x - 26, glow_center_y - 26,
     glow_center_x + 26, glow_center_y + 26],
    fill=(255, 185, 155, 250)
)
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(42))

# 裁剪光晕
glow_mask = Image.new('L', (sf.W, sf.H), 0)
mdraw = ImageDraw.Draw(glow_mask)
mdraw.rectangle([il_left, il_top, il_right, il_bottom], fill=255)
glow_alpha = glow_layer.getchannel('A')
clipped_alpha = Image.composite(glow_alpha, Image.new('L', (sf.W, sf.H), 0), glow_mask)
glow_layer.putalpha(clipped_alpha)

illu_img = Image.alpha_composite(illu_img, glow_layer)
idraw = ImageDraw.Draw(illu_img)

# 底部云层
cloud_top = il_top + int(il_h * 0.70)
for k in range(0, il_w, 36):
    idraw.pieslice(
        [il_left + k - 20, cloud_top - 30,
         il_left + k + 20, cloud_top + 30],
        180, 360, fill=(10, 8, 26, 235)
    )
idraw.rectangle([il_left, cloud_top, il_right, il_bottom], fill=(10, 8, 26, 235))

# 蓝色卷须
tcx = il_left + il_w // 2
tcy = cloud_top + int(il_h * 0.05)
idraw.line([(tcx - 22, tcy - 20), (tcx, tcy + 30), (tcx + 22, tcy - 20)],
           fill=(95, 95, 235, 200), width=4)
for i, angle in enumerate([-30, -15, 0, 15, 30]):
    vert = 125 - i * 10
    horiz = int(vert * np.sin(np.radians(angle)))
    end_x = tcx + horiz
    end_y = tcy + vert
    idraw.line([(tcx, tcy + 8), (end_x, end_y)],
               fill=(70, 70, 210, 210), width=max(3, 7 - i))
    for j in range(2):
        ba = angle + (22 if j == 0 else -20)
        b_x = end_x + int(55 * np.sin(np.radians(ba)))
        b_y = end_y + 42
        idraw.line([(end_x, end_y), (b_x, b_y)],
                   fill=(50, 50, 190, 180), width=3)

# 红色枝杈
base_y = cloud_top - 22
for i, angle in enumerate([-40, -20, 0, 20, 40]):
    length = 90 - i * 8
    end_x = tcx + int(length * np.sin(np.radians(angle)))
    end_y = base_y - length
    idraw.line([(tcx, base_y), (end_x, end_y)],
               fill=(245, 55, 25, 220), width=5)
    b_x = end_x + int(40 * np.sin(np.radians(angle + 25)))
    b_y = end_y - 30
    idraw.line([(end_x, end_y), (b_x, b_y)],
               fill=(228, 50, 20, 190), width=3)

sf.composite(illu_img)

# ---------- Tier 1：文字 ----------

sf.serial(500, 58, SERIAL, family="cjk-hk", size=32,
          fill=(25, 20, 15), anchor="mt", role="meta", bold=True)

sf.datestamp(500, 116, DATE, family="cjk-hk", size=18,
             fill=(70, 58, 42), anchor="mt", role="meta")

quote_parts = QUOTE.split("，", 1)
if len(quote_parts) == 2:
    quote_text = quote_parts[0] + "，" + "\n" + quote_parts[1]
else:
    quote_text = QUOTE

sf.text(500, 180, quote_text, family="cjk-hk", size=44,
        fill=(25, 20, 15), anchor="mt", role="title", bold=True,
        line_gap=0.3, max_w=860)

fact_lines = sf.wrap(FACT, family="cjk-hk", size=28, max_w=420, bold=False)
total_lines = len(fact_lines)
mid_line = (total_lines + 1) // 2
left_text = "\n".join(fact_lines[:mid_line])
right_text = "\n".join(fact_lines[mid_line:])

sf.text(60, 344, left_text, family="cjk-hk", size=28,
        fill=(35, 30, 24), anchor="lt", role="body", line_gap=0.42, max_w=420)

sf.text(520, 344, right_text, family="cjk-hk", size=28,
        fill=(35, 30, 24), anchor="lt", role="body", line_gap=0.42, max_w=420)

sf.save(OUT_PATH)
