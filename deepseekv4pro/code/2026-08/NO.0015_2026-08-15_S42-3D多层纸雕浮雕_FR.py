import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 1000, 1680
SCALE = 2
sf = Surface(W, H, scale=SCALE, bg=(8, 6, 16))

def I(v):
    return int(v * SCALE)


def wave_top_points(top_y, amp, phase, x0=0, x1=W, step=6):
    pts = []
    steps = int((x1 - x0) / step)
    for i in range(steps + 1):
        lx = min(x1, x0 + i * step)
        x = I(lx)
        n = (lx - x0) / (x1 - x0) if x1 > x0 else 0
        y = top_y + amp * math.sin(n * 2 * math.pi * 1.5 + phase) \
            + amp * 0.5 * math.cos(n * 2 * math.pi * 2.4 + phase * 1.2)
        pts.append((x, I(y)))
    return pts


def panel_wave_points(top_y, amp, phase, x0=70, x1=930, step=5):
    pts = []
    steps = int((x1 - x0) / step)
    for i in range(steps + 1):
        lx = min(x1, x0 + i * step)
        x = I(lx)
        n = (lx - x0) / (x1 - x0) if x1 > x0 else 0
        y = top_y + amp * math.sin(n * 2 * math.pi + phase) \
            + amp * 0.4 * math.cos(n * 2 * math.pi * 2 + phase * 1.7)
        pts.append((x, I(y)))
    return pts


# 背景渐变：极深暗室
bg = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
top_c = np.array([10, 7, 20], dtype=float).reshape(1, 1, 3)
bottom_c = np.array([30, 18, 44], dtype=float).reshape(1, 1, 3)
bg[..., :3] = (top_c * (1 - yy[..., None]) + bottom_c * yy[..., None]).astype(np.uint8)
bg[..., 3] = 255
sf.composite(bg)

# 人物周围暖光氛围
glow = sf.layer()
Y, X = np.mgrid[0:sf.H, 0:sf.W]
cx_glow, cy_glow = I(500), I(290)
r_glow = np.sqrt((X - cx_glow) ** 2 + (Y - cy_glow) ** 2)
val_glow = np.clip(1 - r_glow / I(430), 0, 1) ** 2.2
glow[..., 0] = (255 * val_glow).astype(np.uint8)
glow[..., 1] = (190 * val_glow).astype(np.uint8)
glow[..., 2] = (120 * val_glow).astype(np.uint8)
glow[..., 3] = (200 * val_glow).astype(np.uint8)
sf.composite(glow, mode="screen", opacity=0.55)

# 多层剪纸波纹，从后往前叠加
bands = [
    (60, 35, 0.0, (20, 13, 31)),
    (190, 55, 1.8, (35, 23, 49)),
    (330, 55, 3.4, (57, 34, 64)),
    (490, 50, 5.1, (85, 49, 82)),
    (660, 42, 0.6, (119, 67, 95)),
    (810, 36, 2.0, (159, 96, 105)),
    (930, 24, 3.8, (207, 139, 119)),
]
bottom_visual = 990

for top_y, amp, phase, color in bands:
    sh = sf.layer()
    sh_img = Image.fromarray(sh)
    d_sh = ImageDraw.Draw(sh_img)
    pts_sh = wave_top_points(top_y + 16, amp * 0.9, phase)
    pts_sh += [(I(W), I(bottom_visual)), (0, I(bottom_visual))]
    d_sh.polygon(pts_sh, fill=(0, 0, 0, 120))
    sh_img = sh_img.filter(ImageFilter.GaussianBlur(I(16)))
    sf.composite(sh_img, mode="normal", opacity=0.65)

    ba = sf.layer()
    ba_img = Image.fromarray(ba)
    d_ba = ImageDraw.Draw(ba_img)
    pts_band = wave_top_points(top_y, amp, phase)
    pts_band += [(I(W), I(bottom_visual)), (0, I(bottom_visual))]
    d_ba.polygon(pts_band, fill=color + (255,))
    highlight = tuple(min(c + 28, 255) for c in color)
    d_ba.line(pts_band[:-2], fill=highlight + (255,), width=I(4))
    sf.composite(ba_img)

# 人影的暖轮廓光与逆光剪影
cx_person, cy_person = 500, 310
rim = sf.layer()
rim_img = Image.fromarray(rim)
d_rim = ImageDraw.Draw(rim_img)
d_rim.ellipse([I(cx_person - 128), I(cy_person - 154), I(cx_person + 128), I(cy_person + 154)],
              fill=(232, 160, 104, 125))
