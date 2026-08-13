from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

S = 2
W = 1000
H = 1820
WS, HS = W*S, H*S

def grad_round(w, h, r, c_tl, c_br):
    w, h, r = int(w), int(h), int(r)
    x = np.linspace(0, 1, w)[None, :]
    y = np.linspace(0, 1, h)[:, None]
    t = (x + y) / 2.0
    arr = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        arr[:, :, i] = c_tl[i] * (1 - t) + c_br[i] * t
    hl = np.clip(1 - np.sqrt((x*1.6)**2 + (y*1.6)**2), 0, 1) ** 2
    for i in range(3):
        arr[:, :, i] += hl * 26
    sh = np.clip(np.sqrt(((x-1)*1.8)**2 + ((y-1)*1.8)**2), 0, 1) ** 2
    for i in range(3):
        arr[:, :, i] -= sh * 22
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, 'RGB')
    mask = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, w-1, h-1], radius=r, fill=255)
    return img, mask

# background
yy = np.linspace(0, 1, HS)[:, None]
bg = np.zeros((HS, WS, 3), np.float32)
c0 = np.array([253, 246, 238]); c1 = np.array([244, 228, 224])
for i in range(3):
    bg[:, :, i] = c0[i]*(1-yy) + c1[i]*yy
base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')

# main clay panel
pw, ph, pr = 920*S, 1660*S, 90*S
px, py = (WS-pw)//2, 80*S
panel, pmask = grad_round(pw, ph, pr, (255, 250, 243), (243, 222, 216))
psh = Image.new('RGBA', (pw+200, ph+200), (0,0,0,0))
ImageDraw.Draw(psh).rounded_rectangle([100, 130, 100+pw, 130+ph], radius=pr, fill=(150, 110, 120, 85))
psh = psh.filter(ImageFilter.GaussianBlur(45))
base.alpha_composite(psh, (px-100, py-100))
base.paste(panel, (px, py), pmask)

d = ImageDraw.Draw(base)

