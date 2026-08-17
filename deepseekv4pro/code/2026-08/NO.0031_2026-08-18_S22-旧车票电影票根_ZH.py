from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math

W, H = 1000, 1840
sf = Surface(W, H, scale=2, bg=(32, 21, 15))
sf.frame(150, 110, 700, 1600)

S = 2
paper_x0, paper_y0 = 80, 70
paper_x1, paper_y1 = 920, 1770
paper_r = 22

dark_ink = (55, 38, 25)
paper_fill = (232, 216, 179, 255)
paper_outline = (74, 52, 35, 255)
inner_outline = (105, 78, 52, 255)

# background: dark wood-grain desk
bg = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
rr = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2)
bright = 52 - 26 * rr + 5 * np.sin(yy * 30 + xx * 8) + 3 * np.sin(xx * 70) + 2 * np.sin(yy * 80)
bright = np.clip(bright, 12, 75)
bg[..., 0] = (bright * 1.25).astype(np.uint8)
bg[..., 1] = (bright * 0.90).astype(np.uint8)
bg[..., 2] = (bright * 0.60).astype(np.uint8)
bg[..., 3] = 255
sf.composite(bg)

# shadow under ticket
shadow = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle(
    [(paper_x0 + 12) * S, (paper_y0 + 24) * S, (paper_x1 + 12) * S, (paper_y1 + 24) * S],
    radius=paper_r * S,
    fill=(0, 0, 0, 190),
)
shadow = shadow.filter(ImageFilter.GaussianBlur(28))
sf.composite(shadow, mode="multiply", opacity=0.65)

# ticket paper
paper = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
pd = ImageDraw.Draw(paper)
pd.rounded_rectangle(
    [paper_x0 * S, paper_y0 * S, paper_x1 * S, paper_y1 * S],
    radius=paper_r * S,
    fill=paper_fill,
    outline=paper_outline,
    width=6 * S,
)
pd.rounded_rectangle(
    [(paper_x0 + 28) * S, (paper_y0 + 28) * S, (paper_x1 - 28) * S, (paper_y1 - 28) * S],
    radius=16 * S,
    outline=inner_outline,
    width=3 * S,
)

# ticket tear-off line
ticket_y = 840
for x in range(140, 880, 16):
    pd.line([x * S, ticket_y * S, (x + 8) * S, ticket_y * S], fill=inner_outline, width=3 * S)
ticket_y2 = 860
for x in range(140, 880, 16):
    pd.line([x * S, ticket_y2 * S, (x + 8) * S, ticket_y2 * S], fill=inner_outline, width=2 * S)

# aged spots on paper
rng = np.random.default_rng(7)
for _ in range(60):
    cx = int(rng.integers(paper_x0 + 40, paper_x1 - 40))
    cy = int(rng.integers(paper_y0 + 40, paper_y1 - 40))
    rad = int(rng.integers(2, 7))
    alpha = int(rng.integers(10, 35))
    pd.ellipse(
        [(cx - rad) * S, (cy - rad) * S, (cx + rad) * S, (cy + rad) * S],
        fill=(105, 78, 52, alpha),
    )

# barcode at bottom left
barcode_y0, barcode_y1 = 1640, 1720
bx = 190
while bx < 610:
    bw = int(rng.integers(3, 9))
    if bx + bw > 610:
        bw = 610 - bx
    if rng.random() > 0.25:
        pd.rectangle([bx * S, barcode_y0 * S, (bx + bw) * S, barcode_y1 * S], fill=(40, 28, 19, 255))
    bx += bw + int(rng.integers(3, 9))

# empty round rubber stamp at right, lower than fact text
stamp_cx, stamp_cy, stamp_r = 760, 1665, 56
pd.ellipse(
    [(stamp_cx - stamp_r) * S, (stamp_cy - stamp_r) * S, (stamp_cx + stamp_r) * S, (stamp_cy + stamp_r) * S],
    outline=(178, 55, 42, 255),
    width=6 * S,
    fill=(178, 55, 42, 12),
)
pd.ellipse(
    [(stamp_cx - (stamp_r - 10)) * S, (stamp_cy - (stamp_r - 10)) * S,
     (stamp_cx + (stamp_r - 10)) * S, (stamp_cy + (stamp_r - 10)) * S],
    outline=(178, 55, 42, 255),
    width=2 * S,
)
for ang in range(0, 360, 15):
    x1 = stamp_cx + int(math.cos(math.radians(ang)) * (stamp_r + 5))
    y1 = stamp_cy + int(math.sin(math.radians(ang)) * (stamp_r + 5))
    x2 = stamp_cx + int(math.cos(math.radians(ang)) * (stamp_r + 12))
    y2 = stamp_cy + int(math.sin(math.radians(ang)) * (stamp_r + 12))
    pd.line([x1 * S, y1 * S, x2 * S, y2 * S], fill=(178, 55, 42, 255), width=2 * S)

sf.composite(paper, mode="normal", opacity=1.0)

# --- text layout ---

quote_box = sf.text(
    170, 250,
    QUOTE,
    family="cjk-sc",
    size=44,
    fill=dark_ink,
    anchor="lt",
    role="quote",
    bold=False,
    max_w=660,
    line_gap=0.42,
)

fact_box = sf.text(
    170, 920,
    FACT,
    family="cjk-sc",
    size=33,
    fill=(48, 34, 23),
    anchor="lt",
    role="body",
    bold=False,
    max_w=660,
    line_gap=0.40,
)

# ticket-style bottom markings: serial left, date right
sf.serial(170, 1565, SERIAL, family="mono", size=20, fill=dark_ink, anchor="lt", role="meta", bold=False)
sf.datestamp(830, 1565, DATE, family="mono", size=20, fill=dark_ink, anchor="rt", role="meta", bold=False)

sf.save(OUT_PATH)
