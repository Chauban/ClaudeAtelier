import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from atelier_canvas import Surface

W, H = 1000, 1280
S = 2
sf = Surface(W, H, scale=S, bg=(14, 26, 26))

quote_size = 38
fact_size = 30
frame_w = 710
quote_line_gap = 0.42
fact_line_gap = 0.58

card_x = 90
card_w = 820
card_y = 250
card_h = 720
card_bottom = card_y + card_h

frame_x = card_x + 55
frame_y = card_y + 20
top_pad = 35
gap = 24
bar_h = 76
bar_y = card_bottom - bar_h
serial_mid_y = bar_y + bar_h // 2
frame_h = card_h - 40

bg_layer = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
r = (16 + 16 * (1 - yy) + 14 * xx).astype(np.uint8)
g = (32 + 18 * (1 - yy) + 8 * xx).astype(np.uint8)
b = (36 + 20 * yy + 6 * xx).astype(np.uint8)
bg_layer[..., 0] = r
bg_layer[..., 1] = g
bg_layer[..., 2] = b
bg_layer[..., 3] = 255
sf.composite(bg_layer)

glow_layer = sf.layer()
glow_img = Image.fromarray(glow_layer, 'RGBA')
gd = ImageDraw.Draw(glow_img)
gd.ellipse(
    [(W / 2 - 640) * S, (card_y + card_h / 2 - 540) * S,
     (W / 2 + 640) * S, (card_y + card_h / 2 + 540) * S],
    fill=(190, 220, 200, 34)
)
glow_img = glow_img.filter(ImageFilter.GaussianBlur(160))
sf.composite(np.array(glow_img), mode='screen', opacity=0.9)

cards_layer = sf.layer()
cards_img = Image.fromarray(cards_layer, 'RGBA')
draw = ImageDraw.Draw(cards_img)

def rot(cx, cy, x, y, ang_deg):
    rad = math.radians(ang_deg)
    dx = x - cx
    dy = y - cy
    return (
        cx + dx * math.cos(rad) - dy * math.sin(rad),
        cy + dx * math.sin(rad) + dy * math.cos(rad)
    )

def draw_tilted_card(draw, cx, cy, hw, hh, ang, fill, outline=None, offset=(24, 28)):
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    pts = [rot(cx, cy, x, y, ang) for x, y in corners]
    pts_act = [(x * S, y * S) for x, y in pts]
    shadow_act = [(x * S + offset[0] * S, y * S + offset[1] * S) for x, y in pts]
    draw.polygon(shadow_act, fill=(0, 0, 0, 95))
    draw.polygon(pts_act, fill=fill, outline=outline)

draw_tilted_card(draw, 230, 130, 210, 135, -16, (30, 58, 62, 255), outline=(180, 195, 180, 230))
draw_tilted_card(draw, 820, 125, 195, 130, 12, (42, 66, 56, 255), outline=(170, 185, 165, 230))
draw_tilted_card(draw, 165, 1160, 185, 128, 14, (50, 60, 86, 255), outline=(175, 185, 205, 230))
draw_tilted_card(draw, 850, 1170, 200, 135, -11, (98, 62, 46, 255), outline=(200, 175, 135, 230))
draw_tilted_card(draw, 500, 1150, 265, 135, 2, (36, 48, 56, 255), outline=(160, 175, 185, 230))

sf.composite(np.array(cards_img), mode='normal', opacity=1.0)

shadow_layer = sf.layer()
shadow_img = Image.fromarray(shadow_layer, 'RGBA')
sd = ImageDraw.Draw(shadow_img)
sd.rectangle(
    [(card_x + 24) * S, (card_y + 32) * S,
     (card_x + card_w + 24) * S, (card_bottom + 32) * S],
    fill=(0, 0, 0, 105)
)
shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(42))
sf.composite(np.array(shadow_img), mode='normal', opacity=1.0)

front_layer = sf.layer()
fimg = Image.fromarray(front_layer, 'RGBA')
fd = ImageDraw.Draw(fimg)

fd.rectangle(
    [(card_x + 14) * S, (card_y + 18) * S,
     (card_x + card_w + 14) * S, (card_bottom + 18) * S],
    fill=(54, 78, 75, 255)
)
fd.rounded_rectangle(
    [card_x * S, card_y * S, (card_x + card_w) * S, card_bottom * S],
    radius=10,
    fill=(242, 246, 238, 255),
    outline=(195, 165, 103, 255),
    width=4
)
fd.rounded_rectangle(
    [(card_x + 10) * S, (card_y + 10) * S,
     (card_x + card_w - 10) * S, (card_bottom - 10) * S],
    radius=6,
    outline=(215, 190, 128, 185),
    width=2
)

fd.rectangle(
    [card_x * S, bar_y * S, (card_x + card_w) * S, card_bottom * S],
    fill=(32, 60, 58, 255)
)
fd.line(
    [card_x * S, bar_y * S, (card_x + card_w) * S, bar_y * S],
    fill=(195, 165, 103, 255),
    width=3
)
fd.rectangle(
    [(card_x + 14) * S, (card_y + 18) * S,
     (card_x + 22) * S, (card_bottom + 18) * S],
    fill=(50, 78, 75, 200)
)

sf.composite(np.array(fimg), mode='normal', opacity=1.0)

sf.frame(frame_x, frame_y, frame_w, frame_h)

quote_fill = (24, 38, 36)
fact_fill = (24, 38, 36)
meta_fill = (238, 242, 232)

quote_x = frame_x
quote_y = frame_y + top_pad

quote_box = sf.text(
    quote_x, quote_y, QUOTE,
    family='cjk-hk', size=quote_size, fill=quote_fill,
    anchor='lt', role='quote', bold=True,
    max_w=frame_w, line_gap=quote_line_gap
)

fact_y = quote_box.bottom + gap
sf.text(
    frame_x, fact_y, FACT,
    family='cjk-hk', size=fact_size, fill=fact_fill,
    anchor='lt', role='body',
    max_w=frame_w, line_gap=fact_line_gap
)

sf.serial(
    frame_x + 18, serial_mid_y, SERIAL,
    family='cjk-hk', size=20, fill=meta_fill,
    anchor='lm', role='meta'
)

sf.datestamp(
    frame_x + frame_w - 18, serial_mid_y, DATE,
    family='cjk-hk', size=20, fill=meta_fill,
    anchor='rm', role='meta'
)

sf.save(OUT_PATH)
