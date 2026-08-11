"""给看不见图的模型当眼睛。

规则 linter 能判「这行字越界了」，判不了「整张卡的东西全挤在上面三分之一」。
后者恰恰是构图失败最常见的样子。所以把渲染结果压成模型读得懂的形式：
占位图、亮度图、调色板、墨迹重心、纵向直方图、逐块清单。

零成本 —— 纯数组运算，不调用任何模型。
"""
import numpy as np

RAMP = " .:-=+*#%@"          # 由浅到深


def occupancy(sf, cols=40, rows=64):
    """占位图：. 空白 / T 受控文字 / # 非底色内容 / ~ 中间调"""
    img = np.array(sf.img, dtype=np.int16)
    ink = np.array(sf.ink, dtype=np.uint8)
    H, W = ink.shape
    modal = np.median(img[::16, ::16].reshape(-1, 3), axis=0)
    content = (np.abs(img - modal).sum(axis=2) > 30)

    out = []
    for r in range(rows):
        y0, y1 = r * H // rows, max((r + 1) * H // rows, r * H // rows + 1)
        line = ""
        for c in range(cols):
            x0, x1 = c * W // cols, max((c + 1) * W // cols, c * W // cols + 1)
            t = (ink[y0:y1, x0:x1] > 140).mean()
            k = content[y0:y1, x0:x1].mean()
            line += "T" if t > 0.06 else ("#" if k > 0.55 else ("~" if k > 0.12 else "."))
        out.append(line)
    return out


def luminance_art(sf, cols=48, rows=76):
    img = np.array(sf.img.convert("L"), dtype=np.float32)
    H, W = img.shape
    out = []
    for r in range(rows):
        y0, y1 = r * H // rows, max((r + 1) * H // rows, r * H // rows + 1)
        line = ""
        for c in range(cols):
            x0, x1 = c * W // cols, max((c + 1) * W // cols, c * W // cols + 1)
            v = img[y0:y1, x0:x1].mean() / 255.0
            line += RAMP[min(len(RAMP) - 1, int((1.0 - v) * len(RAMP)))]
        out.append(line)
    return out


def palette(sf, top=8):
    img = np.array(sf.img, dtype=np.uint8)[::3, ::3].reshape(-1, 3)
    q = (img // 16 * 16).astype(np.uint8)
    keys = q[:, 0].astype(np.int32) * 65536 + q[:, 1].astype(np.int32) * 256 + q[:, 2]
    vals, counts = np.unique(keys, return_counts=True)
    order = np.argsort(-counts)[:top]
    total = float(len(keys))
    out = []
    for i in order:
        k = int(vals[i])
        out.append(("#{:02x}{:02x}{:02x}".format(k >> 16, (k >> 8) & 255, k & 255),
                    round(counts[i] / total * 100, 1)))
    return out


def ink_stats(sf, buckets=20):
    ink = np.array(sf.ink, dtype=np.uint8) > 140
    H, W = ink.shape
    tot = int(ink.sum())
    if not tot:
        return {"centroid": None, "histogram": [0] * buckets, "ink_px": 0}
    ys, xs = np.nonzero(ink)
    hist = []
    for b in range(buckets):
        y0, y1 = b * H // buckets, (b + 1) * H // buckets
        hist.append(round(float(ink[y0:y1].sum()) / tot * 100, 1))
    return {"centroid": (round(float(xs.mean()) / W * 100, 1),
                         round(float(ys.mean()) / H * 100, 1)),
            "histogram": hist, "ink_px": tot}


def describe(sf, metrics=None):
    """拼成一段喂回给模型的文字。"""
    L = []
    L.append("画布 {}x{} 逻辑像素（实际 {}x{}，scale={}）".format(
        sf.w, sf.h, sf.W, sf.H, sf.scale))

    L.append("\n【占位图】列=画布宽，行=画布高；. 空白  ~ 淡内容  # 实心内容  T 文字")
    L.append("+" + "-" * 40 + "+")
    for row in occupancy(sf):
        L.append("|" + row + "|")
    L.append("+" + "-" * 40 + "+")

    st = ink_stats(sf)
    if st["centroid"]:
        L.append("\n文字墨迹重心：x={}%  y={}%   （y 远离 50% 说明上下不平衡）".format(
            *st["centroid"]))
        h = st["histogram"]
        L.append("纵向文字分布（每格 5% 高度，数字为该带占全部文字墨迹的百分比）：")
        L.append("  " + " ".join("{:>4.0f}".format(v) for v in h[:10]))
        L.append("  " + " ".join("{:>4.0f}".format(v) for v in h[10:]))
        empty_top = sum(1 for v in h[:4] if v < 0.5)
        empty_bot = sum(1 for v in h[-4:] if v < 0.5)
        if empty_bot >= 4:
            L.append("  ! 底部 20% 完全没有文字 —— 检查是不是所有内容都挤在上方")
        if empty_top >= 4:
            L.append("  ! 顶部 20% 完全没有文字")

    L.append("\n【调色板】占比最高的颜色：")
    for hexv, pct in palette(sf):
        L.append("  {}  {:>5.1f}%".format(hexv, pct))

    L.append("\n【已绘制的文字块】")
    for i, b in enumerate(sf.boxes, 1):
        L.append("  {}. role={:5s} size={:>3}px  x={:>4.0f} y={:>4.0f} w={:>4.0f} h={:>4.0f}  {!r}".format(
            i, b.role, b.size, b.x, b.y, b.w, b.h, (b.text or "")[:34]))

    if metrics:
        L.append("\n【检查指标】")
        for k, v in metrics.items():
            L.append("    {:16s} {}".format(k, v))
    return "\n".join(L)
