from atelier_canvas import Surface
import numpy as np
import math
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1360
sf = Surface(W, H, scale=2, bg=(6, 9, 20))
sf.frame(70, 70, W - 140, H - 140)

PW, PH = sf.W, sf.H
HOR = 640
VX = 500


def P(v):
    return int(round(v * 2))


def radial_glow_arr(cx, cy, radius, color, amp):
    yy, xx = np.mgrid[0:PH, 0:PW]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / radius
    a = np.clip(1.0 - d, 0.0, 1.0) ** 2 * amp
    out = np.zeros((PH, PW, 4), np.uint8)
    out[..., 0] = color[0]
    out[..., 1] = color[1]
    out[..., 2] = color[2]
    out[..., 3] = a.astype(np.uint8)
    return out


# ================= Tier 2: 背景与装饰 =================

# 深空渐变
lay = sf.layer()
yy = np.linspace(0, 1, PH)[:, None]
lay[..., 0] = (8 + 10 * (1 - yy)).astype(np.uint8)
lay[..., 1] = (12 + 16 * (1 - yy)).astype(np.uint8)
lay[..., 2] = (26 + 42 * (1 - yy)).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# 中央光芒
sf.composite(radial_glow_arr(P(500), P(545), P(360), (70, 170, 255), 46), mode="screen", opacity=0.85)

# 星空
np.random.seed(2026)
stars = np.zeros((PH, PW, 4), np.uint8)
n = 380
sx = np.random.randint(0, PW, n)
sy = np.random.randint(0, P(HOR) - 40, n)
sb = np.random.randint(60, 230, n)
stars[sy, sx, 0] = 195
stars[sy, sx, 1] = 222
stars[sy, sx, 2] = 255
stars[sy, sx, 3] = sb
n2 = n // 4
sx2 = np.random.randint(0, PW - 2, n2)
sy2 = np.random.randint(0, P(HOR) - 40, n2)
sb2 = np.random.randint(120, 255, n2)
for i in range(n2):
    stars[sy2[i]:sy2[i] + 2, sx2[i]:sx2[i] + 2, 0] = 205
    stars[sy2[i]:sy2[i] + 2, sx2[i]:sx2[i] + 2, 1] = 228
    stars[sy2[i]:sy2[i] + 2, sx2[i]:sx2[i] + 2, 2] = 255
    stars[sy2[i]:sy2[i] + 2, sx2[i]:sx2[i] + 2, 3] = sb2[i]
sf.composite(stars, mode="screen", opacity=0.95)

# 亮星十字
star_img = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
gds = ImageDraw.Draw(star_img)
for (bx, by, br) in [(160, 190, 4), (810, 250, 3), (330, 110, 3), (860, 430, 4), (120, 490, 3)]:
    bx, by, br = P(bx), P(by), P(br)
    gds.line([bx - br * 3, by, bx + br * 3, by], fill=(210, 235, 255, 170), width=1)
    gds.line([bx, by - br * 3, bx, by + br * 3], fill=(210, 235, 255, 170), width=1)
    gds.ellipse([bx - br, by - br, bx + br, by + br], fill=(230, 245, 255, 220))
sf.composite(star_img, mode="screen", opacity=1.0)

# 地平线辉光
hl = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
gdh = ImageDraw.Draw(hl)
gdh.line([0, P(HOR), PW, P(HOR)], fill=(110, 220, 255, 90), width=3)
hl = hl.filter(ImageFilter.GaussianBlur(6))
sf.composite(hl, mode="screen", opacity=0.8)


# 透视网格
def build_grid(line_w=1, alpha_base=150):
    img = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(img)
    hor, vx = P(HOR), P(VX)
    f = 1100.0
    z = 0.55
    while True:
        y = hor + f / z
        if y > PH + 80:
            z *= 1.12
            continue
        if y < hor + 15:
            break
        t = (y - hor) / (PH - hor)
        spread = 120 + 860 * t
        alpha = max(30, int(alpha_base * (0.35 + 0.65 * t)))
        gd.line([int(vx - spread), int(y), int(vx + spread), int(y)],
                fill=(95, 212, 255, alpha), width=line_w)
        z *= 1.12
    for k in range(-16, 17):
        xb = vx + k * 64
        alpha = int(alpha_base * 0.6)
        gd.line([vx, hor, int(xb), int(PH)], fill=(95, 212, 255, alpha), width=line_w)
    return img


grid_glow = build_grid(line_w=8, alpha_base=60).filter(ImageFilter.GaussianBlur(10))
sf.composite(grid_glow, mode="screen", opacity=0.8)
grid_sharp = build_grid(line_w=2, alpha_base=150)
sf.composite(grid_sharp, mode="screen", opacity=0.95)

