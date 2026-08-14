from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math

W, H = 1000, 1440
sf = Surface(W, H, scale=2, bg=(127, 181, 216))
sf.frame(80, 80, 840, 1280)

# ---------- 背景 ----------
lay = np.zeros((sf.H, sf.W, 4), dtype=np.uint8)
yt = np.linspace(0, 1, sf.H)
pos = [0.0, 0.35, 0.75, 1.0]
Rc = np.interp(yt, pos, [120, 200, 242, 255]).astype(np.uint8)
Gc = np.interp(yt, pos, [178, 192, 190, 212]).astype(np.uint8)
Bc = np.interp(yt, pos, [220, 212, 168, 158]).astype(np.uint8)
lay[..., 0] = Rc[:, None]
lay[..., 1] = Gc[:, None]
lay[..., 2] = Bc[:, None]
lay[..., 3] = 255
bg = Image.fromarray(lay, "RGBA")

# 晨光光晕
sun = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(sun)
d.ellipse([280 * 2, -120 * 2, 820 * 2, 420 * 2], fill=(255, 246, 228, 90))
sun = sun.filter(ImageFilter.GaussianBlur(100))
bg = Image.alpha_composite(bg, sun)

# 彩色光斑
spots = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(spots)
d.ellipse([60 * 2, 150 * 2, 420 * 2, 510 * 2], fill=(255, 158, 175, 105))
d.ellipse([610 * 2, 70 * 2, 930 * 2, 390 * 2], fill=(130, 198, 245, 100))
d.ellipse([300 * 2, 640 * 2, 760 * 2, 1100 * 2], fill=(255, 214, 138, 85))
d.ellipse([650 * 2, 460 * 2, 950 * 2, 760 * 2], fill=(188, 152, 248, 80))
d.ellipse([70 * 2, 1100 * 2, 470 * 2, 1500 * 2], fill=(255, 166, 146, 90))
d.ellipse([550 * 2, 1200 * 2, 910 * 2, 1560 * 2], fill=(145, 208, 232, 85))
spots = spots.filter(ImageFilter.GaussianBlur(70))
bg = Image.alpha_composite(bg, spots)

# 毛玻璃的模糊底
blurred = bg.filter(ImageFilter.GaussianBlur(16))

# 主面板投影
sh = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(sh)
d.rounded_rectangle([94 * 2, 276 * 2, 906 * 2, 1238 * 2], radius=76, fill=(28, 45, 80, 60))
sh = sh.filter(ImageFilter.GaussianBlur(30))
bg = Image.alpha_composite(bg, sh)

# 主毛玻璃面板
mask = Image.new("L", (sf.W, sf.H), 0)
d = ImageDraw.Draw(mask)
d.rounded_rectangle([100 * 2, 260 * 2, 900 * 2, 1220 * 2], radius=80, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(2))
bg.paste(blurred, (0, 0), mask)

glass = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(glass)
d.rounded_rectangle([100 * 2, 260 * 2, 900 * 2, 1220 * 2], radius=80,
                    fill=(255, 255, 255, 85), outline=(255, 255, 255, 175), width=3)
bg = Image.alpha_composite(bg, glass)

glow = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(glow)
d.rounded_rectangle([98 * 2, 258 * 2, 902 * 2, 1222 * 2], radius=82, outline=(255, 255, 255, 100), width=5)
glow = glow.filter(ImageFilter.GaussianBlur(6))
bg = Image.alpha_composite(bg, glow)

# 斜向反光
sheen = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(sheen)
d.polygon([(240 * 2, 260 * 2), (480 * 2, 260 * 2), (400 * 2, 1220 * 2), (200 * 2, 1220 * 2)], fill=(255, 255, 255, 20))
bg = Image.alpha_composite(bg, sheen)


def glass_pill(x, y, w, h, r=22):
    m = Image.new("L", (sf.W, sf.H), 0)
    md = ImageDraw.Draw(m)
    md.rounded_rectangle([x * 2, y * 2, (x + w) * 2, (y + h) * 2], radius=r * 2, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(2))
    bg.paste(blurred, (0, 0), m)
    gl = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.rounded_rectangle([x * 2, y * 2, (x + w) * 2, (y + h) * 2], radius=r * 2,
                         fill=(255, 255, 255, 95), outline=(255, 255, 255, 185), width=2)
    gd.line([(x + 16) * 2, (y + 10) * 2, (x + w - 16) * 2, (y + 10) * 2], fill=(255, 255, 255, 70), width=2)
    return gl


