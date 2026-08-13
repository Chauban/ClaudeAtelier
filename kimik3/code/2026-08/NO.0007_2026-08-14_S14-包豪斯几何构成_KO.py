S = 2

from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1000*S, 2200*S
CREAM = (244, 238, 226)
BLACK = (20, 20, 20)
RED = (200, 30, 30)
YELLOW = (240, 180, 30)
BLUE = (30, 60, 160)
GRAY = (90, 88, 82)

img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)

KO_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
KO_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

def font(path, size, idx):
    return ImageFont.truetype(path, size*S, index=idx)

MARGIN = 80*S
NO_BREAK_BEFORE = "·）」』。，、：；！？"

def draw_mixed(text, x0, y0, maxw, ko_f, zh_f, color, line_h):
    cx0, cy0 = x0, y0
    in_paren = False
    for ch in text:
        if ch in "（":
            in_paren = True
        fnt = zh_f if (in_paren or ch in "（）") else ko_f
        cw = d.textlength(ch, font=fnt)
        if cx0 + cw > x0 + maxw and cx0 > x0 and ch not in NO_BREAK_BEFORE:
            cx0 = x0
            cy0 += line_h
        d.text((cx0, cy0), ch, font=fnt, fill=color)
        cx0 += cw
        if ch in "）":
            in_paren = False
    return cy0 + line_h

# ===== Bauhaus hero composition =====
d.rectangle([0, 0, W, 14*S], fill=BLACK)

cx, cy, r = 830*S, 280*S, 250*S
d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=RED)

d.polygon([(MARGIN, 590*S), (MARGIN, 310*S), (350*S, 590*S)], fill=BLUE)

bx, by, br = 420*S, 590*S, 120*S
d.pieslice([bx-br, by-br, bx+br, by+br], 180, 360, fill=YELLOW)

for i in range(14):
    a = math.radians(i*(360/14) + 8)
    px = cx + (r + 55*S)*math.cos(a)
    py = cy + (r + 55*S)*math.sin(a)
    rr = 9*S
    d.ellipse([px-rr, py-rr, px+rr, py+rr], fill=BLACK)

tx, ty = 650*S, 570*S
d.polygon([(tx, ty-64*S), (tx-32*S, ty), (tx+32*S, ty)], fill=BLACK)
d.rectangle([tx-6*S, ty, tx+6*S, ty+32*S], fill=BLACK)

d.rectangle([MARGIN, 660*S, W-MARGIN, 672*S], fill=BLACK)
d.rectangle([W-MARGIN-40*S, 636*S, W-MARGIN, 676*S], fill=YELLOW, outline=BLACK, width=3*S)

# ===== meta =====
f_meta = font(KO_B, 26, 1)
f_meta2 = font(KO_R, 24, 1)
d.rectangle([MARGIN, 700*S, MARGIN+26*S, 760*S], fill=RED)
d.text((MARGIN+44*S, 708*S), SERIAL, font=f_meta, fill=BLACK)
d.text((MARGIN+44*S, 708*S+34*S), DATE, font=f_meta2, fill=GRAY)

# ===== quote (verbatim; Korean face for Korean, SC face inside Chinese parens) =====
y = 830*S
y = draw_mixed(QUOTE, MARGIN, y, W-2*MARGIN,
               font(KO_B, 40, 1), font(KO_B, 40, 2), BLACK, 60*S)

# ===== divider =====
y += 34*S
d.rectangle([MARGIN, y, W-MARGIN, y+6*S], fill=BLACK)
d.rectangle([MARGIN, y-18*S, MARGIN+42*S, y+24*S], fill=BLUE)
cy2 = y + 3*S
d.ellipse([W-MARGIN-42*S, cy2-21*S, W-MARGIN, cy2+21*S], fill=YELLOW, outline=BLACK, width=3*S)
y += 50*S

# ===== fact (verbatim, same mixed-face treatment) =====
y = draw_mixed(FACT, MARGIN, y, W-2*MARGIN,
               font(KO_R, 30, 1), font(KO_R, 30, 2), BLACK, 47*S)

# ===== small Bauhaus motif to balance lower area =====
y += 46*S
mx = W//2
d.ellipse([mx-120*S, y, mx-86*S, y+34*S], fill=RED)
d.polygon([(mx-17*S, y+34*S), (mx, y), (mx+17*S, y+34*S)], fill=BLUE)
d.rectangle([mx+86*S, y, mx+120*S, y+34*S], fill=YELLOW, outline=BLACK, width=3*S)
y += 34*S + 20*S

# ===== footer =====
fy = H - 90*S
d.rectangle([0, fy, W, H], fill=BLACK)
d.ellipse([MARGIN, fy+28*S, MARGIN+34*S, fy+62*S], fill=RED)
d.polygon([(MARGIN+60*S, fy+62*S), (MARGIN+77*S, fy+28*S), (MARGIN+94*S, fy+62*S)], fill=BLUE)
d.rectangle([MARGIN+120*S, fy+28*S, MARGIN+154*S, fy+62*S], fill=YELLOW)

if y > fy - 20*S:
    raise RuntimeError("overflow: y=%d fy=%d" % (y, fy))

img.save(OUT_PATH)
