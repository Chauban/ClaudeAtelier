import random
import math
from PIL import Image, ImageDraw, ImageFont

S = 2
W, H = 1000, 1760
img = Image.new("RGB", (W*S, H*S), (10, 10, 26))
d = ImageDraw.Draw(img)

def px(x, y, w, h, c):
    if w <= 0 or h <= 0:
        return
    d.rectangle([x*S, y*S, (x+w)*S-1, (y+h)*S-1], fill=c)

CJK_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
CJK_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

f_hud = ImageFont.truetype(MONO, 30*S)
f_quote = ImageFont.truetype(CJK_B, 36*S, index=2)
f_fact = ImageFont.truetype(CJK_R, 30*S, index=2)

# ---------- sky: pixel gradient bands ----------
bands = [(8,8,24),(12,10,34),(16,13,46),(20,16,58),(25,20,70),(30,24,82)]
sky_top, sky_bot = 96, 880
band_h = (sky_bot - sky_top) // len(bands)
for i, c in enumerate(bands):
    px(0, sky_top + i*band_h, W, band_h + 2, c)

# ---------- stars ----------
random.seed(42)
for _ in range(90):
    x = random.randint(8, W-16)
    y = random.randint(110, sky_bot-120)
    s = random.choice([2, 3, 3, 4])
    c = random.choice([(255,255,255),(255,240,180),(180,220,255),(200,255,220)])
    px(x, y, s, s, c)
for _ in range(10):
    x = random.randint(20, W-40)
    y = random.randint(130, 500)
    px(x-6, y, 14, 3, (255,255,230))
    px(x, y-6, 3, 14, (255,255,230))

# pixel moon
for r in range(10):
    px(820 - (10-r)*2, 150 + r*10, 20 + (10-r)*4, 10, (250, 240, 200))
px(838, 168, 12, 12, (220, 210, 170))
px(852, 200, 10, 10, (220, 210, 170))

# ---------- distant pixel mountains ----------
for base_x, mh, mw in [(0, 220, 260), (180, 170, 300), (420, 240, 320), (680, 180, 320)]:
    for step in range(0, mw, 20):
        t = 1 - abs(step - mw/2) / (mw/2)
        hh = int(mh * t)
        if hh > 0:
            px(base_x + step, sky_bot - hh, 20, hh, (18, 26, 48))

# ---------- ground ----------
ground_y = 880
px(0, ground_y, W, 14, (86, 200, 90))
px(0, ground_y + 14, W, 10, (60, 160, 70))
for gx in range(0, W, 40):
    px(gx + 8, ground_y - 8, 8, 8, (86, 200, 90))
    px(gx + 24, ground_y - 6, 6, 6, (60, 160, 70))
