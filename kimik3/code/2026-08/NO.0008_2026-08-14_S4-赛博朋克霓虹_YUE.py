import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2
W, H = 1000, 1560
w, h = W*S, H*S

SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SANS_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
IDX = 4

def F(path, size):
    return ImageFont.truetype(path, size*S, index=IDX)

# ---------- background ----------
y = np.linspace(0, 1, h)[:, None].astype(np.float32)
top = np.array([8, 4, 24], dtype=np.float32)
mid = np.array([26, 6, 52], dtype=np.float32)
bot = np.array([60, 8, 60], dtype=np.float32)
bg = np.zeros((h, w, 3), dtype=np.float32)
m1 = np.clip(y/0.55, 0, 1)
bg[:] = top*(1-m1[..., None]) + mid*m1[..., None]
m2 = np.clip((y-0.55)/0.45, 0, 1)
bg = bg*(1-m2[..., None]) + bot*m2[..., None]
rng = np.random.default_rng(8)
bg += rng.normal(0, 4, (h, w, 1))
img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB")
draw = ImageDraw.Draw(img, "RGBA")

# ---------- rolling neon cloud band ----------
cloud_y = int(h*0.17)
for i in range(5):
    cy = cloud_y + i*int(16*S)
    for k in range(26):
        xx = int(-60*S + k*(w+120*S)/25)
        r = int((52 - i*7)*S)
        lay = Image.new("RGBA", (w, h), (0,0,0,0))
        d = ImageDraw.Draw(lay)
        col = (255, 60, 200, 95 - i*15) if i % 2 == 0 else (0, 220, 255, 95 - i*15)
        d.ellipse([xx-r, cy-r//2, xx+r, cy+r//2], fill=col)
        lay = lay.filter(ImageFilter.GaussianBlur(20*S))
        img = Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

# second rolling tube lower, dimmer (adds depth behind fact panel area)
cloud2_y = int(h*0.30)
for k in range(20):
    xx = int(-40*S + k*(w+80*S)/19)
    r = int(30*S)
    lay = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(lay)
    d.ellipse([xx-r, cloud2_y-r//2, xx+r, cloud2_y+r//2], fill=(0, 200, 255, 55))
    lay = lay.filter(ImageFilter.GaussianBlur(16*S))
    img = Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

# ---------- perspective grid floor ----------
horizon = int(h*0.74)
lay = Image.new("RGBA", (w, h), (0,0,0,0))
d = ImageDraw.Draw(lay)
for i in range(21):
    fx = (i - 10) / 10.0
    xb = w/2 + fx*w*1.6
    d.line([(w/2, horizon), (xb, h)], fill=(255, 40, 200, 150), width=2*S)
for j in range(14):
    t = (j/13.0)**2.2
    yy = horizon + t*(h-horizon)
    a = int(40 + 170*t)
    d.line([(0, yy), (w, yy)], fill=(0, 210, 255, a), width=max(1, int((1+2*t)*S)))
lay = lay.filter(ImageFilter.GaussianBlur(1.2*S))
img = Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

# neon glow at horizon then darken floor
lay = Image.new("RGBA", (w, h), (0,0,0,0))
d = ImageDraw.Draw(lay)
d.ellipse([w/2-280*S, horizon-280*S, w/2+280*S, horizon+280*S], fill=(255, 30, 160, 110))
lay = lay.filter(ImageFilter.GaussianBlur(60*S))
img = Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")
mask = Image.new("L", (w, h), 0)
md = ImageDraw.Draw(mask)
md.rectangle([0, horizon, w, h], fill=255)
black = Image.new("RGB", (w, h), (8, 4, 24))
img = Image.composite(black, img, mask)
draw = ImageDraw.Draw(img, "RGBA")

# ---------- neon frame ----------
lay = Image.new("RGBA", (w, h), (0,0,0,0))
d = ImageDraw.Draw(lay)
pad = 36*S
d.rectangle([pad, pad, w-pad, h-pad], outline=(0, 240, 255, 220), width=3*S)
lay_b = lay.filter(ImageFilter.GaussianBlur(8*S))
img = Image.alpha_composite(img.convert("RGBA"), lay_b)
img = Image.alpha_composite(img, lay)
draw = ImageDraw.Draw(img, "RGBA")

# ---------- text helpers ----------
def neon_text(base, pos, text, font, rgb, anchor_center=None, blur=10, glow_alpha=170):
    lay = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(lay)
    if anchor_center is not None:
        bb = d.textbbox((0,0), text, font=font)
        tw = bb[2]-bb[0]
        core_x = anchor_center - tw/2 - bb[0]
    else:
        core_x = pos[0]
    d.text((core_x, pos[1]), text, font=font, fill=rgb+(glow_alpha,))
    gl = lay.filter(ImageFilter.GaussianBlur(blur*S))
    out = Image.alpha_composite(base.convert("RGBA"), gl)
    out = Image.alpha_composite(out, gl)
    d2 = ImageDraw.Draw(out)
    d2.text((core_x, pos[1]), text, font=font, fill=rgb+(255,))
    return out.convert("RGB")

def tokenize(text):
    toks, cur = [], ""
    for ch in text:
        if ch.isascii() and (ch.isalnum() or ch == '.'):
            cur += ch
        else:
            if cur:
                toks.append(cur)
                cur = ""
            toks.append(ch)
    if cur:
        toks.append(cur)
    return toks

def wrap(drw, text, font, maxw):
    lines, cur = [], ""
    for tk in tokenize(text):
        t = cur + tk
        if drw.textbbox((0,0), t, font=font)[2] > maxw and cur:
            lines.append(cur)
            cur = tk if tk != " " else ""
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines

# ---------- layout plan ----------
fq = F(SANS_R, 38)
ff = F(SANS_R, 33)
fh = F(SANS, 30)
maxw_q = (W-200)*S
maxw_f = (W-220)*S
quote_lines = wrap(draw, QUOTE, fq, maxw_q)
fact_lines = wrap(draw, FACT, ff, maxw_f)
lh_q = 64*S
lh_f = 56*S
q_panel_h = lh_q*len(quote_lines) + 80*S
f_panel_h = lh_f*len(fact_lines) + 90*S
header_h = 150*S
gap = 70*S
total = header_h + q_panel_h + gap + f_panel_h
top_margin = (h - total)//2 + 10*S

# ---------- header: serial + date (only allowed texts) ----------
img = neon_text(img, (0, top_margin), SERIAL, fh, (255, 60, 200), anchor_center=w/2, blur=7)
img = neon_text(img, (0, top_margin + 52*S), DATE, fh, (0, 240, 255), anchor_center=w/2, blur=7)
draw = ImageDraw.Draw(img, "RGBA")
lay = Image.new("RGBA", (w, h), (0,0,0,0))
d = ImageDraw.Draw(lay)
dy = top_margin + 108*S
d.line([(w/2-220*S, dy), (w/2+220*S, dy)], fill=(0, 240, 255, 200), width=2*S)
img = Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(4*S)))
img = Image.alpha_composite(img, lay)
draw = ImageDraw.Draw(img, "RGBA")

# ---------- quote panel ----------
qy = top_margin + header_h
lay = Image.new("RGBA", (w, h), (0,0,0,0))
d = ImageDraw.Draw(lay)
d.rectangle([90*S, qy-40*S, w-90*S, qy+q_panel_h-40*S], fill=(10, 6, 30, 195), outline=(255, 60, 200, 220), width=2*S)
img = Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(6*S)))
img = Image.alpha_composite(img, lay)
for i, ln in enumerate(quote_lines):
    img = neon_text(img, (0, qy + i*lh_q), ln, fq, (255, 230, 250), anchor_center=w/2, blur=5)
