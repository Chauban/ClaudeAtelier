import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1000, 1600
S = 2
img = Image.new("RGB", (W*S, H*S), (8, 12, 32))
d = ImageDraw.Draw(img)

# --- deep sky gradient ---
import numpy as np
yy = np.linspace(0, 1, H*S)[:, None]
xx = np.linspace(0, 1, W*S)[None, :]
base = np.zeros((H*S, W*S, 3), dtype=np.float32)
base[..., 0] = 6 + 10*(1-yy)
base[..., 1] = 10 + 14*(1-yy)
base[..., 2] = 30 + 30*(1-yy)
# subtle nebula glows
for cx, cy, r, col in [(0.25, 0.3, 0.35, (20, 12, 45)), (0.75, 0.65, 0.4, (10, 25, 50)), (0.5, 0.85, 0.35, (25, 10, 35))]:
    dist = np.sqrt((xx-cx)**2 + (yy-cy)**2)
    glow = np.clip(1 - dist/r, 0, 1)**2
    for c in range(3):
        base[..., c] += glow * col[c]
img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(img)

rng = random.Random(42)

# --- star field ---
def star(x, y, r, bright, tint=(255, 255, 255)):
    col = tuple(int(c*bright) for c in tint)
    d.ellipse([x-r, y-r, x+r, y+r], fill=col)
    if r > 2.2:
        glow = r*4
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.ellipse([x-glow, y-glow, x+glow, y+glow], fill=col + (60,))
        g = g.filter(ImageFilter.GaussianBlur(r*2))
        img.paste(Image.alpha_composite(img.convert("RGBA"), g).convert("RGB"), (0, 0))
        d.ellipse([x-r, y-r, x+r, y+r], fill=col)

for _ in range(260):
    x = rng.uniform(0, W*S); y = rng.uniform(0, H*S)
    r = rng.uniform(0.6, 2.4)*S/2
    b = rng.uniform(0.35, 1.0)
    tint = rng.choice([(255,255,255),(220,230,255),(255,240,220),(200,215,255)])
    d.ellipse([x-r, y-r, x+r, y+r], fill=tuple(int(c*b) for c in tint))
for _ in range(24):
    star(rng.uniform(0, W*S), rng.uniform(0, H*S), rng.uniform(2.4, 4.0)*S/2, 1.0,
         rng.choice([(255,255,255),(230,238,255),(255,245,225)]))

# crosshair sparkles on a few bright stars
for _ in range(10):
    x = rng.uniform(60, W-60)*S; y = rng.uniform(60, H-60)*S
    ln = rng.uniform(8, 16)*S
    d.line([x-ln, y, x+ln, y], fill=(200, 215, 255, 90) if False else (170, 190, 235), width=1)
    d.line([x, y-ln, x, y+ln], fill=(170, 190, 235), width=1)

# --- coordinate grid (faint, star-chart style) ---
for i in range(1, 6):
    yyg = H*S*i/6
    d.line([0, yyg, W*S, yyg], fill=(40, 55, 100), width=1)
for i in range(1, 4):
    xxg = W*S*i/4
    d.line([xxg, 0, xxg, H*S], fill=(40, 55, 100), width=1)
# horizon circle
d.ellipse([W*S*0.08, H*S*0.08, W*S*0.92, H*S*0.92], outline=(45, 60, 105), width=1)
d.ellipse([W*S*0.14, H*S*0.14, W*S*0.86, H*S*0.86], outline=(35, 48, 88), width=1)

# --- fonts ---
SER_R = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SER_B = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SANS_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
IDX = 3  # TC
def ser(sz, bold=False):
    return ImageFont.truetype(SER_B if bold else SER_R, sz, index=IDX)

f_title = ser(54, True)
f_quote = ser(40)
f_fact = ser(30)
f_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
f_serial = ser(30, True)

GOLD = (232, 196, 120)
LINE = (150, 175, 230)
TXT = (235, 240, 250)
DIM = (160, 175, 205)

# --- constellation: pinball machine playfield, drawn as star-map lines ---
cx0, cy0 = W*S*0.5, H*S*0.42
pts = {
    "A": (cx0-260*S/2, cy0-300*S/2),
    "B": (cx0+260*S/2, cy0-300*S/2),
    "C": (cx0+300*S/2, cy0+120*S/2),
    "D": (cx0+180*S/2, cy0+340*S/2),
    "E": (cx0+60*S/2, cy0+300*S/2),
    "F": (cx0-60*S/2, cy0+300*S/2),
    "G": (cx0-180*S/2, cy0+340*S/2),
    "H": (cx0-300*S/2, cy0+120*S/2),
}
order = ["A","B","C","D","E","F","G","H","A"]
for i in range(len(order)-1):
    p1, p2 = pts[order[i]], pts[order[i+1]]
    d.line([p1[0], p1[1], p2[0], p2[1]], fill=LINE, width=2)

# inner details: plunger lane, bumpers, flippers
inner = [
    ((cx0+225*S/2, cy0-300*S/2), (cx0+225*S/2, cy0+180*S/2)),
    ((cx0-120*S/2, cy0+120*S/2), (cx0-150*S/2, cy0+260*S/2)),
    ((cx0+120*S/2, cy0+120*S/2), (cx0+150*S/2, cy0+260*S/2)),
]
for p1, p2 in inner:
    d.line([p1[0], p1[1], p2[0], p2[1]], fill=(120, 145, 205), width=1)