# 数据链路虚线
link_img = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
gdl = ImageDraw.Draw(link_img)
for (tx, ty) in [(195, 430), (820, 700)]:
    x1, y1 = 500, 525
    dist = math.hypot(tx - x1, ty - y1)
    steps = int(dist / 16)
    if steps < 2:
        continue
    for i in range(0, steps, 2):
        t0 = i / steps
        t1 = min(1.0, (i + 1) / steps)
        xa, ya = x1 + (tx - x1) * t0, y1 + (ty - y1) * t0
        xb, yb = x1 + (tx - x1) * t1, y1 + (ty - y1) * t1
        gdl.line([P(xa), P(ya), P(xb), P(yb)], fill=(120, 220, 255, 90), width=1)
sf.composite(link_img, mode="screen", opacity=0.7)


# 线框球体
def sphere_segments(cx, cy, r):
    segs = []
    f = 900.0
    for i in range(12):
        lon = i * math.pi / 6.0
        pts = []
        for j in range(50):
            lat = -math.pi / 2 + math.pi * j / 49.0
            x = r * math.cos(lat) * math.cos(lon)
            y = r * math.sin(lat)
            z = r * math.cos(lat) * math.sin(lon)
            s = f / (f + z)
            pts.append((cx + x * s, cy + y * s))
        segs.append(pts)
    for j in range(1, 9):
        lat = -math.pi / 2 + math.pi * j / 9.0
        pts = []
        for i in range(60):
            lon = 2 * math.pi * i / 59.0
            x = r * math.cos(lat) * math.cos(lon)
            y = r * math.sin(lat)
            z = r * math.cos(lat) * math.sin(lon)
            s = f / (f + z)
            pts.append((cx + x * s, cy + y * s))
        segs.append(pts)
    return segs


def draw_segments(img, segs, color, line_w):
    gd = ImageDraw.Draw(img)
    for seg in segs:
        pts = [(P(px), P(py)) for (px, py) in seg]
        gd.line(pts, fill=color, width=line_w)


segs = sphere_segments(500, 525, 140)
sph_glow = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
draw_segments(sph_glow, segs, (90, 210, 255, 90), 10)
sph_glow = sph_glow.filter(ImageFilter.GaussianBlur(7))
sf.composite(sph_glow, mode="screen", opacity=0.9)
sph_sharp = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
draw_segments(sph_sharp, segs, (170, 235, 255, 230), 2)
sf.composite(sph_sharp, mode="screen", opacity=1.0)

core = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
gdc = ImageDraw.Draw(core)
r0 = 6
gdc.ellipse([P(500) - r0, P(525) - r0, P(500) + r0, P(525) + r0], fill=(225, 248, 255, 230))
core = core.filter(ImageFilter.GaussianBlur(3))
sf.composite(core, mode="screen", opacity=1.0)


# 轨道环
def draw_orbit(img, cx, cy, a, b, tilt, color, line_w):
    gd = ImageDraw.Draw(img)
    pts = []
    for t in np.linspace(0, 2 * math.pi, 100):
        x = a * math.cos(t)
        y = b * math.sin(t)
        xr = x * math.cos(tilt) - y * math.sin(tilt)
        yr = x * math.sin(tilt) + y * math.cos(tilt)
        pts.append((P(cx + xr), P(cy + yr)))
    gd.line(pts, fill=color, width=line_w)


orb_glow = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
draw_orbit(orb_glow, 500, 545, 240, 85, 0.42, (80, 190, 255, 70), 8)
orb_glow = orb_glow.filter(ImageFilter.GaussianBlur(6))
sf.composite(orb_glow, mode="screen", opacity=0.8)
orb_sharp = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
draw_orbit(orb_sharp, 500, 545, 240, 85, 0.42, (140, 225, 255, 170), 2)
sf.composite(orb_sharp, mode="screen", opacity=1.0)


# 悬浮线框立方体
def cube_edges(cx, cy, size, rot):
    a = size / 2.0
    pts3 = []
    for dx in (-a, a):
        for dy in (-a, a):
            for dz in (-a, a):
                x1 = dx * math.cos(rot) + dz * math.sin(rot)
                z1 = -dx * math.sin(rot) + dz * math.cos(rot)
                y2 = dy * math.cos(rot * 0.7) - z1 * math.sin(rot * 0.7)
                z2 = dy * math.sin(rot * 0.7) + z1 * math.cos(rot * 0.7)
                f = 900.0
                s = f / (f + z2 + 400)
                pts3.append((cx + x1 * s, cy + y2 * s))
    edges = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    return [[pts3[i], pts3[j]] for (i, j) in edges]


def add_cube(cx, cy, size, rot):
    g_img = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    gd_tmp = ImageDraw.Draw(g_img)
    for (p1, p2) in cube_edges(cx, cy, size, rot):
        gd_tmp.line([P(p1[0]), P(p1[1]), P(p2[0]), P(p2[1])], fill=(90, 210, 255, 70), width=8)
    g_img = g_img.filter(ImageFilter.GaussianBlur(6))
    sf.composite(g_img, mode="screen", opacity=0.8)
    s_img = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    gd_tmp2 = ImageDraw.Draw(s_img)
    for (p1, p2) in cube_edges(cx, cy, size, rot):
        gd_tmp2.line([P(p1[0]), P(p1[1]), P(p2[0]), P(p2[1])], fill=(160, 230, 255, 190), width=2)
    sf.composite(s_img, mode="screen", opacity=1.0)