def blob(box, c_tl, c_br):
    x0, y0, x1, y1 = box
    w, h = x1-x0, y1-y0
    x = np.linspace(-1, 1, int(w))[None, :]
    y = np.linspace(-1, 1, int(h))[:, None]
    t = (x*0.5+0.5 + y*0.5+0.5)/2
    arr = np.zeros((int(h), int(w), 3), np.float32)
    for i in range(3):
        arr[:, :, i] = c_tl[i]*(1-t) + c_br[i]*t
    glow = np.clip(1-(((x+0.45)/0.35)**2 + ((y+0.45)/0.35)**2), 0, 1)**2 * 60
    edge = np.clip(np.sqrt(x**2+y**2), 0, 1)**3 * -30
    for i in range(3):
        arr[:, :, i] += glow + edge
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    bimg = Image.fromarray(arr, 'RGB')
    m = Image.new('L', (int(w), int(h)), 0)
    ImageDraw.Draw(m).ellipse([0, 0, w-1, h-1], fill=255)
    sh = Image.new('RGBA', (int(w)+120, int(h)+120), (0,0,0,0))
    ImageDraw.Draw(sh).ellipse([60, 78, w+60, h+78], fill=(120, 90, 110, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    base.alpha_composite(sh, (int(x0)-60, int(y0)-60))
    base.paste(bimg, (int(x0), int(y0)), m)

# decorative blobs, kept clear of all text zones
blob((40*S, 240*S, 170*S, 370*S), (255, 210, 190), (240, 160, 150))
blob((830*S, 260*S, 965*S, 395*S), (190, 225, 255), (140, 175, 235))
blob((45*S, 700*S, 160*S, 815*S), (210, 240, 205), (160, 205, 160))
blob((840*S, 760*S, 960*S, 880*S), (255, 235, 170), (240, 195, 120))
for (cx_, cy_, rr, col) in [(110, 1180, 22, (255,190,200)), (900, 1150, 20, (180,215,250)),
                            (70, 1620, 24, (200,230,190)), (920, 1620, 22, (255,180,190))]:
    blob(((cx_-rr)*S, (cy_-rr)*S, (cx_+rr)*S, (cy_+rr)*S), col, tuple(max(0, v-45) for v in col))

FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FR = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
qfont = ImageFont.truetype(FB, 46*S, index=0)
ffont = ImageFont.truetype(FR, 30*S, index=0)
sfont = ImageFont.truetype(FB, 30*S, index=0)

INK = (110, 85, 95, 255)
cx = WS // 2

def wrap(text, font, maxw):
    lines, cur = [], ''
    for ch in text:
        if ch == '\n':
            lines.append(cur); cur = ''; continue
        if d.textlength(cur + ch, font=font) > maxw and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines

def text_shadow(txt, xy, font, fill, blur=8, off=(0, 5*S), sh=(190, 140, 150, 110)):
    layer = Image.new('RGBA', base.size, (0,0,0,0))
    ImageDraw.Draw(layer).text((xy[0]+off[0], xy[1]+off[1]), txt, font=font, fill=sh)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    d.text(xy, txt, font=font, fill=fill)

# --- top: serial + date on a clay tag ---
tag = SERIAL + '  ' + DATE
tw = d.textlength(tag, font=sfont)
tagw, tagh = int(tw + 100*S), 76*S
tp, tmask = grad_round(tagw, tagh, tagh//2, (255, 205, 185), (238, 155, 145))
tsh = Image.new('RGBA', (tagw+100, tagh+100), (0,0,0,0))
ImageDraw.Draw(tsh).rounded_rectangle([50, 64, 50+tagw, 64+tagh], radius=tagh//2, fill=(140, 100, 110, 90))
tsh = tsh.filter(ImageFilter.GaussianBlur(18))
tx = int(cx - tagw/2)
base.alpha_composite(tsh, (tx-50, 145*S-50))
base.paste(tp, (tx, 145*S), tmask)
d.text((tx + 50*S, 145*S + 15*S), tag, font=sfont, fill=(255, 255, 255, 255))

# --- fortune-cookie clay shape ---
cookie = Image.new('RGBA', (420*S, 300*S), (0,0,0,0))
cd = ImageDraw.Draw(cookie)
cd.ellipse([40*S, 60*S, 300*S, 260*S], fill=(250, 205, 150, 255))
cd.ellipse([150*S, 60*S, 400*S, 260*S], fill=(245, 185, 125, 255))
hi = Image.new('RGBA', cookie.size, (0,0,0,0))
ImageDraw.Draw(hi).ellipse([110*S, 85*S, 220*S, 145*S], fill=(255, 245, 225, 170))
hi = hi.filter(ImageFilter.GaussianBlur(18))
cookie.alpha_composite(hi)
csh = Image.new('RGBA', (cookie.width+160, cookie.height+160), (0,0,0,0))
ImageDraw.Draw(csh).ellipse([80+40*S, 110+60*S, 80+300*S, 110+260*S], fill=(150, 100, 90, 90))
ImageDraw.Draw(csh).ellipse([80+150*S, 110+60*S, 80+400*S, 110+260*S], fill=(150, 100, 90, 90))
csh = csh.filter(ImageFilter.GaussianBlur(30))
base.alpha_composite(csh, (290*S-80, 250*S-80))
base.alpha_composite(cookie, (290*S, 250*S))

# --- quote ---
yl = 600*S
qlines = wrap(QUOTE, qfont, 720*S)
for ln in qlines:
    wln = d.textlength(ln, font=qfont)
    text_shadow(ln, (int(cx - wln/2), yl), qfont, INK)
    yl += 80*S

# divider clay pill
pillw = 220*S
pwimg, pwmask = grad_round(pillw, 26*S, 13*S, (190, 220, 250), (145, 175, 225))
base.paste(pwimg, (int(cx-pillw/2), int(yl+14*S)), pwmask)
yl += 90*S

# --- fact inner clay card ---
fw = 800*S
flines = wrap(FACT, ffont, fw - 100*S)
fh = len(flines)*56*S + 90*S
fp, fmask = grad_round(fw, fh, 60*S, (246, 228, 220), (236, 210, 204))
fsh = Image.new('RGBA', (fw+120, fh+120), (0,0,0,0))
ImageDraw.Draw(fsh).rounded_rectangle([60, 70, 60+fw, 70+fh], radius=60*S, fill=(160, 120, 125, 70))
fsh = fsh.filter(ImageFilter.GaussianBlur(24))
fx = int(cx - fw/2)
base.alpha_composite(fsh, (fx-60, yl-60))
base.paste(fp, (fx, yl), fmask)
yl += 45*S
for ln in flines:
    d.text((fx + 50*S, yl), ln, font=ffont, fill=(120, 92, 100, 255))
    yl += 56*S

img = base.convert('RGB').resize((W, H), Image.LANCZOS)
img.save(OUT_PATH)
