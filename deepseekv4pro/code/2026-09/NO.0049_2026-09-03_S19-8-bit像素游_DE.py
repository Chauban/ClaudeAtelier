import numpy as np
import random
from PIL import Image, ImageDraw
from atelier_canvas import Surface

W = 1000
H = 1600

sf = Surface(W, H, scale=2, bg=(8, 10, 26))
sf.frame(40, 16, 920, 1560)

LATIN = "sans"
CJK = "cjk-sc"
MONO = "mono"

idx = FACT.find("（")
if idx >= 0:
    fact_de = FACT[:idx]
    fact_zh = FACT[idx:]
else:
    fact_de = FACT
    fact_zh = ""

quote_zh = "战争结束时，起因很少留下——有时只剩下一只从天花板垂下的木桶。"

text_x = 72
max_w_base = W - 2 * text_x

# ---------- choose wrap widths to avoid orphan lines ----------
def choose_quote_width(text, family, size, bold, candidates, min_ratio=0.30, max_lines=6):
    for mw in candidates:
        lines = sf.wrap(text, family, size, mw, bold=bold)
        if len(lines) > max_lines:
            continue
        if len(lines) <= 1:
            return mw, lines
        widths = [sf.measure(l, family, size, bold)[0] for l in lines]
        max_prev = max(widths[:-1])
        if max_prev <= 0:
            return mw, lines
        if widths[-1] / max_prev >= min_ratio:
            return mw, lines
    return candidates[-1], sf.wrap(text, family, size, candidates[-1], bold=bold)

q_candidates = [800, 760, 720, 680, 640, 600, 560]
q_max_w, q_lines = choose_quote_width(QUOTE, LATIN, 36, True, q_candidates)

