"""搜索：Wikipedia 优先，DuckDuckGo 兜底。两者都不需要 key。

为什么不买付费搜索 API：
    verify.py 要校验的是**模型引用的那个 URL**上的原文，而不是搜索引擎顺手
    检索到的内容 —— 所以抓取器无论如何都得自己写（见 fetch.py）。既然如此，
    搜索这一环只需要返回 URL，DDG 就够了。

为什么 Wikipedia 单独一层且排在前面：
    官方 API、无 key、ToS 干净、不会封 IP，而且直接给全文。现有卡片的 source
    以 Wikipedia 为主，这一层能覆盖相当大一部分需求。
    实测（真实 Actions runner）：summary 接口 0.1s 返回；全文接口一次取回
    5 万余字。DDG 3/3 成功但首条常是 YouTube 之类的噪音 —— 所以顺序不能反。

provider 做成可替换的，是因为 DDG 是非官方抓取，而 runner 出口是 Azure 共享
IP、被爬虫污染严重。一旦被限流，换 provider 只改这一个文件。
"""
import json
import time
import urllib.parse
import urllib.request

import config

UA = "ClaudeAtelier/1.0 (+https://github.com/Chauban/ClaudeAtelier)"
_last_call = [0.0]


class SearchUnavailable(RuntimeError):
    """全部 provider 都用不了。调用方必须据此跳过本班次，
    绝不允许降级成「不核实直接出卡」。"""


def _throttle():
    gap = time.time() - _last_call[0]
    if gap < config.SEARCH_SPACING:
        time.sleep(config.SEARCH_SPACING - gap)
    _last_call[0] = time.time()


def _get(url, params=None, timeout=25):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


# ---------------------------------------------------------------- Wikipedia
def wikipedia(query, n=None, lang="en"):
    n = n or config.SEARCH_RESULTS
    out = []
    try:
        raw = _get("https://{}.wikipedia.org/w/api.php".format(lang), {
            "action": "query", "list": "search", "srsearch": query,
            "srlimit": n, "format": "json"})
        for it in json.loads(raw).get("query", {}).get("search", []):
            title = it["title"]
            out.append({
                "title": title,
                "url": "https://{}.wikipedia.org/wiki/{}".format(
                    lang, urllib.parse.quote(title.replace(" ", "_"))),
                "snippet": __import__("re").sub(r"<[^>]+>", "", it.get("snippet", "")),
                "provider": "wikipedia-" + lang,
            })
    except Exception:
        return []
    return out


# ---------------------------------------------------------------- DuckDuckGo
def duckduckgo(query, n=None):
    n = n or config.SEARCH_RESULTS
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
    except ImportError:
        return []
    _throttle()
    try:
        with DDGS() as d:
            return [{"title": r.get("title", ""), "url": r.get("href", ""),
                     "snippet": r.get("body", ""), "provider": "ddg"}
                    for r in d.text(query, max_results=n)]
    except Exception:
        return []


PROVIDERS = [("wikipedia", wikipedia), ("ddg", duckduckgo)]


def search(query, n=None):
    """按 provider 顺序找，第一个有结果的就返回。全空则抛 SearchUnavailable。"""
    tried = []
    for name, fn in PROVIDERS:
        res = fn(query, n)
        tried.append("{}={}".format(name, len(res)))
        if res:
            return res
    raise SearchUnavailable(
        "全部搜索 provider 都没有返回结果（{}）。查询：{!r}\n"
        "  DDG 是非官方抓取，runner 出口是 Azure 共享 IP，被限流是已知风险。"
        "本班次必须跳过 —— 绝不允许不核实就出卡。".format(", ".join(tried), query))
