from PIL import Image, ImageDraw, ImageFont

S = 2  # deviceScaleFactor

def px(v):
    return int(v * S)

# ---------- logical canvas (taller so the FACT translation block clears the footer) ----------
W, H = 900, 1840
img = Image.new("RGB", (px(W), px(H)), (235, 232, 226))
d = ImageDraw.Draw(img)

# ---------- fonts ----------
MONO   = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANSB  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CJK    = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

def mono(sz, bold=False):
    return ImageFont.truetype(MONOB if bold else MONO, px(sz))

def sansb(sz):
    return ImageFont.truetype(SANSB, px(sz))

def cjk(sz):
    return ImageFont.truetype(CJK, px(sz), index=2)

# ---------- brutalist palette ----------
INK   = (18, 18, 18)
YEL   = (255, 214, 0)
RED   = (255, 60, 40)
BLUE  = (40, 70, 255)

def rect(x, y, w, h, fill=None, outline=INK, lw=3):
    d.rectangle([px(x), px(y), px(x + w), px(y + h)], fill=fill,
                outline=outline, width=px(lw))

def shadow_block(x, y, w, h, fill, off=10, outline=INK, lw=3):
    d.rectangle([px(x + off), px(y + off), px(x + w + off), px(y + h + off)], fill=INK)
    rect(x, y, w, h, fill=fill, outline=outline, lw=lw)

def text_w(txt, font):
    return d.textbbox((0, 0), txt, font=font)[2]

def wrap(txt, font, maxw):
    words = txt.split(" ")
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_w(t, font) <= px(maxw):
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

# ================= background: visible grid =================
for gx in range(0, W + 1, 75):
    d.line([(px(gx), 0), (px(gx), px(H))], fill=(214, 210, 202), width=px(1))
for gy in range(0, H + 1, 75):
    d.line([(0, px(gy)), (px(W), px(gy))], fill=(214, 210, 202), width=px(1))
for gx in range(0, W + 1, 150):
    d.line([(px(gx), 0), (px(gx), px(H))], fill=(202, 198, 190), width=px(1))

# ================= top bar (fake browser chrome) =================
rect(0, 0, W, 56, fill=INK, lw=0)
f_tb = mono(22, True)
d.ellipse([px(24), px(18), px(42), px(36)], fill=RED)
d.ellipse([px(54), px(18), px(72), px(36)], fill=YEL)
d.ellipse([px(84), px(18), px(102), px(36)], fill=(90, 220, 90))
d.text((px(130), px(15)), "phobos://mars/sky/reverse-orbit", font=f_tb, fill=(240, 240, 240))

# marquee strip
rect(0, 56, W, 40, fill=YEL, lw=0)
d.line([(0, px(56)), (px(W), px(56))], fill=INK, width=px(3))
d.line([(0, px(96)), (px(W), px(96))], fill=INK, width=px(3))
f_mq = mono(20, True)
d.text((px(20), px(64)), "*** FAKT IST FAKT *** DER MOND GEHT IM WESTEN AUF *** 7H39M ***",
       font=f_mq, fill=INK)

# ================= serial + date block =================
bx, by, bw, bh = 40, 130, 300, 96
shadow_block(bx, by, bw, bh, YEL, off=12)
f_ser = sansb(30)
f_dt  = mono(22, True)
d.text((px(bx + 20), px(by + 14)), SERIAL, font=f_ser, fill=INK)
d.text((px(bx + 20), px(by + 56)), DATE, font=f_dt, fill=INK)

# stamp block on right
shadow_block(560, 130, 300, 96, RED, off=12)
f_st = sansb(26)
t1 = "GEBEN SIE"
d.text((px(560 + (300 - text_w(t1, f_st) / S) / 2), px(146)), t1, font=f_st, fill=(255, 255, 255))
t2 = "DEN FAKT EIN"
d.text((px(560 + (300 - text_w(t2, f_st) / S) / 2), px(182)), t2, font=f_st, fill=(255, 255, 255))

# ================= QUOTE section =================
qy = 280
d.line([(px(40), px(qy)), (px(860), px(qy))], fill=INK, width=px(6))
f_tag = mono(24, True)
d.text((px(40), px(qy + 16)), "/zitat  [de]", font=f_tag, fill=BLUE)

quote_lines = [
    "„Weil, so schließt er",
    "messerscharf, nicht sein",
    "kann, was nicht sein darf.“",
]
f_q = sansb(44)
qy2 = qy + 64
for ln in quote_lines:
    d.text((px(44), px(qy2)), ln, font=f_q, fill=INK)
    qy2 += 66
f_attr = mono(26, True)
d.text((px(44), px(qy2 + 6)), "— Christian Morgenstern, „Die unmögliche Tatsache“",
       font=f_attr, fill=INK)

# Chinese translation of quote in a boxed block
ty = qy2 + 66
tb_h = 96
d.rectangle([px(52), px(ty + 10), px(852), px(ty + 10 + tb_h)], fill=INK)
rect(40, ty, 800, tb_h, fill=(255, 255, 255), lw=3)
f_tr = cjk(28)
d.text((px(64), px(ty + 16)), "因为他刀锋般锐利地推断：", font=f_tr, fill=INK)
d.text((px(64), px(ty + 52)), "不该存在之事，就不可能存在。", font=f_tr, fill=INK)

