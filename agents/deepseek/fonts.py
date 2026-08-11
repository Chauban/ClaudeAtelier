"""逻辑字体名 -> 具体字体文件，并断言字形覆盖。

为什么不硬编码路径和 TTC 索引：
    SKILL.md 里那组索引（2=SC, 3=TC, 4=HK, 0=JP, 1=KR）是 Cowork 沙箱那个
    Debian 构建的值。ubuntu-latest 的打包方式不保证一致，Windows 更是另一套。
    硬编码会在换环境时静默画出错字。

为什么光看 cmap 覆盖不够（实测踩到的坑）：
    NotoSansCJK-Regular.ttc 里 SC/TC/HK/JP/KR 五个 face 的**字符覆盖几乎相同**
    —— 区别在字形长相，不在有没有这个字。所以「谁覆盖得全就选谁」会让五种
    CJK 全部落到 face #0，繁体卡用简体字形渲染、日文特有字形也错。
    正确的判据是 face 自己的**名字**：Noto Sans CJK TC / JP / KR……
    覆盖率退化成硬性门槛（不够就淘汰），选谁由名字决定。

拉丁字体同理：只按「文件名含 dejavusans」会选中 DejaVuSans-ExtraLight，
按「含 dejavuserif」会选中 DejaVuSerifCondensed-Italic —— 整篇英文变成
斜体窄衬线。所以要对 Italic/Condensed/Light 这类变体名做惩罚。
"""
import logging
import os
import re
import sys

from fontTools.ttLib import TTCollection, TTFont

# fontTools 对某些系统字体会刷一堆 "extra bytes in post.stringData" 之类的告警，
# 与我们无关，只会把 runner 日志淹掉。
logging.getLogger("fontTools").setLevel(logging.ERROR)

# 逻辑名 -> 该字体必须能画出的探针字符（硬性门槛）
PROBE = {
    "cjk-sc": "简体中文汉字测试说实国",
    "cjk-tc": "繁體中文漢字測試說實國",
    "cjk-hk": "繁體中文漢字測試說實國",
    "cjk-jp": "日本語のひらがなカタカナ漢字",
    "cjk-kr": "한국어의 한글 문자",
    "serif-cjk": "中文衬线字体测试",
    "sans": "Latin ABC abc 123",
    "serif": "Latin ABC abc 123",
    "mono": "Latin ABC abc 123",
}

# 逻辑名 -> face 名字里应当出现的标记，越靠前越优先。这才是选型的主判据。
NAME_TOKENS = {
    "cjk-sc": ["cjk sc", "sans sc", "noto sans sc", "yahei", "heiti sc", "source han sans sc"],
    "cjk-tc": ["cjk tc", "sans tc", "noto sans tc", "jhenghei", "mingliu", "source han sans tc"],
    "cjk-hk": ["cjk hk", "sans hk", "noto sans hk", "cjk tc", "jhenghei"],
    "cjk-jp": ["cjk jp", "sans jp", "noto sans jp", "yu gothic", "meiryo", "ms gothic"],
    "cjk-kr": ["cjk kr", "sans kr", "noto sans kr", "malgun", "batang"],
    "serif-cjk": ["serif cjk sc", "serif sc", "serif cjk", "songti", "simsun", "source han serif"],
    "sans": ["dejavu sans", "liberation sans", "arial", "helvetica", "segoe ui"],
    "serif": ["dejavu serif", "liberation serif", "times new roman", "georgia"],
    "mono": ["dejavu sans mono", "liberation mono", "consolas", "courier new"],
}

# 变体名惩罚：没点名要的话，这些一律不该被选中当正文字体
VARIANT_PENALTY = ["italic", "oblique", "condensed", "narrow", "extralight", "extra light",
                   "ultralight", "light", "thin", "black", "heavy", "semibold", "demibold",
                   "medium", "display", "caption"]

SEARCH_DIRS = [
    "/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
    r"C:\Windows\Fonts", os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Fonts"),
]

_CACHE = {}


class FontError(RuntimeError):
    pass


def _face_name(ttf):
    try:
        nm = ttf["name"]
        full = nm.getDebugName(4) or ""
        fam = nm.getDebugName(1) or ""
        sub = nm.getDebugName(2) or ""
        typo = nm.getDebugName(16) or ""
        return re.sub(r"\s+", " ", " ".join(x for x in (full, typo, fam, sub) if x)).strip()
    except Exception:
        return ""


def _scan():
    if "all" in _CACHE:
        return _CACHE["all"]
    found = []
    for d in SEARCH_DIRS:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for fn in files:
                if not fn.lower().endswith((".ttf", ".otf", ".ttc", ".otc")):
                    continue
                path = os.path.join(root, fn)
                try:
                    if fn.lower().endswith((".ttc", ".otc")):
                        for i, f in enumerate(TTCollection(path, lazy=True).fonts):
                            found.append((path, i, f, _face_name(f)))
                    else:
                        f = TTFont(path, lazy=True, fontNumber=0)
                        found.append((path, 0, f, _face_name(f)))
                except Exception:
                    continue
    _CACHE["all"] = found
    return found


