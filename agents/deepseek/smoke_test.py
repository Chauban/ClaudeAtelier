"""冒烟测试：先证明这套 API 人能驱动，再谈让盲模型驱动。

一、按 S24 工程蓝图画一张真卡，跑 lint，出占位图。
二、逐个触发守卫，确认报错信息足以让盲模型改对。
"""
import io
import sys
import traceback

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import lint
import preview
from atelier_canvas import DrawError, Surface

W, H, S = 1000, 1780, 2
QUOTE = "把尺寸标出来，是为了让后来的人，不必再猜一次。"
FACT = ("一九七九年三月二日，皮尔等人以潮汐加热推算木卫一内部大半已熔融，"
        "并写下：这件事的后果或许会出现在航海家一号即将传回的照片里。"
        "三天后探测器飞掠木星，三月九日照片上浮出一朵高约二百七十公里的喷发云。")
SERIAL, DATE = "DWG NO. DS.0001", "DATE 2026-08-11"


def draw_card():
    sf = Surface(W, H, scale=S, bg=(11, 42, 82))

    # ---- Tier 2：蓝图底 —— 渐变 + 细网格 + 角落晕影
    lay = sf.layer()
    yy = np.linspace(0, 1, sf.H)[:, None]
    xx = np.linspace(0, 1, sf.W)[None, :]
    glow = np.clip(1.15 - ((xx - .5) ** 2 + (yy - .38) ** 2) * 2.6, 0, 1)
    lay[..., 0] = (16 + glow * 26).astype(np.uint8)
    lay[..., 1] = (52 + glow * 44).astype(np.uint8)
    lay[..., 2] = (104 + glow * 62).astype(np.uint8)
    lay[..., 3] = 255
    sf.composite(lay)

    grid = sf.layer()
    step = 40 * S
    grid[::step, :, :3] = 255
    grid[:, ::step, :3] = 255
    grid[::step, :, 3] = 26
    grid[:, ::step, 3] = 26
    big = 200 * S
    grid[::big, :, 3] = 58
    grid[:, ::big, 3] = 58
    sf.composite(grid)

    # ---- 图框（双线）
    fr = sf.layer()
    for inset, alpha, tk in ((28 * S, 190, 3), (40 * S, 110, 1)):
        fr[inset:inset + tk, inset:-inset, :3] = 255
        fr[-inset - tk:-inset, inset:-inset, :3] = 255
        fr[inset:-inset, inset:inset + tk, :3] = 255
        fr[inset:-inset, -inset - tk:-inset, :3] = 255
        fr[inset:inset + tk, inset:-inset, 3] = alpha
        fr[-inset - tk:-inset, inset:-inset, 3] = alpha
        fr[inset:-inset, inset:inset + tk, 3] = alpha
        fr[inset:-inset, -inset - tk:-inset, 3] = alpha
    sf.composite(fr)

    # ---- 尺寸标注线（蓝图的招牌元素）
    ann = sf.layer()
    ax = 78 * S
    ann[300 * S:1180 * S, ax:ax + 2, :3] = 255
    ann[300 * S:1180 * S, ax:ax + 2, 3] = 150
    for yv in (300 * S, 1180 * S):
        ann[yv - 1:yv + 2, ax - 9 * S:ax + 10 * S, :3] = 255
        ann[yv - 1:yv + 2, ax - 9 * S:ax + 10 * S, 3] = 150
    sf.composite(ann)

    sf.frame(96, 120, W - 192, H - 230)

    # ---- Tier 1：文字
    sf.text(W / 2, 168, "VERSE / FACT  SHEET", family="mono", size=30,
            fill=(190, 215, 255), anchor="mt", role="meta")
    sf.text(W / 2, 232, "木 卫 一 · 喷 发 云 观 测", family="cjk-sc", size=46,
            fill=(255, 255, 255), anchor="mt", role="title", bold=True)

    sf.text(W / 2, 400, QUOTE, family="cjk-sc", size=44, fill=(255, 255, 255),
            anchor="mt", role="quote", max_w=W - 300, line_gap=0.62)

    sf.text(W / 2, 760, "SCALE 1:1   SHEET 1 OF 1", family="mono", size=24,
            fill=(150, 185, 240), anchor="mt", role="meta")

    sf.text(W / 2, 880, FACT, family="cjk-sc", size=30, fill=(214, 232, 255),
            anchor="mt", role="body", max_w=W - 300, line_gap=0.72)

    # ---- 标题栏（右下角，蓝图惯例）
    tb = sf.layer()
    x0, y0 = (W - 420) * S, (H - 250) * S
    tb[y0:y0 + 150 * S, x0:x0 + 380 * S, :3] = 255
    tb[y0:y0 + 150 * S, x0:x0 + 380 * S, 3] = 30
    tb[y0:y0 + 2, x0:x0 + 380 * S, 3] = 170
    sf.composite(tb)

    sf.serial(W - 400, H - 228, SERIAL, family="mono", size=26,
              fill=(255, 255, 255), anchor="lt")
    sf.datestamp(W - 400, H - 186, DATE, family="mono", size=26,
                 fill=(206, 228, 255), anchor="lt")
    sf.text(W - 400, H - 144, "PROJECT  CLAUDEATELIER", family="mono", size=22,
            fill=(160, 195, 245), anchor="lt", role="meta")
    return sf