# ================= window: Mars sky + Phobos =================
wy = ty + tb_h + 60
wx, ww, wh = 40, 820, 360
shadow_block(wx, wy, ww, wh, (255, 255, 255), off=14, lw=4)
rect(wx, wy, ww, 44, fill=INK, lw=4)
f_wt = mono(20, True)
d.text((px(wx + 14), px(wy + 10)), "VIEW :: MARS_SKY.BMP  —  PHOBOS RISES IN THE WEST",
       font=f_wt, fill=YEL)

# sky: butterscotch band gradient
sky_top = (196, 120, 70)
sky_bot = (238, 190, 140)
sy0, sy1 = wy + 44, wy + wh
for i in range(sy1 - sy0):
    t = i / (sy1 - sy0)
    c = tuple(int(sky_top[k] + (sky_bot[k] - sky_top[k]) * t) for k in range(3))
    d.line([(px(wx + 4), px(sy0 + i)), (px(wx + ww - 4), px(sy0 + i))], fill=c)
# subtle horizontal haze bands in the lower sky
for byy, hc in [(sy0 + int((sy1 - sy0) * 0.45), (228, 168, 116)),
                (sy0 + int((sy1 - sy0) * 0.58), (233, 178, 126)),
                (sy0 + int((sy1 - sy0) * 0.70), (236, 185, 133))]:
    d.rectangle([px(wx + 4), px(byy), px(wx + ww - 4), px(byy + 12)], fill=hc)

# ground
gy_ground = sy0 + int((sy1 - sy0) * 0.82)
d.rectangle([px(wx + 4), px(gy_ground), px(wx + ww - 4), px(sy1 - 4)], fill=(120, 66, 44))
d.rectangle([px(wx + 4), px(gy_ground), px(wx + ww - 4), px(gy_ground + 6)], fill=INK)
# horizon rocks
d.polygon([(px(wx + 620), px(gy_ground)), (px(wx + 660), px(gy_ground - 18)),
           (px(wx + 700), px(gy_ground))], fill=(90, 48, 32), outline=INK)
d.polygon([(px(wx + 740), px(gy_ground)), (px(wx + 770), px(gy_ground - 12)),
           (px(wx + 800), px(gy_ground))], fill=(90, 48, 32), outline=INK)

# potato-shaped Phobos
def phobos(cx, cy, sc):
    potato = [(0, -18), (16, -14), (26, -2), (20, 12), (6, 20), (-12, 16), (-26, 4), (-20, -12)]
    d.polygon([(px(cx + a * sc), px(cy + b * sc)) for a, b in potato],
              fill=(90, 80, 74), outline=INK, width=px(3))
    d.ellipse([px(cx - 8 * sc), px(cy - 6 * sc), px(cx + 2 * sc), px(cy + 4 * sc)],
              fill=(60, 52, 48))

phx, phy = wx + 170, sy0 + 88
phobos(phx, phy, 1.5)
# dashed orbit path west -> east along the vertical middle of the sky
path_y = sy0 + int((sy1 - sy0) * 0.42)
f_arc = mono(18, True)
for sx in range(phx + 60, wx + ww - 60, 26):
    d.line([(px(sx), px(path_y)), (px(sx + 14), px(path_y))], fill=INK, width=px(3))
d.polygon([(px(wx + ww - 62), px(path_y - 10)), (px(wx + ww - 62), px(path_y + 10)),
           (px(wx + ww - 42), px(path_y))], fill=INK)
d.text((px(phx + 40), px(path_y + 24)), "WEST → OST  ·  2× PRO SOL", font=f_arc, fill=INK)
# second smaller Phobos low in the east, setting
phobos(wx + ww - 90, gy_ground - 46, 0.9)

# ================= FACT section =================
fy = wy + wh + 70
d.line([(px(40), px(fy)), (px(860), px(fy))], fill=INK, width=px(6))
d.text((px(40), px(fy + 16)), "/fakt  [de]", font=f_tag, fill=BLUE)

fact_de = ("Am Marshimmel geht ein Mond verkehrt herum: Phobos geht im Westen auf und "
           "im Osten unter – zweimal an jedem Marstag. Er umrundet den Planeten in nur "
           "7 Stunden und 39 Minuten, schneller, als der Mars sich dreht.")
f_fd = sansb(30)
lines = wrap(fact_de, f_fd, 780)
ly = fy + 64
for ln in lines:
    d.text((px(44), px(ly)), ln, font=f_fd, fill=INK)
    ly += 46

# Chinese translation of FACT, boxed, with comfortable inner padding
fact_zh = ["火星的天空里有一颗“反着来”的卫星：",
           "火卫一从西边升起、在东边落下，每个火星日上演两次——",
           "它绕火星一圈只要 7 小时 39 分钟，比火星自转还快。"]
f_fz = cjk(25)
fb_h = 132
fb_y = ly + 20
d.rectangle([px(52), px(fb_y + 10), px(852), px(fb_y + 10 + fb_h)], fill=INK)
rect(40, fb_y, 800, fb_h, fill=(255, 255, 255), lw=3)
for i, ln in enumerate(fact_zh):
    d.text((px(64), px(fb_y + 14 + i * 40)), ln, font=f_fz, fill=INK)

# ================= footer bar =================
fbar_y = H - 70
rect(0, fbar_y, W, 70, fill=INK, lw=0)
f_fb = mono(22, True)
d.text((px(20), px(fbar_y + 22)), f"EOF :: {SERIAL} :: {DATE}", font=f_fb, fill=YEL)
d.text((px(W - 300), px(fbar_y + 22)), "[SCROLL ▼]", font=f_fb, fill=(240, 240, 240))

# outer border
d.rectangle([px(4), px(4), px(W - 4), px(H - 4)], outline=INK, width=px(8))

img.save(OUT_PATH)
