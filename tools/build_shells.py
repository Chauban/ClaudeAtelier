"""给每张卡生成一个静态展签页（壳页）。

为什么需要：`index.html` 是纯前端站 —— 自己 fetch CSV，再用 JS 把卡片画出来。
后果有两个，都很硬：

    1. 把某张卡的链接发到任何地方，**没有预览图**，只是一条光秃秃的链接。
    2. 搜索引擎**收录不到任何一张卡**。爬虫拿到的是空壳，内容是 JS 事后填的。

壳页就是给每张卡一个真实存在的 HTML：OG 标签写死在源码里，爬虫和聊天软件
不跑 JS 也能读到标题、图和文字。这是藏品能被链接、被引用的前提 ——
博物馆和「一个能滚动的图片流」的区别之一。

## 为什么由一个独立任务统一生成，而不是各家自己写自己的

各家只准碰自己的目录（`COMMIT_ALLOW` 机械执行），所以根目录 `c/` 谁都不属于。
让各家都往 `c/` 里写，就是两个以上的写入方碰同一棵子树 —— 08-05 / 08-08
两次卡片积压事故正是这个形状。

所以反过来：**`c/` 由这一个任务独占**，它只读各家的台账、只写 `c/`，
谁的生成流程都不进。和 `watchdog.py` 一样是个旁观者。

附带的好处是它对家数完全不敏感：台账靠 glob 发现，新来一家什么都不用改，
而且 Claude 那条线（跑自己的 SKILL.md、不用这套代码）也照样有壳页。

## 用法

    python tools/build_shells.py            # 生成到 c/
    python tools/build_shells.py --check    # 只报要写什么，不落盘

壳页是**可重新生成的**：改了模板就全量重跑一次。所以 `_headers` 给它的是
短缓存，不是 web/* 那种一年 immutable。
"""
import argparse
import csv
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "c")

# 站点公开地址，形如 https://example.com（结尾不要斜杠）。
# **留空会让社交预览图在多数平台上不显示** —— OG 规范要求绝对 URL。
# 填上之后重新全量生成一次即可，壳页本来就是可再生的。
SITE_ORIGIN = os.environ.get("ATELIER_SITE_ORIGIN", "").rstrip("/")

SITE_NAME = "ClaudeAtelier"


def ai_labels():
    """{ai_key: 展示名}。从注册表拿，拿不到就用 key 本身。

    不写死映射表：家数是会长的，写死就得每来一家改一次，
    而漏改的表现是展签上出现一个奇怪的名字 —— 不报错，只是难看。
    """
    labels = {"claude": "Claude"}
    try:
        sys.path.insert(0, os.path.join(ROOT, "agents", "deepseek"))
        import config
        for entry in config.AI_REGISTRY.values():
            labels[entry["key"]] = entry["label"]
    except Exception:
        pass
    return labels


def ledgers():
    """[(台账路径, 该展区的目录前缀)]。根目录那份属于 Claude，前缀为空。"""
    out = [(os.path.join(ROOT, "Cards", "cards-index.csv"), "")]
    for p in sorted(glob.glob(os.path.join(ROOT, "*", "Cards", "cards-index*.csv"))):
        base = os.path.basename(os.path.dirname(os.path.dirname(p)))
        out.append((p, base + "/"))
    return [(p, b) for p, b in out if os.path.exists(p)]


def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def clip(s, n):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[:n - 1] + "…"


PAGE = """<!doctype html>
<html lang="{htmllang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{serial} · {style} · {site}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{site}">
<meta property="og:title" content="{serial} · {style}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{img_abs}">
<meta property="og:url" content="{canon}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{serial} · {style}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img_abs}">
<style>
:root{{color-scheme:light dark;--bg:#faf9f7;--fg:#1a1a1c;--fg2:#5a5a62;--fg3:#8a8a94;--line:#e3e0da;--card:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141416;--fg:#ececf0;--fg2:#a8a8b2;--fg3:#70707a;--line:#2a2a2e;--card:#1c1c20}}}}
:root[data-theme="dark"]{{--bg:#141416;--fg:#ececf0;--fg2:#a8a8b2;--fg3:#70707a;--line:#2a2a2e;--card:#1c1c20}}
:root[data-theme="light"]{{--bg:#faf9f7;--fg:#1a1a1c;--fg2:#5a5a62;--fg3:#8a8a94;--line:#e3e0da;--card:#fff}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);
 font:16px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC","Microsoft YaHei",sans-serif;
 -webkit-font-smoothing:antialiased}}
.wrap{{max-width:680px;margin:0 auto;padding:32px 20px 72px}}
.top{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;
 padding-bottom:14px;border-bottom:1px solid var(--line);margin-bottom:26px;flex-wrap:wrap}}
.top a{{color:var(--fg);text-decoration:none;font-weight:500;letter-spacing:.02em}}
.top .no{{color:var(--fg3);font-size:13px;font-variant-numeric:tabular-nums}}
figure{{margin:0 0 26px}}
img{{width:100%;height:auto;display:block;border-radius:10px;
 border:1px solid var(--line);background:var(--card)}}
blockquote{{margin:0 0 22px;padding:0 0 0 16px;border-left:2px solid var(--fg3);
 font-size:19px;line-height:1.7;color:var(--fg)}}
.fact{{margin:0 0 26px;color:var(--fg2)}}
dl{{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;margin:0 0 26px;
 font-size:14px;color:var(--fg2);border-top:1px solid var(--line);padding-top:18px}}
dt{{color:var(--fg3)}}
dd{{margin:0}}
a.link{{color:inherit}}
.foot{{font-size:13px;color:var(--fg3);border-top:1px solid var(--line);padding-top:18px}}
.foot a{{color:var(--fg2)}}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <a href="{home}">{site}</a>
    <span class="no">{serial} · {label}</span>
  </div>

  <figure>
    <img src="{img_rel}" alt="{serial}：{style}风格卡片" loading="eager">
  </figure>

  <blockquote>{quote}</blockquote>
  <p class="fact">{fact}</p>

  <dl>
    <dt>风格</dt><dd>S{S} {style}</dd>
    <dt>语言</dt><dd>{lang}</dd>
    <dt>领域</dt><dd>{topic}</dd>
    <dt>日期</dt><dd>{dt}</dd>
    <dt>执笔</dt><dd>{label}{model}</dd>
    {source_row}
  </dl>

  <div class="foot">
    <a href="{deep}">在收藏里查看这张卡 →</a>{extra}
  </div>
</div>
</body>
</html>
"""