px(0, ground_y + 24, W, 150, (74, 48, 32))
for gy in range(ground_y + 24, ground_y + 174, 24):
    for gx in range(0, W, 24):
        if (gx//24 + gy//24) % 2 == 0:
            px(gx, gy, 24, 24, (88, 58, 40))
        elif random.random() < 0.08:
            px(gx + 8, gy + 8, 8, 8, (120, 84, 56))

# ---------- venus flytrap sprite ----------
sw, sh = 56, 48
spr = Image.new("RGBA", (sw, sh), (0,0,0,0))
sd = ImageDraw.Draw(spr)
GD, GL = (30, 120, 50), (70, 190, 80)
RD, RL = (200, 60, 90), (240, 110, 130)
TEETH = (235, 245, 220)
sd.rectangle([26, 30, 29, 47], fill=GD)
sd.rectangle([27, 30, 28, 47], fill=GL)
sd.polygon([(26, 44), (8, 40), (4, 44), (20, 47)], fill=GD)
sd.polygon([(29, 45), (48, 41), (52, 45), (34, 47)], fill=GD)
sd.pieslice([10, 8, 46, 40], 20, 160, fill=GD)
sd.pieslice([14, 12, 42, 36], 20, 160, fill=RL)
sd.pieslice([10, 0, 46, 32], 200, 340, fill=GD)
sd.pieslice([14, 4, 42, 28], 200, 340, fill=RL)
for ang in range(20, 161, 18):
    a = math.radians(ang)
    x1, y1 = 28 + 18*math.cos(a), 24 + 16*math.sin(a)
    x2, y2 = 28 + 23*math.cos(a), 24 + 21*math.sin(a)
    sd.line([x1, y1, x2, y2], fill=TEETH, width=1)
for ang in range(200, 341, 18):
    a = math.radians(ang)
    x1, y1 = 28 + 18*math.cos(a), 16 + 16*math.sin(a)
    x2, y2 = 28 + 23*math.cos(a), 16 + 21*math.sin(a)
    sd.line([x1, y1, x2, y2], fill=TEETH, width=1)
for hx, hy in [(22, 26), (28, 28), (34, 26)]:
    sd.line([hx, hy, hx, hy - 3], fill=(255, 220, 220), width=1)
spr_big = spr.resize((sw*10, sh*10), Image.NEAREST)
img.paste(spr_big, (240*S, (ground_y - sh*10 + 6)*S), spr_big)

# ---------- fly sprite (clear pixel fly with dotted trail, away from moon) ----------
fw, fh = 16, 12
fly = Image.new("RGBA", (fw, fh), (0,0,0,0))
fd = ImageDraw.Draw(fly)
fd.rectangle([2, 0, 6, 3], fill=(190, 220, 255, 200))   # left wing
fd.rectangle([9, 0, 13, 3], fill=(190, 220, 255, 200))  # right wing
fd.rectangle([4, 4, 11, 9], fill=(45, 45, 58))          # body
fd.rectangle([11, 5, 14, 7], fill=(45, 45, 58))         # head
fd.point([(5, 5), (10, 5)], fill=(255, 90, 90))         # stripes
fly_big = fly.resize((fw*9, fh*9), Image.NEAREST)
fx, fy = 640, 420
img.paste(fly_big, (fx*S, fy*S), fly_big)
# dotted flight path curving toward the trap
for t in range(0, 30, 5):
    px(fx + 60 + t*9, fy + 40 + t*7, 7, 7, (150, 150, 200))
# sparkle near trap trigger hairs
px(430, 610, 6, 18, (255, 255, 180))
px(424, 616, 18, 6, (255, 255, 180))

# ---------- HUD bar ----------
px(0, 0, W, 96, (6, 6, 16))
px(0, 92, W, 4, (90, 220, 100))

def heart(x, y, c):
    rows = ["01100110","11111111","11111111","01111110","00111100","00011000"]
    for ry, row in enumerate(rows):
        for rx, ch in enumerate(row):
            if ch == "1":
                px(x + rx*4, y + ry*4, 4, 4, c)

for i in range(3):
    heart(36 + i*44, 34, (255, 70, 90))
heart(36 + 3*44, 34, (60, 40, 50))

tw = d.textlength(SERIAL, font=f_hud) / S
d.text(((W/2 - tw/2)*S, 32*S), SERIAL, font=f_hud, fill=(255, 230, 90))
tw2 = d.textlength(DATE, font=f_hud) / S
d.text(((W - 40 - tw2)*S, 32*S), DATE, font=f_hud, fill=(140, 220, 255))

# ---------- dialog box ----------
bx, by, bw, bh = 40, 1060, W - 80, 640
px(bx + 10, by + 10, bw, bh, (0, 0, 0))
px(bx, by, bw, bh, (16, 20, 40))
px(bx, by, bw, 6, (245, 245, 245)); px(bx, by + bh - 6, bw, 6, (245, 245, 245))
px(bx, by, 6, bh, (245, 245, 245)); px(bx + bw - 6, by, 6, bh, (245, 245, 245))
px(bx + 12, by + 12, bw - 24, 4, (90, 220, 100)); px(bx + 12, by + bh - 16, bw - 24, 4, (90, 220, 100))
px(bx + 12, by + 12, 4, bh - 24, (90, 220, 100)); px(bx + bw - 16, by + 12, 4, bh - 24, (90, 220, 100))
for cx in (bx, bx + bw - 20):
    for cy in (by, by + bh - 20):
        px(cx, cy, 20, 20, (255, 230, 90))

def wrap_cjk(text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        t = cur + ch
        if d.textlength(t, font=font) / S > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines

max_tw = bw - 110
tx = bx + 56
ty = by + 56

q_lines = wrap_cjk(QUOTE, f_quote, max_tw)
for ln in q_lines:
    d.text((tx*S, ty*S), ln, font=f_quote, fill=(255, 255, 255))
    ty += 56
ty += 14
for dx in range(tx, bx + bw - 56, 28):
    px(dx, ty, 14, 4, (90, 220, 100))
ty += 26
f_lines = wrap_cjk(FACT, f_fact, max_tw)
for ln in f_lines:
    d.text((tx*S, ty*S), ln, font=f_fact, fill=(170, 235, 180))
    ty += 50

cur_y = by + bh - 56
d.polygon([((bx + bw - 70)*S, cur_y*S), ((bx + bw - 46)*S, cur_y*S), ((bx + bw - 58)*S, (cur_y + 18)*S)], fill=(255, 230, 90))

# ---------- scanlines ----------
overlay = Image.new("RGBA", (W*S, H*S), (0,0,0,0))
od = ImageDraw.Draw(overlay)
for yy in range(0, H*S, 6*S):
    od.rectangle([0, yy, W*S, yy + 2*S], fill=(0, 0, 0, 26))
img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

img.save(OUT_PATH)
