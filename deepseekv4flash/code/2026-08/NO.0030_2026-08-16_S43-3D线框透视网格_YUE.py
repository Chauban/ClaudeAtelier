import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

# ─── 画布 ───
W, H = 900, 1700
sf = Surface(W, H, scale=2, bg=(4, 8, 26))
sf.frame(60, 60, 780, 1580)

# ─── 投影与布局常量 ───
CX = 450.0
HORIZON = 850.0
CAM_Y = 2.0
CAM_Z = 5.0
FOV = 550.0
BALL_CY = 3.3
BALL_R = 1.7
GROUND_Y = -1.6
BALL_SCREEN_Y = HORIZON - (BALL_CY - CAM_Y) * (FOV / CAM_Z)

def proj_log(px, py, pz):
    zc = pz + CAM_Z
    s = FOV / zc
    sx = CX + px * s
    sy = HORIZON - (py - CAM_Y) * s
    return sx, sy, s

# ─── 先量 FACT，定 panel 高度 ───
FACT_SIZE = 29
FACT_MAX_W = 650
fact_lines = sf.wrap(FACT, family="cjk-hk", size=FACT_SIZE, max_w=FACT_MAX_W)
fact_text_h = len(fact_lines) * FACT_SIZE * 1.4
PANEL_X0, PANEL_X1 = 80, 820
PANEL_Y0 = 1070
panel_h = int(fact_text_h + 150)
PANEL_Y1 = PANEL_Y0 + panel_h
FACT_X, FACT_Y = 135, 1130

# ═══ Tier 2：背景与装饰 ═══

# 深空渐变
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
lay[..., 0] = (6 + 28 * yy).astype(np.uint8)
lay[..., 1] = (8 + 40 * yy).astype(np.uint8)
lay[..., 2] = (26 + 96 * yy).astype(np.uint8)
lay[..., 3] = 255
sf.composite(lay)

# 球体后的微弱星云光
xx = np.linspace(0, 1, sf.W)[None, :]
yy2 = np.linspace(0, 1, sf.H)[:, None]
d2 = ((xx - 0.5) * 2.3) ** 2 + ((yy2 - BALL_SCREEN_Y / H) * 1.6) ** 2
glow = np.exp(-d2 * 10.0)
lay = sf.layer()
lay[..., 0] = (36 * glow).astype(np.uint8)
lay[..., 1] = (60 * glow).astype(np.uint8)
lay[..., 2] = (130 * glow).astype(np.uint8)
lay[..., 3] = (80 * glow).astype(np.uint8)
sf.composite(lay, mode="screen")

# 星空
rng = np.random.default_rng(20260816)
star_img = Image.fromarray(sf.layer())
sdr = ImageDraw.Draw(star_img)
for _ in range(160):
    x = float(rng.integers(0, sf.W))
    y = float(rng.integers(0, int(sf.H * 0.60)))
    r = float(rng.uniform(0.7, 2.2)) * 2
    b = float(rng.uniform(0.3, 1.0))
    c = (int(130 * b + 50), int(175 * b + 50), int(255 * b + 40), 255)
    if b > 0.82:
        lw = r * 3
        sdr.line([x - lw, y, x + lw, y], fill=c, width=1)
        sdr.line([x, y - lw, x, y + lw], fill=c, width=1)
    sdr.ellipse([x - r, y - r, x + r, y + r], fill=c)
for _ in range(40):
    x = float(rng.integers(0, sf.W))
    y = float(rng.integers(int(sf.H * 0.60), sf.H))
    r = float(rng.uniform(0.6, 1.4)) * 2
    b = float(rng.uniform(0.12, 0.4))
    c = (int(100 * b + 40), int(150 * b + 40), int(255 * b + 30), 255)
    sdr.ellipse([x - r, y - r, x + r, y + r], fill=c)
sf.composite(star_img, mode="screen")

# 透视网格
grid_img = Image.fromarray(sf.layer())
gdr = ImageDraw.Draw(grid_img)
Z_NEAR, Z_FAR = -2.0, 50.0
s_near = FOV / (Z_NEAR + CAM_Z)
s_far = FOV / (Z_FAR + CAM_Z)

def grid_color(t):
    t = max(0.0, min(1.0, t))
    return (int(8 + 42 * t), int(32 + 196 * t), int(64 + 182 * t), 255)

