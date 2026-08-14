from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WL, HL = 1000, 1180
S = 2
W, H = WL * S, HL * S

def lp(x):
    return int(x * S)

INK = (30, 18, 8)

sf = Surface(WL, HL, scale=S, bg=(188, 156, 112))

# ── aged kraft paper background ─────────────────────────────
lay = sf.layer()
yy = np.linspace(0, 1, H)[:, None].astype(np.float32)
xx = np.linspace(0, 1, W)[None, :].astype(np.float32)
yv = yy[:, 0][:, None]

rng = np.random.default_rng(7)
noise = rng.normal(0, 6, (H, W)).astype(np.float32)
noise_img = Image.fromarray(np.clip((noise + 15) * 255 / 30, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12))
noise_blur = np.asarray(noise_img).astype(np.float32) / 255 * 30 - 15

base = np.zeros((H, W, 3), dtype=np.float32)
base[..., 0] = 188 + 10 * yv
base[..., 1] = 156 + 8 * yv
base[..., 2] = 112 + 4 * yv
base += noise_blur[..., None]

blot = rng.normal(0, 10, (H // 8, W // 8)).astype(np.float32)
blot_img = Image.fromarray(np.clip((blot + 20) * 255 / 40, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
blot_large = np.asarray(blot_img).astype(np.float32) / 255 * 30 - 15
base += blot_large[..., None]

dist = np.sqrt(((xx - 0.5) * 1.4) ** 2 + ((yv - 0.9) * 0.85) ** 2)
vig = 1 - 0.38 * np.clip(dist, 0, 1)
base *= vig[..., None]
base = np.clip(base, 0, 255).astype(np.uint8)

lay[..., :3] = base
lay[..., 3] = 255
sf.composite(lay)

# ── layout constants ────────────────────────────────────────
QS = 46
QLG = 0.5
Q_LH = int(QS * (1 + QLG))           # 69
Q_MAXW = 780
q_lines = sf.wrap(QUOTE, "serif-cjk", QS, Q_MAXW, bold=False)
q_start = 190
q_end = q_start + len(q_lines) * Q_LH

swatch_y = q_end + 40
swatch_h = 125
swatch_bottom = swatch_y + swatch_h

FS = 28
FLG = 0.58
f_lh = int(FS * (1 + FLG)) + 8        # 52
F_MAXW = 800
f_lines = sf.wrap(FACT, "cjk-tc", FS, F_MAXW, bold=False)
f_start = swatch_bottom + 54
f_box_h = 41
f_text_bottom = f_start + (len(f_lines) - 1) * f_lh + f_box_h
f_panel_top = f_start - 16
f_panel_bottom = f_text_bottom + 18

jar_body_top = f_panel_bottom + 92
neck_top = jar_body_top - 55
rim_top = neck_top - 8
cork_top = rim_top - 26
jar_body_bottom = jar_body_top + 105

# ── decorative layer ───────────────────────────────────────
deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)

# outer and inner frames
d.rectangle([lp(55), lp(55), lp(945), lp(1125)], outline=(70, 45, 20, 200), width=lp(3))
d.rectangle([lp(65), lp(65), lp(935), lp(1115)], outline=(70, 45, 20, 140), width=lp(1))

# top library band, no text — only stamped ornament
d.rectangle([lp(65), lp(80), lp(935), lp(150)], fill=(110, 80, 50, 150),
            outline=(70, 45, 20, 220), width=lp(1))
d.ellipse([lp(458), lp(91), lp(542), lp(139)], outline=(30, 18, 8, 180), width=lp(2))
d.ellipse([lp(470), lp(101), lp(530), lp(129)], outline=(30, 18, 8, 120), width=lp(1))
d.line([lp(80), lp(115), lp(410), lp(115)], fill=(70, 45, 20, 140), width=lp(1))
d.line([lp(590), lp(115), lp(920), lp(115)], fill=(70, 45, 20, 140), width=lp(1))

# clean reading panels behind quote and body
d.rounded_rectangle([lp(100), lp(176), lp(900), lp(q_end + 18)], radius=12,
                    fill=(210, 182, 140, 235), outline=(70, 45, 20, 120), width=1)
d.rounded_rectangle([lp(68), lp(f_panel_top), lp(932), lp(f_panel_bottom)], radius=10,
                    fill=(208, 178, 136, 240), outline=(70, 45, 20, 120), width=1)

# old stains, kept in clear zones
for cx, cy, r in [(230, 650, 95), (230, 650, 42), (755, 990, 80), (755, 990, 34)]:
    d.ellipse([lp(cx - r), lp(cy - r), lp(cx + r), lp(cy + r)], outline=(170, 135, 80, 55), width=lp(3))

# paint swatch
for bx0, by0, bx1, by1 in [
    (430, swatch_y, 570, swatch_y + swatch_h),
    (398, swatch_y + 16, 522, swatch_y + swatch_h - 10),
    (478, swatch_y - 8, 622, swatch_y + swatch_h + 12),
    (450, swatch_y + 8, 590, swatch_y + swatch_h + 20),
]:
    d.ellipse([lp(bx0), lp(by0), lp(bx1), lp(by1)], fill=(139, 90, 43, 180))

rng2 = np.random.default_rng(11)
for _ in range(42):
    gx = 435 + rng2.random() * 130
    gy = swatch_y + 12 + rng2.random() * (swatch_h - 24)
    d.ellipse([lp(gx), lp(gy), lp(gx + 6), lp(gy + 6)], fill=(60, 38, 18, 190))

d.line([lp(340), lp(swatch_y + swatch_h // 2), lp(395), lp(swatch_y + swatch_h // 2)],
       fill=(70, 45, 20, 160), width=lp(2))
d.line([lp(605), lp(swatch_y + swatch_h // 2), lp(660), lp(swatch_y + swatch_h // 2)],
       fill=(70, 45, 20, 160), width=lp(2))

# glass pigment jar
d.ellipse([lp(455), lp(jar_body_top), lp(545), lp(jar_body_bottom)],
          fill=(85, 55, 30, 120), outline=(70, 45, 20, 200), width=lp(2))
d.rectangle([lp(485), lp(neck_top), lp(515), lp(jar_body_top + 4)],
            fill=(85, 55, 30, 120), outline=(70, 45, 20, 200), width=lp(1))
d.rectangle([lp(478), lp(rim_top), lp(522), lp(neck_top + 8)],
            fill=(110, 80, 50, 180), outline=(70, 45, 20, 220), width=lp(1))
d.rectangle([lp(482), lp(cork_top), lp(518), lp(rim_top)],
            fill=(120, 85, 45, 210), outline=(70, 45, 20, 200), width=lp(1))

label_top = jar_body_top + 38
label_bottom = jar_body_top + 96
d.rectangle([lp(462), lp(label_top), lp(538), lp(label_bottom)],
            fill=(205, 175, 120, 220), outline=(70, 45, 20, 200), width=lp(1))
d.ellipse([lp(475), lp(label_top + 22), lp(525), lp(label_top + 68)],
          fill=(139, 90, 43, 210))

# bottom archival tag panels for serial and date
tag_y = 1032
tag_h = 38
d.rounded_rectangle([lp(80), lp(tag_y), lp(270), lp(tag_y + tag_h)], radius=6,
                    fill=(210, 182, 140, 245), outline=(70, 45, 20, 180), width=1)
d.rounded_rectangle([lp(730), lp(tag_y), lp(920), lp(tag_y + tag_h)], radius=6,
                    fill=(210, 182, 140, 245), outline=(70, 45, 20, 180), width=1)

sf.composite(deco, mode="normal", opacity=1.0)

# ── text layer ─────────────────────────────────────────────
sf.frame(65, 65, 870, 1050)

sf.serial(92, tag_y + 8, SERIAL, family="mono", size=18, fill=INK, anchor="lt",
          role="meta", allow_overlap=False)
sf.datestamp(908, tag_y + 8, DATE, family="mono", size=18, fill=INK, anchor="rt",
             role="meta", allow_overlap=False)

q_y = q_start
for line in q_lines:
    lw, _ = sf.measure(line, "serif-cjk", QS, bold=False)
    x = 500 - lw / 2
    sf.text(x, q_y, line, family="serif-cjk", size=QS, fill=INK,
            anchor="lt", role="quote", bold=False, line_gap=QLG,
            allow_overlap=False)
    q_y += Q_LH

f_y = f_start
for line in f_lines:
    lw, _ = sf.measure(line, "cjk-tc", FS, bold=False)
    x = 500 - lw / 2
    sf.text(x, f_y, line, family="cjk-tc", size=FS, fill=INK,
            anchor="lt", role="body", bold=False, line_gap=FLG,
            allow_overlap=False)
    f_y += f_lh

sf.save(OUT_PATH)