bg = Image.alpha_composite(bg, glass_pill(100, 120, 230, 76, 22))
bg = Image.alpha_composite(bg, glass_pill(670, 120, 230, 76, 22))
bg = Image.alpha_composite(bg, glass_pill(150, 1300, 700, 90, 30))

# 底部雲浪
wave = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
wd = ImageDraw.Draw(wave)


def wave_line(ybase, a1, a2, color, width):
    pts = []
    for xp in range(0, sf.W, 4):
        fx = xp / 2.0
        yy = ybase + a1 * math.sin(fx / 62.0) + a2 * math.sin(fx / 25.0)
        pts.append((xp, yy * 2))
    wd.line(pts, fill=color, width=width)


wave_line(1120, 34, 14, (255, 255, 255, 70), 9)
wave_line(1200, 26, 10, (255, 255, 255, 45), 6)
wave_line(1300, 18, 8, (255, 255, 255, 30), 4)
wave = wave.filter(ImageFilter.GaussianBlur(6))
bg = Image.alpha_composite(bg, wave)

# 漂浮玻璃珠
beads = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(beads)
d.ellipse([140 * 2, 225 * 2, 186 * 2, 271 * 2], fill=(255, 255, 255, 60), outline=(255, 255, 255, 130), width=2)
d.ellipse([800 * 2, 940 * 2, 836 * 2, 976 * 2], fill=(255, 255, 255, 50), outline=(255, 255, 255, 110), width=2)
d.ellipse([60 * 2, 730 * 2, 104 * 2, 774 * 2], fill=(255, 255, 255, 45), outline=(255, 255, 255, 100), width=2)
d.ellipse([852 * 2, 310 * 2, 898 * 2, 356 * 2], fill=(255, 255, 255, 50), outline=(255, 255, 255, 110), width=2)
d.ellipse([180 * 2, 1360 * 2, 214 * 2, 1394 * 2], fill=(255, 255, 255, 45), outline=(255, 255, 255, 100), width=2)
d.ellipse([790 * 2, 1320 * 2, 830 * 2, 1360 * 2], fill=(255, 255, 255, 50), outline=(255, 255, 255, 110), width=2)
beads = beads.filter(ImageFilter.GaussianBlur(1))
bg = Image.alpha_composite(bg, beads)

sf.composite(bg)

# ---------- 文字 ----------
sf.serial(215, 158, SERIAL, family="sans", size=28, fill=(30, 42, 66), bold=True, anchor="mm")
sf.datestamp(785, 158, DATE, family="sans", size=28, fill=(30, 42, 66), bold=True, anchor="mm")

quote_lines = ["人人都話衝浪，", "原來地球上最大嘅浪喺天上——", "唔使落水，飛過去就衝到。"]
qy = 380
last_bottom = 0
for ln in quote_lines:
    b = sf.text(500, qy, ln, family="cjk-hk", size=50, fill=(20, 36, 66),
                anchor="mt", role="quote", line_gap=0.5)
    last_bottom = b.bottom
    qy = b.bottom + 16

sep_y = last_bottom + 46
sep_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
sdg = ImageDraw.Draw(sep_img)
sdg.ellipse([500 * 2 - 9, sep_y * 2 - 9, 500 * 2 + 9, sep_y * 2 + 9], fill=(255, 255, 255, 200))
sdg.line([350 * 2, sep_y * 2, 491 * 2, sep_y * 2], fill=(255, 255, 255, 130), width=3)
sdg.line([509 * 2, sep_y * 2, 650 * 2, sep_y * 2], fill=(255, 255, 255, 130), width=3)
sf.composite(sep_img)

f_lines = sf.wrap(FACT, "cjk-hk", 30, 640)
fy = sep_y + 52
for ln in f_lines:
    b = sf.text(500, fy, ln, family="cjk-hk", size=30, fill=(30, 42, 66),
                anchor="mt", role="body", line_gap=0.5)
    fy = b.bottom + 15

sf.save(OUT_PATH)
