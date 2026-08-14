import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

SC = 2
W, H = 1000, 1500

sf = Surface(W, H, scale=2, bg=(30, 34, 44))
sf.frame(110, 190, 780, 1010)

wpx, hpx = sf.W, sf.H
rng = np.random.default_rng(17)
rng2 = np.random.default_rng(42)

# ===== 排版预估 =====
qlines = sf.wrap(QUOTE, "serif-cjk", 56, 700)
qstep = 84
q_top = 400
q_bottom = q_top + qstep * len(qlines)
sep_y = q_bottom + 48
f_top = sep_y + 56
flines = sf.wrap(FACT, "cjk-tc", 34, 700)
fstep = 58

# ===== 背景渐变 =====
bg = sf.layer()
yy = np.linspace(0, 1, hpx)[:, None]
topc = np.array([54, 58, 72])
botc = np.array([20, 23, 32])
for c in range(3):
    bg[..., c] = (topc[c] * (1 - yy) + botc[c] * yy).astype(np.uint8)
bg[..., 3] = 255
sf.composite(bg)

# 柔和氛围光
glow = sf.layer()
gx = np.linspace(-1.5, 1.5, wpx)[None, :]
gy = np.linspace(-1.4, 1.5, hpx)[:, None]
r2f = gx ** 2 + gy ** 2
fall = np.clip(1 - r2f * 0.55, 0, 1)
glow[..., 0] = (84 * fall).astype(np.uint8)
glow[..., 1] = (90 * fall).astype(np.uint8)
glow[..., 2] = (108 * fall).astype(np.uint8)
glow[..., 3] = (55 * fall).astype(np.uint8)
sf.composite(glow)


# ===== 波浪纸层（剪影山峦，多层投影） =====
def wave_poly(base_y, amp, freq, phase):
    pts = []
    for lx in range(0, W + 4, 4):
        wy = base_y + amp * math.sin(2 * math.pi * freq * lx / W + phase)
        pts.append((lx * SC, wy * SC))
    pts.append((W * SC, H * SC))
    pts.append((0, H * SC))
    return pts


def draw_wave_fill(base_y, amp, freq, phase, rgb):
    pts = wave_poly(base_y, amp, freq, phase)
    mask = Image.new("L", (wpx, hpx), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    lay = np.zeros((hpx, wpx, 4), dtype=np.uint8)
    shv = np.linspace(0, 1, hpx)[:, None]
    for c in range(3):
        lay[..., c] = np.clip(rgb[c] * (1.0 - 0.13 * shv), 0, 255).astype(np.uint8)
    lay[..., 3] = np.array(mask)
    sf.composite(lay)
    hi = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    ImageDraw.Draw(hi).line(pts[:-2], fill=(250, 244, 230, 60), width=int(3 * SC))
    hi = hi.filter(ImageFilter.GaussianBlur(2))
    sf.composite(hi)


def draw_wave_shadow(base_y, amp, freq, phase, dy=16):
    pts = wave_poly(base_y + dy, amp, freq, phase)
    sh = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon(pts, fill=(10, 14, 24, 95))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    sf.composite(sh)


draw_wave_fill(1150, 140, 1.1, 1.2, (74, 84, 98))
draw_wave_shadow(1300, 120, 0.9, 2.6, 16)
draw_wave_fill(1300, 120, 0.9, 2.6, (96, 108, 122))
draw_wave_shadow(1410, 80, 1.2, 0.4, 14)
draw_wave_fill(1410, 80, 1.2, 0.4, (128, 141, 155))

# ===== 尘埃粒子 =====
dust = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
dd = ImageDraw.Draw(dust)
for _ in range(60):
    px = float(rng.uniform(0, W)) * SC
    py = float(rng.uniform(0, H)) * SC
    pr = float(rng.uniform(1.0, 3.0)) * SC
    al = int(rng.uniform(18, 48))
    dd.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(240, 234, 220, al))
dust = dust.filter(ImageFilter.GaussianBlur(2 * SC))
sf.composite(dust)

# ===== 主纸片堆叠 =====
px0, py0, px1, py1 = 110, 200, 890, 1180
rad = 28

sh = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle(
    [(px0 + 16) * SC, (py0 + 24) * SC, (px1 + 16) * SC, (py1 + 24) * SC],
    radius=rad * SC, fill=(8, 10, 18, 185))