HTML_LANG = {
    "简体中文": "zh-Hans", "繁体中文（台湾用语）": "zh-Hant-TW",
    "繁體中文（台灣）": "zh-Hant-TW", "繁体中文（香港用语）": "zh-Hant-HK",
    "粤语口语": "yue", "英文": "en", "日文": "ja", "法文": "fr",
    "德文": "de", "西班牙文": "es", "韩文": "ko", "意大利文": "it",
}


def build(check=False):
    labels = ai_labels()
    written, rows_total = [], 0

    for path, base in ledgers():
        with io.open(path, encoding="utf-8-sig", newline="") as f:
            rows = [r for r in csv.DictReader(f) if (r.get("no") or "").strip()]
        # 该展区的 ai key：优先用行里的 ai 列（权威），否则按目录名推，
        # 根目录那份是 Claude。
        for r in rows:
            rows_total += 1
            ai = (r.get("ai") or "").strip() or (base.rstrip("/") or "claude")
            no = str(r.get("no") or "").strip()
            no4 = no.zfill(4)
            fn = (r.get("filename") or "").strip()
            if not fn:
                continue
            webrel = base + "web/" + fn.replace(".png", ".webp")
            coderel = base + "code/" + fn.replace(".png", ".py")
            textrel = base + "text/" + fn.replace(".png", ".md")

            serial = "NO." + no4
            deep = ("../../#" + ("" if ai == "claude" else ai + "/") + serial)
            canon = (SITE_ORIGIN + "/c/{}/{}.html".format(ai, no4)) if SITE_ORIGIN \
                else "/c/{}/{}.html".format(ai, no4)
            img_abs = (SITE_ORIGIN + "/" + webrel) if SITE_ORIGIN else "/" + webrel

            extra = ' · <a href="../../{}">纯文字</a>'.format(textrel)
            if os.path.exists(os.path.join(ROOT, coderel.replace("/", os.sep))):
                # 手稿：模型为这张卡现写的渲染脚本。别的地方看不到这个。
                extra += ' · <a href="../../{}">看手稿</a>'.format(coderel)

            src = (r.get("source") or "").strip()
            source_row = ('<dt>来源</dt><dd><a class="link" href="{0}" rel="nofollow noopener">'
                          '{1}</a></dd>').format(esc(src), esc(clip(src, 60))) if src else ""
            model = (r.get("model") or "").strip()

            html = PAGE.format(
                htmllang=HTML_LANG.get((r.get("lang") or "").strip(), "zh-Hans"),
                site=SITE_NAME, serial=serial, label=esc(labels.get(ai, ai)),
                style=esc(r.get("style")), S=esc(r.get("S")),
                lang=esc(r.get("lang")), topic=esc(r.get("topic")),
                dt=esc(r.get("datetime")),
                model=("（{}）".format(esc(model)) if model else ""),
                quote=esc(r.get("quote")), fact=esc(r.get("fact")),
                desc=esc(clip(r.get("fact"), 150)),
                img_rel="../../" + webrel, img_abs=esc(img_abs),
                canon=esc(canon), home="../../", deep=deep,
                source_row=source_row, extra=extra)

            out = os.path.join(OUT_DIR, ai, no4 + ".html")
            rel = os.path.relpath(out, ROOT).replace(os.sep, "/")
            if not check:
                os.makedirs(os.path.dirname(out), exist_ok=True)
                io.open(out, "w", encoding="utf-8", newline="\n").write(html)
            written.append(rel)

    print("台账 {} 行 · {} 壳页 {} 个".format(
        rows_total, "将生成" if check else "已生成", len(written)))
    by_ai = {}
    for w in written:
        by_ai[w.split("/")[1]] = by_ai.get(w.split("/")[1], 0) + 1
    for k in sorted(by_ai):
        print("  c/{}/  {} 个".format(k, by_ai[k]))
    if not SITE_ORIGIN:
        print("\n提醒：没设 ATELIER_SITE_ORIGIN，og:image 只能写根相对路径，"
              "\n      微信/Twitter 等多半抓不到预览图。填上站点地址后重跑一次即可。")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只报要写什么，不落盘")
    a = ap.parse_args()
    return build(a.check)


if __name__ == "__main__":
    sys.exit(main())
