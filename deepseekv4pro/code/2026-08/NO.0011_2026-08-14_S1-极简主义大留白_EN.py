from atelier_canvas import Surface
from PIL import Image, ImageDraw

W, H = 1000, 1700
M = 110
TW = W - 2 * M

sf = Surface(W, H, scale=2, bg=(252, 251, 248))
sf.frame(M, 0, TW, H)

# ---------- Tier 2: minimal decorations ----------
lay = Image.new("RGBA", (sf.W, sf.H), (0, 0, 0, 0))
d = ImageDraw.Draw(lay)
ink = (24, 24, 24, 255)

# top hairline
d.line([(M * 2, 100 * 2), ((W - M) * 2, 100 * 2)], fill=ink, width=2)
# bottom hairline
d.line([(M * 2, (H - 90) * 2), ((W - M) * 2, (H - 90) * 2)], fill=ink, width=2)
# small architectural mark resting on the top hairline
sq = 12
d.rectangle([(M * 2, (100 - sq) * 2), ((M + sq) * 2, 100 * 2)], fill=ink)

sf.composite(lay)

# ---------- split original English / Chinese translation ----------
def split_parts(text):
    for marker in ["（", "("]:
        i = text.find(marker)
        if i != -1:
            en = text[:i].strip()
            zh = text[i:].strip()
            if zh.startswith("（"):
                zh = zh[1:]
            elif zh.startswith("("):
                zh = zh[1:]
            if zh.endswith("）"):
                zh = zh[:-1]
            elif zh.endswith(")"):
                zh = zh[:-1]
            return en, zh.strip()
    return text, ""

quote_en, quote_zh = split_parts(QUOTE)
fact_en, fact_zh = split_parts(FACT)

# ---------- Tier 1: quote block (top-down) ----------
box_qe = sf.text(
    M, 190, quote_en,
    family="serif", size=46, fill=(22, 22, 22),
    anchor="lt", role="quote", bold=False,
    max_w=TW, line_gap=0.55, allow_overlap=False,
)
box_qz = sf.text(
    M, box_qe.bottom + 18, quote_zh,
    family="cjk-sc", size=28, fill=(102, 102, 102),
    anchor="lt", role="body", bold=False,
    max_w=TW, line_gap=0.5, allow_overlap=False,
)

# ---------- Tier 1: fact block (bottom-up) ----------
box_fz = sf.text(
    M, H - 130, fact_zh,
    family="cjk-sc", size=28, fill=(102, 102, 102),
    anchor="lb", role="body", bold=False,
    max_w=TW, line_gap=0.42, allow_overlap=False,
)
box_fe = sf.text(
    M, box_fz.y - 26, fact_en,
    family="sans", size=30, fill=(52, 52, 52),
    anchor="lb", role="body", bold=False,
    max_w=TW, line_gap=0.42, allow_overlap=False,
)

# ---------- Tier 1: footer identifiers ----------
sf.serial(
    M, H - 50, SERIAL,
    family="sans", size=16, fill=(132, 132, 132),
    anchor="lb", role="meta", bold=False,
)
sf.datestamp(
    W - M, H - 50, DATE,
    family="sans", size=16, fill=(132, 132, 132),
    anchor="rb", role="meta", bold=False,
)

sf.save(OUT_PATH)