def _cmap(ttf):
    try:
        return set(ttf.getBestCmap().keys())
    except Exception:
        return set()


def resolve(logical, bold=False):
    """返回 (font_path, face_index)。解析不到就抛 FontError。"""
    key = (logical, bool(bold))
    if key in _CACHE:
        return _CACHE[key]
    if logical not in PROBE:
        raise FontError("未知逻辑字体名 {!r}，可用：{}".format(logical, sorted(PROBE)))

    need = {ord(c) for c in PROBE[logical] if not c.isspace()}
    tokens = NAME_TOKENS[logical]
    want_mono = logical == "mono"

    best = None
    for path, idx, ttf, name in _scan():
        if not need <= _cmap(ttf):
            continue                       # 覆盖不全 —— 硬性淘汰
        low = " " + re.sub(r"[-_]", " ", name.lower()) + " "
        flat = re.sub(r"[\s-]", "", (name or "").lower())

        score, hit = 0, False
        for i, t in enumerate(tokens):
            if t in low or re.sub(r"\s", "", t) in flat:
                score += 100 - i * 6
                hit = True
                break
        if not hit:
            fn = os.path.basename(path).lower().replace("-", "").replace("_", "")
            for i, t in enumerate(tokens):
                if re.sub(r"\s", "", t)[:8] in fn:
                    score += 40 - i * 4
                    hit = True
                    break
        if not hit:
            continue                       # 名字对不上，不猜

        for v in VARIANT_PENALTY:
            if v in low:
                if v in ("black", "heavy", "semibold", "demibold") and bold:
                    continue
                score -= 60
        is_bold = ("bold" in low) or bool(re.search(r"\bbd\b", low))
        score += 25 if is_bold == bool(bold) else -25
        if ("mono" in low) != want_mono:
            score -= 30
        # 单向惩罚：无衬线类逻辑名不该选到 Serif 家族。
        # （反向不能写成对称判断 —— Times New Roman 名字里就没有 "serif"。）
        if logical not in ("serif", "serif-cjk") and "serif" in low:
            score -= 70
        if re.search(r"\b(regular|book)\b", low) and not bold:
            score += 8

        if best is None or score > best[0]:
            best = (score, path, idx, name)

    if best is None:
        raise FontError(
            "解析不到逻辑字体 {!r}（bold={}）。\n"
            "  需要覆盖：{!r}\n"
            "  已扫描：{}\n"
            "  Linux 上装 fonts-noto-cjk fonts-noto-cjk-extra fonts-dejavu-core".format(
                logical, bold, PROBE[logical],
                [d for d in SEARCH_DIRS if os.path.isdir(d)]))
    _CACHE[key] = (best[1], best[2])
    _CACHE[("name",) + key] = best[3]
    return _CACHE[key]


def coverage_of(logical, bold=False):
    path, idx = resolve(logical, bold)
    ck = ("cov", path, idx)
    if ck not in _CACHE:
        try:
            if path.lower().endswith((".ttc", ".otc")):
                ttf = TTCollection(path, lazy=True).fonts[idx]
            else:
                ttf = TTFont(path, lazy=True, fontNumber=0)
            _CACHE[ck] = _cmap(ttf)
        except Exception as e:
            raise FontError("读不出 {} 的 cmap：{}".format(path, e))
    return _CACHE[ck]


def missing_glyphs(text, logical, bold=False):
    """该字体画不出来的字符（去重保序）。空列表 = 安全。"""
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
    lines = ["字体解析结果（{}）".format(sys.platform), "-" * 74]
    seen_faces = {}
    for name in PROBE:
        for bold in (False, True):
            try:
                p, i = resolve(name, bold)
                face = _CACHE.get(("name", name, bold), "")
                lines.append("  {:11s} bold={:<5} -> {}#{}  [{}]".format(
                    name, str(bold), os.path.basename(p), i, face[:44]))
                seen_faces.setdefault((p, i), []).append(name)
            except FontError as e:
                lines.append("  {:11s} bold={:<5} -> 失败：{}".format(
                    name, str(bold), str(e).splitlines()[0]))
    # 五种 CJK 如果全指向同一个 face，说明区分失败 —— 那正是要防的退化
    dup = [(k, v) for k, v in seen_faces.items()
           if len({x for x in v if x.startswith("cjk-")}) > 2]
    if dup:
        lines.append("")
        lines.append("  ! 警告：多种 CJK 指向同一 face，区域字形没有区分开：")
        for k, v in dup:
            lines.append("      {}#{} <- {}".format(os.path.basename(k[0]), k[1], v))
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
    print("\n豆腐块抽查：")
    for txt, fam in [("我們以為自己在看世界", "cjk-tc"), ("ひらがな漢字", "cjk-jp"),
                     ("한글 문자", "cjk-kr"), ("Größe façon", "sans"),
                     ("中文译文测试", "cjk-jp")]:
        try:
            miss = missing_glyphs(txt, fam)
            print("  {:16s} {:9s} -> {}".format(
                txt[:14], fam, "OK" if not miss else "缺字 {}".format(miss)))
        except FontError as e:
            print("  {:16s} {:9s} -> {}".format(txt[:14], fam, str(e).splitlines()[0]))