def expect_error(label, fn):
    try:
        fn()
    except (DrawError, lint.LintError) as e:
        first = str(e).strip().splitlines()
        print("  [拦截] {}".format(label))
        for ln in first[:4]:
            print("         {}".format(ln))
        print()
        return True
    except Exception as e:
        print("  [异常] {} -> 抛了意料之外的 {}: {}".format(label, type(e).__name__, e))
        return False
    print("  [漏网] {} —— 守卫没拦住！".format(label))
    return False


print("=" * 66)
print("一、正常渲染一张 S24 工程蓝图")
print("=" * 66)
sf = draw_card()
problems, metrics = lint.run(sf, strict=False)
out = __import__("os").path.join(__import__("os").path.dirname(
    __import__("os").path.abspath(__file__)), "smoke_blueprint.png")
sf.save(out)
print("已保存：{}".format(out))
print("lint 问题数：{}".format(len(problems)))
for p in problems:
    print("  ! {}".format(p))
print()
print(preview.describe(sf, metrics))

print()
print("=" * 66)
print("二、守卫是否真的拦得住（每条都应被拦截）")
print("=" * 66)

results = []
results.append(expect_error("文字越界", lambda: Surface(W, H).text(
    900, 100, "这段文字从右边跑出去了这段文字从右边跑出去了", family="cjk-sc",
    size=40, role="body")))

results.append(expect_error("字号过小", lambda: Surface(W, H).text(
    100, 100, "正文只有 12px", family="cjk-sc", size=12, role="body")))

results.append(expect_error("豆腐块（拉丁字体画中文）", lambda: Surface(W, H).text(
    100, 100, "这些汉字 Arial 画不出来", family="sans", size=40, role="body")))


def _overlap():
    s = Surface(W, H)
    s.text(100, 300, "第一块文字在这里", family="cjk-sc", size=40, role="body")
    s.text(100, 320, "第二块压上去了", family="cjk-sc", size=40, role="body")


results.append(expect_error("两块文字重叠", _overlap))


def _white_on_white():
    s = Surface(W, H, bg=(255, 255, 255))
    s.text(W / 2, 300, "白底白字看不见", family="cjk-sc", size=40,
           fill=(252, 252, 252), anchor="mt", role="body")
    s.serial(100, 1600, "NO.0001", family="mono", size=24)
    s.datestamp(100, 1660, "2026-08-11", family="mono", size=24)
    lint.run(s, strict=True)


results.append(expect_error("白底白字（bbox 检查放行，lint 拦截）", _white_on_white))


def _covered():
    s = Surface(W, H, bg=(20, 20, 30))
    s.text(W / 2, 400, "这行字会被后画的图层盖掉", family="cjk-sc", size=40,
           fill=(255, 255, 255), anchor="mt", role="body")
    s.serial(100, 1600, "NO.0001", family="mono", size=24, fill=(255, 255, 255))
    s.datestamp(100, 1660, "2026-08-11", family="mono", size=24, fill=(255, 255, 255))
    cover = s.layer()
    cover[300 * S:600 * S, :, :3] = 20
    cover[300 * S:600 * S, :, 3] = 255
    s.composite(cover)
    lint.run(s, strict=True)


results.append(expect_error("文字被后画的图层盖住", _covered))


def _no_serial():
    s = Surface(W, H, bg=(240, 240, 235))
    s.text(W / 2, 400, "有正文但忘了编号和日期", family="cjk-sc", size=40,
           fill=(20, 20, 20), anchor="mt", role="body")
    lint.run(s, strict=True)


results.append(expect_error("漏了编号/日期", _no_serial))

print("=" * 66)
print("守卫命中 {}/{}".format(sum(results), len(results)))
print("=" * 66)
