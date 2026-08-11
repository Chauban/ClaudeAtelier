"""风格 / 领域 / 语言三张对照表 —— **从章程解析，不在这里再抄一份**。

这是「单一真相源」落到代码层面的做法。如果把 47 种风格复制进 Python，
改章程时就必须记得同步改这里，而漏改是无声的：卡照出，只是风格编号
对不上名字，等发现时台账里已经写满错数据。解析就没有这个问题 ——
章程改了，这里自动跟着变；章程格式坏了，启动即报错。
"""
import io
import re

import config


class TableError(RuntimeError):
    pass


def _section(text, heading):
    """取出 '## N 标题' 到下一个 '## ' 之间的内容。"""
    m = re.search(r"^##\s+" + re.escape(heading) + r"\s*$(.*?)(?=^##\s|\Z)",
                  text, re.M | re.S)
    if not m:
        raise TableError("章程里找不到小节 {!r}。改过标题？".format(heading))
    return m.group(1)


def _parse_numbered(block, expect):
    """解析 '1 甲 / 2 乙 / 3 丙' 这种一行式编号表。

    不能直接按 '/' 切：风格 38 的括号里就有「顶面/左面/右面」。
    所以只在「斜杠后面紧跟编号」的位置切开。
    """
    line = max((l.strip().lstrip("> ").strip()
                for l in block.splitlines() if re.match(r"^>?\s*1\s+\S", l.strip())),
               key=len, default="")
    if not line:
        raise TableError("这一节里找不到编号表正文")
    parts = re.split(r"\s*/\s*(?=\d{1,2}\s)", line)
    out = {}
    for p in parts:
        m = re.match(r"^(\d{1,2})\s+(.+?)\s*$", p)
        if not m:
            raise TableError("解析不了这一项：{!r}".format(p[:60]))
        out[int(m.group(1))] = m.group(2)
    if sorted(out) != list(range(1, expect + 1)):
        raise TableError("编号应为 1~{}，实际解析出 {} 项：{}".format(
            expect, len(out), sorted(out)))
    return out


_CACHE = {}


def load():
    if "t" in _CACHE:
        return _CACHE["t"]
    text = io.open(config.CHARTER, encoding="utf-8").read()
    t = {
        "styles": _parse_numbered(_section(text, "4. 风格对照表 S"), 47),
        "topics": _parse_numbered(_section(text, "5. 冷知识领域对照表 K"), 17),
        "langs": _parse_numbered(_section(text, "6. 语言对照表 L"), 7),
    }
    _CACHE["t"] = t
    return t


def style(n):
    return load()["styles"][int(n)]


def topic(n):
    return load()["topics"][int(n)]


def lang(n):
    return load()["langs"][int(n)]


# 语言槽 -> 卡面语言代码。第 7 槽是「其他语种」轮换，由 run.py 挑定后覆盖。
LANG_CODE = {1: "ZH", 2: "ZH-TW", 3: "ZH-HK", 4: "YUE", 5: "EN", 6: "JA"}
LANG7_CHOICES = [("法文", "FR"), ("德文", "DE"), ("西班牙文", "ES"),
                 ("韩文", "KO"), ("意大利文", "IT")]

# 语言 -> 渲染时该用的字体族（给模型的提示，非强制）
LANG_FONT = {"ZH": "cjk-sc", "ZH-TW": "cjk-tc", "ZH-HK": "cjk-hk", "YUE": "cjk-hk",
             "JA": "cjk-jp", "KO": "cjk-kr", "EN": "serif", "FR": "serif",
             "DE": "serif", "ES": "serif", "IT": "serif"}


def short_style_name(name):
    """风格简名：4~8 字，去掉括号补充说明和 Windows 非法字符（章程第 12 节）。"""
    s = re.sub(r"[（(].*?[）)]", "", name).strip()
    s = re.sub(r'[\\/:*?"<>|]', "", s)
    s = s.replace(" ", "")
    return s[:8] or "未命名"


if __name__ == "__main__":
    t = load()
    print("风格 {} 种，领域 {} 个，语言 {} 种 —— 全部解析自章程".format(
        len(t["styles"]), len(t["topics"]), len(t["langs"])))
    for n in (1, 24, 38, 47):
        print("  S{:<3} {}  -> 简名 {!r}".format(n, t["styles"][n],
                                                short_style_name(t["styles"][n])))
    print("  K5   {}".format(t["topics"][5]))
    print("  L7   {}".format(t["langs"][7]))