d_rim.rectangle([I(cx_person - 72), I(cy_person + 98), I(cx_person + 72), I(cy_person + 220)],
                fill=(232, 160, 104, 125))
d_rim.ellipse([I(cx_person - 285), I(cy_person + 205), I(cx_person + 285), I(cy_person + 540)],
              fill=(232, 160, 104, 125))
rim_img = rim_img.filter(ImageFilter.GaussianBlur(I(38)))
sf.composite(rim_img, mode="screen", opacity=0.85)

sil = sf.layer()
sil_img = Image.fromarray(sil)
d_sil = ImageDraw.Draw(sil_img)
d_sil.ellipse([I(cx_person - 100), I(cy_person - 126), I(cx_person + 100), I(cy_person + 126)],
              fill=(24, 12, 28, 255))
d_sil.rectangle([I(cx_person - 58), I(cy_person + 94), I(cx_person + 58), I(cy_person + 192)],
                fill=(24, 12, 28, 255))
d_sil.ellipse([I(cx_person - 246), I(cy_person + 184), I(cx_person + 246), I(cy_person + 490)],
              fill=(24, 12, 28, 255))
sf.composite(sil_img)

# 脸部最亮的光核
face = sf.layer()
Yf, Xf = np.mgrid[0:sf.H, 0:sf.W]
cx_face, cy_face = I(500), I(300)
r_face = np.sqrt((Xf - cx_face) ** 2 + (Yf - cy_face) ** 2)
val_face = np.clip(1 - r_face / I(145), 0, 1) ** 2.5
face[..., 0] = (255 * val_face).astype(np.uint8)
face[..., 1] = (190 * val_face).astype(np.uint8)
face[..., 2] = (105 * val_face).astype(np.uint8)
face[..., 3] = (235 * val_face).astype(np.uint8)
sf.composite(face, mode="screen", opacity=0.95)

core = sf.layer()
val_core = np.clip(1 - r_face / I(60), 0, 1) ** 3
core[..., 0] = (255 * val_core).astype(np.uint8)
core[..., 1] = (225 * val_core).astype(np.uint8)
core[..., 2] = (150 * val_core).astype(np.uint8)
core[..., 3] = (255 * val_core).astype(np.uint8)
sf.composite(core, mode="screen", opacity=0.9)

# 微尘与光子颗粒
rng = np.random.default_rng(20260815)
dust = sf.layer()
dust_img = Image.fromarray(dust)
d_dust = ImageDraw.Draw(dust_img)
for _ in range(95):
    x = int(rng.integers(30, sf.W - 30))
    y = int(rng.integers(40, I(960)))
    rad = int(rng.integers(2, 7 * SCALE + 1))
    a = int(rng.integers(45, 165))
    d_dust.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(255, 214, 160, a))
dust_img = dust_img.filter(ImageFilter.GaussianBlur(I(1)))
sf.composite(dust_img, mode="screen", opacity=0.55)

# —— 上层纸片：金句面板 ——
quote_panel_top = 306
quote_panel_bottom = 610
quote_shadow = sf.layer()
qs_img = Image.fromarray(quote_shadow)
d_qs = ImageDraw.Draw(qs_img)
pts_qs = panel_wave_points(quote_panel_top + 14, 13, 0.35)
pts_qs += [(I(930), I(quote_panel_bottom + 14)), (I(70), I(quote_panel_bottom + 14))]
d_qs.polygon(pts_qs, fill=(0, 0, 0, 150))
qs_img = qs_img.filter(ImageFilter.GaussianBlur(I(20)))
sf.composite(qs_img, mode="normal", opacity=0.85)

quote_back = sf.layer()
qb_img = Image.fromarray(quote_back)
d_qb = ImageDraw.Draw(qb_img)
pts_qb = panel_wave_points(quote_panel_top, 11, 0.0)
pts_qb += [(I(930), I(quote_panel_bottom)), (I(70), I(quote_panel_bottom))]
d_qb.polygon(pts_qb, fill=(87, 53, 72, 255))
sf.composite(qb_img)

quote_front = sf.layer()
qf_img = Image.fromarray(quote_front)
d_qf = ImageDraw.Draw(qf_img)
pts_qf = panel_wave_points(quote_panel_top, 9, 1.15)
pts_qf += [(I(930), I(quote_panel_bottom - 8)), (I(70), I(quote_panel_bottom - 8))]
d_qf.polygon(pts_qf, fill=(250, 237, 220, 255))
d_qf.line(pts_qf[:-2], fill=(255, 250, 240, 255), width=I(3))
sf.composite(qf_img)