n_seg = 26
for x in np.linspace(-6.0, 6.0, 13):
    zs = np.linspace(Z_NEAR, Z_FAR, n_seg + 1)
    for i in range(n_seg):
        x0, y0, s0 = proj_log(x, GROUND_Y, zs[i])
        x1, y1, s1 = proj_log(x, GROUND_Y, zs[i + 1])
        t = ((s0 + s1) * 0.5 - s_far) / (s_near - s_far)
        gdr.line([(x0 * 2, y0 * 2), (x1 * 2, y1 * 2)], fill=grid_color(t), width=2)

for z in [0.0, 2.0, 4.0, 6.5, 9.5, 13.0, 17.5, 23.0, 30.0, 40.0]:
    x0, y0, s0 = proj_log(-6.0, GROUND_Y, z)
    x1, y1, s1 = proj_log(6.0, GROUND_Y, z)
    t = ((s0 + s1) * 0.5 - s_far) / (s_near - s_far)
    gdr.line([(x0 * 2, y0 * 2), (x1 * 2, y1 * 2)], fill=grid_color(t * 0.8), width=2)

# 地平线发光横线
for i in range(80):
    tt = i / 79
    xl = tt * W * 2
    lum = float(np.exp(-((tt - 0.5) ** 2) * 14.0))
    gdr.line([(xl, HORIZON * 2), (xl + 24, HORIZON * 2)],
             fill=(int(16 + 220 * lum), int(60 + 200 * lum), int(90 + 165 * lum), 255),
             width=3)

# 轨道环
def ring_points(radius, tilt_x, tilt_y, center=(0.0, BALL_CY, 0.0), n=96):
    pts = []
    for i in range(n):
        th = 2.0 * np.pi * i / n
        px0 = radius * np.cos(th)
        py0 = 0.0
        pz0 = radius * np.sin(th)
        ca, sa = np.cos(tilt_x), np.sin(tilt_x)
        y1 = py0 * ca - pz0 * sa
        z1 = py0 * sa + pz0 * ca
        cb, sb = np.cos(tilt_y), np.sin(tilt_y)
        x2 = px0 * cb + z1 * sb
        z2 = -px0 * sb + z1 * cb
        pts.append((center[0] + x2, center[1] + y1, center[2] + z2))
    return pts

ring_img = Image.fromarray(sf.layer())
rdr = ImageDraw.Draw(ring_img)
for ring, wdt, c0, c1 in (
    (ring_points(2.6, 0.7, 0.25), 2, (140, 30, 80), (250, 70, 240)),
    (ring_points(3.3, -0.45, 0.55), 1, (70, 30, 120), (180, 80, 250)),
):
    for i in range(len(ring) - 1):
        x0, y0, s0 = proj_log(*ring[i])
        x1, y1, s1 = proj_log(*ring[i + 1])
        tt = max(0.0, min(1.0, ((s0 + s1) * 0.5 - 70.0) / 100.0))
        col = (
            int(c0[0] + (c1[0] - c0[0]) * tt),
            int(c0[1] + (c1[1] - c0[1]) * tt),
            int(c0[2] + (c1[2] - c0[2]) * tt),
            255,
        )
        rdr.line([(x0 * 2, y0 * 2), (x1 * 2, y1 * 2)], fill=col, width=wdt)

# 线框球体
def sphere_wireframe(r, n_lat=8, n_lon=13, rot_y=0.55, rot_x=0.18):
    lines = []
    for i in range(1, n_lat):
        phi = np.pi * i / n_lat - np.pi / 2.0
        z0 = r * np.sin(phi)
        rr = r * np.cos(phi)
        pts = []
        for j in range(n_lon + 1):
            th = 2.0 * np.pi * j / n_lon
            pts.append((rr * np.cos(th), z0, rr * np.sin(th)))
        lines.append(np.array(pts, dtype=np.float64))
    for j in range(n_lon):
        th = 2.0 * np.pi * j / n_lon
        pts = []
        for i in range(n_lat + 1):
            phi = np.pi * i / n_lat - np.pi / 2.0
            pts.append((r * np.cos(phi) * np.cos(th), r * np.sin(phi), r * np.cos(phi) * np.sin(th)))
        lines.append(np.array(pts, dtype=np.float64))
    cy_, sy_ = np.cos(rot_y), np.sin(rot_y)
    cx_, sx_ = np.cos(rot_x), np.sin(rot_x)
    out = []
    for ln in lines:
        x, y, z = ln[:, 0], ln[:, 1], ln[:, 2]
        x1 = x * cy_ + z * sy_
        z1 = -x * sy_ + z * cy_
        y1 = y
        y2 = y1 * cx_ - z1 * sx_
        z2 = y1 * sx_ + z1 * cx_
        out.append(np.stack([x1, y2, z2], axis=1))
    return out

