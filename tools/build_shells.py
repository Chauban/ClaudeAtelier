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
import json
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

# 台账里没有 model 列的展区，展签上写哪个版本串。
# Claude 那份是项目最早的 12 列 schema，它跑在 Cowork 的定时任务里、用的是
# Opus 5 —— 由项目所有者告知，不是推断出来的。与 index.html 的 LEDGERS 一致。
# 行里带了 model 的，一律以行内的为准。
DEFAULT_MODEL = {"claude": "claude-opus-5"}


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
<meta property="og:image:alt" content="{serial}：{style}风格的竖版卡片">
<meta property="og:locale" content="{oglocale}">
<script type="application/ld+json">{jsonld}</script>
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
.prov{{margin:0 0 20px;font-size:13px;color:var(--fg3);line-height:1.9}}
.prov b{{font-weight:500;color:var(--fg2);font-variant-numeric:tabular-nums}}
.prov .k{{color:var(--fg3)}}
.prov code{{font:12px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
 word-break:break-all;color:var(--fg2)}}
.note{{margin:0 0 26px;font-size:12.5px;line-height:1.8;color:var(--fg3)}}
.note a{{color:var(--fg2)}}
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

  {prov_block}

  <p class="note">{verify_note}</p>

  <div class="foot">
    <a href="{deep}">在收藏里查看这张卡 →</a>{extra}
  </div>
