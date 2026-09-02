import math
import numpy as np
from PIL import Image, ImageDraw
from atelier_canvas import Surface

# ---------------------------------------------------------------- canvas
W, H = 1080, 3200
sf = Surface(W, H, scale=2, bg=(5, 6, 14))
sf.frame(80, 80, 920, 3040)

QUOTE_SIZE = 32
FACT_SIZE = 28
QR_CNT_FAM = "cjk-kr"

fig_wrap = sf.wrap(QUOTE, "cjk-kr", QUOTE_SIZE, 760)
fact_wrap = sf.wrap(FACT, "cjk-kr", FACT_SIZE, 780)

# ---------------------------------------------------------------- background
PW, PH = sf.W, sf.H
PC = 16
GR = (PH + PC - 1) // PC
GC = (PW + PC - 1) // PC

water_top = []
for cc in range(GC):
    water_top.append(54 + int(5.0 * math.sin(cc / 8.0)) + (cc // 34))

grid = np.zeros((GR, GC, 3), dtype=np.uint8)

for rr in range(GR):
    for cc in range(GC):
        if rr < 58:
            band = rr // 5
            sky = [
                (4, 5, 12), (5, 6, 15), (6, 7, 18), (8, 9, 22),
                (10, 11, 26), (12, 13, 30), (15, 15, 34), (18, 17, 38),
                (20, 18, 41), (24, 21, 45), (28, 25, 51), (34, 30, 59)
            ][min(band, 11)]
            col = sky
        elif rr < 92:
            col = (44, 38, 72)
        elif rr < 136:
            col = (24, 23, 48)
        elif rr < 190:
            col = (14, 16, 34)
        else:
            col = (20, 18, 38)
            if rr % 8 == 0 and cc % 3 == 0:
                col = (28, 24, 48)
            if (cc * 11 + rr * 7) % 47 == 0:
                col = (54, 48, 76)

        # sharpest chunky moon
        if 18 <= rr <= 27 and 82 <= cc <= 90:
            col = (242, 220, 162)
            if (rr == 21 and cc == 85) or (rr == 22 and cc == 87) or (rr == 24 and cc == 84):
                col = (181, 146, 100)

        # sparse stars
        if rr < 92 and ((rr * 37 + cc * 53) % 97 == 0):
            col = (254, 245, 205) if rr % 3 == 0 else (126, 148, 196)

        # brown porter flood
        wt = water_top[cc]
        if wt <= rr <= 126:
            rel = rr - wt
            if rel < 2:
                col = (235, 216, 168)
            elif rel < 5:
                col = (214, 160, 82)
            elif rel < 22:
                col = (168, 102, 42)
            elif rel < 45:
                col = (120, 66, 28)
            else:
                col = (84, 47, 22)
            if rr == wt and (cc * 5 + rr * 3) % 7 < 2:
                col = (250, 238, 198)

        # St Giles house silhouettes above the wave
        left_h = 21 <= cc <= 31 and 38 <= rr <= 53
        right_h = 96 <= cc <= 105 and 39 <= rr <= 53
        if not (wt <= rr <= 126) and (left_h or right_h):
            if left_h:
                if rr < 42:
                    col = (174, 66, 42)
                    if rr == 38 and cc in (22, 25, 28):
                        col = (98, 48, 42)
                else:
                    col = (68, 49, 50)
                    if 43 <= rr <= 49 and cc % 3 == 0 and cc < 30:
                        col = (242, 194, 86)
            else:
                if rr < 43:
                    col = (158, 72, 46)
                else:
                    col = (72, 52, 54)
                    if rr in (44, 45, 46, 47) and cc in (98, 101, 104):
                        col = (243, 205, 94)

        # far blocks on the horizon
        if rr == 36 and 5 <= cc <= 14:
            col = (23, 24, 50)
        if rr == 37 and (5 <= cc <= 14 or 108 <= cc <= 118):
            col = (28, 28, 58)

        grid[rr, cc] = col

# chunky up-scale: 16 physical px per cell
big = np.repeat(np.repeat(grid, PC, axis=0), PC, axis=1)
big = big[:PH, :PW]

lay = sf.layer()
lay[..., :3] = big
lay[..., 3] = 255

img = Image.fromarray(lay)
draw = ImageDraw.Draw(img)

# ---------------------------------------------------------------- helpers
def rectlog(x, y, w, h, color):
    draw.rectangle(
        [int(x * 2), int(y * 2), int((x + w) * 2) - 1, int((y + h) * 2) - 1],
        fill=color
    )


def borderlog(x, y, w, h, color, width_log=3):
    wpx = max(2, int(width_log * 2))
    draw.rectangle(
        [int(x * 2), int(y * 2), int((x + w) * 2) - 1, int((y + h) * 2) - 1],
        outline=color, width=wpx
    )


# ---------------------------------------------------------------- top HUD
rectlog(90, 82, 900, 62, (9, 11, 26))
borderlog(90, 82, 900, 62, (210, 178, 112), width_log=2)
rectlog(90, 82, 22, 62, (226, 194, 128))
rectlog(968, 82, 22, 62, (226, 194, 128))
rectlog(90, 144, 900, 4, (70, 58, 42))

# ---------------------------------------------------------------- large RPG text screen
panel_x, panel_y = 130, 920
panel_w, panel_h = 820, 2120

# hard offset shadow
rectlog(panel_x + 16, panel_y + 20, panel_w, panel_h, (2, 3, 8))
# outer dark backing
rectlog(panel_x, panel_y, panel_w, panel_h, (16, 20, 46))
# thick rough pixel border
borderlog(panel_x, panel_y, panel_w, panel_h, (236, 198, 136), width_log=4)
# inner dark line
borderlog(panel_x + 16, panel_y + 16, panel_w - 32, panel_h - 32, (78, 56, 36), width_log=1)

# scan-line feel: soft darker horizontal stripes
for sy in range(panel_y + 24, panel_y + panel_h - 24, 24):
    rectlog(panel_x + 24, sy, panel_w - 48, 1, (12, 15, 36))
    rectlog(panel_x + 24, sy + 2, panel_w - 48, 1, (27, 31, 66))

# single pixel-art sparkles at frame corners
for sx_, sy_ in [(panel_x, panel_y), (panel_x + panel_w, panel_y),
                 (panel_x, panel_y + panel_h), (panel_x + panel_w, panel_y + panel_h)]:
    rectlog(sx_, sy_, 12, 12, (252, 224, 150))
    rectlog(sx_ + 4, sy_ + 4, 4, 4, (118, 82, 38))

sf.composite(img, mode="normal", opacity=1.0)

# ---------------------------------------------------------------- TEXT (no manual line-step overlap)
head_x = 150
head_right = 950

# top HUD date/serial
sf.datestamp(120, 101, DATE, family="mono", size=24,
             fill=(242, 218, 140), anchor="lt", role="meta")
sf.serial(960, 101, SERIAL, family="mono", size=24,
          fill=(242, 218, 140), anchor="rt", role="meta")

# QUOTE: centered, rendered strictly bottom-to-bottom with measured boxes
y_cursor = panel_y + 132
quote_cx = 540

for line in fig_wrap:
    lw = sf.measure(line, "cjk-kr", QUOTE_SIZE)[0]
    bx = sf.text(int(quote_cx - lw // 2), y_cursor, line,
                 family="cjk-kr", size=QUOTE_SIZE, fill=(250, 228, 162),
                 anchor="lt", role="quote")
    y_cursor = bx.bottom + 22

# little pixel divider between quote and fact
div_y = int(y_cursor + 26)
rectlog(180, div_y, 720, 4, (104, 76, 42))
rectlog(180, div_y, 20, 4, (242, 194, 100))
rectlog(880, div_y, 20, 4, (242, 194, 100))

# FACT: regular readable dialogue paragraph
fact_y = div_y + 62
for line in fact_wrap:
    bx = sf.text(head_x, fact_y, line,
                 family="cjk-kr", size=FACT_SIZE, fill=(226, 237, 228),
                 anchor="lt", role="body")
    fact_y = bx.bottom + 15

sf.save(OUT_PATH)
