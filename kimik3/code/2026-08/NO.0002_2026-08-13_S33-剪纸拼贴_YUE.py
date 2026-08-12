import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

random.seed(42)
S = 2
W, H = 1000*S, 1620*S

def f(path, size, idx=4):
    return ImageFont.truetype(path, size*S, index=idx)

SANSB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SERIFB = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

# ---------- base paper ----------
base = Image.new("RGB", (W, H), (232, 220, 198))
arr = np.array(base).astype(np.float32)
noise = np.random.default_rng(7).normal(0, 7, (H, W, 1))
arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
base = Image.fromarray(arr, "RGB")

yy, xx = np.mgrid[0:H, 0:W]
cx, cy = W/2, H/2
d = np.sqrt(((xx-cx)/(W*0.72))**2 + ((yy-cy)/(H*0.72))**2)
vig = np.clip(1 - 0.22*np.clip(d-0.55, 0, 1)**1.5, 0, 1)
arr = (np.array(base).astype(np.float32) * vig[..., None]).astype(np.uint8)
base = Image.fromarray(arr, "RGB")

def torn_poly(x, y, w, h, jag=6*S, seed=0):
    rng = random.Random(seed)
    pts = []
    n = 14
    for i in range(n+1):
        pts.append((x + w*i/n, y + rng.uniform(-jag, jag)))
    for i in range(1, n+1):
        pts.append((x + w + rng.uniform(-jag, jag), y + h*i/n))
    for i in range(1, n+1):
        pts.append((x + w*(1-i/n), y + h + rng.uniform(-jag, jag)))
    for i in range(1, n):
        pts.append((x + rng.uniform(-jag, jag), y + h*(1-i/n)))
    return pts

def paper_piece(img, x, y, w, h, color, seed, jag=6*S, shadow_blur=10*S, shadow_off=7*S, rot=0):
    pts = torn_poly(x, y, w, h, jag, seed)
    pw, ph = int(w+80*S), int(h+80*S)
    layer = Image.new("RGBA", (pw, ph), (0,0,0,0))
    ld = ImageDraw.Draw(layer)
    off = 40*S
    lpts = [(px-x+off, py-y+off) for px, py in pts]
    ld.polygon([(px+random.uniform(-3,3)*S, py+random.uniform(-3,3)*S) for px, py in lpts],
               fill=(255,255,255,255))
    ld.polygon(lpts, fill=color+(255,))
    la = np.array(layer).astype(np.float32)
    tnoise = np.random.default_rng(seed).normal(0, 6, la.shape[:2])[..., None]
    la[..., :3] = np.clip(la[..., :3] + tnoise, 0, 255)
    layer = Image.fromarray(la.astype(np.uint8), "RGBA")
    mask = layer.split()[3]
    shm = mask.filter(ImageFilter.GaussianBlur(shadow_blur))
    dark = Image.new("RGBA", (pw, ph), (40, 25, 15, 255))
    dark.putalpha(shm.point(lambda a: a*0.45))
    if rot:
        layer = layer.rotate(rot, expand=True, resample=Image.BICUBIC)
        dark = dark.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(dark, (int(x-off+shadow_off), int(y-off+shadow_off)))
    img.alpha_composite(layer, (int(x-off), int(y-off)))

canvas = base.convert("RGBA")

RED    = (196, 60, 48)
DARKRED= (150, 38, 34)
TEAL   = (58, 118, 116)
MUSTARD= (219, 164, 60)
INK    = (46, 40, 36)
CREAM  = (246, 240, 226)
PINK   = (222, 140, 122)

# ---------- background scraps ----------
paper_piece(canvas, -60*S, 90*S, 420*S, 300*S, TEAL, 11, rot=-6)
paper_piece(canvas, W-330*S, 40*S, 400*S, 260*S, MUSTARD, 12, rot=5)
paper_piece(canvas, -80*S, H-460*S, 460*S, 380*S, MUSTARD, 13, rot=4)
paper_piece(canvas, W-380*S, H-520*S, 460*S, 420*S, TEAL, 14, rot=-5)
paper_piece(canvas, W-260*S, 620*S, 300*S, 240*S, PINK, 15, rot=8)
paper_piece(canvas, -40*S, 780*S, 280*S, 220*S, PINK, 16, rot=-7)

# ---------- central cream sheet ----------
mx, my, mw, mh = 90*S, 110*S, 820*S, 1400*S
paper_piece(canvas, mx, my, mw, mh, CREAM, 20, jag=8*S, shadow_blur=16*S, shadow_off=10*S)
main = ImageDraw.Draw(canvas)