# —— 下层纸片：冷知识面板 ——
fact_panel_top = 910
fact_panel_bottom = 1595
fact_shadow = sf.layer()
fs_img = Image.fromarray(fact_shadow)
d_fs = ImageDraw.Draw(fs_img)
pts_fs = panel_wave_points(fact_panel_top + 16, 15, 0.5)
pts_fs += [(I(930), I(fact_panel_bottom + 10)), (I(70), I(fact_panel_bottom + 10))]
d_fs.polygon(pts_fs, fill=(0, 0, 0, 150))
fs_img = fs_img.filter(ImageFilter.GaussianBlur(I(24)))
sf.composite(fs_img, mode="normal", opacity=0.85)

fact_back = sf.layer()
fb_img = Image.fromarray(fact_back)
d_fb = ImageDraw.Draw(fb_img)
pts_fb = panel_wave_points(fact_panel_top, 12, 0.0)
pts_fb += [(I(930), I(fact_panel_bottom)), (I(70), I(fact_panel_bottom))]
d_fb.polygon(pts_fb, fill=(97, 57, 76, 255))
sf.composite(fb_img)

fact_front = sf.layer()
ff_img = Image.fromarray(fact_front)
d_ff = ImageDraw.Draw(ff_img)
pts_ff = panel_wave_points(fact_panel_top, 10, 1.1)
pts_ff += [(I(930), I(fact_panel_bottom - 8)), (I(70), I(fact_panel_bottom - 8))]
d_ff.polygon(pts_ff, fill=(248, 235, 219, 255))
d_ff.line(pts_ff[:-2], fill=(255, 250, 240, 255), width=I(3))
sf.composite(ff_img)

# 文字安全区
sf.frame(85, 300, 830, 1280)

def split_bilingual(text):
    text = text.strip()
    if "（" in text and text.endswith("）"):
        idx = text.find("（")
        return text[:idx].strip(), text[idx + 1:-1].strip()
    return text, None

quote_fr, quote_zh_extracted = split_bilingual(QUOTE)
fact_fr, fact_zh_extracted = split_bilingual(FACT)

QUOTE_ZH_FALLBACK = "我们每个人都发着无人能见的光——它并不因此而不真实。"
FACT_ZH_FALLBACK = "人体会自发发出微弱的可见光，强度约为肉眼可感知下限的千分之一。这光芒在下午四点左右达到顶峰，脸部比身体其他部位更亮。"

quote_zh = quote_zh_extracted if quote_zh_extracted else QUOTE_ZH_FALLBACK
fact_zh = fact_zh_extracted if fact_zh_extracted else FACT_ZH_FALLBACK

text_x = 112
max_w = 790
dark = (46, 25, 18)
soft = (95, 62, 42)
meta_fill = (72, 47, 30)

# 上层金句
y = 330
quote_fr_lines = sf.wrap(quote_fr, "serif", 32, max_w)
b1 = sf.text(text_x, y, "\n".join(quote_fr_lines),
             family="serif", size=32, fill=dark,
             anchor="lt", role="quote", line_gap=0.26)
y = b1.bottom + 10

quote_zh_lines = sf.wrap(quote_zh, "cjk-sc", 28, max_w)
b2 = sf.text(text_x, y, "\n".join(quote_zh_lines),
             family="cjk-sc", size=28, fill=soft,
             anchor="lt", role="quote", line_gap=0.20)

# 下层冷知识
y = 1000
fact_fr_lines = sf.wrap(fact_fr, "sans", 28, max_w)
b3 = sf.text(text_x, y, "\n".join(fact_fr_lines),
             family="sans", size=28, fill=dark,
             anchor="lt", role="body", line_gap=0.24)
y = b3.bottom + 14

fact_zh_lines = sf.wrap(fact_zh, "cjk-sc", 28, max_w)
b4 = sf.text(text_x, y, "\n".join(fact_zh_lines),
             family="cjk-sc", size=28, fill=soft,
             anchor="lt", role="body", line_gap=0.20)

serial_y = 1548
sf.serial(text_x, serial_y, SERIAL,
          family="mono", size=20, fill=meta_fill,
          anchor="lb", role="meta", bold=True)
sf.datestamp(text_x + max_w, serial_y, DATE,
             family="mono", size=20, fill=meta_fill,
             anchor="rb", role="meta", bold=True)

sf.save(OUT_PATH)
