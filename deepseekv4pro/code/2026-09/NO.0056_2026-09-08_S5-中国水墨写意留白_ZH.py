from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

w, h = 1000, 1650
bg = (242, 237, 225)
sf = Surface(w, h, scale=2, bg=bg)

def up(img):
    return img.resize((sf.W, sf.H), Image.LANCZOS)

def qbez(p0, p1, p2, n=64):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts

def tapered(dr, pts, w_start, w_end, col, steps=50):
    n = len(pts)
    for i in range(n - 1):
        p0, p1 = pts[i], pts[i + 1]
        f0 = i / (n - 1)
        f1 = (i + 1) / (n - 1)
        w0 = w_start + (w_end - w_start) * f0
        w1 = w_start + (w_end - w_start) * f1
        for q in range(steps + 1):
            t = q / steps
            x = p0[0] + (p1[0] - p0[0]) * t
            y = p0[1] + (p1[1] - p0[1]) * t
            r = w0 + (w1 - w0) * t
            dr.ellipse([int(x - r), int(y - r), int(x + r), int(y + r)], fill=col)

# -------- ink washes --------
wash = Image.new("RGBA", (w, h), (0, 0, 0, 0))
dw = ImageDraw.Draw(wash)
dw.ellipse([670, 62, 955, 330], fill=(226, 220, 209, 105))
dw.ellipse([30, 1180, 970, 1345], fill=(210, 203, 192, 100))
dw.ellipse([130, 1280, 870, 1435], fill=(192, 184, 173, 90))
dw.ellipse([-60, 1120, 260, 1300], fill=(205, 198, 187, 75))
dw.ellipse([150, 440, 850, 575], fill=(238, 234, 226, 100))
wash = wash.filter(ImageFilter.GaussianBlur(58))
sf.composite(up(wash), mode="multiply", opacity=0.85)

# -------- swift (shifted down to leave upper area for text) --------
bird = Image.new("RGBA", (w, h), (0, 0, 0, 0))
db = ImageDraw.Draw(bird)
ink = (25, 22, 20, 255)
gray = (116, 108, 98, 110)
shift = 580

tapered(db, qbez((260, 262 + shift), (210, 238 + shift), (150, 196 + shift)), 14, 2, gray, steps=40)
tapered(db, qbez((740, 262 + shift), (790, 238 + shift), (850, 196 + shift)), 14, 2, gray, steps=40)

tapered(db, qbez((500, 356 + shift), (365, 300 + shift), (238, 248 + shift), n=70), 26, 3, ink, steps=56)
tapered(db, qbez((500, 356 + shift), (635, 300 + shift), (762, 248 + shift), n=70), 26, 3, ink, steps=56)

tapered(db, [(500, 336 + shift), (500, 432 + shift)], 15, 9, ink, steps=30)
db.ellipse([486, 302 + shift, 514, 332 + shift], fill=ink)
tapered(db, [(502, 306 + shift), (513, 289 + shift)], 4, 1, ink, steps=12)
tapered(db, [(500, 430 + shift), (481, 496 + shift)], 8, 2, ink, steps=22)
tapered(db, [(500, 430 + shift), (519, 496 + shift)], 8, 2, ink, steps=22)

bird = bird.filter(ImageFilter.GaussianBlur(1.5))
sf.composite(up(bird), mode="normal", opacity=1.0)

# -------- red accents --------
acc = Image.new("RGBA", (w, h), (0, 0, 0, 0))
da = ImageDraw.Draw(acc)
red = (176, 54, 46, 255)
paper = (242, 237, 225, 255)

da.ellipse([178, 120, 240, 182], fill=(176, 54, 46, 205))

sx, sy, ss = 150, 1300, 88
da.rounded_rectangle([sx, sy, sx + ss, sy + ss], radius=10, fill=red)
da.rounded_rectangle([sx + 7, sy + 7, sx + ss - 7, sy + ss - 7], radius=7, outline=paper, width=2)
da.line([sx + 20, sy + ss - 24, sx + ss - 20, sy + 24], fill=paper, width=3)
da.line([sx + 20, sy + 42, sx + ss - 20, sy + 42], fill=paper, width=2)

acc = acc.filter(ImageFilter.GaussianBlur(0.5))
sf.composite(up(acc), mode="normal", opacity=0.97)

# -------- text --------
sf.frame(90, 70, 820, 1470)

ink_q = (28, 24, 22)
ink_f = (66, 60, 53)
ink_m = (92, 84, 76)

q1 = sf.text(500, 190, "飞行是它的日常，", family="serif-cjk", size=64,
             fill=ink_q, anchor="mt", role="quote", bold=True)
q2 = sf.text(500, q1.bottom + 26, "落地才是例外。", family="serif-cjk", size=64,
             fill=ink_q, anchor="mt", role="quote", bold=True)

sf.text(500, q2.bottom + 82, FACT, family="serif-cjk", size=29,
        fill=ink_f, anchor="mt", role="body", max_w=700, line_gap=0.52)

sf.serial(268, 1344, SERIAL, family="serif-cjk", size=23, fill=ink_m,
          anchor="lm", role="meta")
sf.datestamp(882, 1344, DATE, family="serif-cjk", size=23, fill=ink_m,
             anchor="rm", role="meta")

sf.save(OUT_PATH)