add_cube(195, 430, 68, 0.6)
add_cube(820, 700, 52, -0.4)

# 网格数据点
np.random.seed(31)
pts_img = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
gdp = ImageDraw.Draw(pts_img)
for _ in range(80):
    x = np.random.randint(120, 880)
    y = np.random.randint(HOR + 15, H - 40)
    t = (y - HOR) / (H - HOR)
    a = int(150 * (0.3 + 0.7 * t))
    r = max(1, int(2.2 * t))
    gdp.ellipse([P(x - r), P(y - r), P(x + r), P(y + r)], fill=(160, 230, 255, a))
sf.composite(pts_img, mode="screen", opacity=0.9)

# 小线框符号
sym_img = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
gdsym = ImageDraw.Draw(sym_img)
np.random.seed(77)
for _ in range(14):
    x = np.random.randint(140, 860)
    y = np.random.randint(HOR + 55, 820)
    t = (y - HOR) / (820 - HOR)
    s = 5 + 9 * t
    alpha = int(110 + 80 * t)
    col = (170, 235, 255, alpha)
    kind = np.random.randint(3)
    if kind == 0:
        gdsym.line([P(x), P(y - s), P(x - s), P(y + s), P(x + s), P(y + s), P(x), P(y - s)], fill=col, width=1)
    elif kind == 1:
        gdsym.line([P(x - s), P(y - s), P(x + s), P(y - s), P(x + s), P(y + s), P(x - s), P(y + s), P(x - s), P(y - s)], fill=col, width=1)
    else:
        gdsym.line([P(x), P(y - s), P(x - s), P(y), P(x), P(y + s), P(x + s), P(y), P(x), P(y - s)], fill=col, width=1)
sf.composite(sym_img, mode="screen", opacity=0.8)

# 底部数据波形
wave = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
gdw = ImageDraw.Draw(wave)
pts = []
for x in range(130, 870, 6):
    y = H - 65 + 16 * math.sin(x * 0.018) + 11 * math.sin(x * 0.043 + 1.2)
    pts.append((P(x), P(y)))
gdw.line(pts, fill=(100, 210, 255, 110), width=2)
sf.composite(wave, mode="screen", opacity=0.55)

# FACT 区域压暗带
band = np.zeros((PH, PW, 4), np.uint8)
y0, y1 = P(840), P(1210)
hgt = y1 - y0
alpha = (0.5 * np.sin(np.linspace(0, math.pi, hgt)) * 255).astype(np.uint8)
band[y0:y1, :, 3] = alpha[:, None]
sf.composite(band, mode="normal", opacity=1.0)

# QUOTE 背景微光
sf.composite(radial_glow_arr(P(500), P(230), P(300), (90, 190, 255), 26), mode="screen", opacity=0.6)

# 四角测量角标
ticks = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
gdt = ImageDraw.Draw(ticks)
tc = (110, 215, 255, 130)
gdt.line([P(62), P(72), P(62), P(88)], fill=tc, width=2)
gdt.line([P(62), P(72), P(78), P(72)], fill=tc, width=2)
gdt.line([P(938), P(72), P(938), P(88)], fill=tc, width=2)
gdt.line([P(938), P(72), P(922), P(72)], fill=tc, width=2)
gdt.line([P(62), P(H - 72), P(62), P(H - 88)], fill=tc, width=2)
gdt.line([P(62), P(H - 88), P(78), P(H - 88)], fill=tc, width=2)
gdt.line([P(938), P(H - 72), P(938), P(H - 88)], fill=tc, width=2)
gdt.line([P(938), P(H - 88), P(922), P(H - 88)], fill=tc, width=2)
sf.composite(ticks, mode="screen", opacity=0.8)

# ================= Tier 1: 文字 =================

sf.serial(90, 88, SERIAL, family="mono", size=24, fill=(140, 225, 255), anchor="lt", role="meta")
sf.datestamp(W - 90, 88, DATE, family="mono", size=24, fill=(140, 225, 255), anchor="rt", role="meta")

b_q1 = sf.text(W // 2, 150, "你以为是千年的凝视，", family="cjk-sc", size=48,
               fill=(240, 250, 255), anchor="mt", role="quote")
b_q2 = sf.text(W // 2, b_q1.bottom + 28, "其实不过一百多年的眺望。", family="cjk-sc", size=48,
               fill=(240, 250, 255), anchor="mt", role="quote")

fact_lines = sf.wrap(FACT, "cjk-sc", 28, 820)
fy = 885
for ln in fact_lines:
    b_f = sf.text(W // 2, fy, ln, family="cjk-sc", size=28,
                  fill=(215, 238, 255), anchor="mt", role="body")
    fy = b_f.bottom + int(28 * 1.5)

sf.save(OUT_PATH)
