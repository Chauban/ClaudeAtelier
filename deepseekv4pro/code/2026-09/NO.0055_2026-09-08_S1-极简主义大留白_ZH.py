from atelier_canvas import Surface
from PIL import Image, ImageDraw

w = 1000
h = 1350

sf = Surface(w, h, scale=2, bg=(250, 250, 248))
sf.frame(110, 100, 780, 1150)

# Hairlines (decorative layer, drawn before text)
hair = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(hair)
gray = (190, 190, 190, 255)
d.line([(110 * 2, 560 * 2), (890 * 2, 560 * 2)], fill=gray, width=2)
d.line([(110 * 2, 880 * 2), (890 * 2, 880 * 2)], fill=gray, width=2)
sf.composite(hair, mode="normal", opacity=1.0)

# Meta: serial and date
sf.serial(110, 100, SERIAL, family="sans", size=16, fill=(120, 120, 120), anchor="lt", role="meta")
sf.datestamp(890, 100, DATE, family="sans", size=16, fill=(120, 120, 120), anchor="rt", role="meta")

# Quote, split at the em dash
dash = QUOTE.find("——")
q1 = QUOTE[:dash + 2]
q2 = QUOTE[dash + 2:]
b1 = sf.text(110, 340, q1, family="cjk-sc", size=42, fill=(25, 25, 25), anchor="lt", role="quote")
b2 = sf.text(110, b1.bottom + 8, q2, family="cjk-sc", size=42, fill=(25, 25, 25), anchor="lt", role="quote")

# Fact, split into three readable lines
colon = FACT.find("：")
comma1 = FACT.find("，", colon + 1)
comma2 = FACT.find("，", comma1 + 1)
f1 = FACT[:colon + 1]
f2 = FACT[colon + 1:comma2 + 1]
f3 = FACT[comma2 + 1:]
c1 = sf.text(110, 975, f1, family="cjk-sc", size=28, fill=(90, 90, 90), anchor="lt", role="body")
c2 = sf.text(110, c1.bottom + 6, f2, family="cjk-sc", size=28, fill=(90, 90, 90), anchor="lt", role="body")
c3 = sf.text(110, c2.bottom + 6, f3, family="cjk-sc", size=28, fill=(90, 90, 90), anchor="lt", role="body")

sf.save(OUT_PATH)
