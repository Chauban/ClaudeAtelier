"""逻辑字体名 -> 具体字体文件，并断言字形覆盖。

为什么不硬编码路径和 TTC 索引：
    SKILL.md 里那组索引（2=SC, 3=TC, 4=HK, 0=JP, 1=KR）是 Cowork 沙箱
    那个 Debian 构建的值。ubuntu-latest 的 fonts-noto-cjk 打包方式不一定
    相同，Windows 上更是另一套字体。硬编码会在换环境时静默画出错字。
    所以：扫描候选目录，用 cmap 实际覆盖率来挑，挑不到就当场报错。

豆腐块（.notdef 方框）在这里被根除：
    绘制前先问 cmap「你有这个码位吗」，没有就抛错。这比渲染完用眼睛
    找方框可靠得多 —— 一屏 CJK 里漏掉一个方框太容易了。
"""
import os
import sys

from fontTools.ttLib import TTCollection, TTFont

# 逻辑名 -> (候选文件名关键词, 该逻辑名必须覆盖的探针字符)
# 探针字符用于在 TTC 的多个 face 里挑出正确的那一个。
LOGICAL = {
    "cjk-sc":  (["notosanscjk", "notosanssc", "msyh", "simhei", "sourcehansans"], "简体中文汉字测试"),
    "cjk-tc":  (["notosanscjk", "notosanstc", "msjh", "pmingliu", "sourcehansans"], "繁體中文漢字測試"),
    "cjk-hk":  (["notosanscjk", "notosanshk", "msjh", "sourcehansans"], "繁體中文漢字測試"),
    "cjk-jp":  (["notosanscjk", "notosansjp", "yugoth", "meiryo", "msmincho"], "日本語のひらがなカタカナ漢字"),
    "cjk-kr":  (["notosanscjk", "notosanskr", "malgun", "batang"], "한국어의 한글 문자"),
    "serif-cjk": (["notoserifcjk", "notoserifsc", "simsun", "songti"], "中文衬线字体测试"),
    "sans":    (["dejavusans", "arial", "helvetica", "liberationsans", "segoeui"], "Latin ABC abc 123"),
    "serif":   (["dejavuserif", "times", "georgia", "liberationserif"], "Latin ABC abc 123"),
    "mono":    (["dejavusansmono", "consola", "couriernew", "liberationmono"], "Latin ABC abc 123"),
}

SEARCH_DIRS = [
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    os.path.expanduser("~/.fonts"),
    r"C:\Windows\Fonts",
    os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Fonts"),
]

_CACHE = {}


class FontError(RuntimeError):
    pass


def _scan():
    """列出所有字体文件 (path, face_index, cmap_set, 名称小写)。"""
    if "all" in _CACHE:
        return _CACHE["all"]
    found = []
    for d in SEARCH_DIRS:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for fn in files:
                low = fn.lower()
                if not low.endswith((".ttf", ".otf", ".ttc", ".otc")):
                    continue
                path = os.path.join(root, fn)
                try:
                    if low.endswith((".ttc", ".otc")):
                        coll = TTCollection(path, lazy=True)
                        for i, f in enumerate(coll.fonts):
                            found.append((path, i, f))
                    else:
                        found.append((path, 0, TTFont(path, lazy=True, fontNumber=0)))
                except Exception:
                    continue
    _CACHE["all"] = found
    return found


def _cmap_of(ttf):
    try:
        return set(ttf.getBestCmap().keys())
    except Exception:
        return set()


def resolve(logical, bold=False):
    """返回 (font_path, face_index)。解析不到就抛 FontError。"""
    key = (logical, bool(bold))
    if key in _CACHE:
        return _CACHE[key]
    if logical not in LOGICAL:
        raise FontError("未知的逻辑字体名 {!r}，可用：{}".format(
            logical, sorted(LOGICAL)))

    keywords, probe = LOGICAL[logical]
    need = {ord(c) for c in probe if not c.isspace()}

    best = None  # (score, path, index)
    for path, idx, ttf in _scan():
        name = os.path.basename(path).lower()
        hit = next((k for k in keywords if k in name.replace("-", "").replace("_", "")), None)
        if hit is None:
            continue
        cov = _cmap_of(ttf)
        if not need <= cov:
            continue                      # 覆盖不全，这个 face 不合格
        # 打分：关键词越靠前越好；粗细匹配加分
        score = -keywords.index(hit) * 10
        is_bold = ("bold" in name) or ("bd." in name) or ("-b." in name)
        score += 5 if is_bold == bool(bold) else 0
        if "regular" in name and not bold:
            score += 2
        if best is None or score > best[0]:
            best = (score, path, idx)

    if best is None:
        raise FontError(
            "解析不到逻辑字体 {!r}（bold={}）。\n"
            "  需要覆盖探针字符：{!r}\n"
            "  已扫描目录：{}\n"
            "  提示：Linux 上装 fonts-noto-cjk / fonts-dejavu-core".format(
                logical, bold, probe, [d for d in SEARCH_DIRS if os.path.isdir(d)]))

    _CACHE[key] = (best[1], best[2])
    return _CACHE[key]


def coverage_of(logical, bold=False):
    """该逻辑字体实际支持的码位集合（用于绘制前的豆腐块检查）。"""
    path, idx = resolve(logical, bold)
    ck = ("cov", path, idx)
    if ck not in _CACHE:
        try:
            if path.lower().endswith((".ttc", ".otc")):
                ttf = TTCollection(path, lazy=True).fonts[idx]
            else:
                ttf = TTFont(path, lazy=True, fontNumber=0)
            _CACHE[ck] = _cmap_of(ttf)
        except Exception as e:
            raise FontError("读不出 {} 的 cmap：{}".format(path, e))
    return _CACHE[ck]


def missing_glyphs(text, logical, bold=False):
    """返回 text 里该字体画不出来的字符（去重、保序）。空列表 = 安全。"""
    cov = coverage_of(logical, bold)
    out, seen = [], set()
    for ch in text:
        if ch in seen or ch.isspace():
            continue
        seen.add(ch)
        if ord(ch) not in cov:
            out.append(ch)
    return out


def report():
    lines = ["字体解析结果（{}）".format(sys.platform), "-" * 58]
    for name in LOGICAL:
        for bold in (False, True):
            try:
                p, i = resolve(name, bold)
                lines.append("  {:11s} bold={:<5} -> {}#{}".format(
                    name, str(bold), os.path.basename(p), i))
            except FontError as e:
                lines.append("  {:11s} bold={:<5} -> 失败：{}".format(
                    name, str(bold), str(e).splitlines()[0]))
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
    print("\n豆腐块检查抽样：")
    for txt, fam in [("我們以為自己在看世界", "cjk-tc"),
                     ("ひらがな漢字", "cjk-jp"),
                     ("한글 문자", "cjk-kr"),
                     ("Größe façon", "sans"),
                     ("emoji 🙂 test", "sans")]:
        try:
            miss = missing_glyphs(txt, fam)
            print("  {:16s} {:9s} -> {}".format(
                txt[:14], fam, "OK" if not miss else "缺字 {}".format(miss)))
        except FontError as e:
            print("  {:16s} {:9s} -> {}".format(txt[:14], fam, str(e).splitlines()[0]))
