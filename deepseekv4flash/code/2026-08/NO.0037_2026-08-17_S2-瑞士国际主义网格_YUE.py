from atelier_canvas import Surface
from PIL import Image, ImageDraw

W, H = 1000, 1600
sf = Surface(W, H, scale=2, bg=(255, 255, 255))
sf.frame(60, 60, W - 120, H - 120)

RED = (227, 6, 19)
INK = (0, 0, 0)


def rect(x, y, w, h, color):
    lay = sf.layer()
    img = Image.fromarray(lay)
    ImageDraw.Draw(img).rectangle(
        [x * 2, y * 2, (x + w) * 2, (y + h) * 2], fill=color + (255,)
    )
    sf.composite(img)


def disc(cx, cy, r, color):
    lay = sf.layer()
    img = Image.fromarray(lay)
    ImageDraw.Draw(img).ellipse(
        [(cx - r) * 2, (cy - r) * 2, (cx + r) * 2, (cy + r) * 2], fill=color + (255,)
    )
    sf.composite(img)


# Tier 2 — grid rules and the single red geometric form
rect(80, 84, 840, 2, INK)          # top hairline of the grid
disc(940, 1140, 170, RED)          # red disc bleeding off the right edge
rect(80, 1460, 840, 3, INK)        # footer rule
rect(80, 1482, 16, 16, RED)        # red registration mark before the serial

# Tier 1 — typography on the grid
q = sf.text(80, 120, QUOTE, family="cjk-hk", size=64, bold=True,
            fill=INK, anchor="lt", max_w=840, line_gap=0.35, role="quote")

rule_y = int(q.bottom) + 48
rect(80, rule_y, 840, 5, INK)      # thick rule closing the title block

fact_y = rule_y + 74
_i = FACT.index("但係如果")
sf.text(80, fact_y, FACT[:_i], family="cjk-hk", size=30, fill=INK,
        anchor="lt", max_w=470, line_gap=0.5, role="body")
sf.text(610, fact_y, FACT[_i:], family="cjk-hk", size=30, fill=INK,
        anchor="lt", max_w=310, line_gap=0.5, role="body")

sf.serial(108, 1482, SERIAL, family="sans", size=22, fill=INK,
          anchor="lt", role="meta")
sf.datestamp(920, 1482, DATE, family="sans", size=22, fill=INK,
             anchor="rt", role="meta")

sf.save(OUT_PATH)