ball_img = Image.fromarray(sf.layer())
bdr = ImageDraw.Draw(ball_img)
segs = []
for ln in sphere_wireframe(BALL_R):
    for i in range(len(ln) - 1):
        p0, p1 = ln[i], ln[i + 1]
        q0 = (p0[0], p0[1] + BALL_CY, p0[2])
        q1 = (p1[0], p1[1] + BALL_CY, p1[2])
        x0, y0, s0 = proj_log(*q0)
        x1, y1, s1 = proj_log(*q1)
        segs.append((x0, y0, x1, y1, (s0 + s1) * 0.5))
s_vals = [e[4] for e in segs]
lo, hi = min(s_vals), max(s_vals)
for x0, y0, x1, y1, sm in segs:
    t = (sm - lo) / (hi - lo) if hi > lo else 0.5
    col = (int(16 + 205 * t), int(62 + 180 * t), int(104 + 148 * t), 255)
    bdr.line([(x0 * 2, y0 * 2), (x1 * 2, y1 * 2)], fill=col, width=2)

# ─── 发光合成 ───
sf.composite(grid_img.filter(ImageFilter.GaussianBlur(6)), mode="screen", opacity=0.7)
sf.composite(ring_img.filter(ImageFilter.GaussianBlur(10)), mode="screen", opacity=0.75)
sf.composite(ball_img.filter(ImageFilter.GaussianBlur(9)), mode="screen", opacity=0.85)
sf.composite(grid_img, mode="normal", opacity=0.7)
sf.composite(ring_img, mode="normal", opacity=0.8)
sf.composite(ball_img, mode="normal", opacity=0.9)

# FACT 信息面板
panel_img = Image.fromarray(sf.layer())
pdr = ImageDraw.Draw(panel_img)
pdr.rounded_rectangle(
    [PANEL_X0 * 2, PANEL_Y0 * 2, PANEL_X1 * 2, PANEL_Y1 * 2],
    radius=16,
    fill=(5, 14, 38, 205),
    outline=(35, 130, 190, 255),
    width=2,
)
pdr.line(
    [(PANEL_X0 * 2 + 14, PANEL_Y0 * 2 + 16), (PANEL_X0 * 2 + 14, PANEL_Y1 * 2 - 16)],
    fill=(80, 210, 255, 255),
    width=3,
)
sf.composite(panel_img)

# HUD 角标装饰
hud_img = Image.fromarray(sf.layer())
hdr = ImageDraw.Draw(hud_img)
hdr.line([(85 * 2, 66 * 2), (85 * 2, 84 * 2)], fill=(70, 200, 255, 255), width=2)
hdr.line([(85 * 2, 66 * 2), (112 * 2, 66 * 2)], fill=(70, 200, 255, 255), width=2)
hdr.line([(815 * 2, 66 * 2), (815 * 2, 84 * 2)], fill=(70, 200, 255, 255), width=2)
hdr.line([(815 * 2, 66 * 2), (788 * 2, 66 * 2)], fill=(70, 200, 255, 255), width=2)
for i in range(17):
    tx = 340 + i * 13
    ty = 70 if i % 3 else 66
    hdr.line([(tx * 2, ty * 2), ((tx + 7) * 2, ty * 2)], fill=(50, 160, 230, 255), width=1)
sf.composite(hud_img, mode="screen", opacity=0.7)

# ═══ Tier 1：文字 ═══
sf.serial(85, 96, SERIAL, family="mono", size=22, fill=(130, 238, 255), anchor="lt", role="meta")
sf.datestamp(815, 96, DATE, family="mono", size=22, fill=(130, 238, 255), anchor="rt", role="meta")

q1 = sf.text(450, 300, "冇番茄，咪用蕉；", family="cjk-hk", size=54,
             fill=(176, 246, 255), anchor="mt", role="quote")
sf.text(450, q1.bottom + 22, "冇得揀，先至有得諗。", family="cjk-hk", size=54,
        fill=(176, 246, 255), anchor="mt", role="quote")

sf.text(FACT_X, FACT_Y, FACT, family="cjk-hk", size=FACT_SIZE,
        fill=(226, 247, 255), anchor="lt", role="body", max_w=FACT_MAX_W, line_gap=0.4)

sf.save(OUT_PATH)