# bumper circles (constellation rings)
bumpers = [(cx0-90*S/2, cy0-80*S/2), (cx0+90*S/2, cy0-80*S/2), (cx0, cy0+40*S/2)]
for bx, by in bumpers:
    d.ellipse([bx-46*S/2, by-46*S/2, bx+46*S/2, by+46*S/2], outline=LINE, width=2)
    d.ellipse([bx-24*S/2, by-24*S/2, bx+24*S/2, by+24*S/2], outline=(120,145,205), width=1)

# the ball's called trajectory: dotted arc from plunger up and around to top bumper
traj = []
for t in np.linspace(0, 1, 40):
    ang = math.pi*0.15 + t*math.pi*1.5
    rx = 200*S/2*(1 - 0.25*t)
    tx = cx0 + math.cos(ang)*rx + 40*S/2
    ty = cy0 + 60*S/2 - math.sin(ang)*(260*S/2)*(1-0.3*t)
    traj.append((tx, ty))
for i, (tx, ty) in enumerate(traj):
    if i % 2 == 0:
        r = 3.2*S/2
        d.ellipse([tx-r, ty-r, tx+r, ty+r], fill=GOLD)

# constellation stars (brighter, with glow)
const_layer = Image.new("RGBA", img.size, (0,0,0,0))
cd = ImageDraw.Draw(const_layer)
allstars = list(pts.values()) + bumpers + [traj[-1]]
for i, (sx, sy) in enumerate(allstars):
    r = (5 if i < 8 else 4)*S/2
    cd.ellipse([sx-r*3.4, sy-r*3.4, sx+r*3.4, sy+r*3.4], fill=(180, 200, 255, 40))
    cd.ellipse([sx-r, sy-r, sx+r, sy+r], fill=(255, 255, 255, 255))
const_layer = const_layer.filter(ImageFilter.GaussianBlur(2))
img = Image.alpha_composite(img.convert("RGBA"), const_layer).convert("RGB")
d = ImageDraw.Draw(img)
for sx, sy in allstars:
    r = 3.4*S/2
    d.ellipse([sx-r, sy-r, sx+r, sy+r], fill=(250, 252, 255))
# the golden ball at end of trajectory
bx, by = traj[-1]
d.ellipse([bx-9*S/2, by-9*S/2, bx+9*S/2, by+9*S/2], fill=GOLD)
d.ellipse([bx-14*S/2, by-14*S/2, bx+14*S/2, by+14*S/2], outline=(232,196,120), width=1)

# star labels
for (sx, sy), name in zip(list(pts.values())[:5], ["α", "β", "γ", "δ", "ε"]):
    d.text((sx+12*S, sy-16*S), name, font=f_label, fill=DIM)

# --- header ---
title = "星 圖 ・ 命 中 星 座"
tw = d.textbbox((0,0), title, font=f_title)[2]
d.text(((W*S-tw)/2, 70*S), title, font=f_title, fill=GOLD)
d.line([W*S*0.2, 150*S, W*S*0.8, 150*S], fill=(120, 140, 190), width=1)
for fx in (W*S*0.2, W*S*0.8):
    d.ellipse([fx-4*S, 150*S-4*S, fx+4*S, 150*S+4*S], outline=GOLD, width=1)

def wrap(text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if d.textbbox((0,0), cur+ch, font=font)[2] > maxw and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur: lines.append(cur)
    return lines

# --- quote block ---
qy = 1080*S
d.line([W*S*0.12, qy, W*S*0.88, qy], fill=(90, 105, 150), width=1)
d.text((W*S*0.5 - d.textbbox((0,0), "✦", font=f_fact)[2]/2, qy - 16*S), "✦", font=f_fact, fill=GOLD)
qy += 34*S
for ln in wrap(QUOTE, f_quote, W*S*0.78):
    lw = d.textbbox((0,0), ln, font=f_quote)[2]
    d.text(((W*S-lw)/2, qy), ln, font=f_quote, fill=TXT)
    qy += 62*S

# --- fact block ---
qy += 40*S
d.line([W*S*0.12, qy, W*S*0.88, qy], fill=(90, 105, 150), width=1)
qy += 34*S
for ln in wrap(FACT, f_fact, W*S*0.8):
    lw = d.textbbox((0,0), ln, font=f_fact)[2]
    d.text(((W*S-lw)/2, qy), ln, font=f_fact, fill=DIM)
    qy += 52*S

# --- footer: serial + date as chart catalog label ---
fy = H*S - 110*S
d.line([W*S*0.12, fy, W*S*0.88, fy], fill=(90, 105, 150), width=1)
lab1 = "CHART " + SERIAL.replace("NO.", "No. ") + "  ★  " + DATE
lab2 = "CONSTELLATIO FLIPPERIS ・ 預告之軌"
w1 = d.textbbox((0,0), lab1, font=f_serial)[2]
w2 = d.textbbox((0,0), lab2, font=f_fact)[2]
d.text(((W*S-w1)/2, fy+18*S), lab1, font=f_serial, fill=GOLD)
d.text(((W*S-w2)/2, fy+62*S), lab2, font=f_fact, fill=DIM)

# small compass rose top-left
crx, cry = 90*S, 90*S
d.ellipse([crx-26*S, cry-26*S, crx+26*S, cry+26*S], outline=(120,140,190), width=1)
d.line([crx, cry-34*S, crx, cry+34*S], fill=(120,140,190), width=1)
d.line([crx-34*S, cry, crx+34*S, cry], fill=(120,140,190), width=1)
d.polygon([(crx, cry-34*S), (crx-6*S, cry), (crx+6*S, cry)], fill=GOLD)

img = img.resize((W, H), Image.LANCZOS)
img.save(OUT_PATH)
