"""台账：读取合并全部台账、发号、抽风格、算 K/L、查重、追加行。

两条与 Claude 侧不同的地方，都是有意的：

1. **发号只看自己的台账**，不扫磁盘。
   Claude 那条「max(台账, 磁盘) + 1」的规则，是因为它把 PNG 写进一个持久
   文件夹、之后又从那里发号 —— 渲染完就崩会留下没人认领的编号。runner 是
   无状态的，崩了什么都不留，原图只有在 lint 通过后才作为 artifact 上传，
   所以那个兜底在这里没有对应的危险。

2. **风格排除窗口看全部台账**，不只看自己的。
   规则存在的目的是「别让观众连着看到同一种长相」，而观众看到的是合并后
   按时间排序的一条流。所以窗口必须是全局的，再并上自己最近 15 条
   （自己的永远是最新已知的，不受推送延迟影响）。
"""
import csv
import glob
import io
import os
import random
import re
import time

import config


def local_now():
    """本地时间（UTC+8）。runner 跑在 UTC，写错会让合并排序错位。"""
    t = time.gmtime(time.time() + config.TZ_OFFSET_HOURS * 3600)
    return time.strftime("%Y-%m-%d %H:%M", t), time.strftime("%Y-%m", t), \
        time.strftime("%Y-%m-%d", t)


def kl_from_clock():
    """K、L 由 UTC 小时数推出（章程第 1 节）。"""
    n = int(time.time()) // 3600
    return n % 17 + 1, n % 7 + 1


def _read(path):
    if not os.path.exists(path):
        return []
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if (r.get("no") or "").strip()]


def load_all():
    """全部台账的行，按 datetime 升序。每行带 _ledger 标明来自哪一份。"""
    rows = []
    for p in sorted(glob.glob(os.path.join(config.CARDS_DIR, "cards-index*.csv"))):
        tag = os.path.basename(p)
        for r in _read(p):
            r["_ledger"] = tag
            rows.append(r)
    rows.sort(key=lambda r: (r.get("datetime") or ""))
    return rows


def load_own():
    return _read(config.LEDGER)


def next_no():
    own = load_own()
    return max([int(r["no"]) for r in own if str(r["no"]).isdigit()], default=0) + 1


def serial(no):
    return "{}{:04d}".format(config.SERIAL_PREFIX, no)


def pick_style(rng=None):
    """排除最近用过的风格后随机抽一个（章程第 1 节）。返回 (S, 名称, 候选数)。"""
    import tables
    rng = rng or random.Random()
    allr = load_all()
    recent = [r.get("S") for r in allr[-config.STYLE_EXCLUDE_WINDOW:]]
    mine = [r.get("S") for r in load_own()[-config.STYLE_EXCLUDE_WINDOW:]]
    used = {int(s) for s in recent + mine if str(s).strip().isdigit()}
    pool = [s for s in range(1, 48) if s not in used]
    if not pool:                       # 理论上不可能（47 > 15+15），兜底
        pool = list(range(1, 48))
    s = rng.choice(pool)
    return s, tables.style(s), len(pool)


def pick_lang7(rng=None):
    """L=7 时从五种外语里挑，避开台账里最近用过的（章程第 6 节）。"""
    import tables
    rng = rng or random.Random()
    recent = [(r.get("lang") or "") for r in load_all()[-12:]]
    pool = [x for x in tables.LANG7_CHOICES if x[0] not in recent] or tables.LANG7_CHOICES
    return rng.choice(pool)


# ------------------------------------------------------------------ 查重
def _trigrams(s):
    s = re.sub(r"\s+", "", s or "")
    return {s[i:i + 3] for i in range(max(0, len(s) - 2))}


def similar_facts(candidate, rows=None, k=15, thresh=0.18):
    """与候选冷知识最相近的若干条既有内容。

    章程要求「换个说法讲同一件事也算重复」。目前 60 条时把全部 fact 塞进
    提示词还行，几百条以后就撑不住了 —— 所以这里先做字符三元组 Jaccard
    粗筛，只把最像的几条交给模型判断，提示词长度不随archive增长。
    """
    rows = load_all() if rows is None else rows
    cg = _trigrams(candidate)
    if not cg:
        return []
    scored = []
    for r in rows:
        for field in ("fact", "quote"):
            g = _trigrams(r.get(field) or "")
            if not g:
                continue
            j = len(cg & g) / float(len(cg | g))
            if j >= thresh:
                scored.append((j, field, r))
    scored.sort(key=lambda x: -x[0])
    seen, out = set(), []
    for j, field, r in scored:
        key = (r.get("_ledger"), r.get("no"))
        if key in seen:
            continue
        seen.add(key)
        out.append({"score": round(j, 3), "field": field,
                    "no": r.get("no"), "ledger": r.get("_ledger"),
                    "quote": r.get("quote"), "fact": r.get("fact")})
        if len(out) >= k:
            break
    return out


def all_quotes_and_facts(rows=None):
    rows = load_all() if rows is None else rows
    return [{"no": r.get("no"), "topic": r.get("topic"),
             "quote": r.get("quote"), "fact": r.get("fact")} for r in rows]


# ------------------------------------------------------------------ 写入
def append(row):
    """往自己的台账追加一行。文件不存在就带 BOM 新建（前端按 utf-8-sig 读）。"""
    exists = os.path.exists(config.LEDGER)
    os.makedirs(os.path.dirname(config.LEDGER), exist_ok=True)
    if not exists:
        with io.open(config.LEDGER, "w", encoding="utf-8-sig", newline="") as f:
            csv.DictWriter(f, fieldnames=config.COLUMNS).writeheader()
    with io.open(config.LEDGER, "a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=config.COLUMNS).writerow(
            {k: row.get(k, "") for k in config.COLUMNS})
    return config.LEDGER


def last_datetime():
    own = load_own()
    return own[-1]["datetime"] if own else None
