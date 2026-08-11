"""证据闸门 —— 不带模型的确定性判定。

章程第 3 节「核实不许跳过」是这个项目最贵、也最容易被悄悄优化掉的一步。
交给模型自觉是没用的，所以做成结构上无法伪造：

  模型必须交出 claims[]，每条含 {claim, url, evidence}，
  其中 evidence 必须是该 url 页面正文里**逐字存在**的句子。
  我们真去抓那个页面，做规范化子串比对。编不出来。

诚实的局限：这只证明「确有页面这么说」，不证明「那个页面是对的」。
但这与 Claude 的 WebSearch 步骤实际提供的保证等价 —— 没有退步，
而且从「靠自觉」变成了「被强制」。
"""
import re

import fetch


class VerifyError(RuntimeError):
    pass


# 需要被证据覆盖的 token：数字、年份、专名
def _key_tokens(text):
    toks = set()
    for m in re.findall(r"\d[\d,\.]*", text or ""):
        t = m.strip(".,")
        if len(t.replace(",", "").replace(".", "")) >= 2:
            toks.add(t)
    # 拉丁专名（连续大写开头词）
    for m in re.findall(r"\b[A-Z][a-zA-Z\-']{2,}\b", text or ""):
        if m.lower() not in ("the", "and", "for", "with", "this", "that"):
            toks.add(m)
    return toks



# 语言 -> 该用哪种字形。粤语、港台繁体都写繁体（Claude 一直是这么做的）。
HANT_LANGS = {"ZH-TW", "ZH-HK", "YUE"}
HANS_LANGS = {"ZH"}

# 一简对多繁、转换要看语境的字。逐字比对时一律跳过，否则会把正确的
# 繁体文本误判成简体（既有的 NO.18 就是被「厘里托」误伤的）。
AMBIGUOUS = set(
    "里厘托后干发系复志表只云松面板谷丑征曲舍术台布才斗范姜卷累帘折冲尽借"
    "当同向恶几家据尔别刮划回汇伙价佣朴曝签苏坛叶郁御愿沄准致制种周注"
)


def check_orthography(text, lang_code):
    """繁简是否与卡片语言相符。返回问题描述，没问题返回 None。

    实测踩到：第一张粤语卡，标题和年表是繁体，正文与金句却是简体 ——
    「葡撻唔係澳門土產」配「葡挞其实唔系澳门土产」，同一张卡两套字形。
    章程的语言表只写「4 粤语口语」，没写该用哪种字形，Claude 靠常识
    推断出繁体，DeepSeek 没有。靠提示词补一句不如直接判定。

    不能「有一处差异就判错」：像「葡萄牙里斯本」的「里」，转繁会变成
    「裡」，但那是误转。所以看差异的量 —— 真正的简体文本会大面积改变。
    """
    try:
        import zhconv
    except ImportError:
        return None                     # 没装就不查，不阻断
    t = (text or "").strip()
    cjk = [c for c in t if "一" <= c <= "鿿"]
    if len(cjk) < 8:
        return None

    def diff_chars(target):
        conv = zhconv.convert(t, target)
        if len(conv) != len(t):
            return []                   # 长度变了就没法逐字比，放过
        out = []
        for a, b in zip(t, conv):
            if a == b:
                continue
            # 只看汉字：zhconv 会把「」转成“”，那不是繁简差异（对既有的
            # NO.41 就是这么误报了 10 处）
            if not ("一" <= a <= "鿿" and "一" <= b <= "鿿"):
                continue
            # 一简对多繁、要看语境的字，一律放过 —— 「葡萄牙里斯本」的「里」
            # 会被转成「裡」，是误转不是错字（NO.18 因此误报）
            if a in AMBIGUOUS:
                continue
            out.append(a)
        return out

    def hit(d):
        """3 个以上一定是；2 个但占比高也算 —— 短金句错两个字就很明显了。
        单个差异一律放过：那多半是 里/裡 这类误转。"""
        n, ratio = len(d), len(d) / float(len(cjk))
        return n >= 3 or (n >= 2 and ratio >= 0.08)

    if lang_code in HANT_LANGS:
        d = diff_chars("zh-hant")
        if hit(d):
            return ("{} 的卡片要用繁体字，但这段文字里有 {} 处简体字形"
                    "（{}…）。请整段改写成繁体。".format(
                        lang_code, len(d), "".join(d[:8])))
    elif lang_code in HANS_LANGS:
        d = diff_chars("zh-hans")
        if hit(d):
            return ("简体中文的卡片里出现了 {} 处繁体字形（{}…），"
                    "请整段改写成简体。".format(len(d), "".join(d[:8])))
    return None


