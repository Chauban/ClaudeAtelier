"""抓取页面正文，供 verify.py 做证据子串校验。

无论用哪家搜索都得有这一层：要校验的是模型引用的那个 URL 上的原文，
搜索 API 返回的正文只覆盖它自己检索到的结果。

已知限制（实测）：付费墙站点只能拿到摘要。nature.com 那篇只抽出 1407 字，
就是个 Abstract，正文在墙后。所以 research 提示词里必须要求模型引用的
evidence 出自**可公开访问**的部分，verify 也只针对可访问正文校验。
"""
import re
import urllib.parse
import urllib.request

UA = "ClaudeAtelier/1.0 (+https://github.com/Chauban/ClaudeAtelier)"
MAX_BYTES = 3_000_000
TIMEOUT = 25


class FetchError(RuntimeError):
    pass


def _strip_html(html):
    html = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?is)<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", "\n", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'"), ("&mdash;", "—")):
        html = html.replace(a, b)
    html = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), html)
    return re.sub(r"[ \t ]+", " ", html)


def page_text(url):
    """返回该 URL 的可读正文。失败抛 FetchError。"""
    if not re.match(r"^https?://", url or ""):
        raise FetchError("只接受 http(s) 链接：{!r}".format(url))

    # Wikipedia 走官方全文接口，比抓 HTML 干净得多，也不给对方添麻烦
    m = re.match(r"^https?://([a-z\-]+)\.wikipedia\.org/wiki/(.+)$", url)
    if m:
        lang, title = m.group(1), urllib.parse.unquote(m.group(2))
        try:
            import json
            api = "https://{}.wikipedia.org/w/api.php?".format(lang) + \
                urllib.parse.urlencode({
                    "action": "query", "prop": "extracts", "explaintext": 1,
                    "format": "json", "redirects": 1, "titles": title})
            req = urllib.request.Request(api, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                pages = json.loads(r.read().decode())["query"]["pages"]
            txt = list(pages.values())[0].get("extract") or ""
            if txt.strip():
                return txt
        except Exception:
            pass          # 退回通用抓取

    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read(MAX_BYTES)
            enc = (r.headers.get_content_charset() or "utf-8")
    except Exception as e:
        raise FetchError("抓不到 {}：{}: {}".format(url, type(e).__name__, e))

    html = raw.decode(enc, "replace")
    try:
        import trafilatura                      # 有就用，抽得更干净
        txt = trafilatura.extract(html) or ""
        if len(txt) > 200:
            return txt
    except Exception:
        pass
    return _strip_html(html)


def normalize(s):
    """规范化：用于证据子串比对。大小写、空白、标点差异一律抹平。"""
    s = (s or "").lower()
    s = re.sub(r"[\s　]+", "", s)
    s = re.sub(r"[，,。.、；;：:！!？?（）()\[\]「」『』【】《》\"'`´‘’“”\-–—_/\\|~·]", "", s)
    return s