sh = sh.filter(ImageFilter.GaussianBlur(32))
sf.composite(sh)

for ox, oy, col in [(24, 34, (208, 199, 179)), (12, 18, (227, 219, 202))]:
    sheet = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    ImageDraw.Draw(sheet).rounded_rectangle(
        [(px0 + ox) * SC, (py0 + oy) * SC, (px1 + ox) * SC, (py1 + oy) * SC],
        radius=rad * SC, fill=(*col, 255))
    sf.composite(sheet)

paper = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
ImageDraw.Draw(paper).rounded_rectangle(
    [px0 * SC, py0 * SC, px1 * SC, py1 * SC], radius=rad * SC, fill=(247, 242, 231, 255))
arr = np.array(paper).astype(np.float32)
shv = np.linspace(0, 1, hpx)[:, None]
arr[..., 0] *= (1.0 - 0.05 * shv)
arr[..., 1] *= (1.0 - 0.055 * shv)
arr[..., 2] *= (1.0 - 0.06 * shv)
arr[..., 0:3] += rng2.normal(0, 2.0, (hpx, wpx, 1))
arr = np.clip(arr, 0, 255).astype(np.uint8)
sf.composite(arr)

hi = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
ImageDraw.Draw(hi).rounded_rectangle(
    [px0 * SC + 2, py0 * SC + 2, px1 * SC - 4, py1 * SC - 4],
    radius=(rad - 1) * SC, outline=(255, 253, 247, 90), width=int(2 * SC))
hi = hi.filter(ImageFilter.GaussianBlur(1))
sf.composite(hi)

# ===== 图钉 =====
pin = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
pnd = ImageDraw.Draw(pin)
pcx, pcy = 500 * SC, 193 * SC
pnd.ellipse([pcx - 13 * SC + 4, pcy - 13 * SC + 6, pcx + 13 * SC + 4, pcy + 13 * SC + 6],
            fill=(58, 50, 40, 120))
pnd.ellipse([pcx - 13 * SC, pcy - 13 * SC, pcx + 13 * SC, pcy + 13 * SC], fill=(92, 84, 72, 235))
pnd.ellipse([pcx - 8 * SC, pcy - 9 * SC, pcx - 1 * SC, pcy - 2 * SC], fill=(205, 198, 186, 220))
sf.composite(pin)

# ===== 漂浮小纸片 =====
def draw_paper_bit(cx, cy, size, ang, rgb):
    half = size / 2
    ca, sa = math.cos(ang), math.sin(ang)
    pts = [((cx + dx * ca - dy * sa) * SC, (cy + dx * sa + dy * ca) * SC)
           for dx, dy in [(-half, -half), (half, -half), (half, half), (-half, half)]]
    bit = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    ImageDraw.Draw(bit).polygon(pts, fill=(*rgb, 210))
    sf.composite(bit)


draw_paper_bit(88, 178, 30, 0.5, (222, 214, 197))
draw_paper_bit(912, 168, 22, -0.3, (233, 226, 210))
draw_paper_bit(918, 460, 18, 0.4, (213, 205, 188))
draw_paper_bit(82, 700, 22, -0.6, (222, 214, 197))

# ===== 底部圆形纸雕（原子意象：多层错位圆环） =====
dcx, dcy, dr = 500, 1330, 140

dsh = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
ImageDraw.Draw(dsh).ellipse(
    [(dcx - dr + 12) * SC, (dcy - dr + 16) * SC, (dcx + dr + 12) * SC, (dcy + dr + 16) * SC],
    fill=(10, 12, 20, 165))
dsh = dsh.filter(ImageFilter.GaussianBlur(26))
sf.composite(dsh)

disk = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
ImageDraw.Draw(disk).ellipse(
    [(dcx - dr) * SC, (dcy - dr) * SC, (dcx + dr) * SC, (dcy + dr) * SC],
    fill=(241, 234, 219, 255))
darr = np.array(disk).astype(np.float32)
ndv = np.linspace(0, 1, hpx)[:, None]
darr[..., 0] *= (1.0 - 0.03 * ndv)
darr[..., 1] *= (1.0 - 0.035 * ndv)
darr[..., 2] *= (1.0 - 0.04 * ndv)
darr[..., 0:3] += rng2.normal(0, 1.5, (hpx, wpx, 1))
darr = np.clip(darr, 0, 255).astype(np.uint8)
sf.composite(darr)

