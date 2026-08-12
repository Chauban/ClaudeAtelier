from atelier_canvas import Surface
from PIL import Image, ImageDraw

w, h = 1000, 1900
scale = 2
sf = Surface(w, h, scale=scale, bg=(244, 241, 235))
sf.frame(70, 70, 860, 1760)

Q_SIZE = 40
F_SIZE = 30
LINE_MULT = 1.7
GAP = 6

def is_cjk_char(ch):
    o = ord(ch)
    if o < 0x2E80:
        return False
    if (0x3000 <= o <= 0x303F or 0x3040 <= o <= 0x30FF or
        0x3400 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF or
        0xFF00 <= o <= 0xFFEF):
        return True
    return False

def tokenize_mixed(text):
    toks = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if is_cjk_char(ch):
            toks.append((ch, 'cjk'))
            i += 1
        elif ch == ' ':
            toks.append((' ', 'space'))
            i += 1
        else:
            j = i
            while j < n and not is_cjk_char(text[j]) and text[j] != ' ':
                j += 1
            toks.append((text[i:j], 'latin'))
            i = j
    return toks

def token_width(tok, kind, size):
    if kind == 'space':
        return sf.measure(' ', 'sans', size)[0]
    if kind == 'latin':
        return sf.measure(tok, 'sans', size)[0]
    return sf.measure(tok, 'cjk-hk', size)[0]

def wrap_mixed(text, max_w, size):
    toks = tokenize_mixed(text)
    lines = []
    line = []
    line_w = 0.0
    for tok, kind in toks:
        tw = token_width(tok, kind, size)
        if kind == 'space':
            if line:
                line.append((tok, kind))
                line_w += tw + GAP
            continue
        if line and line_w + tw + GAP > max_w:
            while line and line[-1][1] == 'space':
                line.pop()
                line_w -= token_width(' ', 'space', size) + GAP
            if line:
                lines.append(line)
            else:
                lines.append([(tok, kind)])
            line = []
            line_w = 0.0
        line.append((tok, kind))
        line_w += tw + GAP
    if line:
        lines.append(line)
    return lines

def fragments_from_tokens(toks):
    frags = []
    cur_kind = None
    cur = []
    for tok, kind in toks:
        if kind == 'space':
            if cur_kind == 'latin':
                cur.append(' ')
            elif cur_kind == 'cjk':
                frags.append((''.join(cur), 'cjk'))
                cur = [' ']
                cur_kind = 'latin'
            else:
                cur_kind = 'latin'
                cur = [' ']
            continue
        if kind == 'latin':
            if cur_kind == 'latin':
                cur.append(tok)
            elif cur_kind == 'cjk':
                frags.append((''.join(cur), 'cjk'))
                cur = [tok]
                cur_kind = 'latin'
            else:
                cur_kind = 'latin'
                cur = [tok]
        else:
            if cur_kind == 'cjk':
                cur.append(tok)
            elif cur_kind == 'latin':
                frags.append((''.join(cur), 'latin'))
                cur = [tok]
                cur_kind = 'cjk'
            else:
                cur_kind = 'cjk'
                cur = [tok]
    if cur:
        frags.append((''.join(cur), cur_kind))
    return frags

def draw_paragraph(x, y, text, max_w, size, fill, role):
    lines = wrap_mixed(text, max_w, size)
    step = int(size * LINE_MULT)
    yy = y
    for line in lines:
        xx = x
        for frag, kind in fragments_from_tokens(line):
            fam = 'sans' if kind == 'latin' else 'cjk-hk'
            sf.text(xx, yy, frag, family=fam, size=size, fill=fill, anchor="lt", role=role)
            xx += sf.measure(frag, fam, size)[0] + GAP
        yy += step

q_lines = wrap_mixed(QUOTE, 600, Q_SIZE)
q_step = int(Q_SIZE * LINE_MULT)
q_block_h = len(q_lines) * q_step

f_lines = wrap_mixed(FACT, 680, F_SIZE)
f_step = int(F_SIZE * LINE_MULT)
f_block_h = len(f_lines) * f_step

q_y = 560
line2_y = q_y + q_block_h + 110
f_y = q_y + q_block_h + 200
f_bottom = f_y + f_block_h + 40

base_pts = [(250, 1240), (480, 1220), (600, 1330), (330, 1390), (410, 1300)]
top_min = min(y for _, y in base_pts)
shift = max(0, f_bottom + 100 - top_min)
pts = [(x, y + shift) for x, y in base_pts]

# ---------- 背景与包豪斯装饰 ----------
lay = sf.layer()
img = Image.fromarray(lay, "RGBA")
d = ImageDraw.Draw(img)

def R(x0, y0, x1, y1):
    return (x0 * scale, y0 * scale, x1 * scale, y1 * scale)

def RP(pl):
    return [(x * scale, y * scale) for x, y in pl]

BLACK = (25, 25, 25, 255)
RED = (214, 40, 40, 255)
YELLOW = (244, 197, 20, 255)
BLUE = (0, 51, 153, 255)
CREAM = (244, 241, 235, 255)

d.ellipse(R(-200, -80, 420, 500), fill=YELLOW, outline=BLACK, width=14 * scale)
d.rectangle(R(730, 0, 1000, 190), fill=RED)
d.ellipse(R(880, 22, 932, 74), fill=YELLOW)
d.rectangle(R(730, 190, 830, 290), fill=BLUE)
d.ellipse(R(748, 215, 800, 267), fill=CREAM)
d.ellipse(R(780, 320, 990, 530), outline=BLACK, width=12 * scale)
d.ellipse(R(848, 388, 920, 460), fill=RED)
d.rectangle(R(0, 470, 1000, 494), fill=BLACK)

d.rectangle(R(70, q_y - 24, 760, q_y + q_block_h + 24), fill=BLACK)
d.rectangle(R(70, q_y - 24, 90, q_y + q_block_h + 24), fill=BLUE)
d.rectangle(R(880, q_y + 60, 940, q_y + 110), fill=YELLOW)

d.rectangle(R(0, line2_y, 1000, line2_y + 10), fill=BLACK)
d.polygon(RP([(500, line2_y - 38), (562, line2_y + 10), (438, line2_y + 10)]), fill=RED)

d.rectangle(R(70, f_y - 14, 92, f_bottom), fill=RED)
d.rectangle(R(70, f_bottom, 815, f_bottom + 6), fill=BLUE)

for i in range(4):
    x0, y0 = pts[i]
    x1, y1 = pts[(i + 1) % 4]
    d.line(RP([(x0, y0), (x1, y1)]), fill=BLACK, width=5 * scale)
for p in pts[:4]:
    d.ellipse(R(p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8), fill=BLACK)
d.ellipse(R(pts[4][0] - 8, pts[4][1] - 8, pts[4][0] + 8, pts[4][1] + 8), fill=RED)

d.rectangle(R(750, 1750, 1000, 1900), fill=BLACK)
d.polygon(RP([(750, 1750), (1000, 1750), (750, 1860)]), fill=RED)
d.rectangle(R(0, 1860, 750, 1900), fill=YELLOW)

sf.composite(img)

# ---------- 文字 ----------
sf.serial(76, 130, SERIAL, family="sans", size=30, fill=(25, 25, 25), bold=True, anchor="lt")
sf.datestamp(745, 82, DATE, family="sans", size=24, fill=(255, 255, 255), bold=True, anchor="lt")

draw_paragraph(135, q_y, QUOTE, 600, Q_SIZE, (245, 245, 245), "quote")
draw_paragraph(135, f_y, FACT, 680, F_SIZE, (35, 35, 35), "body")

sf.save(OUT_PATH)
