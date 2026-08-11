"""渲染后在最终像素上复查 —— Tier1 的逐调用检查抓不到的那些问题。

这里查的都是「画的时候还没错，合成完才错」的情况：
  · 白底白字（bbox 检查会愉快放行）
  · 后画的图层把文字盖住了
  · 脚本跑完了但画布几乎是空的
  · 编号或日期漏掉了 / 画了两次
"""
import numpy as np

# WCAG 对比度阈值
CONTRAST_BODY = 4.5
CONTRAST_LARGE = 3.0        # >=24 逻辑 px 视为大字
CONTRAST_META = 3.0
LARGE_PX = 24

EDGE_PAD = 6                # 逻辑 px：墨迹不许贴到这么近的边缘
MIN_UNIQUE_COLORS = 24
SOLID_ROLES_FOR_WIDOW = {"body", "quote", "title"}   # meta 短本来就正常，不查孤行


class LintError(RuntimeError):
    pass


def _lum(rgb):
    """WCAG 相对亮度。"""
    c = np.asarray(rgb, dtype=np.float64) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def contrast(rgb1, rgb2):
    l1, l2 = _lum(rgb1), _lum(rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def run(sf, strict=True, known_text=None):
    """对 Surface 做全套检查。返回 (问题列表, 指标字典)。

    known_text：本次卡片真实内容（SERIAL/DATE/QUOTE/FACT）。给了就能查出
    模型自己编造的装饰性编号 —— 见下面第 7 项。
    """
    problems, metrics = [], {}
    img = np.array(sf.img, dtype=np.uint8)
    ink = np.array(sf.ink, dtype=np.uint8)
    H, W = img.shape[:2]
    S = sf.scale

    # ---------------------------------------------------- 1. 编号与日期
    if sf._serial_done != 1:
        problems.append(
            "编号：serial() 调用了 {} 次，必须恰好 1 次。"
            "章程第 8 节要求流水号必须出现在卡面上。".format(sf._serial_done))
    if sf._date_done != 1:
        problems.append(
            "日期：datestamp() 调用了 {} 次，必须恰好 1 次。".format(sf._date_done))

    # ---------------------------------------------------- 2. 逐块可读性
    # 一次检查同时覆盖「白底白字」和「被后画的图层盖住」：
    # 都表现为最终图里文字墨色与其局部背景对比度不足。
    worst = None
    warn_local = []      # 局部背景不干净（装饰压字），只警告不拦截
    for b in sf.boxes:
        if not b.mask_bbox:
            continue
        x0, y0, x1, y1 = b.mask_bbox
        x0, y0 = max(0, x0 - 2), max(0, y0 - 2)
        x1, y1 = min(W, x1 + 2), min(H, y1 + 2)
        if x1 <= x0 or y1 <= y0:
            continue
        sub_img = img[y0:y1, x0:x1].reshape(-1, 3)
        sub_ink = ink[y0:y1, x0:x1].reshape(-1)
        ink_px = sub_img[sub_ink > 140]
        bg_px = sub_img[sub_ink < 12]
        if len(ink_px) < 8:
            problems.append(
                "文字没有落墨：{!r}（role={}）在最终图里找不到笔画，"
                "可能被后面的 composite() 完全盖掉了。".format(
                    (b.text or "")[:30], b.role))
            continue
        if len(bg_px) < 8:
            continue
        fg = np.median(ink_px, axis=0)
        bg = np.median(bg_px, axis=0)
        cr = contrast(fg, bg)
        need = (CONTRAST_META if b.role == "meta"
                else CONTRAST_LARGE if b.size >= LARGE_PX else CONTRAST_BODY)
        if worst is None or cr < worst[0]:
            worst = (cr, b, fg, bg, need)

        # 局部最差背景：中位数对中位数会掩盖局部失败。
        # 实测两次踩到：侘寂那张的朱印、纸雕那张的六边形，都只压住文字的一小块，
        # 不足以拉动背景中位数，于是「对比度」读数很漂亮，但那几个字实际糊了。
        # 所以另看：背景里与文字亮度最接近的那一档，占比够大就要报。
        bg_l = _lum(bg_px)
        fg_l = float(_lum(fg))
        if len(bg_px) >= 40:
            edges = np.percentile(bg_l, np.arange(0, 101, 10))
            for lo, hi in zip(edges[:-1], edges[1:]):
                sel = (bg_l >= lo) & (bg_l <= hi)
                share = float(sel.mean())
                if share < 0.06:
                    continue
                band = np.median(bg_px[sel], axis=0)
                c2 = contrast(fg, band)
                if c2 < need * 0.8:
                    warn_local.append(
                        "文字背景不干净：{!r}（role={}）有约 {:.0%} 的背景区域"
                        "与文字亮度接近（该处对比度仅 {:.2f}，整体读数 {:.2f}）。"
                        "多半是装饰元素压在文字上了——把装饰挪开，"
                        "或在文字下方垫一块底色。".format(
                            (b.text or "")[:24], b.role, share, c2, cr))
                    break

        if cr < need:
            problems.append(
                "对比度不足：{!r}（role={} size={}）\n"
                "    文字色 rgb{}  背景色 rgb{}  对比度 {:.2f}，需要 ≥{}\n"
                "    要么换文字颜色，要么给它垫一块底色。".format(
                    (b.text or "")[:30], b.role, b.size,
                    tuple(int(v) for v in fg), tuple(int(v) for v in bg), cr, need))
    metrics["worst_contrast"] = round(float(worst[0]), 2) if worst else None

    # ---------------------------------------------------- 3. 墨迹贴边
    pad = int(EDGE_PAD * S)
    if ink.shape[0] > 2 * pad and ink.shape[1] > 2 * pad:
        edge = ink.copy()
        edge[pad:-pad, pad:-pad] = 0
        n = int((edge > 140).sum())
        metrics["edge_ink_px"] = n
        if n > 0:
            ys, xs = np.nonzero(edge > 140)
            problems.append(
                "文字墨迹贴到画布边缘（{} 个像素，最近处 x={} y={} 逻辑坐标）。"
                "边距至少留 {}px。".format(
                    n, int(xs.min() / S), int(ys.min() / S), EDGE_PAD))

    # ---------------------------------------------------- 4. 退化画面
    small = img[::4, ::4].reshape(-1, 3)
    uniq = len(np.unique((small // 8).astype(np.int32) @ np.array([1, 1 << 8, 1 << 16]), axis=0))
    metrics["unique_colors"] = uniq
    if uniq < MIN_UNIQUE_COLORS:
        problems.append(
            "画面几乎是空的：只有 {} 种颜色（阈值 {}）。"
            "脚本大概跑完了但什么都没画出来。".format(uniq, MIN_UNIQUE_COLORS))

    # 用「结构」而不是「与中位色的差异」来判断画面是否退化。
    #
    # 教训：早先按「偏离中位色的像素比例」算，结果体积光/渐变类风格（S43、S47）
    # 整张画布都是渐变，读数冲到 83% 被判「画面过满」；模型减弱渐变后又掉到 2.9%
    # 被判「内容太少」—— 在两个互相矛盾的阈值之间来回撞墙，三轮都过不了。
    # 平滑渐变既不是内容也不是空白，它是背景。真正能区分「画了东西」和「什么都没画」
    # 的是边缘能量：渐变几乎没有边缘，文字和图形有。
    g = img.astype(np.float32).mean(axis=2)
    edge = np.abs(np.diff(g[::2, ::2], axis=0)[:, :-1]) + \
        np.abs(np.diff(g[::2, ::2], axis=1)[:-1, :])
    detail = float((edge > 12).mean())
    metrics["detail_coverage"] = round(detail, 4)
    if detail < 0.004 and uniq < 64:
        problems.append(
            "画面退化：几乎没有任何边缘结构（细节覆盖 {:.2%}），"
            "看起来只有一层底色或渐变，正文和装饰都没画上去。".format(detail))
    # 注意：这里**没有**「画面过满 / 留白不足」的上限。留白多少是审美判断，
    # 不该由规则裁决 —— 那是模型的创作空间，规则只兜住「什么都没画」这种硬失败。

    # ---------------------------------------------------- 5. 画布规格
    metrics["canvas"] = "{}x{} logical, {}x{} actual".format(sf.w, sf.h, W, H)
    if (W, H) != (sf.w * S, sf.h * S):
        problems.append("画布实际尺寸与 scale 不符。")
    if sf.h <= sf.w:
        problems.append("必须竖版：高要大于宽。")
    if not (800 <= sf.w <= 1200):
        problems.append("逻辑宽度须在 800~1200（章程第 9 节）。")

    metrics["text_boxes"] = len(sf.boxes)
    metrics["composites"] = sf._composites
    metrics["min_font_size"] = min([b.size for b in sf.boxes], default=None)

    # ---------------------------------------------------- 6. 构图（只警告，不拦截）
    # 「文字全挤在上半张、下面一大片空」是最常见的构图失败，而且是可机械判定的。
    # 但极简大留白（S1）之类的风格本来就该空，所以这里只警告、给一次改进机会，
    # 不做硬性拦截 —— 审美判断不该由规则代劳。
    warnings = list(warn_local)

    # 孤行：折行后最后一行只剩一两个字。与禁则处理同一个家族 ——
    # 盲模型看不见，但完全是机械规则。首张端到端卡就出了一个（引言末行只剩「る。」）。
    for b in sf.boxes:
        ls = getattr(b, "lines", None) or []
        if len(ls) >= 2 and b.role in SOLID_ROLES_FOR_WIDOW:
            last, prev = ls[-1].strip(), max((len(x) for x in ls[:-1]), default=1)
            if 0 < len(last) <= 2 and prev >= 6:
                warnings.append(
                    "孤行：{!r} 折行后最后一行只剩 {!r}（前面各行有 {} 字左右）。"
                    "把 max_w 调小一点或换个字号，让末行不至于只挂两个字。".format(
                        (b.text or "")[:22], last, prev))

    rows = (ink > 140).sum(axis=1)
    nz = np.nonzero(rows > 0)[0]
    if len(nz):
        top_gap = nz[0] / float(H)
        bot_gap = (H - 1 - nz[-1]) / float(H)
        metrics["text_span"] = "{:.0%}~{:.0%}".format(top_gap, 1 - bot_gap)
        if bot_gap > 0.22:
            warnings.append(
                "底部 {:.0%} 的高度完全没有文字（文字止于 {:.0%} 处）。"
                "如果这不是刻意的留白，考虑把版面重心下移、加大字号、"
                "增加装饰元素，或缩短画布高度。".format(bot_gap, 1 - bot_gap))
        if top_gap > 0.28:
            warnings.append(
                "顶部 {:.0%} 的高度完全没有文字。".format(top_gap))
    # ---------------------------------------------------- 7. 编造的编号
    # 实测踩到：S42 那张卡右上角正确印了 DS.0002，模型又在底部加了一行装饰性的
    # 「... 006 ...」当版式点缀。卡面上出现两个互相矛盾的编号，对读者是误导；
    # 而且那个假编号还顺带把「底部无文字」的构图警告给盖过去了。
    # 我们知道本卡的全部真实文本，凡是不在其中的数字串，就是模型自己编的。
    if known_text:
        import re
        pool = "".join(str(t or "") for t in known_text)
        pool_digits = set(re.findall(r"\d+", pool))
        for b in sf.boxes:
            for run_ in re.findall(r"\d{3,}", b.text or ""):
                if run_ in pool_digits or any(run_ in d for d in pool_digits):
                    continue
                warnings.append(
                    "卡面上出现了编造的数字「{}」（在文字块 {!r} 里），"
                    "它不属于本卡的流水号、日期、金句或冷知识。"
                    "读者会把它当成另一个编号。请删掉，或改用真实的 SERIAL。".format(
                        run_, (b.text or "")[:24]))

    metrics["warnings"] = warnings

    if problems and strict:
        raise LintError("渲染后检查未通过（{} 项）：\n  - {}".format(
            len(problems), "\n  - ".join(problems)))
    return problems, metrics


def format_metrics(m):
    return "\n".join("    {:16s} {}".format(k, v) for k, v in m.items())