draw = ImageDraw.Draw(img, "RGBA")
for cx, cy2, sx, sy in [(90*S, qy-40*S, 1, 1), (w-90*S, qy-40*S, -1, 1),
                        (90*S, qy+q_panel_h-40*S, 1, -1), (w-90*S, qy+q_panel_h-40*S, -1, -1)]:
    L = 26*S
    draw.line([(cx, cy2), (cx+sx*L, cy2)], fill=(255, 220, 60, 255), width=4*S)
    draw.line([(cx, cy2), (cx, cy2+sy*L)], fill=(255, 220, 60, 255), width=4*S)

# ---------- fact panel ----------
fy = qy + q_panel_h + gap
lay = Image.new("RGBA", (w, h), (0,0,0,0))
d = ImageDraw.Draw(lay)
d.rectangle([90*S, fy-40*S, w-90*S, fy+f_panel_h-40*S], fill=(8, 10, 34, 200), outline=(0, 240, 255, 220), width=2*S)
img = Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(6*S)))
img = Image.alpha_composite(img, lay)
for i, ln in enumerate(fact_lines):
    img = neon_text(img, (110*S, fy + i*lh_f), ln, ff, (200, 245, 255), blur=4)
draw = ImageDraw.Draw(img, "RGBA")
for cx, cy2, sx, sy in [(90*S, fy-40*S, 1, 1), (w-90*S, fy-40*S, -1, 1),
                        (90*S, fy+f_panel_h-40*S, 1, -1), (w-90*S, fy+f_panel_h-40*S, -1, -1)]:
    L = 26*S
    draw.line([(cx, cy2), (cx+sx*L, cy2)], fill=(255, 220, 60, 255), width=4*S)
    draw.line([(cx, cy2), (cx, cy2+sy*L)], fill=(255, 220, 60, 255), width=4*S)

# ---------- scanlines ----------
arr = np.array(img).astype(np.float32)
ys = np.arange(h)[:, None, None]
arr *= (0.92 + 0.08*np.sin(ys*np.pi/(2*S)))
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

img.save(OUT_PATH)
