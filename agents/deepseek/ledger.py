"""台账：发号、抽风格、算 K/L、查重、追加行。

**每家 AI 完全自理：发号、查重、风格轮换，一律只读自己那份台账。**

谁也不用知道谁 —— 让在位的 Claude 去依赖新来者的文件，是拿它的稳定
换整洁，不划算；反过来让新来的去读别人的，也只是把耦合换个方向。
每个模型是一个独立的展区，各自从 NO.0001 起号、各自保证自己不重复。

由此接受的代价（项目所有者已确认）：合并展示的那面墙上，偶尔可能
连着出现同一种风格，或同一条冷知识被两家分别讲过。
"""
import csv
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
    """本 AI 自己台账的全部行，按 datetime 升序。

    名字里的 all 指「这个展区的全部卡片」，不是「全站」——
    各家自理，谁也不读谁的。
    """
    rows = _read(config.LEDGER)
    for r in rows:
        r["_ledger"] = config.AI_KEY
    rows.sort(key=lambda r: (r.get("datetime") or ""))
    return rows


def load_own():
    return _read(config.LEDGER)


def next_no():
    """各家自己从 NO.0001 数起。

    不读别人的台账：两家的编号在各自的展区里各有意义，
    合并展示时由前端用 (ai, no) 作复合标识来区分。

    也不扫磁盘（Claude 那条 max(台账, 磁盘)+1 是为了接住「渲染完就崩、
    没来得及写台账」的孤儿编号）：runner 无状态，崩了什么都不留，
    原图只在 lint 通过后才作为 artifact 上传，那个危险这里不存在。
    """
    own = load_own()
    return max([int(r["no"]) for r in own if str(r["no"]).isdigit()], default=0) + 1


def serial(no):
    return "{}{:04d}".format(config.SERIAL_PREFIX, no)


def pick_style(rng=None):
    """排除最近用过的风格后随机抽一个（章程第 1 节）。返回 (S, 名称, 候选数)。"""
    import tables
    rng = rng or random.Random()
    recent = [r.get("S") for r in load_all()[-config.STYLE_EXCLUDE_WINDOW:]]
    used = {int(s) for s in recent if str(s).strip().isdigit()}
    pool = [s for s in range(1, 48) if s not in used]
    if not pool:                       # 理论上不可能（47 > 15），兜底
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
