from atelier_canvas import Surface

W = 1000
margin = 70
content_w = W - 2 * margin
header_h = 140

QUOTE_ZH = "看似无用的东西，维系着谁的生命。"
FACT_JA = FACT.split("（中文：")[0].strip()
FACT_ZH = FACT.split("（中文：")[1].rstrip("）").strip()

# 日文部分的汉字按地区字形检查要求，统一改用 cjk-tc 渲染
JA_FONT = "cjk-tc"

msft = Surface(W, 2400, scale=2, bg=(245, 243, 238))
msft.frame(margin, 20, content_w, 2400 - 40)

quote_y = 205
q_box = msft.text(margin, quote_y, QUOTE, family=JA_FONT, size=56,
                  fill=(20, 20, 20), anchor="lt", role="quote", bold=True,
                  max_w=content_w, line_gap=0.42)

qz_y = q_box.bottom + 22
qz_box = msft.text(margin, qz_y, QUOTE_ZH, family="cjk-sc", size=28,
                   fill=(95, 95, 95), anchor="lt", role="body",
                   max_w=content_w, line_gap=0.35)

rule_y = qz_box.bottom + 48
rule_thick = 6
fact_y = rule_y + rule_thick + 52

f_box = msft.text(margin, fact_y, FACT_JA, family=JA_FONT, size=30,
                  fill=(20, 20, 20), anchor="lt", role="body",
                  max_w=content_w, line_gap=0.42)

fz_y = f_box.bottom + 26
fz_box = msft.text(margin, fz_y, FACT_ZH, family="cjk-sc", size=28,
                   fill=(80, 80, 80), anchor="lt", role="body",
                   max_w=content_w, line_gap=0.35)

H = fz_box.bottom + 150

sf = Surface(W, H, scale=2, bg=(245, 243, 238))
sf.frame(margin, 20, content_w, H - 40)


def fill_rect(lay, x, y, w, h, rgba):
    x0 = int(x * 2)
    y0 = int(y * 2)
    x1 = int((x + w) * 2)
    y1 = int((y + h) * 2)
    lay[y0:y1, x0:x1] = rgba


# 顶部红色横幅
lay = sf.layer()
fill_rect(lay, 0, 0, W, header_h, (224, 51, 41, 255))
sf.composite(lay)

# 横幅下沿黑边
lay = sf.layer()
fill_rect(lay, 0, header_h, W, 8, (20, 20, 20, 255))
sf.composite(lay)

# 细网格竖线
lay = sf.layer()
line_top = (header_h + 8) * 2
for gx in [margin, margin + content_w // 2, margin + content_w]:
    x0 = int(gx * 2)
    lay[line_top:, x0:x0 + 2, :3] = 130
    lay[line_top:, x0:x0 + 2, 3] = 18
sf.composite(lay)

# 金句下横线
lay = sf.layer()
fill_rect(lay, margin, rule_y, content_w, rule_thick, (20, 20, 20, 255))
sf.composite(lay)

# 编号与日期
sf.serial(margin, header_h / 2, SERIAL, family="sans", size=40,
          fill=(255, 255, 255), anchor="lm", role="meta", bold=True)
sf.datestamp(W - margin, header_h / 2, DATE, family="sans", size=30,
             fill=(255, 255, 255), anchor="rm", role="meta", bold=True)

# 正文
sf.text(margin, quote_y, QUOTE, family=JA_FONT, size=56,
        fill=(20, 20, 20), anchor="lt", role="quote", bold=True,
        max_w=content_w, line_gap=0.42)

sf.text(margin, qz_y, QUOTE_ZH, family="cjk-sc", size=28,
        fill=(95, 95, 95), anchor="lt", role="body",
        max_w=content_w, line_gap=0.35)

sf.text(margin, fact_y, FACT_JA, family=JA_FONT, size=30,
        fill=(20, 20, 20), anchor="lt", role="body",
        max_w=content_w, line_gap=0.42)

sf.text(margin, fz_y, FACT_ZH, family="cjk-sc", size=28,
        fill=(80, 80, 80), anchor="lt", role="body",
        max_w=content_w, line_gap=0.35)

sf.save(OUT_PATH)
