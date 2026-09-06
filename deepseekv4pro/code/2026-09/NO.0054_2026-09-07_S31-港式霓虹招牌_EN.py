from atelier_canvas import Surface
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# ─── 颜色 ───
BG_BASE       = (8, 8, 22)
NEON_PINK     = (255, 92, 138)
NEON_PINK_DIM = (255, 60, 120, 90)
NEON_CYAN     = (0, 229, 222)
NEON_CYAN_DIM = (0, 200, 210, 80)
NEON_YELLOW   = (255, 230, 110)
NEON_BLUE     = (0, 180, 255)
NEON_BLUE_CORE= (210, 245, 255)

# ─── 画布与安全区 ───
W, H = 1000, 1300
sf = Surface(W, H, scale=2, bg=BG_BASE)
sf.frame(60, 60, 880, 1180)       # x 60~940, y 60~1240

# 先测量文字，确定各块位置
quote_family = "cjk-sc"
quote_size   = 52
quote_max_w  = 760
quote_bold   = True
quote_lines  = sf.wrap(QUOTE, quote_family, quote_size, quote_max_w, bold=quote_bold)
quote_line_h = sf.measure("Ag", quote_family, quote_size, bold=quote_bold)[1] * 1.35
quote_h_est  = len(quote_lines) * quote_line_h

fact_family  = "cjk-sc"
fact_size    = 33
fact_max_w   = 800
fact_bold    = False
fact_lines   = sf.wrap(FACT, fact_family, fact_size, fact_max_w, bold=fact_bold)
fact_line_h  = sf.measure("Ag", fact_family, fact_size, bold=fact_bold)[1] * 1.35
fact_h_est   = len(fact_lines) * fact_line_h

# 关键 y 坐标
serial_y = 78
date_y   = 78
quote_y  = 220
# 根据上一轮实际渲染，quote box bottom 约为 601，这里固定留出足够间隙
fact_y   = 680

# 文字背板范围（宽大覆盖，避免漏出装饰）
qpx1, qpy1 = 70, 190
qpx2, qpy2 = 930, 620

fpx1, fpy1 = 55, 648
fpx2, fpy2 = 945, 1120

# 光晕中心
quote_center_y = quote_y + quote_h_est / 2
fact_center_y  = fact_y + fact_h_est / 2

# ─── 自由层：背景径向渐变 ───
lay_bg = sf.layer()
hh, ww = lay_bg.shape[:2]
yy = np.linspace(0, 1, hh)[:, None]
xx = np.linspace(0, 1, ww)[None, :]
dist = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2)
glow = np.exp(-dist ** 2 / 0.22) * 26
lay_bg[..., 0] = (8   + glow).astype(np.uint8)
lay_bg[..., 1] = (8   + glow * 0.75).astype(np.uint8)
lay_bg[..., 2] = (22  + glow * 0.55).astype(np.uint8)
lay_bg[..., 3] = 255
sf.composite(lay_bg, mode="normal", opacity=1.0)

# ─── 自由层：氛围光斑（霓虹光晕） ───
lay_glow = sf.layer()
glow_img = Image.fromarray(lay_glow, 'RGBA')
gd = ImageDraw.Draw(glow_img)

qx1 = int((500 - 360) * 2); qy1 = int((quote_center_y - 190) * 2)
qx2 = int((500 + 360) * 2); qy2 = int((quote_center_y + 190) * 2)
gd.ellipse([qx1, qy1, qx2, qy2], fill=NEON_PINK_DIM)

fx1 = int((500 - 330) * 2); fy1 = int((fact_center_y - 160) * 2)
fx2 = int((500 + 330) * 2); fy2 = int((fact_center_y + 160) * 2)
gd.ellipse([fx1, fy1, fx2, fy2], fill=NEON_CYAN_DIM)

glow_img = glow_img.filter(ImageFilter.GaussianBlur(60))
sf.composite(glow_img, mode="screen", opacity=0.55)

# ─── 自由层：文字背板（干净暗板，遮住装饰） ───
lay_panels = sf.layer()
panel_img = Image.fromarray(lay_panels, 'RGBA')
pd = ImageDraw.Draw(panel_img)
pd.rounded_rectangle([qpx1 * 2, qpy1 * 2, qpx2 * 2, qpy2 * 2], radius=16 * 2, fill=(8, 8, 22, 255))
pd.rounded_rectangle([fpx1 * 2, fpy1 * 2, fpx2 * 2, fpy2 * 2], radius=16 * 2, fill=(8, 8, 22, 255))
sf.composite(panel_img, mode="normal", opacity=1.0)

# ─── 自由层：文字背板霓虹描边 ───
lay_panel_glow = sf.layer()
po_img = Image.fromarray(lay_panel_glow, 'RGBA')
pod = ImageDraw.Draw(po_img)
pod.rounded_rectangle([qpx1 * 2, qpy1 * 2, qpx2 * 2, qpy2 * 2], radius=16 * 2, outline=(255, 92, 138, 180), width=5)
pod.rounded_rectangle([fpx1 * 2, fpy1 * 2, fpx2 * 2, fpy2 * 2], radius=16 * 2, outline=(0, 229, 222, 180), width=5)
po_img = po_img.filter(ImageFilter.GaussianBlur(5))
sf.composite(po_img, mode="screen", opacity=0.65)