def check(payload, min_claims=1, need_https=True, lang_code=None):
    """校验 research 交出来的结构。通过返回报告 dict，不通过抛 VerifyError。"""
    problems, report = [], {"claims": [], "fetched": {}}

    for k in ("quote", "fact", "source", "claims"):
        if not payload.get(k):
            problems.append("缺字段 {}".format(k))
    if problems:
        raise VerifyError("研究结果结构不完整：{}".format("；".join(problems)))

    src = str(payload["source"]).strip()
    if need_https and not re.match(r"^https?://", src):
        problems.append(
            "source 必须是 http(s) 链接，拿到的是 {!r}。"
            "（这条同时挡住 javascript: 之类的注入）".format(src[:60]))

    claims = payload["claims"]
    if not isinstance(claims, list) or len(claims) < min_claims:
        raise VerifyError("claims 至少要有 {} 条，实际 {}".format(
            min_claims, len(claims) if isinstance(claims, list) else "非列表"))

    fact_norm = fetch.normalize(payload["fact"])
    evidence_pool = ""

    for i, c in enumerate(claims, 1):
        url = str((c or {}).get("url") or "").strip()
        ev = str((c or {}).get("evidence") or "").strip()
        entry = {"i": i, "url": url, "claim": (c or {}).get("claim", ""),
                 "evidence": ev[:200], "ok": False, "reason": ""}
        if not re.match(r"^https?://", url):
            entry["reason"] = "url 不是 http(s)"
            report["claims"].append(entry)
            problems.append("第 {} 条断言的 url 不合法：{!r}".format(i, url[:60]))
            continue
        if len(ev) < 12:
            entry["reason"] = "evidence 太短，无法校验"
            report["claims"].append(entry)
            problems.append("第 {} 条断言的 evidence 太短".format(i))
            continue
        try:
            if url not in report["fetched"]:
                report["fetched"][url] = fetch.page_text(url)
            page = report["fetched"][url]
        except fetch.FetchError as e:
            entry["reason"] = str(e)[:120]
            report["claims"].append(entry)
            problems.append("第 {} 条断言的页面抓不到：{}".format(i, str(e)[:90]))
            continue

        if fetch.normalize(ev) in fetch.normalize(page):
            entry["ok"] = True
            evidence_pool += " " + ev
        else:
            entry["reason"] = "evidence 不是该页面正文的子串（可能是编的，或在付费墙后）"
            problems.append(
                "第 {} 条断言的 evidence 在页面上找不到：\n"
                "      url      {}\n"
                "      evidence {!r}\n"
                "    要求逐字引用可公开访问的正文原句。付费墙站点只能引用摘要部分。".format(
                    i, url, ev[:120]))
        report["claims"].append(entry)

    ok_claims = [c for c in report["claims"] if c["ok"]]
    if not ok_claims:
        problems.append("没有任何一条断言通过证据校验")

    # fact 里的关键 token 必须出现在通过校验的证据中
    if ok_claims:
        pool_norm = fetch.normalize(evidence_pool)
        missing = [t for t in _key_tokens(payload["fact"])
                   if fetch.normalize(t) not in pool_norm]
        report["unsupported_tokens"] = missing
        if missing:
            problems.append(
                "冷知识里这些关键信息没有被任何证据覆盖：{}\n"
                "    每一个数字、年份、人名都要能在某条 evidence 里找到。"
                "找不到就把它从 fact 里去掉，或补一条能佐证它的断言。".format(
                    ", ".join(sorted(missing)[:12])))

    # 内容本身的卫生检查：挡住把网页内容当指令带进来的路径
    for field in ("quote", "fact"):
        v = str(payload[field])
        if "```" in v or re.search(r"https?://", v):
            problems.append("{} 里不该出现代码围栏或链接".format(field))
        if any(ord(ch) < 9 or (13 < ord(ch) < 32) for ch in v):
            problems.append("{} 里含控制字符".format(field))
        # 繁简与卡片语言是否相符
        if lang_code:
            o = check_orthography(v, lang_code)
            if o:
                problems.append("{}：{}".format(field, o))

    if problems:
        raise VerifyError("核实未通过：\n  - " + "\n  - ".join(problems))
    report["verified"] = True
    return report
