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


def check(payload, min_claims=1, need_https=True):
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

    if problems:
        raise VerifyError("核实未通过：\n  - " + "\n  - ".join(problems))
    report["verified"] = True
    return report