# ─── 自由层：边框光晕（霓虹蓝） ───
lay_border_glow = sf.layer()
bg_glow_img = Image.fromarray(lay_border_glow, 'RGBA')
bd_glow = ImageDraw.Draw(bg_glow_img)
ox1, oy1, ox2, oy2 = 30 * 2, 30 * 2, 970 * 2, 1270 * 2
bd_glow.rounded_rectangle([ox1, oy1, ox2, oy2], radius=30 * 2, outline=(0, 180, 255, 220), width=10)
ix1, iy1, ix2, iy2 = 48 * 2, 48 * 2, 952 * 2, 1252 * 2
bd_glow.rounded_rectangle([ix1, iy1, ix2, iy2], radius=20 * 2, outline=(0, 180, 255, 220), width=10)
bg_glow_img = bg_glow_img.filter(ImageFilter.GaussianBlur(28))
sf.composite(bg_glow_img, mode="screen", opacity=0.65)

# ─── 自由层：边框亮线（灯管内芯） ───
lay_border_core = sf.layer()
core_img = Image.fromarray(lay_border_core, 'RGBA')
cd = ImageDraw.Draw(core_img)
cd.rounded_rectangle([ox1, oy1, ox2, oy2], radius=30 * 2, outline=NEON_BLUE_CORE, width=5)
cd.rounded_rectangle([ix1, iy1, ix2, iy2], radius=20 * 2, outline=(200, 240, 255, 255), width=5)
core_img = core_img.filter(ImageFilter.GaussianBlur(3))
sf.composite(core_img, mode="normal", opacity=0.85)

# ─── 自由层：边框上的灯点 ───
lay_dots = sf.layer()
dots_img = Image.fromarray(lay_dots, 'RGBA')
dd = ImageDraw.Draw(dots_img)
for lx in range(60, 941, 55):
    dd.ellipse([lx * 2 - 4, 48 * 2 - 4, lx * 2 + 4, 48 * 2 + 4], fill=NEON_YELLOW)
    dd.ellipse([lx * 2 - 4, 1252 * 2 - 4, lx * 2 + 4, 1252 * 2 + 4], fill=NEON_YELLOW)
for ly in range(60, 1252, 55):
    dd.ellipse([48 * 2 - 4, ly * 2 - 4, 48 * 2 + 4, ly * 2 + 4], fill=NEON_YELLOW)
    dd.ellipse([952 * 2 - 4, ly * 2 - 4, 952 * 2 + 4, ly * 2 + 4], fill=NEON_YELLOW)
dots_img = dots_img.filter(ImageFilter.GaussianBlur(2.5))
sf.composite(dots_img, mode="screen", opacity=0.9)

# ─── 自由层：角落装饰圆环 ───
lay_corners = sf.layer()
corner_img = Image.fromarray(lay_corners, 'RGBA')
cr = ImageDraw.Draw(corner_img)
cr.ellipse([38 * 2, 38 * 2, 58 * 2, 58 * 2], outline=NEON_BLUE, width=5)
cr.ellipse([942 * 2, 38 * 2, 962 * 2, 58 * 2], outline=NEON_PINK, width=5)
cr.ellipse([38 * 2, 1242 * 2, 58 * 2, 1262 * 2], outline=NEON_YELLOW, width=5)
cr.ellipse([942 * 2, 1242 * 2, 962 * 2, 1262 * 2], outline=NEON_CYAN, width=5)
corner_img = corner_img.filter(ImageFilter.GaussianBlur(1.5))
sf.composite(corner_img, mode="screen", opacity=0.8)

# ─── 自由层：底部装饰霓虹环（填充留白） ───
lay_bottom = sf.layer()
bottom_img = Image.fromarray(lay_bottom, 'RGBA')
bd2 = ImageDraw.Draw(bottom_img)
ring_y1 = 1120 * 2
ring_y2 = 1140 * 2
ring_colors = [NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_BLUE, NEON_PINK]
for i, cx in enumerate([160, 330, 500, 670, 840]):
    rxl = cx * 2 - 18
    ryl1 = ring_y1
    rxl2 = cx * 2 + 18
    ryl2 = ring_y2
    bd2.ellipse([rxl, ryl1, rxl2, ryl2], outline=ring_colors[i], width=4)
    bd2.ellipse([rxl + 6, ryl1 + 6, rxl2 - 6, ryl2 - 6], outline=ring_colors[i], width=2)
bottom_img = bottom_img.filter(ImageFilter.GaussianBlur(3))
sf.composite(bottom_img, mode="screen", opacity=0.75)

# ─── 受控层文字 ───
# SERIAL（顶部左角，霓虹黄）
sf.serial(60, serial_y, SERIAL,
          family="sans", size=20, fill=NEON_YELLOW,
          anchor="lt", role="meta", bold=True)

# DATE（顶部右角，霓虹黄）
sf.datestamp(940, date_y, DATE,
             family="sans", size=20, fill=NEON_YELLOW,
             anchor="rt", role="meta", bold=True)

# QUOTE（主标语，居中，霓虹粉；整体使用 cjk-sc 字体）
quote_box = sf.text(500, quote_y, QUOTE,
                    family=quote_family, size=quote_size,
                    fill=NEON_PINK, anchor="mt", role="quote",
                    bold=quote_bold, max_w=quote_max_w,
                    line_gap=0.35, allow_overlap=False)

# FACT（冷知识，左对齐，霓虹青；整体使用 cjk-sc 字体）
fact_box = sf.text(60, fact_y, FACT,
                   family=fact_family, size=fact_size,
                   fill=NEON_CYAN, anchor="lt", role="body",
                   bold=fact_bold, max_w=fact_max_w,
                   line_gap=0.35, allow_overlap=False)

# ─── 保存 ───
sf.save(OUT_PATH)
