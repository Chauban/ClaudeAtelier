from atelier_canvas import Surface
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1700
S = 2
sf = Surface(W, H, scale=2, bg=(8, 15, 35))
AW, AH = W * S, H * S

yy = np.linspace(0, 1, AH, dtype=np.float32)[:, None]
xx = np.linspace(0, 1, AW, dtype=np.float32)[None, :]
base_arr = np.zeros((AH, AW, 4), dtype=np.uint8)
base_arr[..., 0] = (8 + 20 * yy + 5 * xx).astype(np.uint8)
base_arr[..., 1] = (15 + 24 * yy + 5 * xx).astype(np.uint8)
base_arr[..., 2] = (38 + 26 * yy + 8 * xx).astype(np.uint8)
base_arr[..., 3] = 255
base_img = Image.fromarray(base_arr, 'RGBA')


def contour_points(base_y, amp, phase, freq, n=640):
    xs = np.linspace(0, W, n)
    ys = (base_y
          + amp * np.sin(2 * math.pi * freq * xs / W + phase)
          + 0.45 * amp * np.sin(2 * math.pi * (freq * 2.17) * xs / W + phase * 1.35 + 0.7))
    pts = [(float(x), float(y)) for x, y in zip(xs, ys)]
    pts.append((float(W), float(H)))
    pts.append((0.0, float(H)))
    return pts


def add_paper_layer(pts, fill_rgb, shadow=True, blur=16, offset=14, alpha=110):
    global base_img
    if shadow:
        sh = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        sp = [(x * S, (y + offset) * S) for x, y in pts]
        d.polygon(sp, fill=(0, 0, 0, alpha))
        sh = sh.filter(ImageFilter.GaussianBlur(blur * S))
        base_img = Image.alpha_composite(base_img, sh)
    im = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p2 = [(x * S, y * S) for x, y in pts]
    d.polygon(p2, fill=fill_rgb + (255,))
    base_img = Image.alpha_composite(base_img, im)


layers = [
    (235, 18, 0.2, 1.0, (164, 195, 222), True, 12, 10, 90),
    (330, 18, 0.9, 1.2, (136, 170, 208), True, 14, 12, 100),
    (425, 20, 1.6, 1.5, (104, 142, 184), True, 16, 14, 110),
    (530, 20, 2.3, 1.8, (76, 116, 160), True, 18, 16, 115),
    (640, 22, 3.0, 2.1, (54, 90, 134), True, 20, 18, 120),
    (760, 24, 3.7, 2.4, (38, 66, 104), True, 22, 20, 125),
    (900, 25, 4.4, 2.8, (26, 46, 78), True, 24, 22, 130),
    (1035, 26, 5.1, 3.2, (11, 22, 46), True, 26, 24, 130),
]

for ly in layers[:4]:
    pts = contour_points(ly[0], ly[1], ly[2], ly[3])
    add_paper_layer(pts, ly[4], shadow=ly[5], blur=ly[6], offset=ly[7], alpha=ly[8])

fish_pts = [
    (180, 620), (250, 575), (350, 555), (500, 548), (640, 560),
    (820, 470), (820, 470), (860, 515), (820, 570), (750, 650),
    (620, 690), (430, 705), (260, 695), (190, 670), (165, 645)
]

sh = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
d = ImageDraw.Draw(sh)
sp = [(x * S, (y + 16) * S) for x, y in fish_pts]
d.polygon(sp, fill=(0, 0, 0, 110))
sh = sh.filter(ImageFilter.GaussianBlur(20 * S))
base_img = Image.alpha_composite(base_img, sh)

body = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
d = ImageDraw.Draw(body)
fp2 = [(x * S, y * S) for x, y in fish_pts]
d.polygon(fp2, fill=(195, 226, 248, 210))
base_img = Image.alpha_composite(base_img, body)

det = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
d = ImageDraw.Draw(det)
d.line(fp2 + [fp2[0]], fill=(225, 242, 255, 255), width=3 * S)
d.ellipse([210 * S, 600 * S, 270 * S, 660 * S],
          fill=(18, 38, 68, 255), outline=(225, 240, 255, 255), width=3 * S)
d.ellipse([285 * S, 605 * S, 380 * S, 660 * S], fill=(28, 55, 95, 210))
d.ellipse([300 * S, 618 * S, 355 * S, 645 * S], fill=(45, 80, 125, 230))
d.line([(340 * S, 630 * S), (760 * S, 600 * S)], fill=(28, 55, 95, 230), width=4 * S)
for rx in range(400, 730, 55):
    d.line([(rx * S, 625 * S), ((rx - 10) * S, 675 * S)],
           fill=(45, 80, 125, 180), width=3 * S)
d.arc([235 * S, 600 * S, 310 * S, 680 * S],
      start=180, end=270, fill=(28, 55, 95, 220), width=3 * S)
base_img = Image.alpha_composite(base_img, det)

for ly in layers[4:]:
    pts = contour_points(ly[0], ly[1], ly[2], ly[3])
    add_paper_layer(pts, ly[4], shadow=ly[5], blur=ly[6], offset=ly[7], alpha=ly[8])

rng = np.random.default_rng(42)
part = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
d = ImageDraw.Draw(part)
for _ in range(70):
    px = rng.uniform(30, 970)
    py = rng.uniform(120, 900)
    pr = rng.uniform(1.5, 4.5)
    pa = int(rng.uniform(28, 105))
    d.ellipse([px * S - pr * S, py * S - pr * S, px * S + pr * S, py * S + pr * S],
              fill=(205, 230, 250, pa))
base_img = Image.alpha_composite(base_img, part)

arr = np.array(base_img).astype(np.int16)
noise = rng.integers(-5, 6, (AH, AW, 1), dtype=np.int16)
arr[..., :3] = np.clip(arr[..., :3] + noise, 0, 255)
base_img = Image.fromarray(arr.astype(np.uint8), 'RGBA')

sf.composite(base_img, mode='normal', opacity=1.0)

sf.frame(90, 80, 820, 1530)

quote_x = 120
quote_width = 760

quote_y = 420
quote_box = sf.text(
    quote_x, quote_y, QUOTE,
    family='cjk-hk', size=36, fill=(248, 251, 255),
    anchor='lt', role='quote', bold=True,
    max_w=quote_width, line_gap=0.42
)

fact_y = quote_box.bottom + 48
fact_box = sf.text(
    quote_x, fact_y, FACT,
    family='cjk-hk', size=28, fill=(226, 233, 244),
    anchor='lt', role='body',
    max_w=quote_width, line_gap=0.48
)

sf.serial(quote_x, 110, SERIAL,
          family='cjk-hk', size=18, fill=(190, 205, 230),
          anchor='lt', role='meta')

sf.datestamp(880, 1490, DATE,
             family='cjk-hk', size=18, fill=(190, 205, 230),
             anchor='rt', role='meta')

sf.save(OUT_PATH)
