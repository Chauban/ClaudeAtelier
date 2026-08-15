import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 1000, 1680
S = 2

sf = Surface(W, H, scale=2, bg=(247, 237, 218))

# 纸面颗粒
base = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
base[..., :3] = (247, 237, 218)
noise = np.random.default_rng(4).integers(-4, 5, (sf.H, sf.W, 1), dtype=np.int16)
base[..., :3] = np.clip(base[..., :3].astype(np.int16) + noise, 0, 255).astype(np.uint8)
base[..., 3] = 255
sf.composite(base)

def R(x0, y0, x1, y1):
    return (int(round(x0 * S)), int(round(y0 * S)), int(round(x1 * S)), int(round(y1 * S)))

def P(x, y):
    return (int(round(x * S)), int(round(y * S)))

# 邮票阴影
sx0, sy0, stamp_w, stamp_h = 672, 80, 238, 292
sh = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
ds = ImageDraw.Draw(sh)
ds.rectangle(R(sx0 + 6, sy0 + 10, sx0 + stamp_w + 6, sy0 + stamp_h + 10), fill=(30, 25, 20, 90))
sh = sh.filter(ImageFilter.GaussianBlur(14))
sf.composite(sh, mode="multiply", opacity=0.38)

# 装饰层
dec = Image.new('RGBA', (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(dec)

paper = (249, 244, 228, 255)
blue_dark = (35, 75, 134, 255)
red_air = (196, 62, 57, 255)

# 航空边框空白带
d.rectangle(R(42, 42, W - 42, 66), fill=paper)
d.rectangle(R(42, H - 66, W - 42, H - 42), fill=paper)
d.rectangle(R(42, 42, 66, H - 42), fill=paper)
d.rectangle(R(W - 66, 42, W - 42, H - 42), fill=paper)

# 红蓝斜条纹
stripe_gap = 18
for x in range(38, W - 38, stripe_gap):
    col = red_air if ((x - 38) // stripe_gap) % 2 == 0 else blue_dark
    d.line([P(x, 42), P(x + 14, 66)], fill=col, width=int(12 * S))
    d.line([P(x, H - 66), P(x + 14, H - 42)], fill=col, width=int(12 * S))

for y in range(38, H - 38, stripe_gap):
    col = red_air if ((y - 38) // stripe_gap) % 2 == 0 else blue_dark
    d.line([P(42, y), P(66, y + 14)], fill=col, width=int(12 * S))
    d.line([P(W - 66, y), P(W - 42, y + 14)], fill=col, width=int(12 * S))

d.rectangle(R(30, 30, W - 30, H - 30), outline=blue_dark, width=int(4 * S))
d.rectangle(R(40, 40, W - 40, H - 40), outline=red_air, width=int(4 * S))

# 邮票主体
d.rectangle(R(sx0, sy0, sx0 + stamp_w, sy0 + stamp_h), fill=(17, 42, 66, 255))
d.rectangle(R(sx0 + 5, sy0 + 5, sx0 + stamp_w - 5, sy0 + stamp_h - 5), outline=(246, 240, 225, 255), width=int(3 * S))

# 星点与月亮
rng = np.random.default_rng(20)
for _ in range(18):
    x = sx0 + 12 + rng.random() * (stamp_w - 24)
    y = sy0 + 10 + rng.random() * (stamp_h - 30)
    d.ellipse(R(x - 1, y - 1, x + 1, y + 1), fill=(230, 214, 145, 255))

d.ellipse(R(sx0 + stamp_w - 35, sy0 + 20, sx0 + stamp_w - 7, sy0 + 48), fill=(236, 213, 118, 255))

# 兰花
fx, fy = sx0 + 122, sy0 + 86
petal = (245, 240, 224, 255)
d.ellipse(R(fx - 24, fy - 38, fx + 2, fy - 12), fill=petal)
d.ellipse(R(fx - 36, fy - 22, fx - 14, fy + 2), fill=petal)
d.ellipse(R(fx + 14, fy - 22, fx + 36, fy + 2), fill=petal)
d.ellipse(R(fx - 26, fy - 8, fx - 6, fy + 16), fill=petal)
d.ellipse(R(fx + 6, fy - 8, fx + 26, fy + 16), fill=petal)
d.ellipse(R(fx - 8, fy - 8, fx + 8, fy + 8), fill=(217, 190, 96, 255))

# 蕊柱与茎
d.line([P(fx - 6, fy + 16), P(sx0 + 50, sy0 + stamp_h - 72)], fill=(120, 155, 104, 255), width=int(5 * S))

# 极长的距
spur_tip = (sx0 + 166, sy0 + 232)
d.line([P(fx, fy + 4), P(fx + 22, fy + 72), P(spur_tip[0], spur_tip[1])],
       fill=(243, 235, 210, 255), width=int(7 * S))

# 天蛾
mx, my = sx0 + 76, sy0 + 228
d.ellipse(R(mx - 38, my - 22, mx - 10, my + 2), fill=(68, 56, 50, 255))
d.ellipse(R(mx + 10, my - 22, mx + 38, my + 2), fill=(68, 56, 50, 255))
d.ellipse(R(mx - 30, my - 8, mx - 12, my + 10), fill=(46, 38, 34, 255))
d.ellipse(R(mx + 12, my - 8, mx + 30, my + 10), fill=(46, 38, 34, 255))
d.ellipse(R(mx - 5, my - 12, mx + 5, my + 14), fill=(38, 30, 28, 255))
d.ellipse(R(mx - 5, my - 18, mx + 5, my - 8), fill=(52, 42, 35, 255))

# 口吻与蜜滴
d.line([P(mx, my - 16), P(mx + 44, my + 2), P(spur_tip[0], spur_tip[1])],
       fill=(218, 184, 122, 255), width=int(4 * S))
d.ellipse(R(spur_tip[0] - 4, spur_tip[1] - 4, spur_tip[0] + 4, spur_tip[1] + 4), fill=(150, 200, 230, 255))

# 邮票齿孔
hole_col = (247, 237, 218, 255)
for x in range(sx0 + 10, sx0 + stamp_w, 18):
    d.ellipse(R(x - 5, sy0 - 5, x + 5, sy0 + 5), fill=hole_col)
    d.ellipse(R(x - 5, sy0 + stamp_h - 5, x + 5, sy0 + stamp_h + 5), fill=hole_col)
for y in range(sy0 + 10, sy0 + stamp_h, 18):
    d.ellipse(R(sx0 - 5, y - 5, sx0 + 5, y + 5), fill=hole_col)
    d.ellipse(R(sx0 + stamp_w - 5, y - 5, sx0 + stamp_w + 5, y + 5), fill=hole_col)

# 邮戳
ink = (45, 55, 68, 255)
cx, cy = 170, 135
d.ellipse(R(cx - 80, cy - 80, cx + 80, cy + 80), outline=ink, width=int(5 * S))
d.ellipse(R(cx - 70, cy - 70, cx + 70, cy + 70), outline=ink, width=int(4 * S))
d.line([P(cx - 58, cy + 26), P(cx + 58, cy + 26)], fill=ink, width=int(3 * S))
d.line([P(cx - 48, cy + 42), P(cx + 48, cy + 42)], fill=ink, width=int(3 * S))
d.line([P(cx - 60, cy + 58), P(cx + 60, cy + 58)], fill=ink, width=int(3 * S))

sf.composite(dec, mode="normal", opacity=1.0)

# 文字安全区
sf.frame(80, 60, 840, H - 120)

# 邮戳内文字
sf.serial(cx, cy - 28, SERIAL, family="mono", size=20, fill=(45, 55, 68),
          anchor="mm", role="meta", bold=False)
sf.datestamp(cx, cy + 2, DATE, family="mono", size=20, fill=(45, 55, 68),
             anchor="mm", role="meta", bold=False)

# 金句
quote_y = 470
quote_box = sf.text(110, quote_y, QUOTE,
                    family="cjk-jp", size=40, fill=(25, 42, 62),
                    anchor="lt", role="quote", bold=False,
                    max_w=750, line_gap=0.5)

# 冷知识日文部分
split_marker = '（1862年'
if split_marker in FACT:
    idx = FACT.index(split_marker)
    jap_part = FACT[:idx]
    chn_part = FACT[idx:]
else:
    jap_part = FACT
    chn_part = ''

fact_y = quote_box.bottom + 30
jap_box = sf.text(110, fact_y, jap_part.strip(),
                  family="cjk-jp", size=32, fill=(30, 40, 55),
                  anchor="lt", role="body", bold=False,
                  max_w=750, line_gap=0.48)

# 中文翻译
chn_y = jap_box.bottom + 20
if chn_part:
    sf.text(110, chn_y, chn_part,
            family="cjk-sc", size=28, fill=(80, 95, 115),
            anchor="lt", role="body", bold=False,
            max_w=750, line_gap=0.46)

sf.save(OUT_PATH)