# ---------- big "=" emblem ----------
ecx, ecy, er = W//2, 460*S, 225*S
circ = Image.new("RGBA", (er*2+60*S, er*2+60*S), (0,0,0,0))
cd = ImageDraw.Draw(circ)
off = 30*S
cpts = []
for i in range(48):
    a = 2*np.pi*i/48
    r = er + random.uniform(-6, 6)*S
    cpts.append((off+er + r*np.cos(a), off+er + r*np.sin(a)))
cd.polygon(cpts, fill=DARKRED+(255,))
ca = np.array(circ).astype(np.float32)
cn = np.random.default_rng(3).normal(0, 6, ca.shape[:2])[..., None]
ca[..., :3] = np.clip(ca[..., :3]+cn, 0, 255)
circ = Image.fromarray(ca.astype(np.uint8), "RGBA")
cshm = circ.split()[3].filter(ImageFilter.GaussianBlur(10*S)).point(lambda a: a*0.5)
cdark = Image.new("RGBA", circ.size, (40,25,15,255)); cdark.putalpha(cshm)
canvas.alpha_composite(cdark, (ecx-er-off+8*S, ecy-er-off+10*S))
canvas.alpha_composite(circ, (ecx-er-off, ecy-er-off))

bar_w, bar_h = 300*S, 46*S
gap = 60*S
paper_piece(canvas, ecx-bar_w//2, ecy-gap//2-bar_h, bar_w, bar_h, CREAM, 31, jag=3*S, shadow_blur=5*S, shadow_off=4*S)
paper_piece(canvas, ecx-bar_w//2, ecy+gap//2, bar_w, bar_h, CREAM, 32, jag=3*S, shadow_blur=5*S, shadow_off=4*S)
main = ImageDraw.Draw(canvas)

# ---------- quote ----------
quote_lines = [
    "平等呢樣嘢，",
    "天上面冇現成嘅。",
    "係有人肯畫兩條平衡線出嚟，",
    "同全世界講：",
    "冇兩樣嘢，可以更加相等。",
]
q_f = f(SERIFB, 44)
qy = 735*S
for ln in quote_lines:
    lw = main.textlength(ln, font=q_f)
    main.text(((W-lw)/2, qy), ln, font=q_f, fill=INK)
    qy += 74*S

# scissors divider
dy = qy + 12*S
main.line([(W/2-160*S, dy), (W/2-30*S, dy)], fill=RED, width=3*S)
main.line([(W/2+30*S, dy), (W/2+160*S, dy)], fill=RED, width=3*S)
main.ellipse([W/2-16*S, dy-6*S, W/2-4*S, dy+6*S], outline=RED, width=3*S)
main.ellipse([W/2+4*S, dy-6*S, W/2+16*S, dy+6*S], outline=RED, width=3*S)
main.line([(W/2-4*S, dy-3*S), (W/2+12*S, dy-14*S)], fill=RED, width=3*S)
main.line([(W/2+4*S, dy-3*S), (W/2-12*S, dy-14*S)], fill=RED, width=3*S)

# ---------- fact (token wrap, keep latin words whole, no leading punctuation) ----------
fact_f = f(SERIF, 29)
maxw = 640*S
tokens = []
buf = ""
for ch in FACT:
    if ch.isascii() and (ch.isalnum() or ch == "."):
        buf += ch
    else:
        if buf:
            tokens.append(buf); buf = ""
        tokens.append(ch)
if buf:
    tokens.append(buf)

PUNCT = set("，。、；：？！」』》")
lines, cur = [], ""
for tk in tokens:
    if cur and main.textlength(cur + tk, font=fact_f) > maxw:
        # never let punctuation start a new line: glue it to previous line
        if tk in PUNCT:
            cur += tk
            lines.append(cur); cur = ""
        else:
            lines.append(cur); cur = tk
    else:
        cur += tk
if cur:
    lines.append(cur)
# safety pass: pull any remaining leading punctuation back to previous line
fixed = []
for ln in lines:
    if fixed and ln and ln[0] in PUNCT:
        fixed[-1] += ln[0]
        ln = ln[1:]
        if ln:
            fixed.append(ln)
    else:
        fixed.append(ln)
lines = fixed

fy = dy + 42*S
for ln in lines:
    lw = main.textlength(ln, font=fact_f)
    main.text(((W-lw)/2, fy), ln, font=fact_f, fill=(70, 60, 52))
    fy += 48*S

# ---------- serial / date stamp ----------
st_f = f(SANSB, 26)
stamp = f"{SERIAL} ｜ {DATE}"
sw = main.textlength(stamp, font=st_f)
sx, sy = (W-sw)/2, fy + 30*S
main.rounded_rectangle([sx-24*S, sy-14*S, sx+sw+24*S, sy+44*S], radius=12*S, outline=DARKRED, width=3*S)
main.text((sx, sy), stamp, font=st_f, fill=DARKRED)

canvas.convert("RGB").save(OUT_PATH)
