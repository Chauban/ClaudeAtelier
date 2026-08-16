from atelier_canvas import Surface
from PIL import Image, ImageDraw

W, H = 1000, 2000
BG = (244, 240, 232)
BLACK = (12, 12, 12)
YELLOW = (255, 213, 0)
RED = (226, 32, 26)
WHITE = (255, 255, 255)

sf = Surface(W, H, scale=2, bg=BG)
sf.frame(30, 30, W - 60, H - 60)


def rect(x, y, w, h, color, opacity=255):
    if w <= 0 or h <= 0:
        return
    lay = sf.layer()
    x0 = max(0, int(x * 2))
    x1 = min(sf.W, int((x + w) * 2))
    y0 = max(0, int(y * 2))
    y1 = min(sf.H, int((y + h) * 2))
    if x1 <= x0 or y1 <= y0:
        return
    lay[y0:y1, x0:x1, 0] = color[0]
    lay[y0:y1, x0:x1, 1] = color[1]
    lay[y0:y1, x0:x1, 2] = color[2]
    lay[y0:y1, x0:x1, 3] = opacity
    sf.composite(lay)


def block(x, y, w, h, fill, border=8, shadow=18):
    rect(x + shadow, y + shadow, w, h, BLACK)
    rect(x - border, y - border, w + border * 2, h + border * 2, BLACK)
    rect(x, y, w, h, fill)


# ===== measure text first (no drawing) =====
q_font, q_size, q_maxw = "cjk-hk", 48, 760
qlines = sf.wrap(QUOTE, q_font, q_size, q_maxw, bold=True)
qm = sf.measure("測", q_font, q_size, bold=True)
q_lh = qm[1] * 1.35
q_text_h = q_lh * (len(qlines) - 1) + qm[1]

q_pad_x, q_pad_top, q_pad_bot = 60, 56, 44
q_cw = q_maxw + q_pad_x * 2
q_ch = int(q_text_h + q_pad_top + q_pad_bot) + 8
q_cx, q_cy = 70, 194
q_tx, q_ty = q_cx + q_pad_x, q_cy + q_pad_top

f_font, f_size, f_maxw = "cjk-hk", 33, 660
flines = sf.wrap(FACT, f_font, f_size, f_maxw, bold=False)
fm = sf.measure("測", f_font, f_size, bold=False)
f_lh = fm[1] * 1.35
f_text_h = f_lh * (len(flines) - 1) + fm[1]

f_pad_x, f_pad_top, f_pad_bot = 54, 84, 52
f_cw = f_maxw + f_pad_x * 2
f_ch = int(f_text_h + f_pad_top + f_pad_bot)
f_cx, f_cy = 170, q_cy + q_ch + 120
f_tx, f_ty = f_cx + f_pad_x, f_cy + f_pad_top

# ===== tier 2: backgrounds & decorations =====
# top bar
rect(0, 0, W, 100, BLACK)
rect(0, 100, W, 8, YELLOW)
rect(W - 90, 12, 76, 76, YELLOW)
rect(W - 78, 24, 28, 28, RED)
rect(236, 30, 6, 40, YELLOW)

# quote card
block(q_cx, q_cy, q_cw, q_ch, YELLOW, border=8, shadow=18)
rect(q_cx, q_cy, 16, q_ch, BLACK)
rect(q_cx + q_cw - 60, q_cy + 18, 28, 28, RED)

# transition blocks in the gap between cards
gap_mid = q_cy + q_ch + 60
rect(80, gap_mid, 36, 36, RED)
rect(128, gap_mid + 12, 24, 24, YELLOW)

# fact card
block(f_cx, f_cy, f_cw, f_ch, WHITE, border=6, shadow=16)
rect(f_cx, f_cy + 16, 26, f_ch - 32, RED)
rect(f_cx + 20, f_cy + 20, 44, 44, RED)
rect(f_cx + 32, f_cy + 32, 20, 20, BLACK)

# decorative band below the fact card
deco_y = f_cy + f_ch + 70
rect(70, deco_y, 860, 12, BLACK)

nx, ny = 110, deco_y + 100
rect(nx, ny, 220, 220, BLACK)
rect(nx + 14, ny + 14, 192, 192, YELLOW)
rect(nx + 30, ny + 30, 84, 84, RED)
rect(nx + 76, ny + 76, 120, 120, BLACK)
rect(nx + 90, ny + 90, 42, 42, WHITE)

px, py, pw, ph = 700, deco_y + 80, 230, 290
rect(px, py, pw, ph, BLACK)
rect(px + 10, py + 10, pw - 20, ph - 20, WHITE)
rect(px + 10, py + 10, pw - 20, 48, YELLOW)
rect(px + 10, py + ph - 58, pw - 20, 48, RED)
rect(px + 36, py + 88, 150, 9, BLACK)
rect(px + 36, py + 114, 108, 9, BLACK)
rect(px + 36, py + 140, 130, 9, YELLOW)
rect(px + 36, py + 166, 84, 9, BLACK)
rect(px + 36, py + 200, 66, 9, BLACK)

tcx, tcy, tr = 490, deco_y + 240, 95
timg = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
td = ImageDraw.Draw(timg)
td.ellipse([(tcx - tr) * 2, (tcy - tr) * 2, (tcx + tr) * 2, (tcy + tr) * 2], fill=RED + (255,))
td.ellipse([(tcx - (tr * 2 // 3)) * 2, (tcy - (tr * 2 // 3)) * 2, (tcx + (tr * 2 // 3)) * 2, (tcy + (tr * 2 // 3)) * 2], fill=YELLOW + (255,))
td.ellipse([(tcx - tr // 3) * 2, (tcy - tr // 3) * 2, (tcx + tr // 3) * 2, (tcy + tr // 3) * 2], fill=BLACK + (255,))
sf.composite(timg)

rect(200, deco_y + 390, 600, 26, BLACK)
rect(200, deco_y + 390, 240, 26, YELLOW)
rect(822, deco_y + 392, 22, 22, RED)

rect(200, deco_y + 450, 200, 46, YELLOW)
rect(600, deco_y + 450, 40, 46, BLACK)
rect(640, deco_y + 450, 160, 46, RED)

rect(70, deco_y + 550, 860, 12, BLACK)

# bottom bar
footer_h = 120
rect(0, H - 8 - footer_h, W, 8, YELLOW)
rect(0, H - footer_h, W, footer_h, BLACK)
rect(60, H - footer_h + 36, 48, 48, RED)
rect(716, H - footer_h + 36, 6, 48, YELLOW)

# ===== tier 1: text (drawn once, over clean solid cards) =====
sf.text(q_tx, q_ty, QUOTE,
        family=q_font, size=q_size, fill=BLACK,
        anchor="lt", role="quote", bold=True,
        max_w=q_maxw, line_gap=0.35)

sf.text(f_tx, f_ty, FACT,
        family=f_font, size=f_size, fill=BLACK,
        anchor="lt", role="body", bold=False,
        max_w=f_maxw, line_gap=0.35)

sf.serial(64, 50, SERIAL,
          family="mono", size=32, fill=WHITE, anchor="lm", role="meta", bold=True)

sf.datestamp(W - 64, H - footer_h // 2, DATE,
             family="mono", size=32, fill=WHITE, anchor="rm", role="meta", bold=True)

sf.save(OUT_PATH)