edge = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
ImageDraw.Draw(edge).ellipse(
    [(dcx - dr + 2) * SC, (dcy - dr + 2) * SC, (dcx + dr - 2) * SC, (dcy + dr - 2) * SC],
    outline=(171, 160, 138, 120), width=int(2 * SC))
edge = edge.filter(ImageFilter.GaussianBlur(1))
sf.composite(edge)


def draw_ring(cx, cy, rad_, stroke, rgb, dx=6, dy=8):
    shd = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    ImageDraw.Draw(shd).ellipse(
        [(cx - rad_ + dx) * SC, (cy - rad_ + dy) * SC,
         (cx + rad_ + dx) * SC, (cy + rad_ + dy) * SC],
        outline=(58, 50, 40, 100), width=int(stroke * SC))
    shd = shd.filter(ImageFilter.GaussianBlur(7))
    sf.composite(shd)
    ring = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse(
        [(cx - rad_) * SC, (cy - rad_) * SC,
         (cx + rad_) * SC, (cy + rad_) * SC],
        outline=(*rgb, 255), width=int(stroke * SC))
    sf.composite(ring)


def draw_dot(cx, cy, rad_, rgb, dx=4, dy=6):
    shd = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    ImageDraw.Draw(shd).ellipse(
        [(cx - rad_ + dx) * SC, (cy - rad_ + dy) * SC,
         (cx + rad_ + dx) * SC, (cy + rad_ + dy) * SC],
        fill=(58, 50, 40, 90))
    shd = shd.filter(ImageFilter.GaussianBlur(6))
    sf.composite(shd)
    dot = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    ImageDraw.Draw(dot).ellipse(
        [(cx - rad_) * SC, (cy - rad_) * SC,
         (cx + rad_) * SC, (cy + rad_) * SC],
        fill=(*rgb, 255))
    sf.composite(dot)


draw_ring(dcx - 8, dcy - 12, 118, 11, (196, 203, 210))
draw_ring(dcx + 18, dcy + 10, 76, 9, (212, 204, 188))
draw_ring(dcx - 4, dcy + 8, 44, 8, (226, 214, 197))
draw_dot(dcx + 26, dcy - 10, 16, (216, 170, 148))
draw_dot(dcx + 110, dcy - 42, 10, (196, 203, 210))
draw_dot(dcx - 110, dcy + 44, 10, (212, 204, 188))
draw_dot(dcx + 40, dcy + 88, 10, (226, 214, 197))

# ===== 分隔装饰线 =====
deco = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
dd2 = ImageDraw.Draw(deco)
ly = sep_y * SC
dd2.line([240 * SC, ly, 404 * SC, ly], fill=(128, 110, 82, 160), width=int(2 * SC))
dd2.line([596 * SC, ly, 760 * SC, ly], fill=(128, 110, 82, 160), width=int(2 * SC))
dcxm, dcym = 500 * SC, ly
dd2.polygon([(dcxm, dcym - 7 * SC), (dcxm + 7 * SC, dcym),
             (dcxm, dcym + 7 * SC), (dcxm - 7 * SC, dcym)],
            fill=(128, 110, 82, 200))
sf.composite(deco)

# ===== 文字（Tier 1） =====
sf.serial(130, 260, SERIAL, family="serif-cjk", size=21, fill=(81, 69, 54),
          anchor="lt", role="meta")
sf.datestamp(870, 260, DATE, family="serif-cjk", size=21, fill=(81, 69, 54),
             anchor="rt", role="meta")

qy = q_top
for line in qlines:
    wq = sf.measure(line, "serif-cjk", 56)[0]
    sf.text(120 + (700 - wq) / 2, qy, line, family="serif-cjk", size=56,
            fill=(58, 48, 40), anchor="lt", role="quote", max_w=700)
    qy += qstep

fy = f_top
for line in flines:
    sf.text(120, fy, line, family="cjk-tc", size=34,
            fill=(58, 48, 40), anchor="lt", role="body", max_w=700)
    fy += fstep

sf.save(OUT_PATH)
