from atelier_canvas import Surface
from PIL import Image, ImageDraw

sf = Surface(1000, 1600, scale=2, bg=(235, 235, 235))
sf.frame(60, 60, 880, 1480)

SCALE = 2

lay = sf.layer()
img = Image.fromarray(lay, 'RGBA')
d = ImageDraw.Draw(img)

def R(x, y, w, h, fill=None, outline=None, width=1):
    d.rectangle([x * SCALE, y * SCALE, (x + w) * SCALE, (y + h) * SCALE],
                fill=fill, outline=outline, width=int(width * SCALE))

def L(x1, y1, x2, y2, fill, width=1):
    d.line([x1 * SCALE, y1 * SCALE, x2 * SCALE, y2 * SCALE],
           fill=fill, width=int(width * SCALE))

# Background grid
for v in range(0, 1001, 100):
    L(v, 0, v, 1600, (0, 0, 0, 18), 1)
for h in range(0, 1601, 100):
    L(0, h, 1000, h, (0, 0, 0, 18), 1)

# Outer brutalist border
R(30, 30, 940, 1540, outline=(0, 0, 0, 255), width=8)

# Top navigation bar
R(60, 60, 880, 110, fill=(0, 0, 0, 255))
R(80, 80, 40, 40, fill=(255, 0, 0, 255))
R(140, 80, 40, 40, fill=(0, 0, 255, 255))
R(200, 80, 40, 40, fill=(255, 255, 0, 255))

# Color strips
R(60, 170, 220, 20, fill=(255, 0, 0, 255))
R(280, 170, 220, 20, fill=(0, 0, 255, 255))
R(500, 170, 220, 20, fill=(255, 255, 0, 255))
R(720, 170, 220, 20, fill=(0, 0, 0, 255))

# QUOTE white block
R(80, 220, 840, 260, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=8)
R(84, 224, 26, 252, fill=(50, 255, 50, 255))
R(700, 420, 160, 40, fill=(0, 0, 255, 255))

# FACT white block
R(80, 520, 840, 600, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=8)
R(84, 538, 24, 582, fill=(0, 0, 255, 255))
R(80, 520, 840, 18, fill=(0, 0, 0, 255))

# Brutalist UI elements inside FACT block
R(140, 1080, 28, 28, outline=(0, 0, 0, 255), width=3)
R(200, 1080, 28, 28, fill=(0, 0, 0, 255))
R(260, 1070, 400, 50, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=4)
R(680, 1070, 160, 50, fill=(0, 0, 0, 255))

# Mid color bars
R(60, 1160, 220, 24, fill=(255, 0, 0, 255))
R(280, 1160, 220, 24, fill=(0, 0, 255, 255))
R(500, 1160, 220, 24, fill=(255, 255, 0, 255))
R(720, 1160, 220, 24, fill=(0, 0, 0, 255))
L(60, 1180, 940, 1180, (0, 0, 0, 255), 4)

# Barcode block
bx = 60
bi = 0
while bx < 940:
    bw = 5 + (bi % 4) * 4
    bh = 90 + (bi % 3) * 45
    R(bx, 1230, bw, bh, fill=(0, 0, 0, 255))
    bx += bw + 8
    bi += 1

# Footer black bar
R(60, 1400, 880, 130, fill=(0, 0, 0, 255))

# Composite decoration before text
sf.composite(img, mode="normal", opacity=1.0)

# Text layer
sf.serial(80, 1420, SERIAL, family="mono", size=26, fill=(255, 255, 255),
          anchor="lt", role="meta", bold=True, allow_overlap=False)
sf.datestamp(920, 1420, DATE, family="mono", size=22, fill=(255, 255, 255),
             anchor="rt", role="meta", bold=True, allow_overlap=False)

sf.text(130, 250, QUOTE, family="cjk-tc", size=58, fill=(0, 0, 0),
        anchor="lt", role="quote", bold=True, max_w=750, line_gap=0.35, allow_overlap=False)

sf.text(120, 590, FACT, family="cjk-tc", size=34, fill=(0, 0, 0),
        anchor="lt", role="body", bold=False, max_w=740, line_gap=0.35, allow_overlap=False)

sf.save(OUT_PATH)
