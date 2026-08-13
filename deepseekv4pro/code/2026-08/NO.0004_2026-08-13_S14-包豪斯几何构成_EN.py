from atelier_canvas import Surface
from PIL import Image, ImageDraw

W, H = 940, 1350
SC = 2
CREAM = (238, 232, 213)
INK = (20, 18, 14)
RED = (211, 47, 47)
YELLOW = (245, 190, 32)
BLUE = (36, 74, 152)
WHITE = (244, 240, 230)

sf = Surface(W, H, scale=SC, bg=CREAM)

# ---------- geometric background ----------
shapes = Image.new('RGBA', (W * SC, H * SC), (0, 0, 0, 0))
d = ImageDraw.Draw(shapes)

# top black bar with red underline
d.rectangle([0, 0, W * SC, 52 * SC], fill=(18, 18, 18, 255))
d.rectangle([0, 52 * SC, W * SC, 60 * SC], fill=(211, 47, 47, 255))

# left black vertical bar
d.rectangle([26 * SC, 80 * SC, 34 * SC, 1100 * SC], fill=(18, 18, 18, 255))

# yellow disc upper right
cx, cy, r = 700, 225, 145
d.ellipse([(cx - r) * SC, (cy - r) * SC, (cx + r) * SC, (cy + r) * SC],
          fill=(245, 190, 32, 255))

# blue vertical rectangle
d.rectangle([770 * SC, 85 * SC, 895 * SC, 670 * SC], fill=(36, 74, 152, 255))

# red square middle right
d.rectangle([675 * SC, 680 * SC, 855 * SC, 860 * SC], fill=(211, 47, 47, 255))

# bottom black bar with yellow line below
d.rectangle([0, 1260 * SC, W * SC, 1320 * SC], fill=(18, 18, 18, 255))
d.rectangle([0, 1320 * SC, W * SC, 1340 * SC], fill=(245, 190, 32, 255))
d.rectangle([0, 1340 * SC, W * SC, 1350 * SC], fill=(18, 18, 18, 255))

# decorative diagonal yellow band from lower left to upper right
d.polygon([(0, 950 * SC), (0, 980 * SC), (940 * SC, 170 * SC), (940 * SC, 140 * SC)],
          fill=(245, 190, 32, 255))

# small white square on yellow band
d.rectangle([190 * SC, 650 * SC, 280 * SC, 740 * SC], fill=(244, 240, 230, 255))

# small black square on red square
d.rectangle([710 * SC, 715 * SC, 820 * SC, 825 * SC], fill=(18, 18, 18, 255))

# blue vertical bar near bottom left
d.rectangle([40 * SC, 980 * SC, 56 * SC, 1160 * SC], fill=(36, 74, 152, 255))

sf.composite(shapes, mode='normal', opacity=1.0)

# ---------- text layer ----------
sf.frame(0, 0, W, H)

# serial + date in top black bar
sf.serial(W - 16, 6, SERIAL,
          family="mono", size=18, fill=WHITE,
          anchor="rt", role="meta", bold=True,
          max_w=220, allow_overlap=False)

sf.datestamp(W - 16, 30, DATE,
             family="mono", size=16, fill=WHITE,
             anchor="rt", role="meta", bold=True,
             max_w=220, allow_overlap=False)

# quote
quote_lines = sf.wrap(QUOTE, "sans", 46, 600, bold=True)
q_y = 130
for line in quote_lines:
    box = sf.text(44, q_y, line,
                  family="sans", size=46, fill=INK,
                  anchor="lt", role="quote", bold=True,
                  max_w=600, line_gap=0.30, allow_overlap=False)
    q_y = box.bottom + 22

# fact (English + Chinese translation, use CJK font)
fact_lines = sf.wrap(FACT, "cjk-sc", 30, 580, bold=False)
fact_y = q_y + 30
for line in fact_lines:
    box = sf.text(44, fact_y, line,
                  family="cjk-sc", size=30, fill=INK,
                  anchor="lt", role="body", bold=False,
                  max_w=580, line_gap=0.36, allow_overlap=False)
    fact_y = box.bottom + 18

sf.save(OUT_PATH)
