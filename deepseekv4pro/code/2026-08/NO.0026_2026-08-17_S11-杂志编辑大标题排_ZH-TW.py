from atelier_canvas import Surface
from PIL import Image, ImageDraw
import numpy as np

W, H = 920, 1500
SC = 2
M = 64

BG      = (243, 238, 230)
RED     = (197, 56, 48)
INK     = (21, 21, 21)
WHITE   = (255, 255, 255)

sf = Surface(W, H, scale=SC, bg=BG)
sf.frame(M, M, W - 2 * M, H - 2 * M)

# ── 预排 ─────────────────────────────────────────────
quote_font = "cjk-tc"
quote_size = 78
quote_bold = True
quote_x = M + 38
quote_y = 238
quote_max_w = W - quote_x - M

quote_lines = sf.wrap(QUOTE, quote_font, quote_size, max_w=quote_max_w, bold=quote_bold)
quote_gap = 16

gutter = 44
col_w = (W - 2 * M - gutter) // 2
fact_x1 = M
fact_x2 = M + col_w + gutter

fact_size = 30
fact_lines = sf.wrap(FACT, "cjk-tc", fact_size, max_w=col_w, bold=False)
mid = (len(fact_lines) + 1) // 2
fact_col1 = fact_lines[:mid]
fact_col2 = fact_lines[mid:]

fact_gap = 12

# ── 背景：刊头 ───────────────────────────────────────
header = Image.new("RGBA", (W * SC, H * SC), (0, 0, 0, 0))
d = ImageDraw.Draw(header)
d.rectangle([0, 0, W * SC, 148 * SC], fill=RED + (255,))
d.rectangle([0, 148 * SC, W * SC, 156 * SC], fill=INK + (255,))
sf.composite(header, mode="normal", opacity=1.0)

# ── 金句文字 ──────────────────────────────────────────
qy = quote_y
for line in quote_lines:
    box = sf.text(
        quote_x, qy, line,
        family=quote_font, size=quote_size,
        fill=INK, anchor="lt", role="quote",
        bold=True,
    )
    qy = box.bottom + quote_gap

quote_bottom = box.bottom

# ── 根据实际金句高度定内文位置 ─────────────────────────
fact_top = quote_bottom + 60

# ── 装饰：左红条 & 内文上方双线 ────────────────────────
deco = Image.new("RGBA", (W * SC, H * SC), (0, 0, 0, 0))
d = ImageDraw.Draw(deco)

d.rectangle([
    M * SC,
    (quote_y + 6) * SC,
    (M + 12) * SC,
    (quote_bottom + 8) * SC,
], fill=RED + (255,))

rule_y1 = fact_top - 42
d.rectangle([M * SC, rule_y1 * SC, (W - M) * SC, (rule_y1 + 5) * SC], fill=INK + (255,))
rule_y2 = rule_y1 + 13
d.rectangle([M * SC, rule_y2 * SC, (W - M) * SC, (rule_y2 + 3) * SC], fill=RED + (255,))

sf.composite(deco, mode="normal", opacity=1.0)

# ── 刊头编号与日期 ─────────────────────────────────────
meta_y = 68
sf.serial(
    M, meta_y, SERIAL,
    family="cjk-tc", size=44, fill=WHITE,
    anchor="lt", role="meta", bold=True
)
sf.datestamp(
    W - M, meta_y, DATE,
    family="cjk-tc", size=22, fill=WHITE,
    anchor="rt", role="meta", bold=False
)

# ── 内文双栏 ──────────────────────────────────────────
fy1 = fact_top
for line in fact_col1:
    b = sf.text(
        fact_x1, fy1, line,
        family="cjk-tc", size=fact_size,
        fill=INK, anchor="lt", role="body",
        bold=False,
    )
    fy1 = b.bottom + fact_gap

fy2 = fact_top
for line in fact_col2:
    b = sf.text(
        fact_x2, fy2, line,
        family="cjk-tc", size=fact_size,
        fill=INK, anchor="lt", role="body",
        bold=False,
    )
    fy2 = b.bottom + fact_gap

sf.save(OUT_PATH)