# split Chinese quote into two roughly equal lines
zc_count = len(quote_zh)
qc_max_w = max(2 * 28, int(28 * ((zc_count + 1) // 2)))
qc_lines = sf.wrap(quote_zh, CJK, 28, qc_max_w, bold=False)

fact_de_max_w = 820
fact_de_lines = sf.wrap(fact_de, LATIN, 30, fact_de_max_w, bold=False)
fact_zh_max_w = 800
fact_zh_lines = sf.wrap(fact_zh, CJK, 28, fact_zh_max_w, bold=False) if fact_zh else []

line_h_q = sf.measure("Ag", LATIN, 36, bold=True)[1] * 1.38
line_h_qc = sf.measure("一", CJK, 28, bold=False)[1] * 1.35
line_h_fg = sf.measure("Ag", LATIN, 30, bold=False)[1] * 1.35
line_h_fc = sf.measure("一", CJK, 28, bold=False)[1] * 1.35

q_y = 440
q_est_h = len(q_lines) * line_h_q
qc_y = q_y + q_est_h + 16
qc_est_h = len(qc_lines) * line_h_qc

div_y = int(qc_y + qc_est_h + 34)
fact_y_est = int(div_y + 42)
fg_est_h = len(fact_de_lines) * line_h_fg
fg_est_bottom = fact_y_est + fg_est_h
fc_y_est = int(fg_est_bottom + 26)
fc_est_h = len(fact_zh_lines) * line_h_fc if fact_zh_lines else 0
fc_est_bottom = fc_y_est + fc_est_h

arrow_y = int(fc_est_bottom + 34)
arrow_y = max(1460, min(arrow_y, 1510))

# ---------- pixel-art background ----------
art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(art)

# HUD bar (top)
hud_y0, hud_y1 = 16, 68
d.rectangle([0, hud_y0, W - 1, hud_y1], fill=(6, 8, 20, 235))
d.rectangle([0, hud_y0, W - 1, hud_y0 + 4], fill=(64, 70, 100, 255))
d.rectangle([0, hud_y1 - 4, W - 1, hud_y1], fill=(64, 70, 100, 255))
d.rectangle([0, hud_y0, 3, hud_y1], fill=(64, 70, 100, 255))
d.rectangle([W - 4, hud_y0, W - 1, hud_y1], fill=(64, 70, 100, 255))
for i in range(6):
    d.rectangle([8 + i * 14, hud_y0 + 6, 12 + i * 14, hud_y0 + 10], fill=(126, 132, 170, 255))
for i in range(6):
    d.rectangle([W - 20 - i * 14, hud_y0 + 6, W - 16 - i * 14, hud_y0 + 10], fill=(126, 132, 170, 255))

# sky scene
scene_top = 84
scene_bottom = 384
rows = (scene_bottom - scene_top) // 8
top_col = (17, 19, 48)
bot_col = (40, 34, 70)
for i in range(rows):
    t = i / (rows - 1)
    col = tuple(int(top_col[j] + (bot_col[j] - top_col[j]) * t) for j in range(3)) + (255,)
    y = scene_top + i * 8
    d.rectangle([0, y, W - 1, y + 7], fill=col)

rng = random.Random(49)
for _ in range(85):
    sx = rng.randrange(0, W // 8)
    sy = rng.randrange(0, 12)
    x = sx * 8
    y = scene_top + sy * 8
    d.rectangle([x, y, x + 7, y + 7], fill=(255, 240, 180, 255))

# moon
moon_x = W - 132
d.rectangle([moon_x, scene_top + 16, moon_x + 40, scene_top + 56], fill=(240, 236, 210, 255))
d.rectangle([moon_x + 10, scene_top + 28, moon_x + 24, scene_top + 42], fill=(212, 202, 174, 255))
d.rectangle([moon_x - 8, scene_top + 24, moon_x + 2, scene_top + 34], fill=(212, 202, 174, 255))

# ceiling beam and hook
d.rectangle([0, scene_top, W - 1, scene_top + 13], fill=(56, 30, 42, 255))
d.rectangle([0, scene_top + 13, W - 1, scene_top + 17], fill=(96, 58, 62, 255))
CX = 500
d.rectangle([CX - 6, scene_top + 14, CX + 6, scene_top + 28], fill=(110, 114, 136, 255))

# rope
ROPE = (208, 172, 122, 255)
rope_top = scene_top + 26
rope_end = rope_top + 88
d.rectangle([CX - 2, rope_top, CX + 2, rope_end], fill=ROPE)

# bucket
RIM_Y0 = rope_end + 10
RIM_H = 12
BODY_Y0 = RIM_Y0 + RIM_H
BODY_Y1 = BODY_Y0 + 104
RIM_L = CX - 48
RIM_R = CX + 48
BODY_L = CX - 36
BODY_R = CX + 36

d.line([(CX, rope_end), (RIM_L + 18, RIM_Y0 - 2)], fill=ROPE, width=4)
d.line([(CX, rope_end), (RIM_R - 18, RIM_Y0 - 2)], fill=ROPE, width=4)
RIM_COL = (150, 92, 48, 255)
RIM_HI = (186, 122, 60, 255)
d.rectangle([RIM_L, RIM_Y0, RIM_R, RIM_Y0 + RIM_H], fill=RIM_COL)
d.rectangle([RIM_L, RIM_Y0, RIM_L + 10, RIM_Y0 + RIM_H], fill=RIM_HI)
BODY_COL = (122, 72, 38, 255)
BODY_HI = (158, 100, 50, 255)
d.rectangle([BODY_L, BODY_Y0, BODY_R, BODY_Y1], fill=BODY_COL)
d.rectangle([BODY_L, BODY_Y0, BODY_L + 12, BODY_Y1], fill=BODY_HI)
BAND = (68, 72, 90, 255)
d.rectangle([BODY_L - 4, BODY_Y0 + 14, BODY_R + 4, BODY_Y0 + 22], fill=BAND)
d.rectangle([BODY_L - 4, BODY_Y1 - 28, BODY_R + 4, BODY_Y1 - 20], fill=BAND)
for i in range(4):
    x = BODY_L + 16 + i * 14
    d.rectangle([x, BODY_Y0 + 2, x + 3, BODY_Y1 - 2], fill=(100, 58, 34, 255))
d.rectangle([BODY_L - 2, BODY_Y1 + 1, BODY_R + 2, BODY_Y1 + 7], fill=(88, 52, 30, 255))

# dialogue window
wx0, wy0, wx1, wy1 = 36, 408, 964, 1544
d.rectangle([wx0, wy0, wx1, wy1], fill=(10, 12, 34, 225))
d.rectangle([wx0, wy0, wx1, wy0 + 4], fill=(52, 56, 82, 255))
d.rectangle([wx0, wy1 - 4, wx1, wy1], fill=(52, 56, 82, 255))
d.rectangle([wx0, wy0, wx0 + 4, wy1], fill=(52, 56, 82, 255))
d.rectangle([wx1 - 4, wy0, wx1, wy1], fill=(52, 56, 82, 255))
d.rectangle([wx0 + 8, wy0 + 8, wx1 - 8, wy0 + 11], fill=(112, 118, 152, 255))
d.rectangle([wx0 + 8, wy1 - 11, wx1 - 8, wy1 - 8], fill=(112, 118, 152, 255))
d.rectangle([wx0 + 8, wy0 + 8, wx0 + 11, wy1 - 8], fill=(112, 118, 152, 255))
d.rectangle([wx1 - 11, wy0 + 8, wx1 - 8, wy1 - 8], fill=(112, 118, 152, 255))
d.rectangle([wx0 + 16, wy0 + 16, wx0 + 24, wy0 + 24], fill=(142, 130, 80, 255))
d.rectangle([wx1 - 24, wy0 + 16, wx1 - 16, wy0 + 24], fill=(142, 130, 80, 255))
d.rectangle([wx0 + 16, wy1 - 24, wx0 + 24, wy1 - 16], fill=(142, 130, 80, 255))
d.rectangle([wx1 - 24, wy1 - 24, wx1 - 16, wy1 - 16], fill=(142, 130, 80, 255))

# divider between quote and fact
d.rectangle([80, div_y, 920, div_y + 2], fill=(112, 118, 152, 255))
d.rectangle([80, div_y - 3, 92, div_y + 5], fill=(142, 130, 80, 255))
d.rectangle([908, div_y - 3, 920, div_y + 5], fill=(142, 130, 80, 255))

# bottom continue arrow
d.polygon([(490, arrow_y), (510, arrow_y), (500, arrow_y + 14)], fill=(142, 130, 80, 255))

# composite background before text
big = art.resize((W * 2, H * 2), Image.NEAREST)
arr = np.array(big, dtype=np.uint8)
sf.composite(arr, mode="normal", opacity=1.0)

# ---------- text ----------
sf.serial(56, 38, SERIAL, family=MONO, size=18, fill=(232, 228, 118), anchor="lt", role="meta")
dw, _ = sf.measure(DATE, MONO, 18, bold=False)
sf.datestamp(W - 56 - dw, 38, DATE, family=MONO, size=18, fill=(232, 228, 118), anchor="lt", role="meta")

q = sf.text(text_x, q_y, QUOTE, family=LATIN, size=36, fill=(235, 232, 205),
            anchor="lt", role="quote", bold=True, max_w=q_max_w, line_gap=0.38)

qc = sf.text(text_x, q.bottom + 16, quote_zh, family=CJK, size=28, fill=(222, 210, 175),
             anchor="lt", role="body", bold=False, max_w=qc_max_w, line_gap=0.35)

fg = sf.text(text_x, qc.bottom + 46, fact_de, family=LATIN, size=30, fill=(224, 226, 214),
             anchor="lt", role="body", bold=False, max_w=fact_de_max_w, line_gap=0.35)

if fact_zh:
    fc = sf.text(text_x, fg.bottom + 24, fact_zh, family=CJK, size=28, fill=(214, 202, 168),
                 anchor="lt", role="body", bold=False, max_w=fact_zh_max_w, line_gap=0.35)

sf.save(OUT_PATH)
