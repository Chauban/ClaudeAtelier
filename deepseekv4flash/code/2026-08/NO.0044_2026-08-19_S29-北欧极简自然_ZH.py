from atelier_canvas import Surface
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 1340
BG = (242, 239, 230)
DARK = (44, 51, 49)
MUTED = (77, 84, 77)
GRAY = (96, 103, 94)
SAGE = (122, 139, 122)
SAGE_D = (92, 112, 96)
TRUNK = (70, 80, 70)
SAND = (210, 177, 108)
BROWN = (139, 115, 85)
HAIR = (210, 208, 198)
HILL_L = (226, 223, 210)
HILL_R = (220, 217, 205)

sf = Surface(W, H, scale=2, bg=BG)
sf.frame(70, 55, 860, 1230)

# ---- background decorations ----

# soft sun with faint halo (upper right)
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
cx, cy, rh, rc = 795, 190, 95, 66
d.ellipse([(cx - rh) * 2, (cy - rh) * 2, (cx + rh) * 2, (cy + rh) * 2], fill=SAND + (40,))
d.ellipse([(cx - rc) * 2, (cy - rc) * 2, (cx + rc) * 2, (cy + rc) * 2], fill=SAND + (95,))
img = img.filter(ImageFilter.GaussianBlur(2.5))
sf.composite(img)

# top hairline
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.line([140, 170, 1860, 170], fill=HAIR + (255,), width=2)
sf.composite(img)

# bottom band: far hills, horizon, pine silhouettes, fallen acorns
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)

# far hills
d.ellipse([-440, 2200, 1240, 2840], fill=HILL_L + (140,))
d.ellipse([860, 2280, 2560, 2840], fill=HILL_R + (140,))

# horizon line
d.line([180, 2490, 1820, 2490], fill=SAGE + (170,), width=3)

# left pine
d.line([460, 2490, 460, 2400], fill=TRUNK + (200,), width=5)
d.polygon([(410, 2400), (510, 2400), (460, 2290)], fill=SAGE + (200,))
d.polygon([(424, 2404), (496, 2404), (460, 2312)], fill=SAGE_D + (180,))
# center pine (smaller, further)
d.line([1000, 2490, 1000, 2450], fill=TRUNK + (180,), width=3)
d.polygon([(978, 2450), (1022, 2450), (1000, 2390)], fill=SAGE + (180,))
# right pine
d.line([1400, 2490, 1400, 2420], fill=TRUNK + (200,), width=4)
d.polygon([(1364, 2420), (1436, 2420), (1400, 2330)], fill=SAGE + (200,))
d.polygon([(1374, 2424), (1426, 2424), (1400, 2348)], fill=SAGE_D + (180,))

# fallen acorns near the ground
for ax0, ay0, ax1, ay1 in [(280, 1258, 300, 1276), (330, 1254, 346, 1270),
                           (440, 1262, 458, 1278), (760, 1256, 776, 1272)]:
    d.ellipse([ax0 * 2, ay0 * 2, ax1 * 2, ay1 * 2], fill=BROWN + (220,))

# tiny grass strokes
for gx0, gy0, gx1, gy1 in [(392, 1260, 390, 1249), (398, 1260, 401, 1247),
                           (612, 1258, 610, 1248), (618, 1258, 621, 1246)]:
    d.line([gx0 * 2, gy0 * 2, gx1 * 2, gy1 * 2], fill=SAGE + (160,), width=2)

sf.composite(img)

# ---- text ----

sf.serial(70, 55, SERIAL, family="sans", size=19, fill=GRAY, anchor="lt", role="meta")
sf.datestamp(930, 55, DATE, family="sans", size=19, fill=GRAY, anchor="rt", role="meta")

_cut = QUOTE.index("，") + 1
QL1 = QUOTE[:_cut]
QL2 = QUOTE[_cut:].lstrip()

Q_SIZE = 53
q1 = sf.text(500, 385, QL1, family="cjk-sc", size=Q_SIZE, fill=DARK, anchor="mt", role="quote")
q2 = sf.text(500, q1.bottom + 28, QL2, family="cjk-sc", size=Q_SIZE, fill=DARK, anchor="mt", role="quote")

orn_y = int(q2.bottom) + 42
lay = sf.layer()
img = Image.fromarray(lay)
d = ImageDraw.Draw(img)
d.line([770, orn_y * 2, 990, orn_y * 2], fill=SAGE + (220,), width=2)
d.line([1010, orn_y * 2, 1230, orn_y * 2], fill=SAGE + (220,), width=2)
d.polygon([(1000, orn_y * 2 - 14), (1014, orn_y * 2), (1000, orn_y * 2 + 14), (986, orn_y * 2)], fill=SAGE + (220,))
sf.composite(img)

sf.text(500, orn_y + 78, FACT, family="cjk-sc", size=31, fill=MUTED, anchor="mt", role="body", max_w=720, line_gap=0.42)

sf.save(OUT_PATH)
