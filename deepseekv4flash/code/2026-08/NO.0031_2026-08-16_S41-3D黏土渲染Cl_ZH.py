from atelier_canvas import Surface
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 2
sf = Surface(1000, 1900, scale=S, bg=(255, 235, 230))
sf.frame(60, 60, 880, 1780)

def sc(v):
    return int(round(v * S))

def rrect(draw, xy, radius, fill):
    draw.rounded_rectangle([sc(xy[0]), sc(xy[1]), sc(xy[2]), sc(xy[3])],
                           radius=sc(radius), fill=fill)

def ellipse(draw, cx, cy, rx, ry, fill=None, outline=None, width=None):
    cx, cy, rx, ry = sc(cx), sc(cy), sc(rx), sc(ry)
    if fill is not None:
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)
    if outline is not None:
        if width is None:
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=outline)
        else:
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=outline,
                         width=sc(width))

def ring(draw, cx, cy, r, w, fill):
    ellipse(draw, cx, cy, r, r, outline=fill, width=w)

def blob_shadow(draw, cx, cy, rx, ry, alpha=110):
    ellipse(draw, cx, cy + 14, rx, ry, fill=(60, 40, 60, alpha))

def blob_body(draw, cx, cy, rx, ry, fill):
    ellipse(draw, cx, cy, rx, ry, fill=fill)

def blob_highlight(draw, cx, cy, rx, ry):
    ellipse(draw, cx, cy - int(ry * 0.35), int(rx * 0.45), int(ry * 0.3),
            fill=(255, 255, 255, 90))

def board_shadow(draw, x0, y0, x1, y1, r, alpha=120):
    rrect(draw, (x0, y0 + 16, x1, y1 + 16), r, (60, 40, 60, alpha))

def board_body(draw, x0, y0, x1, y1, r, fill):
    rrect(draw, (x0, y0, x1, y1), r, fill)

def board_highlight(draw, x0, y0, x1, y1, r):
    h = y1 - y0
    rrect(draw, (x0, y0, x1, y0 + int(h * 0.4)), r, (255, 255, 255, 55))

# ---------- background gradient ----------
grad = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
top = np.array([255, 214, 230])
bottom = np.array([255, 243, 224])
for c in range(3):
    grad[..., c] = (top[c] * (1 - yy) + bottom[c] * yy).astype(np.uint8)
grad[..., 3] = 255
sf.composite(grad)

# ---------- decoration layers ----------
shadow_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
body_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
hl_img = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
ds = ImageDraw.Draw(shadow_img)
db = ImageDraw.Draw(body_img)
dh = ImageDraw.Draw(hl_img)

# ---- top badges ----
for bx0, bx1 in ((70, 280), (720, 930)):
    board_shadow(ds, bx0, 70, bx1, 150, 42, 110)
    board_body(db, bx0, 70, bx1, 150, 42, (250, 230, 180) if bx0 < 400 else (220, 190, 230))
    board_highlight(dh, bx0, 70, bx1, 150, 42)

# ---- clay board for FACT ----
board_y0 = 1360
board_shadow(ds, 60, board_y0, 940, 1840, 64, 130)
board_body(db, 60, board_y0, 940, 1840, 64, (184, 220, 235))
board_highlight(dh, 60, board_y0, 940, 1840, 64)

# ---- sound wave rings ----
ring_cx, ring_cy = 500, 1040
ring_colors = [(246, 200, 214), (220, 190, 230), (198, 226, 210)]
for i, r in enumerate((150, 215, 280)):
    ring(ds, ring_cx, ring_cy + 14, r, 26, (60, 40, 60, 110))
    ring(db, ring_cx, ring_cy, r, 26, ring_colors[i])
    ellipse(dh, ring_cx, ring_cy - r + 14, r, 16, fill=(255, 255, 255, 70))

# ---- clay balls ----
blob_shadow(ds, 85, 370, 70, 70)
blob_body(db, 85, 370, 70, 70, (220, 190, 230))
blob_highlight(dh, 85, 370, 70, 70)

blob_shadow(ds, 905, 300, 42, 42)
blob_body(db, 905, 300, 42, 42, (250, 230, 180))
blob_highlight(dh, 905, 300, 42, 42)

blob_shadow(ds, 200, 690, 30, 30)
blob_body(db, 200, 690, 30, 30, (246, 200, 214))
blob_highlight(dh, 200, 690, 30, 30)

blob_shadow(ds, 810, 880, 46, 46)
blob_body(db, 810, 880, 46, 46, (198, 226, 210))
blob_highlight(dh, 810, 880, 46, 46)

blob_shadow(ds, 140, 1650, 62, 62)
blob_body(db, 140, 1650, 62, 62, (246, 200, 214))
blob_highlight(dh, 140, 1650, 62, 62)

blob_shadow(ds, 878, 1720, 50, 50)
blob_body(db, 878, 1720, 50, 50, (198, 226, 210))
blob_highlight(dh, 878, 1720, 50, 50)

blob_shadow(ds, 180, 1240, 26, 26)
blob_body(db, 180, 1240, 26, 26, (250, 230, 180))
blob_highlight(dh, 180, 1240, 26, 26)

blob_shadow(ds, 840, 1230, 34, 34)
blob_body(db, 840, 1230, 34, 34, (220, 190, 230))
blob_highlight(dh, 840, 1230, 34, 34)

# ---- composite decoration ----
sf.composite(shadow_img.filter(ImageFilter.GaussianBlur(sc(14))))
sf.composite(body_img)
sf.composite(hl_img, opacity=0.7)

# ---------- text tier ----------
sf.serial(175, 110, SERIAL, family="cjk-sc", size=32, fill=(80, 50, 70),
          anchor="mm", role="meta")
sf.datestamp(825, 110, DATE, family="cjk-sc", size=32, fill=(80, 50, 70),
             anchor="mm", role="meta")

sf.text(500, 240, QUOTE, family="cjk-sc", size=44, fill=(90, 60, 75),
        anchor="mt", max_w=820, role="quote", line_gap=0.35)

sf.text(100, 1800, FACT, family="cjk-sc", size=30, fill=(50, 60, 80),
        anchor="lb", max_w=760, role="body", line_gap=0.4)

sf.save(OUT_PATH)