</div>
</body>
</html>
"""

def enc_path(p):
    """路径逐段百分号编码。

    只用在**绝对** URL 上（og:image / canonical）：抓预览图的是各家聊天软件和
    爬虫，不是浏览器，对裸 UTF-8 路径的容忍度参差不齐。页面里的相对 <img src>
    保持原样 —— 那条路径浏览器一直读得懂，改了反而和历史壳页不一致。
    """
    from urllib.parse import quote
    return "/".join(quote(seg) for seg in str(p).split("/"))


def iso_dt(s):
    """台账的 "YYYY-MM-DD HH:MM" -> "YYYY-MM-DDTHH:MM"。

    不补时区：台账记的是生成端本地时刻，各条产线所在时区并不相同，
    硬补一个 offset 就是编造。schema.org 允许不带 offset 的本地时刻。
    """
    s = (str(s or "")).strip()
    m = re.match(r"^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})", s)
    if m:
        return m.group(1) + "T" + m.group(2)
    return m.group(1) if (m := re.match(r"^(\d{4}-\d{2}-\d{2})", s)) else ""


def human_dur(sec):
    """秒 -> 「8 分 49 秒」。展签上给人看，不是给机器看。"""
    try:
        n = int(float(sec))
    except (TypeError, ValueError):
        return ""
    if n <= 0:
        return ""
    return "{} 分 {} 秒".format(n // 60, n % 60) if n >= 60 else "{} 秒".format(n)


def jsonld_for(d):
    """schema.org/VisualArtwork。

    展签要能被机器读成「作品 + 作者 + 日期 + 媒介」，否则爬虫只看得见一段
    散文。creator 用 SoftwareApplication 而不是 Person —— 执笔的确实不是人，
    softwareVersion 写台账 model 列那个解析后的版本串（别名会漂，档案不能漂）。
    """
    o = {
        "@context": "https://schema.org",
        "@type": "VisualArtwork",
        "name": "{} · {}".format(d["serial"], d["style"]),
        "headline": d["quote"],
        "abstract": d["fact"],
        "artform": "Digital artwork",
        "artMedium": "Programmatic rendering",
        "genre": d["style"],
        "about": d["topic"],
        "creator": {
            "@type": "SoftwareApplication",
            "name": d["label"],
            "applicationCategory": "Large language model",
        },
        "isPartOf": {"@type": "Collection", "name": SITE_NAME},
    }
    if d.get("model"):
        o["creator"]["softwareVersion"] = d["model"]
    if d.get("lang_tag"):
        o["inLanguage"] = d["lang_tag"]
    if d.get("iso"):
        o["dateCreated"] = d["iso"]
    if d.get("canon"):
        o["url"] = d["canon"]
    if d.get("img_abs"):
        o["image"] = d["img_abs"]
    if d.get("source"):
        o["citation"] = d["source"]
    if d.get("sha256"):
        # 原图不进仓库，这串是它唯一进得了 git 的部分，当作藏品编目号用。
        o["identifier"] = "sha256:" + d["sha256"]
    if SITE_ORIGIN:
        o["isPartOf"]["url"] = SITE_ORIGIN + "/"
    txt = json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    # 内联 JSON 里出现 "</script" 会提前关掉标签。转成 < 是 JSON 合法写法。
    return txt.replace("<", "\\u003c").replace("&", "\\u0026")


HTML_LANG = {
    "简体中文": "zh-Hans", "繁体中文（台湾用语）": "zh-Hant-TW",
    "繁體中文（台灣）": "zh-Hant-TW", "繁体中文（香港用语）": "zh-Hant-HK",
    "粤语口语": "yue", "英文": "en", "日文": "ja", "法文": "fr",
    "德文": "de", "西班牙文": "es", "韩文": "ko", "意大利文": "it",
}


# og:locale 用的是下划线的 language_TERRITORY，和 html lang 不是一套写法。
OG_LOCALE = {
    "zh-Hans": "zh_CN", "zh-Hant-TW": "zh_TW", "zh-Hant-HK": "zh_HK",
    "yue": "zh_HK", "en": "en_US", "ja": "ja_JP", "fr": "fr_FR",
    "de": "de_DE", "es": "es_ES", "ko": "ko_KR", "it": "it_IT",
}

# 卡面上那条冷知识的核实状态。证据闸门 2026-08-12 下线之后，断言是模型
# 自己声称的、程序没有逐字比对过 —— 展签必须说出这件事，否则读者会以为
# 它被验过。博物馆写 "attribution uncertain" 就是这个用途。
VERIFY_NOTE = ("冷知识由执笔的模型自行查证。逐条断言、来源与所引原句"
               "存档在<a href=\"../../{textrel}\">纯文字副本</a>里，"
               "<b>未经程序逐字校验</b>，留作事后核实。")


def prov_html(r):
    """过程记录。台账里早就有，画廊不展、档案馆要展 ——

    而这个站两样都是，所以展签上给它一块地方。空值一律省略：`rounds` 空着
    表示「不知道」（08-12 之前的行没记过），不是 0，绝不能显示成 0。
    """
    bits = []
    rounds = (r.get("rounds") or "").strip()
    if rounds:
        bits.append(('画了几轮', '<b>{}</b> 轮'.format(esc(rounds))))
    att = (r.get("research_attempts") or "").strip()
    if att:
        bits.append(('选题尝试', '<b>{}</b> 次'.format(esc(att))))
    dur = human_dur(r.get("duration_s"))
    if dur:
        bits.append(('从开工到落地', '<b>{}</b>'.format(esc(dur))))
    fp = (r.get("fingerprint") or "").strip()
    if fp:
        bits.append(('后端指纹', '<code>{}</code>'.format(esc(fp))))
    sha = (r.get("sha256") or "").strip()
    if sha:
        bits.append(('原图指纹', '<code>{}</code>'.format(esc(sha[:16]))))
    if not bits:
        return ""
    return ('<div class="prov">'
            + '<br>'.join('<span class="k">{}</span>　{}'.format(k, v) for k, v in bits)
            + '</div>')


def write_sitemap(entries, check=False):
    """sitemap.xml + robots.txt。

    为什么必须有：`index.html` 是纯前端站，卡片列表是 JS 事后 fetch 出来的，
    爬虫顺着首页**发现不了任何一个壳页**。壳页把内容写死进了 HTML，但没人
    告诉爬虫它们存在 —— 两件事要一起做才有意义。

    sitemap 的 loc 规范上要求绝对 URL，所以没设 SITE_ORIGIN 时干脆不写：
    宁可少一份，也不写一份地址是错的。
    """
    if not SITE_ORIGIN:
        print("提醒：没设 ATELIER_SITE_ORIGIN，跳过 sitemap.xml（loc 必须是绝对 URL）。")
        return []

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
             "  <url><loc>{}/</loc><changefreq>hourly</changefreq>"
             "<priority>1.0</priority></url>".format(SITE_ORIGIN)]
    for rel, lastmod in entries:
        lines.append("  <url><loc>{}/{}</loc>{}<changefreq>monthly</changefreq>"
                     "<priority>0.7</priority></url>".format(
                         SITE_ORIGIN, rel,
                         "<lastmod>{}</lastmod>".format(lastmod) if lastmod else ""))
    lines.append("</urlset>")
    xml = "\n".join(lines) + "\n"

    robots = ("User-agent: *\n"
              "Allow: /\n"
              "Sitemap: {}/sitemap.xml\n".format(SITE_ORIGIN))

    out = []
    for name, text in (("sitemap.xml", xml), ("robots.txt", robots)):
        if not check:
            io.open(os.path.join(ROOT, name), "w",
                    encoding="utf-8", newline="\n").write(text)
        out.append(name)
    return out


def build(check=False):
    labels = ai_labels()
    written, rows_total, sitemap_rows = [], 0, []

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
            # Cloudflare Workers 的静态资源默认 html_handling 会把 `/x.html`
            # 307 重定向到无扩展名的 `/x`。所以对外声明的地址（canonical /
            # og:url / sitemap loc）一律写**无扩展名**那个：写 .html 的话每条
            # URL 都要多跳一次，而且搜索引擎最终收录的是跳转后的地址，和
            # canonical 声明的对不上 —— 正好废掉 canonical 的作用。
            # 落盘的文件名不动，仍然是 c/{ai}/{编号}.html。
            pub = "c/{}/{}".format(ai, no4)
            canon = (SITE_ORIGIN + "/" + pub) if SITE_ORIGIN else "/" + pub
            img_abs = ((SITE_ORIGIN + "/" + enc_path(webrel)) if SITE_ORIGIN
                       else "/" + enc_path(webrel))

            extra = ' · <a href="../../{}">纯文字</a>'.format(textrel)
            if os.path.exists(os.path.join(ROOT, coderel.replace("/", os.sep))):
                # 手稿：模型为这张卡现写的渲染脚本。别的地方看不到这个。
                extra += ' · <a href="../../{}">看手稿</a>'.format(coderel)

            src = (r.get("source") or "").strip()
            source_row = ('<dt>来源</dt><dd><a class="link" href="{0}" rel="nofollow noopener">'
                          '{1}</a></dd>').format(esc(src), esc(clip(src, 60))) if src else ""
            # 台账没有 model 列时退回注册表的默认（Claude 那份是最早的 12 列 schema）
            model = (r.get("model") or "").strip() or DEFAULT_MODEL.get(ai, "")

            htmllang = HTML_LANG.get((r.get("lang") or "").strip(), "zh-Hans")
            label = labels.get(ai, ai)
            jsonld = jsonld_for({
                "serial": serial, "style": (r.get("style") or "").strip(),
                "quote": (r.get("quote") or "").strip(),
                "fact": (r.get("fact") or "").strip(),
                "topic": (r.get("topic") or "").strip(),
                "label": label, "model": model, "lang_tag": htmllang,
                "iso": iso_dt(r.get("datetime")), "canon": canon,
                "img_abs": img_abs, "source": src,
                "sha256": (r.get("sha256") or "").strip(),
            })

            html = PAGE.format(
                htmllang=htmllang,
                oglocale=OG_LOCALE.get(htmllang, "zh_CN"),
                jsonld=jsonld,
                prov_block=prov_html(r),
                verify_note=VERIFY_NOTE.format(textrel=textrel),
                site=SITE_NAME, serial=serial, label=esc(label),
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
            # lastmod 用卡片自己的日期，不用文件 mtime —— 壳页是可再生的，
            # 每次全量重跑 mtime 都会变成今天，那对爬虫是纯噪音。
            sitemap_rows.append((pub, iso_dt(r.get("datetime"))[:10]))

    extra_files = write_sitemap(sitemap_rows, check)

    print("台账 {} 行 · {} 壳页 {} 个".format(
        rows_total, "将生成" if check else "已生成", len(written)))
    by_ai = {}
    for w in written:
        by_ai[w.split("/")[1]] = by_ai.get(w.split("/")[1], 0) + 1
    for k in sorted(by_ai):
        print("  c/{}/  {} 个".format(k, by_ai[k]))
    for f in extra_files:
        print("  {}  {}".format(f, "将写" if check else "已写"))
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
